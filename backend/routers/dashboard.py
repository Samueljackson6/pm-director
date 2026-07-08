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

from fastapi import APIRouter, Query

from backend.database import get_db
from backend.models import vben_response

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


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
    db = get_db()

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
    # ------------------------------------------------------------------
    rows = db.execute(
        "SELECT strftime('%Y-%m', invoice_date) as month, "
        "COALESCE(SUM(CASE WHEN invoice_type = '客户开票' "
        "  THEN amount END), 0) / 10000 as invoiced_wan, "
        "COALESCE(SUM(CASE WHEN invoice_type = '客户回款' "
        "  THEN amount END), 0) / 10000 as received_wan "
        "FROM invoices GROUP BY month ORDER BY month"
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

    db.close()

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
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
    }
    return vben_response(data)
