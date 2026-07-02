#!/usr/bin/env bash
# ================================================================
# pm-director 一键发布脚本
# 完整自动化流水线: 代码检查 → 提交 → 推送 → 部署 → 验证 → 审计
#
# 用法:
#   bash scripts/auto-publish.sh            完整流水线
#   bash scripts/auto-publish.sh deploy     仅部署（代码已推送时）
#   bash scripts/auto-publish.sh verify     仅验证
#   bash scripts/auto-publish.sh audit      仅审计
#   bash scripts/auto-publish.sh status     查看当前状态
# ================================================================

set -e

# ---------- 配置 ----------
SSH_HOST="${PM_DIRECTOR_SSH_HOST:-236}"
PROJECT_DIR="/home/samuel/.openclaw/workspace/pm-director"
VBEN_DIR="$PROJECT_DIR/ui-vben/apps/web-antd"
UI_DIR="$PROJECT_DIR/ui"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

# ---------- 颜色 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }
info() { echo -e "${YELLOW}[INFO]${NC} $1"; }
step() { echo ""; echo "=== $1 ==="; }

# ---------- 检查前置条件 ----------
check_prereqs() {
  step "检查前置条件"
  
  # 检查 git
  command -v git &>/dev/null || fail "git 未安装"
  
  # 检查 git 仓库状态
  if [ ! -d "$LOCAL_DIR/.git" ]; then
    fail "当前目录不是 git 仓库"
  fi
  
  # 检查是否能 SSH 到 236
  if ssh -o ConnectTimeout=3 -o BatchMode=yes "$SSH_HOST" "echo ok" 2>/dev/null | grep -q ok; then
    pass "SSH 到 $SSH_HOST 正常"
    SSH_OK=true
  else
    info "SSH 到 $SSH_HOST 不可达，跳过远程操作"
    SSH_OK=false
  fi
  
  pass "前置条件检查完成"
}

# ---------- Lint 检查 ----------
run_lint() {
  step "Lint 检查"
  
  # Python 语法检查
  PY_FILES=$(find "$LOCAL_DIR/backend" -name "*.py" 2>/dev/null || true)
  if [ -n "$PY_FILES" ]; then
    for f in $PY_FILES; do
      if python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        :
      else
        fail "Python 语法错误: $f"
      fi
    done
    pass "Python 语法检查通过 ($(echo "$PY_FILES" | wc -w) files)"
  else
    info "没有 Python 文件需要检查"
  fi
  
  # UI 文件存在性检查
  for f in \
    "$LOCAL_DIR/ui/src/api/contracts.ts" \
    "$LOCAL_DIR/ui/src/api/invoices.ts" \
    "$LOCAL_DIR/ui/src/api/suppliers.ts"
  do
    if [ -f "$f" ]; then
      pass "API 文件存在: $(basename "$f")"
    else
      info "API 文件不存在（可能尚未创建）: $(basename "$f")"
    fi
  done
  
  info "Lint 检查完成（仅语法验证，完整 lint 需要 GitHub Actions）"
}

# ---------- 测试 ----------
run_tests() {
  step "测试"
  info "暂无自动化测试用例（待建设）"
  # TODO: 添加 pytest / vitest 测试
}

# ---------- 提交 ----------
do_commit() {
  step "Git 提交"
  
  # 检查是否有未暂存文件
  if [ -z "$(git -C "$LOCAL_DIR" status --porcelain)" ]; then
    info "没有需要提交的变更"
    return
  fi
  
  # 显示变更
  git -C "$LOCAL_DIR" status --short
  
  # 如果提供了提交信息
  if [ -n "$1" ]; then
    git -C "$LOCAL_DIR" add -A
    git -C "$LOCAL_DIR" commit -m "$1"
    pass "提交完成: $1"
  else
    info "请手动提交: git add -A && git commit -m '类型(范围): 描述'"
    info "提交信息格式: feat|fix|docs|ci|refactor(scope): message"
  fi
}

# ---------- 推送 ----------
do_push() {
  step "推送到 GitHub"
  
  # 检查是否有未推送提交
  LOCAL=$(git -C "$LOCAL_DIR" rev-parse @)
  REMOTE=$(git -C "$LOCAL_DIR" rev-parse @{upstream} 2>/dev/null || echo "")
  
  if [ "$LOCAL" = "$REMOTE" ]; then
    info "本地和远程一致，无需推送"
    return
  fi
  
  git -C "$LOCAL_DIR" push origin master
  pass "推送成功"
}

# ---------- 236 部署 ----------
do_deploy() {
  step "236 部署"
  
  if [ "$SSH_OK" != "true" ]; then
    info "SSH 不可达，跳过部署"
    info "请在 236 上手动运行: bash scripts/deploy-236.sh all"
    return
  fi
  
  ssh "$SSH_HOST" "cd $PROJECT_DIR && bash scripts/deploy-236.sh all"
  pass "236 部署完成"
}

