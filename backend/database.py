"""Shared database module: DB_PATH + get_db() for all routers."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'database' / 'project_management.db'


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn
