#!/usr/bin/env python3
"""
阶段/付款/服务内容 数据修复
"""
import sqlite3, os, re

db = sqlite3.connect('database/project_management.db')
db.row_factory = sqlite3.Row

print('='*60)
print('修复1: 阶段数据清洗')
print('='*60)

# 清洗所有阶段的考核目标(去除页码和模板ID垃圾)
stages = db.execute('SELECT stage_id, contract_id, acceptance_criteria FROM stages WHERE acceptance_criteria IS NOT NULL').fetchall()
cleaned = 0
for s in stages:
    old = s['acceptance_criteria'] or ''
    if not old:
        continue
    new = old
    # 去除 "[第N页]"
    new = re.sub(r'\[\s*第\d+\s*页\s*\]', '', new)
    # 去除 "SGTYHT/24-JS-001科学技术项目合同合同编号：SGS..."
    new = re.sub(r'SGTYHT/\d+-\w+-\d+科学技术项目合同', '', new)
    new = re.sub(r'合同编号[：:]\w+', '', new)
    new = re.sub(r'SGSC\w+', '', new)
    # 去除悬挂的页码数字
    new = re.sub(r'\b\d+\[第', '', new)
    # 去除 "5.4" "5.5" 等段落编号在考核目标末尾
    new = re.sub(r'\s*\d+\.\d+\s*$', '', new)
    new = new.strip()
    if new != old:
        db.execute('UPDATE stages SET acceptance_criteria=? WHERE stage_id=?', (new, s['stage_id']))
        cleaned += 1

print(f'  清洗考核目标: {cleaned} 条')

# 对remarks也做同样清洗
stages2 = db.execute('SELECT stage_id, contract_id, remarks FROM stages WHERE remarks IS NOT NULL').fetchall()
cleaned2 = 0
for s in stages2:
    old = s['remarks'] or ''
    if not old:
        continue
    new = old
    new = re.sub(r'\[\s*第\d+\s*页\s*\]', '', new)
    new = re.sub(r'SGTYHT/\d+-\w+-\w+', '', new)
    new = re.sub(r'合同编号[：:]\w+', '', new)
    new = re.sub(r'SGSC\w+', '', new)
    new = new.strip()
    if new != old:
        db.execute('UPDATE stages SET remarks=? WHERE stage_id=?', (new, s['stage_id']))
        cleaned2 += 1

print(f'  清洗备考: {cleaned2} 条')

# 修复阶段编号空缺
print()
for cid in ['ZH02-202509025']:
    stages = db.execute('SELECT stage_id, stage_number FROM stages WHERE contract_id=? ORDER BY stage_number', (cid,)).fetchall()
    nums = [s[1] for s in stages]
    print(f'  {cid} 当前阶段编号: {nums}')
    # 检查是否需要重编号
    expected = list(range(len(stages)))
    if nums != expected:
        for i, s in enumerate(stages):
            db.execute('UPDATE stages SET stage_number=? WHERE stage_id=?', (i, s[0]))
        print(f'  重编号为: {list(range(len(stages)))}')

db.commit()

print()
print('='*60)
print('修复2: 付款条件清洗')
print('='*60)

pays = db.execute('SELECT payment_id, contract_id, payment_condition, payment_stage FROM payments').fetchall()
for p in pays:
    cond = p['payment_condition'] or ''
    stage = p['payment_stage'] or ''
    
    # 清洗条件文本
    new_cond = cond
    new_cond = re.sub(r'\s+', ' ', new_cond)  # 合并多余空白
    new_cond = re.sub(r'^\s*[，,、\s]+', '', new_cond)  # 去掉开头的标点
    new_cond = new_cond[:200]
    
    if new_cond != cond:
        db.execute('UPDATE payments SET payment_condition=? WHERE payment_id=?', (new_cond, p['payment_id']))

print('  付款条件已清洗')

db.commit()
db.close()
print('\n完成')
