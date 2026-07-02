"""
合同管理系统 FastAPI 后端 + 静态文件服务
SQLite 只读 API + Vue3 仪表盘静态文件

启动: uvicorn backend.main:app --host 0.0.0.0 --port 8800
访问: http://192.168.0.236:8800 (API + Dashboard)
"""
import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title='Contract Management API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

DB_PATH = Path(__file__).parent.parent / 'database' / 'project_management.db'

# ===== Vben-compatible response wrapper =====
def vben_response(data):
    """Wrap data in Vben's expected format: {code: 0, data: ...}"""
    return {'code': 0, 'data': data, 'message': 'success'}

def vben_list(page: int, size: int, total: int, items: list):
    """Paginated list in Vben format"""
    return {'code': 0, 'data': {'total': total, 'page': page, 'size': size, 'items': items}, 'message': 'success'}

# ===== Vben Auth Mock Endpoints =====
@app.post('/system/auth/login')
def vben_login():
    return vben_response({'accessToken': 'vben-dev-token', 'refreshToken': 'vben-refresh-token', 'expires': 9999999999})

@app.post('/system/captcha/get')
def vben_captcha():
    return vben_response({'captchaEnabled': False})

@app.get('/system/user/info')
def vben_user_info():
    return vben_response({'username': 'admin', 'realName': 'Admin', 'roles': ['admin'], 'homePath': '/#/dashboard'})

@app.post('/system/auth/logout')
def vben_logout():
    return vben_response(True)

@app.post('/system/auth/refresh-token')
def vben_refresh_token(refreshToken: str = ''):
    return vben_response({'accessToken': 'vben-dev-token', 'refreshToken': 'vben-refresh-token', 'expires': 9999999999})

@app.get('/system/auth/get-permission-info')
def vben_permission_info():
    return vben_response({
        'user': {
            'userId': 1,
            'username': 'admin',
            'nickname': '管理员',
            'avatar': '',
            'homePath': '/#/dashboard',
            'roles': ['admin'],
        },
        'roles': ['admin'],
        'permissions': ['*:*:*'],
        'menus': [{
            'id': 1,
            'parentId': 0,
            'name': '概览',
            'path': '/dashboard',
            'component': 'BasicLayout',
            'componentName': 'Dashboard',
            'icon': 'lucide:layout-dashboard',
            'visible': True,
            'keepAlive': False,
            'sort': 0,
            'children': [{
                'id': 11,
                'parentId': 1,
                'name': '分析页',
                'path': 'analytics',
                'component': '/dashboard/analytics/index',
                'componentName': 'Analytics',
                'icon': '',
                'visible': True,
                'keepAlive': False,
                'sort': 0,
            }],
        }, {
            'id': 2,
            'parentId': 0,
            'name': '合同管理',
            'path': '/contracts',
            'component': 'BasicLayout',
            'componentName': 'ContractManagement',
            'icon': 'lucide:file-text',
            'visible': True,
            'keepAlive': False,
            'sort': 1,
            'children': [{
                'id': 21,
                'parentId': 2,
                'name': '合同列表',
                'path': 'list',
                'component': '/contracts/index',
                'componentName': 'ContractList',
                'icon': '',
                'visible': True,
                'keepAlive': False,
                'sort': 0,
            }],
        }, {
            'id': 3,
            'parentId': 0,
            'name': '发票管理',
            'path': '/invoices',
            'component': 'BasicLayout',
            'componentName': 'InvoiceManagement',
            'icon': 'lucide:receipt',
            'visible': True,
            'keepAlive': False,
            'sort': 2,
            'children': [{
                'id': 31,
                'parentId': 3,
                'name': '发票列表',
                'path': 'list',
                'component': '/invoices/index',
                'componentName': 'InvoiceList',
                'icon': '',
                'visible': True,
                'keepAlive': False,
                'sort': 0,
            }],
        }, {
            'id': 4,
            'parentId': 0,
            'name': '供应商管理',
            'path': '/suppliers',
            'component': 'BasicLayout',
            'componentName': 'SupplierManagement',
            'icon': 'lucide:building',
            'visible': True,
            'keepAlive': False,
            'sort': 3,
            'children': [{
                'id': 41,
                'parentId': 4,
                'name': '供应商列表',
                'path': 'list',
                'component': '/suppliers/index',
                'componentName': 'SupplierList',
                'icon': '',
                'visible': True,
                'keepAlive': False,
                'sort': 0,
            }],
        }],
    })

@app.get('/api/menu/list')
def vben_menu_list():
    return vben_response([{
        'path': '/dashboard', 'name': 'Dashboard', 'component': 'BasicLayout',
        'meta': {'title': 'Dashboard', 'icon': 'lucide:layout-dashboard'},
        'children': [
            {'path': '/dashboard/analytics', 'name': 'Analytics', 'component': '/dashboard/analytics/index', 'meta': {'title': 'Analytics'}},
        ]
    }])

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

