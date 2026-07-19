"""共享数据库连接：写入连接与严格只读连接。"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'database' / 'project_management.db'


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # UTF-8 解码容错：遇到非 UTF-8 字节时替换为 �，防止 GBK 等编码导致崩溃
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    _init_tables(conn)
    return conn


def get_readonly_db():
    """返回严格只读的 SQLite 连接，不执行建表、写入或提交。"""
    conn = sqlite3.connect(f'{DB_PATH.resolve().as_uri()}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    # UTF-8 解码容错：保持普通连接与只读连接的读取行为一致
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    return conn


def _init_tables(conn):
    """Ensure required tables exist."""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS supplier_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id TEXT NOT NULL,
            name TEXT NOT NULL,
            position TEXT,
            phone TEXT,
            email TEXT,
            is_primary INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        )
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_supplier_contacts_supplier
        ON supplier_contacts(supplier_id)
    ''')
    conn.commit()
