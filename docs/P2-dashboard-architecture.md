# P2 架构评审与任务分解：Dashboard 后端实装 (T8) + 前端财务仪表盘接入 (T9)

> 作者：高见远（software-architect）｜范围：仅架构评审与任务分解，不含实现代码
> 代码库：`D:/Tare-workspace/pm-director`（REAL 仓库，P1 已收口：pytest 5/5、vitest 5/5、CI 全绿、部署 dev/test）

---

## 0. 现状摘要（调查结论）

### 0.1 后端现状
| 项 | 结论 |
|---|---|
| `backend/routers/dashboard.py` | **仅占位**：只有 `router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])`，无任何端点。`main.py` 已 `include_router(dashboard.router)`，注册就绪。 |
| 现 `/api/stats` 在哪 | 在 **`backend/routers/finance.py`**（非 dashboard.py）。返回 `contract_count / total_amount / invoiced / received / receipt_rate / sub_invoiced / sub_paid / stages / payments / deliverables`。已被 T4 测试覆盖，CI 绿。 |
| 现有聚合能力 | `finance.py` 还提供 `/api/stats/types`、`/api/finance/summary`、`/api/finance/trend`、`/api/finance/top-customers`；`invoices.py` 提供 `/api/invoices/summary`。即"指标"已分散在多个端点。 |
| 响应包装 | 统一用 `backend/models.py` 的 `vben_response(data)` → `{code:0, data, message:"success"}`；列表用 `vben_list`。 |
| DB 访问 | `backend/database.py`：`DB_PATH = <repo>/database/project_management.db`，`get_db()` 运行时连接（已确认 DB 真实位于仓库根 `database/`）。 |

### 0.2 生产库真实表/视图（已用 sqlite 直连核对）
- **`contracts`(50 行)**：含 `contract_id, project_name, project_type, contract_amount(REAL/万元), party_a, sign_date, contract_status(TEXT，当前全为 'signed'), estimated_amount` 等。`contract_status` 列**存在**。
- **`invoices`(71 行)**：`invoice_type∈{客户开票(46,≈1004万), 客户回款(25,≈477万)}`，`amount(REAL)`、`invoice_date`、`status∈{已开(46),已回款(25)}`、`payment_status(全 '未匹配')`、`direction∈{outbound,inbound}`、`project_id`。**`amount` 单位为「元」**。
- **`finance_records`(40 行)**：逐周追加的财务快照（按 `batch_id` 标识），含 `invoice_total / invoice_unbilled / payment_total / payment_unreceived / sub_invoice_total / sub_payment_total / subcontract_amount / batch_id / import_time`，均**「万元」**。
- **`current_finance_view`（生产视图，关键）**：
  ```sql
  SELECT fr.project_id, fr.project_name, fr.customer, c.contract_amount AS contract_total,
         fr.invoice_total, fr.invoice_unbilled, fr.payment_total, fr.payment_unreceived,
         fr.subcontractor, fr.subcontract_amount, fr.batch_id, fr.import_time
  FROM finance_records fr
  LEFT JOIN contracts c ON fr.project_id = c.contract_id
  WHERE fr.record_id IN (SELECT MAX(record_id) FROM finance_records GROUP BY project_id)
  ```
  ⚠️ 该视图**不含** `sub_invoice_total / sub_payment_total`（只有 `subcontract_amount`）。
- 其它相关表：`stages`、`payments`、`deliverables`、`projects`、`contract_type_attributes`（均有 `contract_id/project_id` 关联）。
- **视图与测试库不一致**：`backend/tests/conftest.py` 的 `_MINIMAL_SCHEMA` 定义的 `current_finance_view` 只有 `project_id, invoice_total, payment_total, subcontractor` 四列，缺 `project_name / payment_unreceived / contract_total` 等。因此 `/api/finance/summary`（SELECT 了 `cv.project_name, cv.payment_unreceived`）在测试库会 500。T8 必须同步扩展 conftest 视图，否则新端点无法测试。

### 0.3 单位口径冲突（重要风险）
| 数据源 | 已开票合计 | 已回款合计 | 单位 |
|---|---|---|---|
| `invoices.amount`（`/api/invoices/summary` 用） | ≈1004 万(由 元 折算) | ≈477 万 | **元**（原值 14,814,618.79） |
| `current_finance_view`（`/api/stats` 用） | 1049.13 | 707.15 | **万元** |
| `contracts.contract_amount` | 2364.79 合计 | — | 万元 |

