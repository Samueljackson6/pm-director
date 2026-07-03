"""
标准数据JSON -> SQLite 导入器 (v2 - 智能ID映射版)
- 利用 contract_id_mapping 表将 SGSC ID 转为 ZH02 ID
- 数据增强：对已入库合同补充 stage/payment/deliverable 数据

用法:
  python scripts/_do_import.py           # 执行导入
  python scripts/_do_import.py --dry-run # 试运行
  python scripts/_do_import.py --status  # 查看状态
"""
import json, sys, sqlite3
from pathlib import Path

BASE = Path(__file__).parent.parent
CACHE_DIR = BASE / 'cache' / 'contracts'
DB_PATH = BASE / 'database' / 'project_management.db'
conn = None

def get_db():
    global conn
    if conn is None:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
    return conn

def load_id_mapping():
    """加载SGSC->ZH02映射，只保留以ZH02-开头的有效映射"""
    db = get_db()
    mapping = {}
    rows = db.execute('SELECT project_id_sgsc, project_id_zh FROM contract_id_mapping WHERE project_id_sgsc IS NOT NULL').fetchall()
    for r in rows:
        sgsc = r['project_id_sgsc'].strip()
        zh = r['project_id_zh']
        if zh and zh.strip().startswith('ZH02-'):
            mapping[sgsc] = zh.strip()
    return mapping

def resolve_id(raw_id, id_map):
    """仅在映射到有效ZH02 ID时使用映射，否则保持原ID"""
    mapped = id_map.get(raw_id)
    if mapped:
        return mapped
    return raw_id

def upsert_contract(data, pid):
    db = get_db()
    existing = db.execute('SELECT contract_id FROM contracts WHERE contract_id=?', (pid,)).fetchone()
    if existing:
        return False, 'EXISTS'
    basic = data.get('\u57fa\u672c\u4fe1\u606f', {})
    amount = data.get('\u5408\u540c\u91d1\u989d', {})
    amt = (amount.get('\u542b\u7a0e\u91d1\u989d', 0) or 0)
    amt_wan = amt / 10000 if amt > 1000 else amt
    db.execute('''
        INSERT OR REPLACE INTO contracts 
        (contract_id, project_name, project_type, contract_amount,
         party_a, party_b, sign_date, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ''', (
        pid,
        basic.get('\u9879\u76ee\u540d\u79f0', '') or '',
        data.get('\u9879\u76ee\u7c7b\u578b', '') or '',
        round(amt_wan, 4),
        basic.get('\u7532\u65b9', '') or '',
        basic.get('\u4e59\u65b9', '') or '',
        basic.get('\u7b7e\u8ba2\u65e5\u671f', None),
    ))
    return True, 'INSERTED'

def upsert_stages(pid, data):
    stages = data.get('\u7814\u7a76\u9636\u6bb5', [])
    if not stages or not isinstance(stages, list):
        return 0
    db = get_db()
    count = 0
    for s in stages:
        stage_num = s.get('\u9636\u6bb5\u7f16\u53f7', str(count + 1))
        stage_id = f'{pid}-S{stage_num}'
        existing = db.execute('SELECT stage_id FROM stages WHERE stage_id=?', (stage_id,)).fetchone()
        if existing:
            count += 1
            continue
        assess = s.get('\u8003\u6838\u76ee\u6807', '') or ''
        if isinstance(assess, list):
            assess = '; '.join(str(x) for x in assess)
        content = s.get('\u4e3b\u8981\u5185\u5bb9', '') or ''
        if isinstance(content, list):
            content = '; '.join(str(x) for x in content)
        try:
            db.execute('''
                INSERT INTO stages (stage_id, contract_id, stage_name, stage_number, start_time, acceptance_criteria, status)
                VALUES (?,?,?,?,?,?,?)
            ''', (stage_id, pid, content[:200], count + 1,
                  s.get('\u65f6\u95f4\u8303\u56f4', '') or '',
                  assess[:500], 'pending'))
            count += 1
        except Exception as e:
            pass
    return count

def upsert_payments(pid, data):
    payments = data.get('\u4ed8\u6b3e\u8ba1\u5212', [])
    if not payments or not isinstance(payments, list):
        return 0
    db = get_db()
    count = 0
    for p in payments:
        pay_id = f'{pid}-P{count + 1}'
        existing = db.execute('SELECT payment_id FROM payments WHERE payment_id=?', (pay_id,)).fetchone()
        if existing:
            count += 1
            continue
        amt = p.get('\u91d1\u989d', 0) or p.get('\u4ed8\u6b3e\u91d1\u989d', 0) or 0
        amt_wan = amt / 10000 if amt > 1000 else amt
        condition = p.get('\u4ed8\u6b3e\u6761\u4ef6', '') or ''
        try:
            db.execute('''
                INSERT INTO payments (payment_id, contract_id, payment_stage, planned_amount, payment_condition, status)
                VALUES (?,?,?,?,?,?)
            ''', (pay_id, pid, condition[:50], round(amt_wan, 4), condition, 'pending'))
            count += 1
        except:
            pass
    return count

def upsert_deliverables(pid, data):
    deliverables = data.get('\u4ea4\u4ed8\u7269', [])
    if not deliverables or not isinstance(deliverables, list):
        return 0
    db = get_db()
    count = 0
    for d in deliverables:
        del_id = f'{pid}-D{count + 1}'
        existing = db.execute('SELECT deliverable_id FROM deliverables WHERE deliverable_id=?', (del_id,)).fetchone()
        if existing:
            count += 1
            continue
        try:
            db.execute('''
                INSERT INTO deliverables (deliverable_id, contract_id, deliverable_name, deliverable_type, quantity, status)
                VALUES (?,?,?,?,?,?)
            ''', (del_id, pid,
                  d.get('\u540d\u79f0', '') or '',
                  d.get('\u7c7b\u578b', '\u6210\u679c') or '',
                  d.get('\u6570\u91cf', 1) or 1,
                  'pending'))
            count += 1
        except:
            pass
    return count

