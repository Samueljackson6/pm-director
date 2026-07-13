# 综合驾驶舱四视图重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 `/dashboard/overview` 路由下实现全域、经营管理、项目执行、财务回款四个驾驶舱视图。

**Architecture:** 保留单一聚合接口并新增 `project_execution`，前端入口只负责加载、路由 Query 和视图切换，各场景拆成独立展示组件。现有图表组件继续复用，不引入依赖和可配置拖拽系统。

**Tech Stack:** FastAPI、SQLite、Vue 3、TypeScript、Vben Admin、Ant Design Vue、ECharts、VxeTable、pytest、Vitest、Playwright。

## Global Constraints

- 禁止使用 gpt-5.6-sol。
- 实现代理使用 gpt-5.6-luna、低思考深度，每个任务一次调用。
- 不引入新依赖。
- 不修改真实认证、合同、发票、供应商数据。
- 所有金额统一为万元。
- 保持现有 dashboard API 字段兼容。
- 新增文档和关键注释使用中文。
- 禁止大范围格式化和无关重构。

---

### Task 1: 项目执行聚合与前端类型

**Files:**
- Modify: `backend/routers/dashboard.py`
- Modify: `backend/tests/test_dashboard.py`
- Modify: `backend/tests/conftest.py`（仅在测试 schema 缺列时）
- Modify: `ui-vben/apps/web-antd/src/api/dashboard.ts`

**Interfaces:**
- Produces: `DashboardOverview.project_execution: ProjectExecutionOverview`
- Existing fields under `DashboardOverview` remain unchanged.

- [ ] **Step 1: 扩展失败测试**
  - 在 dashboard API 测试中断言 `project_execution` 存在。
  - 断言指标为整数、分布为数组、最近项目为数组。
  - 添加至少一个项目/阶段/交付物测试数据，验证非零聚合。

- [ ] **Step 2: 运行测试确认失败**
  - Run: `backend/.venv/Scripts/python.exe -m pytest backend/tests/test_dashboard.py -q`
  - Expected: FAIL，缺少 `project_execution`。

- [ ] **Step 3: 实现最小聚合查询**
  - 使用 projects/stages/deliverables 的聚合 SQL。
  - 缺负责人定义为 `project_manager IS NULL OR TRIM(project_manager)=''`。
  - 逾期阶段要求有可解析的 `end_time` 且状态不是 completed。
  - 最近项目按 `updated_at/created_at` 排序，最多 10 条。
  - 禁止逐项目查询。

- [ ] **Step 4: 补齐前端类型**
  - 新增项目状态、风险、最近项目和聚合接口类型。
  - `DashboardOverview` 增加必需的 `project_execution` 字段。

- [ ] **Step 5: 运行验证**
  - Run: `backend/.venv/Scripts/python.exe -m pytest backend/tests/test_dashboard.py -q`
  - Run: `backend/.venv/Scripts/ruff.exe check backend --quiet`
  - Expected: PASS。

---

### Task 2: 四视图前端驾驶舱

**Files:**
- Modify: `ui-vben/apps/web-antd/src/views/dashboard/overview/index.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/dashboard-types.ts`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/components/dashboard-header.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/components/metric-card.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/components/alert-strip.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/components/all-view.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/components/management-view.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/components/project-view.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/components/finance-view.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/components/finance-funnel.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/components/recent-contracts.vue`
- Create: `ui-vben/apps/web-antd/src/views/dashboard/overview/__tests__/dashboard-view.test.ts`

**Interfaces:**
- Consumes: `DashboardOverview` including `project_execution` from Task 1.
- Produces: `view=all|management|projects|finance` URL Query behavior.

- [ ] **Step 1: 写失败测试**
  - 测试四个合法视图值和非法值回落 all。
  - 测试待办总数和财务漏斗计算纯函数。
  - 测试入口源码包含四视图组件且不再内联旧版完整表格。

- [ ] **Step 2: 运行测试确认失败**
  - Run: `pnpm vitest run src/views/dashboard/overview/__tests__/dashboard-view.test.ts`
  - Expected: FAIL，视图工具和组件尚不存在。

- [ ] **Step 3: 实现入口与公共组件**
  - `index.vue` 只负责数据加载、错误处理、Query 和场景组件切换。
  - Header 展示更新时间、单位和刷新。
  - Tab 使用 Ant Design，不引入依赖。
  - Query 变化和用户切换双向同步，避免循环更新。

- [ ] **Step 4: 实现四个场景视图**
  - 全域总览：综合 KPI、预警、结构、趋势、项目摘要、最近合同。
  - 经营管理：经营 KPI、类型/状态、Top 客户、月度趋势。
  - 项目执行：项目 KPI、状态/风险分布、最近项目。
  - 财务回款：漏斗、未开票/未回款、趋势、发票状态和待办。
  - 复用已有图表组件；无数据时显示空态。

- [ ] **Step 5: 样式与无障碍**
  - 使用主题 class/token，集中定义场景颜色。
  - Tab 和刷新按钮有明确文本。
  - 1440/1024/窄屏不横向溢出。

- [ ] **Step 6: 运行前端验证**
  - Run: `pnpm vitest run src/views/dashboard/overview/__tests__/dashboard-view.test.ts`
  - Run: `pnpm test`
  - Run: `pnpm typecheck`，dashboard 新增/修改文件错误必须为 0。
  - Run: `pnpm build`

---

### Task 3: 主代理集成与运行态回归

**Files:**
- Modify: `docs/审计整改执行报告-20260711.md`
- Create: `.planning/dashboard-refactor-20260711/` 下证据文件。

- [ ] **Step 1: 审查 Task 1 和 Task 2 diff**
  - 检查文件范围、API 兼容、金额单位、空态和无 N+1。

- [ ] **Step 2: 重建后端和前端**
  - Run: `docker compose build backend && docker compose up -d backend`
  - Run: `pnpm build`

- [ ] **Step 3: Playwright 四视图回归**
  - 登录后进入综合看板。
  - 切换四个 Tab，检查 URL Query。
  - 刷新后保留当前视图。
  - 检查 KPI、项目、财务、最近合同。
  - 收集 console/pageerror/requestfailed/HTTP >= 400。
  - 1440px 和 768px 截图，无横向溢出。

- [ ] **Step 4: 更新文档**
  - 写入完成内容、验证结果和剩余风险。