# ---- Stats ----
@app.get('/api/stats')
def get_stats():
    db = get_db()
    c = db.execute('SELECT COUNT(*) FROM contracts').fetchone()[0]
    total_amt = db.execute('SELECT COALESCE(SUM(contract_amount),0) FROM contracts').fetchone()[0]
    fin = db.execute('''
        SELECT COALESCE(SUM(invoice_total),0) as inv,
               COALESCE(SUM(payment_total),0) as pay
        FROM current_finance_view
    ''').fetchone()
    fin2 = db.execute('''
        SELECT COALESCE(SUM(sub_invoice_total),0) as sub_inv,
               COALESCE(SUM(sub_payment_total),0) as sub_pay
        FROM finance_records
        WHERE record_id IN (SELECT MAX(record_id) FROM finance_records GROUP BY project_id)
    ''').fetchone()
    stages = db.execute('SELECT COUNT(*) FROM stages').fetchone()[0]
    payments = db.execute('SELECT COUNT(*) FROM payments').fetchone()[0]
    deliverables = db.execute('SELECT COUNT(*) FROM deliverables').fetchone()[0]
    db.close()
    rate = round(fin['pay'] / fin['inv'] * 100, 1) if fin['inv'] else 0
    return vben_response({
        'contract_count': c,
        'total_amount': round(total_amt, 2),
        'invoiced': round(fin['inv'], 2),
        'received': round(fin['pay'], 2),
        'receipt_rate': rate,
        'sub_invoiced': round(fin2['sub_inv'], 2),
        'sub_paid': round(fin2['sub_pay'], 2),
        'stages': stages,
        'payments': payments,
        'deliverables': deliverables,
    })

# ---- Contracts list ----
@app.get('/api/contracts')
def get_contracts(page: int = 1, size: int = 20, search: str = '', sort: str = 'amount_desc'):
    db = get_db()
    where = ''
    params = []
    if search:
        where = "WHERE c.project_name LIKE ? OR c.contract_id LIKE ? OR c.party_a LIKE ?"
        like = f'%{search}%'
        params = [like, like, like]
    order = 'c.contract_amount DESC'
    if sort == 'amount_asc': order = 'c.contract_amount ASC'
    elif sort == 'name': order = 'c.project_name ASC'
    elif sort == 'date_desc': order = 'c.sign_date DESC'
    offset = (page - 1) * size
    total = db.execute(f'SELECT COUNT(*) FROM contracts c {where}', params).fetchone()[0]
    rows = db.execute(f'''
        SELECT c.*, COALESCE(fr.invoice_total,0) as invoice_total,
               COALESCE(fr.payment_total,0) as payment_total
        FROM contracts c
        LEFT JOIN current_finance_view fr ON c.contract_id = fr.project_id
        {where}
        ORDER BY {order}
        LIMIT ? OFFSET ?
    ''', params + [size, offset]).fetchall()
    db.close()
    return vben_list(page, size, total, [dict(r) for r in rows])

# ---- Contract detail ----
@app.get('/api/contracts/{contract_id}')
def get_contract(contract_id: str):
    db = get_db()
    row = db.execute('SELECT * FROM contracts WHERE contract_id=?', (contract_id,)).fetchone()
    if not row:
        raise HTTPException(404, 'Contract not found')
    stages = [dict(r) for r in db.execute('SELECT * FROM stages WHERE contract_id=? ORDER BY stage_number', (contract_id,)).fetchall()]
    payments = [dict(r) for r in db.execute('SELECT * FROM payments WHERE contract_id=? ORDER BY payment_id', (contract_id,)).fetchall()]
    deliverables = [dict(r) for r in db.execute('SELECT * FROM deliverables WHERE contract_id=?', (contract_id,)).fetchall()]
    finance = db.execute('SELECT * FROM current_finance_view WHERE project_id=?', (contract_id,)).fetchone()
    db.close()
    return vben_response({'contract': dict(row), 'stages': stages, 'payments': payments, 'deliverables': deliverables, 'finance': dict(finance) if finance else None})

# ---- Finance summary ----
@app.get('/api/finance/summary')
def get_finance_summary():
    db = get_db()
    rows = db.execute('''
        SELECT cv.project_id, cv.project_name, cv.invoice_total, cv.payment_total,
               cv.payment_unreceived, fr.sub_invoice_total, fr.sub_payment_total, cv.subcontractor
        FROM current_finance_view cv
        LEFT JOIN finance_records fr ON cv.project_id = fr.project_id
            AND fr.record_id IN (SELECT MAX(record_id) FROM finance_records GROUP BY project_id)
        ORDER BY cv.invoice_total DESC
    ''').fetchall()
    db.close()
    return vben_response({'items': [dict(r) for r in rows]})

