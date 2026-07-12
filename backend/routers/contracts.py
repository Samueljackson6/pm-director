"""Contract endpoints — list, detail, categories."""

import os
import re
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
        -- 通过 mapping 表链接 SGSC→ZH，确保 finance 数据能匹配到
        LEFT JOIN contract_id_mapping m ON m.project_id_sgsc = c.contract_id
        LEFT JOIN current_finance_view fr ON COALESCE(m.project_id_zh, c.contract_id) = fr.project_id
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
        db.close()
        raise HTTPException(404, 'Contract not found')

    # 通过 contract_id_mapping 查找对应的映射 ID，用于关联表查询
    # 优先采用 ZH 前缀的真实 canonical ID（避免 system_id 占位的 SYS- 映射抢占 fetchone）
    mapped_id = contract_id
    map_row = db.execute(
        'SELECT project_id_zh FROM contract_id_mapping '
        'WHERE (project_id_sgsc=? OR project_id_zh=?) AND project_id_zh LIKE ? LIMIT 1',
        (contract_id, contract_id, 'ZH%')
    ).fetchone()
    if not map_row:
        # 回退：无任何 ZH 映射时，才接受 SYS- 等占位映射
        map_row = db.execute(
            'SELECT project_id_zh FROM contract_id_mapping WHERE project_id_sgsc=? OR project_id_zh=? LIMIT 1',
            (contract_id, contract_id)
        ).fetchone()
    if map_row and map_row[0]:
        mapped_id = map_row[0]
    # 关联表可能以 SGSC 原始 id 或 ZH canonical id 建键，二者都查
    link_ids = list(dict.fromkeys([contract_id, mapped_id]))
    link_q = ','.join('?' * len(link_ids))

    stages = [
        dict(r)
        for r in db.execute(
            f'SELECT * FROM stages WHERE contract_id IN ({link_q}) ORDER BY stage_number', link_ids
        ).fetchall()
    ]
    # 付款：SGSC 与 ZH 双 id 都可能建键；L3 已清除重复 SGSC 付款行，这里直接并集两者。
    # 不再用 NOT LIKE 'SGSC%' 排除，否则会漏掉“仅以 SGSC id 建键”的合法付款。
    _pay_rows = db.execute(
        f'SELECT * FROM payments WHERE contract_id IN ({link_q}) OR project_id IN ({link_q}) ORDER BY payment_id',
        link_ids + link_ids
    ).fetchall()
    _seen = set()
    payments = []
    for r in _pay_rows:
        d = dict(r)
        if d['payment_id'] in _seen:
            continue
        _seen.add(d['payment_id'])
        payments.append(d)
    deliverables = [
        dict(r)
        for r in db.execute(
            f'SELECT * FROM deliverables WHERE contract_id IN ({link_q}) OR project_id IN ({link_q})',
            link_ids + link_ids
        ).fetchall()
    ]
    # 违约/罚款条款
    clauses = [
        dict(r)
        for r in db.execute(
            f'SELECT * FROM contract_clauses WHERE contract_id IN ({link_q}) ORDER BY clause_category',
            link_ids,
        ).fetchall()
    ]
    # 经费预算（科研类）
    budgets = [
        dict(r)
        for r in db.execute(
            f'SELECT * FROM contract_budgets WHERE contract_id IN ({link_q}) ORDER BY category',
            link_ids,
        ).fetchall()
    ]
    # finance: 查询 finance_records 表（字段名统一为 contract_total）
    finance_row = db.execute(
        'SELECT project_id, project_name, customer, contract_amount as contract_total, contract_amount, invoice_total, invoice_unbilled, payment_total, payment_unreceived FROM finance_records WHERE project_id=? OR project_id=? LIMIT 1', (contract_id, mapped_id)
    ).fetchone()
    if not finance_row:
        finance_row = db.execute(
            'SELECT * FROM current_finance_view WHERE project_id=? OR project_id=? LIMIT 1', (contract_id, mapped_id)
        ).fetchone()
    finance = dict(finance_row) if finance_row else None
    # Associated projects
    projects = [
        dict(r)
        for r in db.execute('''
            SELECT p.*, cpl.link_type, cpl.link_note
            FROM projects p
            JOIN contract_project_link cpl ON p.project_id = cpl.project_id
            WHERE cpl.contract_id=? OR cpl.project_id=? OR cpl.contract_id=?
            ORDER BY p.project_name
        ''', (mapped_id, mapped_id, contract_id)).fetchall()
    ]
    # Contract files
    files = [
        dict(r)
        for r in db.execute(
            'SELECT * FROM contract_files WHERE contract_id=? OR contract_id=? ORDER BY upload_time DESC',
            (mapped_id, contract_id)
        ).fetchall()
    ]
    # Invoices linked to this contract
    invoices = [
        dict(r)
        for r in db.execute(
            'SELECT * FROM invoices WHERE project_id=? OR project_id=? ORDER BY invoice_date DESC',
            (mapped_id, contract_id)
        ).fetchall()
    ]
    # 如果合同缺少 service_period，用最后一个阶段的日期兜底
    c = dict(row)
    if not c.get('service_period') and stages:
        last_stage = stages[-1]
        end_time = last_stage.get('end_time') or last_stage.get('expected_end')
        if end_time:
            c['service_period'] = f'预计至 {end_time}'
    # 科研类合同：如果缺少 expiry_date，用最后一个阶段的结束时间兜底
    if not c.get('expiry_date') and c.get('project_type') == '科研类' and stages:
        last_end = None
        for s in reversed(stages):
            end_val = s.get('end_time')
            if end_val:
                last_end = end_val
                break
            # start_time 可能是 "2026-05 至 2026-08" 这样的区间，提取结束部分
            start_val = s.get('start_time') or ''
            m = re.search(r'至\s*(\d{4}-\d{2}(?:-\d{2})?)', start_val)
            if not m:
                m = re.search(r'—\s*(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)', start_val)
            if m:
                last_end = m.group(1)
                break
        if last_end:
            c['expiry_date'] = last_end
    db.close()
    return vben_response({
        'contract': c,
        'stages': stages,
        'payments': payments,
        'deliverables': deliverables,
        'clauses': clauses,
        'budgets': budgets,
        'finance': dict(finance) if finance else None,
        'projects': projects,
        'files': files,
        'invoices': invoices,
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


# ── Team / Personnel ─────────────────────────────────────────

@router.get('/{contract_id}/team')
def get_contract_team(contract_id: str):
    """返回合同关联的团队成员（项目负责人、双方联系人、项目成员）。"""
    db = get_db()
    row = db.execute('SELECT * FROM contracts WHERE contract_id=?', (contract_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Contract not found')

    c = dict(row)

    # 通过 mapping 找 canonical ID
    mapped_id = contract_id
    map_row = db.execute(
        'SELECT project_id_zh FROM contract_id_mapping '
        'WHERE (project_id_sgsc=? OR project_id_zh=?) AND project_id_zh LIKE ? LIMIT 1',
        (contract_id, contract_id, 'ZH%')
    ).fetchone()
    if not map_row:
        map_row = db.execute(
            'SELECT project_id_zh FROM contract_id_mapping WHERE project_id_sgsc=? OR project_id_zh=? LIMIT 1',
            (contract_id, contract_id)
        ).fetchone()
    if map_row and map_row[0]:
        mapped_id = map_row[0]

    link_ids = list(dict.fromkeys([contract_id, mapped_id]))
    link_q = ','.join('?' * len(link_ids))

    # 项目负责人 & 双方联系人（从 contracts 表）
    key_members = []
    if c.get('project_leader'):
        key_members.append({
            'role': 'project_leader',
            'role_label': '项目负责人',
            'person_name': c['project_leader'],
        })
    if c.get('party_a_contact'):
        key_members.append({
            'role': 'party_a_contact',
            'role_label': '甲方联系人',
            'person_name': c['party_a_contact'],
            'phone': c.get('party_a_phone') or '',
        })
    if c.get('party_b_contact'):
        key_members.append({
            'role': 'party_b_contact',
            'role_label': '乙方联系人',
            'person_name': c['party_b_contact'],
            'phone': c.get('party_b_phone') or '',
        })

    # 通过 project_personnel + personnel 表获取正式成员
    team_members = []
    # 查找此合同关联的每个项目 -> 查找项目的人员
    project_rows = db.execute(
        f'SELECT cpl.project_id FROM contract_project_link cpl WHERE cpl.contract_id IN ({link_q})',
        link_ids,
    ).fetchall()
    project_ids = [r['project_id'] for r in project_rows]
    if project_ids:
        proj_q = ','.join('?' * len(project_ids))
        members = db.execute(
            f'''
            SELECT p.person_name, p.phone, p.email, p.department, p.role_tags,
                   pp.role_type, pp.assigned_date, pp.is_active, pp.project_id
            FROM project_personnel pp
            LEFT JOIN personnel p ON pp.person_id = p.person_id
            WHERE pp.project_id IN ({proj_q}) AND pp.is_active = 1
            ORDER BY pp.assigned_date
            ''',
            project_ids,
        ).fetchall()
        for m in members:
            team_members.append(dict(m))

    db.close()
    return vben_response({
        'key_members': key_members,
        'team_members': team_members,
    })


# ── Payment CRUD ──────────────────────────────────────────────

@router.get('/{contract_id}/payments')
def get_contract_payments(contract_id: str):
    """获取合同的付款计划列表。"""
    db = get_db()
    row = db.execute('SELECT 1 FROM contracts WHERE contract_id=?', (contract_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Contract not found')

    mapped_id = contract_id
    map_row = db.execute(
        'SELECT project_id_zh FROM contract_id_mapping '
        'WHERE (project_id_sgsc=? OR project_id_zh=?) AND project_id_zh LIKE ? LIMIT 1',
        (contract_id, contract_id, 'ZH%')
    ).fetchone()
    if map_row and map_row[0]:
        mapped_id = map_row[0]
    link_ids = list(dict.fromkeys([contract_id, mapped_id]))
    link_q = ','.join('?' * len(link_ids))

    _rows = db.execute(
        f'SELECT * FROM payments WHERE contract_id IN ({link_q}) OR project_id IN ({link_q}) ORDER BY payment_id',
        link_ids + link_ids
    ).fetchall()
    _seen = set()
    payments = []
    for r in _rows:
        d = dict(r)
        if d['payment_id'] in _seen:
            continue
        _seen.add(d['payment_id'])
        payments.append(d)
    db.close()
    return vben_response({'payments': payments})


@router.post('/{contract_id}/payments')
def create_contract_payment(contract_id: str, payload: dict):
    """新增付款记录。"""
    import uuid
    db = get_db()
    row = db.execute('SELECT 1 FROM contracts WHERE contract_id=?', (contract_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Contract not found')

    payment_id = payload.get('payment_id') or f'P{uuid.uuid4().hex[:8].upper()}'
    planned_amount = payload.get('planned_amount', 0)
    db.execute(
        '''INSERT OR REPLACE INTO payments
           (payment_id, contract_id, payment_stage, payment_condition,
            planned_amount, planned_date, status, payment_date)
           VALUES (?,?,?,?,?,?,?,?)''',
        (payment_id, contract_id,
         payload.get('payment_stage', ''),
         payload.get('payment_condition', ''),
         planned_amount,
         payload.get('planned_date', ''),
         payload.get('status', 'pending'),
         payload.get('payment_date', ''))
    )
    db.commit()
    db.close()
    return vben_response({'payment_id': payment_id, 'created': True})


@router.put('/{contract_id}/payments/{payment_id}')
def update_contract_payment(contract_id: str, payment_id: str, payload: dict):
    """更新付款记录。"""
    db = get_db()
    existing = db.execute('SELECT 1 FROM payments WHERE payment_id=? AND contract_id=?',
                          (payment_id, contract_id)).fetchone()
    if not existing:
        db.close()
        raise HTTPException(404, 'Payment not found')

    updatable = {'payment_stage', 'payment_condition', 'planned_amount',
                 'planned_date', 'status', 'payment_date'}
    fields = []
    values = []
    for k, v in payload.items():
        if k in updatable and v is not None:
            fields.append(f'{k}=?')
            values.append(v)
    if fields:
        values.append(payment_id)
        values.append(contract_id)
        db.execute(
            f'UPDATE payments SET {", ".join(fields)} WHERE payment_id=? AND contract_id=?',
            values,
        )
        db.commit()
    db.close()
    return vben_response({'payment_id': payment_id, 'updated': True})


@router.delete('/{contract_id}/payments/{payment_id}')
def delete_contract_payment(contract_id: str, payment_id: str):
    """删除付款记录。"""
    db = get_db()
    existing = db.execute('SELECT 1 FROM payments WHERE payment_id=? AND contract_id=?',
                          (payment_id, contract_id)).fetchone()
    if not existing:
        db.close()
        raise HTTPException(404, 'Payment not found')
    db.execute('DELETE FROM payments WHERE payment_id=? AND contract_id=?',
               (payment_id, contract_id))
    db.commit()
    db.close()
    return vben_response({'payment_id': payment_id, 'deleted': True})


# ── CRUD: Update & Create ────────────────────────────────────

@router.put('/{contract_id}')
def update_contract(contract_id: str, payload: dict):
    """更新合同基本信息。"""
    db = get_db()
    row = db.execute('SELECT 1 FROM contracts WHERE contract_id=?', (contract_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Contract not found')

    # 允许更新的字段
    updatable = {
        'project_name', 'official_name', 'project_type', 'project_nature',
        'contract_amount', 'party_a', 'party_b',
        'sign_date', 'expiry_date', 'service_content', 'service_period',
        'project_leader', 'financial_id', 'tax_rate', 'contract_status', 'sgsc_id',
        'party_a_contact', 'party_a_phone', 'party_b_contact', 'party_b_phone',
        'service_method', 'service_location', 'acceptance_criteria',
        'acceptance_method', 'acceptance_location', 'quality_bond_pct',
        'warranty_months', 'sign_location',
    }
    fields = []
    values = []
    for k, v in payload.items():
        if k in updatable and v is not None:
            fields.append(f'{k}=?')
            values.append(v)

    if not fields:
        db.close()
        return vben_response({'contract_id': contract_id, 'updated': False})

    values.append(contract_id)
    db.execute(
        f'UPDATE contracts SET {", ".join(fields)}, updated_at=datetime("now") WHERE contract_id=?',
        values,
    )

    # 处理科研类合同的阶段更新
    if 'stages' in payload and isinstance(payload['stages'], list):
        db.execute('DELETE FROM stages WHERE contract_id=?', (contract_id,))
        for s in payload['stages']:
            stage_id = s.get('stage_id') or f'{contract_id}-阶段{s.get("stage_number","")}'
            db.execute(
                'INSERT OR REPLACE INTO stages (stage_id, contract_id, stage_name, stage_number, start_time, end_time, acceptance_criteria, status) VALUES (?,?,?,?,?,?,?,?)',
                (stage_id, contract_id, s.get('stage_name',''), s.get('stage_number'), s.get('start_time'), s.get('end_time'), s.get('acceptance_criteria',''), s.get('status','pending'))
            )

    # 处理科研类合同的交付物更新
    if 'deliverables' in payload and isinstance(payload['deliverables'], list):
        db.execute('DELETE FROM deliverables WHERE contract_id=?', (contract_id,))
        for d in payload['deliverables']:
            del_id = d.get('deliverable_id') or f'{contract_id}-交付物{payload["deliverables"].index(d)+1}'
            db.execute(
                'INSERT OR REPLACE INTO deliverables (deliverable_id, contract_id, deliverable_name, deliverable_type, status) VALUES (?,?,?,?,?)',
                (del_id, contract_id, d.get('deliverable_name',''), d.get('deliverable_type','报告'), d.get('status','pending'))
            )

    db.commit()
    db.close()
    return vben_response({'contract_id': contract_id, 'updated': True})


@router.post('')
def create_contract(payload: dict):
    """新增合同。"""
    db = get_db()
    contract_id = payload.get('contract_id')
    if not contract_id:
        raise HTTPException(400, 'contract_id is required')

    # 检查是否已存在
    existing = db.execute('SELECT 1 FROM contracts WHERE contract_id=?', (contract_id,)).fetchone()
    if existing:
        db.close()
        raise HTTPException(409, 'Contract already exists')

    required = {'contract_id', 'project_name', 'project_type', 'contract_amount', 'party_a', 'party_b', 'sign_date'}
    missing = required - set(payload.keys())
    if missing:
        db.close()
        raise HTTPException(400, f'Missing required fields: {missing}')

    fields = []
    values = []
    all_fields = [
        'contract_id', 'project_name', 'project_type', 'contract_amount', 'party_a', 'party_b',
        'sign_date', 'expiry_date', 'service_content', 'service_period', 'project_leader',
        'financial_id', 'project_nature', 'official_name', 'sgsc_id', 'contract_status', 'tax_rate',
    ]
    for f in all_fields:
        fields.append(f)
        values.append(payload.get(f))

    placeholders = ', '.join(['?' for _ in fields])
    db.execute(
        f'INSERT INTO contracts ({", ".join(fields)}, created_at, updated_at) VALUES ({placeholders}, datetime("now"), datetime("now"))',
        values,
    )
    db.commit()
    db.close()
    return vben_response({'contract_id': contract_id, 'created': True})
