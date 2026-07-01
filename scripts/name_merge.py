"""Fix remaining 8 SYS: match by name to existing ZH02, or keep as SYS if truly unique"""
import sqlite3
from difflib import SequenceMatcher

DB = '/home/samuel/.openclaw/workspace/pm-director/database/project_management.db'
conn = sqlite3.connect(DB)
c = conn.cursor()

# Get SYS records and their names
sys_records = c.execute("""
    SELECT contract_id, project_name, contract_amount FROM contracts
    WHERE contract_id LIKE 'SYS-%'
""").fetchall()

# Get all ZH02 records for matching
zh_records = c.execute("""
    SELECT contract_id, project_name, contract_amount FROM contracts
    WHERE contract_id LIKE 'ZH02%'
""").fetchall()

merged = 0
unmatched = []

for sys_id, sys_name, sys_amt in sys_records:
    best_match = None
    best_score = 0.0
    
    for zh_id, zh_name, zh_amt in zh_records:
        if not sys_name or not zh_name:
            continue
        # Name similarity
        name_sim = SequenceMatcher(None, sys_name.strip()[:30], zh_name.strip()[:30]).ratio()
        
        # Amount similarity (if both have amounts)
        if sys_amt and zh_amt and sys_amt > 0 and zh_amt > 0:
            amt_sim = 1 - min(abs(sys_amt - zh_amt) / max(sys_amt, zh_amt), 1)
        else:
            amt_sim = 0
        
        score = name_sim * 0.7 + amt_sim * 0.3
        
        if score > best_score:
            best_score = score
            best_match = zh_id
    
    if best_match and best_score > 0.4:
        print(f"  MERGE {sys_id} -> {best_match} (score={best_score:.2f}) {str(sys_name)[:50]}")
        for tbl in ['stages','payments','deliverables','supplier_contracts','finance_records']:
            try: c.execute(f"UPDATE {tbl} SET contract_id=? WHERE contract_id=?", (best_match, sys_id))
            except: pass
        c.execute("DELETE FROM contracts WHERE contract_id=?", (sys_id,))
        merged += 1
    else:
        unmatched.append((sys_id, sys_name, best_score, best_match))
        print(f"  KEEP {sys_id} (no ZH02 match, best={best_match} score={best_score:.2f})")

conn.commit()

# Final state
total = c.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]
zh = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'ZH02%'").fetchone()[0]
sys = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'SYS-%'").fetchone()[0]
sg = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'SGSC%'").fetchone()[0]

print(f"\n=== FINAL STATE ===")
print(f"ZH02: {zh}, SYS: {sys}, SGSC: {sg}, Total: {total}")
print(f"Merged: {merged}, Unmatched: {len(unmatched)}")

if unmatched:
    print("\nUnmatched SYS (kept — no ZH02 counterpart):")
    for r in unmatched:
        print(f"  {r[0]} {str(r[1])[:60]}")

mappings = c.execute("SELECT COUNT(*) FROM contract_id_mapping").fetchone()[0]
print(f"\ncontract_id_mapping: {mappings} entries (SGSC references)")

conn.close()