# ---- Finance trend (by batch) ----
@app.get('/api/finance/trend')
def get_finance_trend():
    db = get_db()
    rows = db.execute('''
        SELECT batch_id,
               COALESCE(SUM(invoice_total),0) as inv,
               COALESCE(SUM(payment_total),0) as pay,
               import_time
        FROM finance_records
        WHERE batch_id IS NOT NULL
        GROUP BY batch_id
        ORDER BY import_time
    ''').fetchall()
    db.close()
    return vben_response({'trends': [dict(r) for r in rows]})

# ---- Top customers ----
@app.get('/api/finance/top-customers')
def get_top_customers(limit: int = 10):
    db = get_db()
    rows = db.execute('''
        SELECT party_a as customer, COUNT(*) as cnt, COALESCE(SUM(contract_amount),0) as total
        FROM contracts
        WHERE party_a IS NOT NULL AND party_a != ''
        GROUP BY party_a
        ORDER BY total DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    db.close()
    return vben_response({'customers': [dict(r) for r in rows]})

# ---- Project types distribution (with extended categories) ----
@app.get('/api/stats/types')
def get_type_distribution():
    db = get_db()
    rows = db.execute('''
        SELECT COALESCE(cta.contract_category, c.project_type) as type,
               COUNT(*) as cnt, COALESCE(SUM(c.contract_amount),0) as total
        FROM contracts c
        LEFT JOIN contract_type_attributes cta ON c.contract_id = cta.contract_id
        WHERE c.contract_amount > 0
        GROUP BY type
        ORDER BY total DESC
    ''').fetchall()
    db.close()
    return vben_response({'types': [dict(r) for r in rows]})

# ---- Invoices ----
@app.get('/api/invoices')
def get_invoices(project_id: str = '', page: int = 1, size: int = 50):
    db = get_db()
    where = ''
    params = []
    if project_id:
        where = 'WHERE project_id = ?'
        params = [project_id]
    total = db.execute(f'SELECT COUNT(*) FROM invoices {where}', params).fetchone()[0]
    rows = db.execute(f'SELECT * FROM invoices {where} ORDER BY invoice_date DESC LIMIT ? OFFSET ?',
        params + [size, (page-1)*size]).fetchall()
    db.close()
    return vben_list(page, size, total, [dict(r) for r in rows])

# ---- Invoice summary by project ----
@app.get('/api/invoices/summary')
def get_invoice_summary():
    db = get_db()
    rows = db.execute('''
        SELECT i.project_id, c.project_name, c.contract_amount,
               SUM(CASE WHEN i.invoice_type='客户开票' THEN i.amount ELSE 0 END) as invoiced,
               SUM(CASE WHEN i.invoice_type='客户回款' THEN i.amount ELSE 0 END) as received,
               COUNT(CASE WHEN i.invoice_type='客户开票' THEN 1 END) as inv_count,
               COUNT(CASE WHEN i.invoice_type='客户回款' THEN 1 END) as pay_count
        FROM invoices i
        LEFT JOIN contracts c ON i.project_id = c.contract_id
        GROUP BY i.project_id
        ORDER BY invoiced DESC
    ''').fetchall()
    db.close()
    return vben_response({'items': [dict(r) for r in rows]})

# ---- Suppliers ----
@app.get('/api/suppliers')
def get_suppliers():
    db = get_db()
    rows = db.execute('''
        SELECT * FROM suppliers WHERE status='active' AND total_contract_amount > 0
        ORDER BY total_contract_amount DESC
    ''').fetchall()
    db.close()
    return vben_response({'items': [dict(r) for r in rows]})

@app.get('/api/suppliers/{supplier_id}')
def get_supplier(supplier_id: str):
    db = get_db()
    sup = db.execute('SELECT * FROM suppliers WHERE supplier_id=?', (supplier_id,)).fetchone()
    if not sup:
        raise HTTPException(404, 'Supplier not found')
    contracts = [dict(r) for r in db.execute('''
        SELECT sc.*, c.project_name FROM supplier_contracts sc
        LEFT JOIN contracts c ON sc.project_id = c.contract_id
        WHERE sc.supplier_id=?
    ''', (supplier_id,)).fetchall()]
    db.close()
    return {'supplier': dict(sup), 'contracts': contracts}

# ---- Contract categories ----
@app.get('/api/contracts/categories')
def get_contract_categories():
    db = get_db()
    rows = db.execute('''
        SELECT cta.*, c.project_name, c.contract_amount, c.project_type
        FROM contract_type_attributes cta
        LEFT JOIN contracts c ON cta.contract_id = c.contract_id
        ORDER BY c.contract_amount DESC
    ''').fetchall()
    db.close()
    return {'items': [dict(r) for r in rows]}

# ---- Database stats ----
@app.get('/api/db/summary')
def get_db_summary():
    db = get_db()
    tables = ['contracts','stages','payments','deliverables','finance_records',
              'invoices','suppliers','supplier_contracts','contract_id_mapping',
              'contract_type_attributes','project_status']
    result = {}
    for t in tables:
        try:
            cnt = db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
            result[t] = cnt
        except:
            result[t] = 0
    db.close()
    return result
