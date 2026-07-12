"""针对性修复: 阶段名 + 残留OCR垃圾清理"""
import sqlite3, re
db = sqlite3.connect('/app/database/project_management.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()

fixes = 0

# ===== 1. 修复阶段名: 去除"完成完成"重复 + 截断过长 =====
for s in db.execute('SELECT stage_id, stage_name, remarks, acceptance_criteria FROM stages WHERE stage_name LIKE "完成完成%" OR stage_name LIKE "开展开展%" OR LENGTH(stage_name) > 40').fetchall():
    sid, name, remarks, ac = s
    
    # 从remarks中提取更简洁的阶段名
    rm = (remarks or '').strip()
    
    # 提取第一个关键动词短语 (20-30字)
    m = re.search(r'[（(]?\d+[．.)）]?\s*(.{15,30}?)[。，,\.\s；;]', rm)
    if m:
        new_name = m.group(1).strip()
        # 去掉开头的 "完成" (如果后面还有内容)
        new_name = re.sub(r'^(完成|开展|研发|构建|研制)\s*', '', new_name)
        new_name = new_name.strip()
    else:
        # 取remarks前25字
        new_name = rm[:25].strip()
    
    if new_name and new_name != name and len(new_name) >= 5:
        cursor.execute('UPDATE stages SET stage_name=? WHERE stage_id=?', (new_name, sid))
        fixes += 1

# ===== 2. 清理ac末尾残留页码 =====
for s in db.execute('SELECT stage_id, acceptance_criteria FROM stages WHERE acceptance_criteria IS NOT NULL AND acceptance_criteria != ""').fetchall():
    sid, ac = s
    cleaned = ac
    
    # 去掉末尾的 " 7"、" 6" 等孤立数字
    cleaned = re.sub(r'\s+\d{1,2}\s*$', '', cleaned)
    # 去掉末尾的 "7"、"8"等（如果前面是换行或空格）
    cleaned = re.sub(r'\s+\d+\s*$', '', cleaned)
    
    if cleaned != ac:
        cursor.execute('UPDATE stages SET acceptance_criteria=? WHERE stage_id=?', (cleaned.strip(), sid))
        fixes += 1

# ===== 3. 修复阶段号混入词语 =====
for s in db.execute('SELECT stage_id, remarks, acceptance_criteria FROM stages').fetchall():
    sid, remarks, ac = s
    updates = {}
    
    if remarks:
        cleaned = remarks
        # 修复 "时5.4序" → "时序"、"问5.6题" → "问题"、"专5.3利" → "专利"、"验5.6收" → "验收"
        for old, new in [
            (r'时(\d+\.\d+)序', '时序'),
            (r'问(\d+\.\d+)题', '问题'),
            (r'专(\d+\.\d+)利', '专利'),
            (r'验(\d+\.\d+)收', '验收'),
            (r'申(\d+\.\d+)报', '申报'),
            (r'开(\d+\.\d+)展', '开展'),
        ]:
            cleaned = re.sub(old, new, cleaned)
        
        if cleaned != remarks:
            updates['remarks'] = cleaned
    
    if ac:
        cleaned = ac
        for old, new in [
            (r'时(\d+\.\d+)序', '时序'),
            (r'问(\d+\.\d+)题', '问题'),
            (r'专(\d+\.\d+)利', '专利'),
            (r'验(\d+\.\d+)收', '验收'),
            (r'申(\d+\.\d+)报', '申报'),
            (r'开(\d+\.\d+)展', '开展'),
        ]:
            cleaned = re.sub(old, new, cleaned)
        
        # 去掉开头的 "研究，" / "研究资料，" 等残留前缀
        cleaned = re.sub(r'^(研究[，,]\s*)(.{3,})', r'\2', cleaned)
        cleaned = re.sub(r'^(研究资料[，,]\s*)(.{3,})', r'\2', cleaned)
        
        if cleaned != ac:
            updates['acceptance_criteria'] = cleaned
    
    if updates:
        set_clause = ', '.join(f'{k}=?' for k in updates)
        values = list(updates.values()) + [sid]
        cursor.execute(f'UPDATE stages SET {set_clause} WHERE stage_id=?', values)
        fixes += 1

# ===== 4. 清理空的/无意义的付款记录 =====
deleted = 0
for p in db.execute('SELECT payment_id FROM payments WHERE payment_stage = "" AND payment_condition = "" AND (planned_amount = 0 OR planned_amount IS NULL)'):
    cursor.execute('DELETE FROM payments WHERE payment_id=?', (p[0],))
    deleted += 1

# 对于有金额但无描述的付款
for p in db.execute('SELECT payment_id, contract_id, payment_stage, planned_amount FROM payments WHERE payment_stage = "" AND payment_condition = "" AND planned_amount > 0'):
    print(f'⚠ 待手动: {p["contract_id"]} {p["payment_id"]} amount={p["planned_amount"]}')

db.commit()
print(f'阶段名修复: {fixes} 项, 付款清理: {deleted} 条')

# 抽查
for cid in ['ZH02-202604026', 'ZH02-202604020']:
    print(f'\n=== {cid} 最终 ===')
    for s in db.execute('SELECT stage_number, stage_name, remarks, acceptance_criteria FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)):
        ac = s['acceptance_criteria'] or ''
        rm = s['remarks'] or ''
        print(f'  #{s["stage_number"]}: [{s["stage_name"]}]')
        if '考核目标' in rm: print('    ⚠ remarks仍含考核目标')
        print(f'    主要内容({len(rm)}字): {rm[:80]}')
        print(f'    考核目标({len(ac)}字): {ac[:80]}')

db.close()
