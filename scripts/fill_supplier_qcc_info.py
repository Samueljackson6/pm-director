"""
批量填充供应商统一社会信用代码 — 修复版

修复：直接使用 sqlite3 连接，确保 commit 生效。
"""

import asyncio
import sqlite3
import json
import httpx
import os
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).parent.parent / 'database' / 'project_management.db'
QCC_TOKEN = os.getenv('QCC_API_TOKEN', 'MqQRwv2e0N5SLDGYlqmxKVM0NzvsLNot6kTZF50l08N1zih4')
QCC_BASE_URL = 'https://agent.qcc.com/mcp/company/stream'


async def query_company(client: httpx.AsyncClient, name: str) -> dict:
    headers = {'Authorization': f'Bearer {QCC_TOKEN}', 'Content-Type': 'application/json'}
    payload = {
        'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
        'params': {'name': 'get_company_by_query', 'arguments': {'searchKey': name.strip()}}
    }
    try:
        resp = await client.post(QCC_BASE_URL, headers=headers, json=payload)
        for line in resp.text.split('\n'):
            if line.startswith('data: '):
                data = json.loads(line[6:])
                if 'result' in data and 'content' in data['result']:
                    return json.loads(data['result']['content'][0]['text'])
    except Exception as e:
        print(f'  请求异常: {e}')
    return {'匹配结果': '失败', '检索关键字': name}


async def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 获取所有缺少 credit_code 的供应商
    cur.execute(
        "SELECT supplier_id, supplier_name FROM suppliers "
        "WHERE status='active' AND (credit_code IS NULL OR credit_code='') "
        "ORDER BY total_contract_amount DESC"
    )
    suppliers = cur.fetchall()
    print(f'需要处理的供应商: {len(suppliers)} 条\n' + '='*60)

    async with httpx.AsyncClient(timeout=15.0) as client:
        success = 0
        skip = 0
        manual = []

        for i, row in enumerate(suppliers):
            sid = row['supplier_id']
            name = row['supplier_name'].strip()
            print(f'[{i+1}/{len(suppliers)}] {name}')

            result = await query_company(client, name)
            match = result.get('匹配结果', '')
            info = result.get('企业信息')

            # info 可能是 dict（唯一匹配）或 list（多候选）
            if match in ('唯一匹配', '唯一精确匹配') and info:
                entry = info if isinstance(info, dict) else info[0]
                cc = entry.get('统一社会信用代码', '')
                if cc:
                    cur.execute(
                        "UPDATE suppliers SET credit_code=?, updated_at=? WHERE supplier_id=?",
                        (cc, datetime.now().isoformat(), sid)
                    )
                    conn.commit()
                    # 立即验证
                    cur.execute("SELECT credit_code FROM suppliers WHERE supplier_id=?", (sid,))
                    verify = cur.fetchone()
                    if verify and verify['credit_code'] == cc:
                        print(f'  ✓ 写入成功: {cc}')
                        success += 1
                    else:
                        print(f'  ✗ commit 后验证失败！')
                        manual.append({'supplier_id': sid, 'supplier_name': name, 'candidate': entry})
                else:
                    print(f'  - 无统一社会信用代码')
                    skip += 1
            elif match == '多候选' and info:
                candidates = info if isinstance(info, list) else [info]
                # 尝试精确名称匹配
                best = None
                for c in candidates:
                    if c.get('企业名称', '').strip() == name and c.get('状态') == '存续':
                        best = c
                        break
                if not best:
                    for c in candidates:
                        if c.get('企业名称', '').strip() == name:
                            best = c
                            break
                if best and best.get('统一社会信用代码'):
                    cur.execute(
                        "UPDATE suppliers SET credit_code=?, updated_at=? WHERE supplier_id=?",
                        (best['统一社会信用代码'], datetime.now().isoformat(), sid)
                    )
                    conn.commit()
                    cur.execute("SELECT credit_code FROM suppliers WHERE supplier_id=?", (sid,))
                    v = cur.fetchone()
                    if v and v['credit_code'] == best['统一社会信用代码']:
                        _cc = best['统一社会信用代码']
                        print(f'  ✓ 多候选精确匹配: {_cc}')
                        success += 1
                    else:
                        manual.append({'supplier_id': sid, 'supplier_name': name, 'candidate': best})
                else:
                    print(f'  ⚠ {len(candidates)} 个候选，需确认')
                    manual.append({'supplier_id': sid, 'supplier_name': name, 'candidates': candidates[:3]})
                    skip += 1
            else:
                print(f'  ✗ 无匹配 ({match})')
                skip += 1

    conn.close()

    print('\n' + '='*60)
    print(f'自动填充成功: {success}')
    print(f'跳过/需确认: {skip}')

    if manual:
        with open('database/manual_confirm.json', 'w', encoding='utf-8') as f:
            json.dump(manual, f, ensure_ascii=False, indent=2)
        print(f'需人工确认的记录已保存到 database/manual_confirm.json')

    # 最终验证
    vconn = sqlite3.connect(str(DB_PATH))
    vcur = vconn.cursor()
    vcur.execute("SELECT COUNT(*) FROM suppliers WHERE status='active'")
    total = vcur.fetchone()[0]
    vcur.execute("SELECT COUNT(*) FROM suppliers WHERE status='active' AND credit_code IS NOT NULL AND credit_code!=''")
    filled = vcur.fetchone()[0]
    vconn.close()
    print(f'\n最终验证: 总计 {total} 条, 已填充 {filled} 条, 填充率 {filled/total*100:.1f}%')


if __name__ == '__main__':
    asyncio.run(main())
