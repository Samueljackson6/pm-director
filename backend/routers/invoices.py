"""Invoice endpoints — list and summary."""

import math
import os
import sqlite3
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from backend.database import get_db, get_readonly_db
from backend.models import vben_response, vben_list

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

# 文件上传目录
UPLOAD_DIR = 'uploads/invoices'
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _collection_data_state(rows: list[dict]) -> str:
    """区分可用数据、已知零值与需要人工核验的金额。"""
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


@router.get('')
def get_invoices(
    project_id: str = '',
    direction: str = '',
    invoice_type: str = '',
    page: int = 1,
    size: int = 50,
):
    """读取发票列表；读取路径不得初始化或改写业务数据库。"""
    db = get_readonly_db()
    try:
        where = 'WHERE 1=1'
        params = []
        if project_id:
            where += ' AND project_id = ?'
            params.append(project_id)
        if direction:
            where += ' AND direction = ?'
            params.append(direction)
        if invoice_type:
            where += ' AND invoice_type = ?'
            params.append(invoice_type)

        try:
            total = db.execute(f'SELECT COUNT(*) FROM invoices {where}', params).fetchone()[0]
            rows = db.execute(
                f'SELECT * FROM invoices {where} ORDER BY invoice_date DESC LIMIT ? OFFSET ?',
                params + [size, (page - 1) * size],
            ).fetchall()
        except sqlite3.OperationalError as error:
            if _is_missing_table(error, 'invoices'):
                return vben_list(page, size, 0, [], data_state='source_not_established')
            raise

        items = [dict(row) for row in rows]
        return vben_list(page, size, total, items, data_state=_collection_data_state(items))
    finally:
        db.close()


@router.get('/supplier-summary')
def get_supplier_invoice_summary():
    """供应商发票统计."""
    db = get_db()
    rows = db.execute('''
        SELECT
            COALESCE(SUM(CASE WHEN i.status != '已付款' THEN i.amount ELSE 0 END), 0) as unpaid,
            COALESCE(SUM(CASE WHEN i.status = '已付款' THEN i.amount ELSE 0 END), 0) as paid,
            COUNT(*) as total_count,
            COALESCE(SUM(i.amount), 0) as total_amount
        FROM invoices i
        WHERE i.direction = 'inbound'
    ''').fetchone()
    db.close()
    return vben_response(dict(rows))


@router.get('/summary')
def get_invoice_summary():
    db = get_db()
    rows = db.execute('''
        SELECT i.project_id, c.project_name, c.contract_amount,
               SUM(CASE WHEN i.invoice_type='客户开票' THEN i.amount ELSE 0 END) as invoiced,
               SUM(CASE WHEN i.invoice_type='客户回款' THEN i.amount ELSE 0 END) as received,
               COUNT(CASE WHEN i.invoice_type='客户开票' THEN 1 END) as inv_count,
               COUNT(CASE WHEN i.invoice_type='客户回款' THEN 1 END) as pay_count
        FROM invoices i
        LEFT JOIN contracts c ON i.project_id = c.contract_id
        GROUP BY i.project_id
        ORDER BY invoiced DESC
    ''').fetchall()
    db.close()
    return vben_response({'items': [dict(r) for r in rows]})


@router.get('/{invoice_id}')
def get_invoice(invoice_id: int):
    """读取单张发票详情；禁止通过详情 GET 触发写入。"""
    db = get_readonly_db()
    try:
        row = db.execute('''
            SELECT i.*, c.project_name, c.party_a as customer_name
            FROM invoices i
            LEFT JOIN contracts c ON i.project_id = c.contract_id
            WHERE i.invoice_id=?
        ''', (invoice_id,)).fetchone()
        if not row:
            raise HTTPException(404, 'Invoice not found')
        return vben_response({'invoice': dict(row)})
    finally:
        db.close()


