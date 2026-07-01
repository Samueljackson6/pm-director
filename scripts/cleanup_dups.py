"""Clean up: delete SYS duplicates that already have ZH02 counterparts"""
import sqlite3

DB = '/home/samuel/.openclaw/workspace/pm-director/database/project_management.db'
conn = sqlite3.connect(DB)
c = conn.cursor()

# Find SYS records with matching ZH02 (same project_name)
c.execute("""
    SELECT s.contract_id as sys_id, z.contract_id as zh_id,
           s.project_name, s.contract_amount
    FROM contracts s
    JOIN contracts z ON z.project_name = s.project_name
    WHERE s.contract_id LIKE 'SYS-%'
      AND z.contract_id LIKE 'ZH02%'
""")
dups = c.fetchall()
print(f"SYS duplicates of ZH02: {len(dups)}")

deleted = 0
for d in dups:
    sys_id, zh_id = d[0], d[1]
    print(f"  DELETE SYS {sys_id} -> already exists as ZH02 {zh_id} ({str(d[2])[:40]})")
    
    # Merge any linked data from SYS to ZH02 (if ZH02 doesn't have it)
    for tbl in ['stages', 'payments', 'deliverables', 'supplier_contracts', 'finance_records', 'project_status']:
        try:
            c.execute(f"UPDATE {tbl} SET contract_id=? WHERE contract_id=?", (zh_id, sys_id))
        except:
            pass
    
    try:
        c.execute("DELETE FROM contract_type_attributes WHERE contract_id=?", (sys_id,))
    except:
        pass
    c.execute("DELETE FROM contracts WHERE contract_id=?", (sys_id,))
    deleted += 1

# Also find SYS records that match by amount + name similarity
c.execute("""
    SELECT s.contract_id as sys_id, s.project_name as s_name,
           z.contract_id as zh_id, z.project_name as z_name
    FROM contracts s
    JOIN contracts z ON ABS(s.contract_amount - z.contract_amount) < 0.5
    WHERE s.contract_id LIKE 'SYS-%' AND z.contract_id LIKE 'ZH02%'
      AND s.contract_amount > 0
""")
similars = c.fetchall()
for d in similars:
    if d[1] and d[3]:
        import difflib
        sim = difflib.SequenceMatcher(None, (d[1] or '')[:30], (d[3] or '')[:30]).ratio()
        if sim > 0.3 and sim < 1.0:
            print(f"  SIMILAR (score={sim:.2f}): SYS {d[0]} → ZH02 {d[2]} ({str(d[1])[:40]})")
            # Only merge if confidence high enough
            if sim > 0.6:
                for tbl in ['stages', 'payments', 'deliverables', 'supplier_contracts', 'finance_records']:
                    try:
                        c.execute(f"UPDATE {tbl} SET contract_id=? WHERE contract_id=?", (d[2], d[0]))
                    except:
                        pass
                c.execute("DELETE FROM contracts WHERE contract_id=?", (d[0],))
                deleted += 1

conn.commit()

# Final state
total = c.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]
zh = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'ZH02%'").fetchone()[0]
sys = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'SYS-%'").fetchone()[0]
sg = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'SGSC%'").fetchone()[0]

print(f"\nFINAL: ZH02={zh}, SYS={sys}, SGSC={sg}, Total={total}")
print(f"Deleted: {deleted}")

if sys > 0:
    print("\nRemaining SYS contracts:")
    for r in c.execute("SELECT contract_id, project_name FROM contracts WHERE contract_id LIKE 'SYS-%'").fetchall():
        print(f"  {r[0]} -> {str(r[1])[:60]}")
else:
    print("No SYS contracts remaining")

conn.close()
