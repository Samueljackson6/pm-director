"""
科研类阶段修正: #0合并入#1, 编号从1开始 + 全字段深度审计
"""
import sqlite3, re

DB = '/app/database/project_management.db'
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

# ============================================================
# PART 1: 科研类 - 合并#0到#1, 重编号
# ============================================================
print('=== PART 1: 科研类阶段合并 ===')
fixed_contracts = 0

for cid_row in db.execute('SELECT DISTINCT contract_id FROM contracts WHERE project_type="科研类"').fetchall():
    cid = cid_row['contract_id']
    
    # 找到#0和#1
    s0 = db.execute('SELECT * FROM stages WHERE contract_id=? AND stage_number=0', (cid,)).fetchone()
    if not s0:
        continue
    
    all_stages = db.execute('SELECT * FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall()
    
    # 找到#1 (目前是研究阶段5.1)
    s1_candidates = [s for s in all_stages if s['stage_number'] == 1]
    if not s1_candidates:
        # 没有#1, 把#0重命名为研究阶段5.1
        cur.execute('UPDATE stages SET stage_name="研究阶段5.1", stage_number=1 WHERE stage_id=?', (s0['stage_id'],))
        fixed_contracts += 1
        continue
    
    s1 = s1_candidates[0]
    
    # 合并: #1的start变成#0的start (合同签订之日)
    new_start = s0['start_time']
    new_end = s1['end_time']
    
    # 合并remarks
    rm0 = (s0['remarks'] or '').strip()
    rm1 = (s1['remarks'] or '').strip()
    if rm0 and rm0 not in rm1:
        new_rm = rm0 + '; ' + rm1
    else:
        new_rm = rm1 or rm0
    
    # 合并ac (取更完整的)
    ac0 = (s0['acceptance_criteria'] or '').strip()
    ac1 = (s1['acceptance_criteria'] or '').strip()
    new_ac = ac1 if ac1 else ac0
    
    # 更新#1
    cur.execute('''UPDATE stages SET 
        stage_name="研究阶段5.1", start_time=?, end_time=?, remarks=?, acceptance_criteria=?
        WHERE stage_id=?''',
        (new_start, new_end, new_rm, new_ac, s1['stage_id']))
    
    # 删除#0
    cur.execute('DELETE FROM stages WHERE stage_id=?', (s0['stage_id'],))
    
    # 重编号: #2→#2, #3→#3... (保持不变, 因为#0已删除,#1已更新)
    # 实际上原来#2的stage_number就是2, 不需要改
    # 但有些合同可能有gap, 需要重新连续编号
    
    # 重新连续编号
    remaining = db.execute('SELECT stage_id FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall()
    for i, rs in enumerate(remaining):
        cur.execute('UPDATE stages SET stage_number=? WHERE stage_id=?', (i + 1, rs['stage_id']))
    
    fixed_contracts += 1
    print(f'  {cid}: #0合并→阶段1, 共{len(remaining)}阶段')

db.commit()
print(f'合并: {fixed_contracts} 合同')

# ============================================================
# PART 2: 深度审计 - 所有文本字段的截断和无关内容
# ============================================================
print('\n=== PART 2: 全字段深度审计 ===')
issues_found = 0

for c_row in db.execute('SELECT * FROM contracts ORDER BY contract_id').fetchall():
    cid = c_row['contract_id']
    ptype = c_row['project_type'] or '未分类'
    c_issues = []
    
    # A. 阶段字段深度检查
    for s in db.execute('SELECT * FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall():
        sn = s['stage_number']
        
        # 检查remarks是否有截断迹象: 末尾是不完整句子
        for field in ['remarks', 'acceptance_criteria']:
            val = (s[field] or '').strip()
            if not val:
                continue
            # 尾部截断: 以 "请" "的" "和" "与" "及" "或" "第" "经" 结尾且>20字
            if len(val) > 20 and re.search(r'[的和与及或经向到以第]$', val):
                c_issues.append(f'阶段{sn} {field}疑似截断({len(val)}字)')
            # 含OCR页码标识
            if re.search(r'\[第\d|第\d+页\]', val):
                c_issues.append(f'阶段{sn} {field}含页码')
            # 含模板编号
            if re.search(r'SGTYHT|SGSCD.{5,}|合同编号[：:]', val):
                c_issues.append(f'阶段{sn} {field}含模板编号')
            # 含预算表内容(非阶段内容)
            if re.search(r'科目名称|预算金额|人工费.*业务费|万元.*万元', val):
                c_issues.append(f'阶段{sn} {field}混入预算表')
            # 内容重复(remarks和ac相同)
        
        # 检查remarks和ac内容高度相似 (>80%)
        rm = (s['remarks'] or '').strip()
        ac = (s['acceptance_criteria'] or '').strip()
        if rm and ac and len(rm) > 10 and len(ac) > 10:
            # 简单相似度
            common = len(set(rm) & set(ac))
            shorter = min(len(rm), len(ac))
            if shorter > 0 and common / shorter > 0.8:
                c_issues.append(f'阶段{sn} remarks/ac高度重复')
    
    # B. 付款字段深度检查
    for p in db.execute('SELECT * FROM payments WHERE contract_id=?', (cid,)).fetchall():
        pid = p['payment_id']
        for field in ['payment_stage', 'payment_condition']:
            val = (p[field] or '').strip()
            if not val:
                continue
            # 含纯数字/金额格式（是表格内容而非付款条件）
            if re.match(r'^\d+\.?\d*$', val):
                c_issues.append(f'{pid} {field}为纯数字({val})')
            # 含"费（万元）"表格头
            if '费（万元）' in val or '收款单位' in val:
                c_issues.append(f'{pid} {field}含表格头')
            # 尾部截断: 以日期结尾但句子不完整
            if len(val) > 15 and re.search(r'合同签订|收到|开具|支付$', val) and re.search(r'\d{4}年$', val):
                c_issues.append(f'{pid} {field}尾部截断({val[-20:]})')
    
    # C. 服务字段检查 (技术服务类)
    if ptype == '服务类':
        for field in ['service_content', 'service_quality', 'service_schedule']:
            val = (c_row[field] if field in c_row.keys() else '') or ''
            if not val:
                continue
            # 含非本字段内容
            if field == 'service_content':
                if '3.甲方提供' in val or '组织与管理' in val or '4.1' in val:
                    c_issues.append(f'service_content仍含3.x/4.x节')
                if 'SGTYHT' in val or '合同编号' in val:
                    c_issues.append(f'service_content含模板编号')
            # 含"_"下划线OCR垃圾
            if re.search(r'_{2,}|∠|⊥', val):
                c_issues.append(f'{field}含OCR图形字符(∠⊥_)')
    
    if c_issues:
        issues_found += 1
        print(f'  {cid} ({ptype}): {len(c_issues)}个问题')
        for i in c_issues:
            print(f'    - {i}')

print(f'\n有问题合同: {issues_found}/42')

db.commit()
db.close()
print('✅ 修正完成')
