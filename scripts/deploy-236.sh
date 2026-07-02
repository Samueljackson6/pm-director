#!/bin/bash
# ============================================
# pm-director 一键部署脚本 (236 服务器)
# 用法: bash scripts/deploy-236.sh [frontend|backend|all|verify]
# ============================================

set -e

export PATH="$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"

VBEN_DIR=/home/samuel/ruoyi-office-vben/apps/web-antd
PM_DIR=/home/samuel/.openclaw/workspace/pm-director

deploy_backend() {
  echo ">>> Deploying Backend..."
  cd $PM_DIR
  git fetch origin master
  git reset --hard origin/master

  systemctl --user restart pm-backend
  sleep 3

  STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8800/api/stats)
  echo "Backend: HTTP $STATUS"
  if [ "$STATUS" != "200" ]; then
    echo "ERROR: Backend failed to start!"
    journalctl --user -u pm-backend -n 10 --no-pager
    exit 1
  fi
}

deploy_frontend() {
  echo ">>> Deploying Frontend..."

  # Step 1: Sync custom UI code
  echo "Syncing UI files..."
  mkdir -p $VBEN_DIR/src/views/{contracts,invoices,suppliers,dashboard}
  cp $PM_DIR/ui/src/api/*.ts $VBEN_DIR/src/api/
  cp $PM_DIR/ui/src/views/contracts/index.vue $VBEN_DIR/src/views/contracts/
  cp $PM_DIR/ui/src/views/contracts/detail.vue $VBEN_DIR/src/views/contracts/
  cp $PM_DIR/ui/src/views/invoices/index.vue $VBEN_DIR/src/views/invoices/
  cp $PM_DIR/ui/src/views/suppliers/index.vue $VBEN_DIR/src/views/suppliers/
  cp $PM_DIR/ui/src/views/dashboard/index.vue $VBEN_DIR/src/views/dashboard/
  cp $PM_DIR/ui/src/router/routes/modules/*.ts $VBEN_DIR/src/router/routes/modules/

  # Step 2: Build
  echo "Building Vben..."
  cd /home/samuel/ruoyi-office-vben
  pnpm -F @vben/web-antd build
  if [ $? -ne 0 ]; then
    echo "ERROR: Frontend build failed!"
    exit 1
  fi

  # Step 3: Restart server
  echo "Restarting frontend server..."
  systemctl --user restart pm-frontend
  sleep 3

  STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5777/)
  echo "Frontend: HTTP $STATUS"
  if [ "$STATUS" != "200" ]; then
    echo "ERROR: Frontend failed to start!"
    journalctl --user -u pm-frontend -n 10 --no-pager
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
