# pm-director — 项目开发指南

> 本文件是 Claude Code / Cursor 等 IDE Agent 的**项目入口文档**。
> 任何 Agent 加入本项目协作时，必须先阅读以下内容。

---

## 关键文档索引（按优先级）

| 优先级 | 文档 | 内容 |
|--------|------|------|
| ⭐ P0 | `docs/vben-framework-rules.md` | **Vben Admin 5 框架开发规则** — 所有前端开发必须遵循 |
| ⭐ P0 | `docs/开发流程规范.md` | **开发流程规范** — PR、CI、部署、验收流程 |
| ⭐ P0 | `docs/贡献约束.md` | **贡献约束** — 路由、返回契约、命名规范 |
| 🔹 P1 | `docs/规范路由清单-20260713.md` | 规范路由注册表 |
| 🔹 P1 | `docs/部署规范.md` | 部署规范（本地 Docker + 236 生产） |
| 🔹 P1 | `knowledge-base/index.md` | 知识库索引 |

### 关于本项目

- **项目**: 国网合同管理系统 (pm-director)
- **前端**: Vben Admin 5 (Vue3 + Vite7 + Tailwind CSS + Ant Design Vue)
- **后端**: Python FastAPI + SQLite
- **主应用**: `ui-vben/apps/web-antd`
- **本地测试**: `http://localhost:18090/web/` (Docker 前端)
- **Docker 后端**: `http://localhost:18080`

---

## 审计发现的核心问题

> 来源：`docs/audits/系统全量审计与改造基线-2026-07-13.md`

当前系统存在**四套基础关系同时失控**：

1. **菜单与路由没有唯一真值** — 后端模式被改造成静态与动态路由混合
2. **源码、容器和实际页面版本不一致** — PR 已合并不等于前端已部署
3. **数据契约没有被数据库约束** — 外键关闭、167 条外键违规、金额单位混标
4. **GitHub 合并与发布门禁失效** — PR 在 CI 完成前合并，失败后仍留在 master

**结论**：继续逐页"美化"只会把新界面叠在旧结构上。必须按以下顺序整改：

```
阶段0: 安全止血 → 阶段1: 路由与发布基线 → 阶段2: 数据契约 → 阶段3: 信息架构与UI
```

---

## Vben 框架核心规则（快速参考）

> 详细版见 `docs/vben-framework-rules.md`

### 路由与菜单

- 本项目使用 **`accessMode: 'backend'`**，路由由后端 API (`backend/routers/auth.py`) 控制
- **路由唯一真值**：后端菜单定义是唯一来源，前端 `routes/modules/` 仅作为旧路由重定向
- 新增页面 = ① 在 `views/` 下建 `.vue` 文件 + ② 在 `auth.py` 的 `menus` 中添加菜单项
- 默认首页通过 `auth.py` 的 `user.homePath` 设置

### 组件开发

- **VxeTable**: 从 `#/adapter/vxe-table` 导入，用 `:formatter`，**禁止** `#default="{ row }"` slot
- **ECharts**: 从 `@vben/plugins/echarts` 导入 `EchartsUI` + `useEcharts`
- **API**: 使用 `requestClient`（`#/api/request`），自动解包 `data`

### 构建与部署

- 后端改源码 → `docker compose build backend && docker compose up -d backend`
- 前端改源码 → `cd ui-vben/apps/web-antd && pnpm build` → 重启前端容器
- 测试 → `pnpm vitest run`（单元测试）、Playwright（功能验证）

---

## 禁止行为

### 路由相关

- ❌ 新增页面时绕过 `auth.py` 的菜单 API，只改前端 module 文件
- ❌ 在前端 `routes/modules/` 中添加业务路由（仅允许 `Legacy*` 重定向）
- ❌ 详情页使用固定跳列表，不保留来源信息
- ❌ 新页面主动跳回旧路由（如 `InvoiceList`、`ProjectList`）

### 代码相关

- ❌ 使用 `#default="{ row }"` 写 VxeTable column
- ❌ 跳过 `docker compose build backend` 直接重启后端容器
- ❌ 修改 `preferences.ts` 的 `accessMode` 或核心路由

### 数据相关

- ❌ 金额字段不带单位标注（必须在 API schema 和 UI 中明确"元"或"万元"）
- ❌ 新增表或字段时不定义外键约束

### 协作相关

- ❌ 在 CI 检查完成前合并 PR
- ❌ 跳过部署验收直接关闭 Issue

---

## 返回契约规范

### 原则

1. **列表进入详情时携带来源** — 使用 `from` 参数或 `router.push` 时保留 state
2. **详情页优先返回可信来源** — 使用 `router.back()` 或 `from` 参数
3. **无可信来源时回到模块规范列表** — 使用 `router.push({ name: 'ModuleNameList' })`
4. **旧路径只做单向重定向** — 业务页面不得主动跳回旧路径

### 规范路由命名

| 模块 | 列表路由名 | 详情路由名 |
|------|-----------|-----------|
| 合同 | `ContractList` | `ContractDetail` |
| 客户发票 | `CustomerInvoices` | `CustomerInvoiceDetail` |
| 客户回款 | `CustomerReceipts` | `CustomerReceiptDetail` |
| 供应商 | `SupplierList` | `SupplierDetail` |
| 供应商发票 | `SupplierInvoices` | `SupplierInvoiceDetail` |
| 供应商付款 | `SupplierPayments` | `SupplierPaymentDetail` |

---

## 开发流程摘要

> 详细版见 `docs/开发流程规范.md`

### 标准流程

```
Issue 定义问题和验收标准
  → 设计/RFC 确认路由、数据和 UI 边界
  → 从最新 master 建短分支
  → Draft PR，先展示方案与风险
  → 实现 + 单元/契约/E2E 测试
  → 至少 1 人审查并解决全部对话
  → 所有必需检查完成且通过
  → 合并 master
  → 部署验收
  → 关闭 Issue
```

### 禁止流程

- ❌ 先合并、等 CI
- ❌ 先关 Issue、再验证部署
- ❌ 一个 PR 同时改路由、数据、UI 和基础设施

---

## 快速命令

```bash
# 构建前端
cd ui-vben/apps/web-antd && pnpm build

# 构建后端镜像并重启
docker compose build backend && docker compose up -d backend

# 重启前端容器（加载新构建）
docker restart pm-director-frontend

# 查看容器状态
docker ps

# 运行前端测试
cd ui-vben/apps/web-antd && pnpm vitest run

# 运行后端测试
cd backend && python -m pytest -q

# 验证后端 API
curl http://localhost:18080/system/auth/get-permission-info | grep 供应商列表

# 查看前端日志
docker logs pm-director-frontend --tail 20
```

---

## 当前改造进度

```
阶段0: ✅ 完成 — 安全止血、分支保护、数据库备份
阶段1: ✅ 完成 — 路由与发布基线修复
阶段2: ⏳ 待开始 — 数据契约与清洗
阶段3: ⏳ 待开始 — 信息架构与UI重设计
```

### 阶段1 遗留问题（Issue #34）

- 部分详情页仍使用旧路由名（通过重定向可工作）
- 仪表盘组件使用旧路径
- 需要在后续 PR 中统一清理
