"""数据库初始化迁移脚本 - 仅用于首次部署或表结构变更时执行"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'database' / 'project_management.db'


def migrate():
    """执行数据库迁移，创建所需表结构。"""
    conn = sqlite3.connect(str(DB_PATH))
    
    # supplier_contacts 表
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
    conn.close()
    print(f"Migration completed. DB path: {DB_PATH}")


if __name__ == '__main__':
    migrate()
