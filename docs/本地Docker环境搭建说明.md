# 本地 Docker 开发测试环境搭建说明

> 更新日期: 2026-07-05
> 参考文档:
> - Docker 官方安装文档: https://docs.docker.com/desktop/setup/install/windows-install/
> - WSL 官方安装文档: https://learn.microsoft.com/en-us/windows/wsl/install
> - Vben Admin 官方构建文档: https://doc.vben.pro/guide/deploy

---

## 一、环境概要

### 1.1 组件版本

| 组件 | 版本 | 路径 |
|------|------|------|
| Docker Desktop | 4.80.0 | D:\\Docker |
| Docker Engine | 29.6.1 | WSL2 内运行 |
| WSL 2 | 最新 | Docker Desktop 内置管理 |
| Python | 3.11-slim | 后端容器镜像 |
| Node.js | 20-alpine | 前端构建镜像 |
| Nginx | alpine | 前端服务镜像 |

### 1.2 存储位置

| 内容 | 路径 | 说明 |
|------|------|------|
| Docker 程序 | D:\\Docker | --installation-dir=D:\\Docker |
| Docker WSL 数据 | D:\\Docker\\data | --wsl-default-data-root=D:\\Docker\\data |
| Docker 配置 | %USERPROFILE%\\.docker\\daemon.json | registry-mirrors 配置 |
| 项目代码 | D:\\Tare-workspace\\pm-director | 本仓库 |

---

## 二、安装步骤

### 2.1 下载安装器

```powershell
# 从 Docker 官方下载（备用 URL 在国内可用）
curl.exe -L -o D:\Docker\installer\Docker-Desktop-installer.exe `
  "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
```

注意: 主 URL `https://desktop.docker.com/win/stable/...` 在国内 SSL 握手会失败，
备用 URL (main 通道) 可以正常下载。

### 2.2 安装到 D 盘

```powershell
# 安装到 D 盘并指定 WSL 数据目录
& "D:\Docker\installer\Docker-Desktop-installer.exe" install `
  --accept-license `
  --installation-dir=D:\Docker `
  --wsl-default-data-root=D:\Docker\data
```

### 2.3 配置国内镜像源

配置文件: `%USERPROFILE%\.docker\daemon.json`

```json
{
  "registry-mirrors": ["https://docker.m.daocloud.io"]
}
```

### 2.4 手动拉取基础镜像（国内网络）

```powershell
# 通过 DaoCloud 代理拉取
docker pull docker.m.daocloud.io/library/python:3.11-slim
docker pull docker.m.daocloud.io/library/node:20-alpine
docker pull docker.m.daocloud.io/library/nginx:alpine

# 重新打标签
docker tag docker.m.daocloud.io/library/python:3.11-slim python:3.11-slim
docker tag docker.m.daocloud.io/library/node:20-alpine node:20-alpine
docker tag docker.m.daocloud.io/library/nginx:alpine nginx:alpine
```

---

## 三、构建与运行

### 3.1 构建镜像

```powershell
cd D:\Tare-workspace\pm-director
docker compose build
```

### 3.2 启动服务

```powershell
docker compose up -d
```

### 3.3 验证

```powershell
# 后端 API
curl http://localhost:8800/api/stats

# 前端页面（需要前端构建成功）
curl http://localhost:5777/web/
```

---

## 四、已知问题

### 4.1 前端 Vben Admin 构建

前端构建因 `ui-vben/` 目录中部分源码不完整而失败（这是仓库快照问题，非 Docker 环境问题）。

具体表现:
1. `@vben-core/shared` 缺少 `src/cache/index.ts`（已手动创建）
2. `unbuild --stub` 在未配 `stub` 脚本的包上不执行
3. 运行 `unbuild` 时 Alpine 包管理器 `apk` 被 GFW 阻断（已改为 `node` 替代 `jq`）
4. Vite 构建时 `@vben/common-ui/es/loading` 等子路径不存在

### 4.2 解决方案

前端构建失败不影响后端服务运行。如需开发前端，建议在本地直接运行
(Windows 上安装 Node.js 20+ 和 pnpm 后执行 `pnpm dev`)。

### 4.3 国内网络限制

| 资源 | 状态 | 解决方案 |
|------|------|----------|
| registry-1.docker.io | ❌ 阻断 | 配置 docker.m.daocloud.io 镜像 |
| dl-cdn.alpinelinux.org | ❌ 阻断 | 用 node 替代 apk 安装 jq |
| Docker 官网 | ❌ 阻断 | 使用 main 通道的 CDN URL |
| npmjs.org | ✅ 正常 | pnpm install 可直接使用 |

---

## 五、目录结构

```
D:\Docker\
├── data\                # WSL2 数据磁盘 (VHDX 文件)
│   ├── disk\            # docker_data.vhdx
│   └── main\            # ext4.vhdx
├── installer\           # Docker Desktop 安装器
├── frontend\            # Docker Desktop UI 前端
├── resources\           # Docker CLI 等资源
│   └── bin\             # docker.exe, docker-compose.exe
├── Docker Desktop.exe
├── DockerCli.exe
├── com.docker.service
└── ... (其他运行时文件)
```
