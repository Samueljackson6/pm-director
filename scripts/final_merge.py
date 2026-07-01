"""Final merge: use contract_id_mapping to resolve remaining SYS records"""
import sqlite3

DB = '/home/samuel/.openclaw/workspace/pm-director/database/project_management.db'
conn = sqlite3.connect(DB)
c = conn.cursor()

# Find SYS records that have SGSC→ZH02 mapping
c.execute("""
    SELECT s.contract_id as sys_id, cim.project_id_zh as zh_id, s.project_name
    FROM contracts s
    JOIN contract_id_mapping cim ON s.contract_id = cim.project_id_sgsc
    WHERE s.contract_id LIKE 'SYS-%'
""")
mapped = c.fetchall()
print(f"SYS with SGSC mapping: {len(mapped)}")

for sys_id, zh_id, name in mapped:
    # Check if ZH02 already exists in contracts
    exists = c.execute("SELECT 1 FROM contracts WHERE contract_id=?", (zh_id,)).fetchone()
    if exists:
        print(f"  DELETE {sys_id} (dup of {zh_id})")
        for tbl in ['stages','payments','deliverables','supplier_contracts','finance_records']:
            try: c.execute(f"UPDATE {tbl} SET contract_id=? WHERE contract_id=?", (zh_id, sys_id))
            except: pass
        c.execute("DELETE FROM contracts WHERE contract_id=?", (sys_id,))
    else:
        print(f"  RENAME {sys_id} -> {zh_id}")
        c.execute("UPDATE contracts SET contract_id=? WHERE contract_id=?", (zh_id, sys_id))

conn.commit()

# Final stats
total = c.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]
zh = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'ZH02%'").fetchone()[0]
sys = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'SYS-%'").fetchone()[0]
print(f"\nZH02: {zh}, SYS: {sys}, Total: {total}")

if sys:
    print("\nRemaining SYS (no ZH02 found):")
    for r in c.execute("SELECT contract_id, project_name FROM contracts WHERE contract_id LIKE 'SYS-%'").fetchall():
        print(f"  {r[0]} {r[1][:50]}")

mappings = c.execute("SELECT COUNT(*) FROM contract_id_mapping").fetchone()[0]
print(f"\ncontract_id_mapping: {mappings} entries")
conn.close()
