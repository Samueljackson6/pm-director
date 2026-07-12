import sqlite3
db = sqlite3.connect('/app/database/project_management.db')
db.row_factory = sqlite3.Row

print('=== contracts 表列名 ===')
for c in db.execute('PRAGMA table_info(contracts)'):
    print(f'{c["name"]:35s} {c["type"]}')

print('\n=== 阶段名为空 ===')
for r in db.execute('SELECT contract_id, stage_number, stage_name FROM stages WHERE stage_name IS NULL OR stage_name=""'):
    print(f'  {r["contract_id"]} #{r["stage_number"]}: (空)')

print('\n=== 阶段名为日期(无业务名) ===')
for r in db.execute('SELECT contract_id, stage_number, stage_name FROM stages WHERE stage_name GLOB "*[0-9][0-9][0-9][0-9]年*" AND LENGTH(stage_name) > 10'):
    print(f'  {r["contract_id"]} #{r["stage_number"]}: {r["stage_name"]}')

print('\n=== 付款截断详情(小于等于10字) ===')
for p in db.execute("SELECT contract_id, payment_id, payment_stage, payment_condition, planned_amount FROM payments WHERE length(payment_stage) <= 10 AND payment_stage != ''"):
    print(f'  {p["contract_id"]} {p["payment_id"]}: stage="{p["payment_stage"]}" cond="{p["payment_condition"][:30]}" plan={p["planned_amount"]}')

print('\n=== 付款stage==condition ===')
for p in db.execute("SELECT contract_id, payment_id, payment_stage, planned_amount FROM payments WHERE payment_stage = payment_condition AND payment_stage != ''"):
    print(f'  {p["contract_id"]} {p["payment_id"]}: "{p["payment_stage"][:50]}" plan={p["planned_amount"]}')

# 全局分类统计：每个合同的阶段质量
print('\n=== 按合同统计阶段污染 ===')
for r in db.execute('SELECT DISTINCT contract_id FROM stages ORDER BY contract_id'):
    cid = r['contract_id']
    total = db.execute('SELECT COUNT(*) FROM stages WHERE contract_id=?', (cid,)).fetchone()[0]
    dup = db.execute('SELECT COUNT(*) FROM (SELECT stage_number, COUNT(*) as c FROM stages WHERE contract_id=? GROUP BY stage_number HAVING c>1)', (cid,)).fetchone()[0]
    rm_in_kh = db.execute('SELECT COUNT(*) FROM stages WHERE contract_id=? AND remarks LIKE "%考核目标%"', (cid,)).fetchone()[0]
    ac_empty = db.execute('SELECT COUNT(*) FROM stages WHERE contract_id=? AND (acceptance_criteria IS NULL OR acceptance_criteria="")', (cid,)).fetchone()[0]
    name_date = db.execute('SELECT COUNT(*) FROM stages WHERE contract_id=? AND stage_name GLOB "*[0-9][0-9][0-9][0-9]年*"', (cid,)).fetchone()[0]
    if dup > 0 or rm_in_kh > 0 or ac_empty > 0 or name_date > 0:
        flags = []
        if dup: flags.append(f'{dup}段重复')
        if rm_in_kh: flags.append(f'{rm_in_kh}/{total}remarks含考核目标')
        if ac_empty: flags.append(f'{ac_empty}/{total}考核目标空')
        if name_date: flags.append(f'{name_date}阶段名为日期')
        print(f'  {cid}: {", ".join(flags)}')

db.close()
