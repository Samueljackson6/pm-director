"""Contract endpoints — list, detail, categories."""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from backend.database import get_db
from backend.models import vben_response, vben_list

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

# 合同文件存储目录（容器内 /app/uploads/contract_files，已通过 docker volume 持久化）
# contracts.py 位于 backend/routers/，parent.parent.parent = 仓库根(/app)，与 compose 挂载的 /app/uploads 对齐
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "contract_files"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
    # 违约/罚款条款（#3 数据补全新增）
    clauses = [
        dict(r)
        for r in db.execute(
            'SELECT * FROM contract_clauses WHERE contract_id=? ORDER BY clause_category',
            (contract_id,),
        ).fetchall()
    ]
    finance = db.execute(
        'SELECT * FROM current_finance_view WHERE project_id=?', (contract_id,)
    ).fetchone()
    # Associated projects
    projects = [
        dict(r)
        for r in db.execute('''
            SELECT p.*, cpl.link_type, cpl.link_note
            FROM projects p
            JOIN contract_project_link cpl ON p.project_id = cpl.project_id
            WHERE cpl.contract_id=?
            ORDER BY p.project_name
        ''', (contract_id,)).fetchall()
    ]
    # Contract files
    files = [
        dict(r)
        for r in db.execute(
            'SELECT * FROM contract_files WHERE contract_id=? ORDER BY upload_time DESC',
            (contract_id,)
        ).fetchall()
    ]
    db.close()
    return vben_response({
        'contract': dict(row),
        'stages': stages,
        'payments': payments,
        'deliverables': deliverables,
        'clauses': clauses,
        'finance': dict(finance) if finance else None,
        'projects': projects,
        'files': files,
    })


@router.post('/{contract_id}/files')
async def upload_contract_file(contract_id: str, file: UploadFile = File(...)):
    """上传合同文件并写入 contract_files 表。"""
    db = get_db()
    row = db.execute('SELECT 1 FROM contracts WHERE contract_id=?', (contract_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Contract not found')

    fid = f"F{uuid.uuid4().hex[:12].upper()}"
    ext = os.path.splitext(file.filename or '')[1].lower()
    save_name = f"{fid}{ext}"
    save_path = UPLOAD_DIR / save_name
    with open(save_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    size = save_path.stat().st_size

    db.execute(
        '''
        INSERT INTO contract_files
            (file_id, contract_id, file_name, file_type, file_path, file_size, upload_time, is_latest, version)
        VALUES (?,?,?,?,?,?, datetime('now'), 1, '1.0')
        ''',
        (fid, contract_id, file.filename or save_name, ext or '', save_name, size),
    )
    db.commit()
    db.close()
    return vben_response({'file_id': fid, 'file_name': file.filename or save_name})


@router.get('/{contract_id}/files/{file_id}/download')
def download_contract_file(contract_id: str, file_id: str):
    """下载合同文件（按 contract_id + file_id 定位）。"""
    db = get_db()
    row = db.execute(
        'SELECT * FROM contract_files WHERE contract_id=? AND file_id=?',
        (contract_id, file_id),
    ).fetchone()
    db.close()
    if not row:
        raise HTTPException(404, 'File not found')
    path = UPLOAD_DIR / row['file_path']
    if not path.exists():
        raise HTTPException(404, 'File missing on disk')
    return FileResponse(str(path), filename=row['file_name'])