def import_all(dry_run=False):
    id_map = load_id_mapping()
    files = sorted(CACHE_DIR.glob('*\u6807\u51c6\u6570\u636e*.json'))
    print(f'Standard data files: {len(files)}')
    print(f'SGSC->ZH02 mappings loaded: {len(id_map)}\n')
    stats = {'inserted': 0, 'skipped': 0, 'stages': 0, 'payments': 0, 'deliverables': 0, 'errors': 0}

    for f in files:
        try:
            data = json.load(open(f, 'r', encoding='utf-8'))
            basic = data.get('\u57fa\u672c\u4fe1\u606f', {})
            raw_id = basic.get('\u5408\u540c\u7f16\u53f7', '') or basic.get('\u9879\u76ee\u7f16\u53f7', '') or ''
            if not raw_id:
                print(f'  SKIP {f.name}: no contract ID')
                stats['errors'] += 1
                continue
            pid = resolve_id(raw_id, id_map)
            mapped = ' [mapped]' if pid != raw_id else ''
            stages = data.get('\u7814\u7a76\u9636\u6bb5', [])
            payments = data.get('\u4ed8\u6b3e\u8ba1\u5212', [])
            deliverables = data.get('\u4ea4\u4ed8\u7269', [])
            s = len(stages) if isinstance(stages, list) else 0
            p = len(payments) if isinstance(payments, list) else 0
            d = len(deliverables) if isinstance(deliverables, list) else 0

            if dry_run:
                print(f'  {pid:30s}{mapped} | S:{s} P:{p} D:{d}')
                stats['stages'] += s
                stats['payments'] += p
                stats['deliverables'] += d
            else:
                ins, reason = upsert_contract(data, pid)
                if ins:
                    stats['inserted'] += 1
                else:
                    stats['skipped'] += 1
                sc = upsert_stages(pid, data)
                pc = upsert_payments(pid, data)
                dc = upsert_deliverables(pid, data)
                stats['stages'] += sc
                stats['payments'] += pc
                stats['deliverables'] += dc
                if ins:
                    print(f'  + {pid:30s}{mapped} | +S:{sc} +P:{pc} +D:{dc}')
                elif sc or pc or dc:
                    print(f'  ~ {pid:30s}{mapped} | +S:{sc} +P:{pc} +D:{dc}')
        except Exception as e:
            import traceback
            print(f'  ERR {f.name}: {e}')
            traceback.print_exc()
            stats['errors'] += 1

    if not dry_run:
        get_db().commit()
    print(f'\nResults: +contracts={stats["inserted"]} skipped={stats["skipped"]} +stages={stats["stages"]} +payments={stats["payments"]} +deliverables={stats["deliverables"]} errors={stats["errors"]}')

def show_status():
    db = get_db()
    files = sorted(CACHE_DIR.glob('*\u6807\u51c6\u6570\u636e*.json'))
    id_map = load_id_mapping()
    c_count = db.execute('SELECT COUNT(*) FROM contracts').fetchone()[0]
    s_count = db.execute('SELECT COUNT(*) FROM stages').fetchone()[0]
    p_count = db.execute('SELECT COUNT(*) FROM payments').fetchone()[0]
    d_count = db.execute('SELECT COUNT(*) FROM deliverables').fetchone()[0]
    print(f'DB: contracts={c_count} stages={s_count} payments={p_count} deliverables={d_count}')
    print(f'JSON: {len(files)} files, {len(id_map)} mappings\n')

    for f in files:
        try:
            data = json.load(open(f, 'r', encoding='utf-8'))
            basic = data.get('\u57fa\u672c\u4fe1\u606f', {})
            raw_id = basic.get('\u5408\u540c\u7f16\u53f7', '') or basic.get('\u9879\u76ee\u7f16\u53f7', '') or ''
            if not raw_id:
                continue
            pid = resolve_id(raw_id, id_map)
            in_db = db.execute('SELECT contract_id FROM contracts WHERE contract_id=?', (pid,)).fetchone()
            stages = data.get('\u7814\u7a76\u9636\u6bb5', [])
            payments = data.get('\u4ed8\u6b3e\u8ba1\u5212', [])
            deliverables = data.get('\u4ea4\u4ed8\u7269', [])
            j_s = len(stages) if isinstance(stages, list) else 0
            j_p = len(payments) if isinstance(payments, list) else 0
            j_d = len(deliverables) if isinstance(deliverables, list) else 0
            if in_db:
                d_s = db.execute('SELECT COUNT(*) FROM stages WHERE contract_id=?', (pid,)).fetchone()[0]
                d_p = db.execute('SELECT COUNT(*) FROM payments WHERE contract_id=?', (pid,)).fetchone()[0]
                d_d = db.execute('SELECT COUNT(*) FROM deliverables WHERE contract_id=?', (pid,)).fetchone()[0]
                s_ok = 'OK' if d_s >= j_s else f'{d_s}/{j_s}'
                p_ok = 'OK' if d_p >= j_p else f'{d_p}/{j_p}'
                d_ok = 'OK' if d_d >= j_d else f'{d_d}/{j_d}'
                print(f'  Y {pid:30s} | S:{s_ok} P:{p_ok} D:{d_ok}')
            else:
                print(f'  N {pid:30s} | S:{j_s} P:{j_p} D:{j_d}')
        except:
            pass

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        import_all(dry_run=True)
    elif len(sys.argv) > 1 and sys.argv[1] == '--status':
        show_status()
    else:
        import_all()