→ **两个权威源数值不一致**。T8 需明确以谁为准（见 §5 待明确事项）。

### 0.4 前端现状
| 项 | 结论 |
|---|---|
| 财务仪表盘页 | `ui-vben/apps/web-antd/src/views/dashboard/index.vue`（路由 `/dashboard` → `DashboardOverview`，`meta.ignoreAccess:true`）。当前 `onMounted` 调 `getStatsApi()` + `getContractsApi()` 两个请求拼装。 |
| ⚠️ 字段错配 bug | 该页读取 `s.total_invoiced / s.total_paid`，但后端 `/api/stats` 返回的是 `invoiced / received` → **当前"已开票/已回款"两张卡片恒显 0**，T9 修复。 |
| API 封装层 | `src/api/contracts.ts` 内 `getStatsApi()→/api/stats`、`getTypesApi()→/api/stats/types`；统一 `requestClient`（`src/api/request.ts`）已配置 `codeField:'code', dataField:'data', successCode:0`，自动解包 `data`。 |
| 图表库 | **ECharts**，经 `@vben/plugins/echarts` 的 `EchartsUI` + `useEcharts`（如 `dashboard/analytics/analytics-trends.vue`、`infra/redis/modules/*.vue` 等大量用法）。 |
| 卡片/表格 | 当前页用原生 `div.rounded-lg.border.bg-card` 卡片 + `VxeTable/VxeColumn`（已 import 使用）。Vben 另提供 `@vben/common-ui` 的 `AnalysisOverview / AnalysisChartCard`（analytics 页在用），可作富化选项。 |
| 路由别名 | `#/api/*` → `src/api/*`（确认 `dashboard/index.vue` 用 `#/api/contracts`）。 |
| `getStatsApi` 引用点 | 仅 `dashboard/index.vue` 一处（T9 替换无扩散影响）。 |
| 其它 dashboard 子页 | `analytics/`（通用 Vben 模板：访问量/用户量，**非财务**）、`home/`（可配置首页）、`workspace/`，均非 T9 目标。 |

---

## 1. T8 范围界定：Dashboard 后端聚合端点

### 1.1 设计决策
- **新增单一聚合端点 `GET /api/dashboard/overview`**（置于 `backend/routers/dashboard.py`），一次性返回财务仪表盘所需的全部 KPI/图表/列表数据，前端只发 1 个请求。
- **保留 `/api/stats` 不动**（向后兼容、已被测、CI 绿）。`overview` 是其结构化超集，专为前端财务看板设计。
- **权威财务口径**：建议 `invoiced/received/unreceived/sub_*` 以 `current_finance_view`（finance_records 快照，万元）为准，与现 `/api/stats` 一致；`invoices` 表仅用于"状态分布 + 月度趋势"，金额按 `/10000` 折算为万元（需 PM 确认，见 §5）。
- `dashboard.py` 内可抽取私有 `_aggregate(...)` helper，避免与 `finance.py` 重复（不跨文件耦合）。

### 1.2 端点契约

```
GET /api/dashboard/overview
Query (全部可选):
  period : "all"(默认) | "ytd" | "year" | "quarter" | "month"   # 时间筛选（MVP 默认 all；见 §5 待确认）
  from   : ISO 日期字符串 (YYYY-MM-DD)                          # 自定义起
  to     : ISO 日期字符串                                        # 自定义止
  project_type : string                                         # 合同类型过滤
Response: { code:0, data:{...}, message:"success" }
```

