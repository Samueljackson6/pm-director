# 本地 Docker 开发测试环境搭建说明

> 更新：2026-07-07（v2 修订：对齐真实 `docker-compose.yml`——前端 `:8900` → `/web/`，并补全前端 dist 构建步骤与 jiti 处理说明）
> 参考文档：
> - Docker 官方安装文档
> - WSL 官方安装文档
> - Vben Admin 官方构建文档：https://doc.vben.pro/guide/deploy

---

## 一、环境概要

### 1.1 组件版本

| 组件 | 版本 | 路径/说明 |
|------|------|----------|
| Docker Desktop | 4.80.0 | WSL2 内运行 |
| Docker Engine | 29.6.1 | |
| Python | 3.11-slim | 后端容器镜像（`Dockerfile`） |
| Node.js | 20-alpine / 22-alpine | 前端构建镜像（`Dockerfile.frontend`） |
| Nginx | alpine | 前端服务镜像（compose `frontend` 服务） |

### 1.2 一句话结论

**本地开发/测试环境在 Docker 中**：`docker compose` 启动后端容器（8800）与前端 nginx 容器（8900 → `/web/`）。

> 改业务代码时可用 `pnpm dev` 热更新；但**联调/自测的基准环境是 Docker**。

---

## 二、安装步骤（Windows）

### 2.1 安装到 D 盘

```powershell
& "D:\Docker\installer\Docker-Desktop-installer.exe" install `
  --accept-license --installation-dir=D:\Docker `
  --wsl-default-data-root=D:\Docker\data
```

### 2.2 配置国内镜像源

`%USERPROFILE%\.docker\daemon.json`：
```json
{ "registry-mirrors": ["https://docker.m.daocloud.io"] }
```

### 2.3 手动拉取基础镜像（国内网络）

```powershell
docker pull docker.m.daocloud.io/library/python:3.11-slim
docker pull docker.m.daocloud.io/library/node:20-alpine
docker pull docker.m.daocloud.io/library/nginx:alpine
docker tag docker.m.daocloud.io/library/python:3.11-slim python:3.11-slim
docker tag docker.m.daocloud.io/library/node:20-alpine node:20-alpine
docker tag docker.m.daocloud.io/library/nginx:alpine nginx:alpine
```

---

## 三、构建与运行（重点）

### 3.1 关键前提：前端 dist 必须先构建

`docker-compose.yml` 的 `frontend` 服务是 `nginx:alpine` + 挂载宿主 `./ui-vben/apps/web-antd/dist`，**自身不构建前端**。所以启动前必须先把前端产物准备好（二选一）：

**方式一：宿主构建（推荐，最快）**
```powershell
cd D:\Tare-workspace\pm-director\ui-vben
corepack enable && corepack prepare pnpm@10 --activate
pnpm install
cd apps\web-antd
pnpm build                      # 产物 → ui-vben/apps/web-antd/dist
```
> 构建时 `ui/` 的业务代码（api/views/router）+ `.env*` 会被 `Dockerfile.frontend` 的 COPY 逻辑合并进 web-antd；宿主构建需确保你的 `ui/.env*` 与 `ui/src` 已就位。

**方式二：全镜像构建（含 jiti 补丁）**
```powershell
# 手动用 Dockerfile.frontend 打出带 dist 的镜像（已用 esbuild + 后处理解决 jiti 内联问题）
docker build -f Dockerfile.frontend -t pm-director-frontend .
# 若要让 compose 直接用此镜像，需把 docker-compose.yml 的 frontend 服务改为 build: { dockerfile: Dockerfile.frontend }
```

### 3.2 启动服务

```powershell
cd D:\Tare-workspace\pm-director
docker compose build        # 当前仅重建 backend（frontend 用外部 nginx 镜像 + 宿主 dist 卷）
docker compose up -d
```

### 3.3 验证（修正：前端在 8900 / `/web/`，不是 5777）

```powershell
# 后端 API
curl http://localhost:8800/api/stats

# 前端页面（注意：端口 8900，路径 /web/；直接访问根路径 / 会 301 到 /web/）
curl http://localhost:8900/web/
```

---

## 四、已知问题与解决

### 4.1 前端 jiti 构建问题（Docker 路径已解决）

`@vben/vite-config` 会把 `jiti`（Node 构建工具）内联进浏览器 bundle，SPA 初始化 `createJiti()` 会报错。
- **Docker 全镜像构建**（`Dockerfile.frontend`）：已用 esbuild 编译 vite-config + Python 后处理把 `createJiti` 调用替换为安全桩，构建产物可正常运行。
- **宿主 `pnpm build`**：若遇 jiti 问题，可用 `Dockerfile.frontend` 的镜像构建路径，或参考 Vben 官方 Issue #5634/#6959（清理依赖重装 / resolve.alias 映射 node:* 桩文件 / 降级 Vite 到 7.1.10）。
- **`pnpm dev` 开发模式**：天然绕过该问题。

### 4.2 国内网络限制

| 资源 | 状态 | 解决方案 |
|------|------|----------|
| registry-1.docker.io | ❌ 阻断 | 配置 `docker.m.daocloud.io` 镜像 |
| dl-cdn.alpinelinux.org | ❌ 阻断 | 构建脚本已用 `node` 替代 `apk` 安装 jq |
| npmjs.org | ✅ 正常 | `pnpm install` 可直接使用 |

---

## 五、目录结构（Docker 相关）

```
pm-director/
├── docker-compose.yml        # 后端(8800) + 前端 nginx(8900→/web/)
├── Dockerfile                # 后端：python:3.11-slim + uvicorn
├── Dockerfile.frontend       # 前端：node:22-alpine 构建 web-antd（含 jiti 补丁）→ nginx
├── nginx.conf                # 前端容器内的反向代理 + /web/ 路由
├── ui-vben/                  # Vben 框架（仓库内，生产框架来源）
│   └── apps/web-antd/        # 生产前端 app，构建产物 dist/ 被 compose 挂载
├── ui/                       # 业务代码 overlay（api/views/router + .env*）
└── database/                 # SQLite 文件（compose 以卷挂载）
```
