from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers import suppliers as suppliers_router


def _create_supplier_detail_schema(db_path: Path) -> None:
    schema = (
        "CREATE TABLE suppliers (supplier_id TEXT PRIMARY KEY, supplier_name TEXT, credit_code TEXT);"
        "CREATE TABLE contracts (contract_id TEXT PRIMARY KEY, project_name TEXT);"
        "CREATE TABLE supplier_contracts (supplier_id TEXT, project_id TEXT);"
        "CREATE TABLE invoices (invoice_id TEXT PRIMARY KEY, project_id TEXT, invoice_type TEXT,"
        " direction TEXT, amount REAL, invoice_date TEXT);"
        "CREATE TABLE supplier_payments (payment_id INTEGER PRIMARY KEY, supplier_id TEXT,"
        " project_id TEXT, payment_date TEXT, amount REAL);"
        "CREATE TABLE supplier_contacts (id INTEGER PRIMARY KEY, supplier_id TEXT, name TEXT,"
        " position TEXT, phone TEXT, email TEXT, is_primary INTEGER, notes TEXT);"
    )
    with sqlite3.connect(db_path) as db:
        db.executescript(schema)


@pytest.fixture
def supplier_detail_client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    db_path = tmp_path / "supplier-detail.db"
    _create_supplier_detail_schema(db_path)

    def get_test_db() -> sqlite3.Connection:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        return db

    app = FastAPI()
    app.state.supplier_detail_db_path = str(db_path)
    app.include_router(suppliers_router.router)
    monkeypatch.setattr(suppliers_router, "get_db", get_test_db)
    monkeypatch.setattr(suppliers_router, "get_readonly_db", get_test_db)

    with TestClient(app) as client:
        yield client


def _seed_supplier_detail(db_path: Path, *, include_supplier_invoice: bool) -> None:
    with sqlite3.connect(db_path) as db:
        db.execute(
            "INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)",
            ("SUP-TRUTH", "Truth Supplier"),
        )
        db.execute(
            "INSERT INTO contracts (contract_id, project_name) VALUES (?, ?)",
            ("PROJECT-TRUTH", "Truth Project"),
        )
        db.execute(
            "INSERT INTO supplier_contracts (supplier_id, project_id) VALUES (?, ?)",
            ("SUP-TRUTH", "PROJECT-TRUTH"),
        )
        invoice_sql = (
            "INSERT INTO invoices "
            "(invoice_id, project_id, invoice_type, direction, amount, invoice_date) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        db.execute(
            invoice_sql,
            ("CUSTOMER-RECEIPT", "PROJECT-TRUTH", "客户回款", "inbound", 300.0, "2026-07-01"),
        )
        if include_supplier_invoice:
            db.execute(
                invoice_sql,
                ("SUPPLIER-INVOICE", "PROJECT-TRUTH", "供应商开票", "inbound", 500.0, "2026-07-02"),
            )


def _test_db_path(client: TestClient) -> Path:
    return Path(client.app.state.supplier_detail_db_path)


def test_supplier_detail_aggregates_by_supplier_id_and_declares_empty_data_truth(
    supplier_detail_client: TestClient,
) -> None:
    db_path = _test_db_path(supplier_detail_client)
    _seed_supplier_detail(db_path, include_supplier_invoice=False)

    response = supplier_detail_client.get("/api/suppliers/SUP-TRUTH")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["supplier"]["supplier_id"] == "SUP-TRUTH"
    assert data["contracts"] == [
        {
            "supplier_id": "SUP-TRUTH",
            "project_id": "PROJECT-TRUTH",
            "project_name": "Truth Project",
        }
    ]
    assert data["data_states"]["supplier_invoices"] == "source_not_established"
    assert data["data_states"]["supplier_payments"] == "known_zero"


def test_supplier_detail_excludes_customer_receipt_from_supplier_invoices(
    supplier_detail_client: TestClient,
) -> None:
    db_path = _test_db_path(supplier_detail_client)
    _seed_supplier_detail(db_path, include_supplier_invoice=True)

    response = supplier_detail_client.get("/api/suppliers/SUP-TRUTH")

    assert response.status_code == 200
    invoices = response.json()["data"]["supplier_invoices"]
    assert [invoice["invoice_id"] for invoice in invoices] == ["SUPPLIER-INVOICE"]
