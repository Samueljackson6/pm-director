#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据整体验证脚本

验证内容：
1. 外键完整性
2. 数据格式一致性
3. 编码正确性
4. 业务逻辑约束
"""

import sqlite3
import sys
import re
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).parent.parent / "database" / "project_management.db"


def validate_database():
    """执行数据库验证"""
    print("=" * 70)
    print("DATABASE VALIDATION REPORT")
    print("=" * 70)
    print(f"Database: {DB_PATH}")
    print()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    issues = []
    warnings = []

    # ================== 1. 外键完整性检查 ==================
    print("[1] FOREIGN KEY INTEGRITY")
    print("-" * 50)

    # 1.1 付款记录 -> 合同
    cursor.execute("""
        SELECT p.payment_id, p.contract_id
        FROM payments p
        LEFT JOIN contracts c ON p.contract_id = c.contract_id
        WHERE p.contract_id IS NOT NULL AND p.contract_id != '' AND c.contract_id IS NULL
    """)
    orphan_payments = cursor.fetchall()
    if orphan_payments:
        issues.append(f"Payments with invalid contract_id: {len(orphan_payments)}")
        for pid, cid in orphan_payments[:5]:
            print(f"  [ERROR] Payment {pid} references non-existent contract {cid}")
    else:
        print("  [OK] All payment contract_id references are valid")

    # 1.2 交付物 -> 合同
    cursor.execute("""
        SELECT d.deliverable_id, d.contract_id
        FROM deliverables d
        LEFT JOIN contracts c ON d.contract_id = c.contract_id
        WHERE d.contract_id IS NOT NULL AND d.contract_id != '' AND c.contract_id IS NULL
    """)
    orphan_deliverables = cursor.fetchall()
    if orphan_deliverables:
        issues.append(f"Deliverables with invalid contract_id: {len(orphan_deliverables)}")
        for did, cid in orphan_deliverables[:5]:
            print(f"  [ERROR] Deliverable {did} references non-existent contract {cid}")
    else:
        print("  [OK] All deliverable contract_id references are valid")

    # 1.3 发票 -> 合同/项目
    cursor.execute("""
        SELECT i.invoice_id, i.project_id
        FROM invoices i
        LEFT JOIN contracts c ON i.project_id = c.contract_id
        WHERE i.project_id IS NOT NULL AND i.project_id != '' AND c.contract_id IS NULL
        LIMIT 10
    """)
    orphan_invoices = cursor.fetchall()
    if orphan_invoices:
        warnings.append(f"Invoices with non-matching project_id: {len(orphan_invoices)} (may be OK - different ID system)")
    else:
        print("  [OK] Invoice project_id references checked")

    print()

    # ================== 2. 数据格式一致性检查 ==================
    print("[2] DATA FORMAT CONSISTENCY")
    print("-" * 50)

    # 2.1 payment_id 格式
    cursor.execute("SELECT payment_id FROM payments")
    payment_ids = [row[0] for row in cursor.fetchall()]

    standard_pattern = re.compile(r'^PAY-.+-\d+$')
    non_standard = [pid for pid in payment_ids if not standard_pattern.match(pid)]

    if non_standard:
        issues.append(f"Non-standard payment_id format: {len(non_standard)}")
        for pid in non_standard[:5]:
            print(f"  [ERROR] Non-standard payment_id: {pid}")
    else:
        print(f"  [OK] All {len(payment_ids)} payment_id follow standard format (PAY-xxx-N)")

    # 2.2 deliverable_id 格式
    cursor.execute("SELECT deliverable_id FROM deliverables")
    deliverable_ids = [row[0] for row in cursor.fetchall()]

    deliverable_pattern = re.compile(r'^.+-D\d+$|^.+-交付物\d+$|^待补充-D\d+$')
    non_standard_del = [did for did in deliverable_ids if not deliverable_pattern.match(did)]

    if non_standard_del:
        warnings.append(f"Non-standard deliverable_id format: {len(non_standard_del)}")
        print(f"  [WARN] {len(non_standard_del)} non-standard deliverable_id (may be OK)")
    else:
        print(f"  [OK] All {len(deliverable_ids)} deliverable_id follow standard format")

    print()

    # ================== 3. 编码正确性检查 ==================
    print("[3] ENCODING VALIDATION")
    print("-" * 50)

    # 检查乱码字符
    garbled_chars = ['楠', '敹', '鍚', '敮', '屾', '敮']
    cursor.execute("SELECT payment_id, payment_stage FROM payments")
    for pid, stage in cursor.fetchall():
        if stage and any(c in stage for c in garbled_chars):
            issues.append(f"Garbled text in payment_stage: {pid}")
            print(f"  [ERROR] Garbled text in {pid}: {stage[:30]}...")

    cursor.execute("SELECT deliverable_id, deliverable_name FROM deliverables")
    for did, name in cursor.fetchall():
        if name and any(c in name for c in garbled_chars):
            issues.append(f"Garbled text in deliverable_name: {did}")
            print(f"  [ERROR] Garbled text in {did}: {name[:30]}...")

    if not any('Garbled' in i for i in issues):
        print("  [OK] No garbled text found")

    print()

    # ================== 4. 业务逻辑约束检查 ==================
    print("[4] BUSINESS LOGIC CONSTRAINTS")
    print("-" * 50)

    # 4.1 付款金额合理性
    cursor.execute("""
        SELECT payment_id, planned_amount, actual_amount
        FROM payments
        WHERE planned_amount < 0 OR actual_amount < 0
    """)
    negative_amounts = cursor.fetchall()
    if negative_amounts:
        issues.append(f"Negative payment amounts: {len(negative_amounts)}")
        for pid, planned, actual in negative_amounts[:5]:
            print(f"  [ERROR] {pid}: planned={planned}, actual={actual}")
    else:
        print("  [OK] No negative payment amounts")

    # 4.2 重复交付物检查
    cursor.execute("""
        SELECT contract_id, deliverable_name, COUNT(*) as cnt
        FROM deliverables
        GROUP BY contract_id, deliverable_name
        HAVING COUNT(*) > 1
    """)
    dup_deliverables = cursor.fetchall()
    if dup_deliverables:
        issues.append(f"Duplicate deliverables: {len(dup_deliverables)}")
        for cid, name, cnt in dup_deliverables:
            print(f"  [ERROR] Contract {cid}: '{name[:30]}...' duplicated {cnt} times")
    else:
        print("  [OK] No duplicate deliverables")

    # 4.3 空合同编号检查
    cursor.execute("""
        SELECT COUNT(*) FROM contracts WHERE contract_id IS NULL OR contract_id = ''
    """)
    empty_contracts = cursor.fetchone()[0]
    if empty_contracts > 0:
        issues.append(f"Contracts with empty ID: {empty_contracts}")
    else:
        print("  [OK] All contracts have valid IDs")

    print()

    # ================== 5. 统计摘要 ==================
    print("[5] STATISTICS SUMMARY")
    print("-" * 50)

    tables = [
        ('contracts', '合同'),
        ('payments', '付款记录'),
        ('deliverables', '交付物'),
        ('invoices', '发票'),
        ('receipts', '回款'),
        ('suppliers', '供应商'),
        ('supplier_payments', '供应商付款'),
    ]

    for table, name in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {name}: {count:,} 条")

    print()

    # ================== 最终结果 ==================
    print("=" * 70)
    print("VALIDATION RESULT")
    print("=" * 70)

    if issues:
        print(f"[FAIL] Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("[PASS] All validations passed!")

    if warnings:
        print(f"\n[WARN] {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"  - {warning}")

    conn.close()
    return True


if __name__ == "__main__":
    success = validate_database()
    sys.exit(0 if success else 1)
