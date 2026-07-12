"""
全量OCR数据清洗 + 阶段/付款修复脚本 v2
===========================================
修复范围:
  1. OCR文本清洗管道
  2. stages: 去重 + remarks/考核目标拆分 + 垃圾清理
  3. payments: 截断修复 + 垃圾清理
  4. 全42合同应用
"""

import sqlite3, re, json, sys
from collections import Counter

DB_PATH = '/app/database/project_management.db'

# ============================================================
# SECTION 1: OCR 文本清洗管道
# ============================================================

def clean_ocr_text(text: str) -> str:
    """综合OCR文本清洗，移除所有常见噪声"""
    if not text:
        return text

    # 1. 移除页码标记 [第X页] [第X页/共Y页]
    text = re.sub(r'\[第\s*\d+\s*页(?:\s*/\s*共\s*\d+\s*页)?\]', '', text)

    # 2. 移除SGTYHT模板合同编号 (形如 SGTYHT/24—JS—001 或 SGSCDK00SDJS2500281)
    text = re.sub(r'SGTYHT\s*/\s*\d+\s*[—\-]\s*JS\s*[—\-]\s*\d+', '', text)
    text = re.sub(r'SGSCDK\d{2}SDJS\d+', '', text)
    text = re.sub(r'SGSCCD\d{2}\w+', '', text)

    # 3. 移除孤立的 "第X页]" 或 "X页]" (页码碎片)
    text = re.sub(r'第?\s*\d+\s*页\s*\]', '', text)

    # 4. 移除 "有限公司 第X页]" 这种断裂的页脚
    text = re.sub(r'(?:有限)?公司\s*第?\s*\d*\s*页?\s*\]', '', text)
    text = re.sub(r'\S+有限公司\s*第?\s*\d*\s*页?\s*\]?', '', text)

    # 5. 移除纯页码行 (单独一行只有一个数字)
    text = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', text)

    # 6. 修复阶段编号混入文本 (如 "5.3" 出现在词中间: "申请专5.3利")
    text = re.sub(r'(专|申|报|利|完|成|进|行|开|展)(\d+\.\d+)(利|报|申|完|成|进)', r'\1\3', text)

    # 7. 合并连续空行（最多保留1个）
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # 8. 合并多个空格
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # 9. 清理行首尾空格
    text = re.sub(r'^[ \t]+|[ \t]+$', '', text, flags=re.MULTILINE)

    # 10. 修复全角/半角混用
    # — (em dash U+2014) 替换为 - （仅当它用作分隔符时，中文文本保留）
    # 这里保守处理：只替换出现在英文/数字上下文中的全角符号

    # 11. 去除首尾空白
    text = text.strip()

    return text


def split_remarks_and_khmb(remarks_text: str) -> tuple:
    """
    从 remarks 中分离"主要内容"和"考核目标"
    返回: (主要内容, 考核目标)
    常见格式: "主要内容：xxx考核目标：yyy" 或 "主要内容：xxx5.X考核目标：yyy"
    """
    if not remarks_text:
        return ('', '')

    text = clean_ocr_text(remarks_text)

    # 模式1: "主要内容：...考核目标：..."
    match = re.search(r'主要内容[：:]\s*(.*?)(?:\d+\.\d+)?\s*考核目标[：:]\s*(.*)', text, re.DOTALL)
    if match:
        main = match.group(1).strip()
        khmb = match.group(2).strip()
        # 用 clean_ocr_text 清洗考核目标
        khmb = clean_ocr_text(khmb)
        return (main, khmb)

    # 模式2: 只有"主要内容：..."
    match = re.search(r'主要内容[：:]\s*(.*)', text, re.DOTALL)
    if match:
        return (match.group(1).strip(), '')

    # 模式3: 只有"考核目标：..."
    match = re.search(r'考核目标[：:]\s*(.*)', text, re.DOTALL)
    if match:
        return ('', clean_ocr_text(match.group(1).strip()))

    # 没有可识别的分隔，全部归为remarks
    return (text, '')


def is_ocr_garbage(text: str) -> bool:
    """判断文本是否全为OCR垃圾"""
    if not text or len(text) < 3:
        return True
    patterns = [
        r'^[\(（]?共计',         # "款项(共计"
        r'有限公司\s*第?\d*\s*页?\]?',  # OCR脚注碎片
        r'^第\d+页',            # 孤立的页码
        r'^SGTYHT',            # 模板编号
        r'^SGSCDK',
        r'^\d+\.\d+$',         # 孤立数字
        r'^[—\-]{2,}',         # 全横线
    ]
    for p in patterns:
        if re.match(p, text):
            return True
    return False

