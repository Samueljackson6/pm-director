#!/usr/bin/env python3
"""
供应商 + 项目团队数据填充方案
"""
import sqlite3, re, uuid
from collections import defaultdict

db = sqlite3.connect('database/project_management.db')
db.row_factory = sqlite3.Row

print('=' * 60)
print('方案: 供应商 + 项目团队数据填充')
print('=' * 60)

# ============================================================
# 方案1: 供应商数据
# ============================================================
# 从 contracts 表中提取乙方(供应商)和甲方(客户)作为供应商
# suppliers 表结构: supplier_id, supplier_name, contact_person, phone, address, category, remark

print('\n## 方案1: 供应商填充')
print('\n数据源: contracts.party_b + party_a')

# 乙方去重（供应商）
b_parties = db.execute('SELECT DISTINCT party_b FROM contracts WHERE party_b IS NOT NULL AND party_b != ""').fetchall()
# 甲方去重（可同时作为供应商的）
a_parties = db.execute('SELECT DISTINCT party_a FROM contracts WHERE party_a IS NOT NULL AND party_a != ""').fetchall()

print(f'  乙方(供应商): {len(b_parties)} 个')
print(f'  甲方(客户): {len(a_parties)} 个')
print(f'  合计: {len(set([r[0] for r in b_parties] + [r[0] for r in a_parties]))} 个')

# 展示样例
print('\n乙方(供应商)示例:')
for r in b_parties:
    cnt = db.execute('SELECT COUNT(*) FROM contracts WHERE party_b=?', (r[0],)).fetchone()[0]
    print(f'  {r[0][:40]:40s} 关联{cnt}个合同')

print('\n甲方(客户)前5:')
for r in a_parties[:5]:
    cnt = db.execute('SELECT COUNT(*) FROM contracts WHERE party_a=?', (r[0],)).fetchone()[0]
    print(f'  {r[0][:40]:40s} 关联{cnt}个合同')

# ============================================================
# 方案2: 项目团队数据
# ============================================================
print('\n\n## 方案2: 项目团队填充')
print('\n数据源1: contracts 表的 project_leader / party_a_contact / party_b_contact')
print('数据源2: OCR 项目简表中的团队成员（科研类合同）')
print('数据源3: 如果有外部人员数据源可批量导入')

# 当前联系人统计
leaders = db.execute('SELECT COUNT(*) FROM contracts WHERE project_leader IS NOT NULL AND project_leader != ""').fetchone()[0]
a_contacts = db.execute('SELECT COUNT(*) FROM contracts WHERE party_a_contact IS NOT NULL AND party_a_contact != ""').fetchone()[0]
b_contacts = db.execute('SELECT COUNT(*) FROM contracts WHERE party_b_contact IS NOT NULL AND party_b_contact != ""').fetchone()[0]

print(f'\n当前可用人员数据:')
print(f'  项目负责人: {leaders}/42')
print(f'  甲方联系人: {a_contacts}/42')
print(f'  乙方联系人: {b_contacts}/42')

# 展示样例
print('\n项目人员示例（前10）:')
people = db.execute('''
    SELECT contract_id, project_leader, party_a_contact, party_a_phone, party_b_contact, party_b_phone, project_name
    FROM contracts 
    WHERE project_leader IS NOT NULL AND project_leader != ""
    LIMIT 10
''').fetchall()
for p in people:
    d = dict(p)
    print(f'  {d["contract_id"][:25]:25s} 负责人={d["project_leader"]} 甲方={d["party_a_contact"]} 乙方={d["party_b_contact"]}')

# 分析科研合同OCR中"项目简表"的人员信息
print('\n\n## 科研合同OCR项目简表人员分析')
ocr_dir = 'cache/ocr'
research = ['ZH02-202408007','ZH02-202507011','ZH02-202509025',
            'ZH02-202604020','ZH02-202604021','ZH02-202604023',
            'ZH02-202604024','ZH02-202604025','ZH02-202604026']

import os
for cid in research:
    fpath = os.path.join(ocr_dir, f'{cid}_ocr.txt')
    if not os.path.exists(fpath):
        fpath = os.path.join(ocr_dir, f'{cid}_full_ocr.txt')
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 找项目简表区域
    idx = text.find('项目简表')
    if idx < 0:
        continue
    
    section = text[idx:idx+600]
    # 提取姓名/单位/职称
    names = []
    for m in re.finditer(r'姓名\n(.+)', section):
        name = m.group(1).strip()
        if re.match(r'^[\u4e00-\u9fff]{2,4}$', name):
            names.append(name)
    if names:
        print(f'  {cid}: 项目简表人员={names}')

db.close()
