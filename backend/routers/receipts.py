"""Receipt endpoints — 回款管理和智能匹配."""

import sqlite3

from fastapi import APIRouter, HTTPException, Query
from backend.database import get_db
from backend.models import vben_response, vben_list

router = APIRouter(prefix="/api/receipts", tags=["receipts"])


@router.get('')
def get_receipts(project_id: str = '', page: int = 1, size: int = 50):
    """获取回款列表."""
    db = get_db()
    try:
        where = 'WHERE 1=1'
        params = []
        if project_id:
            where += ' AND project_id = ?'
            params.append(project_id)

        total = db.execute(f'SELECT COUNT(*) FROM receipts {where}', params).fetchone()[0]
        rows = db.execute(
            f'SELECT * FROM receipts {where} ORDER BY receipt_date DESC LIMIT ? OFFSET ?',
            params + [size, (page - 1) * size],
        ).fetchall()
        invalid_receipt_count = db.execute(
            f'SELECT COUNT(*) FROM receipts {where} AND (amount IS NULL OR amount < 0)',
            params,
        ).fetchone()[0]
        summary = {
            'currency_unit': '元',
            'status': 'pending_verification' if invalid_receipt_count else 'available',
            'receipt_total': None,
            'matched_total': None,
            'unmatched_total': None,
        }

        if total == 0:
            summary.update({
                'receipt_total': 0,
                'matched_total': 0,
                'unmatched_total': 0,
                'status': 'available',
            })
        elif not invalid_receipt_count:
            receipt_total = db.execute(
                f'SELECT COALESCE(SUM(amount), 0) FROM receipts {where}', params
            ).fetchone()[0]
            summary['receipt_total'] = receipt_total
            try:
                invalid_link_count = db.execute(f'''
                    SELECT COUNT(*)
                    FROM invoice_receipt_link irl
                    INNER JOIN receipts r ON r.receipt_id = irl.receipt_id
                    {where.replace('project_id', 'r.project_id')}
                    AND (irl.link_amount IS NULL OR irl.link_amount < 0)
                ''', params).fetchone()[0]
                if invalid_link_count:
                    summary['status'] = 'pending_verification'
                else:
                    matched_total = db.execute(f'''
                        SELECT COALESCE(SUM(matched_amount), 0) FROM (
                            SELECT r.receipt_id,
                                   MIN(r.amount, MAX(0, COALESCE(SUM(irl.link_amount), 0))) AS matched_amount
                            FROM receipts r
                            LEFT JOIN invoice_receipt_link irl ON irl.receipt_id = r.receipt_id
                            {where.replace('project_id', 'r.project_id')}
                            GROUP BY r.receipt_id, r.amount
                        )
                    ''', params).fetchone()[0]
                    summary['matched_total'] = matched_total
                    summary['unmatched_total'] = max(0, receipt_total - matched_total)
                    summary['status'] = 'available'
            except sqlite3.OperationalError as exc:
                if 'no such table: invoice_receipt_link' not in str(exc).lower():
                    raise
                summary['status'] = 'pending_verification'

        response = vben_list(page, size, total, [dict(r) for r in rows])
        response['data']['summary'] = summary
        return response
    finally:
        db.close()


@router.post('')
def create_receipt(payload: dict):
    """新增回款记录."""
    db = get_db()
    fields = ['project_id', 'receipt_date', 'amount', 'receipt_no',
              'payer_name', 'receipt_method', 'status', 'notes']
    values = [payload.get(f) for f in fields]

    placeholders = ', '.join(['?' for _ in fields])
    db.execute(
        f'INSERT INTO receipts ({", ".join(fields)}) VALUES ({placeholders})',
        values,
    )
    db.commit()
    receipt_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return vben_response({'receipt_id': receipt_id, 'created': True})


@router.get('/{receipt_id}')
def get_receipt(receipt_id: int):
    """获取回款详情."""
    db = get_db()
    receipt = db.execute('SELECT * FROM receipts WHERE receipt_id=?', (receipt_id,)).fetchone()
    if not receipt:
        db.close()
        raise HTTPException(404, 'Receipt not found')

    # 获取关联的发票
    invoices = db.execute('''
        SELECT i.*, irl.link_amount
        FROM invoices i
        INNER JOIN invoice_receipt_link irl ON i.invoice_id = irl.invoice_id
        WHERE irl.receipt_id = ?
        ORDER BY i.invoice_date DESC
    ''', (receipt_id,)).fetchall()
    db.close()
    return vben_response({'receipt': dict(receipt), 'linked_invoices': [dict(i) for i in invoices]})


