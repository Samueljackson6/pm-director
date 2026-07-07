"""Tests for the lightweight health probe endpoints.

Covers:
  * ``GET /health``
  * ``GET /api/health``

Neither endpoint touches the database, so they should always return 200
with ``status == "ok"`` and the expected probe keys.
"""

from fastapi.testclient import TestClient


def test_health_root(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "ok"
    assert body.get("service") == "pm-director"
    for key in ("status", "service", "timestamp", "version"):
        assert key in body, f"missing health key: {key}"


def test_health_api(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "ok"
    for key in ("status", "service", "timestamp", "version"):
        assert key in body, f"missing health key: {key}"