#### 1.2.1 `data` JSON Schema
```jsonc
{
  "generated_at": "2026-07-07T12:00:00+00:00",          // string(ISO8601 UTC)
  "filters": { "period": "all", "from": null, "to": null, "project_type": null },
  "summary": {                                            // KPI 卡片
    "contract_count": 50,                                 // int
    "contract_total_amount": 2364.79,                    // number 万元
    "invoiced_amount": 1049.13,                          // number 万元 (current_finance_view.invoice_total 求和)
    "received_amount": 707.15,                           // number 万元 (payment_total 求和)
    "unreceived_amount": 341.98,                         // number 万元 (payment_unreceived 求和)
    "receipt_rate": 67.4,                                // number % = received/invoiced*100
    "uninvoiced_amount": 1315.66,                        // number 万元 = contract_total - invoiced
    "sub_invoiced_amount": 399.96,                      // number 万元 (finance_records.sub_invoice_total 最新快照求和)
    "sub_paid_amount": 287.03,                           // number 万元 (sub_payment_total 最新快照求和)
    "currency_unit": "万元"                              // string 常量，前端据此展示
  },
  "contracts_by_type": [                                 // 饼图：合同类型分布
    { "project_type": "科研类", "count": 30, "amount": 1234.5 }
  ],
  "contracts_by_status": [                               // 饼图/条形：合同状态分布
    { "contract_status": "signed", "count": 50, "amount": 2364.79 }
  ],
  "invoice_status_distribution": [                       // 饼图：发票状态
    { "status": "已开", "count": 46, "amount_wan": 1004.32 },
    { "status": "已回款", "count": 25, "amount_wan": 477.14 }
  ],
  "invoice_monthly": [                                   // 折线：月度开票/回款趋势
    { "month": "2026-01", "invoiced_wan": 200.5, "received_wan": 100.2 }
  ],
  "finance_trend": [                                     // 折线：财务快照按批次趋势
    { "batch_id": "2026-W26", "import_time": "2026-06-30T...", "invoiced_wan": 1049.13, "received_wan": 707.15 }
  ],
  "top_customers": [                                     // 条形：Top 客户
    { "customer": "甲方A", "count": 5, "total_amount": 800.0 }
  ],
  "pending_tasks": {                                     // 待办卡片
    "unmatched_payments": 71,                            // int: invoices.payment_status='未匹配'
    "pending_deliverables": 12,                          // int: deliverables.status 非终态
    "overdue_payments": 3,                               // int: payments 逾期未付（简化口径，见 §5）
    "uninvoiced_contracts": 8                            // int: 合同额>已开票
  },
  "recent_contracts": [                                  // 表格：最近合同
    { "contract_id":"ZH02-...", "project_name":"...", "contract_amount":123.4,
      "party_a":"...", "sign_date":"2026-05-01", "project_type":"科研类",
      "contract_status":"signed", "invoice_total":80.0, "payment_total":50.0 }
  ]
}
```

### 1.3 底层聚合逻辑（SQL 级，均在 `dashboard.py` 内执行）
> 约定：金额统一「万元」；`current_finance_view` 已按"每项目最新快照"过滤。

| `data` 字段 | SQL 来源 | 说明 |
|---|---|---|
| `summary.contract_count / contract_total_amount` | `contracts` | `COUNT(*)`、`SUM(contract_amount)`（可加 `project_type` 过滤） |
| `summary.invoiced/received/unreceived_amount` | `current_finance_view` | `SUM(invoice_total/payment_total/payment_unreceived)` |
| `summary.sub_invoiced/sub_paid_amount` | `finance_records`（最新快照子查询） | `WHERE record_id IN (SELECT MAX(record_id) ... GROUP BY project_id)` 后 `SUM(sub_invoice_total/sub_payment_total)`（视图不含此二列，须直查表） |
| `summary.receipt_rate` | 内存计算 | `round(received/invoiced*100,1)`（invoiced=0 时取 0） |
| `summary.uninvoiced_amount` | 内存计算 | `contract_total_amount - invoiced_amount` |
| `contracts_by_type` | `contracts` | `GROUP BY project_type`，`SUM(contract_amount)`，`ORDER BY amount DESC` |
| `contracts_by_status` | `contracts` | `GROUP BY contract_status` |
| `invoice_status_distribution` | `invoices` | `GROUP BY status`，`SUM(amount)/10000 AS amount_wan` |
| `invoice_monthly` | `invoices` | `strftime('%Y-%m', invoice_date) GROUP BY month`，开票/回款分别 `CASE invoice_type` 求和 `/10000` |
| `finance_trend` | `finance_records` | `WHERE batch_id IS NOT NULL GROUP BY batch_id ORDER BY import_time`，`SUM(invoice_total/payment_total)` |
| `top_customers` | `contracts` | `WHERE party_a<>'' GROUP BY party_a ORDER BY SUM(contract_amount) DESC LIMIT 10` |
| `pending_tasks.unmatched_payments` | `invoices` | `COUNT(*) WHERE payment_status='未匹配'` |
| `pending_tasks.pending_deliverables` | `deliverables` | `COUNT(*) WHERE status NOT IN ('completed','已交付')`（枚举待确认） |
| `pending_tasks.overdue_payments` | `payments` | 简化：`COUNT(*) WHERE planned_amount>COALESCE(paid_amount,0) AND planned_date < date('now')`（口径待确认） |
| `pending_tasks.uninvoiced_contracts` | `contracts`⋈`current_finance_view` | `COUNT(*) WHERE contract_amount > COALESCE(invoice_total,0)` |
| `recent_contracts` | `contracts`⋈`current_finance_view` | `LEFT JOIN` 取 `invoice_total/payment_total`，`ORDER BY sign_date DESC LIMIT 10` |

