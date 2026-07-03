"""
合同管理系统 FastAPI 后端 + 静态文件服务
SQLite 只读 API + Vue3 仪表盘静态文件

启动: uvicorn backend.main:app --host 0.0.0.0 --port 8800
访问: http://192.168.0.236:8800 (API + Dashboard)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth, contracts, finance, invoices, suppliers, dashboard, database as db_router

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
