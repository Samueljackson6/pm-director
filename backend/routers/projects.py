"""Project management endpoints — list, detail, stages, payments, deliverables, progress."""

from fastapi import APIRouter, HTTPException

from backend.database import get_db
from backend.models import vben_response, vben_list

router = APIRouter(prefix="/api/projects", tags=["projects"])

# ── Sort mapping ──────────────────────────────────────────────
_SORT_MAP = {
    'amount_desc': 'p.total_contract_amount DESC',
    'amount_asc': 'p.total_contract_amount ASC',
    'name': 'p.project_name ASC',
    'date_desc': "COALESCE(p.planned_start, '') DESC",
    'date_asc': "COALESCE(p.planned_start, '') ASC",
    'progress_desc': 'p.overall_progress DESC',
    'progress_asc': 'p.overall_progress ASC',
}


@router.get('')
def get_projects(
    page: int = 1,
    size: int = 20,
    search: str = '',
    status: str = '',
    project_type: str = '',
    manager: str = '',
    sort: str = 'amount_desc',
):
    """Paginated project list with search, filter, and sort."""
    db = get_db()
    conditions = []
    params = []

    if search:
        conditions.append("(p.project_name LIKE ? OR p.customer_name LIKE ?)")
        like = f'%{search}%'
        params.extend([like, like])

    if status:
        conditions.append('p.project_status = ?')
        params.append(status)

    if project_type:
        conditions.append('p.project_type = ?')
        params.append(project_type)

    if manager:
        conditions.append(
            "(p.project_manager LIKE ? OR p.tech_lead LIKE ? OR p.sales_lead LIKE ?)"
        )
        like = f'%{manager}%'
        params.extend([like, like, like])

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
    order = _SORT_MAP.get(sort, _SORT_MAP['amount_desc'])
    offset = (page - 1) * size

    total = db.execute(f'SELECT COUNT(*) FROM projects p {where}', params).fetchone()[0]
    rows = db.execute(
        f'SELECT p.* FROM projects p {where} ORDER BY {order} LIMIT ? OFFSET ?',
        params + [size, offset],
    ).fetchall()
    db.close()
    return vben_list(page, size, total, [dict(r) for r in rows])


@router.get('/{project_id}')
def get_project(project_id: str):
    """Project detail with linked contracts, stages summary, payment summary."""
    db = get_db()
    row = db.execute('SELECT * FROM projects WHERE project_id=?', (project_id,)).fetchone()
    if not row:
        raise HTTPException(404, 'Project not found')

    project = dict(row)

    # Linked contracts
    contracts = [
        dict(r)
        for r in db.execute(
            '''
            SELECT c.*, cpl.link_type, cpl.link_note
            FROM contract_project_link cpl
            LEFT JOIN contracts c ON cpl.contract_id = c.contract_id
            WHERE cpl.project_id = ?
            ORDER BY c.contract_amount DESC
            ''',
            (project_id,),
        ).fetchall()
    ]

    # Stages summary (counts + latest)
    stage_statuses = db.execute(
        '''
        SELECT status, COUNT(*) as cnt
        FROM stages WHERE project_id = ?
        GROUP BY status
        ''',
        (project_id,),
    ).fetchall()
    stage_summary = {s['status']: s['cnt'] for s in stage_statuses}

    # Payment summary
    payment_row = db.execute(
        '''
        SELECT
            COUNT(*) as total_count,
            COALESCE(SUM(planned_amount), 0) as total_planned,
            COALESCE(SUM(paid_amount), 0) as total_paid,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count
        FROM payments WHERE project_id = ?
        ''',
        (project_id,),
    ).fetchone()

    # Deliverables summary
    deliv_statuses = db.execute(
        '''
        SELECT status, COUNT(*) as cnt
        FROM deliverables WHERE project_id = ?
        GROUP BY status
        ''',
        (project_id,),
    ).fetchall()
    deliverable_summary = {d['status']: d['cnt'] for d in deliv_statuses}

    db.close()
    return vben_response({
        'project': project,
        'contracts': contracts,
        'stage_summary': stage_summary,
        'payment_summary': dict(payment_row),
        'deliverable_summary': deliverable_summary,
    })


