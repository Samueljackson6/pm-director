"""Properly fix ID system: ZH02=primary, SGSC=external reference only"""
import sqlite3, json, os, re

DB = '/home/samuel/.openclaw/workspace/pm-director/database/project_management.db'
CACHE = '/home/samuel/.openclaw/workspace/pm-director/cache/contracts/'

conn = sqlite3.connect(DB)
c = conn.cursor()

# === 1. Find duplicate pairs (same name+amount, one ZH02, one SGSC) ===
print("=== FINDING DUPLICATE PAIRS ===")
pairs = []
rows = c.execute("""
    SELECT z.contract_id as zh_id, s.contract_id as sg_id,
           z.project_name, z.contract_amount, z.project_type
    FROM contracts z
    JOIN contracts s ON ABS(z.contract_amount - s.contract_amount) < 0.5
        AND z.contract_amount > 0
    WHERE z.contract_id LIKE 'ZH02%' AND s.contract_id LIKE 'SGSC%'
        AND z.contract_id != s.contract_id
""").fetchall()

for r in pairs:
    print(f"  {r['zh_id']} ↔ {r['sg_id']}  ¥{r['contract_amount']:.2f}万  {str(r['project_name'])[:40]}")

# === 2. Merge: keep ZH02, move SGSC to mapping, delete SGSC record ===
print("\n=== MERGING ===")
merged = 0
for r in pairs:
    zh_id = r['zh_id']
    sg_id = r['sg_id']
    
    # Store SGSC reference
    c.execute("""INSERT OR REPLACE INTO contract_id_mapping
        (project_id_zh, project_id_sgsc, project_name, source)
        VALUES (?, ?, ?, 'id_merge')""",
        (zh_id, sg_id, r['project_name']))
    
    # Update any foreign references from SGSC to ZH02
    for tbl in ['stages', 'payments', 'deliverables', 'supplier_contracts']:
        c.execute(f"UPDATE {tbl} SET contract_id=? WHERE contract_id=?", (zh_id, sg_id))
    
    # Update finance_records
    c.execute("UPDATE finance_records SET project_id=? WHERE project_id=?", (zh_id, sg_id))
    
    # Delete the SGSC duplicate
    c.execute("DELETE FROM contracts WHERE contract_id=?", (sg_id,))
    merged += 1

# === 3. Handle remaining SGSC-only records (no ZH02 match found) ===
print(f"\nMerged: {merged}")

# Check what SGSC records remain
c.execute("SELECT contract_id, project_name FROM contracts WHERE contract_id LIKE 'SGSC%'")
remaining = c.fetchall()
if remaining:
    print(f"\n=== REMAINING SGSC ({len(remaining)}) ===")
    for r in remaining:
        print(f"  {r[0]:30s} {str(r[1])[:50]}")
    
    # Try to find their ZH02 from JSON
    print("\n=== MATCHING FROM JSON ===")
    for sg_r in remaining:
        sg_id = sg_r[0]
        sg_name = (sg_r[1] or '').strip()[:30]
        
        for f in os.listdir(CACHE):
            if not f.endswith('.json'):
                continue
            try:
                data = json.load(open(os.path.join(CACHE, f)))
                basic = data.get('基本信息', {})
                j_name = (basic.get('项目名称', '') or '').strip()
                
                # Find ZH02 from filename
                m = re.search(r'(ZH02-\d{9})', f)
                if not m:
                    continue
                zh_id = m.group(1)
                
                # Check if names match
                if sg_name[:15] in j_name or j_name[:15] in sg_name:
                    # Found matching ZH02
                    print(f"  {sg_id} → {zh_id} (via {f[:50]})")
                    
                    # Rename contract from SGSC to ZH02
                    c.execute("UPDATE contracts SET contract_id=? WHERE contract_id=?", (zh_id, sg_id))
                    
                    # Store SGSC reference
                    c.execute("""INSERT OR REPLACE INTO contract_id_mapping
                        (project_id_zh, project_id_sgsc, project_name, source)
                        VALUES (?, ?, ?, 'json_match')""",
                        (zh_id, sg_id, j_name))
                    merged += 1
                    break
            except:
                pass

# === 4. Final cleanup: ensure no SGSC as primary ===
# For any still remaining, generate system ID
c.execute("SELECT contract_id, project_name FROM contracts WHERE contract_id LIKE 'SGSC%'")
still_sg = c.fetchall()

if still_sg:
    print(f"\n=== STILL SGSC ({len(still_sg)}) ===")
    for r in still_sg:
        # Generate system ID: SYS-YYYYMM-XXX
        from datetime import datetime
        seq = c.execute("SELECT COUNT(*) FROM contracts WHERE contract_id LIKE 'SYS-%'").fetchone()[0]
        sys_id = f"SYS-{datetime.now().strftime('%Y%m')}-{seq+1:03d}"
        
        # Store old SGSC reference
        c.execute("""INSERT OR REPLACE INTO contract_id_mapping
            (project_id_zh, project_id_sgsc, project_name, source)
            VALUES (?, ?, ?, 'system_id')""",
            (sys_id, r[0], r[1]))
        
        # Rename
        c.execute("UPDATE contracts SET contract_id=? WHERE contract_id=?", (sys_id, r[0]))
        print(f"  {r[0]} → {sys_id}  {str(r[1])[:50]}")
        merged += 1

conn.commit()

# === 5. Final state ===
print(f"\n=== FINAL ===")
rows = c.execute("SELECT contract_id, project_name, contract_amount FROM contracts ORDER BY contract_id").fetchall()
zh = [r for r in rows if r[0].startswith('ZH02')]
sg = [r for r in rows if r[0].startswith('SGSC')]
sys = [r for r in rows if r[0].startswith('SYS-')]
print(f"ZH02: {len(zh)}, SGSC: {len(sg)}, SYS: {len(sys)}, Total: {len(rows)}")

if sg:
    print("WARNING: SGSC still as primary:")
    for r in sg:
        print(f"  {r[0]}")
else:
    print("✅ No SGSC as primary key")

mappings = c.execute("SELECT COUNT(*) FROM contract_id_mapping").fetchone()[0]
print(f"contract_id_mapping: {mappings} entries")

conn.close()
