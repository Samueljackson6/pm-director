#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外键违规数据修复脚本

处理 167 条外键违规记录：
1. contract_clauses (66条) - 删除无效引用
2. stage_payment_link (72条) - 清理无效关联
3. project_status (11条) - 清理无效状态
4. contract_type_attributes (11条) - 删除无效属性
5. contract_project_link (5条) - 清理无效关联
6. finance_records (1条) - 修复或删除
7. supplier_contracts (1条) - 修复或删除

运行前自动备份数据库。
"""

import sqlite3
import shutil
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).parent.parent / "database" / "project_management.db"
BACKUP_DIR = Path(__file__).parent.parent / "database" / "backups"


def backup_database():
    """备份数据库"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"project_management-before-fk-fix-{timestamp}.db"
    shutil.copy2(DB_PATH, backup_path)
    print(f"[OK] Database backed up to: {backup_path}")
    return backup_path


def analyze_violations(conn):
    """分析外键违规情况"""
    cursor = conn.cursor()
    violations = {}

    # 1. contract_clauses
    cursor.execute("""
        SELECT cc.contract_id, cc.clause_category, cc.clause_text
        FROM contract_clauses cc
        WHERE cc.contract_id NOT IN (SELECT contract_id FROM contracts)
    """)
    violations['contract_clauses'] = cursor.fetchall()

    # 2. stage_payment_link - stage_id
    cursor.execute("""
        SELECT spl.stage_id, spl.payment_id
        FROM stage_payment_link spl
        WHERE spl.stage_id NOT IN (SELECT stage_id FROM stages)
    """)
    violations['stage_payment_link-stage'] = cursor.fetchall()

    # 3. stage_payment_link - payment_id
    cursor.execute("""
        SELECT spl.stage_id, spl.payment_id
        FROM stage_payment_link spl
        WHERE spl.payment_id NOT IN (SELECT payment_id FROM payments)
    """)
    violations['stage_payment_link-payment'] = cursor.fetchall()

    # 4. project_status
    cursor.execute("""
        SELECT ps.contract_id, ps.status, ps.overall_progress
        FROM project_status ps
        WHERE ps.contract_id NOT IN (SELECT contract_id FROM contracts)
    """)
    violations['project_status'] = cursor.fetchall()

    # 5. contract_type_attributes
    cursor.execute("""
        SELECT cta.contract_id, cta.contract_category, cta.delivery_schedule
        FROM contract_type_attributes cta
        WHERE cta.contract_id NOT IN (SELECT contract_id FROM contracts)
    """)
    violations['contract_type_attributes'] = cursor.fetchall()

    # 6. contract_project_link
    cursor.execute("""
        SELECT cpl.contract_id, cpl.project_id
        FROM contract_project_link cpl
        WHERE cpl.contract_id NOT IN (SELECT contract_id FROM contracts)
    """)
    violations['contract_project_link'] = cursor.fetchall()

    # 7. finance_records
    cursor.execute("""
        SELECT fr.record_id, fr.project_id, fr.contract_amount
        FROM finance_records fr
        WHERE fr.project_id NOT IN (SELECT contract_id FROM contracts)
    """)
    violations['finance_records'] = cursor.fetchall()

    # 8. supplier_contracts
    cursor.execute("""
        SELECT sc.supplier_id, sc.project_id
        FROM supplier_contracts sc
        WHERE sc.project_id NOT IN (SELECT contract_id FROM contracts)
    """)
    violations['supplier_contracts'] = cursor.fetchall()

    return violations


