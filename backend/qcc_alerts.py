"""企查查风险预警模块 - 监控企业风险变化并发送通知"""

import json
from typing import Dict, Any, List
from backend.database import get_db


def init_alert_tables():
    """初始化预警相关表"""
    db = get_db()

    # 风险预警表
    db.execute('''
        CREATE TABLE IF NOT EXISTS qcc_risk_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_code TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            alert_level TEXT NOT NULL,
            alert_message TEXT NOT NULL,
            alert_data TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 预警配置表
    db.execute('''
        CREATE TABLE IF NOT EXISTS qcc_alert_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_code TEXT UNIQUE NOT NULL,
            enabled INTEGER DEFAULT 1,
            alert_on_risk_increase INTEGER DEFAULT 1,
            alert_on_legal_change INTEGER DEFAULT 1,
            alert_on_status_change INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    db.commit()
    db.close()


def check_and_create_alerts(credit_code: str, changes: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    检查变化并创建预警

    Args:
        credit_code: 统一社会信用代码
        changes: detect_changes 返回的变化数据

    Returns:
        创建的预警列表
    """
    if not changes.get('has_changes'):
        return []

    init_alert_tables()
    db = get_db()

    created_alerts = []

    try:
        for change in changes.get('changes', []):
            severity = change.get('severity', 'low')
            change_type = change.get('type', '')
            field = change.get('field', '')

            # 根据严重程度确定预警级别
            alert_level = 'info'
            if severity == 'critical':
                alert_level = 'critical'
            elif severity == 'high':
                alert_level = 'warning'
            elif severity == 'medium':
                alert_level = 'info'

            # 生成预警消息
            old_val = change.get('old_value', '')
            new_val = change.get('new_value', '')
            message = f"{field} 发生变化: {old_val} → {new_val}"

            # 创建预警记录
            cursor = db.execute('''
                INSERT INTO qcc_risk_alerts
                (credit_code, alert_type, alert_level, alert_message, alert_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                credit_code,
                change_type,
                alert_level,
                message,
                json.dumps(change, ensure_ascii=False)
            ))

            alert_id = cursor.lastrowid
            created_alerts.append({
                'id': alert_id,
                'credit_code': credit_code,
                'alert_type': change_type,
                'alert_level': alert_level,
                'alert_message': message,
                'change': change
            })

        db.commit()
        return created_alerts

    finally:
        db.close()


def get_alerts(credit_code: str = None, unread_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
    """
    获取预警列表

    Args:
        credit_code: 统一社会信用代码（可选，不传则获取所有）
        unread_only: 是否只返回未读预警
        limit: 返回数量限制

    Returns:
        预警列表
    """
    init_alert_tables()
    db = get_db()

    try:
        query = 'SELECT * FROM qcc_risk_alerts'
        params = []

        conditions = []
        if credit_code:
            conditions.append('credit_code = ?')
            params.append(credit_code)

        if unread_only:
            conditions.append('is_read = 0')

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        rows = db.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    finally:
        db.close()


def mark_alert_read(alert_id: int) -> bool:
    """标记预警为已读"""
    init_alert_tables()
    db = get_db()

    try:
        db.execute('UPDATE qcc_risk_alerts SET is_read = 1 WHERE id = ?', (alert_id,))
        db.commit()
        return True
    finally:
        db.close()


def get_alert_stats(credit_code: str = None) -> Dict[str, Any]:
    """
    获取预警统计

    Args:
        credit_code: 统一社会信用代码（可选）

    Returns:
        统计信息
    """
    init_alert_tables()
    db = get_db()

    try:
        where_clause = ''
        params = []

        if credit_code:
            where_clause = 'WHERE credit_code = ?'
            params.append(credit_code)

        # 总数
        total = db.execute(f'SELECT COUNT(*) FROM qcc_risk_alerts {where_clause}', params).fetchone()[0]

        # 未读数
        unread_where = where_clause + (' AND ' if where_clause else 'WHERE ') + 'is_read = 0'
        unread = db.execute(f'SELECT COUNT(*) FROM qcc_risk_alerts {unread_where}', params).fetchone()[0]

        # 按级别统计
        critical = db.execute(
            f'SELECT COUNT(*) FROM qcc_risk_alerts {where_clause} {"AND " if where_clause else "WHERE "}alert_level = ?',
            params + ['critical']
        ).fetchone()[0]

        warning = db.execute(
            f'SELECT COUNT(*) FROM qcc_risk_alerts {where_clause} {"AND " if where_clause else "WHERE "}alert_level = ?',
            params + ['warning']
        ).fetchone()[0]

        return {
            'total': total,
            'unread': unread,
            'critical': critical,
            'warning': warning,
            'info': total - critical - warning
        }

    finally:
        db.close()


def update_alert_config(credit_code: str, config: Dict[str, Any]) -> bool:
    """
    更新预警配置

    Args:
        credit_code: 统一社会信用代码
        config: 配置项

    Returns:
        是否成功
    """
    init_alert_tables()
    db = get_db()

    try:
        # 检查是否已存在配置
        existing = db.execute(
            'SELECT id FROM qcc_alert_config WHERE credit_code = ?',
            (credit_code,)
        ).fetchone()

        if existing:
            # 更新
            updates = []
            params = []

            for key in ['enabled', 'alert_on_risk_increase', 'alert_on_legal_change', 'alert_on_status_change']:
                if key in config:
                    updates.append(f'{key} = ?')
                    params.append(config[key])

            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                params.append(credit_code)
                db.execute(
                    f'UPDATE qcc_alert_config SET {", ".join(updates)} WHERE credit_code = ?',
                    params
                )
        else:
            # 插入
            fields = ['credit_code']
            values = [credit_code]

            for key in ['enabled', 'alert_on_risk_increase', 'alert_on_legal_change', 'alert_on_status_change']:
                if key in config:
                    fields.append(key)
                    values.append(config[key])

            placeholders = ', '.join(['?' for _ in fields])
            db.execute(
                f'INSERT INTO qcc_alert_config ({", ".join(fields)}) VALUES ({placeholders})',
                values
            )

        db.commit()
        return True

    finally:
        db.close()


def get_alert_config(credit_code: str) -> Dict[str, Any]:
    """获取预警配置"""
    init_alert_tables()
    db = get_db()

    try:
        row = db.execute(
            'SELECT * FROM qcc_alert_config WHERE credit_code = ?',
            (credit_code,)
        ).fetchone()

        if row:
            return dict(row)

        # 返回默认配置
        return {
            'credit_code': credit_code,
            'enabled': 1,
            'alert_on_risk_increase': 1,
            'alert_on_legal_change': 1,
            'alert_on_status_change': 1
        }

    finally:
        db.close()
