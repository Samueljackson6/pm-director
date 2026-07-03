#!/usr/bin/env bash
# pm-director Docker 一键部署脚本
# 在 236 上执行: bash scripts/deploy-docker.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== pm-director Docker 部署 ==="
echo "目录: $ROOT_DIR"
echo "时间: $(date)"

# ============================================================
# 1. 环境检查
# ============================================================
echo ""
echo "=== Step 1: 环境检查 ==="

if ! command -v docker &>/dev/null; then
    echo "❌ docker 未安装"
    exit 1
fi
echo "✅ docker $(docker --version | cut -d' ' -f3 | tr -d ',')"

if ! docker compose version &>/dev/null; then
    echo "❌ docker compose 不可用"
    exit 1
fi
echo "✅ docker compose $(docker compose version | cut -d' ' -f4)"

# ============================================================
# 2. 拉取最新代码
# ============================================================
echo ""
echo "=== Step 2: Git 拉取最新代码 ==="
git pull --ff-only origin master || echo "⚠️ git pull失败，继续使用当前代码"

# ============================================================
# 3. Docker 构建
# ============================================================
echo ""
echo "=== Step 3: Docker 构建 ==="
echo "后端: Dockerfile"
echo "前端: Dockerfile.frontend"
docker compose build --no-cache 2>&1 | tail -5 || {
    echo "❌ 构建失败"
    exit 1
}
echo "✅ 构建完成"

# ============================================================
# 4. 停止旧服务
# ============================================================
echo ""
echo "=== Step 4: 停止旧服务 ==="
docker compose down 2>/dev/null || true
echo "✅ 旧服务已停止"

# ============================================================
# 5. 启动新服务
# ============================================================
echo ""
echo "=== Step 5: 启动新服务 ==="
docker compose up -d 2>&1
echo "✅ 服务已启动"

# 等待服务就绪
echo "等待服务就绪..."
for i in $(seq 1 10); do
    sleep 2
    BE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8800/api/stats || echo 000)
    FE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5777/ || echo 000)
    echo "  尝试 $i: 后端=$BE 前端=$FE"
    if [ "$BE" = "200" ] && [ "$FE" = "200" ]; then
        echo "✅ 前后端均已就绪"
        break
    fi
done

# ============================================================
# 6. 验证
# ============================================================
echo ""
echo "=== Step 6: 验证 ==="
echo "容器状态:"
docker compose ps

echo ""
echo "后端 API 测试:"
curl -s http://localhost:8800/api/stats | python3 -c \
    "import json,sys; d=json.load(sys.stdin); print(f'  contracts={d[\"data\"][\"contract_count\"]}, total={d[\"data\"][\"total_amount\"]}wan')" 2>/dev/null || \
    echo "  ⚠️ 后端响应异常"

echo ""
echo "前端访问测试:"
FE_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5777/ || echo 000)
echo "  HTTP $FE_CODE"

# ============================================================
# 7. 审计
# ============================================================
echo ""
echo "=== Step 7: 审计 ==="
echo "Commit: $(git rev-parse --short HEAD)"
echo "时间: $(date)"

BE_OK=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8800/api/stats || echo 000)
FE_OK=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5777/ || echo 000)
echo "后端: $BE_OK"
echo "前端: $FE_OK"

if [ "$BE_OK" = "200" ] && [ "$FE_OK" = "200" ]; then
    echo "=== ✅ 审计通过 ==="
else
    echo "=== ❌ 审计失败 ==="
    echo "请检查: docker compose logs"
    exit 1
fi
