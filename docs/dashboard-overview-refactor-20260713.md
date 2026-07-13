# 综合看板改造总结 — 2026-07-13

> 会话：`pm-director` · 操作人：Sisyphus

---

## 改造概述

对综合看板（`/dashboard/overview/index`）进行了 6 项优化和修复，涵盖后端数据修复、前端交互增强和菜单入口调整。

---

## 改造清单

### P0-1：修复月度开票/回款趋势图 null 横坐标问题 ✅

**问题**：ECharts 横坐标出现 `null` 值，影响所有曲线观感。

**根因**：
- `invoices` 表中 60 条记录的日期格式非 ISO 标准（如 `2024-9-24` 而非 `2024-09-24`）
- SQLite 的 `strftime()` 无法解析非标准日期格式，返回 NULL
- 另有 2 条记录的 `invoice_date` 为空字符串

**修复**：
- 数据库：执行 SQL 修复脚本，将 60 条非标准日期格式化为 `YYYY-MM-DD`，2 条空日期设为 NULL
- 后端：`dashboard.py` 第 146-152 行，`invoice_monthly` 查询增加 `WHERE invoice_date IS NOT NULL AND invoice_date != ''` 过滤条件
- 涉及文件：`backend/routers/dashboard.py`、数据库 `project_management.db`

**验证**：API 返回 `invoice_monthly` 19 条记录，无 null 月份值。

---

### P0-2：完善风险统计卡片的分类展示和跳转逻辑 ✅

**问题**：`风险与待处理 187项` 卡片点击无响应；其他卡片跳转到列表页无筛选提示。

**修复**：
- 新建 `risk-detail-modal.vue` 组件，点击 `风险与待处理` 卡片弹出详情面板
  - 展示 4 类风险的明细（名称、描述、数量）
  - 每项可点击跳转到对应筛选页面
- 更新 `alert-strip.vue`，4 个子卡片点击时带筛选参数跳转：
  - 待匹配回款 → `/invoices?payment_status=未匹配`
  - 待交付成果 → `/contracts?deliverable_status=pending`
  - 逾期付款 → `/contracts?payment_overdue=true`
  - 未开票合同 → `/contracts?invoice_status=uninvoiced`
- 更新 `metric-card.vue`，支持 `clickable` prop 和 `@click` 事件
- 涉及文件：`all-view.vue`、`risk-detail-modal.vue`（新建）、`alert-strip.vue`、`metric-card.vue`

**风险卡片业务逻辑**：

| 卡片 | 当前值 | 统计口径 | 涵义 |
|------|--------|---------|------|
| 风险与待处理 | 187 项 | 下面 4 项之和 | 汇总指标 |
| 待匹配回款 | 85 条 | `invoices.payment_status = '未匹配'` | 客户回款开票未正确关联合同 |
| 待交付成果 | 72 条 | `deliverables.status NOT IN ('completed', '已交付', '已验收')` | 项目交付物未完成 |
| 逾期付款 | 2 条 | `payments.planned_amount > paid_amount AND planned_date < today` | 客户应付但逾期未付的收款计划 |
| 未开票合同 | 28 条 | `contract_amount > invoice_total` | 合同存在未开票金额 |

---

### P1-1：最近合同列表添加行点击跳转合同详情 ✅

**问题**：最近合同列表无行点击功能，点击后无跳转。

**修复**：
- `recent-contracts.vue` 添加 `@cell-click="handleRowClick"` 事件
- 点击行跳转到 `/contracts/detail?id=<contract_id>`
- 涉及文件：`recent-contracts.vue`

---

### P1-2：隐藏 Vben 框架自带的演示分析页菜单 ✅

**问题**：概览菜单下的 `分析页` 是 Vben 框架自带的演示页面（用户量、访问量等虚拟数据），与合同管理系统业务无关。

**修复**：
- `auth.py` 第 92 行，分析页菜单项的 `visible` 从 `True` 改为 `False`
- 菜单中隐藏，路由仍可访问
- 涉及文件：`backend/routers/auth.py`

---

### P2-1：优化财务批次趋势单批次数据展示 ✅

**问题**：`finance_trend` 仅有一个批次（2026-W26），图表无法展示趋势。

**修复**：
- `all-view.vue` 增加 `hasMultipleBatches` 计算属性
- 单批次时显示提示信息（含批次 ID）而非空白图表
- 涉及文件：`all-view.vue`

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/routers/dashboard.py` | ✏️ 修改 | 月度趋势 SQL 过滤空日期 |
| `backend/routers/auth.py` | ✏️ 修改 | 分析页菜单 `visible: False` |
| `views/dashboard/overview/components/all-view.vue` | ✏️ 修改 | 风险弹窗 + 批次趋势优化 |
| `views/dashboard/overview/components/alert-strip.vue` | ✏️ 修改 | 筛选参数跳转 |
| `views/dashboard/overview/components/recent-contracts.vue` | ✏️ 修改 | 行点击跳转合同详情 |
| `views/dashboard/overview/components/metric-card.vue` | ✏️ 修改 | clickable 支持 |
| `views/dashboard/overview/components/risk-detail-modal.vue` | ➕ 新建 | 风险详情弹窗 |
| `database/project_management.db` | ✏️ 修改 | 60 条发票日期格式修复 |

---

## 部署情况

- 后端镜像已重建，API 验证通过
- 前端 dist 已构建并部署，JS bundle 含新增组件
- 变更已随 commit `dacdae4` 合并到 `master` 分支

---

## 后续工作

1. **合同列表页筛选**：需实现 `payment_overdue`、`deliverable_status`、`invoice_status` 等筛选参数处理
2. **发票列表页筛选**：需实现 `payment_status` 筛选处理
3. **合同状态数据补充**：当前 42 个合同全部为 `signed` 状态，建议后续更新
