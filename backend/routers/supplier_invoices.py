"""Supplier invoice endpoints for P1-1: unmatched invoices, auto-match, status sync."""

import sqlite3
from fastapi import APIRouter, HTTPException

from backend.database import get_readonly_db, get_db
from backend.models import vben_response

router = APIRouter(prefix="/api/supplier-invoices", tags=["supplier-invoices"])


def _is_missing_table(error: sqlite3.OperationalError, table_name: str) -> bool:
    return f"no such table: {table_name}" in str(error).lower()


@router.get("/unmatched")
def get_unmatched_supplier_invoices(page: int = 1, size: int = 50):
    """获取未匹配的供应商发票（已开但未付款）。

    未匹配定义：direction='inbound' AND status='已开' AND 同 project_id 无 supplier_payments 已付款记录。
    """
    db = get_readonly_db()
    try:
        try:
            total = db.execute("""
                SELECT COUNT(*) FROM invoices i
                WHERE i.direction = 'inbound'
                  AND i.status IN ('已开', '已回款')
                  AND NOT EXISTS (
                      SELECT 1 FROM supplier_payments sp
                      WHERE sp.project_id = i.project_id AND sp.status IN ('已付', 'paid')
                  )
            """).fetchone()[0]

            rows = db.execute("""
                SELECT i.*, s.supplier_name
                FROM invoices i
                LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
                WHERE i.direction = 'inbound'
                  AND i.status IN ('已开', '已回款')
                  AND NOT EXISTS (
                      SELECT 1 FROM supplier_payments sp
                      WHERE sp.project_id = i.project_id AND sp.status IN ('已付', 'paid')
                  )
                ORDER BY i.invoice_date DESC
                LIMIT ? OFFSET ?
            """, (size, (page - 1) * size)).fetchall()
        except sqlite3.OperationalError as error:
            if _is_missing_table(error, 'supplier_payments'):
                return vben_response({
                    'items': [], 'total': 0, 'page': page, 'size': size,
                    'data_state': 'source_not_established'
                })
            raise

        items = [dict(r) for r in rows]
        return vben_response({
            'items': items, 'total': total, 'page': page, 'size': size,
            'data_state': 'available' if items else 'known_zero'
        })
    finally:
        db.close()


@router.get("/matching-suggestions")
def get_matching_suggestions(invoice_id: int):
    """为指定供应商发票推荐可匹配的付款记录。

    匹配策略：
    1. 同 project_id 的 supplier_payments（status='已付'）
    2. 同 supplier_id 的 supplier_payments（金额相近）
    """
    db = get_readonly_db()
    try:
        invoice = db.execute(
            "SELECT * FROM invoices WHERE invoice_id=?", (invoice_id,)
        ).fetchone()
        if not invoice:
            raise HTTPException(404, "Invoice not found")

        inv = dict(invoice)
        suggestions = []

        # 策略1：同 project_id
        rows = db.execute("""
            SELECT sp.*, 'project_match' as match_reason
            FROM supplier_payments sp
            WHERE sp.project_id = ? AND sp.status IN ('已付', 'paid')
            ORDER BY sp.payment_date DESC
        """, (inv['project_id'],)).fetchall()
        suggestions.extend([dict(r) for r in rows])

        # 策略2：同 supplier_id（如果有）
        if inv.get('supplier_id'):
            rows2 = db.execute("""
                SELECT sp.*, 'supplier_match' as match_reason
                FROM supplier_payments sp
                WHERE sp.supplier_id = ? AND sp.status IN ('已付', 'paid')
                  AND sp.project_id != ?
                ORDER BY sp.payment_date DESC
            """, (inv['supplier_id'], inv['project_id'])).fetchall()
            suggestions.extend([dict(r) for r in rows2])

        return vben_response({
            'invoice': inv,
            'suggestions': suggestions[:10],
            'total_suggestions': len(suggestions)
        })
    finally:
        db.close()


