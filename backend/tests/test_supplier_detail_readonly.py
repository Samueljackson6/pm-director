from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend import qcc_sync
from backend.routers import suppliers as suppliers_router


def _create_schema(db_path: Path) -> None:
    with sqlite3.connect(db_path) as db:
        db.executescript(
            "CREATE TABLE suppliers (supplier_id TEXT PRIMARY KEY, supplier_name TEXT, credit_code TEXT);"
            "CREATE TABLE contracts (contract_id TEXT PRIMARY KEY, project_name TEXT);"
            "CREATE TABLE supplier_contracts (supplier_id TEXT, project_id TEXT);"
            "CREATE TABLE invoices (invoice_id TEXT PRIMARY KEY, project_id TEXT, invoice_type TEXT, direction TEXT, amount REAL, invoice_date TEXT);"
            "CREATE TABLE supplier_payments (payment_id INTEGER PRIMARY KEY, supplier_id TEXT, project_id TEXT, payment_date TEXT, amount REAL);"
            "CREATE TABLE supplier_contacts (id INTEGER PRIMARY KEY, supplier_id TEXT, name TEXT, position TEXT, phone TEXT, email TEXT, is_primary INTEGER, notes TEXT);"
            "INSERT INTO suppliers (supplier_id, supplier_name, credit_code) VALUES ('SUP-READONLY', '只读供应商', '91330000TEST000001');"
        )


def _readonly_connection(db_path: Path, statements: list[str]) -> sqlite3.Connection:
    db = sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    db.set_trace_callback(statements.append)
    return db


def test_supplier_detail_is_strictly_readonly_when_qcc_tables_are_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """详情读取不得初始化 QCC 表，也不得执行任何写入或提交。"""
    db_path = tmp_path / "supplier-readonly.db"
    _create_schema(db_path)
    statements: list[str] = []

    def get_test_readonly_db() -> sqlite3.Connection:
        return _readonly_connection(db_path, statements)

    app = FastAPI()
    app.include_router(suppliers_router.router)
    monkeypatch.setattr(suppliers_router, "get_readonly_db", get_test_readonly_db)
    monkeypatch.setattr(qcc_sync, "get_readonly_db", get_test_readonly_db)

    with TestClient(app) as client:
        response = client.get("/api/suppliers/SUP-READONLY")

    assert response.status_code == 200
    assert response.json()["data"]["qcc_data"] is None

    with sqlite3.connect(db_path) as db:
        qcc_tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE 'qcc_%'"
        ).fetchall()

    assert qcc_tables == []
    write_prefixes = (
        "BEGIN",
        "COMMIT",
        "CREATE",
        "DELETE",
        "DROP",
        "INSERT",
        "ALTER",
        "REPLACE",
        "ROLLBACK",
        "UPDATE",
    )
    assert not any(statement.lstrip().upper().startswith(write_prefixes) for statement in statements)
