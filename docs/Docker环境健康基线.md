# Docker 环境健康基线（固化）

> 生成日期：2026-07-07
> 适用范围：本地 `docker-compose` 开发测试环境（**非** 236 老环境）
> 关联任务：T3（固化并归档 Docker 环境健康基线）｜关联 Issue #3

## 1. 目的

固化本地 Docker 开发测试环境的**健康探针定义**与**预期基线值**，作为：

- CI（`ci.yml`）与部署脚本（`deploy-docker.sh`）验证步骤的判定基准；
- 后续回归检测 / 环境漂移排查的对照表；
- 新成员一键自检环境的依据。

## 2. 服务清单与端口

| 服务 | 容器名 | 构建方式 | 宿主机端口 | 容器内端口 | 状态预期 |
|------|--------|----------|-----------|-----------|---------|
| backend  | `pm-director-backend`  | `build:` Dockerfile `target=backend`（python:3.11-slim） | 8800 | 8800 | Up |
| frontend | `pm-director-frontend` | `nginx:alpine`（挂载宿主机 `dist`）                      | 8900 | 80   | Up |

> ⚠️ **关键点**：backend 服务是**打镜像**（`build:`），仅 `./database` 与 `./cache` 以卷挂载。
> 因此**修改 `backend/` 源码后必须 `docker compose build backend` 重建镜像并重启容器**，否则运行中的容器仍是旧代码。
> （本次 T1 `/health` 端点就曾因未重建，导致 `curl /health` 返回 `{"detail":"Not Found"}`。）

## 3. 健康探针（Probes）

### 3.1 后端存活探针

- **端点**：`GET /health` 与 `GET /api/health`（两者等价）
- **预期响应**：`200 OK`，body：

  ```json
  {
    "status": "ok",
    "service": "pm-director",
    "timestamp": "<UTC ISO8601>",
    "version": "0.1.0"
  }
  ```

- **特性**：纯存活检测，**不依赖数据库**，可用于基础设施存活判定与 compose healthcheck。
- **compose healthcheck 实现**（规避基础镜像无 `curl`）：

  ```yaml
  test: ["CMD","python","-c","import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8800/health').status == 200 else 1)"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 10s
  ```

### 3.2 前端可用性探针

- **端点**：`GET http://localhost:8900/web/`
- **预期**：`200`，返回 `index.html`（SPA 入口）
- **说明**：前端以 `/web/` 子路径托管，nginx 根指向构建产物 `dist`。

## 4. 依赖与约束

- 后端基础镜像 `python:3.11-slim` **默认无 `curl`** → healthcheck 必须用 `python` 实现。
- 前端 `nginx:alpine`。
- 数据卷：`./database`、`./cache` 挂载进 backend（SQLite 与缓存持久化）。
- 源码变更 → **rebuild 镜像**才生效（backend 非源码挂载）。

## 5. 验证脚本

- `scripts/verify-env.sh`：一键检测上述全部探针，输出 `PASS/FAIL` 汇总。
- 用法：

  ```bash
  bash scripts/verify-env.sh
  ```

## 6. 已知限制 / WARN

- **236 老环境**（端口 5777 / `systemd --user` + 外部 `ruoyi-office-vben` JS fork）待退役，**不纳入本基线**（见 T11）。
- **jiti 构建缺陷**（T7）可能影响前端 `pnpm build`，导致 stale-dist；CI 已加产物时间戳校验缓解（见 T2 / T10）。

## 7. 实际基线记录（2026-07-07 实测）

> 验证方式：重建 backend 镜像（`docker compose build backend`）+ 重启容器后，运行 `bash scripts/verify-env.sh`。
> 汇总：**9 PASS / 0 FAIL / 1 WARN**（WARN 为 stale-dist 已知风险，由 T2/T10 兜底）。

| 探针 | 实测结果 | 时间 |
|------|---------|------|
| `GET /health`        | ✅ PASS — `{"status":"ok","service":"pm-director","version":"0.1.0",...}` | 2026-07-07 16:29 |
| `GET /api/health`    | ✅ PASS — 与 `/health` 等价（同一 handler） | 2026-07-07 16:29 |
| `GET /web/`（前端）  | ✅ PASS — `HTTP 200`（SPA 入口） | 2026-07-07 16:29 |

### 7.1 全量探针实测明细（verify-env.sh）

| # | 探针 | 结果 | 观测 |
|---|------|------|------|
| 1 | 容器状态 backend/frontend 均 Up | PASS | backend_up=1 frontend_up=1 |
| 2 | `GET /api/stats` → 200 + contract_count/total_amount | PASS | fields=10, contract_count=50, total_amount=2364.79 |
| 3 | `GET /health` → 200 JSON（P0 纯存活探针） | PASS | status=ok, keys=[service,status,timestamp,version] |
| 4 | `GET /api/projects?page=1&size=1` → 200, total=50 | PASS | total=50, items=1 |
| 5 | `GET /api/contracts?page=1&size=1` → 200, total=50 | PASS | total=50, items=1 |
| 6 | `GET /` → 301 跳转 `/web/` | PASS | http=301 → /web/ |
| 7 | `GET /web/` → 200（SPA 入口） | PASS | http=200 |
| 8 | `GET /web/dashboard` → 200（SPA fallback 深链） | PASS | http=200 |
| 9 | `GET /health`（nginx 8900）→ 200 | PASS | http=200 |
| 10 | 静态产物 dist/index.html 存在 | WARN | mtime=2026-07-06 17:59:52，stale-dist 已知风险（T2/T10 兜底） |
