#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
付款金额单位统一修复脚本

问题：
- 部分付款记录金额单位是元
- 部分付款记录金额单位是万元
- 导致付款总额与合同金额比例异常

修复策略：
1. 分析每条付款记录与合同金额的比例
2. 如果比例 > 5，认为是元单位，需除以 10000 转换为万元
3. 生成修复报告并执行修正

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

# 比例阈值：超过此值认为是元单位
RATIO_THRESHOLD = 5.0


def backup_database():
    """备份数据库"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"project_management-before-amount-fix-{timestamp}.db"
    shutil.copy2(DB_PATH, backup_path)
    print(f"[OK] Database backed up to: {backup_path}")
    return backup_path


def analyze_amount_units(conn):
    """分析付款金额单位问题"""
    cursor = conn.cursor()

    # 获取每个合同的付款总额与合同金额对比
    cursor.execute("""
        SELECT c.contract_id, c.contract_amount,
               SUM(p.planned_amount) as total_payment,
               COUNT(p.payment_id) as payment_count
        FROM contracts c
        JOIN payments p ON c.contract_id = p.contract_id
        GROUP BY c.contract_id
        HAVING c.contract_amount > 0
    """)

    results = cursor.fetchall()

    # 分类：正常、元单位（需转换）、异常
    normal = []
    needs_conversion = []
    anomalies = []

    for row in results:
        contract_id, contract_amount, total_payment, payment_count = row
        if contract_amount > 0:
            ratio = total_payment / contract_amount

            if ratio < RATIO_THRESHOLD:
                # 正常（万元单位）
                normal.append((contract_id, contract_amount, total_payment, ratio))
            elif ratio > 100 and ratio < 2000:
                # 可能是元单位，检查转换后是否合理
                converted_ratio = total_payment / 10000 / contract_amount
                if converted_ratio < RATIO_THRESHOLD and converted_ratio > 0.001:
                    # 转换后比例合理（0.1% - 500%）
                    needs_conversion.append((contract_id, contract_amount, total_payment, ratio, converted_ratio))
                else:
                    # 转换后比例仍然异常
                    anomalies.append((contract_id, contract_amount, total_payment, ratio,
                                     f"转换后比例{converted_ratio:.4f}仍然异常"))
            else:
                # 其他异常情况
                anomalies.append((contract_id, contract_amount, total_payment, ratio,
                                 "付款金额与合同金额比例异常，需手动检查"))

    return normal, needs_conversion, anomalies


def get_payments_to_convert(conn, contract_ids):
    """获取需要转换的付款记录"""
    cursor = conn.cursor()
    placeholders = ",".join("?" * len(contract_ids))
    cursor.execute(f"""
        SELECT payment_id, contract_id, planned_amount, actual_amount
        FROM payments
        WHERE contract_id IN ({placeholders})
    """, contract_ids)

    return cursor.fetchall()


def fix_amount_units(dry_run=True):
    """修复付款金额单位"""
    print("=" * 70)
    print("Payment Amount Unit Fix Script")
    print("=" * 70)
    print(f"Database: {DB_PATH}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'EXECUTE (will modify)'}")
    print()

    conn = sqlite3.connect(DB_PATH)

    # 分析
    print("[ANALYSIS] Analyzing payment amount units...")
    print("-" * 50)
    normal, needs_conversion, anomalies = analyze_amount_units(conn)

    print(f"Normal contracts (ratio < {RATIO_THRESHOLD}): {len(normal)}")
    print(f"Needs conversion (元 -> 万元): {len(needs_conversion)}")
    print(f"Anomalies (check manually): {len(anomalies)}")
    print()

    if normal:
        print("  Normal examples:")
        for row in normal[:5]:
            print(f"    {row[0]}: contract={row[1]:.2f}万, payment={row[2]:.2f}万, ratio={row[3]:.2f}")

    if needs_conversion:
        print("\n  Needs conversion (元 -> 万元):")
        for row in needs_conversion:
            print(f"    {row[0]}: contract={row[1]:.2f}万, payment={row[2]:.2f}元 (ratio={row[3]:.2f})")
            print(f"      -> After conversion: {row[2]/10000:.2f}万 (ratio={row[4]:.2f})")

    if anomalies:
        print("\n  Anomalies (need manual review):")
        for row in anomalies:
            if len(row) == 5:
                contract_id, contract_amount, total_payment, ratio, reason = row
                print(f"    {contract_id}: contract={contract_amount:.2f}万, payment={total_payment:.2f}, ratio={ratio:.2f}")
                print(f"      Reason: {reason}")

    print()

    if needs_conversion:
        # 获取需要转换的付款记录
        contract_ids = [row[0] for row in needs_conversion]
        payments = get_payments_to_convert(conn, contract_ids)

        print(f"[DETAILS] {len(payments)} payment records to convert:")
        print("-" * 50)
        for payment_id, contract_id, planned, actual in payments[:10]:
            print(f"  {payment_id}: {planned:.2f}元 -> {planned/10000:.4f}万元")
        if len(payments) > 10:
            print(f"  ... and {len(payments) - 10} more")
        print()

    if dry_run:
        print("[INFO] This is a DRY RUN. No data was modified.")
        print("       Proposed actions:")
        print(f"       1. Convert {len(needs_conversion) * 0 + len(payments) if needs_conversion else 0} payment records from 元 to 万元")
        print(f"       To execute: python {Path(__file__).name} --execute")
    else:
        if not needs_conversion:
            print("[OK] No conversion needed.")
        else:
            backup_database()

            cursor = conn.cursor()

            # 获取需要转换的付款记录
            contract_ids = [row[0] for row in needs_conversion]
            payments = get_payments_to_convert(conn, contract_ids)

            # 执行转换
            for payment_id, contract_id, planned, actual in payments:
                new_planned = planned / 10000
                new_actual = actual / 10000 if actual else 0

                cursor.execute("""
                    UPDATE payments
                    SET planned_amount = ?, actual_amount = ?
                    WHERE payment_id = ?
                """, (new_planned, new_actual, payment_id))

            conn.commit()
            print(f"[OK] Converted {len(payments)} payment records from 元 to 万元")

            # 验证
            print("\n[VERIFICATION] Checking results...")
            normal_after, needs_conversion_after, anomalies_after = analyze_amount_units(conn)

            print(f"  Normal contracts: {len(normal_after)}")
            print(f"  Needs conversion: {len(needs_conversion_after)}")
            print(f"  Anomalies: {len(anomalies_after)}")

    conn.close()


if __name__ == "__main__":
    dry_run = "--execute" not in sys.argv

    if "--execute" in sys.argv:
        print("[WARN] About to execute database modifications!")
        confirm = input("Confirm amount unit conversion? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            sys.exit(0)

    fix_amount_units(dry_run=dry_run)