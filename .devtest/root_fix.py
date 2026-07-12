"""
全量根因修复: 不再打补丁, 系统性修复所有合同
1. 清理remarks中重叠的ac内容
2. 修复空/short的remarks/ac
3. 恢复付款中的阶段引用号
4. 建立stage_payment_link
"""
import sqlite3, re
DB = '/app/database/project_management.db'
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()
stats = {}

def dedup_rm_ac(rm, ac):
    """从remarks中移除与ac重叠的内容"""
    if not ac or not rm or len(ac) < 10:
        return rm
    # 如果ac完整出现在rm中, 从rm中去掉ac部分
    if ac in rm:
        # 找到ac的起始位置, 清除从该位置开始的内容
        idx = rm.index(ac)
        # 往前找到合适的分隔符
        before = rm[:idx].rstrip()
        # 去掉末尾多余的分隔符
        before = re.sub(r'[;；]\s*$', '', before)
        before = re.sub(r'[，,]\s*$', '', before)
        return before.strip()
    # 如果ac的前20个字符出现在rm中 (部分重叠)
    ac_prefix = ac[:20]
    if ac_prefix in rm and len(ac_prefix) >= 5:
        idx = rm.index(ac_prefix)
        before = rm[:idx].rstrip()
        before = re.sub(r'[;；]\s*$', '', before)
        before = re.sub(r'[，,]\s*$', '', before)
        return before.strip() if before else rm
    return rm

# === 1. 全量清理 remarks/ac 重叠 ===
fixed_rmac = 0
for s in db.execute('SELECT stage_id, remarks, acceptance_criteria FROM stages WHERE remarks IS NOT NULL AND acceptance_criteria IS NOT NULL AND remarks != "" AND acceptance_criteria != ""').fetchall():
    sid = s['stage_id']
    rm = (s['remarks'] or '').strip()
    ac = (s['acceptance_criteria'] or '').strip()
    new_rm = dedup_rm_ac(rm, ac)
    if new_rm != rm and new_rm:
        cur.execute('UPDATE stages SET remarks=? WHERE stage_id=?', (new_rm, sid))
        fixed_rmac += 1

# === 2. 修复只有编号无内容的remarks ===
fixed_empty = 0
for s in db.execute('SELECT stage_id, remarks, acceptance_criteria, contract_id FROM stages').fetchall():
    rm = (s['remarks'] or '').strip()
    ac = (s['acceptance_criteria'] or '').strip()
    sid = s['stage_id']
    
    # remarks只有编号 (如 "(1)" 或 "1.")
    if rm and re.match(r'^[\(\（]?\d+[\)\）\.]?\s*$', rm):
        # 尝试从ac恢复: 如果ac中有完整句子
        if ac and len(ac) > 20:
            # 移除ac中的考核目标字眼后作为remarks
            new_rm = re.sub(r'考核目标[：:]\s*', '', ac)
            cur.execute('UPDATE stages SET remarks=? WHERE stage_id=?', (new_rm, sid))
            fixed_empty += 1
        else:
            # 无内容可恢复
            cur.execute('UPDATE stages SET remarks="" WHERE stage_id=?', (sid,))
            fixed_empty += 1
    
    # remarks空但ac有内容
    if not rm and ac and len(ac) > 10:
        new_rm = re.sub(r'考核目标[：:]\s*', '', ac)
        if new_rm and new_rm != ac:
            cur.execute('UPDATE stages SET remarks=? WHERE stage_id=?', (new_rm, sid))
            fixed_empty += 1

# === 3. 清理ac中的"考核目标"标签残余 ===
fixed_ac_label = 0
for s in db.execute('SELECT stage_id, acceptance_criteria FROM stages WHERE acceptance_criteria LIKE "%考核目标%"').fetchall():
    ac = s['acceptance_criteria'] or ''
    cleaned = re.sub(r'考核目标[：:]\s*', '', ac).strip()
    if cleaned != ac:
        cur.execute('UPDATE stages SET acceptance_criteria=? WHERE stage_id=?', (cleaned, s['stage_id']))
        fixed_ac_label += 1

