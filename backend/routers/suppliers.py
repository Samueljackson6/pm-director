"""Supplier endpoints — list and detail."""

import math
import sqlite3

from fastapi import APIRouter, HTTPException
from backend.database import get_db, get_readonly_db
from backend.models import vben_response, vben_list
from backend.qcc_mcp_client import get_qcc_client

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


# ── 付款路由（必须在 /{supplier_id} 之前注册以免冲突） ──


def _collection_data_state(rows: list[dict]) -> str:
    """付款列表的空值、负值与已知零值必须保留不同业务语义。"""
    if not rows:
        return 'known_zero'
    for row in rows:
        try:
            amount = float(row.get('amount'))
        except (TypeError, ValueError):
            return 'pending_verification'
        if not math.isfinite(amount) or amount < 0:
            return 'pending_verification'
    return 'available'


def _is_missing_table(error: sqlite3.OperationalError, table_name: str) -> bool:
    return f'no such table: {table_name}' in str(error).lower()


@router.get('/payments')
def get_supplier_payments(page: int = 1, size: int = 50, supplier_id: str = ''):
    """读取供应商付款列表，不允许由 GET 建表或写入。"""
    db = get_readonly_db()
    try:
        where = 'WHERE 1=1'
        params = []
        if supplier_id:
            where += ' AND sp.supplier_id = ?'
            params.append(supplier_id)

        try:
            total = db.execute(f'SELECT COUNT(*) FROM supplier_payments sp {where}', params).fetchone()[0]
            rows = db.execute(
                f'''SELECT sp.*, s.supplier_name, s.short_name
                    FROM supplier_payments sp
                    LEFT JOIN suppliers s ON sp.supplier_id = s.supplier_id
                    {where}
                    ORDER BY sp.payment_date DESC
                    LIMIT ? OFFSET ?''',
                params + [size, (page - 1) * size],
            ).fetchall()
        except sqlite3.OperationalError as error:
            if _is_missing_table(error, 'supplier_payments'):
                return vben_list(page, size, 0, [], data_state='source_not_established')
            raise

        items = [dict(row) for row in rows]
        return vben_list(page, size, total, items, data_state=_collection_data_state(items))
    finally:
        db.close()


@router.get('/payments/{payment_id}')
def get_supplier_payment(payment_id: int):
    """读取付款及同项目供应商收票，客户回款不得混入关联单据。"""
    db = get_readonly_db()
    try:
        row = db.execute('''
            SELECT sp.*, s.supplier_name, s.short_name
            FROM supplier_payments sp
            LEFT JOIN suppliers s ON sp.supplier_id = s.supplier_id
            WHERE sp.payment_id=?
        ''', (payment_id,)).fetchone()
        if not row:
            raise HTTPException(404, 'Payment not found')

        try:
            invoice_rows = db.execute('''
                SELECT i.* FROM invoices i
                WHERE i.project_id = ?
                  AND i.direction = 'inbound'
                  AND i.invoice_type = '供应商开票'
                ORDER BY i.invoice_date DESC
            ''', (row['project_id'],)).fetchall()
        except sqlite3.OperationalError as error:
            if _is_missing_table(error, 'invoices'):
                invoice_rows = []
                linked_invoices_data_state = 'source_not_established'
            else:
                raise
        else:
            linked_invoices_data_state = _collection_data_state([dict(item) for item in invoice_rows])

        return vben_response({
            'payment': dict(row),
            'linked_invoices': [dict(item) for item in invoice_rows],
            'linked_invoices_data_state': linked_invoices_data_state,
        })
    finally:
        db.close()


