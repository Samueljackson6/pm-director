#!/usr/bin/env bash
# scripts/verify-env.sh - pm-director Docker 本地环境健康基线一键复跑
#
# 对应基线文档: docs/Docker环境健康基线.md
# 用法:
#   bash scripts/verify-env.sh
#
# 设计要点:
#   - 使用 set -uo pipefail（不含 set -e），单项失败不会中断其它检查。
#   - 逐项打印 ● PASS / ● FAIL 及实际观测。
#   - stale-dist 作为独立 WARN 项单列（不计入 FAIL，但给出提示与处置结论）。
#   - 末尾打印汇总 "X PASS / Y FAIL / 1 WARN"，并以退出码反映整体健康度：
#       有任何 FAIL -> 退出码 1；否则 0。
#
# 期望（健康部署后）输出: 9 PASS / 0 FAIL / 1 WARN
#   （9 PASS = 检查项 1~9；1 WARN = stale-dist 已知风险，见检查项 10）

set -uo pipefail

BACKEND="http://localhost:8800"
FRONTEND="http://localhost:8900"
DIST="ui-vben/apps/web-antd/dist/index.html"

PASS=0
FAIL=0
WARN=1   # stale-dist 始终作为 1 个已知风险项单列

# 记录一条结果: record <pass|fail> <label> <observed>
record() {
  local r="$1" label="$2" obs="$3"
  if [ "$r" = "pass" ]; then
    PASS=$((PASS + 1))
    printf '● PASS %s\n' "$label"
  else
    FAIL=$((FAIL + 1))
    printf '● FAIL %s\n' "$label"
  fi
  if [ -n "$obs" ]; then
    printf '    └─ 观测: %s\n' "$obs"
  fi
}

# 取 HTTP 状态码（超时 5s，连接失败记 000）
# 注意: 不使用 `|| echo 000`，因为 Git-Bash 下 curl 偶发非零退出但仍会打印正确状态码，
#       直接追加 000 会产生 "200000" 这类错误结果。
http_code() {
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$1" 2>/dev/null)
  [ -z "$code" ] && code="000"
  printf '%s' "$code"
}

echo "=========================================="
echo " pm-director Docker 环境健康基线复跑"
echo " 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo " 后端: $BACKEND   前端: $FRONTEND"
echo "=========================================="

# ---------------------------------------------------------------
# [1] 容器状态
# ---------------------------------------------------------------
echo ""
echo "[1] 容器状态 (pm-director-backend / pm-director-frontend 均 Up)"
UP=$(docker ps --filter name=pm-director --format '{{.Names}} {{.Status}}' 2>/dev/null)
echo "$UP" | sed 's/^/    /'
BE_UP=$(echo "$UP" | grep -c 'pm-director-backend.*Up' || true)
FE_UP=$(echo "$UP" | grep -c 'pm-director-frontend.*Up' || true)
if [ "$BE_UP" -ge 1 ] && [ "$FE_UP" -ge 1 ]; then
  record pass "[1] 容器状态" "backend_up=$BE_UP frontend_up=$FE_UP (期望均>=1)"
else
  record fail "[1] 容器状态" "backend_up=$BE_UP frontend_up=$FE_UP (期望均>=1)"
fi

# ---------------------------------------------------------------
# [2] 后端 GET /api/stats -> 200 + data 含 contract_count/total_amount
# ---------------------------------------------------------------
echo ""
echo "[2] 后端 GET /api/stats -> 200 + data 含 contract_count/total_amount"
C=$(http_code "$BACKEND/api/stats")
if [ "$C" = "200" ]; then
  OBS=$(curl -s --max-time 5 "$BACKEND/api/stats" | python3 -c \
    "import sys,json; d=json.load(sys.stdin)['data']; print('fields=%d contract_count=%s total_amount=%s' % (len(d), d.get('contract_count'), d.get('total_amount')))" 2>/dev/null)
  if echo "$OBS" | grep -q "contract_count"; then
    record pass "[2] /api/stats" "$OBS"
  else
    record fail "[2] /api/stats" "http=$C 但 data 结构异常: $OBS"
  fi
else
  record fail "[2] /api/stats" "http=$C (期望 200)"
fi