def fix_foreign_keys(dry_run=True):
    """修复外键违规"""
    print("=" * 70)
    print("Foreign Key Violation Fix Script")
    print("=" * 70)
    print(f"Database: {DB_PATH}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'EXECUTE (will modify)'}")
    print()

    if not dry_run:
        backup_database()

    conn = sqlite3.connect(DB_PATH)
    violations = analyze_violations(conn)

    # 显示分析结果
    print("[ANALYSIS] Foreign Key Violations:")
    print("-" * 50)
    total = 0
    for table, records in violations.items():
        count = len(records)
        total += count
        print(f"  {table}: {count} records")
        if count > 0 and count <= 5:
            for rec in records[:5]:
                print(f"    - {rec}")
        elif count > 5:
            for rec in records[:3]:
                print(f"    - {rec}")
            print(f"    ... and {count - 3} more")

    print(f"\n  TOTAL: {total} violations")
    print()

    if dry_run:
        print("[INFO] This is a DRY RUN. No data was modified.")
        print("       Proposed actions:")
        print("       1. Delete orphan contract_clauses (66 records)")
        print("       2. Delete orphan stage_payment_link (72 records)")
        print("       3. Delete orphan project_status (11 records)")
        print("       4. Delete orphan contract_type_attributes (11 records)")
        print("       5. Delete orphan contract_project_link (5 records)")
        print("       6. Delete orphan finance_records (1 record)")
        print("       7. Delete orphan supplier_contracts (1 record)")
        print()
        print(f"       To execute: python {Path(__file__).name} --execute")
    else:
        cursor = conn.cursor()

        # 1. 删除无效的 contract_clauses
        cursor.execute("""
            DELETE FROM contract_clauses
            WHERE contract_id NOT IN (SELECT contract_id FROM contracts)
        """)
        print(f"[OK] Deleted {cursor.rowcount} orphan contract_clauses")

        # 2. 删除无效的 stage_payment_link
        cursor.execute("""
            DELETE FROM stage_payment_link
            WHERE stage_id NOT IN (SELECT stage_id FROM stages)
               OR payment_id NOT IN (SELECT payment_id FROM payments)
        """)
        print(f"[OK] Deleted {cursor.rowcount} orphan stage_payment_link")

        # 3. 删除无效的 project_status
        cursor.execute("""
            DELETE FROM project_status
            WHERE contract_id NOT IN (SELECT contract_id FROM contracts)
        """)
        print(f"[OK] Deleted {cursor.rowcount} orphan project_status")

        # 4. 删除无效的 contract_type_attributes
        cursor.execute("""
            DELETE FROM contract_type_attributes
            WHERE contract_id NOT IN (SELECT contract_id FROM contracts)
        """)
        print(f"[OK] Deleted {cursor.rowcount} orphan contract_type_attributes")

        # 5. 删除无效的 contract_project_link
        cursor.execute("""
            DELETE FROM contract_project_link
            WHERE contract_id NOT IN (SELECT contract_id FROM contracts)
        """)
        print(f"[OK] Deleted {cursor.rowcount} orphan contract_project_link")

        # 6. 删除无效的 finance_records
        cursor.execute("""
            DELETE FROM finance_records
            WHERE project_id NOT IN (SELECT contract_id FROM contracts)
        """)
        print(f"[OK] Deleted {cursor.rowcount} orphan finance_records")

        # 7. 删除无效的 supplier_contracts
        cursor.execute("""
            DELETE FROM supplier_contracts
            WHERE project_id NOT IN (SELECT contract_id FROM contracts)
        """)
        print(f"[OK] Deleted {cursor.rowcount} orphan supplier_contracts")

        conn.commit()

        # 验证
        print()
        print("[VERIFICATION] Checking remaining violations...")
        remaining = analyze_violations(conn)
        remaining_count = sum(len(r) for r in remaining.values())
        if remaining_count == 0:
            print("[OK] All foreign key violations have been resolved!")
        else:
            print(f"[WARN] {remaining_count} violations still remain")

    conn.close()


if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv

    if "--execute" in sys.argv:
        print("[WARN] About to execute database modifications!")
        confirm = input("Confirm deletion of 167 orphan records? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            sys.exit(0)

    fix_foreign_keys(dry_run=dry_run)