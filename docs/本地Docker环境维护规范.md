# 本地 Docker 开发测试环境维护规范

> 生效日期: 2026-07-08
> 所有开发人员/Agent 必须遵循本规范进行环境维护

---

## 1. 开发交付流程（强制）

### 1.1 每个开发任务的完整生命周期

```
需求 → 开发 → 代码审查 → 本地环境验证 → Playwright测试 → 汇报 → 确认提交 → PR合并 → CI部署
```

每个环节**不可跳过**，必须依次执行。

### 1.2 代码审查（Code Review）
- 所有代码变更（新增/修改/删除）必须经过审查
- 审查要点：是否遵循 Vben 框架规则（`docs/vben-framework-rules.md`）
- 审查要点：是否修改了正确的文件（backend auth.py vs frontend module）
- 审查通过后方可进入下一步

### 1.3 本地环境验证（Dev/Test Environment）

**必须在本地 Docker 环境验证**（`http://localhost:8900/web/`），验证内容包括：

```bash
# 1. 后端修改后重建镜像
docker compose build backend && docker compose up -d backend

# 2. 检查容器健康
docker ps  # 确认 backend healthy, frontend up

# 3. 验证后端 API
curl -s http://localhost:8800/api/dashboard/overview | head -c 100
curl -s http://localhost:8800/health

# 4. 前端修改后重建dist
cd ui-vben/apps/web-antd && pnpm build

# 5. 验证前端可访问
curl -s -o /dev/null -w "%{http_code}" http://localhost:8900/web/
```

### 1.4 Playwright 模拟用户测试

所有功能变更必须用 Playwright 模拟真实用户操作验证：

```bash
cd .devtest && PLAYWRIGHT_BROWSERS_PATH=D:/DevCache/ms-playwright \
  node playwright-t9.mjs
```

测试必须覆盖：
- 登录流程（mock auth 账号 admin/admin123）
- 受影响页面的核心功能（列表加载、点击跳转、数据展示）
- 菜单导航和路由跳转
- 0 控制台错误

**测试未通过 = 任务未完成**，必须修复后重新测试。

### 1.5 汇报与提交

全部验证通过后，向用户汇报：
1. 做了什么
2. 验证结果（多少 PASS / 多少 FAIL）
3. Playwright 测试摘要
4. **询问是否提交 GitHub PR**，不得自行推送

### 1.6 PR 合并与 CI 部署

- 用户确认后，创建 PR 到 `main` 分支
- 等待 CI 门禁全部通过（pytest + vitest + lint）
- CI 自动部署到 236 生产环境（GitHub Actions workflow）
- 确认部署成功，关闭对应 Issue

---

## 2. Docker 环境维护

### 2.1 磁盘空间分析

```bash
# 查看 Docker 磁盘使用情况
docker system df

# 查看所有镜像
docker images

# 查看所有容器（含已停止）
docker ps -a
```

### 2.2 定期清理（每周执行）

```bash
# 1. 清理构建缓存
docker builder prune --all --force

# 2. 清理未使用的镜像
docker image prune --all --force

# 3. 完整清理（谨慎：会删除所有停止的容器和未使用的网络）
docker system prune --all --volumes --force
```

### 2.3 Docker Desktop VHDX 压缩（每月执行）

Docker Desktop 的虚拟磁盘文件（VHDX）不会自动缩小。删除容器/镜像后磁盘空间不会立即释放。

**压缩步骤：**

```powershell
# 1. 完整清理
docker system prune --all --volumes --force

# 2. 退出 Docker Desktop（右下角托盘 → 退出）

# 3. 以管理员身份打开 PowerShell，运行：
Optimize-VHD -Path "D:\Docker\DockerDesktopWSL\data\ext4.vhdx" -Mode Full

# 4. 重新启动 Docker Desktop
```

> ⚠️ `Optimize-VHD` 命令需要 Hyper-V 管理工具，Windows 10/11 专业版/企业版可用。
> 家庭版用户可以手动删除 `D:\Docker` 目录后重新安装 Docker Desktop。

### 2.4 缓存目录清理

```bash
# pnpm 缓存（保留最近版本）
pnpm store prune

# npm 缓存（如果存在）
npm cache clean --force

# 项目临时文件
rm -rf ui-vben/apps/web-antd/dist
```

### 2.5 空间告警阈值

| 级别 | 可用空间 | 动作 |
|------|---------|------|
| 🟢 正常 | > 50GB | 无需操作 |
| 🟡 注意 | 20-50GB | 执行构建缓存清理 |
| 🟠 警告 | 10-20GB | 执行完整清理 + 检查大文件 |
| 🔴 紧急 | < 10GB | 执行 VHDX 压缩 + 深度清理 |

---

## 3. 日常操作命令速查

```bash
# === 启动/停止 ===
docker compose up -d           # 启动所有服务
docker compose up -d backend   # 仅重启后端
docker compose down            # 停止所有服务

# === 构建 ===
docker compose build backend   # 重建后端镜像
cd ui-vben/apps/web-antd && pnpm build  # 构建前端

# === 检查 ===
docker ps                       # 容器状态
docker logs pm-director-backend # 后端日志
curl http://localhost:8800/health  # 健康检查

# === 测试 ===
cd ui-vben/apps/web-antd && pnpm vitest run    # 单元测试
cd .devtest && node playwright-t9.mjs           # 功能测试

# === 清理 ===
docker builder prune --all --force   # 清理构建缓存
```

---

## 4. 禁止行为

- ❌ 跳过 Playwright 测试直接汇报"完成"
- ❌ 未在本地 Docker 环境验证直接提交 PR
- ❌ 在 Docker 容器运行状态下直接修改 `backend/` 源码不 rebuild（后端是镜像构建，源码不挂载）
- ❌ `docker compose down` 不加服务名（会停掉所有共享容器）
- ❌ 长时间保留大量构建缓存不清理
- ❌ Docker 磁盘空间告警后仍无视继续构建
