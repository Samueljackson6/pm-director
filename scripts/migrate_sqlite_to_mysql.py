#!/usr/bin/env python3
"""
SQLite → MySQL 迁移脚本
生成MySQL兼容的DDL + INSERT语句，输出为 .sql 文件

用法:
  python scripts/migrate_sqlite_to_mysql.py                     # 生成迁移SQL
  python scripts/migrate_sqlite_to_mysql.py --execute           # 直接执行迁移
  python scripts/migrate_sqlite_to_mysql.py --dry-run           # 预览SQL

输出: migrations/mysql_migration_YYYYMMDD.sql
"""
import os, sys, sqlite3, textwrap
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
SRC_DB = BASE / 'database' / 'project_management.db'
OUT_DIR = BASE / 'migrations'
OUT_DIR.mkdir(exist_ok=True)

# SQLite → MySQL 类型映射
TYPE_MAP = {
    'INTEGER': 'INT',
    'INT': 'INT',
    'BIGINT': 'BIGINT',
    'TEXT': 'TEXT',
    'REAL': 'DECIMAL(15,4)',
    'FLOAT': 'DECIMAL(15,4)',
    'DOUBLE': 'DECIMAL(15,4)',
    'NUMERIC': 'DECIMAL(15,4)',
    'BOOLEAN': 'TINYINT(1)',
    'BLOB': 'LONGBLOB',
    'DATE': 'DATE',
    'TIMESTAMP': 'DATETIME',
    'DATETIME': 'DATETIME',
    'VARCHAR': 'VARCHAR(255)',
}

def sqlite_type_to_mysql(sqlite_type):
    upper = sqlite_type.upper().split('(')[0].split(' ')[0]
    if upper.startswith('VARCHAR'):
        return 'VARCHAR(255)'
    if upper.startswith('CHAR'):
        return 'VARCHAR(255)'
    if upper.startswith('DECIMAL'):
        return 'DECIMAL(15,4)'
    if 'INT' in upper:
        return 'INT'
    return TYPE_MAP.get(upper, 'TEXT')

def get_table_names(db):
    rows = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
    return [r[0] for r in rows]

def get_create_sql(db, table):
    r = db.execute(f'SELECT sql FROM sqlite_master WHERE name=? AND type="table"', (table,)).fetchone()
    return r[0] if r else ''

def convert_create_sql(sqlite_sql, table_name):
    """将SQLite CREATE TABLE转为MySQL兼容"""
    lines = sqlite_sql.split('\n')
    mysql_lines = []
    mysql_lines.append(f'DROP TABLE IF EXISTS `{table_name}`;')
    mysql_lines.append(f'CREATE TABLE `{table_name}` (')
    
    col_defs = []
    in_pk = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('CREATE') or stripped.startswith(')'):
            continue
        
        # 处理列定义
        if not stripped:
            continue
        if stripped.startswith('`') or stripped[0].isalpha():
            # Parse column name and type
            parts = stripped.split(' ')
            col_name = parts[0].strip('`')
            sqlite_type = parts[1].rstrip(',')
            mysql_type = sqlite_type_to_mysql(sqlite_type)
            
            # Handle constraints
            rest = ' '.join(parts[2:])
            not_null = 'NOT NULL' if 'NOT NULL' in rest.upper() else ''
            default = ''
            if 'DEFAULT' in rest:
                # Extract default value
                import re
                m = re.search(r"DEFAULT\s+('.*?'|\d+\.?\d*|NULL|CURRENT_TIMESTAMP)", rest, re.IGNORECASE)
                if m:
                    default = f'DEFAULT {m.group(1)}'
            
            # Handle auto increment
            ai = ''
            if 'AUTOINCREMENT' in rest.upper() or col_name.lower() == 'id':
                ai = 'AUTO_INCREMENT'
            
            col_line = f'  `{col_name}` {mysql_type} {not_null} {default} {ai}'.strip()
            col_defs.append(col_line)
        
        # Handle PRIMARY KEY
        if 'PRIMARY KEY' in stripped:
            in_pk = True
        if in_pk and stripped.endswith(','):
            col_defs.append(f'  {stripped}')
            if stripped.strip().endswith(')'):
                in_pk = False
    
    # Add default primary key if none found
    has_pk = any('PRIMARY KEY' in c.upper() for c in col_defs)
    if not has_pk:
        col_defs.append(f'  PRIMARY KEY (`id`)')
    
    mysql_lines.append(',\n'.join(col_defs))
    mysql_lines.append(') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;')
    
    return '\n'.join(mysql_lines)

def generate_insert_sql(db, table):
    """为指定表生成INSERT语句"""
    rows = db.execute(f'SELECT * FROM "{table}"').fetchall()
    if not rows:
        return f'-- Table `{table}` is empty\n'
    
    cols = [d[0] for d in db.execute(f'PRAGMA table_info("{table}")').fetchall()]
    col_names = ', '.join(f'`{c}`' for c in cols)
    placeholders = ', '.join(['?' for _ in cols])
    
    sql_parts = [f'-- {table}: {len(rows)} rows']
    batch = []
    batch_size = 50
    
    for row in rows:
        values = []
        for i, val in enumerate(row):
            if val is None:
                values.append('NULL')
            elif isinstance(val, (int, float)):
                values.append(str(val))
            else:
                # Escape single quotes
                s = str(val).replace("'", "''")
                values.append(f"'{s}'")
        
        batch.append(f'({", ".join(values)})')
        if len(batch) >= batch_size:
            sql_parts.append(f'INSERT INTO `{table}` ({col_names}) VALUES\n' + ',\n'.join(batch) + ';')
            batch = []
    
    if batch:
        sql_parts.append(f'INSERT INTO `{table}` ({col_names}) VALUES\n' + ',\n'.join(batch) + ';')
    
    return '\n'.join(sql_parts)

def migrate(dry_run=False):
    db = sqlite3.connect(str(SRC_DB))
    db.row_factory = sqlite3.Row
    tables = get_table_names(db)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_file = OUT_DIR / f'mysql_migration_{timestamp}.sql'
    
    output_lines = [
        f'-- MySQL Migration from SQLite',
        f'-- Source: {SRC_DB.name}',
        f'-- Generated: {datetime.now().isoformat()}',
        f'-- Total tables: {len(tables)}',
        f'',
        f'SET NAMES utf8mb4;',
        f'SET FOREIGN_KEY_CHECKS = 0;',
        f'',
    ]
    
    for t in tables:
        row_count = db.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        output_lines.append(f'-- ===== {t} ({row_count} rows) =====')
        
        # DDL
        sql = get_create_sql(db, t)
        mysql_sql = convert_create_sql(sql, t)
        output_lines.append(mysql_sql)
        output_lines.append('')
        
        # DML
        insert_sql = generate_insert_sql(db, t)
        output_lines.append(insert_sql)
        output_lines.append('')
    
    output_lines.append('SET FOREIGN_KEY_CHECKS = 1;')
    output_lines.append('-- Migration complete')
    
    content = '\n'.join(output_lines)
    
    if dry_run:
        print(f'Preview: {len(tables)} tables -> {out_file.name}')
        # Show first 30 lines
        lines = content.split('\n')
        for l in lines[:30]:
            print(l)
        print(f'... ({len(lines)} lines total)')
    else:
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Migration SQL written to: {out_file}')
        print(f'Tables: {len(tables)}')
        print(f'Size: {os.path.getsize(out_file)} bytes')
    
    db.close()

if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    migrate(dry_run=dry)
