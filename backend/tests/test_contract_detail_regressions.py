"""合同详情页回归测试。"""

import pytest
from fastapi import HTTPException

from backend.routers import contracts


class _FakeResult:
    """提供合同详情函数所需的最小查询结果接口。"""

    def __init__(self, *, one=None, many=()):
        self._one = one
        self._many = list(many)

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._many


class _FakeDb:
    """按 SQL 片段返回固定结果，避免回归测试依赖真实数据库。"""

    def __init__(self, contract_exists=True):
        self.closed = False
        self.contract = {
            "contract_id": "CONTRACT-001",
            "service_period": None,
            "expiry_date": None,
            "project_type": "科研类",
        }
        if not contract_exists:
            self.contract = None
        self.stage = {
            "contract_id": "CONTRACT-001",
            "stage_number": 1,
            "start_time": None,
            "end_time": None,
        }

    def execute(self, sql, _params=()):
        normalized_sql = " ".join(sql.split()).lower()
        if normalized_sql.startswith("select * from contracts where"):
            return _FakeResult(one=self.contract)
        if "from stages where" in normalized_sql:
            return _FakeResult(many=[self.stage])
        return _FakeResult()

    def close(self):
        self.closed = True


def test_contract_detail_handles_null_stage_start_time(monkeypatch):
    """阶段 start_time 为 NULL 时，合同详情调用应成功。"""

    monkeypatch.setattr(contracts, "get_db", lambda: _FakeDb())

    response = contracts.get_contract("CONTRACT-001")

    assert response["code"] == 0
    assert response["data"]["stages"][0]["start_time"] is None


def test_missing_contract_closes_database_connection(monkeypatch):
    """合同不存在时，抛出 404 前必须关闭数据库连接。"""

    db = _FakeDb(contract_exists=False)
    monkeypatch.setattr(contracts, "get_db", lambda: db)

    with pytest.raises(HTTPException) as exc_info:
        contracts.get_contract("NOT-FOUND")

    assert exc_info.value.status_code == 404
    assert db.closed is True
