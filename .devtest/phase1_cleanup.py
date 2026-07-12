#!/usr/bin/env python3
"""
阶段1: 数据深度清理 + 阶段考核目标彻底清洗
阶段2: 人员数据填充（从contracts联系人）
阶段3: 供应商数据填充（从contracts甲乙方）
"""
import sqlite3, re, uuid

db = sqlite3.connect('database/project_management.db')
db.row_factory = sqlite3.Row

print('='*60)
print('Phase 1: 阶段考核目标深度清洗')
print('='*60)

# 更彻底的清洗模式
patterns_to_clean = [
    (r'\[\s*第\d+\s*页\s*\]', ''),           # [第N页]
    (r'SGTYHT/\d+[\u2014\u2013\-\uFF0D]\w+[\u2014\u2013\-\uFF0D]\w+', ''),  # SGTYHT/XX-XX-XXX
    (r'合同编号[：:]\s*\w+', ''),             # 合同编号:XXX
    (r'科学技术项目合同', ''),                # 模板名
    (r'技术服务合同', ''),
    (r'\b\d+\s*$', ''),                      # 行末尾孤立数字
    (r'\n\s*\d+\s*$', ''),                    # 换行后的孤立数字
]

cl_ct = 0
for col in ['acceptance_criteria', 'remarks']:
    rows = db.execute(f'SELECT stage_id, contract_id, {col} FROM stages WHERE {col} IS NOT NULL AND {col} != ""').fetchall()
    for r in rows:
        old = r[col] or ''
        new = old
        for pat, repl in patterns_to_clean:
            new = re.sub(pat, repl, new)
        new = re.sub(r'\s+', ' ', new).strip()
        if new != old:
            db.execute(f'UPDATE stages SET {col}=? WHERE stage_id=?', (new, r['stage_id']))
            cl_ct += 1
print(f'  清洗: {cl_ct} 条')

print()
print('='*60)
print('Phase 2: personnel 表填充（从contracts联系人）')
print('='*60)

# 提取所有人员并去重
people = {}  # name -> {phone, role}
for r in db.execute('SELECT contract_id, project_leader, party_a_contact, party_a_phone, party_b_contact, party_b_phone FROM contracts').fetchall():
    d = dict(r)
    for field, role in [('project_leader','project_leader'), ('party_a_contact','party_a_contact'), ('party_b_contact','party_b_contact')]:
        name = d.get(field) or ''
        name = name.strip()
        if not name or len(name) < 2:
            continue
        phone = d.get(field.replace('contact','phone')) or ''
        if name not in people:
            people[name] = {'phone': phone, 'roles': set(), 'contracts': []}
        people[name]['roles'].add(role)
        people[name]['contracts'].append(d['contract_id'])

print(f'  去重人员: {len(people)} 个')

# 写入personnel表
person_ids = {}  # name -> person_id
for name, info in people.items():
    pid = 'P' + uuid.uuid4().hex[:8].upper()
    db.execute('INSERT INTO personnel (person_id, person_name, phone, role_tags) VALUES (?,?,?,?)',
               (pid, name, info['phone'], ' '.join(info['roles'])))
    person_ids[name] = pid
print(f'  写入personnel: {len(person_ids)} 行')

# 写入project_personnel表
pp_count = 0
for name, info in people.items():
    pid = person_ids[name]
    for cid in info['contracts']:
        roles = ','.join(info['roles'])
        db.execute('INSERT INTO project_personnel (person_id, project_id, role_type, is_active) VALUES (?,?,?,1)',
                   (pid, cid, roles))
        pp_count += 1
print(f'  写入project_personnel: {pp_count} 行')

print()
print('='*60)
print('Phase 3: suppliers 表填充（从contracts甲乙方）')
print('='*60)

# 清理乙方名称中的OCR垃圾
def clean_name(n):
    n = re.sub(r'\s*签订日期[：:].*$', '', n)
    n = re.sub(r'\s*签订时间[：:].*$', '', n)
    n = re.sub(r'\s*合同编号.*$', '', n)
    return n.strip()

# 删除重复的乙方记录
for bad_name in ['北京振华永创智能科技有限公司签订日期：', '北京振华永创智能科技有限公司签订时间：']:
    db.execute(f'DELETE FROM suppliers WHERE supplier_name=?', (bad_name,))

# 提取所有去重后的公司
companies = {}
for r in db.execute('SELECT DISTINCT party_a FROM contracts WHERE party_a IS NOT NULL').fetchall():
    name = r[0].strip()
    if name and len(name) > 3:
        companies[name] = {'role': 'customer', 'count': 0}
for r in db.execute('SELECT DISTINCT party_b FROM contracts WHERE party_b IS NOT NULL').fetchall():
    name = clean_name(r[0])
    if name and len(name) > 3:
        if name not in companies:
            companies[name] = {'role': 'supplier', 'count': 0}

# 统计关联合同数
for name in companies:
    a_cnt = db.execute('SELECT COUNT(*) FROM contracts WHERE party_a=?', (name,)).fetchone()[0]
    b_cnt = db.execute('SELECT COUNT(*) FROM contracts WHERE party_b LIKE ?', (name+'%',)).fetchone()[0]
    companies[name]['count'] = a_cnt + b_cnt

# 写入suppliers表
supplier_count = 0
for name, info in sorted(companies.items(), key=lambda x: -x[1]['count']):
    existing = db.execute('SELECT supplier_id FROM suppliers WHERE supplier_name=?', (name,)).fetchone()
    if existing:
        continue
    sid = 'S' + uuid.uuid4().hex[:6].upper()
    db.execute('INSERT INTO suppliers (supplier_id, supplier_name, notes) VALUES (?,?,?)',
               (sid, name, info['role'] + ' ' + str(info['count']) + ' contracts'))
    supplier_count += 1

print(f'  新增供应商: {supplier_count} 个')

db.commit()
db.close()
print('\n完成')