@router.put('/{invoice_id}')
def update_invoice(invoice_id: int, payload: dict):
    """更新发票信息。"""
    db = get_db()
    row = db.execute('SELECT 1 FROM invoices WHERE invoice_id=?', (invoice_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Invoice not found')

    updatable = {'project_id', 'invoice_type', 'invoice_no', 'invoice_date', 'amount',
                 'tax_rate', 'tax_amount', 'total_with_tax', 'status', 'received_date',
                 'payment_status', 'notes', 'direction'}
    fields = []
    values = []
    for k, v in payload.items():
        if k in updatable and v is not None:
            fields.append(f'{k}=?')
            values.append(v)

    if not fields:
        db.close()
        return vben_response({'invoice_id': invoice_id, 'updated': False})

    values.append(invoice_id)
    db.execute(f'UPDATE invoices SET {", ".join(fields)} WHERE invoice_id=?', values)
    db.commit()
    db.close()
    return vben_response({'invoice_id': invoice_id, 'updated': True})


@router.post('')
def create_invoice(payload: dict):
    """新增发票。"""
    db = get_db()
    fields = ['project_id', 'invoice_type', 'invoice_no', 'invoice_date', 'amount',
              'tax_rate', 'tax_amount', 'total_with_tax', 'status', 'received_date',
              'payment_status', 'notes', 'direction']
    values = [payload.get(f) for f in fields]

    placeholders = ', '.join(['?' for _ in fields])
    db.execute(
        f'INSERT INTO invoices ({", ".join(fields)}) VALUES ({placeholders})',
        values,
    )
    db.commit()
    invoice_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return vben_response({'invoice_id': invoice_id, 'created': True})


@router.get('/{invoice_id}/files')
def get_invoice_files(invoice_id: int):
    """获取发票文件列表。"""
    db = get_db()
    files = db.execute(
        'SELECT * FROM invoice_files WHERE invoice_id=? ORDER BY upload_time DESC',
        (invoice_id,)
    ).fetchall()
    db.close()
    return vben_response({'files': [dict(f) for f in files]})


@router.post('/{invoice_id}/files')
async def upload_invoice_file(invoice_id: int, file: UploadFile = File(...)):
    """上传发票文件。"""
    db = get_db()
    row = db.execute('SELECT 1 FROM invoices WHERE invoice_id=?', (invoice_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Invoice not found')

    # 保存文件
    file_path = os.path.join(UPLOAD_DIR, f'{invoice_id}_{file.filename}')
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    # 记录到数据库
    db.execute(
        'INSERT INTO invoice_files (invoice_id, file_name, file_path, file_type, file_size) VALUES (?, ?, ?, ?, ?)',
        (invoice_id, file.filename, file_path, file.content_type, len(content))
    )
    db.commit()
    file_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()

    return vben_response({'file_id': file_id, 'uploaded': True})


@router.get('/{invoice_id}/files/{file_id}')
def download_invoice_file(invoice_id: int, file_id: int):
    """下载发票文件。"""
    db = get_db()
    file = db.execute(
        'SELECT * FROM invoice_files WHERE file_id=? AND invoice_id=?',
        (file_id, invoice_id)
    ).fetchone()
    db.close()

    if not file:
        raise HTTPException(404, 'File not found')

    return FileResponse(
        path=file['file_path'],
        filename=file['file_name'],
        media_type=file['file_type'] or 'application/octet-stream'
    )


@router.delete('/{invoice_id}/files/{file_id}')
def delete_invoice_file(invoice_id: int, file_id: int):
    """删除发票文件。"""
    db = get_db()
    file = db.execute(
        'SELECT * FROM invoice_files WHERE file_id=? AND invoice_id=?',
        (file_id, invoice_id)
    ).fetchone()

    if not file:
        db.close()
        raise HTTPException(404, 'File not found')

    # 删除文件
    if os.path.exists(file['file_path']):
        os.remove(file['file_path'])

    # 删除数据库记录
    db.execute('DELETE FROM invoice_files WHERE file_id=?', (file_id,))
    db.commit()
    db.close()

    return vben_response({'deleted': True})


@router.delete('/{invoice_id}')
def delete_invoice(invoice_id: int):
    """删除发票。"""
    db = get_db()
    row = db.execute('SELECT 1 FROM invoices WHERE invoice_id=?', (invoice_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Invoice not found')

    # 删除关联文件
    files = db.execute('SELECT * FROM invoice_files WHERE invoice_id=?', (invoice_id,)).fetchall()
    for file in files:
        if os.path.exists(file['file_path']):
            os.remove(file['file_path'])

    # 删除文件记录
    db.execute('DELETE FROM invoice_files WHERE invoice_id=?', (invoice_id,))
    # 删除关联
    db.execute('DELETE FROM invoice_receipt_link WHERE invoice_id=?', (invoice_id,))
    # 删除发票
    db.execute('DELETE FROM invoices WHERE invoice_id=?', (invoice_id,))
    db.commit()
    db.close()

    return vben_response({'deleted': True})


@router.get('/{invoice_id}/receipts')
def get_invoice_receipts(invoice_id: int):
    """获取发票关联的回款。"""
    db = get_db()
    receipts = db.execute('''
        SELECT r.*, irl.link_amount
        FROM receipts r
        INNER JOIN invoice_receipt_link irl ON r.receipt_id = irl.receipt_id
        WHERE irl.invoice_id = ?
        ORDER BY r.receipt_date DESC
    ''', (invoice_id,)).fetchall()
    db.close()
    return vben_response({'receipts': [dict(r) for r in receipts]})


@router.delete('/{invoice_id}/receipts/{receipt_id}')
def unlink_invoice_receipt(invoice_id: int, receipt_id: int):
    """取消发票与回款的关联。"""
    db = get_db()
    db.execute('DELETE FROM invoice_receipt_link WHERE invoice_id=? AND receipt_id=?', (invoice_id, receipt_id))
    db.commit()
    db.close()
    return vben_response({'unlinked': True})


@router.post('/{invoice_id}/receipts/{receipt_id}')
def link_invoice_receipt(invoice_id: int, receipt_id: int, payload: dict = None):
    """手动关联发票与回款。"""
    db = get_db()
    # 检查发票和回款是否存在
    invoice = db.execute('SELECT * FROM invoices WHERE invoice_id=?', (invoice_id,)).fetchone()
    receipt = db.execute('SELECT * FROM receipts WHERE receipt_id=?', (receipt_id,)).fetchone()
    if not invoice or not receipt:
        db.close()
        raise HTTPException(404, 'Invoice or receipt not found')

    link_amount = payload.get('link_amount') if payload else receipt['amount']

    db.execute(
        'INSERT INTO invoice_receipt_link (invoice_id, receipt_id, link_amount, link_type) VALUES (?, ?, ?, ?)',
        (invoice_id, receipt_id, link_amount, 'manual')
    )
    db.commit()
    db.close()
    return vben_response({'linked': True})
