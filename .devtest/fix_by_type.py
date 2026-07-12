"""
按合同类型分治修复:
  1. 科研类: 阶段名标准化(研究阶段5.1-5.6, 从1开始) + 阶段#0清理
  2. 技术服务类: service_content分字段拆分(只留1.2, 1.3→method, 2.x→各字段)
  3. 付款文本修复: 5.15.3→5.1~5.3, 补全截断文本
"""
import sqlite3, re

DB = '/app/database/project_management.db'
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

stats = {'stage_names': 0, 'service_split': 0, 'fields_added': 0, 'payment_fix': 0}

# ============================================================
# PART 1: 科研类 - 阶段名标准化
# ============================================================
print('=== PART 1: 科研类阶段名标准化 ===')

# 1a. 修复stage_number: 确保从0开始连续（合同签订之日=0, 研究阶段=1..N）
for r in db.execute('''
    SELECT c.contract_id FROM contracts c WHERE c.project_type='科研类'
''').fetchall():
    cid = r['contract_id']
    stages = db.execute('SELECT stage_id, stage_number, stage_name FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall()
    
    # 找出哪个是合同签订之日
    sign_day_idx = None
    research_stages = []
    for s in stages:
        if '合同签订之日' in (s['stage_name'] or ''):
            sign_day_idx = s
        else:
            research_stages.append(s)
    
    # 重新编号: sign_day=0, research=1,2,3...N
    new_num = 1
    for rs in research_stages:
        # 生成标准化阶段名
        new_name = f'研究阶段5.{new_num}'
        
        # 特殊处理: stage_number从1开始
        cur.execute('UPDATE stages SET stage_name=?, stage_number=? WHERE stage_id=?',
                   (new_name, new_num, rs['stage_id']))
        stats['stage_names'] += 1
        new_num += 1
    
    # 合同签订之日固定为#0
    if sign_day_idx and sign_day_idx['stage_number'] != 0:
        cur.execute('UPDATE stages SET stage_number=0 WHERE stage_id=?', (sign_day_idx['stage_id'],))
        stats['stage_names'] += 1

# 1b. 清理阶段#0的remarks（去掉冗余的"主要内容："前缀和OCR碎片）
for r in db.execute('''
    SELECT s.stage_id, s.remarks FROM stages s JOIN contracts c ON s.contract_id=c.contract_id
    WHERE s.stage_number=0 AND c.project_type='科研类'
''').fetchall():
    rm = r['remarks'] or ''
    # 清理
    cleaned = re.sub(r'合同签订之日[—\-–]\s*\d{4}年\d{1,2}月\d{1,2}日\s*主要内容[：:]\s*', '', rm)
    cleaned = cleaned.strip()
    if cleaned != rm:
        cur.execute('UPDATE stages SET remarks=? WHERE stage_id=?', (cleaned, r['stage_id']))
        stats['stage_names'] += 1

print(f'  阶段名标准化: {stats["stage_names"]}')

# ============================================================
# PART 2: 技术服务类 - service_content分字段拆分
# ============================================================
print('\n=== PART 2: 技术服务类service_content分字段 ===')

# 2a. 确认contracts表是否有service_schedule和service_quality列
existing_cols = [c[1] for c in db.execute('PRAGMA table_info(contracts)').fetchall()]
for col in ['service_schedule', 'service_quality']:
    if col not in existing_cols:
        cur.execute(f'ALTER TABLE contracts ADD COLUMN {col} TEXT')
        stats['fields_added'] += 1
        print(f'  新增列: {col}')

# 2b. 拆分service_content
for r in db.execute("SELECT * FROM contracts WHERE project_type='服务类' OR project_type IS NULL ORDER BY contract_id").fetchall():
    cid = r['contract_id']
    sc = (r['service_content'] or '').strip()
    if not sc:
        continue
    
    # 提取各节内容
    sections = {}
    
    # 1.2 技术服务的内容
    m = re.search(r'1\.2\s*技术服务的内容[：:]\s*(.*?)(?=1\.3|2\.|$)', sc, re.DOTALL)
    if m:
        sections['service_content'] = m.group(1).strip()
        # 清理尾部OCR垃圾
        sections['service_content'] = re.sub(r'\s*\d+\.\d+\s*$', '', sections['service_content'])
    
    # 1.3 技术服务的方式
    m = re.search(r'1\.3\s*技术服务的方式[：:]\s*(.*?)(?=2\.|3\.|$)', sc, re.DOTALL)
    if m:
        val = m.group(1).strip().rstrip('_。.，, ')
        if val and not re.match(r'^[_' ']*$', val):
            sections['service_method'] = val
    
    # 2.1 技术服务地点
    m = re.search(r'2\.1\s*技术服务地点[：:]\s*(.*?)(?=2\.2|2\.3|2\.4|3\.|$)', sc, re.DOTALL)
    if m:
        val = m.group(1).strip().rstrip('_。.，, ')
        if val and not re.match(r'^[_' ']*$', val):
            sections['service_location'] = val
    
    # 2.2 技术服务期限
    m = re.search(r'2\.2\s*技术服务期限[：:]\s*(.*?)(?=2\.3|2\.4|3\.|$)', sc, re.DOTALL)
    if m:
        val = m.group(1).strip().rstrip('_。.，, ')
        if val and not re.match(r'^[_' ']*$', val):
            sections['service_period'] = val
    
    # 2.3 技术服务进度 (新字段)
    m = re.search(r'2\.3\s*技术服务进度[：:]\s*(.*?)(?=2\.4|3\.|$)', sc, re.DOTALL)
    if m:
        val = m.group(1).strip().rstrip('_。.，, ')
        if val and not re.match(r'^[_' ']*$', val):
            sections['service_schedule'] = val
    
    # 2.4 技术服务质量要求 (新字段)
    m = re.search(r'2\.4\s*技术服务质量要求[：:]\s*(.*?)(?=3\.|4\.|$)', sc, re.DOTALL)
    if m:
        val = m.group(1).strip().rstrip('_。.，, ')
        if val and not re.match(r'^[_' ']*$', val):
            sections['service_quality'] = val
    
    # 更新数据库
    if 'service_content' in sections:
        updates = sections.copy()
        # 清理已提取字段中的OCR碎片
        for k in updates:
            v = updates[k]
            # 移除SGTYHT模板号
            v = re.sub(r'SGTYHT\s*/\s*\d+\s*[—\-]\s*JS\s*[—\-]\s*\d+', '', v)
            # 移除SGSCD编号
            v = re.sub(r'SGSCD\w{15,}', '', v)
            # 移除阶段标识 (如 "5.2考核目标")
            v = re.sub(r'\d+\.\d+考核目标[：:].*$', '', v, flags=re.DOTALL)
            # 清理空白
            v = re.sub(r'\s{2,}', ' ', v).strip()
            updates[k] = v
        
        set_parts = []
        values = []
        for k, v in updates.items():
            set_parts.append(f'{k}=?')
            values.append(v)
        values.append(cid)
        
        set_str = ", ".join(set_parts)
        cur.execute(f'UPDATE contracts SET {set_str} WHERE contract_id=?', values)
        stats['service_split'] += 1
        print(f'  {cid}: 拆分出 {list(updates.keys())}')

print(f'  服务内容拆分: {stats["service_split"]} 合同')

# ============================================================
# PART 3: 付款文本修复
# ============================================================
print('\n=== PART 3: 付款文本修复 ===')

for p in db.execute('SELECT * FROM payments WHERE payment_stage != \"\" OR payment_condition != \"\"').fetchall():
    pid = p['payment_id']
    updates = {}
    
    for field in ['payment_stage', 'payment_condition']:
        val = p[field] or ''
        if not val:
            continue
        
        cleaned = val
        # 修复 "5.15.3" → "5.1、5.3"
        cleaned = re.sub(r'(\d+\.\d+)\.?(\d+\.\d+)', r'\1、\2', cleaned)
        # 修复 "5.45.6" → "5.4、5.6"
        cleaned = re.sub(r'(\d+)(\.\d+)', r'\1\2', cleaned)
        cleaned = re.sub(r'(5\.1)(5\.3)', r'\1、\2', cleaned)
        cleaned = re.sub(r'(5\.4)(5\.6)', r'\1、\2', cleaned)
        # 修复 "成果经 2026年" → "成果经甲方验收合格后，2026年..."
        cleaned = re.sub(r'成果经\s*\d{4}年', '成果经甲方验收合格且甲方收到乙方开具的等额增值税专用发票后支付', cleaned)
        cleaned = re.sub(r'成果经\s*$', '成果经甲方验收合格后支付', cleaned)
        # 清理多余空格
        cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()
        
        if cleaned != val:
            updates[field] = cleaned
    
    if updates:
        set_parts = []
        values = []
        for k, v in updates.items():
            set_parts.append(f'{k}=?')
            values.append(v)
        values.append(pid)
        set_str = ", ".join(set_parts)
        cur.execute(f'UPDATE payments SET {set_str} WHERE payment_id=?', values)
        stats['payment_fix'] += 1

print(f'  付款修复: {stats["payment_fix"]} 条')

# ============================================================
# PART 4: 验证
# ============================================================
db.commit()

print('\n=== 验证 ===')
# 科研类阶段名
print('--- 科研类阶段名抽样 ---')
for cid in ['ZH02-202604020', 'ZH02-202604026', 'ZH02-202509025']:
    stages = db.execute('SELECT stage_number, stage_name FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall()
    names = [f'#{s["stage_number"]}[{s["stage_name"][:15]}]' for s in stages]
    arrow = " → "
    print(f'  {cid}: {arrow.join(names)}')

# 技术服务类服务字段
print('\n--- 技术服务类服务字段抽样 ---')
for cid in ['ZH02-202508013', 'ZH02-202508019']:
    c = db.execute('SELECT service_content, service_method, service_location, service_period, service_schedule, service_quality FROM contracts WHERE contract_id=?', (cid,)).fetchone()
    if c:
        sc = (c['service_content'] or '')[:80]
        sc_len = len(c['service_content'] or '')
        sm = c['service_method'] or '-'
        sq = c['service_quality'] or '-'
        ss = c['service_schedule'] or '-'
        print(f'  {cid}:')
        print(f'    content({sc_len}字): {sc}')
        print(f'    method: {sm}')
        print(f'    schedule: {ss[:60]}')
        print(f'    quality: {sq[:60]}')

# 付款
print('\n--- 付款修复抽样 ---')
for p in db.execute('SELECT * FROM payments WHERE contract_id="ZH02-202604020" ORDER BY payment_id').fetchall():
    pid = p['payment_id']
    ps = p['payment_stage'] or ''
    print(f'  {pid}: stage({len(ps)}字)={ps[:80]}')

db.close()
print('\n✅ 分治修复完成')
