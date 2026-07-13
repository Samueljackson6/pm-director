"""企查查数据同步模块 - 将企查查数据同步到本地数据库"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.database import get_db
from backend.qcc_mcp_client import get_qcc_client


def init_qcc_tables():
    """初始化企查查数据表"""
    db = get_db()

    # 企查查工商信息表
    db.execute('''
        CREATE TABLE IF NOT EXISTS qcc_basic_info (
            credit_code TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            legal_representative TEXT,
            registered_capital TEXT,
            paid_capital TEXT,
            establishment_date TEXT,
            business_status TEXT,
            company_type TEXT,
            taxpayer_qualification TEXT,
            insured_count INTEGER,
            personnel_scale TEXT,
            registration_authority TEXT,
            registration_area TEXT,
            business_scope TEXT,
            registered_address TEXT,
            english_name TEXT,
            industry TEXT,
            organization_code TEXT,
            business_number TEXT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 企查查企业简介表
    db.execute('''
        CREATE TABLE IF NOT EXISTS qcc_company_profile (
            credit_code TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            profile TEXT,
            qcc_industry TEXT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 企查查风险扫描表
    db.execute('''
        CREATE TABLE IF NOT EXISTS qcc_risk_scan (
            credit_code TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            risk_summary TEXT,
            risk_factors_count INTEGER,
            clean_factors_count INTEGER,
            risk_factors_json TEXT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 企查查软件著作权表
    db.execute('''
        CREATE TABLE IF NOT EXISTS qcc_software_copyrights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_code TEXT NOT NULL,
            company_name TEXT,
            software_name TEXT,
            short_name TEXT,
            version TEXT,
            registration_number TEXT,
            registration_date TEXT,
            acquisition_method TEXT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(credit_code, registration_number)
        )
    ''')

    # 企查查对外投资表
    db.execute('''
        CREATE TABLE IF NOT EXISTS qcc_external_investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_code TEXT NOT NULL,
            company_name TEXT,
            investee_name TEXT,
            investee_status TEXT,
            investee_establishment_date TEXT,
            shareholding_ratio TEXT,
            subscribed_capital TEXT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(credit_code, investee_name)
        )
    ''')

    # 数据同步日志表
    db.execute('''
        CREATE TABLE IF NOT EXISTS qcc_sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_code TEXT NOT NULL,
            sync_type TEXT,
            sync_status TEXT,
            sync_message TEXT,
            sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    db.commit()
    db.close()


async def sync_supplier_qcc_data(credit_code: str) -> Dict[str, Any]:
    """
    同步供应商的企查查数据到本地数据库

    Args:
        credit_code: 统一社会信用代码

    Returns:
        同步结果
    """
    init_qcc_tables()
    db = get_db()

    try:
        # 记录同步开始
        db.execute(
            'INSERT INTO qcc_sync_log (credit_code, sync_type, sync_status, sync_message) VALUES (?, ?, ?, ?)',
            (credit_code, 'full', 'started', '开始同步')
        )
        db.commit()

        # 从企查查获取数据
        client = get_qcc_client()
        data = await client.get_supplier_detail(credit_code)

        if not data or not data.get('basic_info'):
            raise Exception('企查查数据获取失败')

        # 同步工商信息
        basic = data['basic_info']
        db.execute('''
            INSERT OR REPLACE INTO qcc_basic_info (
                credit_code, company_name, legal_representative, registered_capital,
                paid_capital, establishment_date, business_status, company_type,
                taxpayer_qualification, insured_count, personnel_scale,
                registration_authority, registration_area, business_scope,
                registered_address, english_name, industry, organization_code,
                business_number, update_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            credit_code,
            basic.get('企业名称'),
            basic.get('法定代表人'),
            basic.get('注册资本'),
            basic.get('实缴资本'),
            basic.get('成立日期'),
            basic.get('登记状态'),
            basic.get('企业类型'),
            basic.get('纳税人资质'),
            basic.get('参保人数'),
            basic.get('人员规模'),
            basic.get('登记机关'),
            basic.get('所属地区'),
            basic.get('经营范围'),
            basic.get('注册地址'),
            basic.get('英文名'),
            basic.get('国标行业'),
            basic.get('组织机构代码'),
            basic.get('工商注册号'),
            datetime.now().isoformat()
        ))

        # 同步企业简介
        profile = data.get('profile')
        if profile:
            db.execute('''
                INSERT OR REPLACE INTO qcc_company_profile (
                    credit_code, company_name, profile, qcc_industry, update_time
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                credit_code,
                profile.get('企业名称'),
                profile.get('简介'),
                profile.get('企查查行业'),
                datetime.now().isoformat()
            ))

        # 同步风险扫描
        risk = data.get('risk_scan')
        if risk:
            db.execute('''
                INSERT OR REPLACE INTO qcc_risk_scan (
                    credit_code, company_name, risk_summary,
                    risk_factors_count, clean_factors_count, risk_factors_json, update_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                credit_code,
                risk.get('企业名称'),
                risk.get('摘要'),
                risk.get('有记录因子数'),
                risk.get('无记录因子数'),
                json.dumps(risk.get('风险因子扫描', []), ensure_ascii=False),
                datetime.now().isoformat()
            ))

        # 同步软件著作权
        copyrights = data.get('software_copyrights', {}).get('软件著作权信息', [])
        for sw in copyrights:
            db.execute('''
                INSERT OR REPLACE INTO qcc_software_copyrights (
                    credit_code, company_name, software_name, short_name,
                    version, registration_number, registration_date,
                    acquisition_method, update_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                credit_code,
                data['basic_info'].get('企业名称'),
                sw.get('软件全称'),
                sw.get('软件简称'),
                sw.get('版本号'),
                sw.get('登记号'),
                sw.get('登记日期'),
                sw.get('权利取得方式'),
                datetime.now().isoformat()
            ))

        # 同步对外投资
        investments = data.get('external_investments', {}).get('对外投资信息', [])
        for inv in investments:
            db.execute('''
                INSERT OR REPLACE INTO qcc_external_investments (
                    credit_code, company_name, investee_name, investee_status,
                    investee_establishment_date, shareholding_ratio,
                    subscribed_capital, update_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                credit_code,
                data['basic_info'].get('企业名称'),
                inv.get('被投资企业名称'),
                inv.get('状态'),
                inv.get('成立日期'),
                inv.get('持股比例'),
                inv.get('认缴出资额/持股数'),
                datetime.now().isoformat()
            ))

        # 记录同步成功
        db.execute(
            'INSERT INTO qcc_sync_log (credit_code, sync_type, sync_status, sync_message) VALUES (?, ?, ?, ?)',
            (credit_code, 'full', 'success', f'同步成功: {len(copyrights)} 项软著, {len(investments)} 项投资')
        )
        db.commit()

        return {
            'status': 'success',
            'message': '同步成功',
            'data': {
                'copyrights_count': len(copyrights),
                'investments_count': len(investments),
                'has_risk': risk.get('有记录因子数', 0) if risk else 0
            }
        }

    except Exception as e:
        # 记录同步失败
        db.execute(
            'INSERT INTO qcc_sync_log (credit_code, sync_type, sync_status, sync_message) VALUES (?, ?, ?, ?)',
            (credit_code, 'full', 'failed', str(e))
        )
        db.commit()
        raise
    finally:
        db.close()


def get_local_qcc_data(credit_code: str) -> Optional[Dict[str, Any]]:
    """
    从本地数据库获取企查查数据

    Args:
        credit_code: 统一社会信用代码

    Returns:
        企查查数据字典
    """
    init_qcc_tables()
    db = get_db()

    try:
        # 获取工商信息
        basic_row = db.execute(
            'SELECT * FROM qcc_basic_info WHERE credit_code = ?',
            (credit_code,)
        ).fetchone()

        if not basic_row:
            return None

        basic = dict(basic_row)

        # 获取企业简介
        profile_row = db.execute(
            'SELECT * FROM qcc_company_profile WHERE credit_code = ?',
            (credit_code,)
        ).fetchone()
        profile = dict(profile_row) if profile_row else None

        # 获取风险扫描
        risk_row = db.execute(
            'SELECT * FROM qcc_risk_scan WHERE credit_code = ?',
            (credit_code,)
        ).fetchone()
        risk = dict(risk_row) if risk_row else None
        if risk and risk.get('risk_factors_json'):
            risk['风险因子扫描'] = json.loads(risk['risk_factors_json'])

        # 获取软件著作权
        copyright_rows = db.execute(
            'SELECT * FROM qcc_software_copyrights WHERE credit_code = ? ORDER BY registration_date DESC',
            (credit_code,)
        ).fetchall()
        copyrights = [dict(r) for r in copyright_rows]

        # 获取对外投资
        investment_rows = db.execute(
            'SELECT * FROM qcc_external_investments WHERE credit_code = ?',
            (credit_code,)
        ).fetchall()
        investments = [dict(r) for r in investment_rows]

        return {
            'basic_info': basic,
            'profile': profile,
            'risk_scan': risk,
            'software_copyrights': {'软件著作权信息': copyrights},
            'external_investments': {'对外投资信息': investments},
            'source': 'local'
        }

    finally:
        db.close()


def get_sync_history(credit_code: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    获取同步历史记录

    Args:
        credit_code: 统一社会信用代码
        limit: 返回记录数

    Returns:
        同步历史列表
    """
    init_qcc_tables()
    db = get_db()

    try:
        rows = db.execute(
            '''SELECT * FROM qcc_sync_log
               WHERE credit_code = ?
               ORDER BY sync_time DESC
               LIMIT ?''',
            (credit_code, limit)
        ).fetchall()

        return [dict(r) for r in rows]
    finally:
        db.close()


