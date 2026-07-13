"""企查查 MCP 客户端 - 调用企查查 MCP 服务器获取企业信息，支持缓存"""

import json
import time
import sqlite3
import httpx
import os
from typing import Optional, Dict, Any
from pathlib import Path


class QccCache:
    """查询缓存，支持 Redis（优先）和 SQLite（后备）"""

    def __init__(self, redis_url: str = None, db_path: str = None, ttl: int = 86400):
        self.ttl = ttl
        self.prefix = "qcc"
        self.backend = None

        # 优先尝试 Redis
        if redis_url:
            try:
                import redis
                self.redis = redis.from_url(redis_url, decode_responses=True)
                self.redis.ping()
                self.backend = "redis"
                print(f"企查查缓存: Redis ({redis_url}), TTL={ttl}s")
                return
            except Exception:
                pass

        # 后备: SQLite
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / "database" / "qcc_cache.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self._init_db()
        self.backend = "sqlite"
        print(f"企查查缓存: SQLite ({db_path}), TTL={ttl}s")

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS qcc_cache (
                    cache_key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON qcc_cache(created_at)")

    def get(self, key: str) -> Optional[Any]:
        full_key = f"{self.prefix}:{key}"

        if self.backend == "redis":
            try:
                cached = self.redis.get(full_key)
                return json.loads(cached) if cached else None
            except Exception:
                return None

        try:
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute(
                    "SELECT data, created_at FROM qcc_cache WHERE cache_key = ?",
                    (full_key,)
                ).fetchone()
                if row and (time.time() - row[1]) < self.ttl:
                    return json.loads(row[0])
                if row:
                    conn.execute("DELETE FROM qcc_cache WHERE cache_key = ?", (full_key,))
        except Exception:
            pass
        return None

    def set(self, key: str, data: Any) -> None:
        full_key = f"{self.prefix}:{key}"
        json_str = json.dumps(data, ensure_ascii=False)

        if self.backend == "redis":
            try:
                self.redis.setex(full_key, self.ttl, json_str)
            except Exception:
                pass
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO qcc_cache (cache_key, data, created_at) VALUES (?, ?, ?)",
                    (full_key, json_str, time.time())
                )
        except Exception:
            pass

    def clear(self, pattern_key: str) -> int:
        """清除匹配 key 的缓存，返回清除数量"""
        pattern = f"{self.prefix}:{pattern_key}"

        if self.backend == "redis":
            try:
                keys = list(self.redis.scan_iter(match=pattern, count=100))
                if keys:
                    return self.redis.delete(*keys)
            except Exception:
                pass
            return 0

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM qcc_cache WHERE cache_key LIKE ?",
                    (pattern.replace("*", "%"),)
                )
                return cursor.rowcount
        except Exception:
            return 0

    def stats(self) -> Dict[str, Any]:
        info = {"backend": self.backend, "prefix": self.prefix, "ttl_seconds": self.ttl}

        if self.backend == "redis":
            try:
                keys = list(self.redis.scan_iter(match=f"{self.prefix}:*", count=1000))
                info["total_keys"] = len(keys)
            except Exception as e:
                info["error"] = str(e)
        else:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    row = conn.execute(
                        "SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM qcc_cache"
                    ).fetchone()
                    info["total_keys"] = row[0] or 0
                    if row[1]:
                        info["oldest_entry"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(row[1]))
                        info["newest_entry"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(row[2]))
            except Exception as e:
                info["error"] = str(e)

        return info


class QccMcpClient:
    """企查查 MCP 客户端"""

    def __init__(self, token: str, cache: QccCache = None):
        self.token = token
        self.base_url = "https://agent.qcc.com/mcp"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.cache = cache

    async def _call_mcp_tool(self, server: str, tool_name: str, search_key: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{server}/stream"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": {"searchKey": search_key}}
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()

                for line in response.text.split('\n'):
                    if line.startswith('data: '):
                        data = json.loads(line[6:])
                        if 'result' in data and 'content' in data['result']:
                            return json.loads(data['result']['content'][0]['text'])
                return None
            except Exception as e:
                print(f"调用企查查 MCP 失败: {e}")
                return None

    async def _cached_query(self, dimension: str, search_key: str, server: str, tool_name: str) -> Optional[Dict[str, Any]]:
        cache_key = f"{dimension}:{search_key}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        result = await self._call_mcp_tool(server, tool_name, search_key)

        if result and self.cache:
            self.cache.set(cache_key, result)

        return result

    async def get_company_registration_info(self, search_key: str) -> Optional[Dict[str, Any]]:
        return await self._cached_query("basic", search_key, "company", "get_company_registration_info")

    async def get_company_profile(self, search_key: str) -> Optional[Dict[str, Any]]:
        return await self._cached_query("profile", search_key, "company", "get_company_profile")

    async def get_company_risk_scan(self, search_key: str) -> Optional[Dict[str, Any]]:
        return await self._cached_query("risk", search_key, "risk", "get_company_risk_scan")

    async def get_software_copyright_info(self, search_key: str) -> Optional[Dict[str, Any]]:
        return await self._cached_query("software", search_key, "ipr", "get_software_copyright_info")

    async def get_external_investments(self, search_key: str) -> Optional[Dict[str, Any]]:
        return await self._cached_query("investment", search_key, "company", "get_external_investments")

    async def get_supplier_detail(self, search_key: str) -> Dict[str, Any]:
        """获取供应商详细信息（5 维度聚合查询）"""
        import asyncio

        results = await asyncio.gather(
            self.get_company_registration_info(search_key),
            self.get_company_profile(search_key),
            self.get_company_risk_scan(search_key),
            self.get_software_copyright_info(search_key),
            self.get_external_investments(search_key)
        )

        return {
            "basic_info": results[0],
            "profile": results[1],
            "risk_scan": results[2],
            "software_copyrights": results[3],
            "external_investments": results[4]
        }

    def clear_supplier_cache(self, search_key: str) -> int:
        return self.cache.clear(f"*:{search_key}") if self.cache else 0

    def get_cache_stats(self) -> Dict[str, Any]:
        return self.cache.stats() if self.cache else {"enabled": False}


_qcc_client: Optional[QccMcpClient] = None


def get_qcc_client() -> QccMcpClient:
    global _qcc_client

    if _qcc_client is None:
        token = os.getenv("QCC_API_TOKEN", "MqQRwv2e0N5SLDGYlqmxKVM0NzvsLNot6kTZF50l08N1zih4")
        redis_url = os.getenv("REDIS_URL")
        cache_ttl = int(os.getenv("QCC_CACHE_TTL", "86400"))
        cache = QccCache(redis_url=redis_url, ttl=cache_ttl)
        _qcc_client = QccMcpClient(token, cache=cache)

    return _qcc_client
