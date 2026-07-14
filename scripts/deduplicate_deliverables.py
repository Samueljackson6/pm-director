#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交付物去重脚本

清理 deliverables 表中同一合同下同名交付物的重复记录。
保留最早创建的记录，删除后续重复记录。

运行前会自动备份数据库。
"""

import sqlite3
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).parent.parent / "database" / "project_management.db"
BACKUP_DIR = Path(__file__).parent.parent / "database" / "backups"


def backup_database():
    """备份数据库"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"project_management-before-dedup-{timestamp}.db"
    shutil.copy2(DB_PATH, backup_path)
    print(f"[OK] Database backed up to: {backup_path}")
    return backup_path


def find_duplicates(conn):
    """查找重复的交付物"""
    cursor = conn.cursor()

    # 查找同一合同下同名的重复交付物
    cursor.execute("""
        SELECT contract_id, deliverable_name, COUNT(*) as cnt
        FROM deliverables
        GROUP BY contract_id, deliverable_name
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
    """)

    duplicate_groups = cursor.fetchall()
    return duplicate_groups


def get_duplicate_records(conn, contract_id, deliverable_name):
    """获取重复记录的详细信息，按创建时间排序"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT deliverable_id, contract_id, deliverable_name, created_at
        FROM deliverables
        WHERE contract_id = ? AND deliverable_name = ?
        ORDER BY created_at ASC
    """, (contract_id, deliverable_name))

    return cursor.fetchall()


def deduplicate_deliverables(dry_run=True):
    """执行去重操作"""
    print("=" * 60)
    print("Deliverables Deduplication Script")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'EXECUTE (will modify)'}")
    print()

    # 备份数据库
    if not dry_run:
        backup_path = backup_database()

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)

    # 查找重复组
    duplicate_groups = find_duplicates(conn)

    if not duplicate_groups:
        print("[OK] No duplicate deliverables found. Data is clean.")
        conn.close()
        return

    print(f"Found {len(duplicate_groups)} duplicate groups:\n")

    total_duplicates = 0
    records_to_delete = []

    for contract_id, deliverable_name, count in duplicate_groups:
        name_preview = deliverable_name[:50] + "..." if len(deliverable_name) > 50 else deliverable_name
        print(f"Contract {contract_id}: '{name_preview}' (duplicated {count} times)")

        # 获取该组的所有记录
        records = get_duplicate_records(conn, contract_id, deliverable_name)

        # 保留第一条（最早创建），删除其余的
        keep = records[0]
        to_delete = records[1:]

        print(f"  [KEEP]   {keep[0]} (created: {keep[3]})")
        for rec in to_delete:
            print(f"  [DELETE] {rec[0]} (created: {rec[3]})")
            records_to_delete.append(rec[0])

        total_duplicates += len(to_delete)
        print()

    print("-" * 60)
    print(f"Total records to delete: {total_duplicates}")
    print("-" * 60)

    if dry_run:
        print("\n[INFO] This is a DRY RUN. No data was modified.")
        print("       To execute actual deletion, run:")
        print(f"       python {Path(__file__).name} --execute")
    else:
        # 执行删除
        cursor = conn.cursor()
        placeholders = ",".join("?" * len(records_to_delete))
        cursor.execute(f"""
            DELETE FROM deliverables
            WHERE deliverable_id IN ({placeholders})
        """, records_to_delete)

        deleted_count = cursor.rowcount
        conn.commit()

        print(f"\n[OK] Successfully deleted {deleted_count} duplicate records")

        # 验证结果
        remaining_duplicates = find_duplicates(conn)
        if remaining_duplicates:
            print(f"\n[WARN] {len(remaining_duplicates)} duplicate groups still remain")
        else:
            print("\n[OK] Verification passed: No more duplicates in database")

    conn.close()


if __name__ == "__main__":
    # 检查命令行参数
    dry_run = "--execute" not in sys.argv

    if "--execute" in sys.argv:
        print("[WARN] About to execute deletion!")
        confirm = input("Confirm? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            sys.exit(0)

    deduplicate_deliverables(dry_run=dry_run)
