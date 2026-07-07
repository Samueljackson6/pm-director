"""
合同管理系统 FastAPI 后端 + 静态文件服务
SQLite 只读 API + Vue3 仪表盘静态文件

启动: uvicorn backend.main:app --host 0.0.0.0 --port 8800
访问: http://192.168.0.236:8800 (API + Dashboard)
"""

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth, contracts, finance, invoices, suppliers, dashboard, database as db_router, projects

# 服务版本号（轻量探针返回，可随发版更新）
SERVICE_VERSION = '0.1.0'

app = FastAPI(title='Contract Management API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

# Register all routers
app.include_router(auth.router)
app.include_router(contracts.router)
app.include_router(finance.router)
app.include_router(invoices.router)
app.include_router(suppliers.router)
app.include_router(dashboard.router)
app.include_router(db_router.router)
app.include_router(projects.router)


@app.get('/health')
@app.get('/api/health')
async def health_check() -> dict:
    """轻量存活探针：不查询数据库、不做任何重 IO，直接返回 200 + JSON。

    供 Docker compose healthcheck 与基础设施存活检测使用。
    """
    return {
        'status': 'ok',
        'service': 'pm-director',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': SERVICE_VERSION,
    }
