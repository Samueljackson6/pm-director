"""Fix P0-3 (ID mapping) and P0-2 (progress demo)"""
import sqlite3, re
from pathlib import Path
from difflib import SequenceMatcher

DB = Path('/home/samuel/.openclaw/workspace/pm-director/database/project_management.db')
conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row
c = conn.cursor()

# ============================================================
# P0-3: Complete ID Mapping
# ============================================================
print("=" * 60)
print("P0-3: Complete ID Mapping")
print("=" * 60)

old_count = c.execute("SELECT COUNT(*) FROM contract_id_mapping").fetchone()[0]

# Strategy 1: Fuzzy name matching (first 20 chars) with ±10% amount
zh02_contracts = c.execute("""
    SELECT contract_id, project_name, contract_amount FROM contracts
    WHERE contract_id LIKE 'ZH02%' AND contract_amount > 0
""").fetchall()

sgsc_contracts = c.execute("""
    SELECT contract_id, project_name, contract_amount FROM contracts
    WHERE contract_id LIKE 'SGSC%' AND contract_amount > 0
""").fetchall()

added = 0
for zh in zh02_contracts:
    zh_name = (zh['project_name'] or '').strip()[:20]
    zh_amt = zh['contract_amount']
    
    best_sgsc = None
    best_score = 0.0
    
    for sg in sgsc_contracts:
        sg_name = (sg['project_name'] or '').strip()[:20]
        sg_amt = sg['contract_amount']
        
        # Name similarity
        name_sim = SequenceMatcher(None, zh_name, sg_name).ratio()
        
        # Amount similarity (within 5%)
        if zh_amt > 0 and sg_amt > 0:
            amt_ratio = min(zh_amt, sg_amt) / max(zh_amt, sg_amt)
            if amt_ratio < 0.95:  # more than 5% diff
                continue
        else:
            amt_ratio = 1.0
        
        score = name_sim * 0.6 + amt_ratio * 0.4
        if score > best_score and name_sim > 0.3:
            best_score = score
            best_sgsc = sg
    
    if best_sgsc and best_score > 0.5:
        c.execute("""INSERT OR IGNORE INTO contract_id_mapping
            (project_id_zh, project_id_sgsc, project_name, source)
            VALUES (?, ?, ?, 'fuzzy_match')""",
            (zh['contract_id'], best_sgsc['contract_id'], zh['project_name']))
        added += 1
        print(f"  {zh['contract_id'][:25]} ↔ {best_sgsc['contract_id'][:25]} (score:{best_score:.2f})")

# Strategy 2: Find financial_ids from master_table
c.execute("""
    SELECT 项目编号, 财务编号 FROM master_table WHERE 财务编号 IS NOT NULL
""")
for r in c.fetchall():
    pid = r[0]
    fid = r[1]
    if not fid:
        continue
    # Try to match to any contract
    c.execute("""SELECT contract_id FROM contracts WHERE (contract_id=? OR contract_id LIKE ?)""",
        (pid, f'%{pid[:10]}%'))
    matched = c.fetchone()
    if matched:
        c.execute("""UPDATE contract_id_mapping SET financial_id=?
            WHERE project_id_zh=? OR project_id_sgsc=?""",
            (fid, matched[0], matched[0]))

# Strategy 3: Direct financial_id from contracts
c.execute("""
    SELECT contract_id, financial_id FROM contracts WHERE financial_id IS NOT NULL AND financial_id != ''
""")
for r in c.fetchall():
    c.execute("""INSERT OR IGNORE INTO contract_id_mapping
        (project_id_zh, project_id_sgsc, financial_id, project_name, source)
        VALUES (?, ?, ?, (SELECT project_name FROM contracts WHERE contract_id=?), 'financial_id')""",
        (r[0], None, r[1], r[0]))

conn.commit()

new_count = c.execute("SELECT COUNT(*) FROM contract_id_mapping").fetchone()[0]
print(f"\n  Result: {old_count} → {new_count} (+{new_count - old_count})")

# ============================================================
# P0-2: Demo Progress
# ============================================================
print("\n" + "=" * 60)
print("P0-2: Seed Sample Progress Data")
print("=" * 60)

# Find contracts with BOTH stages and payments
c.execute("""
    SELECT DISTINCT s.contract_id, c.project_name
    FROM stages s
    INNER JOIN payments p ON s.contract_id = p.contract_id
    JOIN contracts c ON s.contract_id = c.contract_id
    WHERE c.contract_amount > 0
""")
eligible = c.fetchall()

if not eligible:
    print("  No contracts with both stages and payments - can only mark payments")
    # Fallback: just update random payments
    c.execute("UPDATE payments SET actual_amount = planned_amount * 0.5, status = 'completed' WHERE contract_id IN (SELECT contract_id FROM contracts ORDER BY contract_amount DESC LIMIT 5) AND planned_amount > 0")
    c.execute("SELECT COUNT(*) FROM payments WHERE status='completed'")
    print(f"  Marked {c.fetchone()[0]} payments as completed")

for r in eligible[:6]:  # first 6 contracts
    cid = r['contract_id']
    print(f"\n  {r['project_name'][:50]} ({cid})")
    
    # Mark first 2 stages as completed
    stages = c.execute("SELECT stage_id FROM stages WHERE contract_id=? ORDER BY stage_number LIMIT 2", (cid,)).fetchall()
    for s in stages:
        c.execute("UPDATE stages SET status='completed' WHERE stage_id=?", (s['stage_id'],))
        print(f"    Stage {s['stage_id'][:30]} → completed")
    
    # Mark first 1-2 payments with partial actual_amount
    payments = c.execute("SELECT payment_id, planned_amount FROM payments WHERE contract_id=? ORDER BY payment_id LIMIT 2", (cid,)).fetchall()
    for i, p in enumerate(payments):
        actual = p['planned_amount'] * (0.8 if i == 0 else 0.4)
        c.execute("UPDATE payments SET actual_amount=?, status='completed' WHERE payment_id=?",
            (actual, p['payment_id']))
        print(f"    Payment {p['payment_id'][:30]} actual=¥{actual:.2f}")

    # Mark 1 deliverable as completed
    c.execute("SELECT deliverable_id FROM deliverables WHERE contract_id=? LIMIT 1", (cid,))
    d = c.fetchone()
    if d:
        c.execute("UPDATE deliverables SET status='completed' WHERE deliverable_id=?", (d['deliverable_id'],))
        print(f"    Deliverable {d['deliverable_id'][:30]} → completed")

conn.commit()

# Now recalculate progress
print("\n  Recalculating progress...")
c.execute("DELETE FROM project_status")  # Clear and recalc

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

# Show results
c.execute("""
    SELECT c.project_name, ps.overall_progress, ps.stage_progress, ps.payment_progress, ps.risk_level
    FROM project_status ps
    JOIN contracts c ON ps.contract_id = c.contract_id
    WHERE ps.overall_progress > 0
    ORDER BY ps.overall_progress DESC
""")
rows = c.fetchall()
print(f"\n  Contracts with progress > 0%: {len(rows)}")
for r in rows[:10]:
    print(f"  {r['overall_progress']:5.1f}% stage={r['stage_progress']:5.1f}% pay={r['payment_progress']:5.1f}% risk={r['risk_level']:6s} | {str(r['project_name'])[:45]}")

conn.close()