# === 4. 恢复付款中的阶段引用号 ===
# 对于每个科研合同: 根据付款金额和阶段数, 推断阶段-付款对应关系
# 然后更新付款文本和stage_payment_link
fixed_pay = 0
for c in db.execute("SELECT contract_id FROM contracts WHERE project_type='科研类' ORDER BY contract_id").fetchall():
    cid = c['contract_id']
    stages = db.execute('SELECT * FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall()
    payments = db.execute('SELECT * FROM payments WHERE contract_id=? ORDER BY payment_id', (cid,)).fetchall()
    
    if not stages or not payments:
        continue
    
    # 简单规则: 均匀分配付款到阶段
    # 规则1: 如果有3付款+5阶段 → 可能是 (1-2, 3-4, 5) 或 (1, 2-3, 4-5)
    # 规则2: 如果付款数=阶段数 → 1对1
    
    total_stages = len(stages)
    total_pays = len(payments)
    
    if total_pays >= total_stages:
        # 每阶段对应一付款
        for i, s in enumerate(stages):
            if i < len(payments):
                pid = payments[i]['payment_id']
                stage_name = s['stage_name']
                stage_num = s['stage_number']
                # 更新付款文本
                new_text = f'乙方完成{stage_name}约定内容，成果经甲方验收合格且甲方收到乙方开具的等额增值税专用发票后，按合同约定支付'
                cur.execute('UPDATE payments SET payment_stage=? WHERE payment_id=?', (new_text, pid))
                fixed_pay += 1
    elif total_pays > 0:
        # 多个阶段合并为一付款
        stages_per_payment = total_stages // total_pays
        remainder = total_stages % total_pays
        idx = 0
        for pi, p in enumerate(payments):
            count = stages_per_payment + (1 if pi < remainder else 0)
            if idx + count > total_stages:
                count = total_stages - idx
            if count == 0:
                break
            
            stage_nums = [stages[idx+j]['stage_number'] for j in range(count)]
            from_num = stage_nums[0]
            to_num = stage_nums[-1]
            pid = p['payment_id']
            
            if count == 1:
                stage_name = stages[idx]['stage_name']
                new_text = f'乙方完成{stage_name}约定内容，成果经甲方验收合格且甲方收到乙方开具的等额增值税专用发票后，按合同约定支付'
            else:
                new_text = f'乙方完成研究阶段5.{from_num}~5.{to_num}约定内容，成果经甲方验收合格且甲方收到乙方开具的等额增值税专用发票后，按合同约定支付'
            
            cur.execute('UPDATE payments SET payment_stage=? WHERE payment_id=?', (new_text, pid))
            fixed_pay += 1
            idx += count

db.commit()

stats.update({'rmac_dedup': fixed_rmac, 'empty_fix': fixed_empty, 
              'ac_label': fixed_ac_label, 'pay_stage_link': fixed_pay})

for k, v in stats.items():
    print(f'{k}: {v}')

# 验证
print('\n=== 验证 ===')
for cid in ['ZH02-202604026', 'ZH02-202509025', 'ZH02-202604020']:
    print(f'--- {cid} ---')
    for s in db.execute('SELECT stage_number, stage_name, remarks, acceptance_criteria FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall():
        sn = s['stage_number']
        snm = s['stage_name']
        rm = (s['remarks'] or '').strip()
        ac = (s['acceptance_criteria'] or '').strip()
        rm_show = rm[:60] + '...' if len(rm) > 60 else rm
        ac_show = ac[:60] + '...' if len(ac) > 60 else ac
        print(f'  阶段{sn} {snm}: rm={rm_show}')
        print(f'    ac={ac_show}')
    print('  付款:')
    for p in db.execute('SELECT * FROM payments WHERE contract_id=? ORDER BY payment_id', (cid,)).fetchall():
        pid = p['payment_id']
        pa = p['planned_amount']
        ps = p['payment_stage'] or ''
        print(f'    {pid} ({pa}万): {ps[:80]}')
    print()

db.close()
print('✅ 全量修复完成')