# ---------------------------------------------------------------
# [3] 后端 GET /health -> 200 JSON (P0 新增纯存活探针)
# ---------------------------------------------------------------
echo ""
echo "[3] 后端 GET /health -> 200 JSON (P0 新增纯存活探针)"
C=$(http_code "$BACKEND/health")
if [ "$C" = "200" ]; then
  OBS=$(curl -s --max-time 5 "$BACKEND/health" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print('status=%s service=%s keys=%s' % (d.get('status'), d.get('service'), sorted(d.keys())))" 2>/dev/null)
  if echo "$OBS" | grep -q "status=ok"; then
    record pass "[3] /health (backend)" "$OBS"
  else
    record fail "[3] /health (backend)" "http=$C body=$OBS"
  fi
else
  record fail "[3] /health (backend)" "http=$C (期望 200；若容器未重新部署 T1 则仍为 404，需 docker compose build backend && docker compose up -d backend)"
fi

# ---------------------------------------------------------------
# [4] 后端 GET /api/projects?page=1&size=1 -> 200, total=50, items[]
# ---------------------------------------------------------------
echo ""
echo "[4] 后端 GET /api/projects?page=1&size=1 -> 200, total=50, items[]"
C=$(http_code "$BACKEND/api/projects?page=1&size=1")
if [ "$C" = "200" ]; then
  OBS=$(curl -s --max-time 5 "$BACKEND/api/projects?page=1&size=1" | python3 -c \
    "import sys,json; d=json.load(sys.stdin)['data']; print('total=%s items=%d' % (d.get('total'), len(d.get('items', []))))" 2>/dev/null)
  if echo "$OBS" | grep -q "total=50"; then
    record pass "[4] /api/projects" "$OBS"
  else
    record fail "[4] /api/projects" "http=$C $OBS (期望 total=50)"
  fi
else
  record fail "[4] /api/projects" "http=$C (期望 200)"
fi

# ---------------------------------------------------------------
# [5] 后端 GET /api/contracts?page=1&size=1 -> 200, total=50, items[]
# ---------------------------------------------------------------
echo ""
echo "[5] 后端 GET /api/contracts?page=1&size=1 -> 200, total=50, items[]"
C=$(http_code "$BACKEND/api/contracts?page=1&size=1")
if [ "$C" = "200" ]; then
  OBS=$(curl -s --max-time 5 "$BACKEND/api/contracts?page=1&size=1" | python3 -c \
    "import sys,json; d=json.load(sys.stdin)['data']; print('total=%s items=%d' % (d.get('total'), len(d.get('items', []))))" 2>/dev/null)
  if echo "$OBS" | grep -q "total=50"; then
    record pass "[5] /api/contracts" "$OBS"
  else
    record fail "[5] /api/contracts" "http=$C $OBS (期望 total=50)"
  fi
else
  record fail "[5] /api/contracts" "http=$C (期望 200)"
fi

# ---------------------------------------------------------------
# [6] 前端 GET / -> 301 跳转 /web/
# ---------------------------------------------------------------
echo ""
echo "[6] 前端 GET / -> 301 跳转 /web/"
C=$(http_code "$FRONTEND/")
LOC=$(curl -s -D - -o /dev/null --max-time 5 "$FRONTEND/" 2>/dev/null | grep -i '^location:' | tr -d '\r' | awk '{print $2}')
if [ "$C" = "301" ] && echo "$LOC" | grep -q "/web/"; then
  record pass "[6] GET / 重定向" "http=$C -> $LOC"
else
  record fail "[6] GET / 重定向" "http=$C location=$LOC (期望 301 -> .../web/)"
fi

# ---------------------------------------------------------------
# [7] 前端 GET /web/ -> 200 (SPA 入口)
# ---------------------------------------------------------------
echo ""
echo "[7] 前端 GET /web/ -> 200 (SPA 入口)"
C=$(http_code "$FRONTEND/web/")
if [ "$C" = "200" ]; then
  record pass "[7] GET /web/" "http=$C"
else
  record fail "[7] GET /web/" "http=$C (期望 200)"
fi

# ---------------------------------------------------------------
# [8] 前端 GET /web/dashboard -> 200 (SPA fallback 深链)
# ---------------------------------------------------------------
echo ""
echo "[8] 前端 GET /web/dashboard -> 200 (SPA fallback 深链)"
C=$(http_code "$FRONTEND/web/dashboard")
if [ "$C" = "200" ]; then
  record pass "[8] GET /web/dashboard" "http=$C"
else
  record fail "[8] GET /web/dashboard" "http=$C (期望 200)"
fi

# ---------------------------------------------------------------
# [9] 前端 GET /health (nginx 8900) -> 200
# ---------------------------------------------------------------
echo ""
echo "[9] 前端 GET /health (nginx 8900) -> 200"
C=$(http_code "$FRONTEND/health")
if [ "$C" = "200" ]; then
  record pass "[9] GET /health (nginx)" "http=$C"
else
  record fail "[9] GET /health (nginx)" "http=$C (期望 200)"
fi

# ---------------------------------------------------------------
# [10] 静态产物 dist/index.html 存在 (+ stale-dist 风险 WARN)
# ---------------------------------------------------------------
echo ""
echo "[10] 静态产物 dist/index.html 存在 (+ stale-dist 风险 WARN)"
if [ -f "$DIST" ]; then
  MT=$(stat -c '%y' "$DIST" 2>/dev/null | cut -d. -f1)
  SZ=$(stat -c %s "$DIST" 2>/dev/null)
  printf '● WARN [10] 静态产物存在 (mtime=%s, %sB)\n' "$MT" "$SZ"
  echo "    └─ 观测: $DIST 当前存在，但 compose frontend 挂载宿主机 dist 卷、不自动构建；"
  echo "       若改动前端源码后未先 pnpm build 即重启容器，将服务旧产物（stale-dist）。"
  echo "       处置结论: 接受为已知风险，由 T2(部署/CI 强制 build+校验) 与 T10(compose 真正构建前端) 兜底跟踪，非源码缺陷。"
else
  FAIL=$((FAIL + 1))
  printf '● FAIL [10] 静态产物缺失\n'
  echo "    └─ 观测: $DIST 不存在；SPA 将无法加载，需先 pnpm build 产出 dist。"
  echo "    └─ WARN: 同上 stale-dist 风险（已知，非源码缺陷）。"
fi

# ---------------------------------------------------------------
# 汇总
# ---------------------------------------------------------------
echo ""
echo "=========================================="
echo " 汇总: $PASS PASS / $FAIL FAIL / $WARN WARN"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
  exit 1
else
  exit 0
fi
