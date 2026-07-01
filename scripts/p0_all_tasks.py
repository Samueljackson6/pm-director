#!/usr/bin/env python3
"""P0 Tasks: stage-payment linking, project progress, ID mapping, invoice structuring"""
import sqlite3, re, json
from pathlib import Path

DB = Path('/home/samuel/.openclaw/workspace/pm-director/database/project_management.db')
WORKSPACE = Path('/home/samuel/.openclaw/workspace/pm-director')
conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row
c = conn.cursor()

# ===========================================================
# P0-1: Stage ↔ Payment Linking
# ===========================================================
print("=" * 60)
print("P0-1: Stage-Payment Linking")
print("=" * 60)

# Get contracts with both stages AND payments
c.execute("""
    SELECT DISTINCT s.contract_id FROM stages s
    INNER JOIN payments p ON s.contract_id = p.contract_id
""")
linked_contracts = [r[0] for r in c.fetchall()]
print(f"Contracts with both stages & payments: {len(linked_contracts)}")

# Clear existing
c.execute("DELETE FROM stage_payment_link")
links = 0

for cid in linked_contracts:
    stages = c.execute("SELECT * FROM stages WHERE contract_id=? ORDER BY stage_number", (cid,)).fetchall()
    payments = c.execute("SELECT * FROM payments WHERE contract_id=? ORDER BY payment_id", (cid,)).fetchall()
    
    if not stages or not payments:
        continue

    matched_indices = set()
    
    for s in stages:
        s_num = str(s['stage_number'])
        s_content = (s['acceptance_criteria'] or '') + (s['stage_name'] or '')
        
        for pi, p in enumerate(payments):
            if pi in matched_indices:
                continue
            p_cond = p['payment_condition'] or ''
            
            # Match: payment condition contains stage number
            if s_num in p_cond and s_num != '1':  # '1' too ambiguous
                link_type = 'direct'
            # Match: payment condition text in stage content or vice versa
            elif len(p_cond) > 10 and p_cond[:20] in s_content:
                link_type = 'direct'
            # Match: sequential (1st stage → 1st payment, etc)
            elif len(stages) == len(payments):
                link_type = 'sequential'
                if pi == stages.index(s):  # same position
                    pass
                else:
                    continue
            else:
                continue
            
            confidence = 'high' if link_type != 'sequential' else 'medium'
            c.execute("""INSERT OR IGNORE INTO stage_payment_link
                (project_id, stage_id, payment_id, link_type, confidence, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cid, s['stage_id'], p['payment_id'], link_type, confidence,
                  f"stage_{s_num}_to_payment_{pi+1}"))
            matched_indices.add(pi)
            links += 1

    # Sequential match: if not all matched, link remaining by position
    if len(matched_indices) < min(len(stages), len(payments)):
        for i in range(min(len(stages), len(payments))):
            if i not in matched_indices:
                c.execute("""INSERT OR IGNORE INTO stage_payment_link
                    (project_id, stage_id, payment_id, link_type, confidence, notes)
                    VALUES (?, ?, ?, 'sequential', 'medium', ?)
                """, (cid, stages[i]['stage_id'], payments[i]['payment_id'],
                      f"positional_link_{i+1}"))
                links += 1

conn.commit()
link_count = c.execute("SELECT COUNT(*) FROM stage_payment_link").fetchone()[0]
print(f"Links created: {link_count}")
c.execute("SELECT project_id, COUNT(*) as cnt FROM stage_payment_link GROUP BY project_id").fetchall()
for r in c.fetchall()[-5:]:
    print(f"  {r[0][:30]} -> {r[1]} link(s)")

# ===========================================================
# P0-2: Project Progress Calculation
# ===========================================================
print("\n" + "=" * 60)
print("P0-2: Project Progress Calculation")
print("=" * 60)

c.execute("DELETE FROM project_status")

c.execute("""
    INSERT OR REPLACE INTO project_status (contract_id, overall_progress, payment_progress,
        deliverable_progress, stage_progress, status, risk_level, last_updated)
    SELECT 
        c.contract_id,
        ROUND((COALESCE(s_prog, 0) + COALESCE(p_prog, 0) + COALESCE(d_prog, 0)) / 
              (CASE WHEN s_prog IS NULL THEN 0 ELSE 1 END + 
               CASE WHEN p_prog IS NULL THEN 0 ELSE 1 END + 
               CASE WHEN d_prog IS NULL THEN 0 ELSE 1 END), 1) as overall,
        COALESCE(p_prog, 0) as payment_progress,
        COALESCE(d_prog, 0) as deliverable_progress,
        COALESCE(s_prog, 0) as stage_progress,
        CASE WHEN COALESCE(s_prog, 0) >= 100 AND COALESCE(p_prog, 0) >= 100 THEN 'completed' ELSE 'active' END,
        CASE 
            WHEN COALESCE(s_prog, 0) < 25 AND COALESCE(p_prog, 0) < 25 THEN 'high'
            WHEN COALESCE(s_prog, 0) < 50 OR COALESCE(p_prog, 0) < 50 THEN 'medium'
            ELSE 'low'
        END,
        CURRENT_TIMESTAMP
    FROM contracts c
    LEFT JOIN (
        SELECT contract_id,
            COUNT(DISTINCT CASE WHEN status='completed' THEN stage_id END) * 100.0 / NULLIF(COUNT(DISTINCT stage_id), 0) as s_prog
        FROM stages GROUP BY contract_id
    ) s ON c.contract_id = s.contract_id
    LEFT JOIN (
        SELECT contract_id,
            SUM(actual_amount) * 100.0 / NULLIF(SUM(planned_amount), 0) as p_prog
        FROM payments WHERE planned_amount > 0 GROUP BY contract_id
    ) p ON c.contract_id = p.contract_id
    LEFT JOIN (
        SELECT contract_id,
            COUNT(DISTINCT CASE WHEN status='completed' THEN deliverable_id END) * 100.0 / NULLIF(COUNT(DISTINCT deliverable_id), 0) as d_prog
        FROM deliverables GROUP BY contract_id
    ) d ON c.contract_id = d.contract_id
""")

conn.commit()

# Stats
c.execute("SELECT COUNT(*) FROM project_status WHERE overall_progress > 0")
active_ct = c.fetchone()[0]
c.execute("SELECT AVG(overall_progress) FROM project_status WHERE overall_progress > 0")
avg_prog = c.fetchone()[0] or 0
c.execute("SELECT status, COUNT(*) FROM project_status GROUP BY status")
status_dist = c.fetchall()

print(f"Contracts with progress: {active_ct}")
print(f"Average progress: {avg_prog:.1f}%")
for s in status_dist:
    print(f"  {s[0]}: {s[1]}")

# Also add API endpoint to backend/main.py
backend_file = WORKSPACE / 'backend' / 'main.py'
with open(backend_file) as f:
    backend_code = f.read()

new_endpoint = """
@app.get('/api/projects/progress')
def get_project_progress():
    db = get_db()
    rows = db.execute('''
        SELECT c.project_name, c.contract_id, c.contract_amount, c.project_type,
               ps.overall_progress, ps.stage_progress, ps.payment_progress,
               ps.deliverable_progress, ps.status, ps.risk_level
        FROM project_status ps
        JOIN contracts c ON ps.contract_id = c.contract_id
        ORDER BY ps.overall_progress DESC
    ''').fetchall()
    db.close()
    stats = {
        'total': len(rows),
        'avg_progress': round(sum(r['overall_progress'] or 0 for r in rows) / max(1, len(rows)), 1),
        'completed': sum(1 for r in rows if r['status'] == 'completed'),
        'active': sum(1 for r in rows if r['status'] == 'active'),
    }
    return {'items': [dict(r) for r in rows], 'stats': stats}
"""

if "get_project_progress" not in backend_code:
    # Insert before the last line
    with open(backend_file, 'w') as f:
        f.write(backend_code.rstrip() + '\n' + new_endpoint + '\n')
    print("API endpoint /api/projects/progress added to backend/main.py")
else:
    print("API endpoint /api/projects/progress already exists")

# ===========================================================
# P0-3: ID Mapping Completion
# ===========================================================
print("\n" + "=" * 60)
print("P0-3: ID Mapping")
print("=" * 60)

old_count = c.execute("SELECT COUNT(*) FROM contract_id_mapping").fetchone()[0]
print(f"Current mappings: {old_count}")

# Method 1: Match by identical contract_amount + similar project_name
c.execute("""
    SELECT z.contract_id as zh_id, s.contract_id as sgsc_id,
           z.project_name, z.contract_amount
    FROM contracts z
    JOIN contracts s ON ABS(z.contract_amount - s.contract_amount) < 0.01
        AND z.contract_amount > 0
    WHERE z.contract_id LIKE 'ZH02%' AND s.contract_id LIKE 'SGSC%'
        AND z.contract_id != s.contract_id
""")
for r in c.fetchall():
    c.execute("""INSERT OR IGNORE INTO contract_id_mapping
        (project_id_zh, project_id_sgsc, project_name, source)
        VALUES (?, ?, ?, 'amount_match')""",
        (r['zh_id'], r['sgsc_id'], r['project_name']))

# Method 2: Get financial_id from master_table
c.execute("""
    SELECT 项目编号, 财务编号 FROM master_table WHERE 财务编号 IS NOT NULL AND 财务编号 != ''
""")
for r in c.fetchall():
    pid = r[0]
    fid = r[1]
    # Find matching contract
    c.execute("SELECT contract_id FROM contracts WHERE contract_id=?", (pid,))
    contract = c.fetchone()
    if contract:
        c.execute("""UPDATE contract_id_mapping SET financial_id=?
            WHERE project_id_zh=? OR project_id_sgsc=?""",
            (fid, pid, pid))

conn.commit()

new_count = c.execute("SELECT COUNT(*) FROM contract_id_mapping").fetchone()[0]
added = new_count - old_count
print(f"New mappings: +{added} (total: {new_count})")

# Show unmapped
c.execute("""SELECT contract_id, project_name FROM contracts
    WHERE contract_id NOT IN (SELECT project_id_zh FROM contract_id_mapping WHERE project_id_zh IS NOT NULL)
    AND contract_id NOT IN (SELECT project_id_sgsc FROM contract_id_mapping WHERE project_id_sgsc IS NOT NULL)
    AND contract_amount > 0 LIMIT 5""")
unmapped = c.fetchall()
if unmapped:
    print("Still unmapped:")
    for r in unmapped:
        print(f"  {r[0][:30]} {str(r[1])[:40]}")

# ===========================================================
# P0-4: Invoice Structuring
# ===========================================================
print("\n" + "=" * 60)
print("P0-4: Invoice Structuring")
print("=" * 60)

# Add columns if not exist
try:
    c.execute("ALTER TABLE invoices ADD COLUMN invoice_no TEXT")
    print("Added: invoice_no")
except: pass
try:
    c.execute("ALTER TABLE invoices ADD COLUMN tax_rate REAL DEFAULT 6.0")
    print("Added: tax_rate")
except: pass
try:
    c.execute("ALTER TABLE invoices ADD COLUMN tax_amount REAL")
    print("Added: tax_amount")
except: pass
try:
    c.execute("ALTER TABLE invoices ADD COLUMN verification_status TEXT DEFAULT 'unverified'")
    print("Added: verification_status")
except: pass

# Populate tax_rate from master_table
tax_map = {}
for r in c.execute("SELECT 项目编号, 税率 FROM master_table WHERE 税率 IS NOT NULL").fetchall():
    tax_map[r[0]] = r[1]

# Update per project
updated_tax = 0
for r in c.execute("SELECT DISTINCT project_id FROM invoices WHERE project_id IS NOT NULL").fetchall():
    pid = r[0]
    tr = tax_map.get(pid, 6.0)  # default 6%
    c.execute("UPDATE invoices SET tax_rate=?, tax_amount=ROUND(amount * ? / (100 + ?), 2) WHERE project_id=?",
        (tr, tr, tr, pid))
    updated_tax += 1

# Mark verified where invoice amounts match finance_records totals
c.execute("""
    UPDATE invoices SET verification_status = 'verified'
    WHERE project_id IN (
        SELECT project_id FROM finance_records
        WHERE ABS(invoice_total * 10000 - 
            (SELECT SUM(amount) FROM invoices i2 WHERE i2.project_id = finance_records.project_id AND i2.invoice_type='客户开票'))
            < 100
    )
""")

# Stats
inv_tax = c.execute("SELECT COUNT(*) FROM invoices WHERE tax_rate IS NOT NULL").fetchone()[0]
inv_verified = c.execute("SELECT COUNT(*) FROM invoices WHERE verification_status='verified'").fetchone()[0]
print(f"Invoices with tax_rate: {inv_tax}/71")
print(f"Invoices verified: {inv_verified}/71")

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("ALL P0 TASKS COMPLETE")
print("=" * 60)
