"""Database stats endpoint — table row counts."""

from fastapi import APIRouter

from backend.database import get_db

router = APIRouter(prefix="/api/db", tags=["database"])


@router.get('/summary')
def get_db_summary():
    db = get_db()
    tables = [
        'contracts', 'stages', 'payments', 'deliverables', 'finance_records',
        'invoices', 'suppliers', 'supplier_contracts', 'contract_id_mapping',
        'contract_type_attributes', 'project_status',
    ]
    result = {}
    for t in tables:
        try:
            cnt = db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
            result[t] = cnt
        except Exception:
            result[t] = 0
    db.close()
    return result