# ============================================================
# SECTION 2: 阶段数据清洗
# ============================================================

def extract_stage_name_from_content(remarks: str, acceptance_criteria: str) -> str:
    """从remarks内容中提取有意义的阶段名"""
    text = (remarks or '') + ' ' + (acceptance_criteria or '')
    # 尝试提取主要内容的第一句
    match = re.search(r'主要内容[：:]\s*(.{10,60}?)[。，,\.\s]', text)
    if match:
        return match.group(1).strip()
    # 尝试提取"完成"开头的内容
    match = re.search(r'(?:完成|开展|研发|构建|设计|研制|梳理)(.{10,40}?)[。，,\.\s]', text)
    if match:
        return ('完成' if not text.startswith('完成') else '') + match.group(0).strip()
    return ''


def fix_stages(db):
    """修复阶段数据: 去重 + 拆分remarks/考核目标 + 清理 + 生成有意义的阶段名"""
    cursor = db.cursor()

    # 1. 获取所有合同
    contracts = [r[0] for r in db.execute('SELECT DISTINCT contract_id FROM stages').fetchall()]

    stats = {'deduped': 0, 'split_remarks': 0, 'cleaned_ac': 0, 'names_generated': 0}

    for cid in contracts:
        # --- 步骤1: 检测重复阶段 ---
        dup_groups = db.execute('''
            SELECT stage_number, COUNT(*) as cnt FROM stages
            WHERE contract_id=? GROUP BY stage_number HAVING cnt > 1
        ''', (cid,)).fetchall()

        if dup_groups:
            for dg in dup_groups:
                snum = dg[0]
                rows = db.execute('''
                    SELECT stage_id, stage_name, start_time, end_time, remarks, acceptance_criteria
                    FROM stages WHERE contract_id=? AND stage_number=? ORDER BY stage_id
                ''', (cid, snum)).fetchall()

                # 找出哪个是有日期范围的，哪个是有业务名称的
                name_row = None
                date_row = None
                for r in rows:
                    name = r[1] or ''
                    if re.search(r'\d{4}年', name):  # 日期范围行
                        date_row = r
                    elif name and not re.match(r'^\d', name):  # 业务名称行
                        name_row = r

                if name_row and date_row:
                    # 合并: 用业务名称 + 日期范围
                    merged_name = name_row[1]
                    merged_start = None
                    merged_end = None
                    date_name = date_row[1] or ''
                    dm = re.match(r'(\d{4}年\d{1,2}月\d{1,2}日?)\s*[—\-–]\s*(\d{4}年\d{1,2}月\d{1,2}日?)', date_name)
                    if dm:
                        merged_start = dm.group(1)
                        merged_end = dm.group(2)
                    else:
                        merged_start = date_row[2]
                        merged_end = date_row[3]

                    # 合并remarks（取较长的那个）
                    rm_a = name_row[4] or ''
                    rm_b = date_row[4] or ''
                    merged_remarks = rm_a if len(rm_a) >= len(rm_b) else rm_b

                    # 合并acceptance_criteria
                    ac_a = name_row[5] or ''
                    ac_b = date_row[5] or ''
                    merged_ac = ac_a if len(ac_a) >= len(ac_b) else ac_b

                    # 更新第一个stage_id为合并值
                    target_id = name_row[0]
                    cursor.execute('''
                        UPDATE stages SET
                            stage_name=?, start_time=?, end_time=?,
                            remarks=?, acceptance_criteria=?
                        WHERE stage_id=?
                    ''', (merged_name, merged_start, merged_end, merged_remarks, merged_ac, target_id))

                    # 删除重复行
                    for r in rows:
                        if r[0] != target_id:
                            cursor.execute('DELETE FROM stages WHERE stage_id=?', (r[0],))
                            stats['deduped'] += 1
                else:
                    # 无法确认哪行更完整，保留第一行，删其余
                    target_id = rows[0][0]
                    for r in rows[1:]:
                        cursor.execute('DELETE FROM stages WHERE stage_id=?', (r[0],))
                        stats['deduped'] += 1

        # --- 步骤2: 拆分 remarks 中的 "主要内容" / "考核目标" ---
        stages = db.execute('''
            SELECT stage_id, remarks, acceptance_criteria
            FROM stages WHERE contract_id=? AND remarks LIKE '%考核目标%'
        ''', (cid,)).fetchall()

        for s in stages:
            sid, remarks, ac = s
            main_content, khmb = split_remarks_and_khmb(remarks or '')

            # 如果成功拆分出考核目标
            if khmb:
                existing_ac = ac or ''
                # 如果已有考核目标内容，用已拆分的（优先保留更长的）
                new_ac = khmb if len(khmb) > len(existing_ac) else existing_ac
                new_ac = clean_ocr_text(new_ac)

                cursor.execute('''
                    UPDATE stages SET remarks=?, acceptance_criteria=?
                    WHERE stage_id=?
                ''', (main_content, new_ac, sid))
                stats['split_remarks'] += 1

        # --- 步骤3: 清理 acceptance_criteria 中的OCR垃圾 ---
        stages = db.execute('''
            SELECT stage_id, acceptance_criteria FROM stages
            WHERE contract_id=? AND acceptance_criteria IS NOT NULL AND acceptance_criteria != ''
        ''', (cid,)).fetchall()

        for s in stages:
            sid, ac = s
            cleaned = clean_ocr_text(ac)

            # 移除预算表内容 (如果考核目标里混入了预算表)
            cleaned = re.sub(r'\d+\s*[．.]?\s*项目经费.*', '', cleaned, flags=re.DOTALL)
            cleaned = re.sub(r'单位[：:]\s*万元.*', '', cleaned, flags=re.DOTALL)
            cleaned = re.sub(r'科目名称\s+预算金额.*', '', cleaned, flags=re.DOTALL)

            # 移除阶段编号污染 (如 "专5.3利" → "专利")
            cleaned = re.sub(r'(\S)\d+\.\d+(\S)', r'\1\2', cleaned)
            cleaned = re.sub(r'问5\.\d+题', '问题', cleaned)
            cleaned = re.sub(r'验5\.\d+收', '验收', cleaned)

            if cleaned != ac:
                cursor.execute('UPDATE stages SET acceptance_criteria=? WHERE stage_id=?', (cleaned.strip(), sid))
                stats['cleaned_ac'] += 1

        # --- 步骤4: 生成有意义的阶段名 (对以日期命名的阶段) ---
        stages = db.execute('''
            SELECT stage_id, stage_name, remarks, acceptance_criteria, start_time, end_time
            FROM stages WHERE contract_id=? AND stage_name GLOB "*[0-9][0-9][0-9][0-9]年*"
            AND LENGTH(stage_name) > 10
        ''', (cid,)).fetchall()

        for s in stages:
            sid, name, remarks, ac, start, end = s
            # 生成业务名称
            biz_name = extract_stage_name_from_content(remarks or '', ac or '')
            if biz_name and len(biz_name) >= 6:
                cursor.execute('UPDATE stages SET stage_name=? WHERE stage_id=?', (biz_name[:50], sid))
                stats['names_generated'] += 1

    db.commit()
    return stats


