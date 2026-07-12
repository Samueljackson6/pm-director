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
        db.close()
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