@router.put('/payments/{payment_id}')
def update_supplier_payment(payment_id: int, payload: dict):
    """更新供应商付款记录."""
    db = get_db()
    row = db.execute('SELECT 1 FROM supplier_payments WHERE payment_id=?', (payment_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Payment not found')

    updatable = {'supplier_id', 'project_id', 'payment_date', 'amount',
                 'payment_method', 'status', 'notes'}
    fields = []
    values = []
    for k, v in payload.items():
        if k in updatable and v is not None:
            fields.append(f'{k}=?')
            values.append(v)

    if not fields:
        db.close()
        return vben_response({'payment_id': payment_id, 'updated': False})

    values.append(payment_id)
    db.execute(f'UPDATE supplier_payments SET {", ".join(fields)} WHERE payment_id=?', values)
    db.commit()
    db.close()
    return vben_response({'payment_id': payment_id, 'updated': True})


@router.delete('/payments/{payment_id}')
def delete_supplier_payment(payment_id: int):
    """删除供应商付款记录."""
    db = get_db()
    row = db.execute('SELECT 1 FROM supplier_payments WHERE payment_id=?', (payment_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Payment not found')
    db.execute('DELETE FROM supplier_payments WHERE payment_id=?', (payment_id,))
    db.commit()
    db.close()
    return vben_response({'deleted': True})


@router.post('/payments')
def create_supplier_payment(payload: dict):
    """新增供应商付款记录。"""
    db = get_db()
    fields = ['supplier_id', 'project_id', 'payment_date', 'amount',
              'payment_method', 'status', 'notes']
    values = [payload.get(f) for f in fields]

    if not payload.get('supplier_id'):
        db.close()
        raise HTTPException(400, 'supplier_id is required')
    if not payload.get('amount'):
        db.close()
        raise HTTPException(400, 'amount is required')

    placeholders = ', '.join(['?' for _ in fields])
    db.execute(
        f'INSERT INTO supplier_payments ({", ".join(fields)}) VALUES ({placeholders})',
        values,
    )
    db.commit()
    payment_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return vben_response({'payment_id': payment_id, 'created': True})


# ── 企查查 MCP 路由（特定路径，必须在 /{supplier_id} 之前注册） ──


@router.get('/qcc/{credit_code}')
async def get_supplier_qcc_info(credit_code: str):
    """
    从企查查 MCP 获取供应商详细信息

    包含5个维度的数据：
    1. 工商信息
    2. 企业简介
    3. 风险扫描
    4. 软件著作权
    5. 对外投资

    Args:
        credit_code: 统一社会信用代码

    Returns:
        包含所有维度数据的字典
    """
    try:
        client = get_qcc_client()
        data = await client.get_supplier_detail(credit_code)

        if not data:
            raise HTTPException(404, '未找到企业信息')

        return vben_response({
            'basic_info': data.get('basic_info'),
            'profile': data.get('profile'),
            'risk_scan': data.get('risk_scan'),
            'software_copyrights': data.get('software_copyrights'),
            'external_investments': data.get('external_investments'),
        })

    except Exception as e:
        raise HTTPException(500, f'查询企查查数据失败: {str(e)}')


@router.get('/qcc/{credit_code}/basic')
async def get_qcc_basic(credit_code: str):
    """企查查 MCP - 工商信息"""
    try:
        client = get_qcc_client()
        data = await client.get_company_registration_info(credit_code)
        return vben_response(data)
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.get('/qcc/{credit_code}/profile')
async def get_qcc_profile(credit_code: str):
    """企查查 MCP - 企业简介"""
    try:
        client = get_qcc_client()
        data = await client.get_company_profile(credit_code)
        return vben_response(data)
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.get('/qcc/{credit_code}/risk')
async def get_qcc_risk(credit_code: str):
    """企查查 MCP - 风险扫描"""
    try:
        client = get_qcc_client()
        data = await client.get_company_risk_scan(credit_code)
        return vben_response(data)
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.get('/qcc/{credit_code}/software')
async def get_qcc_software(credit_code: str):
    """企查查 MCP - 软件著作权"""
    try:
        client = get_qcc_client()
        data = await client.get_software_copyright_info(credit_code)
        return vben_response(data)
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.get('/qcc/{credit_code}/investment')
async def get_qcc_investment(credit_code: str):
    """企查查 MCP - 对外投资"""
    try:
        client = get_qcc_client()
        data = await client.get_external_investments(credit_code)
        return vben_response(data)
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.get('/qcc/{credit_code}/changes')
async def detect_qcc_changes(credit_code: str):
    """检测企查查数据变化"""
    try:
        from backend.qcc_sync import detect_changes

        # 先查询最新数据
        client = get_qcc_client()
        new_data = await client.get_supplier_detail(credit_code)

        if not new_data:
            raise HTTPException(404, '未找到企业信息')

        # 检测变化
        result = detect_changes(credit_code, new_data)
        return vben_response(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'检测失败: {str(e)}')


@router.get('/qcc/{credit_code}/changes/check')
async def check_and_alert_changes(credit_code: str):
    """检测变化并创建预警"""
    try:
        from backend.qcc_sync import detect_changes
        from backend.qcc_alerts import check_and_create_alerts

        # 查询最新数据
        client = get_qcc_client()
        new_data = await client.get_supplier_detail(credit_code)

        if not new_data:
            raise HTTPException(404, '未找到企业信息')

        # 检测变化
        changes = detect_changes(credit_code, new_data)

        # 创建预警
        alerts = check_and_create_alerts(credit_code, changes)

        return vben_response({
            'changes': changes,
            'alerts_created': len(alerts),
            'alerts': alerts
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'检测失败: {str(e)}')


# ── 风险预警 API（必须在 /{supplier_id} 之前注册以免冲突） ──


@router.get('/alerts')
async def get_risk_alerts(credit_code: str = None, unread_only: bool = False, limit: int = 50):
    """获取风险预警列表"""
    try:
        from backend.qcc_alerts import get_alerts
        alerts = get_alerts(credit_code, unread_only, limit)
        return vben_response({'alerts': alerts})
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.put('/alerts/{alert_id}/read')
async def mark_alert_as_read(alert_id: int):
    """标记预警为已读"""
    try:
        from backend.qcc_alerts import mark_alert_read
        success = mark_alert_read(alert_id)
        return vben_response({'success': success})
    except Exception as e:
        raise HTTPException(500, f'操作失败: {str(e)}')


@router.get('/alerts/stats')
async def get_alert_statistics(credit_code: str = None):
    """获取预警统计"""
    try:
        from backend.qcc_alerts import get_alert_stats
        stats = get_alert_stats(credit_code)
        return vben_response(stats)
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.get('/alerts/config/{credit_code}')
async def get_alert_configuration(credit_code: str):
    """获取预警配置"""
    try:
        from backend.qcc_alerts import get_alert_config
        config = get_alert_config(credit_code)
        return vben_response(config)
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.put('/alerts/config/{credit_code}')
async def update_alert_configuration(credit_code: str, config: dict):
    """更新预警配置"""
    try:
        from backend.qcc_alerts import update_alert_config
        success = update_alert_config(credit_code, config)
        return vben_response({'success': success})
    except Exception as e:
        raise HTTPException(500, f'更新失败: {str(e)}')


# ── 数据同步路由（必须在 /{supplier_id} 之前注册以免冲突） ──


@router.post('/sync/{credit_code}')
async def sync_supplier_qcc_data(credit_code: str):
    """
    同步供应商企查查数据到本地数据库

    Args:
        credit_code: 统一社会信用代码

    Returns:
        同步结果
    """
    try:
        from backend.qcc_sync import sync_supplier_qcc_data as sync_func
        result = await sync_func(credit_code)
        return vben_response(result)
    except Exception as e:
        raise HTTPException(500, f'同步失败: {str(e)}')


@router.get('/local/{credit_code}')
def get_local_qcc_data(credit_code: str):
    """
    从本地数据库获取企查查数据

    Args:
        credit_code: 统一社会信用代码

    Returns:
        企查查数据
    """
    try:
        from backend.qcc_sync import get_local_qcc_data
        data = get_local_qcc_data(credit_code)
        if not data:
            raise HTTPException(404, '本地无数据，请先同步')
        return vben_response(data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.get('/sync/{credit_code}/history')
def get_sync_history(credit_code: str, limit: int = 10):
    """
    获取同步历史记录

    Args:
        credit_code: 统一社会信用代码
        limit: 返回记录数

    Returns:
        同步历史列表
    """
    try:
        from backend.qcc_sync import get_sync_history
        history = get_sync_history(credit_code, limit)
        return vben_response({'history': history})
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.get('/cache/stats')
def get_cache_stats():
    """获取缓存统计信息"""
    try:
        client = get_qcc_client()
        stats = client.get_cache_stats()
        return vben_response(stats)
    except Exception as e:
        raise HTTPException(500, f'查询失败: {str(e)}')


@router.delete('/cache/{credit_code}')
def clear_supplier_cache(credit_code: str):
    """
    清除指定供应商的缓存

    Args:
        credit_code: 统一社会信用代码

    Returns:
        清除结果
    """
    try:
        client = get_qcc_client()
        cleared = client.clear_supplier_cache(credit_code)
        return vben_response({'cleared': cleared})
    except Exception as e:
        raise HTTPException(500, f'清除失败: {str(e)}')


# ── 供应商基础路由（泛匹配 /{supplier_id}，必须放在最后以免截获其他路由） ──


@router.get('')
def get_suppliers():
    db = get_db()
    rows = db.execute('''
        SELECT * FROM suppliers WHERE status='active' AND total_contract_amount > 0
        ORDER BY total_contract_amount DESC
    ''').fetchall()
    db.close()
    return vben_response({'items': [dict(r) for r in rows]})


@router.get('/{supplier_id}')
def get_supplier(supplier_id: str):
    db = get_readonly_db()
    try:
        sup = db.execute('SELECT * FROM suppliers WHERE supplier_id=?', (supplier_id,)).fetchone()
        if not sup:
            raise HTTPException(404, 'Supplier not found')
        contracts = [
            dict(r)
            for r in db.execute(
                '''
                SELECT sc.*, c.project_name FROM supplier_contracts sc
                LEFT JOIN contracts c ON sc.project_id = c.contract_id
                WHERE sc.supplier_id=?
                ''',
                (supplier_id,),
            ).fetchall()
        ]
        supplier_invoices = [
            dict(r)
            for r in db.execute(
                '''
                SELECT i.* FROM invoices i
                INNER JOIN supplier_contracts sc ON i.project_id = sc.project_id
                WHERE sc.supplier_id = ?
                  AND i.invoice_type = '供应商开票'
                  AND i.direction = 'inbound'
                ORDER BY i.invoice_date DESC
                ''',
                (supplier_id,),
            ).fetchall()
        ]
        payments = [
            dict(r)
            for r in db.execute(
                '''
                SELECT * FROM supplier_payments
                WHERE supplier_id = ?
                ORDER BY payment_date DESC
                ''',
                (supplier_id,),
            ).fetchall()
        ]
        contacts = [
            dict(r)
            for r in db.execute(
                'SELECT id, name, position, phone, email, is_primary, notes '
                'FROM supplier_contacts WHERE supplier_id=? ORDER BY is_primary DESC, id ASC',
                (supplier_id,),
            ).fetchall()
        ]
        sup_dict = dict(sup)
    finally:
        db.close()

    # 本地企查查缓存使用独立只读连接，失败时不影响供应商主档展示。
    qcc_data = None
    credit_code = sup_dict.get('credit_code')
    if credit_code:
        try:
            from backend.qcc_sync import get_local_qcc_data
            qcc_data = get_local_qcc_data(credit_code)
        except Exception:
            qcc_data = None
    data_states = {
        'supplier_invoices': 'available' if supplier_invoices else 'source_not_established',
        'supplier_payments': 'available' if payments else 'known_zero',
    }
    return vben_response({
        'supplier': sup_dict,
        'contracts': contracts,
        'supplier_invoices': supplier_invoices,
        'invoices': supplier_invoices,
        'data_states': data_states,
        'payments': payments,
        'contacts': contacts,
        'qcc_data': qcc_data,
    })


@router.put('/{supplier_id}')
def update_supplier(supplier_id: str, payload: dict):
    """更新供应商信息。"""
    db = get_db()
    row = db.execute('SELECT 1 FROM suppliers WHERE supplier_id=?', (supplier_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Supplier not found')

    updatable = {'supplier_name', 'short_name', 'contact_person', 'contact_phone',
                 'category', 'status', 'notes', 'evaluation'}
    fields = []
    values = []
    for k, v in payload.items():
        if k in updatable and v is not None:
            fields.append(f'{k}=?')
            values.append(v)

    if not fields:
        db.close()
        return vben_response({'supplier_id': supplier_id, 'updated': False})

    values.append(supplier_id)
    db.execute(f'UPDATE suppliers SET {", ".join(fields)} WHERE supplier_id=?', values)
    db.commit()
    db.close()
    return vben_response({'supplier_id': supplier_id, 'updated': True})


@router.post('')
def create_supplier(payload: dict):
    """新增供应商。"""
    db = get_db()
    fields = ['supplier_id', 'supplier_name', 'short_name', 'contact_person',
              'contact_phone', 'category', 'notes']
    values = [payload.get(f) for f in fields]

    if not payload.get('supplier_id'):
        db.close()
        raise HTTPException(400, 'supplier_id is required')

    placeholders = ', '.join(['?' for _ in fields])
    db.execute(
        f'INSERT INTO suppliers ({", ".join(fields)}, status, created_at) VALUES ({placeholders}, \'active\', datetime(\'now\'))',
        values,
    )
    db.commit()
    db.close()
    return vben_response({'supplier_id': payload['supplier_id'], 'created': True})
