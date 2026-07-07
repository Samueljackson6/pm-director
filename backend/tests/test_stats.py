"""Tests for the ``GET /api/stats`` statistics endpoint.

The response is wrapped by ``vben_response`` so the payload lives under
``body["data"]``. We assert the endpoint returns 200 and that the
``contract_count`` / ``total_amount`` fields are present and numeric.
"""

from fastapi.testclient import TestClient


def test_stats_structure(client: TestClient) -> None:
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("code") == 0
    data = body.get("data", {})
    assert "contract_count" in data
    assert "total_amount" in data
    assert isinstance(data["contract_count"], int)
    assert isinstance(data["total_amount"], (int, float))
