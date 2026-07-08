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
