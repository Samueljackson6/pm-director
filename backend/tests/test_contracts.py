"""Tests for the ``GET /api/contracts`` paginated list endpoint.

The response is wrapped by ``vben_list`` so the payload lives under
``body["data"]`` with ``total`` (int) and ``items`` (list) fields.
"""

from fastapi.testclient import TestClient


def test_contracts_paginated(client: TestClient) -> None:
    resp = client.get("/api/contracts", params={"page": 1, "size": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("code") == 0
    data = body.get("data", {})
    assert "total" in data
    assert "items" in data
    assert isinstance(data["total"], int)
    assert isinstance(data["items"], list)
