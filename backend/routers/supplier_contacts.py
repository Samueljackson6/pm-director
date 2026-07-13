"""Supplier contacts CRUD."""

from fastapi import APIRouter, HTTPException
from backend.database import get_db
from backend.models import vben_response

router = APIRouter(prefix="/api/suppliers", tags=["supplier-contacts"])

UPDATABLE = {'name', 'position', 'phone', 'email', 'is_primary', 'notes'}


@router.get('/{supplier_id}/contacts')
def list_contacts(supplier_id: str):
    """获取供应商联系人列表."""
    db = get_db()
    rows = db.execute(
        'SELECT id, supplier_id, name, position, phone, email, is_primary, notes '
        'FROM supplier_contacts WHERE supplier_id=? ORDER BY is_primary DESC, id ASC',
        (supplier_id,),
    ).fetchall()
    db.close()
    return vben_response({'items': [dict(r) for r in rows]})


@router.post('/{supplier_id}/contacts')
def create_contact(supplier_id: str, payload: dict):
    """新增联系人."""
    if not payload.get('name'):
        raise HTTPException(400, 'name is required')

    db = get_db()
    # 验证供应商存在
    exists = db.execute('SELECT 1 FROM suppliers WHERE supplier_id=?', (supplier_id,)).fetchone()
    if not exists:
        db.close()
        raise HTTPException(404, 'Supplier not found')

    fields = ['supplier_id', 'name', 'position', 'phone', 'email', 'is_primary', 'notes']
    values = [supplier_id, payload.get('name'), payload.get('position'),
              payload.get('phone'), payload.get('email'),
              1 if payload.get('is_primary') else 0, payload.get('notes')]

    db.execute(
        f'INSERT INTO supplier_contacts ({", ".join(fields)}) VALUES ({", ".join(["?" for _ in fields])})',
        values,
    )
    db.commit()
    contact_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return vben_response({'id': contact_id, 'created': True})


@router.put('/{supplier_id}/contacts/{contact_id}')
def update_contact(supplier_id: str, contact_id: int, payload: dict):
    """更新联系人."""
    db = get_db()
    row = db.execute(
        'SELECT 1 FROM supplier_contacts WHERE id=? AND supplier_id=?',
        (contact_id, supplier_id),
    ).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Contact not found')

    fields = []
    values = []
    for k, v in payload.items():
        if k in UPDATABLE and v is not None:
            fields.append(f'{k}=?')
            values.append(v)

    if not fields:
        db.close()
        return vben_response({'id': contact_id, 'updated': False})

    values.append(contact_id)
    db.execute(f'UPDATE supplier_contacts SET {", ".join(fields)} WHERE id=?', values)
    db.commit()
    db.close()
    return vben_response({'id': contact_id, 'updated': True})


@router.delete('/{supplier_id}/contacts/{contact_id}')
def delete_contact(supplier_id: str, contact_id: int):
    """删除联系人."""
    db = get_db()
    row = db.execute(
        'SELECT 1 FROM supplier_contacts WHERE id=? AND supplier_id=?',
        (contact_id, supplier_id),
    ).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Contact not found')

    db.execute('DELETE FROM supplier_contacts WHERE id=?', (contact_id,))
    db.commit()
    db.close()
    return vben_response({'deleted': True})