@router.get('/{project_id}/stages')
def get_project_stages(project_id: str):
    """Project stages with status."""
    db = get_db()
    row = db.execute('SELECT 1 FROM projects WHERE project_id=?', (project_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Project not found')
    stages = [
        dict(r)
        for r in db.execute(
            'SELECT * FROM stages WHERE project_id=? ORDER BY stage_number',
            (project_id,),
        ).fetchall()
    ]
    db.close()
    return vben_response({'stages': stages})


@router.get('/{project_id}/payments')
def get_project_payments(project_id: str):
    """Project payments."""
    db = get_db()
    row = db.execute('SELECT 1 FROM projects WHERE project_id=?', (project_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Project not found')
    payments = [
        dict(r)
        for r in db.execute(
            'SELECT * FROM payments WHERE project_id=? ORDER BY payment_id',
            (project_id,),
        ).fetchall()
    ]
    db.close()
    return vben_response({'payments': payments})


@router.get('/{project_id}/deliverables')
def get_project_deliverables(project_id: str):
    """Project deliverables."""
    db = get_db()
    row = db.execute('SELECT 1 FROM projects WHERE project_id=?', (project_id,)).fetchone()
    if not row:
        db.close()
        raise HTTPException(404, 'Project not found')
    deliverables = [
        dict(r)
        for r in db.execute(
            'SELECT * FROM deliverables WHERE project_id=? ORDER BY deliverable_id',
            (project_id,),
        ).fetchall()
    ]
    db.close()
    return vben_response({'deliverables': deliverables})


@router.get('/{project_id}/progress')
def get_project_progress(project_id: str):
    """Computed progress: stages, payments, deliverables, overall."""
    db = get_db()

    # Stage progress
    stage_rows = db.execute(
        'SELECT status, COUNT(*) as cnt FROM stages WHERE project_id=? GROUP BY status',
        (project_id,),
    ).fetchall()
    total_stages = sum(r['cnt'] for r in stage_rows)
    stage_progress = {r['status']: r['cnt'] for r in stage_rows}
    stage_rate = (
        round(
            (stage_progress.get('completed', 0) + stage_progress.get('delivered', 0))
            / total_stages * 100,
            1,
        )
        if total_stages
        else 0
    )

    # Payment progress
    pay_row = db.execute(
        'SELECT COALESCE(SUM(planned_amount),0) as planned, COALESCE(SUM(paid_amount),0) as paid FROM payments WHERE project_id=?',
        (project_id,),
    ).fetchone()
    payment_rate = round(pay_row['paid'] / pay_row['planned'] * 100, 1) if pay_row['planned'] else 0

    # Deliverable progress
    deliv_rows = db.execute(
        'SELECT status, COUNT(*) as cnt FROM deliverables WHERE project_id=? GROUP BY status',
        (project_id,),
    ).fetchall()
    total_deliv = sum(r['cnt'] for r in deliv_rows)
    deliv_progress = {r['status']: r['cnt'] for r in deliv_rows}
    deliv_rate = (
        round(
            (deliv_progress.get('completed', 0) + deliv_progress.get('delivered', 0))
            / total_deliv * 100,
            1,
        )
        if total_deliv
        else 0
    )

    # Overall progress (weighted: 40% stages + 30% payments + 30% deliverables)
    overall = round(stage_rate * 0.4 + payment_rate * 0.3 + deliv_rate * 0.3, 1)

    db.close()
    return vben_response({
        'stage_progress': {
            'total': total_stages,
            'by_status': stage_progress,
            'rate': stage_rate,
        },
        'payment_progress': {
            'planned': round(pay_row['planned'], 2),
            'paid': round(pay_row['paid'], 2),
            'rate': payment_rate,
        },
        'deliverable_progress': {
            'total': total_deliv,
            'by_status': deliv_progress,
            'rate': deliv_rate,
        },
        'overall': overall,
    })
