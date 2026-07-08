# UI 布局与显示审计 — 2026-07-08

> 审计范围：P2（仪表盘）+ P3（合同/发票/供应商详情页）全部前端改动
> 评估基准：ardot-ui-design 设计准则（Purpose First / Dominant Region / System Status / Consistency / Density）+ Vben 框架规范
> 审计方式：代码级静态审计 + 设计准则对照（未启动实时浏览器渲染，像素级验证建议走 Playwright 视觉回归）

---

## 一、修改总览（受审文件）

| 文件 | 动作 | 路由状态 |
|------|------|---------|
| `views/dashboard/overview/index.vue` | 新建 | ✅ 已注册 `DashboardOverview`（首页） |
| `views/dashboard/index.vue` | 修改 | ⚠️ **未注册 = 死代码** |
| `views/dashboard/components/*.vue`（5 个图表组件） | 新建 | 随 overview 加载 |
| `views/contracts/detail.vue` | 重写 | ✅ `ContractDetail` |
| `views/invoices/detail.vue` | 新建 | ✅ `InvoiceDetail` |
| `views/suppliers/detail.vue` | 新建 | ✅ `SupplierDetail` |
| `views/invoices/index.vue` | 修改 | ✅ + CellRouterLink |
| `views/suppliers/index.vue` | 修改 | ✅ + CellRouterLink |
| 后端 `auth.py` / `contracts.py` / `invoices.py` / `suppliers.py` / `dashboard.py` | 修改 | — |

---

## 二、逐页审计

### 2.1 综合看板 Dashboard（overview/index.vue）— 良好
- ✅ 三态齐全：Loading / Error（`重试`按钮）/ Empty（最近合同表）
- ✅ 结构清晰：KPI 行（4 列）→ 3 图表行（1/3 各）→ 2 全宽趋势图 → 最近合同表
- ✅ 卡片风格统一（`border + bg-card + shadow-sm`），响应式 `lg:grid-cols-*`
- ⚠️ 图表内颜色硬编码 `#5ab1ef` / `#019680`，未使用主题 token
- ⚠️ `finance-trend-chart` 与 `monthly-trend-chart` 代码 ~95% 重复，应合并为参数化组件
- ⚠️ 「财务批次趋势」x 轴用 `batch_id`（如 B001），非时间轴，"趋势"语义偏弱

### 2.2 合同详情（detail.vue）— 可用但粗糙，偏离设计稿
- ✅ 头部两栏（基本信息 2 格 + 财务汇总 1 格）、关联项目 + 合同文件两栏
- ✅ 交付物表格、回款率进度条
- ❌ **阶段进度用 CSS 假进度条**（completed=100% / in_progress=60% / pending=10%），非真实进度，具误导性
- ❌ **设计稿要求的 ECharts 甘特图未实现**（仅简单横条）
- ❌ **文件上传未实现**（后端无 upload 端点；前端仅"预览"链接）
- ❌ 缺 Error / Not-Found 空态（仅有 `a-spin`，接口失败即空白）
- ⚠️ 颜色再次硬编码（`#5ab1ef`/`#019680`/`#faad14`）
- ⚠️ `clean()` 正则截断甲方/乙方括号内容，可能丢失有效信息
- ⚠️ 付款用 `a-timeline`（设计稿为"付款计划表"），属可接受替代

### 2.3 发票详情（detail.vue）— 过于单薄
- ✅ 单卡片描述列表，字段完整
- ❌ 无 Error / Empty 态
- ❌ 仅平铺字段，无关联合同/回款上下文，与合同详情"深度"不一致（详情页之间体验断层）

### 2.4 供应商详情（detail.vue）— 较好但跨页不一致
- ✅ 基本信息 + 财务汇总（4 列指标行）+ 关联合同表
- ✅ 使用全局 token `text-blue/text-green/text-orange`（有效）
- ❌ 无 Error / Empty 态
- ⚠️ token 色值（#1677ff/#52c41a）与看板（#5ab1ef/#019680）**不一致**
- ⚠️ 关联合同表未提供跳转到合同详情的链接（列表页能跳入，供应商页跳不出）

### 2.5 列表页（invoices / suppliers index）— 良好
- ✅ `CellRouterLink` 跳转详情（正确模式）
- ✅ 发票双 Tab（客户/供应商）、汇总卡片、工具栏、分页
- ⚠️ invoices 自带 scoped `.text-blue`（#1677ff），与看板色值不同

---

## 三、系统性问题（跨页）

| # | 问题 | 严重度 | 说明 |
|---|------|--------|------|
| 1 | **`views/dashboard/index.vue` 为死代码** | P1 | 路由仅注册 overview，该 256 行文件永不加载，应删除或合并 |
| 2 | **财务语义色无统一 token** | P1 | 看板 `#5ab1ef/#019680` vs 列表 `#1677ff/#52c41a` vs 硬编码 `#faad14`，缺单一来源 |
| 3 | **详情页缺 Error/Empty 态** | P1 | 3 个详情页仅 `a-spin`，接口失败/无数据即空白（违反设计准则 §6） |
| 4 | **阶段进度为假百分比** | P1 | 固定 100/60/10，误导；应改真实值或改标签为"状态" |
| 5 | **两套卡片体系并存** | P2 | 看板用 `border+bg-card`，详情页用 antd `a-card`，视觉语言不统一 |
| 6 | **图表组件重复** | P2 | finance/monthly 趋势图应合并 |
| 7 | **设计稿偏差** | P2 | 甘特图（ECharts）、文件上传均未落地；子组件未拆分 |

> 功能性：无阻断级 Bug（历史 Playwright 已通过）。以上均为质量/一致性/体验问题。

---

## 四、与 P3 设计稿（docs/P3-contract-detail-design.md）偏差

| 设计稿要求 | 实际 | 状态 |
|-----------|------|------|
| 阶段甘特图（ECharts 横向条形） | CSS 假进度条 | ❌ 未实现 |
| 文件上传/预览组件 + 后端端点 | 仅只读列表 | ❌ 未实现 |
| 子组件拆分（gantt/finance/file/project） | 全内联单文件 | ⚠️ 简化 |
| 两栏分屏布局 | 近似实现（grid 分栏） | ✅ |
| 付款计划表 | a-timeline 替代 | ✅ 可接受 |

---

## 五、下一步建议（按优先级）

1. **删除死代码** `views/dashboard/index.vue`，避免维护歧义。
2. **建立设计 token**：在全局 CSS 定义 `--finance-invoiced / --finance-received / --finance-unreceived`，替换所有硬编码 hex（看板 5 组件 + 合同/发票/供应商详情）。
3. **补齐三态**：为 3 个详情页抽取共享 `StateBlock`（loading/error/empty），对齐设计准则 §6。
4. **修正阶段进度**：用真实完成度，或将标签改为"状态指示"以避免误导。
5. **（回头优化）** 按 P3 设计稿落地 ECharts 甘特图 + 文件上传。
6. **视觉验证**：启动本地 Docker / Playwright 对每页截图，做像素级回归（本次为代码级审计，未渲染实时界面）。
