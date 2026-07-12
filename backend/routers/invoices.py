"""Invoice endpoints — list and summary."""

from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models import vben_response, vben_list

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.get('')
def get_invoices(project_id: str = '', page: int = 1, size: int = 50):
    db = get_db()
    where = ''
    params = []
    if project_id:
        where = 'WHERE project_id = ?'
        params = [project_id]
    total = db.execute(f'SELECT COUNT(*) FROM invoices {where}', params).fetchone()[0]
    rows = db.execute(
        f'SELECT * FROM invoices {where} ORDER BY invoice_date DESC LIMIT ? OFFSET ?',
        params + [size, (page - 1) * size],
    ).fetchall()
    db.close()
    return vben_list(page, size, total, [dict(r) for r in rows])


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
    db = get_db()
    row = db.execute('SELECT * FROM invoices WHERE invoice_id=?', (invoice_id,)).fetchone()
    if not row:
        raise HTTPException(404, 'Invoice not found')
    db.close()
    return vben_response({'invoice': dict(row)})


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
