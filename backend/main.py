"""
合同管理系统 FastAPI 后端 + 静态文件服务
SQLite API + Vue3 仪表盘静态文件

启动: uvicorn backend.main:app --host 0.0.0.0 --port 8800
访问: http://192.168.0.236:8800 (API + Dashboard)
"""

import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend import database
from backend.routers import auth, contracts, finance, invoices, suppliers, supplier_contacts, supplier_invoices, dashboard, database as db_router, projects, receipts

# 服务版本号（轻量探针返回，可随发版更新）
SERVICE_VERSION = '0.1.0'
DEFAULT_CORS_ORIGINS = (
    'http://localhost:18090',
    'http://localhost:8900',
    'http://localhost:5777',
)
CORS_ORIGINS = tuple(
    origin.strip()
    for origin in os.getenv('PM_CORS_ORIGINS', ','.join(DEFAULT_CORS_ORIGINS)).split(',')
    if origin.strip()
)

app = FastAPI(title='Contract Management API', version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ORIGINS),
    allow_methods=['*'],
    allow_headers=['*'],
)

# 注册所有业务路由
app.include_router(auth.router)
app.include_router(contracts.router)
app.include_router(finance.router)
app.include_router(invoices.router)
app.include_router(suppliers.router)
app.include_router(supplier_contacts.router)
app.include_router(dashboard.router)
app.include_router(db_router.router)
app.include_router(projects.router)
app.include_router(receipts.router)
app.include_router(supplier_invoices.router)


@app.get('/health')
@app.get('/api/health')
async def health_check() -> dict:
    """轻量存活探针：不查询数据库、不做任何重 IO。"""
    return {
        'status': 'ok',
        'service': 'pm-director',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': SERVICE_VERSION,
    }


@app.get('/ready')
def readiness_check() -> dict:
    """就绪探针：确认数据库可连接，并确保连接始终关闭。"""
    db = None
    try:
        db = database.get_db()
        db.execute('SELECT 1')
    except Exception as exc:
        raise HTTPException(status_code=503, detail='database unavailable') from exc
    finally:
        if db is not None:
            db.close()
    return {'status': 'ready'}
