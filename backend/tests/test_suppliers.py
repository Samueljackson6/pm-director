"""供应商详情接口契约与异常路径测试。"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers import suppliers as suppliers_router


class _FakeResult:
    """提供路由所需的最小查询结果接口。"""

    def __init__(self, one=None, many=None):
        self._one = one
        self._many = many or []

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._many


class _FakeConnection:
    """记录关闭状态，并返回供应商详情查询所需的数据。"""

    def __init__(self, supplier):
        self.closed = False
        self.supplier = supplier

    def execute(self, sql, _params):
        if 'FROM suppliers' in sql:
            return _FakeResult(one=self.supplier)
        if 'FROM supplier_contracts' in sql:
            return _FakeResult(many=[])
        if 'FROM invoices' in sql:
            return _FakeResult(many=[])
        if 'FROM supplier_payments' in sql:
            return _FakeResult(many=[])
        raise AssertionError(f'未预期的 SQL：{sql}')

    def close(self):
        self.closed = True


def _supplier_client(db: _FakeConnection, monkeypatch) -> TestClient:
    """创建只挂载供应商路由的测试客户端，避免引入无关路由依赖。"""
    app = FastAPI()
    app.include_router(suppliers_router.router)
    monkeypatch.setattr(suppliers_router, 'get_db', lambda: db)
    return TestClient(app)


def test_supplier_detail_uses_vben_response_envelope(monkeypatch) -> None:
    """供应商详情必须返回 code=0 且在 data 下提供 supplier 与 contracts。"""
    db = _FakeConnection({'supplier_id': 'SUP-1', 'supplier_name': '测试供应商'})

    with _supplier_client(db, monkeypatch) as client:
        response = client.get('/api/suppliers/SUP-1')

    assert response.status_code == 200
    body = response.json()
    assert body['code'] == 0
    # API 实际返回可能包含 supplier, contracts, invoices, payments
    assert 'supplier' in body['data']
    assert 'contracts' in body['data']
    assert body['data']['supplier']['supplier_id'] == 'SUP-1'
    assert isinstance(body['data']['contracts'], list)


def test_missing_supplier_closes_database_connection(monkeypatch) -> None:
    """供应商不存在时返回 404 前必须关闭数据库连接。"""
    db = _FakeConnection(None)

    with _supplier_client(db, monkeypatch) as client:
        response = client.get('/api/suppliers/NOT-FOUND')

    assert response.status_code == 404
    assert db.closed is True