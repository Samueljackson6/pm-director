#!/bin/bash
# ============================================
# pm-director 一键部署脚本 (236 服务器)
# 用法: bash scripts/deploy-236.sh [frontend|backend|all]
# ============================================

set -e

VBEN_DIR=/home/samuel/.openclaw/workspace/pm-director/ui-vben/apps/web-antd
PM_DIR=/home/samuel/.openclaw/workspace/pm-director

deploy_backend() {
  echo ">>> Deploying Backend..."
  cd $PM_DIR
  git pull origin master 2>/dev/null || echo "git pull skipped (not a git repo or no network)"
  
  # 复制 backend 文件 (如果本地有修改)
  # cp backend/main.py ... 
  
  pkill -f 'uvicorn backend.main' 2>/dev/null || true
  sleep 1
  nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8800 > /tmp/pm-backend.log 2>&1 &
  sleep 2
  
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8800/api/stats)
  echo "Backend: HTTP $STATUS"
  if [ "$STATUS" != "200" ]; then
    echo "ERROR: Backend failed to start!"
    tail -5 /tmp/pm-backend.log
    exit 1
  fi
}

deploy_frontend() {
  echo ">>> Deploying Frontend..."
  
  # Step 1: Sync custom UI code
  echo "Syncing UI files..."
  cp $PM_DIR/ui/src/api/*.ts $VBEN_DIR/src/api/
  cp $PM_DIR/ui/src/views/contracts/index.vue $VBEN_DIR/src/views/contracts/
  cp $PM_DIR/ui/src/views/contracts/detail.vue $VBEN_DIR/src/views/contracts/
  cp $PM_DIR/ui/src/views/invoices/index.vue $VBEN_DIR/src/views/invoices/
  cp $PM_DIR/ui/src/views/suppliers/index.vue $VBEN_DIR/src/views/suppliers/
  cp $PM_DIR/ui/src/router/routes/modules/*.ts $VBEN_DIR/src/router/routes/modules/
  
  # Step 2: Build
  echo "Building Vben..."
  cd $PM_DIR/ui-vben
  npx pnpm -F @vben/web-antd build
  if [ $? -ne 0 ]; then
    echo "ERROR: Frontend build failed!"
    exit 1
  fi
  
  # Step 3: Restart server
  echo "Restarting frontend server..."
  pkill -f 'http.server 5777' 2>/dev/null || true
  sleep 1
  nohup python3 -m http.server 5777 --bind 0.0.0.0 \
    --directory $VBEN_DIR/dist > /tmp/vben5777.log 2>&1 &
  sleep 2
  
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5777/)
  echo "Frontend: HTTP $STATUS"
  if [ "$STATUS" != "200" ]; then
    echo "ERROR: Frontend failed to start!"
    tail -5 /tmp/vben5777.log
    exit 1
  fi
}

verify() {
  echo ""
  echo "=== Verification ==="
  echo -n "Frontend: "; curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:5777/
  echo -n "Backend:  "; curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:8800/api/stats
  echo -n "Contracts JS: "; ls $VBEN_DIR/dist/js/contracts-*.js 2>/dev/null | wc -l | xargs -I{} echo "{} files"
  echo -n "Invoices JS:  "; ls $VBEN_DIR/dist/js/invoices-*.js 2>/dev/null | wc -l | xargs -I{} echo "{} files"
  echo -n "Suppliers JS: "; ls $VBEN_DIR/dist/js/suppliers-*.js 2>/dev/null | wc -l | xargs -I{} echo "{} files"
  echo "Build time: $(stat --format='%y' $VBEN_DIR/dist/index.html 2>/dev/null)"
}

case "${1:-all}" in
  backend)  deploy_backend; verify ;;
  frontend) deploy_frontend; verify ;;
  all)      deploy_backend; deploy_frontend; verify ;;
  verify)   verify ;;
  *)        echo "Usage: $0 [frontend|backend|all|verify]"; exit 1 ;;
esac

echo ">>> Deploy complete!"
