from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers import invoices as invoices_router
from backend.routers import suppliers as suppliers_router


def _create_schema(db_path: Path) -> None:
    with sqlite3.connect(db_path) as db:
        db.executescript(
            "CREATE TABLE suppliers (supplier_id TEXT PRIMARY KEY, supplier_name TEXT, short_name TEXT);"
            "CREATE TABLE invoices (invoice_id INTEGER PRIMARY KEY, project_id TEXT, invoice_type TEXT, direction TEXT, amount REAL, invoice_date TEXT);"
            "CREATE TABLE supplier_payments (payment_id INTEGER PRIMARY KEY, supplier_id TEXT, project_id TEXT, payment_date TEXT, amount REAL);"
        )


@pytest.fixture
def supplier_finance_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "supplier-finance.db"
    _create_schema(db_path)

    def get_test_readonly_db() -> sqlite3.Connection:
        db = sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        return db

    app = FastAPI()
    app.state.supplier_finance_db_path = str(db_path)
    app.include_router(invoices_router.router)
    app.include_router(suppliers_router.router)
    monkeypatch.setattr(invoices_router, "get_readonly_db", get_test_readonly_db)
    monkeypatch.setattr(suppliers_router, "get_readonly_db", get_test_readonly_db)

    with TestClient(app) as client:
        yield client


def _db_path(client: TestClient) -> Path:
    return Path(client.app.state.supplier_finance_db_path)


def test_supplier_invoice_list_excludes_customer_receipts_and_returns_available_state(
    supplier_finance_client: TestClient,
) -> None:
    with sqlite3.connect(_db_path(supplier_finance_client)) as db:
        db.executemany(
            "INSERT INTO invoices (invoice_id, project_id, invoice_type, direction, amount, invoice_date) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (1, "PROJECT-1", '客户回款', "inbound", 300.0, "2026-07-01"),
                (2, "PROJECT-1", '供应商开票', "inbound", 500.0, "2026-07-02"),
                (3, "PROJECT-1", '供应商开票', "outbound", 700.0, "2026-07-03"),
            ],
        )

    response = supplier_finance_client.get(
        "/api/invoices",
        params={"direction": "inbound", "invoice_type": '供应商开票'},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["data_state"] == "available"
    assert [item["invoice_id"] for item in data["items"]] == [2]


def test_supplier_invoice_list_marks_known_zero_and_pending_verification(
    supplier_finance_client: TestClient,
) -> None:
    empty_response = supplier_finance_client.get(
        "/api/invoices",
        params={"direction": "inbound", "invoice_type": '供应商开票'},
    )
    assert empty_response.json()["data"]["data_state"] == "known_zero"

    with sqlite3.connect(_db_path(supplier_finance_client)) as db:
        db.execute(
            "INSERT INTO invoices (invoice_id, project_id, invoice_type, direction, amount, invoice_date) VALUES (?, ?, ?, ?, ?, ?)",
            (1, "PROJECT-1", '供应商开票', "inbound", None, "2026-07-02"),
        )

    pending_response = supplier_finance_client.get(
        "/api/invoices",
        params={"direction": "inbound", "invoice_type": '供应商开票'},
    )
    assert pending_response.json()["data"]["data_state"] == "pending_verification"


def test_supplier_payment_list_states_and_detail_excludes_customer_receipts(
    supplier_finance_client: TestClient,
) -> None:
    empty_response = supplier_finance_client.get("/api/suppliers/payments")
    assert empty_response.status_code == 200
    assert empty_response.json()["data"]["data_state"] == "known_zero"

    with sqlite3.connect(_db_path(supplier_finance_client)) as db:
        db.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", ("SUP-1", '供应商开票'))
        db.execute(
            "INSERT INTO supplier_payments (payment_id, supplier_id, project_id, payment_date, amount) VALUES (?, ?, ?, ?, ?)",
            (1, "SUP-1", "PROJECT-1", "2026-07-03", None),
        )
        db.executemany(
            "INSERT INTO invoices (invoice_id, project_id, invoice_type, direction, amount, invoice_date) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (1, "PROJECT-1", '客户回款', "inbound", 300.0, "2026-07-01"),
                (2, "PROJECT-1", '供应商开票', "inbound", 500.0, "2026-07-02"),
            ],
        )

    pending_response = supplier_finance_client.get("/api/suppliers/payments")
    assert pending_response.json()["data"]["data_state"] == "pending_verification"

    detail_response = supplier_finance_client.get("/api/suppliers/payments/1")
    assert detail_response.status_code == 200
    detail = detail_response.json()["data"]
    assert detail["linked_invoices_data_state"] == "available"
    assert [item["invoice_id"] for item in detail["linked_invoices"]] == [2]


def test_supplier_finance_lists_declare_source_not_established_when_table_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """?????????????????? GET ???????????"""
    db_path = tmp_path / "supplier-finance-missing-source.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE suppliers (supplier_id TEXT PRIMARY KEY, supplier_name TEXT, short_name TEXT)")

    def get_test_readonly_db() -> sqlite3.Connection:
        db = sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        return db

    app = FastAPI()
    app.include_router(invoices_router.router)
    app.include_router(suppliers_router.router)
    monkeypatch.setattr(invoices_router, "get_readonly_db", get_test_readonly_db)
    monkeypatch.setattr(suppliers_router, "get_readonly_db", get_test_readonly_db)

    with TestClient(app) as client:
        invoice_response = client.get("/api/invoices", params={"direction": "inbound", "invoice_type": "?????"})
        payment_response = client.get("/api/suppliers/payments")

    assert invoice_response.status_code == 200
    assert invoice_response.json()["data"] == {
        "total": 0, "page": 1, "size": 50, "items": [], "data_state": "source_not_established"
    }
    assert payment_response.status_code == 200
    assert payment_response.json()["data"] == {
        "total": 0, "page": 1, "size": 50, "items": [], "data_state": "source_not_established"
    }
