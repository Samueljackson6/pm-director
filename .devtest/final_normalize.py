import sqlite3, re

db = sqlite3.connect('/app/database/project_management.db')
db.row_factory = sqlite3.Row
cur = db.cursor()
total = 0

# 全局文本归一化
for table in ['stages', 'payments', 'contracts']:
    text_cols = [c[1] for c in db.execute(f'PRAGMA table_info({table})').fetchall() 
                 if c[2] in ('TEXT', '')]
    for col in text_cols:
        rows = db.execute(f'SELECT rowid as rid, [{col}] FROM {table} WHERE [{col}] IS NOT NULL AND [{col}] != ""').fetchall()
        for r in rows:
            val = r[col]
            new_val = val
            # em-dash "第—" → "第一"
            new_val = re.sub(r'第—', '第一', new_val)
            # 中文之间多余空格
            new_val = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', new_val)
            # 标点前多余空格
            new_val = re.sub(r'\s+([，,。\.、；;：:])', r'\1', new_val)
            if new_val != val:
                cur.execute(f'UPDATE {table} SET [{col}]=? WHERE rowid=?', (new_val, r['rid']))
                total += 1

# 阶段名去"完成"前缀
for s in db.execute("SELECT stage_id, stage_name FROM stages WHERE stage_name LIKE '完成%' OR stage_name LIKE '开展%'"):
    new_name = re.sub(r'^(完成|开展)\s*', '', s['stage_name']).strip()
    if new_name != s['stage_name']:
        cur.execute('UPDATE stages SET stage_name=? WHERE stage_id=?', (new_name, s['stage_id']))
        total += 1

db.commit()

# 最终抽查
for cid in ['ZH02-202604026', 'ZH02-202604020']:
    print(f'=== {cid} 最终 ===')
    for s in db.execute('SELECT stage_number, stage_name, remarks, acceptance_criteria FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)):
        nm = (s['stage_name'] or '')[:35]
        rm = (s['remarks'] or '')[:60]
        ac = (s['acceptance_criteria'] or '')[:80]
        print(f'  #{s["stage_number"]}: [{nm}]')
        print(f'    主: {rm}')
        print(f'    考: {ac}')

print(f'\n总修复项: {total}')
db.close()