@router.post("/auto-match")
def auto_match_supplier_invoice(invoice_id: int):
    """自动匹配供应商发票到付款。

    策略：
    1. 精确匹配：同 project_id 且金额相等
    2. 总额匹配：同 project_id 的多张发票总额 = 付款金额
    3. 模糊匹配：同 project_id 且金额相近（±10%）
    """
    db = get_db()
    try:
        invoice = db.execute(
            "SELECT * FROM invoices WHERE invoice_id=?", (invoice_id,)
        ).fetchone()
        if not invoice:
            raise HTTPException(404, "Invoice not found")

        inv = dict(invoice)
        matched = []

        # 策略1：精确匹配（同 project_id 且金额相等）
        rows = db.execute("""
            SELECT sp.* FROM supplier_payments sp
            WHERE sp.project_id = ? AND sp.status IN ('已付', 'paid')
              AND ABS(sp.amount - ?) < 0.01
        """, (inv['project_id'], inv['amount'])).fetchall()
        for r in rows:
            sp = dict(r)
            db.execute(
                "INSERT INTO invoice_payment_link (invoice_id, payment_id, match_type, amount) VALUES (?, ?, 'exact', ?)",
                (invoice_id, sp['payment_id'], inv['amount'])
            )
            matched.append({'payment_id': sp['payment_id'], 'match_type': 'exact', 'amount': sp['amount']})

        # 策略2：模糊匹配（同 project_id 且金额相近 ±10%）
        if not matched:
            rows = db.execute("""
                SELECT sp.* FROM supplier_payments sp
                WHERE sp.project_id = ? AND sp.status IN ('已付', 'paid')
                  AND sp.amount > 0 AND ABS(sp.amount - ?) / sp.amount <= 0.1
            """, (inv['project_id'], inv['amount'])).fetchall()
            for r in rows:
                sp = dict(r)
                db.execute(
                    "INSERT INTO invoice_payment_link (invoice_id, payment_id, match_type, amount) VALUES (?, ?, 'fuzzy', ?)",
                    (invoice_id, sp['payment_id'], inv['amount'])
                )
                matched.append({'payment_id': sp['payment_id'], 'match_type': 'fuzzy', 'amount': sp['amount']})

        if matched:
            db.commit()
            return vben_response({
                'matched': True,
                'matches': matched,
                'message': f'成功匹配 {len(matched)} 条付款记录'
            })
        else:
            return vben_response({
                'matched': False,
                'matches': [],
                'message': '未找到可匹配的付款记录，建议先录入供应商付款'
            })
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))
    finally:
        db.close()


@router.put("/{invoice_id}/status")
def update_invoice_status(invoice_id: int, payload: dict):
    """更新发票状态（支持批量更新）。

    状态流转：待开 → 已开 → 已付款
    """
    db = get_db()
    try:
        invoice = db.execute(
            "SELECT * FROM invoices WHERE invoice_id=?", (invoice_id,)
        ).fetchone()
        if not invoice:
            raise HTTPException(404, "Invoice not found")

        new_status = payload.get('status')
        if new_status not in ('待开', '已开', '已付款', '已取消'):
            raise HTTPException(400, f"无效状态: {new_status}")

        # 如果标记为已付款，检查是否有对应付款记录
        if new_status == '已付款':
            existing = db.execute("""
                SELECT COUNT(*) FROM invoice_payment_link ipl
                INNER JOIN supplier_payments sp ON ipl.payment_id = sp.payment_id
                WHERE ipl.invoice_id = ?
            """, (invoice_id,)).fetchone()
            if existing and existing[0] == 0:
                raise HTTPException(400, "发票标记为已付款但无对应付款记录，请先匹配付款")

        db.execute(
            "UPDATE invoices SET status=?, payment_status=? WHERE invoice_id=?",
            (new_status, '已核销' if new_status == '已付款' else '待核销', invoice_id)
        )
        db.commit()

        # 重新查询更新后的发票
        updated = dict(db.execute("SELECT * FROM invoices WHERE invoice_id=?", (invoice_id,)).fetchone())
        return vben_response({'invoice': updated, 'updated': True})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))
    finally:
        db.close()


@router.get("/{invoice_id}/linked-payments")
def get_linked_payments(invoice_id: int):
    """获取发票关联的付款记录。"""
    db = get_readonly_db()
    try:
        rows = db.execute("""
            SELECT sp.*, ipl.match_type, ipl.amount as link_amount
            FROM invoice_payment_link ipl
            INNER JOIN supplier_payments sp ON ipl.payment_id = sp.payment_id
            WHERE ipl.invoice_id = ?
            ORDER BY sp.payment_date DESC
        """, (invoice_id,)).fetchall()
        return vben_response({
            'payments': [dict(r) for r in rows],
            'total': len(rows)
        })
    finally:
        db.close()
