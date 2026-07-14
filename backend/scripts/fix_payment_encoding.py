#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
付款进度编码修复脚本
问题：数据以 GBK 编码存入，但被当作 UTF-8 存储
解决：以二进制模式读取原始字节，用 GBK 解码后更新
"""

import sqlite3
from pathlib import Path
import sys
import io

# Windows 控制台编码
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

DB_PATH = Path(__file__).parent.parent.parent / "database" / "project_management.db"

def fix_payment_encoding():
    """修复付款进度编码"""
    # 以二进制模式连接，避免自动解码
    conn = sqlite3.connect(DB_PATH)

    # 设置 text_factory 为 bytes，返回原始字节
    conn.text_factory = bytes

    cursor = conn.cursor()

    # 获取所有有付款阶段的记录（作为原始字节）
    cursor.execute("SELECT payment_id, payment_stage FROM payments WHERE payment_stage IS NOT NULL")
    rows = cursor.fetchall()

    fixed_count = 0
    error_count = 0
    skipped_count = 0

    print(f"[INFO] 共有 {len(rows)} 条付款记录需要检查")

    # 切换回字符串模式进行更新
    conn.text_factory = str

    for payment_id, stage_bytes in rows:
        if not stage_bytes:
            skipped_count += 1
            continue

        try:
            # 尝试用 GBK 解码原始字节
            decoded_stage = stage_bytes.decode('gbk')

            # 检查解码结果是否合理（不包含大量替换字符）
            if decoded_stage.count('�') < len(decoded_stage) * 0.1:
                # 更新记录
                cursor.execute(
                    "UPDATE payments SET payment_stage = ? WHERE payment_id = ?",
                    (decoded_stage, payment_id.decode() if isinstance(payment_id, bytes) else payment_id)
                )
                fixed_count += 1
                print(f"[OK] {payment_id}: 已修复 -> {decoded_stage[:30]}...")
            else:
                skipped_count += 1

        except Exception as e:
            error_count += 1
            pid = payment_id.decode() if isinstance(payment_id, bytes) else payment_id
            print(f"[ERR] {pid}: {e}")

    if fixed_count > 0:
        conn.commit()
        print(f"\n[OK] 共修复 {fixed_count} 条付款进度记录")

    if skipped_count > 0:
        print(f"[INFO] 跳过 {skipped_count} 条记录")

    if error_count > 0:
        print(f"[WARN] {error_count} 条记录处理出错")

    conn.close()
    return fixed_count

if __name__ == "__main__":
    print("=" * 60)
    print("付款进度编码修复脚本")
    print("=" * 60)

    fixed = fix_payment_encoding()
    print(f"\n[DONE] 修复完成，共 {fixed} 条记录")
