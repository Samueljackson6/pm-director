"""Contract endpoints — list, detail, categories."""

from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models import vben_response, vben_list

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

# ── Sort mapping ──────────────────────────────────────────────
_SORT_MAP = {
    'amount_desc': 'c.contract_amount DESC',
    'amount_asc': 'c.contract_amount ASC',
    'name': 'c.project_name ASC',
    'date_desc': "COALESCE(c.sign_date, '') DESC",
    'date_asc': "COALESCE(c.sign_date, '') ASC",
}


@router.get('')
def get_contracts(
    page: int = 1,
    size: int = 20,
    search: str = '',
    sort: str = 'amount_desc',
    project_type: str = '',
    contract_status: str = '',
    min_amount: float | None = None,
    max_amount: float | None = None,
    sign_date_from: str = '',
    sign_date_to: str = '',
    party_a: str = '',
):
    """Paginated contract list with search, multi-field filter, and sort."""
    db = get_db()
    conditions = []
    params = []

    if search:
        conditions.append("(c.project_name LIKE ? OR c.contract_id LIKE ? OR c.party_a LIKE ?)")
        like = f'%{search}%'
        params.extend([like, like, like])

    if project_type:
        conditions.append('c.project_type = ?')
        params.append(project_type)

    if contract_status:
        conditions.append('c.contract_status = ?')
        params.append(contract_status)

    if min_amount is not None:
        conditions.append('c.contract_amount >= ?')
        params.append(min_amount)

    if max_amount is not None:
        conditions.append('c.contract_amount <= ?')
        params.append(max_amount)

    if sign_date_from:
        conditions.append('c.sign_date >= ?')
        params.append(sign_date_from)

    if sign_date_to:
        conditions.append('c.sign_date <= ?')
        params.append(sign_date_to)

    if party_a:
        conditions.append('c.party_a LIKE ?')
        params.append(f'%{party_a}%')

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
    order = _SORT_MAP.get(sort, _SORT_MAP['amount_desc'])
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
