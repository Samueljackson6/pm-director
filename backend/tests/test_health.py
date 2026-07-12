"""健康检查、就绪检查与 CORS 白名单测试。"""

import sqlite3

from fastapi.testclient import TestClient

import backend.database as database


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


def test_ready_returns_200_when_database_is_accessible(client: TestClient, monkeypatch) -> None:
    class FakeConnection:
        closed = False

        def execute(self, query: str) -> None:
            assert query == "SELECT 1"

        def close(self) -> None:
            self.closed = True

    connection = FakeConnection()
    monkeypatch.setattr(database, "get_db", lambda: connection)

    resp = client.get("/ready")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ready"}
    assert connection.closed is True


def test_ready_returns_503_when_database_is_unavailable(client: TestClient, monkeypatch) -> None:
    def failing_get_db():
        raise sqlite3.Error("database unavailable")

    monkeypatch.setattr(database, "get_db", failing_get_db)

    resp = client.get("/ready")

    assert resp.status_code == 503
    assert resp.json() == {"detail": "database unavailable"}


def test_cors_allows_only_explicit_local_frontend_origins(client: TestClient) -> None:
    for origin in (
        "http://localhost:18090",
        "http://localhost:8900",
        "http://localhost:5777",
    ):
        resp = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == origin
        assert resp.headers.get("access-control-allow-origin") != "*"


def test_cors_rejects_unlisted_origin(client: TestClient) -> None:
    resp = client.options(
        "/health",
        headers={
            "Origin": "https://unlisted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert resp.headers.get("access-control-allow-origin") != "*"
    assert "access-control-allow-origin" not in resp.headers
