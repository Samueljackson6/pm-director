import sqlite3, re
db = sqlite3.connect('/app/database/project_management.db')
cur = db.cursor()

n = cur.execute("UPDATE stages SET remarks='' WHERE remarks=acceptance_criteria AND remarks!='' AND LENGTH(remarks)>15").rowcount

for s in cur.execute("SELECT stage_id,remarks FROM stages WHERE remarks LIKE '%;%'").fetchall():
    rm = s[1]
    cleaned = re.sub(r'[;；]\s*[\(\（]\d*[\)\）]\s*$', '', rm).strip()
    if cleaned != rm:
        cur.execute('UPDATE stages SET remarks=? WHERE stage_id=?', (cleaned, s[0]))
        n += 1

db.commit()
print(f'修复: {n}')

db.row_factory = sqlite3.Row
for cid in ['ZH02-202604026','ZH02-202509025','ZH02-202604020']:
    print(f'\n{cid}:')
    for s in db.execute('SELECT stage_number,remarks,acceptance_criteria FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall():
        rm = (s['remarks'] or '').strip()
        ac = (s['acceptance_criteria'] or '').strip()
        dup = ' DUP' if rm and ac and rm==ac else ''
        info = f' rm={rm[:50]}' if rm else ' rm=空'
        print(f'  #{s["stage_number"]} rm={len(rm)} ac={len(ac)}{dup}{info}')
db.close()