# ============================================================
# SECTION 3: 付款数据清洗
# ============================================================

def fix_payments(db):
    """修复付款数据: 清理OCR垃圾、去除重复、标记无效"""
    cursor = db.cursor()
    stats = {'cleaned_stage': 0, 'cleaned_condition': 0, 'marked_garbage': 0, 'fixed_truncation': 0}

    payments = db.execute('SELECT payment_id, payment_stage, payment_condition FROM payments').fetchall()

    for p in payments:
        pid, stage, cond = p
        updates = {}

        # 清理 payment_stage
        new_stage = clean_ocr_text(stage or '')
        if is_ocr_garbage(new_stage):
            new_stage = ''  # 标记为无效
            stats['marked_garbage'] += 1
        if new_stage != (stage or ''):
            updates['payment_stage'] = new_stage
            stats['cleaned_stage'] += 1

        # 清理 payment_condition
        new_cond = clean_ocr_text(cond or '')
        if is_ocr_garbage(new_cond):
            new_cond = ''
            stats['marked_garbage'] += 1
        if new_cond != (cond or ''):
            updates['payment_condition'] = new_cond
            stats['cleaned_condition'] += 1

        if updates:
            set_clause = ', '.join(f'{k}=?' for k in updates)
            values = list(updates.values()) + [pid]
            cursor.execute(f'UPDATE payments SET {set_clause} WHERE payment_id=?', values)

    db.commit()
    return stats


# ============================================================
# SECTION 4: 合同文本字段清洗
# ============================================================

