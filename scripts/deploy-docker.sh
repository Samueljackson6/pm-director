#!/usr/bin/env bash
# pm-director Docker 一键部署脚�?
# �? 236 上执�?: bash scripts/deploy-docker.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== pm-director Docker 部署 ==="
echo "目录: $ROOT_DIR"
echo "时间: $(date)"

# ============================================================
# 1. 环境检�?
# ============================================================
echo ""
echo "=== Step 1: 环境检�? ==="

if ! command -v docker &>/dev/null; then
    echo "�? docker 未安�?"
    exit 1
fi
echo "�? docker $(docker --version | cut -d' ' -f3 | tr -d ',')"

if ! docker compose version &>/dev/null; then
    echo "�? docker compose 不可�?"
    exit 1
fi
echo "�? docker compose $(docker compose version | cut -d' ' -f4)"

# ============================================================
# 2. 拉取最新代�?
# ============================================================
echo ""
echo "=== Step 2: Git 拉取最新代�? ==="
git pull --ff-only origin master || echo "⚠️ git pull失败，继续使用当前代�?"

# ============================================================
# 3. Docker 构建
# ============================================================
echo ""
echo "=== Step 3: Docker 构建 ==="
echo "后端: Dockerfile"
echo "前端: 使用宿主机预构建�? dist（部署前请先 pnpm build），Dockerfile.frontend 仅作参�?"
docker compose build --no-cache 2>&1 | tail -5 || {
    echo "�? 构建失败"
    exit 1
}
echo "�? 构建完成"

# ============================================================
# 4. 停止旧服�?
# ============================================================
echo ""
echo "=== Step 4: 停止旧服�? ==="
docker compose down 2>/dev/null || true
echo "�? 旧服务已停止"

# ============================================================
# 5. 启动新服�?
# ============================================================
echo ""
echo "=== Step 5: 启动新服�? ==="
# ============================================================
# 4.5 前端构建与产物校验（部署前会重新构建前端并校验 dist，避免 stale-dist 翻车）
# ============================================================
echo ""
echo "=== 前端构建与产物校验（部署前会重新构建前端并校验 dist） ==="

FRONTEND_DIR="ui-vben/apps/web-antd"
DIST_INDEX="$FRONTEND_DIR/dist/index.html"

# 检查构建依赖：pnpm / node 必须可用，缺失则明确报错并中止（不静默跳过）
if ! command -v pnpm &>/dev/null; then
    echo "❌ 未找到 pnpm，请先安装 (npm i -g pnpm) 或将其加入 PATH"
    exit 1
fi
if ! command -v node &>/dev/null; then
    echo "❌ 未找到 node，请先安装 Node.js"
    exit 1
fi
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ 前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

# 记录 build 开始时间，用于校验产物新鲜度（mtime 不早于该时间）
BUILD_START_TS=$(date +%s)

echo "▶ 进入 $FRONTEND_DIR 执行 pnpm build ..."
( cd "$FRONTEND_DIR" && pnpm build ) || {
    echo "❌ 前端 pnpm build 失败"
    exit 1
}
echo "✅ 前端构建完成"

# 产物校验：dist/index.html 必须存在且 mtime 不早于 build 开始时间
if [ ! -f "$DIST_INDEX" ]; then
    echo "❌ 构建产物缺失: $DIST_INDEX（build 未产出，中止部署）"
    exit 1
fi

DIST_MTIME=$(date -r "$DIST_INDEX" +%s 2>/dev/null || stat -c %Y "$DIST_INDEX" 2>/dev/null || echo 0)
if [ "$DIST_MTIME" -lt "$BUILD_START_TS" ]; then
    echo "❌ 构建产物不新鲜 (stale-dist)：dist/index.html 早于 build 开始时间，中止部署"
    exit 1
fi
echo "✅ 前端产物校验通过: $DIST_INDEX"

docker compose up -d 2>&1
echo "�? 服务已启�?"

# 等待服务就绪
echo "等待服务就绪..."
for i in $(seq 1 10); do
    sleep 2
    BE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8800/api/stats || echo 000)
    FE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8900/web/ || echo 000)
    echo "  尝试 $i: 后端=$BE 前端=$FE"
    if [ "$BE" = "200" ] && [ "$FE" = "200" ]; then
        echo "�? 前后端均已就�?"
        break
    fi
done

# ============================================================
# 6. 验证
# ============================================================
echo ""
echo "=== Step 6: 验证 ==="
echo "容器状�?:"
docker compose ps

echo ""
echo "后端 API 测试:"
curl -s http://localhost:8800/api/stats | python3 -c \
    "import json,sys; d=json.load(sys.stdin); print(f'  contracts={d[\"data\"][\"contract_count\"]}, total={d[\"data\"][\"total_amount\"]}wan')" 2>/dev/null || \
    echo "  ⚠️ 后端响应异常"

echo ""
echo "前端访问测试:"
FE_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8900/web/ || echo 000)
echo "  HTTP $FE_CODE"

# ============================================================
# 7. 审计
# ============================================================
echo ""
echo "=== Step 7: 审计 ==="
echo "Commit: $(git rev-parse --short HEAD)"
echo "时间: $(date)"

BE_OK=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8800/api/stats || echo 000)
FE_OK=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8900/web/ || echo 000)
echo "后端: $BE_OK"
echo "前端: $FE_OK"

if [ "$BE_OK" = "200" ] && [ "$FE_OK" = "200" ]; then
    echo "=== �? 审计通过 ==="
else
    echo "=== �? 审计失败 ==="
    echo "请检�?: docker compose logs"
    exit 1
fi
