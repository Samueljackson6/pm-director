"""Dashboard aggregation endpoints.

Provides a single ``GET /api/dashboard/overview`` endpoint that returns all
KPI / chart / list data required by the finance dashboard in one request.

Amounts are returned in **万元** (ten-thousand CNY) to match ``/api/stats``:
  * Finance KPIs (invoiced / received / unreceived / sub_*) come from
    ``current_finance_view`` / a direct ``finance_records`` latest-snapshot
    query — the same source used by ``/api/stats``.
  * ``invoices.amount`` is stored in **元**, so it is divided by ``10000``
    when used for status distribution and monthly trends.
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query

from backend.database import get_readonly_db
from backend.models import vben_response

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _table_columns(db: Any, table_name: str) -> set[str]:
    """Return table fields to avoid presenting absent fields as zero values."""
    return {
        str(row["name"])
        for row in db.execute(f"PRAGMA table_info({table_name})").fetchall()
    }


def _latest_data_value(
    db: Any, table_name: str, candidates: tuple[str, ...]
) -> str | None:
    """Read the newest available business timestamp without inventing a value."""
    available = [column for column in candidates if column in _table_columns(db, table_name)]
    if not available:
        return None
    expression = available[0] if len(available) == 1 else f"COALESCE({', '.join(available)})"
    row = db.execute(
        f"SELECT MAX({expression}) AS data_as_of FROM {table_name}"
    ).fetchone()
    return row["data_as_of"] if row and row["data_as_of"] else None


def _action(
    *, action_id: str, category: str, title: str, object_type: str,
    object_id: str | int, reason: str, due_date: str | None,
    owner: str | None, status: str, path: str, query: dict[str, str],
) -> dict[str, Any]:
    """Create an actionable record; unknown owner and due date remain null."""
    return {
        "action_id": action_id,
        "category": category,
        "title": title,
        "object_type": object_type,
        "object_id": str(object_id),
        "reason": reason,
        "due_date": due_date,
        "owner": owner,
        "status": status,
        "target": {"path": path, "query": query},
    }


def _metric(
    key: str, label: str, unit: str, definition: str, source: list[str],
    coverage: str, data_as_of: str | None,
) -> dict[str, Any]:
    """Build reviewable metric metadata; mirrored records remain unverified by default."""
    return {
        "key": key,
        "label": label,
        "unit": unit,
        "definition": definition,
        "source": source,
        "coverage": coverage,
        "verification_status": "pending_verification",
        "data_as_of": data_as_of,
    }


@router.get("/overview")
def get_dashboard_overview(
    period: str = "all",
    from_date: str | None = Query(default=None, alias="from"),
    to: str | None = None,
    project_type: str | None = None,
):
    """Aggregate dashboard overview in a single request.

    Query params (all optional):
      * ``period``       – "all" (default). ytd/year/quarter/month reserved.
      * ``from`` / ``to`` – ISO dates, accepted but ignored in the MVP
                            (snapshot data is weekly, not transactional).
      * ``project_type`` – filters ``contracts`` when provided.

    Returns the Vben-wrapped payload described in the P2 architecture doc
    §1.2.1.
    """
    db = get_readonly_db()

    # Echo the incoming filters back so the frontend can render active chips.
    filters = {
        "period": period,
        "from": from_date,
        "to": to,
        "project_type": project_type,
    }

    # ------------------------------------------------------------------
    # summary — KPI cards
    # ------------------------------------------------------------------
    # Contract base metrics (optionally filtered by project_type).
    type_filter = "WHERE project_type = ?" if project_type else ""
    type_param = (project_type,) if project_type else ()
    contract_row = db.execute(
        f"SELECT COUNT(*) as cnt, COALESCE(SUM(contract_amount), 0) as total "
        f"FROM contracts {type_filter}",
        type_param,
    ).fetchone()
    contract_count = int(contract_row["cnt"])
    contract_total_amount = round(contract_row["total"], 2)

    # Finance KPIs sourced from the per-project latest snapshot view (万元).
    fin = db.execute(
        "SELECT COALESCE(SUM(invoice_total), 0) as inv, "
        "COALESCE(SUM(payment_total), 0) as pay, "
        "COALESCE(SUM(payment_unreceived), 0) as unreceived "
        "FROM current_finance_view"
    ).fetchone()
    invoiced_amount = round(fin["inv"], 2)
    received_amount = round(fin["pay"], 2)
    unreceived_amount = round(fin["unreceived"], 2)

    # Sub-contractor metrics must be read directly from the latest snapshot
    # of finance_records — the view does not expose sub_invoice_total /
    # sub_payment_total.
    fin2 = db.execute(
        "SELECT COALESCE(SUM(sub_invoice_total), 0) as sub_inv, "
        "COALESCE(SUM(sub_payment_total), 0) as sub_pay "
        "FROM finance_records "
        "WHERE record_id IN ("
        "  SELECT MAX(record_id) FROM finance_records GROUP BY project_id)"
    ).fetchone()
    sub_invoiced_amount = round(fin2["sub_inv"], 2)
    sub_paid_amount = round(fin2["sub_pay"], 2)

    # Derived metrics computed in memory.
    receipt_rate = (
        round(received_amount / invoiced_amount * 100, 1) if invoiced_amount else 0
    )
    uninvoiced_amount = round(contract_total_amount - invoiced_amount, 2)

    summary = {
        "contract_count": contract_count,
        "contract_total_amount": contract_total_amount,
        "invoiced_amount": invoiced_amount,
        "received_amount": received_amount,
        "unreceived_amount": unreceived_amount,
        "receipt_rate": receipt_rate,
        "uninvoiced_amount": uninvoiced_amount,
        "sub_invoiced_amount": sub_invoiced_amount,
        "sub_paid_amount": sub_paid_amount,
        "currency_unit": "万元",
    }

    # ------------------------------------------------------------------
    # contracts_by_type — pie chart
    # ------------------------------------------------------------------
    rows = db.execute(
        "SELECT project_type, COUNT(*) as count, "
        "COALESCE(SUM(contract_amount), 0) as amount "
        "FROM contracts GROUP BY project_type ORDER BY amount DESC"
    ).fetchall()
    contracts_by_type = [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # contracts_by_status — pie / bar chart
    # ------------------------------------------------------------------
    rows = db.execute(
        "SELECT contract_status, COUNT(*) as count, "
        "COALESCE(SUM(contract_amount), 0) as amount "
        "FROM contracts GROUP BY contract_status"
    ).fetchall()
    contracts_by_status = [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # invoice_status_distribution — pie chart
    # invoices.amount is in 元 → /10000 to 万元
    # ------------------------------------------------------------------
    rows = db.execute(
        "SELECT status, COUNT(*) as count, "
        "COALESCE(SUM(amount), 0) / 10000 as amount_wan "
        "FROM invoices GROUP BY status"
    ).fetchall()
    invoice_status_distribution = [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # invoice_monthly — line chart (开票 vs 回款, 万元)
    # 过滤空日期记录，避免横坐标出现 null 值
    # ------------------------------------------------------------------
    rows = db.execute(
        "SELECT strftime('%Y-%m', invoice_date) as month, "
        "COALESCE(SUM(CASE WHEN invoice_type = '客户开票' "
        "  THEN amount END), 0) / 10000 as invoiced_wan, "
        "COALESCE(SUM(CASE WHEN invoice_type = '客户回款' "
        "  THEN amount END), 0) / 10000 as received_wan "
        "FROM invoices WHERE invoice_date IS NOT NULL AND invoice_date != '' "
        "GROUP BY month ORDER BY month"
    ).fetchall()
    invoice_monthly = [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # finance_trend — line chart (snapshot per batch, 万元)
    # ------------------------------------------------------------------
    rows = db.execute(
        "SELECT batch_id, import_time, "
        "COALESCE(SUM(invoice_total), 0) as invoiced_wan, "
        "COALESCE(SUM(payment_total), 0) as received_wan "
        "FROM finance_records WHERE batch_id IS NOT NULL "
        "GROUP BY batch_id ORDER BY import_time"
    ).fetchall()
    finance_trend = [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # top_customers — bar chart
    # ------------------------------------------------------------------
    rows = db.execute(
        "SELECT party_a as customer, COUNT(*) as count, "
        "COALESCE(SUM(contract_amount), 0) as total_amount "
        "FROM contracts WHERE party_a IS NOT NULL AND party_a != '' "
        "GROUP BY party_a ORDER BY total_amount DESC LIMIT 10"
    ).fetchall()
    top_customers = [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # pending_tasks — to-do cards
    # ------------------------------------------------------------------
    unmatched_payments = db.execute(
        "SELECT COUNT(*) FROM invoices WHERE payment_status = '未匹配'"
    ).fetchone()[0]
    # deliverables real enum is {pending, completed}; treat any terminal
    # state (completed / 已交付 / 已验收) as done, everything else as pending.
    pending_deliverables = db.execute(
        "SELECT COUNT(*) FROM deliverables "
        "WHERE status NOT IN ('completed', '已交付', '已验收')"
    ).fetchone()[0]
    # payments.planned_date is the scheduled/planned payment date.
    # A payment is overdue when its planned date has passed
    # and it is not yet fully paid.
    overdue_payments = db.execute(
        "SELECT COUNT(*) FROM payments "
        "WHERE planned_amount > COALESCE(paid_amount, 0) "
        "AND planned_date IS NOT NULL "
        "AND planned_date < date('now')"
    ).fetchone()[0]
    uninvoiced_contracts = db.execute(
        "SELECT COUNT(*) FROM contracts "
        "LEFT JOIN current_finance_view "
        "  ON contracts.contract_id = current_finance_view.project_id "
        "WHERE contracts.contract_amount > "
        "  COALESCE(current_finance_view.invoice_total, 0)"
    ).fetchone()[0]
    pending_tasks = {
        "unmatched_payments": int(unmatched_payments),
        "pending_deliverables": int(pending_deliverables),
        "overdue_payments": int(overdue_payments),
        "uninvoiced_contracts": int(uninvoiced_contracts),
    }

    # ------------------------------------------------------------------
    # action queues ? every record retains an object ID and a target route.
    # ------------------------------------------------------------------
    task_actions: list[dict[str, Any]] = []
    risk_actions: list[dict[str, Any]] = []
    verification_actions: list[dict[str, Any]] = []

    for row in db.execute(
        "SELECT invoice_id FROM invoices "
        "WHERE invoice_type = '客户回款' AND payment_status = '未匹配' "
        "ORDER BY invoice_date DESC LIMIT 8"
    ).fetchall():
        task_actions.append(
            _action(
                action_id=f"unmatched-receipt-{row['invoice_id']}",
                category="task",
                title="核对未匹配回款",
                object_type="invoice",
                object_id=row["invoice_id"],
                reason="客户回款记录尚未建立发票关联。",
                due_date=None,
                owner=None,
                status="pending_verification",
                path="/customer-finance/invoice-detail",
                query={"id": str(row["invoice_id"])},
            )
        )

    deliverable_columns = _table_columns(db, "deliverables")
    deliverable_due_field = "planned_date" if "planned_date" in deliverable_columns else "NULL"
    deliverable_order = (
        "CASE WHEN planned_date IS NULL OR planned_date = '' THEN 1 ELSE 0 END, planned_date ASC"
        if "planned_date" in deliverable_columns
        else "deliverable_id ASC"
    )
    for row in db.execute(
        "SELECT deliverable_id, contract_id, project_id, "
        f"{deliverable_due_field} AS planned_date FROM deliverables "
        "WHERE status NOT IN ('completed', '已交付', '已验收') "
        f"ORDER BY {deliverable_order} LIMIT 8"
    ).fetchall():
        parent_id = row["project_id"] or row["contract_id"]
        if parent_id:
            task_actions.append(
                _action(
                    action_id=f"pending-deliverable-{row['deliverable_id']}",
                    category="task",
                    title="推进待交付成果",
                    object_type="deliverable",
                    object_id=row["deliverable_id"],
                    reason="交付物尚未标记为已交付或已验收。",
                    due_date=row["planned_date"],
                    owner=None,
                    status="pending",
                    path="/projects/detail" if row["project_id"] else "/contracts/detail",
                    query={"id": str(parent_id)},
                )
            )

    for row in db.execute(
        "SELECT payment_id, contract_id, project_id, planned_date FROM payments "
        "WHERE planned_amount > COALESCE(paid_amount, 0) "
        "AND planned_date IS NOT NULL AND planned_date < date('now') "
        "ORDER BY planned_date ASC LIMIT 8"
    ).fetchall():
        parent_id = row["contract_id"] or row["project_id"]
        if parent_id:
            risk_actions.append(
                _action(
                    action_id=f"overdue-payment-{row['payment_id']}",
                    category="risk",
                    title="跟进逾期付款条件",
                    object_type="payment",
                    object_id=row["payment_id"],
                    reason="计划付款日已过，且计划金额尚未全部支付。",
                    due_date=row["planned_date"],
                    owner=None,
                    status="overdue",
                    path="/contracts/detail" if row["contract_id"] else "/projects/detail",
                    query={"id": str(parent_id)},
                )
            )

    for row in db.execute(
        "SELECT c.contract_id FROM contracts c "
        "LEFT JOIN current_finance_view cv ON c.contract_id = cv.project_id "
        "WHERE c.contract_amount > COALESCE(cv.invoice_total, 0) "
        "ORDER BY c.contract_amount DESC LIMIT 8"
    ).fetchall():
        risk_actions.append(
            _action(
                action_id=f"uninvoiced-contract-{row['contract_id']}",
                category="risk",
                title="核对合同开票缺口",
                object_type="contract",
                object_id=row["contract_id"],
                reason="合同金额高于当前财务快照中的累计开票金额。",
                due_date=None,
                owner=None,
                status="pending_verification",
                path="/contracts/detail",
                query={"id": str(row["contract_id"])},
            )
        )

    for row in db.execute(
        "SELECT project_id FROM projects "
        "WHERE project_manager IS NULL OR TRIM(project_manager) = '' "
        "ORDER BY COALESCE(updated_at, created_at) DESC LIMIT 8"
    ).fetchall():
        verification_actions.append(
            _action(
                action_id=f"missing-project-manager-{row['project_id']}",
                category="verification",
                title="补充项目责任人",
                object_type="project",
                object_id=row["project_id"],
                reason="项目记录未填写项目经理，责任归属无法核验。",
                due_date=None,
                owner=None,
                status="pending_verification",
                path="/projects/detail",
                query={"id": str(row["project_id"])},
            )
        )

    if "ocr_doc_path" in _table_columns(db, "contracts"):
        for row in db.execute(
            "SELECT contract_id FROM contracts "
            "WHERE ocr_doc_path IS NULL OR TRIM(ocr_doc_path) = '' LIMIT 8"
        ).fetchall():
            verification_actions.append(
                _action(
                    action_id=f"missing-contract-text-{row['contract_id']}",
                    category="verification",
                    title="补充合同文本派生层",
                    object_type="contract",
                    object_id=row["contract_id"],
                    reason="未关联 OCR 文本路径，条款核验需回到合同原件或补齐文本派生层。",
                    due_date=None,
                    owner=None,
                    status="pending_verification",
                    path="/contracts/detail",
                    query={"id": str(row["contract_id"])},
                )
            )

    if "verification_status" in _table_columns(db, "invoices"):
        for row in db.execute(
            "SELECT invoice_id FROM invoices "
            "WHERE verification_status IS NULL OR TRIM(verification_status) = '' "
            "ORDER BY invoice_date DESC LIMIT 8"
        ).fetchall():
            verification_actions.append(
                _action(
                    action_id=f"unverified-invoice-{row['invoice_id']}",
                    category="verification",
                    title="核验发票来源与状态",
                    object_type="invoice",
                    object_id=row["invoice_id"],
                    reason="发票记录未填写核验状态，不能作为已确认财务事实使用。",
                    due_date=None,
                    owner=None,
                    status="pending_verification",
                    path="/customer-finance/invoice-detail",
                    query={"id": str(row["invoice_id"])},
                )
            )

    # recent_contracts — table
    # ------------------------------------------------------------------
    rows = db.execute(
        "SELECT c.contract_id, c.project_name, c.contract_amount, c.party_a, "
        "c.sign_date, c.project_type, c.contract_status, "
        "COALESCE(cv.invoice_total, 0) as invoice_total, "
        "COALESCE(cv.payment_total, 0) as payment_total "
        "FROM contracts c "
        "LEFT JOIN current_finance_view cv "
        "  ON c.contract_id = cv.project_id "
        "ORDER BY c.sign_date DESC LIMIT 10"
    ).fetchall()
    recent_contracts = [dict(r) for r in rows]

    # project_execution：项目执行驾驶舱聚合数据。
    project_metrics = db.execute(
        "SELECT COUNT(*) AS total_projects, "
        "SUM(CASE WHEN COALESCE(project_status, '') NOT IN ('completed', '已完成') "
        "THEN 1 ELSE 0 END) AS active_projects, "
        "SUM(CASE WHEN project_status IN ('completed', '已完成') "
        "THEN 1 ELSE 0 END) AS completed_projects, "
        "SUM(CASE WHEN risk_level IN ('high', '高') THEN 1 ELSE 0 END) AS high_risk_projects, "
        "SUM(CASE WHEN project_manager IS NULL OR TRIM(project_manager) = '' "
        "THEN 1 ELSE 0 END) AS missing_manager_projects "
        "FROM projects"
    ).fetchone()
    overdue_stages = db.execute(
        "SELECT COUNT(*) FROM stages "
        "WHERE status NOT IN ('completed', '已完成') "
        "AND end_time IS NOT NULL AND date(end_time) IS NOT NULL "
        "AND date(end_time) < date('now')"
    ).fetchone()[0]
    pending_project_deliverables = db.execute(
        "SELECT COUNT(*) FROM deliverables "
        "WHERE status NOT IN ('completed', '已交付', '已验收')"
    ).fetchone()[0]
    status_distribution = [
        dict(row)
        for row in db.execute(
            "SELECT COALESCE(project_status, '') AS status, COUNT(*) AS count "
            "FROM projects GROUP BY project_status ORDER BY count DESC"
        ).fetchall()
    ]
    risk_distribution = [
        dict(row)
        for row in db.execute(
            "SELECT COALESCE(risk_level, '') AS risk_level, COUNT(*) AS count "
            "FROM projects GROUP BY risk_level ORDER BY count DESC"
        ).fetchall()
    ]
    recent_projects = [
        dict(row)
        for row in db.execute(
            "SELECT project_id, project_name, customer_name, project_status, "
            "COALESCE(risk_level, '') AS risk_level, "
            "COALESCE(overall_progress, 0) AS overall_progress, "
            "COALESCE(project_manager, '') AS project_manager, "
            "COALESCE(planned_end, '') AS planned_end, "
            "COALESCE(total_contract_amount, 0) AS total_contract_amount "
            "FROM projects ORDER BY COALESCE(updated_at, created_at) DESC LIMIT 10"
        ).fetchall()
    ]
    project_execution = {
        "total_projects": int(project_metrics["total_projects"] or 0),
        "active_projects": int(project_metrics["active_projects"] or 0),
        "completed_projects": int(project_metrics["completed_projects"] or 0),
        "high_risk_projects": int(project_metrics["high_risk_projects"] or 0),
        "missing_manager_projects": int(project_metrics["missing_manager_projects"] or 0),
        "overdue_stages": int(overdue_stages),
        "pending_deliverables": int(pending_project_deliverables),
        "status_distribution": status_distribution,
        "risk_distribution": risk_distribution,
        "recent_projects": recent_projects,
    }

    contract_as_of = _latest_data_value(
        db, "contracts", ("updated_at", "sign_date", "created_at")
    )
    finance_as_of = _latest_data_value(db, "finance_records", ("import_time",))
    invoice_as_of = _latest_data_value(db, "invoices", ("invoice_date", "created_at"))
    project_as_of = _latest_data_value(
        db, "projects", ("updated_at", "planned_end", "created_at")
    )
    finance_snapshot_count = int(
        db.execute("SELECT COUNT(*) FROM current_finance_view").fetchone()[0]
    )
    invoice_count = int(db.execute("SELECT COUNT(*) FROM invoices").fetchone()[0])
    project_count = int(db.execute("SELECT COUNT(*) FROM projects").fetchone()[0])

    # Recent changes only use stored business timestamps; no synthetic activity stream.
    recent_changes: list[dict[str, Any]] = []
    contract_columns = _table_columns(db, "contracts")
    contract_changed_at = (
        "COALESCE(updated_at, sign_date, created_at)"
        if "updated_at" in contract_columns and "created_at" in contract_columns
        else "sign_date"
    )
    contract_title = (
        "COALESCE(official_name, project_name, contract_id)"
        if "official_name" in contract_columns
        else "COALESCE(project_name, contract_id)"
    )
    for row in db.execute(
        "SELECT contract_id, "
        f"{contract_title} AS title, {contract_changed_at} AS changed_at FROM contracts "
        f"ORDER BY {contract_changed_at} DESC LIMIT 6"
    ).fetchall():
        recent_changes.append(
            {
                "object_type": "contract",
                "object_id": str(row["contract_id"]),
                "title": row["title"] or str(row["contract_id"]),
                "changed_at": row["changed_at"],
                "change_type": "合同系统记录时间",
                "target": {"path": "/contracts/detail", "query": {"id": str(row["contract_id"]) }},
            }
        )

    project_columns = _table_columns(db, "projects")
    project_changed_at = (
        "COALESCE(updated_at, created_at)"
        if "updated_at" in project_columns and "created_at" in project_columns
        else "planned_end"
    )
    for row in db.execute(
        "SELECT project_id, COALESCE(project_name, project_id) AS title, "
        f"{project_changed_at} AS changed_at FROM projects "
        f"ORDER BY {project_changed_at} DESC LIMIT 6"
    ).fetchall():
        recent_changes.append(
            {
                "object_type": "project",
                "object_id": str(row["project_id"]),
                "title": row["title"] or str(row["project_id"]),
                "changed_at": row["changed_at"],
                "change_type": "项目系统记录时间",
                "target": {"path": "/projects/detail", "query": {"id": str(row["project_id"]) }},
            }
        )
    recent_changes.sort(key=lambda item: item["changed_at"] or "", reverse=True)
    recent_changes = recent_changes[:10]

    generated_at = datetime.now(timezone.utc).isoformat()
    data_contract = {
        "generated_at": generated_at,
        "metrics": [
            _metric(
                "contract_total_amount", "合同总额", "万元",
                "合同主档 contract_amount 合计。",
                ["contracts.contract_amount"],
                f"当前筛选覆盖 {contract_count} 条合同系统记录。", contract_as_of,
            ),
            _metric(
                "invoiced_amount", "累计开票", "万元",
                "每个项目最新财务快照中的 invoice_total 合计。",
                ["current_finance_view.invoice_total"],
                f"覆盖 {finance_snapshot_count} 个财务项目快照。", finance_as_of,
            ),
            _metric(
                "received_amount", "累计回款", "万元",
                "每个项目最新财务快照中的 payment_total 合计。",
                ["current_finance_view.payment_total"],
                f"覆盖 {finance_snapshot_count} 个财务项目快照。", finance_as_of,
            ),
            _metric(
                "unreceived_amount", "未回款", "万元",
                "每个项目最新财务快照中的 payment_unreceived 合计。",
                ["current_finance_view.payment_unreceived"],
                f"覆盖 {finance_snapshot_count} 个财务项目快照。", finance_as_of,
            ),
            _metric(
                "receipt_rate", "回款率", "%",
                "累计回款除以累计开票；累计开票为零时返回 0。",
                ["current_finance_view.payment_total", "current_finance_view.invoice_total"],
                f"覆盖 {finance_snapshot_count} 个财务项目快照。", finance_as_of,
            ),
        ],
        "sources": [
            {
                "key": "contract_master",
                "label": "合同系统记录",
                "source": ["contracts"],
                "coverage": f"{contract_count} 条合同记录",
                "verification_status": "pending_verification",
                "data_as_of": contract_as_of,
            },
            {
                "key": "finance_snapshot",
                "label": "财务快照",
                "source": ["current_finance_view", "finance_records"],
                "coverage": f"{finance_snapshot_count} 个项目最新快照",
                "verification_status": "pending_verification",
                "data_as_of": finance_as_of,
            },
            {
                "key": "invoice_records",
                "label": "发票系统记录",
                "source": ["invoices"],
                "coverage": f"{invoice_count} 条发票记录",
                "verification_status": "pending_verification",
                "data_as_of": invoice_as_of,
            },
            {
                "key": "project_records",
                "label": "项目系统记录",
                "source": ["projects"],
                "coverage": f"{project_count} 条项目记录",
                "verification_status": "pending_verification",
                "data_as_of": project_as_of,
            },
        ],
        "verification_summary": {
            "status": "pending_verification",
            "pending_action_count": len(verification_actions),
            "description": "当前系统记录为镜像与增强层；关键金额、来源和映射仍需按对象回溯原件或运营表核验。",
        },
    }

    data = {
        "generated_at": generated_at,
        "filters": filters,
        "summary": summary,
        "contracts_by_type": contracts_by_type,
        "contracts_by_status": contracts_by_status,
        "invoice_status_distribution": invoice_status_distribution,
        "invoice_monthly": invoice_monthly,
        "finance_trend": finance_trend,
        "top_customers": top_customers,
        "pending_tasks": pending_tasks,
        "recent_contracts": recent_contracts,
        "recent_changes": recent_changes,
        "project_execution": project_execution,
        "task_actions": task_actions,
        "risk_actions": risk_actions,
        "verification_actions": verification_actions,
        "data_contract": data_contract,
    }
    db.close()
    return vben_response(data)
