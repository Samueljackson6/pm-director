import sqlite3, re
db = sqlite3.connect('/app/database/project_management.db')
cur = db.cursor()
fixed = 0

# 1. rm==ac完全相同 → 清空rm
for s in db.execute("SELECT stage_id, remarks, acceptance_criteria FROM stages WHERE remarks=acceptance_criteria AND remarks != '' AND LENGTH(remarks)>20").fetchall():
    cur.execute('UPDATE stages SET remarks="" WHERE stage_id=?', (s[0],))
    fixed += 1

# 2. rm尾部的残片清理
for s in db.execute("SELECT stage_id, remarks FROM stages WHERE remarks LIKE '%;%'").fetchall():
    rm = s[1]
    cleaned = re.sub(r'[;；]\s*[\(\（][^\)\）]{0,20}$', '', rm).strip()
    if cleaned != rm:
        cur.execute('UPDATE stages SET remarks=? WHERE stage_id=?', (cleaned, s[0]))
        fixed += 1

# 3. 短remarks恢复
for s in db.execute('SELECT stage_id, remarks, acceptance_criteria FROM stages').fetchall():
    sid = s[0]
    rm = (s[1] or '').strip()
    ac = (s[2] or '').strip()
    if rm and len(rm) < 20 and ac and len(ac) > len(rm):
        new_rm = re.sub(r'^[\(\（]?\d+[\)\）\.]?\s*', '', ac)
        if new_rm != rm:
            cur.execute('UPDATE stages SET remarks=? WHERE stage_id=?', (new_rm, sid))
            fixed += 1

db.commit()
print(f'微调: {fixed}')

db.row_factory = sqlite3.Row
for cid in ['ZH02-202604026','ZH02-202509025','ZH02-202604020']:
    print(f'\n=== {cid} ===')
    for s in db.execute('SELECT stage_number,remarks,acceptance_criteria FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall():
        rm = (s['remarks'] or '').strip()
        ac = (s['acceptance_criteria'] or '').strip()
        ok_rm = 'OK' if rm and len(rm)>10 else 'X'
        ok_ac = 'OK' if ac and len(ac)>10 else 'X'
        print(f'  阶段{s["stage_number"]}: rm={ok_rm}({len(rm)}字) ac={ok_ac}({len(ac)}字)')
        if rm: print(f'    rm: {rm[:80]}')
        if ac: print(f'    ac: {ac[:80]}')
db.close()
