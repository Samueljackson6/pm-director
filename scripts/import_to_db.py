#!/usr/bin/env python3
"""
标准数据JSON → SQLite 导入器
将 cache/contracts/*-标准数据.json 的数据导入到 project_management.db

用法:
  python3 scripts/import_to_db.py                    # 导入所有(增量)
  python3 scripts/import_to_db.py --dry-run          # 试运行(不写入)
  python3 scripts/import_to_db.py --force            # 强制覆盖已有
  python3 scripts/import_to_db.py --status           # 查看导入状态
"""

import json, os, sys, sqlite3
from pathlib import Path
from datetime import datetime

WORKSPACE = Path('/home/samuel/.openclaw/workspace/pm-director')
CACHE_DIR = WORKSPACE / 'cache' / 'contracts'
DB_PATH = WORKSPACE / 'database' / 'project_management.db'

conn = None

def get_db():
    global conn
    if conn is None:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
    return conn

def get_contract_id(data):
    """从JSON中提取合同编号"""
    basic = data.get('基本信息', {})
    return basic.get('合同编号', '') or basic.get('项目编号', '')

def upsert_contract(data):
    """导入/更新合同基本信息"""
    basic = data.get('基本信息', {})
    amount = data.get('合同金额', {})
    pid = get_contract_id(data)
    if not pid:
        return False

    db = get_db()
    existing = db.execute('SELECT contract_id FROM contracts WHERE contract_id=?', (pid,)).fetchone()

    if existing and '--force' not in sys.argv:
        return False  # 已存在，跳过

    db.execute('''
        INSERT OR REPLACE INTO contracts 
        (contract_id, project_name, project_type, contract_amount, 
         party_a, party_b, sign_date, expiry_date, 
         service_content, service_period,
         created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ''', (
        pid,
        basic.get('项目名称', ''),
        data.get('项目类型', ''),
        (amount.get('含税金额', 0) or 0) / 10000,  # 元 → 万元
        basic.get('甲方', ''),
        basic.get('乙方', ''),
        basic.get('签订日期'),
        basic.get('有效期限'),
        data.get('服务信息', {}).get('服务内容', '') or '',
        data.get('服务信息', {}).get('服务期限', '') or '',
    ))
    return True

