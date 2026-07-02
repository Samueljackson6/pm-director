#!/bin/bash
# pm-director systemd 服务安装脚本
# 用法: bash systemd/install.sh
# 注意: 需要 sudo 权限，会提示输入密码

set -e

echo "=== pm-director systemd 服务安装 ==="
echo ""

# 复制 service 文件
echo "1. 复制 service 文件到 /etc/systemd/system/ ..."
sudo cp "$(dirname "$0")/pm-backend.service" /etc/systemd/system/
sudo cp "$(dirname "$0")/pm-frontend.service" /etc/systemd/system/

# 重载 systemd
echo "2. 重载 systemd 配置 ..."
sudo systemctl daemon-reload

# 启用服务
echo "3. 启用服务（开机自启）..."
sudo systemctl enable pm-backend
sudo systemctl enable pm-frontend

# 停止旧进程
echo "4. 停止旧进程 ..."
pkill -f 'http.server 5777' 2>/dev/null || true
pkill -f 'uvicorn backend.main' 2>/dev/null || true
sleep 1

# 启动服务
echo "5. 启动 systemd 服务 ..."
sudo systemctl restart pm-backend
sudo systemctl restart pm-frontend

# 等待启动
sleep 3

# 验证
echo ""
echo "=== 验证 ==="
sudo systemctl status pm-backend --no-pager | head -5
echo "---"
sudo systemctl status pm-frontend --no-pager | head -5
echo ""
echo -n "Frontend: "; curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:5777/
echo -n "Backend:  "; curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:8800/api/stats

echo ""
echo "=== 安装完成 ==="
echo "管理命令:"
echo "  sudo systemctl status pm-backend"
echo "  sudo systemctl restart pm-backend"
echo "  sudo journalctl -u pm-backend -f"
echo ""
echo "  sudo systemctl status pm-frontend"
echo "  sudo systemctl restart pm-frontend"
echo "  sudo journalctl -u pm-frontend -f"
