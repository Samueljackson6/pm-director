"""Supplier endpoints — list and detail."""

from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models import vben_response

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


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
    db = get_db()
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
    db.close()
    return vben_response({'supplier': dict(sup), 'contracts': contracts})
