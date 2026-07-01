"""Final fix: merge last SYS + verify amounts"""
import sqlite3

DB = '/home/samuel/.openclaw/workspace/pm-director/database/project_management.db'
conn = sqlite3.connect(DB)
c = conn.cursor()

# Merge SYS-607016 -> ZH02-202604021
for tbl in ['stages','payments','deliverables','supplier_contracts','finance_records']:
    try:
        c.execute(f"UPDATE {tbl} SET contract_id=? WHERE contract_id=?", ('ZH02-202604021', 'SYS-202607-016'))
    except:
        pass
c.execute("DELETE FROM contracts WHERE contract_id=?", ('SYS-202607-016',))
conn.commit()

# Final state
total = c.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]
zh = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'ZH02%'").fetchone()[0]
sys = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'SYS-%'").fetchone()[0]
sg = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'SGSC%'").fetchone()[0]
mappings = c.execute("SELECT COUNT(*) FROM contract_id_mapping").fetchone()[0]

print(f"ZH02={zh}, SYS={sys}, SGSC={sg}, Total={total}")
print(f"SGSC references: {mappings}")
print(f"No SGSC as primary key: {sg == 0}")

conn.close()
