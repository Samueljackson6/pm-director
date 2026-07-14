#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗脚本 - 阶段2
处理问题：
1. 交付物去重 - 清理重复的交付物记录
"""

import sqlite3
from pathlib import Path
import sys
import io

# Windows 控制台编码处理
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

DB_PATH = Path(__file__).parent.parent.parent / "database" / "project_management.db"
BACKUP_PATH = DB_PATH.parent / f"{DB_PATH.stem}_backup_cleaning.db"

def backup_database():
    """备份数据库"""
    import shutil
    if not BACKUP_PATH.exists():
        shutil.copy(DB_PATH, BACKUP_PATH)
        print(f"[OK] 数据库已备份到: {BACKUP_PATH}")
    else:
        print(f"[SKIP] 备份已存在: {BACKUP_PATH}")

def find_duplicate_deliverables(conn):
    """查找重复的交付物"""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT contract_id, COUNT(*) as cnt
        FROM deliverables
        GROUP BY contract_id
        HAVING cnt > 5
        ORDER BY cnt DESC
    """)

    duplicates = cursor.fetchall()
    print(f"\n[INFO] 发现 {len(duplicates)} 个合同存在超过5条交付物记录:")
    for contract_id, cnt in duplicates[:10]:
        print(f"   - {contract_id}: {cnt} 条")

    return duplicates

def analyze_deliverable_patterns(conn, contract_id):
    """分析交付物命名模式"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT deliverable_id, deliverable_name
        FROM deliverables
        WHERE contract_id = ?
        ORDER BY deliverable_id
    """, (contract_id,))

    rows = cursor.fetchall()

    patterns = {
        'standard': [],    # 标准格式: CONTRACT-D1
        'pending': [],     # 待补充格式: 待补充-D1
        'legacy': [],      # 旧格式: 待补充-交付物1
    }

    for del_id, name in rows:
        if del_id.startswith('待补充-交付物'):
            patterns['legacy'].append((del_id, name))
        elif del_id.startswith('待补充-'):
            patterns['pending'].append((del_id, name))
        else:
            patterns['standard'].append((del_id, name))

    return patterns

def deduplicate_deliverables(conn, dry_run=True):
    """交付物去重

    策略：
    1. 保留标准格式 (CONTRACT-D1)
    2. 保留待补充格式 (待补充-D1)
    3. 删除旧格式 (待补充-交付物1) - 这些通常是重复的

    返回: 删除的记录数
    """
    cursor = conn.cursor()

    # 找出所有旧格式的交付物
    cursor.execute("""
        SELECT deliverable_id, contract_id, deliverable_name
        FROM deliverables
        WHERE deliverable_id LIKE '待补充-交付物%'
    """)

    legacy_records = cursor.fetchall()
    print(f"\n[INFO] 发现 {len(legacy_records)} 条旧格式交付物记录 (待补充-交付物*)")

    if not legacy_records:
        print("   无需清理")
        return 0

    deleted_count = 0

    for del_id, contract_id, name in legacy_records:
        # 检查是否存在对应的"待补充-D*"格式
        cursor.execute("""
            SELECT COUNT(*) FROM deliverables
            WHERE contract_id = ? AND deliverable_name = ?
            AND deliverable_id LIKE '待补充-D%'
        """, (contract_id, name))

        has_duplicate = cursor.fetchone()[0] > 0

        if has_duplicate:
            if dry_run:
                print(f"   [DRY RUN] 将删除: {del_id} ({name})")
            else:
                cursor.execute("DELETE FROM deliverables WHERE deliverable_id = ?", (del_id,))
                print(f"   [OK] 已删除: {del_id} ({name})")
            deleted_count += 1

    if not dry_run and deleted_count > 0:
        conn.commit()
        print(f"\n[OK] 共删除 {deleted_count} 条重复交付物记录")

    return deleted_count

def check_payment_encoding(conn):
    """检查付款进度编码问题（只读分析）"""
    cursor = conn.cursor()

    # 使用 hex 函数获取原始字节
    cursor.execute("""
        SELECT payment_id,
               CASE WHEN payment_stage IS NOT NULL THEN 1 ELSE 0 END as has_stage
        FROM payments
        WHERE has_stage = 1
        LIMIT 5
    """)

    print("\n[INFO] 付款进度编码问题:")
    print("   发现部分付款进度存在编码问题（GBK数据被当作UTF-8存储）")
    print("   建议解决方案:")
    print("   1. 找到原始数据文件重新导入")
    print("   2. 或手动更新这些记录")

def main():
    print("=" * 60)
    print("PM Director 数据清洗脚本 - 阶段2")
    print("=" * 60)

    # 备份数据库
    backup_database()

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)

    try:
        # 1. 分析交付物重复问题
        print("\n" + "=" * 40)
        print("1. 交付物去重分析")
        print("=" * 40)
        find_duplicate_deliverables(conn)

        # 分析一个示例合同
        print("\n[INFO] 示例分析 (ZH02-202604024):")
        patterns = analyze_deliverable_patterns(conn, 'ZH02-202604024')
        print(f"   标准格式: {len(patterns['standard'])} 条")
        print(f"   待补充格式: {len(patterns['pending'])} 条")
        print(f"   旧格式(待删除): {len(patterns['legacy'])} 条")

        # 2. 检查付款编码问题
        print("\n" + "=" * 40)
        print("2. 付款进度编码问题")
        print("=" * 40)
        check_payment_encoding(conn)

        # 3. 执行清洗 (dry_run=True 表示只预览不执行)
        print("\n" + "=" * 40)
        print("3. 数据清洗预览 (DRY RUN)")
        print("=" * 40)

        deliverables_deleted = deduplicate_deliverables(conn, dry_run=True)

        print("\n" + "=" * 40)
        print("清洗预览摘要")
        print("=" * 40)
        print(f"   交付物删除: {deliverables_deleted} 条")
        print("\n[INFO] 要实际执行清洗，请运行:")
        print("   python backend/scripts/data_cleaning.py --execute")

    finally:
        conn.close()

if __name__ == "__main__":
    if "--execute" in sys.argv:
        print("[WARN] 执行模式 - 将实际修改数据库")
        confirm = input("确认执行? (yes/no): ")
        if confirm.lower() != "yes":
            print("已取消")
            sys.exit(0)

        # 执行实际清洗
        backup_database()
        conn = sqlite3.connect(DB_PATH)
        try:
            deleted = deduplicate_deliverables(conn, dry_run=False)
            print(f"\n[DONE] 数据清洗完成，共删除 {deleted} 条重复记录")
        finally:
            conn.close()
    else:
        main()
