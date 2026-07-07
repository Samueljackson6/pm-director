"""Pytest fixtures for the pm-director backend test suite.

Provides an isolated FastAPI ``TestClient`` backed by a throwaway SQLite
database so that the real production database
(``database/project_management.db``) is **never** touched by the tests.

The schema created here is the *minimal* subset of tables/views that the
core read-only API endpoints query. It exists only to let the endpoints
return HTTP 200 with a sane JSON structure instead of 500 — it is NOT a
copy of (nor kept in sync with) the production schema.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.database as db_module


# ── Minimal schema for the isolated test database ────────────────
# Only the tables/columns referenced by the endpoints under test are
# declared. The view referenced by JOINs/queries is created so that the
# SQL does not fail; it returns empty/zero rows when there is no data.
_MINIMAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS contracts (
    contract_id     TEXT PRIMARY KEY,
    project_name    TEXT,
    party_a         TEXT,
    contract_amount REAL,
    sign_date       TEXT,
    project_type    TEXT,
    contract_status TEXT
);

CREATE TABLE IF NOT EXISTS projects (
    project_id            TEXT PRIMARY KEY,
    project_name          TEXT,
    customer_name         TEXT,
    project_status        TEXT,
    project_type          TEXT,
    project_manager       TEXT,
    tech_lead             TEXT,
    sales_lead            TEXT,
    total_contract_amount REAL,
    planned_start         TEXT,
    overall_progress      REAL
);

CREATE TABLE IF NOT EXISTS stages (
    project_id   TEXT,
    contract_id  TEXT,
    stage_number INTEGER,
    status       TEXT
);

CREATE TABLE IF NOT EXISTS payments (
    project_id   TEXT,
    contract_id  TEXT,
    payment_id   TEXT,
    planned_amount REAL,
    paid_amount  REAL,
    status       TEXT
);

CREATE TABLE IF NOT EXISTS deliverables (
    project_id     TEXT,
    contract_id    TEXT,
    deliverable_id TEXT,
    status         TEXT
);

CREATE TABLE IF NOT EXISTS finance_records (
    record_id          INTEGER PRIMARY KEY,
    project_id         TEXT,
    sub_invoice_total  REAL,
    sub_payment_total  REAL,
    batch_id           TEXT,
    import_time        TEXT
);

-- View consumed by /api/stats and the /api/contracts list JOIN.
-- Returns one zeroed row per project so aggregates resolve to 0
-- and LEFT JOINs never error when there is no data.
CREATE VIEW IF NOT EXISTS current_finance_view AS
SELECT
    p.project_id AS project_id,
    0            AS invoice_total,
    0            AS payment_total,
    ''           AS subcontractor
FROM projects p;
"""


def _init_isolated_db(db_path: Path) -> None:
    """Create the minimal schema inside an isolated SQLite file."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys = OFF;")
        conn.executescript(_MINIMAL_SCHEMA)
        conn.commit()
    finally:
        conn.close()


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Yield an isolated ``TestClient`` wired to a temporary SQLite DB.

    The production ``backend.database.DB_PATH`` is monkeypatched for the
    duration of the test, so every ``get_db()`` call inside the routers
    hits the throwaway database instead of the real one.
    """
    test_db = tmp_path / "test_pm.db"
    _init_isolated_db(test_db)

    # Redirect the shared DB module at the isolated database.
    monkeypatch.setattr(db_module, "DB_PATH", test_db)

    # Import the app lazily, after the DB path is patched, so any
    # module-level resolution of DB_PATH would already use the test DB.
    from backend.main import app

    with TestClient(app) as test_client:
        yield test_client
