# 设计审计证据

## 结构证据

- 审计页面静态交互声明共 148 个：壳层 7、综合看板 8、合同列表 18、合同详情及子组件 80、供应商列表 1、供应商详情 34。代表性证据：`layouts/basic.vue:227-273`、`contracts/detail.vue:6-710`、`suppliers/detail.vue:7-339`。
- 项目自有主组件树最大深度为 4：`BasicLayout → ContractDetail → ResearchContent → StageGantt`。证据：`backend/routers/auth.py:110-145`、`contracts/detail.vue:336-344`、`ResearchContent.vue:13`。
- 同用途重复交互模式共 10 组，包括返回、退出、刷新、新增发票、付款、打开详情和锚点导航。证据：`contracts/detail.vue:9,211,219`、`suppliers/detail.vue:7,21,197`。
- dead prop 1 个：`ResearchContent` 声明但未读取 `contract`。证据：`ResearchContent.vue:296-303`、父传入 `contracts/detail.vue:338`。
- 当前壳层在顶部、侧栏和页面 Tab 同时提供导航；运行截图见 `docs/audits/evidence/2026-07-13/01-dashboard.png`。

## 视觉证据

- 间距规模：`[2,4,6,8,10,12,16,20,24,32,48]px`。证据：`dashboard-header.vue:2-14`、`contracts/detail.vue:2-329`。
- 字号规模：`[12,14,16,18,20,24]px`。证据：`dashboard-header.vue:4-19`、`metric-card.vue:7-12`。
- 目标页面源码引用 31 种独特色彩，当前综合看板与壳层实际渲染 26 种。
- 主要文本最低对比度约 `2.17:1`，对象为“待交付成果”橙色数字；普通文字阈值应为 `4.5:1`，大号粗体最低 `3:1`。截图：`docs/audits/evidence/2026-07-13/01-dashboard.png`。
- empty/loading/error/success/focus/disabled 六类状态在源码中均存在，但供应商当前和旧入口都只得到 404，属于业务路由错误，不是被妥善设计的局部错误态。证据：`state-block/index.vue:3-34`、`docs/audits/evidence/2026-07-13/02-suppliers-current.png`、`03-suppliers-legacy.png`。
- 项目列表和旧发票列表视觉上完整，但都没有菜单入口。截图：`04-projects-direct.png`、`05-invoices-legacy.png`。

## 文案与诚实性证据

- “未检测到明显异常”实际只检查最近合同中的三类异常；标签范围大于算法范围。证据：`finance-view.vue:61-63,102-123`。
- “合同含税总额”直接展示通用 `contract_amount`，没有证明该字段一定含税。证据：`contracts/detail.vue:38-40`。
- 供应商“综合评级”“技术实力”“经营稳定性”分别来自简单启发式平均、软件著作权数量和成立年限，没有展示标准、数据时点和适用边界。证据：`suppliers/detail/index.vue:283-318,390-431`。
- 合同列表“导出”只提示“功能开发中”；合同详情“导出”没有事件；供应商“查看全部”没有行为。证据：`contracts/index.vue:33,222-224`、`contracts/detail.vue:28-29`、`suppliers/detail/index.vue:240-242`。
- 客户发票页面以“元”录入金额，却把原始数值直接标成“万元”。证据：`customer-finance/invoices/index.vue:20-22,147-148,300-301`。
- 看板告警卡父子组件分别执行导航且目标不一致。证据：`dashboard/overview/index.vue:74-83`、`alert-strip.vue:37-79`。
- 客户发票详情返回旧 `InvoiceList`；项目详情返回无菜单 `ProjectList`；供应商详情返回当前错误 `SupplierList`。证据：`customer-finance/invoices/detail.vue:379`、`projects/detail.vue:253`、`suppliers/detail.vue:621-623`。
- 未发现付费诱导、隐藏成本、假稀缺或确认羞辱等暗黑模式。

## 性能与摩擦证据

- 初始 JavaScript 编码体积约 `4,070,331B`，28 个脚本；最大单个脚本约 `3,607,760B`。
- 从登录到主视图 60 秒测量窗共 87 个网络请求，其中脚本 65 个。
- 一次冷启动在 `60,471ms` 内未达到可交互条件，最终显示 dashboard API 10 秒超时；另一次热路径可成功渲染，说明性能和运行状态不稳定。
- 空闲 Web Animations API 动画数为 0；初始通知、徽标和弹窗数为 0。
- 运行入口 `18090` 可用，但文档/CI 仍验证无监听的 `8900`，发布摩擦被错误端口掩盖。

## 可访问性证据

- 综合看板多个主要文本不满足 WCAG AA：风险数值 `2.17:1`、当前页签 `3.18:1`、待办标签 `3.70–3.91:1`、当前顶栏 `4.00:1`。
- 合同列表链接约 `3.24:1`；合同详情多组绿色、橙色、灰色和删除文字约 `1.11–3.37:1`，均低于相应阈值。
- 顶部一级菜单 `role=menuitem` 但 `tabIndex=-1`，键盘不可达。
- 看板 KPI/风险卡使用普通 `div` 点击，没有角色和 `tabIndex`。证据：`alert-strip.vue:3-8`、`metric-card.vue:2-5`。
- 合同列表依赖行点击进入详情，键盘动作列表中不可达。证据：`contracts/index.vue:197-205`。
- 登录页可聚焦按钮中有多个没有可访问名称；深色主题按钮 `tabIndex=-1`。
- 已渲染页面都没有 skip link；供应商错误页没有 ARIA landmark。

## 十原则对应事实

1. 创新：界面主要复用常见后台卡片、表格、Tab 和侧栏模式，没有发现独特且克制的新交互。
2. 有用：看板和列表提供真实业务指标，但供应商主任务当前 404，项目/旧发票任务需要绕过菜单。
3. 美学：存在基础间距和字号系统，但颜色数量、低对比度、新旧页面并存和多层导航形成明显不一致。
4. 易懂：菜单、路径、标题、标签和返回目标不一致；一次动作可能进入隐藏旧页面。
5. 克制：内容本身有价值，但顶部、侧栏、Tab 和大量卡片同时竞争注意力。
6. 诚实：没有暗黑模式，但多个标签、单位、评分和按钮与实际能力不一致。
7. 长久：标准后台骨架可延续，但 Emoji、渐变、过多圆角卡片和年度化模板痕迹容易老化。
8. 细致：六类状态存在，焦点样式也存在；键盘语义、对比度、路由错误和无效按钮仍粗糙。
9. 环保：无空闲动画是优点，但 4.07MB JS 和 87 请求明显超预算。
10. 极简：旧新路由、旧新页面和三层导航属于重复 affordance，许多元素不能证明必要性。

## 已知缺口

- 供应商列表和新版详情无法从当前构建正常进入，无法完成其完整 DOM/键盘检查；
- ECharts Canvas 文本未计入 DOM 对比度；
- 未覆盖深色、移动和高对比度模式；
- 未在远端生产环境复测；
- 合同详情通过运行时证据取得，但列表点击详情的完整链路受异步加载波动影响。
