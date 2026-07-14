#!/bin/bash
# ============================================================
# 退役 236 老环境 + frp 改指 8900
# 对应 Issue: T11, T12
# ============================================================

set -e

echo "=== 236 老环境退役脚本 ==="
echo ""

# 1. 检查 Docker 服务状态
echo "1. 检查 Docker 服务状态..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep pm-director || echo "  Docker 容器未运行"

# 2. 停止老 systemd 服务
echo ""
echo "2. 停止老 systemd 服务..."
if systemctl --user is-active pm-backend 2>/dev/null; then
    echo "  停止 pm-backend..."
    systemctl --user stop pm-backend
    systemctl --user disable pm-backend
else
    echo "  pm-backend 服务不存在或已停止"
fi

if systemctl --user is-active pm-frontend 2>/dev/null; then
    echo "  停止 pm-frontend..."
    systemctl --user stop pm-frontend
    systemctl --user disable pm-frontend
else
    echo "  pm-frontend 服务不存在或已停止"
fi

# 3. 验证端口 5777 不再监听
echo ""
echo "3. 验证端口 5777 不再监听..."
if ss -tlnp | grep -q ":5777"; then
    echo "  ⚠️ 端口 5777 仍在监听，请手动检查"
else
    echo "  ✅ 端口 5777 已释放"
fi

# 4. 验证端口 8900 (Docker 前端)
echo ""
echo "4. 验证端口 8900 (Docker 前端)..."
if ss -tlnp | grep -q ":8900"; then
    echo "  ✅ 端口 8900 正在监听"
else
    echo "  ⚠️ 端口 8900 未监听，请确保 Docker 容器已启动"
fi

# 5. 更新 frp 配置
echo ""
echo "5. 更新 frp 配置..."
FRP_CONF="/home/samuel/frp/frpc.ini"
if [ -f "$FRP_CONF" ]; then
    # 备份原配置
    cp "$FRP_CONF" "${FRP_CONF}.bak.$(date +%Y%m%d%H%M%S)"

    # 检查是否需要更新
    if grep -q "local_port = 5777" "$FRP_CONF"; then
        echo "  更新 frp 配置：5777 → 8900"
        sed -i 's/local_port = 5777/local_port = 8900/g' "$FRP_CONF"

        # 重启 frp
        echo "  重启 frp 服务..."
        pkill -HUP frpc || echo "  frpc 未运行，跳过"
    else
        echo "  frp 配置已更新或无需更新"
    fi
else
    echo "  ⚠️ frp 配置文件不存在: $FRP_CONF"
fi

# 6. 验证公网访问
echo ""
echo "6. 验证公网访问..."
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://47.98.184.188:15777/web/ || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✅ 公网访问正常 (HTTP $HTTP_CODE)"
else
    echo "  ⚠️ 公网访问异常 (HTTP $HTTP_CODE)"
fi

# 7. 清理旧依赖（可选）
echo ""
echo "7. 清理旧依赖（可选）..."
echo "  如需删除 ruoyi-office-vben 目录，请手动执行："
echo "  rm -rf /home/samuel/ruoyi-office-vben"

echo ""
echo "=== 退役完成 ==="
echo "验证清单："
echo "  - [ ] 老 systemd 服务已停止"
echo "  - [ ] 端口 5777 已释放"
echo "  - [ ] 端口 8900 正在监听"
echo "  - [ ] frp 已指向 8900"
echo "  - [ ] 公网访问正常"
