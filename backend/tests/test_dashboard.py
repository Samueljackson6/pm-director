"""Tests for the ``GET /api/dashboard/overview`` aggregation endpoint.

Uses the isolated ``client`` fixture from conftest, which redirects every
``get_db()`` call to a throwaway SQLite database whose minimal schema has
been extended to cover the dashboard query (incl. the ``invoices`` table and
the production-aligned ``current_finance_view``).
"""

from fastapi.testclient import TestClient


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
