"""Shared database module: DB_PATH + get_db() for all routers."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'database' / 'project_management.db'


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # UTF-8 解码容错：遇到非 UTF-8 字节时替换为 �，防止 GBK 等编码导致崩溃
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    return conn