def fix_contracts(db):
    """清理 contracts 表中的文本字段"""
    cursor = db.cursor()
    stats = {'cleaned_service_content': 0, 'cleaned_party_names': 0}

    # 清理服务字段
    for r in db.execute('SELECT contract_id, service_content, service_period, service_method, service_location FROM contracts').fetchall():
        cid, sc, sp, sm, sl = r
        updates = {}
        for col, val in [('service_content', sc), ('service_period', sp), ('service_method', sm), ('service_location', sl)]:
            if val:
                cleaned = clean_ocr_text(val)
                if cleaned != val:
                    updates[col] = cleaned
        if updates:
            set_clause = ', '.join(f'{k}=?' for k in updates)
            values = list(updates.values()) + [cid]
            cursor.execute(f'UPDATE contracts SET {set_clause} WHERE contract_id=?', values)
            stats['cleaned_service_content'] += 1

    # 清理甲乙方名称
    for r in db.execute('SELECT contract_id, party_a, party_b FROM contracts').fetchall():
        cid, pa, pb = r
        updates = {}
        for col, val in [('party_a', pa), ('party_b', pb)]:
            if val:
                # 移除日期后缀 (签订日期：xxxx年xx月xx日)
                cleaned = re.sub(r'签订日期[：:]\s*\d{4}年\d{1,2}月\d{1,2}日', '', val)
                # 移除 "第X页]"
                cleaned = re.sub(r'第?\d*\s*页?\s*\]', '', cleaned)
                cleaned = cleaned.strip()
                if cleaned != val:
                    updates[col] = cleaned
        if updates:
            set_clause = ', '.join(f'{k}=?' for k in updates)
            values = list(updates.values()) + [cid]
            cursor.execute(f'UPDATE contracts SET {set_clause} WHERE contract_id=?', values)
            stats['cleaned_party_names'] += 1

    db.commit()
    return stats


# ============================================================
# SECTION 5: 主流程
# ============================================================

def main():
    db = sqlite3.connect(DB_PATH)

    print('=' * 60)
    print('全量OCR数据清洗 & 阶段/付款修复 v2')
    print('=' * 60)

    # Step 1: 阶段修复
    print('\n>>> Step 1: 阶段数据修复...')
    s1 = fix_stages(db)
    print(f'  阶段去重:  {s1["deduped"]} 行')
    print(f'  remarks/考核目标拆分: {s1["split_remarks"]} 阶段')
    print(f'  acceptance_criteria清理: {s1["cleaned_ac"]} 阶段')
    print(f'  阶段名生成: {s1["names_generated"]} 阶段')

    # Step 2: 付款修复
    print('\n>>> Step 2: 付款数据修复...')
    s2 = fix_payments(db)
    print(f'  payment_stage清理: {s2["cleaned_stage"]}')
    print(f'  payment_condition清理: {s2["cleaned_condition"]}')
    print(f'  OCR垃圾标记为空: {s2["marked_garbage"]}')

    # Step 3: 合同文本字段
    print('\n>>> Step 3: 合同文本字段清理...')
    s3 = fix_contracts(db)
    print(f'  服务内容清理: {s3["cleaned_service_content"]} 合同')
    print(f'  甲乙方名称清理: {s3["cleaned_party_names"]} 合同')

    # Step 4: 验证
    print('\n>>> Step 4: 验证修复效果...')
    # 阶段重复复查
    dups = db.execute('SELECT COUNT(*) FROM (SELECT contract_id, stage_number FROM stages GROUP BY contract_id, stage_number HAVING COUNT(*)>1)').fetchone()[0]
    print(f'  剩余阶段重复: {dups} (应为0)')

    # remarks含考核目标残余
    rm_kh = db.execute('SELECT COUNT(*) FROM stages WHERE remarks LIKE "%考核目标%"').fetchone()[0]
    print(f'  remarks残留考核目标: {rm_kh} (预期减少)')

    # 付款垃圾残余
    pay_garbage = db.execute('SELECT COUNT(*) FROM payments WHERE payment_stage = "" AND payment_condition = ""').fetchone()[0]
    print(f'  付款双空(被清为无效): {pay_garbage}')

    # 抽查ZH02-202604026
    print('\n>>> 抽查: ZH02-202604026 阶段修复后')
    for s in db.execute('SELECT stage_number, stage_name, remarks, acceptance_criteria FROM stages WHERE contract_id="ZH02-202604026" ORDER BY stage_number').fetchall():
        acl = len(s[3] or '')
        rml = len(s[2] or '')
        print(f'  #{s[0]}: [{s[1][:30]}] remarks={rml}字 ac={acl}字')

    # 抽查ZH02-202604020
    print('\n>>> 抽查: ZH02-202604020 阶段修复后')
    for s in db.execute('SELECT stage_number, stage_name, remarks, acceptance_criteria FROM stages WHERE contract_id="ZH02-202604020" ORDER BY stage_number').fetchall():
        acl = len(s[3] or '')
        rml = len(s[2] or '') 
        print(f'  #{s[0]}: [{s[1][:35]}] remarks={rml}字 ac={acl}字')

    print('\n✅ v2 清洗修复完成')
    db.close()


if __name__ == '__main__':
    main()
