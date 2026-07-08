# P2 交付总结 — Dashboard 后端实装 (T8) + 前端财务仪表盘接入 (T9)

> 交付日期：2026-07-08 | 主理人：齐活林
> 关联架构文档：`docs/P2-dashboard-architecture.md`

---

## TL;DR

P2 完成：后端 `GET /api/dashboard/overview` 聚合端点（T8）上线并验证通过；前端 5 个 ECharts 图表组件 + 单请求仪表盘页（T9）代码完成，因 Vben Admin 布局 Bug 导致页面渲染阻塞，已单独提 Bug。

---

## T8 — Dashboard 后端聚合端点 ✅ **已上线**

### 端点
```
GET /api/dashboard/overview
Response: { code:0, data: { generated_at, filters, summary, contracts_by_type, contracts_by_status, invoice_status_distribution, invoice_monthly, finance_trend, top_customers, pending_tasks, recent_contracts }, message:"success" }
```

### 验证结果
- **独立验证**（主理人）：`pytest backend/tests/test_dashboard.py` — **2/2 通过**
- **实时验证**（Docker 容器）：`curl http://localhost:8800/api/dashboard/overview` — `code:0`
  - `contract_count=50`, `invoiced_amount=1049.13`, `received_amount=707.15`, `receipt_rate=67.4%`
  - 11 个字段齐全，金额统一"万元"
- **前端代理验证**（Playwright）：`fetch('/admin-api/api/dashboard/overview')` — `code:0`（确认 nginx 代理通）

### 文件
| 文件 | 动作 | 说明 |
|------|------|------|
| `backend/routers/dashboard.py` | 修改 | 从空占位重写为完整聚合端点 |
| `backend/tests/conftest.py` | 修改 | 扩展 `current_finance_view` 列对齐生产 |
| `backend/tests/test_dashboard.py` | 新建 | 2 个测试用例（overview code==0, 字段映射） |

> 注：`pending_tasks.overdue_payments` 当前为 0（工程师用真实 `payment_date` 列替代架构文档中不存在的 `planned_date`，72 行全 NULL → overdue=0）。需 PM 确认是否放宽口径。

---

## T9 — 前端财务仪表盘接入 ✅ **代码完成，页面渲染因 Vben 布局 Bug 阻塞**

### 代码验证结果
| 验证项 | 结果 |
|--------|------|
| Vitest | **3 文件 7/7 全部通过** |
| `pnpm build` | **✓ built in 2-3 min**，12807 modules |
| 控制台错误 | **0 错误**（非仪表盘页面） |
| 页面渲染（contracts/invoices/suppliers） | **全部通过**（40/50/24 行） |
| 页面渲染（finance-dashboard） | ❌ 因 Vben BasicLayout VxeTable 崩溃 |

### 文件
| 文件 | 动作 | 说明 |
|------|------|------|
| `ui-vben/.../src/api/dashboard.ts` | **新建** | 完整 TS 接口 + `getDashboardOverviewApi()` |
| `ui-vben/.../src/views/dashboard/index.vue` | **修改** | 单请求消费 T8 端点，KPI 卡片 + 图表布局 + loading/error |
| `ui-vben/.../src/views/dashboard/components/contract-type-pie.vue` | **新建** | ECharts 饼图（合同类型分布） |
| `ui-vben/.../src/views/dashboard/components/invoice-status-pie.vue` | **新建** | ECharts 饼图（发票状态分布，含颜色语义） |
| `ui-vben/.../src/views/dashboard/components/finance-trend-chart.vue` | **新建** | ECharts 双折线（财务批次趋势） |
| `ui-vben/.../src/views/dashboard/components/monthly-trend-chart.vue` | **新建** | ECharts 双折线（月度开票/回款，45°旋转标签） |
| `ui-vben/.../src/views/dashboard/components/top-customers-bar.vue` | **新建** | ECharts 横向条形（Top 客户，升序排列） |
| `ui-vben/.../src/api/__tests__/dashboard.test.ts` | **新建** | Vitest：mock requestClient，断言端点调用和字段映射 |
| `ui-vben/.../src/router/routes/modules/dashboard.ts` | **修改** | 路由配置（独立 `/finance-dashboard` 路径） |

### 修复的 Bug
- 原 `index.vue` 读取 `stats.total_invoiced` / `stats.total_paid`，后端 `/api/stats` 返回 `invoiced` / `received` → 已开票/已回款恒显 0。T9 改用 `summary.invoiced_amount` / `summary.received_amount` 修复。

### 已知阻塞问题
- **Bug #BUG-001**：Vben Admin BasicLayout 在独立路由上触发 VxeTable 渲染崩溃（`docs/bug-vben-layout-vxetable-crash.md`）

---

## Playwright 全量回归结果

```
PASS  login
PASS  api-stats-local — contract_count=50
PASS  dashboard-api — code=0
PASS  contracts — rows=40
PASS  invoices — rows=50
PASS  suppliers — rows=24
PASS  console-errors — 0 (non-dashboard pages)
```

---

## 待办事项

1. 修复 Vben BasicLayout VxeTable 崩溃 Bug（`docs/bug-vben-layout-vxetable-crash.md`）
2. PM 确认 `overdue_payments` 口径（当前用 `payment_date`，全 NULL → 0）
3. 提交 P2 代码 PR（含 T8 + T9 全部改动）
4. 关闭 Issue #8 / #9
