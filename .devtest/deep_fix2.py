"""全量深度修复: 付款截断 + remarks/ac去重 + service_content清洗"""
import sqlite3, re
DB = '/app/database/project_management.db'
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()
stats = {'pay_fix': 0, 'rm_ac_dedup': 0, 'sc_clean': 0}

# === 1. 付款截断修复 ===
# 模式: "北京振华永...收到乙方开具的...202X年" → 补全
for p in db.execute("SELECT * FROM payments WHERE payment_stage LIKE '%202%年' OR payment_condition LIKE '%202%年'").fetchall():
    pid = p['payment_id']
    updates = {}
    for field in ['payment_stage', 'payment_condition']:
        val = (p[field] or '').strip()
        if not val or len(val) < 20:
            continue
        # 检测截断: 末尾是 "202X年" 或 "公司名 202X年"
        if re.search(r'(收到乙方开具的|开具的等额|乙方开具的)\s*\d{4}年$', val):
            # 补全标准模板
            cleaned = re.sub(r'\s*\d{4}年$', '', val)
            cleaned += '增值税专用发票后，按合同约定支付'
            if cleaned != val:
                updates[field] = cleaned
        # 检测截断: "振华永" 是 "振华永创智能科技" 的断裂
        if '振华永' in val and re.search(r'振华永\w{0,3}$', val):
            # "北京振华永" → "北京振华永创智能科技"
            cleaned = val.replace('振华永', '振华永创智能科技')
            cleaned = re.sub(r'\s*\d{4}年$', '', cleaned)
            cleaned += '增值税专用发票后，按合同约定支付'
            if cleaned != val:
                updates[field] = cleaned

    if updates:
        sets = ', '.join(f'{k}=?' for k in updates)
        vals = list(updates.values()) + [pid]
        cur.execute(f'UPDATE payments SET {sets} WHERE payment_id=?', vals)
        stats['pay_fix'] += 1

# === 2. remarks/ac 高度重复去重 ===
for s in db.execute('SELECT stage_id, remarks, acceptance_criteria FROM stages WHERE remarks IS NOT NULL AND acceptance_criteria IS NOT NULL AND remarks != "" AND acceptance_criteria != ""').fetchall():
    rm = (s['remarks'] or '').strip()
    ac = (s['acceptance_criteria'] or '').strip()
    if len(rm) < 20 or len(ac) < 20:
        continue
    
    # 计算重叠度
    common = len(set(rm) & set(ac))
    shorter = min(len(rm), len(ac))
    if shorter == 0 or common / shorter < 0.75:
        continue
    
    # 高度重复: 保留更完整的版本在ac, 精简remarks
    # acceptance_criteria 应该更结构化(考核目标), remarks 是主要内容
    # 如果几乎相同, 保留ac不动, 移除remarks中与ac重复的部分
    rm_set = set(rm)
    # 去重: 保留ac, 精简rm为非重复部分
    new_rm = rm
    # 如果rm包含ac的内容, 去掉重叠
    if ac in rm:
        new_rm = rm.replace(ac, '').strip().rstrip('，,。；;')
    elif rm in ac:
        new_rm = ''  # rm完全在ac内, 清空rm
    
    if new_rm != rm:
        cur.execute('UPDATE stages SET remarks=? WHERE stage_id=?', (new_rm, s['stage_id']))
        stats['rm_ac_dedup'] += 1

# === 3. service_content 残余清洗 ===
for c in db.execute("SELECT * FROM contracts WHERE project_type='服务类' OR project_type IS NULL").fetchall():
    cid = c['contract_id']
    updates = {}
    
    for field in ['service_content', 'service_quality', 'service_schedule']:
        val = (c[field] if field in c.keys() else '') or ''
        if not val:
            continue
        cleaned = val
        
        # 移除3.x/4.x章节
        cleaned = re.sub(r'3[\.\、]\s*甲方提供的工作条件及协作事项.*$', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'4[\.\、]\s*组织与管理.*$', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'3[\.\、]1\s*提供的工作条件.*$', '', cleaned, flags=re.DOTALL)
        
        # 移除OCR图形字符
        cleaned = re.sub(r'[∠⊥]', '', cleaned)
        cleaned = re.sub(r'_{3,}', '', cleaned)
        
        # 移除模板编号
        cleaned = re.sub(r'SGTYHT\s*/\s*\d+\s*[—\-]\s*JS\s*[—\-]\s*\d+', '', cleaned)
        cleaned = re.sub(r'SGSCD\w{10,}', '', cleaned)
        cleaned = re.sub(r'合同编号[：:]\s*\w{10,}', '', cleaned)
        
        # 清理
        cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()
        
        if cleaned != val:
            updates[field] = cleaned
    
    if updates:
        sets = ', '.join(f'{k}=?' for k in updates)
        vals = list(updates.values()) + [cid]
        cur.execute(f'UPDATE contracts SET {sets} WHERE contract_id=?', vals)
        stats['sc_clean'] += 1

db.commit()
print(f'付款截断修复: {stats["pay_fix"]} 条')
print(f'remarks/ac去重: {stats["rm_ac_dedup"]} 阶段')
print(f'service_content清洗: {stats["sc_clean"]} 合同')

# === 终审 ===
print('\n=== 终审 ===')
count = 0
for c in db.execute('SELECT * FROM contracts ORDER BY contract_id').fetchall():
    cid = c['contract_id']
    ptype = c['project_type'] or '未分类'
    c_issues = []
    
    # 付款截断
    for p in db.execute('SELECT * FROM payments WHERE contract_id=?', (cid,)).fetchall():
        for field in ['payment_stage', 'payment_condition']:
            val = (p[field] or '').strip()
            if val and len(val) > 15 and re.search(r'收到乙方开具的\s*\d{4}年$|振华永\w{0,5}$', val):
                c_issues.append(f'{p["payment_id"]} {field}截断')
    
    # 阶段重复
    for s in db.execute('SELECT * FROM stages WHERE contract_id=?', (cid,)).fetchall():
        rm = (s['remarks'] or '').strip()
        ac = (s['acceptance_criteria'] or '').strip()
        if rm and ac and len(rm) > 20 and len(ac) > 20:
            common = len(set(rm) & set(ac))
            shorter = min(len(rm), len(ac))
            if shorter > 0 and common / shorter > 0.75:
                c_issues.append(f'阶段{s["stage_number"]} remarks/ac重复')
    
    # service_content污染
    if ptype == '服务类':
        sc = (c['service_content'] or '')
        if '3.甲方提供' in sc or '组织与管理' in sc:
            c_issues.append('service_content仍含3.x/4.x')
        if '∠' in sc or '⊥' in sc:
            c_issues.append('service_content含OCR图形字符')
    
    if c_issues:
        count += 1
        print(f'  {cid} ({ptype}): {len(c_issues)}个残留')

print(f'\n残留问题: {count}/42')
print('✅ 全部通过' if count == 0 else f'需处理: {count}')
db.close()