### 1.4 与 `/api/stats` 的关系
- **复用**：`overview.summary` 的 `contract_count / contract_total_amount / invoiced / received / receipt_rate / sub_*` 数值口径与 `/api/stats` 完全一致（同源 `current_finance_view`）。
- **扩展**：`overview` 额外提供按类型/状态分组、发票分布、月度趋势、财务批次趋势、Top 客户、待办、最近合同——这些是前端原需多次请求或前端手算的。
- **不破坏**：`/api/stats` 保留，待无其他消费者（仅 dashboard 页）后再考虑弃用。

---

## 2. T9 范围界定：前端财务仪表盘接入

### 2.1 目标页
- 改造 `ui-vben/apps/web-antd/src/views/dashboard/index.vue`：弃用 `getStatsApi()+getContractsApi()`，改为单请求 `getDashboardOverviewApi()`，修复"已开票/已回款恒为 0"的字段错配。
- 新增图表：合同类型饼图、发票状态饼图、月度开票/回款折线、财务批次趋势折线、Top 客户条形。

### 2.2 前端文件清单（新建/修改）
| 动作 | 文件 | 说明 |
|---|---|---|
| **新建** | `ui-vben/apps/web-antd/src/api/dashboard.ts` | 定义 `getDashboardOverviewApi()` → `requestClient.get('/api/dashboard/overview')` + TS 接口 `DashboardOverview`、`DashboardSummary` 等（对齐 §1.2.1 schema） |
| **修改** | `ui-vben/apps/web-antd/src/views/dashboard/index.vue` | 单请求拉取 overview；渲染 KPI 卡片 + 图表容器 + 最近合同表；加载/错误态 |
| **新建** | `ui-vben/apps/web-antd/src/views/dashboard/components/finance-trend-chart.vue` | ECharts 折线（finance_trend） |
| **新建** | `ui-vben/apps/web-antd/src/views/dashboard/components/contract-type-pie.vue` | ECharts 饼图（contracts_by_type） |
| **新建** | `ui-vben/apps/web-antd/src/views/dashboard/components/invoice-status-pie.vue` | ECharts 饼图（invoice_status_distribution） |
| **新建** | `ui-vben/apps/web-antd/src/views/dashboard/components/top-customers-bar.vue` | ECharts 条形（top_customers） |
| **新建(可选)** | `ui-vben/apps/web-antd/src/views/dashboard/components/kpi-cards.vue` | 抽取 KPI 卡片为子组件（保持 index.vue 简洁） |
| **新建(测试)** | `ui-vben/apps/web-antd/src/api/__tests__/dashboard.test.ts` | vitest：mock requestClient，断言 overview 解包与字段映射 |

> 复用：图表统一用 `@vben/plugins/echarts` 的 `EchartsUI + useEcharts`（与 `analytics-trends.vue` 同款）；表格复用现有 `VxeTable/VxeColumn`；卡片沿用现有 `div.rounded-lg.border.bg-card` 风格（或升级为 `@vben/common-ui` 的 `AnalysisOverview`）。

### 2.3 页面布局（建议）
```
┌ KPI 卡片行 (col-span 4) ┐ contract_count / contract_total / invoiced / received / unreceived / receipt_rate / sub_*
├ 合同类型饼图 │ 发票状态饼图 │ Top 客户条形 ┤   (各 1/3)
├ 财务批次趋势折线 (finance_trend) 全宽 ┤
├ 月度开票/回款折线 (invoice_monthly) 全宽 ┤
└ 最近合同表 (VxeTable, recent_contracts) 全宽 ┘
```

### 2.4 API 封装示例（伪代码，非实现）
```ts
// src/api/dashboard.ts
import { requestClient } from '#/api/request'
export interface DashboardOverview { generated_at:string; summary:DashboardSummary; contracts_by_type:ContractType[]; /* ... */ recent_contracts:RecentContract[] }
export function getDashboardOverviewApi(params?: {period?:string; from?:string; to?:string; project_type?:string}) {
  return requestClient.get<DashboardOverview>('/api/dashboard/overview', { params })
}
```

---

## 3. 任务分解表（有序、含依赖/顺序/工作量）

> 顺序原则：**T8 先于 T9**（前端依赖后端契约）；后端测试与前端可部分并行。

