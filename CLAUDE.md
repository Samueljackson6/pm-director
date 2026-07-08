# pm-director — 项目开发指南

> 本文件是 Claude Code / Cursor 等 IDE Agent 的**项目入口文档**。
> 任何 Agent 加入本项目协作时，必须先阅读以下内容。

---

## 关键文档索引（按优先级）

| 优先级 | 文档 | 内容 |
|--------|------|------|
| ⭐ P0 | `docs/vben-framework-rules.md` | **Vben Admin 5 框架开发规则** — 所有前端开发必须遵循 |
| ⭐ P0 | `RULES.md` | 项目核心规则（跨项目协议、Vben 规则摘要） |
| ⭐ P0 | `AGENTS.md` | Session 启动流程、任务前查询规范 |
| 🔹 P1 | `WORKFLOW.md` | 开发工作流、环境说明 |
| 🔹 P1 | `docs/部署规范.md` | 部署规范（本地 Docker + 236 生产） |
| 🔹 P1 | `docs/本地Docker环境搭建说明.md` | Docker 环境搭建 |
| 🔹 P1 | `docs/Docker环境健康基线.md` | 环境健康检查基线 |

### 关于本项目

- **项目**: 国网合同管理系统 (pm-director)
- **前端**: Vben Admin 5 (Vue3 + Vite7 + Tailwind CSS + Ant Design Vue)
- **后端**: Python FastAPI + SQLite
- **主应用**: `ui-vben/apps/web-antd`
- **本地测试**: `http://localhost:8900/web/` (backend :8800)
- **访问地址**: `http://localhost:8900/` → 登录 → 默认首页为财务仪表盘

---

## Vben 框架核心规则（快速参考）

> 详细版见 `docs/vben-framework-rules.md`

### 路由与菜单
- 本项目使用 **`accessMode: 'backend'`**，路由由后端 API (`backend/routers/auth.py`) 控制
- 新增页面 = ① 在 `views/` 下建 `.vue` 文件 + ② 在 `auth.py` 的 `menus` 中添加菜单项
- 默认首页通过 `auth.py` 的 `user.homePath` 设置

### 组件开发
- **VxeTable**: 从 `#/adapter/vxe-table` 导入，用 `:formatter`，**禁止** `#default="{ row }"` slot
- **ECharts**: 从 `@vben/plugins/echarts` 导入 `EchartsUI` + `useEcharts`
- **API**: 使用 `requestClient`（`#/api/request`），自动解包 `data`

### 构建与部署
- 后端改源码 → `docker compose build backend && docker compose up -d backend`
- 前端改源码 → `cd ui-vben/apps/web-antd && pnpm build`
- 测试 → `pnpm vitest run`（单元测试）、Playwright（功能验证）

---

## 禁止行为

- ❌ 新增页面时绕过 `auth.py` 的菜单 API，只改前端 module 文件
- ❌ 使用 `#default="{ row }"` 写 VxeTable column
- ❌ 跳过 `docker compose build backend` 直接重启后端容器
- ❌ 修改 `preferences.ts` 的 `accessMode` 或核心路由（`src/router/routes/core/`）

---

## 快速命令

```bash
# 构建前端
cd ui-vben/apps/web-antd && pnpm build

# 构建后端镜像
docker compose build backend && docker compose up -d backend

# 查看容器状态
docker ps

# 运行 vitest
cd ui-vben/apps/web-antd && pnpm vitest run

# Playwright 功能验证
cd .devtest && node playwright-t9.mjs

# 验证后端 API
curl http://localhost:8800/api/dashboard/overview
```
