"""Fix ID system: ZH02 = primary key, SGSC = secondary reference"""
import sqlite3, json, os, re

DB = '/home/samuel/.openclaw/workspace/pm-director/database/project_management.db'
CACHE = '/home/samuel/.openclaw/workspace/pm-director/cache/contracts/'

conn = sqlite3.connect(DB)
c = conn.cursor()

# === 1. Current state ===
print("=== CURRENT CONTRACT IDs ===")
rows = c.execute("SELECT contract_id, project_name, contract_amount, project_type FROM contracts ORDER BY contract_id").fetchall()
zh_count = sum(1 for r in rows if r[0].startswith('ZH'))
sg_count = sum(1 for r in rows if r[0].startswith('SGSC'))
other_count = sum(1 for r in rows if not r[0].startswith(('ZH', 'SGSC')))
print(f"ZH02: {zh_count}, SGSC: {sg_count}, Other: {other_count}, Total: {len(rows)}")

print("\nSGSC as primary (should be ZH02):")
for r in rows:
    if r[0].startswith('SGSC'):
        print(f"  {r[0]:30s} ¥{r[2] or 0:>8.2f}万  {str(r[1])[:50]}")

print("\nNon-standard IDs:")
for r in rows:
    if not r[0].startswith(('ZH', 'SGSC')):
        print(f"  {r[0]:30s} ¥{r[2] or 0:>8.2f}万  {str(r[1])[:50]}")

# === 2. Find ZH02 from standard data JSON ===
print("\n=== FINDING ZH02 IDs FROM JSON ===")
json_contracts = {}
for f in os.listdir(CACHE):
    if not f.endswith('-标准数据.json'):
        continue
    try:
        data = json.load(open(os.path.join(CACHE, f)))
        basic = data.get('基本信息', {})
        pid = basic.get('合同编号', '') or basic.get('项目编号', '')
        pname = basic.get('项目名称', '')
        # Extract ZH02 from filename if available
        m = re.search(r'(ZH02-\d{9})', f)
        if m:
            zh_id = m.group(1)
            json_contracts[zh_id] = {
                'name': pname,
                'sgsc': pid if pid.startswith('SGSC') else '',
                'amount': data.get('合同金额', {}).get('含税金额', 0),
                'type': data.get('项目类型', '')
            }
    except:
        pass

print(f"Found {len(json_contracts)} ZH02 contracts in JSON")
for zh_id, info in sorted(json_contracts.items()):
    sgsc_ref = f" SGSC={info['sgsc']}" if info['sgsc'] else ""
    print(f"  {zh_id} -> {info['name'][:40]}{sgsc_ref}")

# === 3. Fix: Ensure ZH02 records exist ===
print("\n=== FIXING CONTRACTS ===")
added = 0
mapped = 0

for zh_id, info in json_contracts.items():
    # Check if ZH02 record exists
    existing = c.execute("SELECT contract_id FROM contracts WHERE contract_id=?", (zh_id,)).fetchone()
    
    if not existing:
        # Need to create or update the record
        # Check if SGSC record exists with similar name/amount
        sgsc_record = None
        if info['sgsc']:
            sgsc_record = c.execute(
                "SELECT * FROM contracts WHERE contract_id=?",
                (info['sgsc'],)
            ).fetchone()
        
        if sgsc_record:
            # Rename SGSC record to ZH02 (keep the data, fix the ID)
            zh_name = info['name'][:100] if info['name'] else sgsc_record[1]
            amt = info['amount'] / 10000 if info['amount'] and info['amount'] > 100 else sgsc_record[3]
            c.execute("UPDATE contracts SET contract_id=? WHERE contract_id=?",
                (zh_id, info['sgsc']))
            
            # Store SGSC in contract_id_mapping
            c.execute("""INSERT OR REPLACE INTO contract_id_mapping
                (project_id_zh, project_id_sgsc, project_name, source)
                VALUES (?, ?, ?, 'id_fix')""",
                (zh_id, info['sgsc'], info['name'] or ''))
            added += 1
        else:
            # Create new ZH02 record
            amt = info['amount'] / 10000 if info['amount'] and info['amount'] > 100 else 0
            c.execute("""INSERT OR REPLACE INTO contracts
                (contract_id, project_name, project_type, contract_amount)
                VALUES (?, ?, ?, ?)""",
                (zh_id, info['name'] or '', info['type'] or '未知', amt))
            added += 1
    
    # Map SGSC reference
    if info['sgsc']:
        c.execute("""INSERT OR IGNORE INTO contract_id_mapping
            (project_id_zh, project_id_sgsc, project_name, source)
            VALUES (?, ?, ?, 'json_mapping')""",
            (zh_id, info['sgsc'], info['name'] or ''))
        mapped += 1

conn.commit()

# === 4. Final state ===
print(f"Added/renamed: {added}, SGSC mapped: {mapped}")

rows = c.execute("SELECT contract_id, project_name FROM contracts ORDER BY contract_id").fetchall()
zh_count = sum(1 for r in rows if r[0].startswith('ZH'))
sg_count = sum(1 for r in rows if r[0].startswith('SGSC'))

print(f"\n=== FINAL STATE ===")
print(f"ZH02: {zh_count}, SGSC: {sg_count}, Total: {len(rows)}")

if sg_count > 0:
    print("Remaining SGSC records:")
    for r in rows:
        if r[0].startswith('SGSC'):
            print(f"  {r[0]} -> {str(r[1])[:50]}")

conn.close()