@router.put('/{receipt_id}')
def update_receipt(receipt_id: int, payload: dict):
    """更新回款记录."""
    db = get_db()
    row = db.execute('SELECT 1 FROM receipts WHERE receipt_id=?', (receipt_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Receipt not found')

    updatable = {'project_id', 'receipt_date', 'amount', 'receipt_no',
                 'payer_name', 'receipt_method', 'status', 'notes'}
    fields = []
    values = []
    for k, v in payload.items():
        if k in updatable and v is not None:
            fields.append(f'{k}=?')
            values.append(v)

    if not fields:
        db.close()
        return vben_response({'receipt_id': receipt_id, 'updated': False})

    values.append(receipt_id)
    db.execute(f'UPDATE receipts SET {", ".join(fields)} WHERE receipt_id=?', values)
    db.commit()
    db.close()
    return vben_response({'receipt_id': receipt_id, 'updated': True})


@router.delete('/{receipt_id}')
def delete_receipt(receipt_id: int):
    """删除回款记录."""
    db = get_db()
    row = db.execute('SELECT 1 FROM receipts WHERE receipt_id=?', (receipt_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Receipt not found')

    # 删除关联
    db.execute('DELETE FROM invoice_receipt_link WHERE receipt_id=?', (receipt_id,))
    # 删除回款
    db.execute('DELETE FROM receipts WHERE receipt_id=?', (receipt_id,))
    db.commit()
    db.close()
    return vben_response({'deleted': True})


@router.post('/auto-match')
def auto_match_receipts(project_id: str = ''):
    """智能匹配发票和回款.

    ⚠️ 此接口会写入数据库，仅用于测试/演示。生产环境应通过业务确认后再执行。
    """
    db = get_db()

    # 获取所有项目或指定项目
    where = 'WHERE 1=1'
    params = []
    if project_id:
        where = 'WHERE project_id = ?'
        params = [project_id]

    # 获取未匹配的发票和回款
    invoices = db.execute(f'''
        SELECT * FROM invoices
        {where}
        AND invoice_type = '客户开票'
        AND invoice_id NOT IN (SELECT invoice_id FROM invoice_receipt_link)
        ORDER BY project_id, invoice_date
    ''', params).fetchall()

    receipts = db.execute(f'''
        SELECT * FROM receipts
        {where}
        AND receipt_id NOT IN (SELECT receipt_id FROM invoice_receipt_link)
        ORDER BY project_id, receipt_date
    ''', params).fetchall()

    matched = 0
    # 按项目分组匹配
    projects = set(inv['project_id'] for inv in invoices) | set(r['project_id'] for r in receipts)

    for proj_id in projects:
        proj_invoices = [inv for inv in invoices if inv['project_id'] == proj_id]
        proj_receipts = [r for r in receipts if r['project_id'] == proj_id]

        for receipt in proj_receipts:
            receipt_amount = receipt['amount']
            receipt_date = receipt['receipt_date']

            # 查找日期之前的发票
            valid_invoices = [inv for inv in proj_invoices
                            if inv['invoice_date'] <= receipt_date]

            if not valid_invoices:
                continue

            # 策略1: 精确匹配单张发票
            exact_match = next((inv for inv in valid_invoices
                               if abs(inv['amount'] - receipt_amount) < 0.01), None)

            if exact_match:
                db.execute('''
                    INSERT INTO invoice_receipt_link (invoice_id, receipt_id, link_amount, link_type)
                    VALUES (?, ?, ?, 'auto')
                ''', (exact_match['invoice_id'], receipt['receipt_id'], receipt_amount))
                matched += 1
                continue

            # 策略2: 匹配最近2-3张发票总额
            for n in [2, 3]:
                if len(valid_invoices) >= n:
                    recent_invoices = valid_invoices[-n:]
                    total_amount = sum(inv['amount'] for inv in recent_invoices)
                    if abs(total_amount - receipt_amount) < 0.01:
                        for inv in recent_invoices:
                            proportion = inv['amount'] / total_amount
                            link_amount = receipt_amount * proportion
                            db.execute('''
                                INSERT INTO invoice_receipt_link (invoice_id, receipt_id, link_amount, link_type)
                                VALUES (?, ?, ?, 'auto')
                            ''', (inv['invoice_id'], receipt['receipt_id'], link_amount))
                        matched += 1
                        break

            # 策略3: 部分匹配（考虑质保金）
            if matched == 0:
                # 查找金额最接近的发票
                closest = min(valid_invoices, key=lambda inv: abs(inv['amount'] - receipt_amount))
                if abs(closest['amount'] - receipt_amount) / closest['amount'] < 0.1:  # 10%误差
                    db.execute('''
                        INSERT INTO invoice_receipt_link (invoice_id, receipt_id, link_amount, link_type)
                        VALUES (?, ?, ?, 'auto_partial')
                    ''', (closest['invoice_id'], receipt['receipt_id'], receipt_amount))
                    matched += 1

    db.commit()
    db.close()
    return vben_response({'matched': matched})