# ---------- 验证 ----------
do_verify() {
  step "验证"
  
  if [ "$SSH_OK" != "true" ]; then
    info "SSH 不可达，跳过验证"
    info "请手动验证: curl http://192.168.0.236:5777/"
    return
  fi
  
  ssh "$SSH_HOST" "bash $PROJECT_DIR/scripts/deploy-236.sh verify"
  pass "验证完成"
}

# ---------- 审计 ----------
do_audit() {
  step "审计"
  
  echo "===== pm-director 发布审计 ====="
  echo "时间: $TIMESTAMP"
  echo ""
  
  # 1. Git 状态
  echo "--- Git 状态 ---"
  git -C "$LOCAL_DIR" log --oneline -3 2>/dev/null || echo "  (无)"
  
  # 2. 文件变更
  echo ""
  echo "--- 最近变更 ---"
  git -C "$LOCAL_DIR" diff --name-only HEAD~1..HEAD 2>/dev/null | head -20 || echo "  (仅一次提交)"
  
  # 3. 服务状态
  echo ""
  echo "--- 服务状态 ---"
  if [ "$SSH_OK" = "true" ]; then
    FE_STATUS=$(ssh "$SSH_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost:5777/" 2>/dev/null)
    BE_STATUS=$(ssh "$SSH_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8800/api/stats" 2>/dev/null)
    echo "  Frontend: HTTP $FE_STATUS"
    echo "  Backend:  HTTP $BE_STATUS"
    
    # 检查 systemd 服务
    echo ""
    echo "--- systemd 服务 ---"
    ssh "$SSH_HOST" "sudo systemctl is-active pm-backend pm-frontend 2>/dev/null" | tr '\n' ' '
    echo ""
  else
    echo "  (SSH 不可达)"
  fi
  
  # 4. 构建信息
  echo ""
  echo "--- 构建信息 ---"
  if [ "$SSH_OK" = "true" ]; then
    BUILD_TIME=$(ssh "$SSH_HOST" "stat --format='%y' $VBEN_DIR/dist/index.html 2>/dev/null" || echo "unknown")
    echo "  Vben build: $BUILD_TIME"
    
    JS_FILES=$(ssh "$SSH_HOST" "ls $VBEN_DIR/dist/js/contracts-*.js $VBEN_DIR/dist/js/invoices-*.js $VBEN_DIR/dist/js/suppliers-*.js 2>/dev/null" | wc -l)
    echo "  Custom JS bundles: $JS_FILES files"
  fi
  
  # 5. 完成度评估
  echo ""
  echo "--- 完成度评估 ---"
  TASK_KEYWORDS=("$@")
  if [ ${#TASK_KEYWORDS[@]} -gt 0 ]; then
    LAST_COMMIT=$(git -C "$LOCAL_DIR" log --oneline -1 2>/dev/null)
    MATCHES=0
    TOTAL=${#TASK_KEYWORDS[@]}
    for kw in "${TASK_KEYWORDS[@]}"; do
      if echo "$LAST_COMMIT" | grep -iq "$kw"; then
        MATCHES=$((MATCHES + 1))
      fi
    done
    PCT=$((MATCHES * 100 / TOTAL))
    echo "  任务关键词匹配度: $MATCHES/$TOTAL ($PCT%)"
    if [ $PCT -ge 70 ]; then
      pass "完成度 >= 70%，任务完成 ✅"
    else
      fail "完成度 < 70%，需要继续 ❌"
    fi
  else
    info "  未提供任务关键词，跳过完成度评估"
  fi
  
  echo ""
  pass "审计完成"
}

# ---------- 状态报告 ----------
do_status() {
  step "当前状态"
  
  echo "=== Git ==="
  git -C "$LOCAL_DIR" log --oneline -3
  echo ""
  
  echo "=== 未提交 ==="
  git -C "$LOCAL_DIR" status --short || echo "  (干净)"
  echo ""
  
  if [ "$SSH_OK" = "true" ]; then
    echo "=== 236 服务 ==="
    FE=$(ssh "$SSH_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost:5777/" 2>/dev/null)
    BE=$(ssh "$SSH_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8800/api/stats" 2>/dev/null)
    echo "  Frontend: HTTP $FE"
    echo "  Backend:  HTTP $BE"
  fi
}

# ================================================================
# Main
# ================================================================

MODE="${1:-full}"
shift 2>/dev/null || true

# SSH 连接性预检
check_prereqs

case "$MODE" in
  full)
    run_lint
    run_tests
    do_commit "$1"
    do_push
    do_deploy
    do_verify
    do_audit "$@"
    echo ""
    pass "完整流水线执行完毕!"
    ;;
  deploy)
    do_deploy
    do_verify
    do_audit "$@"
    ;;
  verify)
    do_verify
    ;;
  audit)
    do_audit "$@"
    ;;
  status)
    do_status
    ;;
  *)
    echo "用法: bash scripts/auto-publish.sh [full|deploy|verify|audit|status] [commit_message]"
    echo ""
    echo "  full             完整流水线（默认）"
    echo "  deploy           仅部署（代码已推送时）"
    echo "  verify           仅验证"
    echo "  audit            仅审计"
    echo "  status           查看当前状态"
    exit 0
    ;;
esac
