#!/usr/bin/env python3
"""
pm-director 合同数据清洗脚本
清洗规则：
1. project_name → official_name：去合约ID前缀、去OCR残留、去-精简版
2. party_a：去"受托方(乙方):公司名"后缀
3. sign_date：修正异常年份
"""
import sqlite3, re, sys
from pathlib import Path

DB = Path(__file__).parent.parent / 'database' / 'project_management.db'
conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# ── 1. 读取全部合同 ──
cur.execute("SELECT rowid, * FROM contracts ORDER BY contract_id")
rows = cur.fetchall()
print(f"共 {len(rows)} 条合同")

# ── 2. 清洗函数 ──
def clean_project_name(name: str) -> str:
    if not name:
        return name
    # 去合约ID前缀：ZH02-XXXXXXXX 或 SGSCXXX 开头的编号(但不删除整个字符串如果编号就是内容)
    # ZH02- 打头的编号前缀（含后续紧跟的-或空格）
    name = re.sub(r'^(ZH02-\d{6,9})[\s-]*', '', name)
    # SGSC 开头的也可能是编号前缀（在project_name开头出现）
    # 但有些合同名本身就包含 SGSC（如合同编号字段），需要判断
    # 只去除 project_name 开头明确的编号标记
    name = re.sub(r'^(SGSC\w+)[\s-]*', '', name)
    # 去 -精简版 后缀
    name = re.sub(r'[-－—]\s*精简版\s*$', '', name)
    # 去 (OCR 后缀
    name = re.sub(r'\s*\(OCR\s*$', '', name)
    # 去 (签署版 后缀 — 这是正常的合同标记，保留
    # 去首尾空格和多余空格
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def clean_party_a(party: str) -> str:
    if not party:
        return party
    # 去 "受托方(乙方):北京振华永创智能科技有限公司"
    party = re.sub(r'受托方\(乙方\):?\s*北京振华永创智能科技有限公司\s*', '', party)
    # 去 "受托方(乙方):" 单独出现
    party = re.sub(r'受托方\(乙方\):?\s*', '', party)
    # 去 "签订日期" 残留
    party = re.sub(r'签订日期.*', '', party)
    return party.strip()

def clean_sign_date(date_str: str) -> str:
    if not date_str:
        return date_str
    # 修正 2075 → 2025（OCR识别错误）
    if date_str.startswith('207'):
        date_str = '202' + date_str[3:]
    return date_str

# ── 3. 执行清洗 ──
stats = {'cleaned_name': 0, 'cleaned_party': 0, 'cleaned_date': 0, 'filled_type': 0, 'official_filled': 0}

for r in rows:
    rowid = r['rowid']
    changes = []
    
    # 3a. project_name → official_name
    raw_name = r['project_name'] or ''
    cleaned = clean_project_name(raw_name)
    if cleaned and cleaned != raw_name:
        cur.execute("UPDATE contracts SET official_name = ? WHERE rowid = ?", (cleaned, rowid))
        stats['official_filled'] += 1
        stats['cleaned_name'] += 1
        print(f"  [名称] {r['contract_id']}: {raw_name[:50]}... → {cleaned}")
    elif cleaned and not r['official_name']:
        # 即使没有清洗，也把当前project_name填入official_name（如本身已干净）
        cur.execute("UPDATE contracts SET official_name = ? WHERE rowid = ?", (cleaned, rowid))
        stats['official_filled'] += 1
    
    # 3b. party_a 清洗
    raw_party = r['party_a'] or ''
    party_cleaned = clean_party_a(raw_party)
    if party_cleaned != raw_party:
        cur.execute("UPDATE contracts SET party_a = ? WHERE rowid = ?", (party_cleaned, rowid))
        stats['cleaned_party'] += 1
        print(f"  [甲方] {r['contract_id']}: 清洗甲方")
    
    # 3c. sign_date 修正
    raw_date = r['sign_date'] or ''
    date_cleaned = clean_sign_date(raw_date)
    if date_cleaned != raw_date:
        cur.execute("UPDATE contracts SET sign_date = ? WHERE rowid = ?", (date_cleaned, rowid))
        stats['cleaned_date'] += 1
        print(f"  [日期] {r['contract_id']}: {raw_date} → {date_cleaned}")
    
    # 3d. project_type 补充（根据名称判断）
    if not r['project_type']:
        name_lower = (r['project_name'] or '').lower()
        if '科研' in name_lower or '研究' in name_lower or '研发' in name_lower or '科技' in name_lower:
            cur.execute("UPDATE contracts SET project_type = '科研类' WHERE rowid = ?", (rowid,))
            stats['filled_type'] += 1
            print(f"  [类型] {r['contract_id']}: 补充为 科研类")
        elif '服务' in name_lower or '维护' in name_lower or '技术' in name_lower or '监测' in name_lower:
            cur.execute("UPDATE contracts SET project_type = '服务类' WHERE rowid = ?", (rowid,))
            stats['filled_type'] += 1
            print(f"  [类型] {r['contract_id']}: 补充为 服务类")

conn.commit()

# ── 4. 统计报告 ──
print(f"\n{'='*50}")
print(f"清洗统计:")
print(f"  official_name 已填写: {stats['official_filled']}")
print(f"  project_name 已清洗: {stats['cleaned_name']}")
print(f"  party_a 已清洗:     {stats['cleaned_party']}")
print(f"  sign_date 已修正:   {stats['cleaned_date']}")
print(f"  project_type 已补充: {stats['filled_type']}")
print(f"{'='*50}")

# 显示清洗后样例
print(f"\n清洗后样例:")
cur.execute("SELECT contract_id, official_name, party_a, sign_date, project_type FROM contracts LIMIT 10")
for r in cur.fetchall():
    print(f"  {r['contract_id']}: {r['official_name'][:40] if r['official_name'] else '?' :40s} | {r['party_a'][:20] if r['party_a'] else '?':20s} | {r['sign_date'] or '?'} | {r['project_type'] or '?'}")

conn.close()
print("\n✅ 数据清洗完成")
