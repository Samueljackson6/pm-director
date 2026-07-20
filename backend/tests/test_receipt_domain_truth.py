from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers import receipts as receipts_router


def _create_schema(db_path: Path, *, with_link_table: bool = True) -> None:
    schema = """
    CREATE TABLE receipts (
        receipt_id INTEGER PRIMARY KEY,
        project_id TEXT,
        receipt_date TEXT,
        amount REAL
    );
    """
    if with_link_table:
        schema += """
        CREATE TABLE invoice_receipt_link (
            invoice_id INTEGER,
            receipt_id INTEGER,
            link_amount REAL
        );
        """
    with sqlite3.connect(db_path) as db:
        db.executescript(schema)


@pytest.fixture
def receipt_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "receipts.db"
    _create_schema(db_path)

    def get_test_db() -> sqlite3.Connection:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        return db

    app = FastAPI()
    app.state.receipt_db_path = str(db_path)
    app.include_router(receipts_router.router)
    monkeypatch.setattr(receipts_router, "get_db", get_test_db)
    with TestClient(app) as client:
        yield client


def _db_path(client: TestClient) -> Path:
    return Path(client.app.state.receipt_db_path)


def _seed_receipts(db_path: Path) -> None:
    with sqlite3.connect(db_path) as db:
        db.executemany(
            "INSERT INTO receipts (receipt_id, project_id, receipt_date, amount) VALUES (?, ?, ?, ?)",
            [
                (1, "P-A", "2026-07-03", 100.0),
                (2, "P-A", "2026-07-02", 200.0),
                (3, "P-B", "2026-07-01", 900.0),
            ],
        )
        db.executemany(
            "INSERT INTO invoice_receipt_link (invoice_id, receipt_id, link_amount) VALUES (?, ?, ?)",
            [
                (11, 1, 40.0),
                (12, 1, 90.0),
                (13, 2, 50.0),
                (14, 3, 900.0),
            ],
        )


def test_receipt_summary_uses_all_filtered_rows_not_current_page_and_caps_each_receipt(
    receipt_client: TestClient,
) -> None:
    _seed_receipts(_db_path(receipt_client))

    response = receipt_client.get("/api/receipts", params={"project_id": "P-A", "page": 1, "size": 1})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["summary"] == {
        "currency_unit": "元",
        "status": "available",
        "receipt_total": 300.0,
        "matched_total": 150.0,
        "unmatched_total": 150.0,
    }


def test_receipt_summary_declares_known_zero_when_link_table_exists(receipt_client: TestClient) -> None:
    with sqlite3.connect(_db_path(receipt_client)) as db:
        db.execute(
            "INSERT INTO receipts (receipt_id, project_id, receipt_date, amount) VALUES (?, ?, ?, ?)",
            (1, "P-ZERO", "2026-07-01", 0.0),
        )

    response = receipt_client.get("/api/receipts", params={"project_id": "P-ZERO"})

    assert response.status_code == 200
    assert response.json()["data"]["summary"] == {
        "currency_unit": "元",
        "status": "available",
        "receipt_total": 0.0,
        "matched_total": 0.0,
        "unmatched_total": 0.0,
    }


def test_receipt_summary_marks_pending_when_link_table_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "receipts-without-links.db"
    _create_schema(db_path, with_link_table=False)
    with sqlite3.connect(db_path) as db:
        db.execute(
            "INSERT INTO receipts (receipt_id, project_id, receipt_date, amount) VALUES (?, ?, ?, ?)",
            (1, "P-MISSING", "2026-07-01", 100.0),
        )

    def get_test_db() -> sqlite3.Connection:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        return db

    app = FastAPI()
    app.include_router(receipts_router.router)
    monkeypatch.setattr(receipts_router, "get_db", get_test_db)
    with TestClient(app) as client:
        response = client.get("/api/receipts", params={"project_id": "P-MISSING"})

    assert response.status_code == 200
    assert response.json()["data"]["summary"] == {
        "currency_unit": "元",
        "status": "pending_verification",
        "receipt_total": 100.0,
        "matched_total": None,
        "unmatched_total": None,
    }


@pytest.mark.parametrize(
    ("amount", "expected_total"),
    [(None, None), (-1.0, None)],
    ids=["null-receipt", "negative-receipt"],
)
def test_receipt_summary_marks_pending_for_null_or_negative_receipt_amount(
    receipt_client: TestClient,
    amount: float | None,
    expected_total: float | None,
) -> None:
    with sqlite3.connect(_db_path(receipt_client)) as db:
        db.execute(
            "INSERT INTO receipts (receipt_id, project_id, receipt_date, amount) VALUES (?, ?, ?, ?)",
            (1, "P-INVALID-RECEIPT", "2026-07-01", amount),
        )

    response = receipt_client.get("/api/receipts", params={"project_id": "P-INVALID-RECEIPT"})

    assert response.status_code == 200
    summary = response.json()["data"]["summary"]
    assert summary["status"] == "pending_verification"
    assert summary["receipt_total"] == expected_total
    assert summary["matched_total"] is None
    assert summary["unmatched_total"] is None


@pytest.mark.parametrize("link_amount", [None, -1.0], ids=["null-link", "negative-link"])
def test_receipt_summary_marks_pending_for_null_or_negative_link_amount(
    receipt_client: TestClient,
    link_amount: float | None,
) -> None:
    with sqlite3.connect(_db_path(receipt_client)) as db:
        db.execute(
            "INSERT INTO receipts (receipt_id, project_id, receipt_date, amount) VALUES (?, ?, ?, ?)",
            (1, "P-INVALID-LINK", "2026-07-01", 100.0),
        )
        db.execute(
            "INSERT INTO invoice_receipt_link (invoice_id, receipt_id, link_amount) VALUES (?, ?, ?)",
            (1, 1, link_amount),
        )

    response = receipt_client.get("/api/receipts", params={"project_id": "P-INVALID-LINK"})

    assert response.status_code == 200
    summary = response.json()["data"]["summary"]
    assert summary["status"] == "pending_verification"
    assert summary["receipt_total"] == 100.0
    assert summary["matched_total"] is None
    assert summary["unmatched_total"] is None


def test_receipt_summary_reraises_unrelated_operational_error_and_closes_connection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "receipts-operational-error.db"
    _create_schema(db_path)
    with sqlite3.connect(db_path) as db:
        db.execute(
            "INSERT INTO receipts (receipt_id, project_id, receipt_date, amount) VALUES (?, ?, ?, ?)",
            (1, "P-ERROR", "2026-07-01", 100.0),
        )

    class FailingConnection:
        def __init__(self) -> None:
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row
            self.closed = False

        def execute(self, sql: str, params: list[object] | None = None):
            if "invoice_receipt_link" in sql:
                raise sqlite3.OperationalError("database is locked")
            return self.connection.execute(sql, params or [])

        def close(self) -> None:
            self.closed = True
            self.connection.close()

    db = FailingConnection()
    monkeypatch.setattr(receipts_router, "get_db", lambda: db)

    with pytest.raises(sqlite3.OperationalError, match="database is locked"):
        receipts_router.get_receipts(project_id="P-ERROR")

    assert db.closed is True