def upsert_stages(pid, data):
    """导入研究阶段"""
    stages = data.get('研究阶段', [])
    if not stages:
        return 0
    db = get_db()
    count = 0
    for s in stages:
        stage_num = s.get('阶段编号', str(count + 1))
        stage_id = f'{pid}-S{stage_num}'
        # old format may have list for 考核目标
        assess = s.get('考核目标', '') or s.get('主要内容', '')
        if isinstance(assess, list):
            assess = '; '.join(str(x) for x in assess)
        content = s.get('主要内容', '')
        if isinstance(content, list):
            content = '; '.join(str(x) for x in content)
        db.execute('''
            INSERT OR IGNORE INTO stages
            (stage_id, contract_id, stage_name, stage_number,
             start_time, end_time, acceptance_criteria, status)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (
            stage_id, pid,
            content[:100],
            int(stage_num.split('.')[0]) if stage_num.isdigit() or ('.' in stage_num and stage_num.split('.')[0].isdigit()) else count + 1,
            s.get('时间范围', ''),
            '',
            assess[:500],
            'pending'
        ))
        count += 1
    return count

def upsert_payments(pid, data):
    """导入付款计划"""
    payments = data.get('付款计划', [])
    if not payments:
        return 0
    db = get_db()
    count = 0
    for p in payments:
        pay_id = f'{pid}-P{p.get("付款节点", count + 1)}'
        amt = p.get('金额', 0) or p.get('付款金额', 0) or 0
        if amt > 1000:
            amt = amt / 10000  # 元 → 万元
        db.execute('''
            INSERT OR IGNORE INTO payments
            (payment_id, contract_id, payment_stage, planned_amount,
             payment_condition, status)
            VALUES (?,?,?,?,?,?)
        ''', (
            pay_id, pid,
            p.get('付款条件', '')[:50],
            amt,
            p.get('付款条件', ''),
            'pending'
        ))
        count += 1
    return count

def upsert_deliverables(pid, data):
    """导入交付物"""
    deliverables = data.get('交付物', [])
    if not deliverables:
        return 0
    db = get_db()
    count = 0
    for d in deliverables:
        del_id = f'{pid}-D{count + 1}'
        db.execute('''
            INSERT OR IGNORE INTO deliverables
            (deliverable_id, contract_id, deliverable_name, deliverable_type, quantity, status)
            VALUES (?,?,?,?,?,?)
        ''', (
            del_id, pid,
            d.get('名称', ''),
            d.get('类型', '成果'),
            d.get('数量', 1),
            'pending'
        ))
        count += 1
    return count

def import_all(dry_run=False):
    """导入所有标准数据文件"""
    files = sorted(CACHE_DIR.glob('*标准数据.json'))
    print(f'标准数据文件: {len(files)} 个\n')

    stats = {'contracts': 0, 'stages': 0, 'payments': 0, 'deliverables': 0, 'skipped': 0, 'errors': 0}

    for f in files:
        try:
            data = json.load(open(f))
            pid = get_contract_id(data)
            if not pid:
                print(f'  ⚠️  {f.name}: 无合同编号')
                stats['errors'] += 1
                continue

            if dry_run:
                s = len(data.get('研究阶段', []))
                p = len(data.get('付款计划', []))
                d = len(data.get('交付物', []))
                print(f'  📄 {pid:30s} | S{s} P{p} D{d} | {data.get("项目类型",""):6s} | ¥{data.get("合同金额",{}).get("含税金额","?"):>10}')
                stats['contracts'] += 1
                stats['stages'] += s
                stats['payments'] += p
                stats['deliverables'] += d
            else:
                if upsert_contract(data):
                    stats['contracts'] += 1
                else:
                    stats['skipped'] += 1
                sc = upsert_stages(pid, data)
                pc = upsert_payments(pid, data)
                dc = upsert_deliverables(pid, data)
                stats['stages'] += sc
                stats['payments'] += pc
                stats['deliverables'] += dc
                if sc or pc or dc:
                    print(f'  ✅ {pid:30s} | +S{sc} +P{pc} +D{dc}')

        except Exception as e:
            print(f'  ❌ {f.name}: {e}')
            stats['errors'] += 1

    if not dry_run:
        get_db().commit()

    print(f'\n统计: contracts={stats["contracts"]}(+{stats["skipped"]}已存在) stages={stats["stages"]} payments={stats["payments"]} deliverables={stats["deliverables"]} errors={stats["errors"]}')

def show_status():
    """显示导入状态"""
    db = get_db()
    files = sorted(CACHE_DIR.glob('*标准数据.json'))

    c_count = db.execute('SELECT COUNT(*) FROM contracts').fetchone()[0]
    s_count = db.execute('SELECT COUNT(*) FROM stages').fetchone()[0]
    p_count = db.execute('SELECT COUNT(*) FROM payments').fetchone()[0]
    d_count = db.execute('SELECT COUNT(*) FROM deliverables').fetchone()[0]

    print(f'DB: contracts={c_count} stages={s_count} payments={p_count} deliverables={d_count}')
    print(f'JSON: {len(files)} 个标准数据文件\n')

    # Compare
    for f in files:
        try:
            data = json.load(open(f))
            pid = get_contract_id(data)
            if not pid:
                continue
            in_db = db.execute('SELECT contract_id FROM contracts WHERE contract_id=?', (pid,)).fetchone()
            j_stages = len(data.get('研究阶段', []))
            d_stages = db.execute('SELECT COUNT(*) FROM stages WHERE contract_id=?', (pid,)).fetchone()[0]
            j_pays = len(data.get('付款计划', []))
            d_pays = db.execute('SELECT COUNT(*) FROM payments WHERE contract_id=?', (pid,)).fetchone()[0]

            db_status = '✅' if in_db else '❌'
            stage_ok = '✅' if d_stages >= j_stages else f'⚠️ {d_stages}/{j_stages}'
            pay_ok = '✅' if d_pays >= j_pays else f'⚠️ {d_pays}/{j_pays}'

            print(f'{db_status} {pid:30s} | DB=Y S={stage_ok:10s} P={pay_ok:10s} | JSON_S={j_stages} JSON_P={j_pays}')
        except:
            pass

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        import_all(dry_run=True)
    elif len(sys.argv) > 1 and sys.argv[1] == '--status':
        show_status()
    else:
        import_all()
