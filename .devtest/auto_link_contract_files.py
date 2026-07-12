"""
自动关联本地合同文件（PDF/Word）到 contract_files 表
扫描 F:/temp/pm-director-ht/项目合同/ 目录，提取 ZH02* ID，匹配合同并入库
"""
import sqlite3
import os
import re
from datetime import datetime

DB = 'database/project_management.db'
DOCX_DIR = 'F:/temp/pm-director-ht/项目合同'

def extract_contract_id(filename: str) -> str | None:
    """从文件名提取 ZH02* 合同编号"""
    m = re.search(r'(ZH02-\d{6,})', filename)
    if m:
        return m.group(1)
    return None

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # 获取所有合同 ID
    cur.execute("SELECT contract_id FROM contracts")
    valid_ids = set(r[0] for r in cur.fetchall())

    # 扫描目录
    if not os.path.exists(DOCX_DIR):
        print(f"目录不存在: {DOCX_DIR}")
        return

    files = [f for f in os.listdir(DOCX_DIR)
             if f.lower().endswith(('.pdf', '.docx', '.doc'))]

    print(f"扫描到 {len(files)} 个 PDF/Word 文件")

    matched = 0
    for fname in files:
        cid = extract_contract_id(fname)
        if not cid or cid not in valid_ids:
            # 尝试模糊匹配
            cur.execute("SELECT contract_id FROM contracts WHERE project_name LIKE ? LIMIT 1",
                        (f"%{fname.split('-')[0].strip()}%",))
            row = cur.fetchone()
            if row:
                cid = row[0]
            else:
                print(f"  ❌ 未匹配: {fname}")
                continue

        # 检查是否已存在
        cur.execute("SELECT 1 FROM contract_files WHERE contract_id=? AND file_name=?", (cid, fname))
        if cur.fetchone():
            continue

        # 入库
        fpath = os.path.join(DOCX_DIR, fname)
        fsize = os.path.getsize(fpath) if os.path.exists(fpath) else 0
        ext = os.path.splitext(fname)[1].lower()
        file_id = f"FILE{int(datetime.now().timestamp()*1000)}{matched}"

        cur.execute("""INSERT INTO contract_files
            (file_id, contract_id, file_name, file_type, file_path, file_size, upload_time, is_latest)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            (file_id, cid, fname, ext, fpath, fsize, datetime.now().isoformat()))

        matched += 1
        print(f"  ✅ 关联: {cid} <- {fname}")

    conn.commit()
    conn.close()
    print(f"\n完成：{matched} 个文件已关联到 contract_files 表")

if __name__ == '__main__':
    main()