def detect_changes(credit_code: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    检测企查查数据变化（与本地数据库对比）

    Args:
        credit_code: 统一社会信用代码
        new_data: 新查询的数据

    Returns:
        变化检测结果
    """
    old_data = get_local_qcc_data(credit_code)
    if not old_data:
        return {
            'credit_code': credit_code,
            'has_changes': False,
            'changes': [],
            'message': '首次同步，无历史数据对比'
        }

    changes = []

    # 对比工商信息
    old_basic = old_data.get('basic_info', {})
    new_basic = new_data.get('basic_info', {})

    fields_to_check = [
        ('注册资本', 'registered_capital'),
        ('实缴资本', 'paid_capital'),
        ('法定代表人', 'legal_representative'),
        ('登记状态', 'business_status'),
        ('参保人数', 'insured_count'),
    ]

    for label, key in fields_to_check:
        old_val = str(old_basic.get(key, ''))
        new_val = str(new_basic.get(key, ''))
        if old_val != new_val and new_val:
            changes.append({
                'type': 'basic_info',
                'field': label,
                'old_value': old_val,
                'new_value': new_val,
                'severity': 'high' if label in ['法定代表人', '登记状态'] else 'medium'
            })

    # 对比风险扫描
    old_risk = old_data.get('risk_scan', {})
    new_risk = new_data.get('risk_scan', {})

    old_risk_count = old_risk.get('risk_factors_count', 0) or 0
    new_risk_count = new_risk.get('risk_factors_count', 0) or 0

    if old_risk_count != new_risk_count:
        changes.append({
            'type': 'risk_scan',
            'field': '风险因子数量',
            'old_value': str(old_risk_count),
            'new_value': str(new_risk_count),
            'severity': 'critical' if new_risk_count > old_risk_count else 'low'
        })

    # 对比软件著作权数量
    old_copyrights = old_data.get('software_copyrights', {}).get('软件著作权信息', [])
    new_copyrights = new_data.get('software_copyrights', {}).get('软件著作权信息', [])

    if len(old_copyrights) != len(new_copyrights):
        changes.append({
            'type': 'software_copyrights',
            'field': '软件著作权数量',
            'old_value': str(len(old_copyrights)),
            'new_value': str(len(new_copyrights)),
            'severity': 'low'
        })

    # 对比对外投资数量
    old_investments = old_data.get('external_investments', {}).get('对外投资信息', [])
    new_investments = new_data.get('external_investments', {}).get('对外投资信息', [])

    if len(old_investments) != len(new_investments):
        changes.append({
            'type': 'external_investments',
            'field': '对外投资数量',
            'old_value': str(len(old_investments)),
            'new_value': str(len(new_investments)),
            'severity': 'medium'
        })

    return {
        'credit_code': credit_code,
        'has_changes': len(changes) > 0,
        'changes': changes,
        'change_count': len(changes),
        'critical_changes': len([c for c in changes if c.get('severity') == 'critical']),
        'high_changes': len([c for c in changes if c.get('severity') == 'high']),
    }
