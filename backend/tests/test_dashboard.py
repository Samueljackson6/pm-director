"""Tests for the ``GET /api/dashboard/overview`` aggregation endpoint.

Uses the isolated ``client`` fixture from conftest, which redirects every
``get_db()`` call to a throwaway SQLite database whose minimal schema has
been extended to cover the dashboard query (incl. the ``invoices`` table and
the production-aligned ``current_finance_view``).
"""

from fastapi.testclient import TestClient


def _seed_project_execution_data(client: TestClient) -> None:
    """向隔离数据库写入项目执行聚合测试数据。"""
    import backend.database as db_module

    db = db_module.get_db()
    db.executemany(
        "INSERT INTO projects (project_id, project_name, customer_name, "
        "project_status, project_manager, planned_end, risk_level, "
        "overall_progress, updated_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("P-1", "项目一", "客户一", "active", "经理一", "2026-07-01", "high", 40, "2026-07-10", "2026-06-01"),
            ("P-2", "项目二", "客户二", "completed", "", "2026-08-01", "low", 100, "2026-07-09", "2026-05-01"),
        ],
    )
    db.execute(
        "INSERT INTO stages (project_id, stage_number, status, end_time) "
        "VALUES ('P-1', 1, 'in_progress', '2026-07-01')"
    )
    db.execute(
        "INSERT INTO deliverables (project_id, deliverable_id, status) "
        "VALUES ('P-1', 'D-1', 'pending')"
    )
    db.commit()
    db.close()


def test_dashboard_overview_structure(client: TestClient) -> None:
    """The overview endpoint returns code 0 with the documented data shape."""
    resp = client.get("/api/dashboard/overview")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("code") == 0

    data = body.get("data", {})

    # Top-level envelope keys.
    assert "generated_at" in data
    assert "filters" in data

    # summary KPIs.
    summary = data.get("summary", {})
    assert isinstance(summary.get("contract_count"), int)
    assert isinstance(summary.get("invoiced_amount"), (int, float))
    assert isinstance(summary.get("received_amount"), (int, float))
    assert isinstance(summary.get("receipt_rate"), (int, float))
    assert summary.get("currency_unit") == "万元"

    # Collection sections must be present and be lists.
    for key in (
        "contracts_by_type",
        "contracts_by_status",
        "invoice_status_distribution",
        "invoice_monthly",
        "finance_trend",
        "top_customers",
        "recent_contracts",
    ):
        assert key in data, f"missing dashboard key: {key}"
        assert isinstance(data[key], list), f"{key} should be a list"

    # pending_tasks is an object with four integer counters.
    pending = data.get("pending_tasks", {})
    assert isinstance(pending, dict)
    for pt_key in (
        "unmatched_payments",
        "pending_deliverables",
        "overdue_payments",
        "uninvoiced_contracts",
    ):
        assert pt_key in pending, f"missing pending_task key: {pt_key}"
        assert isinstance(pending[pt_key], int)


def test_dashboard_overview_with_project_type(client: TestClient) -> None:
    """An optional ``project_type`` filter is accepted and must not error."""
    resp = client.get(
        "/api/dashboard/overview", params={"project_type": "科研类"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("code") == 0
    assert body.get("data", {}).get("filters", {}).get("project_type") == "科研类"


def test_dashboard_project_execution_aggregation(client: TestClient) -> None:
    """项目执行视图返回聚合指标、分布和最近项目。"""
    _seed_project_execution_data(client)

    resp = client.get("/api/dashboard/overview")
    assert resp.status_code == 200
    execution = resp.json()["data"]["project_execution"]

    assert execution["total_projects"] == 2
    assert execution["active_projects"] == 1
    assert execution["completed_projects"] == 1
    assert execution["high_risk_projects"] == 1
    assert execution["missing_manager_projects"] == 1
    assert execution["overdue_stages"] == 1
    assert execution["pending_deliverables"] == 1
    assert isinstance(execution["status_distribution"], list)
    assert isinstance(execution["risk_distribution"], list)
    assert execution["recent_projects"][0]["project_id"] == "P-1"