| ID | 任务 | 真实文件清单 | 依赖 | 顺序 | 工作量 | 风险点 |
|---|---|---|---|---|---|---|
| **T8-A** | 实现 `GET /api/dashboard/overview` 聚合端点 | `backend/routers/dashboard.py` | 无 | 1（首位） | M | ①单位口径（元 vs 万元）需 PM 确认；②`sub_*` 须直查 `finance_records`（视图无此列）；③`pending_tasks` 各枚举口径待定 |
| **T8-B** | 扩展 conftest 视图 + 补充 dashboard 测试 | `backend/tests/conftest.py`（扩展 `current_finance_view` 列）、`backend/tests/test_dashboard.py`（新建） | T8-A | 2 | S | conftest 视图须与生产列对齐，否则测试 500；保持 CI 绿 |
| **T9-A** | 新增前端 dashboard API + 重写仪表盘页骨架 | `src/api/dashboard.ts`（新）、`src/views/dashboard/index.vue`（改） | T8-A | 2（可与 T8-B 并行） | M | 字段名对齐（修复 `total_invoiced→invoiced_amount` 错配）；`#/api/dashboard` 别名可用 |
| **T9-B** | 实现财务图表组件并接入仪表盘 | `src/views/dashboard/components/*.vue`（5 个新建，可选 kpi-cards.vue） | T9-A | 3 | M | ECharts option 与 overview 数据结构对齐；响应式 resize |
| **T9-C** | 前端容错/加载态 + 联调验证 | `src/views/dashboard/index.vue`（补）、`src/api/__tests__/dashboard.test.ts`（新） | T9-B, T8-B | 4（收尾） | S | dev/test 服务器联调；CI vitest 门禁 |

**依赖图（Mermaid）** 见 `docs/P2-dashboard-task-graph.mermaid`（另附）。

---

## 4. 图表（Mermaid）

### 4.1 后端类/结构图
> 见 `docs/P2-dashboard-class.mermaid`

### 4.2 调用时序图
> 见 `docs/P2-dashboard-sequence.mermaid`

### 4.3 任务依赖图
> 见 `docs/P2-dashboard-task-graph.mermaid`

---

## 5. 待明确事项（需向 PM/用户确认）

1. **单位口径（高优先级）**：`invoices.amount` 是「元」，`finance_records/current_finance_view` 是「万元」，二者"已开票/已回款"数值不一致（≈1004万 vs 1049万）。仪表盘应统一以哪个为准？**建议**：财务 KPI 以 `finance_records` 快照（万元）为权威；`invoices` 仅用于状态分布与月度趋势（金额 `/10000` 折算并明确标注）。
2. **时间范围筛选是否 MVP 必须**：财务数据为周批次快照（`batch_id`），非逐笔交易日期。`period` 参数建议 MVP 默认 `all`，作为可选增强（影响 `invoice_monthly`/`finance_trend` 的过滤实现）。
3. **权限/数据隔离**：当前 `/dashboard` 路由 `ignoreAccess:true`，全员可见；DB 有 `personnel/project_personnel` 但未在前端鉴权使用。是否需按用户/角色过滤（如只看自己负责项目）？**建议 MVP 不区分**，后续增强。
4. **`contract_status` 枚举**：当前全为 `'signed'`。是否有其它状态（draft/active/closed）需在"按状态分布"中预留？
5. **`pending_tasks` 口径**：
   - `pending_deliverables` 的"终态"枚举（`deliverables.status` 取值未全量核对）；
   - `overdue_payments` 的逾期判定（`payments.planned_date` vs 当前日期、`paid_amount` 对比）；
   - `unmatched_payments` 当前 = 71（全量 `payment_status='未匹配'`），是否作为"待办"展示。
6. **金额展示单位**：前端卡片统一显示「万元」还是「元」？需与单位口径(1)一起定。
7. **`sub_*` 指标展示**：`current_finance_view` 不含 `sub_invoice_total/sub_payment_total`，需直查 `finance_records` 最新快照；是否前端需要"供应商"维度卡片？

---

## 6. 结论与建议
- T8 工作量可控（单端点 + 测试），核心风险是**单位口径**与 **conftest 视图与生产不一致**，必须在 T8-A/T8-B 同步解决。
- T9 为前端改造，单请求替换双请求即可修复现有 bug，并借 ECharts 组件补齐图表；工作量中等。
- 建议 PM 优先确认 §5 第 1、3、5 项，以免返工。
