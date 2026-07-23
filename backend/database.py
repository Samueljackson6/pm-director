"""共享数据库连接：写入连接与严格只读连接。"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'database' / 'project_management.db'


def get_db():
    """返回可写 SQLite 连接。不自动建表，建表由迁移脚本显式执行。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # UTF-8 解码容错：遇到非 UTF-8 字节时替换为 �，防止 GBK 等编码导致崩溃
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    return conn


def get_readonly_db():
    """返回严格只读的 SQLite 连接，不执行建表、写入或提交。"""
    conn = sqlite3.connect(f'{DB_PATH.resolve().as_uri()}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    # UTF-8 解码容错：保持普通连接与只读连接的读取行为一致
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    return conn
