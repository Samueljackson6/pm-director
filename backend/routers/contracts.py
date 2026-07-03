"""Contract endpoints — list, detail, categories."""

from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models import vben_response, vben_list

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.get('')
def get_contracts(page: int = 1, size: int = 20, search: str = '', sort: str = 'amount_desc'):
    db = get_db()
    where = ''
    params = []
    if search:
        where = "WHERE c.project_name LIKE ? OR c.contract_id LIKE ? OR c.party_a LIKE ?"
        like = f'%{search}%'
        params = [like, like, like]
    order = 'c.contract_amount DESC'
    if sort == 'amount_asc':
        order = 'c.contract_amount ASC'
    elif sort == 'name':
        order = 'c.project_name ASC'
    elif sort == 'date_desc':
        order = 'c.sign_date DESC'
    offset = (page - 1) * size
    total = db.execute(f'SELECT COUNT(*) FROM contracts c {where}', params).fetchone()[0]
    rows = db.execute(
        f'''
        SELECT c.*, COALESCE(fr.invoice_total,0) as invoice_total,
               COALESCE(fr.payment_total,0) as payment_total
        FROM contracts c
        LEFT JOIN current_finance_view fr ON c.contract_id = fr.project_id
        {where}
        ORDER BY {order}
        LIMIT ? OFFSET ?
        ''',
        params + [size, offset],
    ).fetchall()
    db.close()
    return vben_list(page, size, total, [dict(r) for r in rows])


@router.get('/categories')
def get_contract_categories():
    db = get_db()
    rows = db.execute('''
        SELECT cta.*, c.project_name, c.contract_amount, c.project_type
        FROM contract_type_attributes cta
        LEFT JOIN contracts c ON cta.contract_id = c.contract_id
        ORDER BY c.contract_amount DESC
    ''').fetchall()
    db.close()
    return {'items': [dict(r) for r in rows]}


@router.get('/{contract_id}')
def get_contract(contract_id: str):
    db = get_db()
    row = db.execute('SELECT * FROM contracts WHERE contract_id=?', (contract_id,)).fetchone()
    if not row:
        raise HTTPException(404, 'Contract not found')
    stages = [
        dict(r)
        for r in db.execute(
            'SELECT * FROM stages WHERE contract_id=? ORDER BY stage_number', (contract_id,)
        ).fetchall()
    ]
    payments = [
        dict(r)
        for r in db.execute(
            'SELECT * FROM payments WHERE contract_id=? ORDER BY payment_id', (contract_id,)
        ).fetchall()
    ]
    deliverables = [
        dict(r)
        for r in db.execute('SELECT * FROM deliverables WHERE contract_id=?', (contract_id,)).fetchall()
    ]
    finance = db.execute(
        'SELECT * FROM current_finance_view WHERE project_id=?', (contract_id,)
    ).fetchone()
    db.close()
    return vben_response({
        'contract': dict(row),
        'stages': stages,
        'payments': payments,
        'deliverables': deliverables,
        'finance': dict(finance) if finance else None,
    })
