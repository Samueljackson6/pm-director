#!/usr/bin/env python3
"""全量 42 合同逐项扫描：阶段重复/付款重复/交付物/KPI正确性"""
import sqlite3, json, urllib.request

conn = sqlite3.connect(r'D:\Tare-workspace\pm-director\database\project_management.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute('SELECT contract_id, project_name, contract_amount FROM contracts ORDER BY contract_amount DESC')
contracts = [(r[0], r[1], r[2]) for r in c.fetchall()]

print(f'全量扫描 {len(contracts)} 个合同')
print('='*100)

issues = []
for cid, name, amt in contracts:
    problems = []

    # API验证
    try:
        resp = urllib.request.urlopen(f'http://localhost:18080/api/contracts/{cid}', timeout=10)
        d = json.loads(resp.read())['data']
    except:
        problems.append('API不可达')
        issues.append((cid, name, amt, problems))
        continue

    c = d.get('contract', {})
    stages = d.get('stages', [])
    payments = d.get('payments', [])
    deliverables = d.get('deliverables', [])
    clauses = d.get('clauses', [])
    finance = d.get('finance')

    # 1. 基本字段检查
    if not c.get('service_content') or len(c.get('service_content',''))<5:
        problems.append('服务内容异常')
    if not c.get('party_b'):
        problems.append('无乙方')
    if not c.get('tax_rate'):
        problems.append('无税率')
    if not c.get('sign_date'):
        problems.append('无签订日期')
    if amt and amt < 0.01:
        problems.append('金额为0')

    # 2. 阶段重复检查
    stage_nums = [s.get('stage_number', '?') for s in stages]
    dup_stages = [n for n in stage_nums if stage_nums.count(n) > 1]
    if dup_stages:
        problems.append(f'阶段重复({len(set(dup_stages))})组')

    # 3. 付款重复检查
    pay_conds = [p.get('payment_condition', '')[:20] for p in payments]
    dup_pays = [c for c in pay_conds if pay_conds.count(c) > 1 and c != '']
    if dup_pays:
        problems.append(f'付款重复({len(set(dup_pays))})组')

    # 4. 付款金额异常
    zero_pays = [p for p in payments if p.get('planned_amount', 0) == 0]
    if zero_pays:
        problems.append(f'{len(zero_pays)}条付款金额为0')

    # 5. 阶段与付款不匹配
    if len(stages) > 0 and len(payments) > 0:
        if max(len(stages), len(payments)) / max(min(len(stages), len(payments)), 1) > 3:
            problems.append(f'阶段({len(stages)})与付款({len(payments)})严重不匹配')

    # 6. KPI计算检查
    # 付款总额
    pay_total = sum(p.get('planned_amount', 0) for p in payments)
    if pay_total > 0 and (pay_total / (amt or 1)) > 1.5:
        problems.append(f'付款总额({pay_total:.0f}万)超合同额({amt:.1f}万)')

    # 7. 科学类有阶段无交付物
    if c.get('project_type') == '科研类' and len(stages) > 2 and len(deliverables) == 0:
        problems.append('科研类缺交付物')

    # 8. 无阶段但有付款
    if len(stages) == 0 and len(payments) > 0:
        problems.append('无阶段有付款')

    if problems:
        issues.append((cid, name, amt, problems))

# 输出
print(f'{"#":>3} {"合同编号":24s} {"金额":>8} {"问题数":>4}')
print('-'*60)
for cid, name, amt, probs in issues:
    print(f'{issues.index((cid,name,amt,probs))+1:>3} {cid:24s} {amt:>8.2f} {len(probs):>4}')
    for p in probs:
        print(f'      ❌ {p}')

print(f'\n有问题合同: {len(issues)}/{len(contracts)}')
conn.close()
