# `/make-plan` 交接提示

```text
/make-plan Redesign PM Director 的全局导航、菜单路由、列表详情返回流程与核心业务页面。Current design failed audit at 7/30 with critical gaps in principles #2 useful, #4 understandable, #9 environmentally friendly, #10 as little design as possible.

Verdict paragraph (quoted from 03-verdict.md):
> REDESIGN：当前设计仅 7/30，且有用性、易懂性两个承重原则均为 0，必须重做信息架构、导航和主流程，不能只换皮。

Why redesign and not refine: 供应商核心入口不可用，项目和旧发票绕过菜单可达，返回动作进入隐藏旧页；这些问题发生在任务结构层，而不是颜色、圆角或间距层。

Primary user: 项目总监和项目管理人员。
Primary task: 快速判断合同、项目、开票、回款、付款和风险状态，并从列表进入详情、查看关联对象后可靠返回原工作上下文。
Constraints: 保留 Vue 3、Vben Admin 5、Ant Design Vue、FastAPI；中文界面；WCAG 2.1 AA；先设计后实现；数据单位与状态必须可追溯；旧路径必须有明确退役期限。

Preserve from current design:
- Vue/Vben/Ant Design Vue 技术栈和暗色算法接入，见 ui-vben/apps/web-antd/src/app.vue:16-35。
- 财务语义 Token 的集中管理方向，见 ui-vben/apps/web-antd/src/styles/finance-tokens.css:1-23；允许为 WCAG AA 调整色值。
- 统一加载/错误/空态组件方向，见 ui-vben/apps/web-antd/src/components/state-block/index.vue:3-34。
- 综合看板的核心业务指标与四视图概念；迁移前先确认金额、状态和风险口径。

Discard:
- backend 模式下无条件合并业务静态路由。Evidence: ui-vben/packages/utils/src/helpers/generate-routes-backend.ts:55-56. Caused failure on principles #2, #4, #10.
- 顶部一级菜单、侧栏、页面 Tab 同时承担同级导航。Evidence: docs/audits/evidence/2026-07-13/01-dashboard.png. Caused failure on principles #4, #5, #10.
- 新页面主动跳回旧 InvoiceList/ProjectList/SupplierList，且不保留来源。Evidence: customer-finance/invoices/detail.vue:379, projects/detail.vue:253, suppliers/detail.vue:621-623. Caused failure on principles #2, #4, #6.
- 没有口径的“综合评级/优秀/全域”与元值直接标万元。Evidence: suppliers/detail/index.vue:283-318, customer-finance/invoices/index.vue:20-22,147-148. Caused failure on principle #6.

Top 3–5 moves from the audit (verbatim):
1. 原则 #2/#4 — 有用且易懂：确定唯一菜单/路由真值，重建“列表 → 详情 → 关联对象 → 返回来源”的显式契约，并让供应商、项目、发票都通过同一入口体系可达。证据：generate-routes-backend.ts:55-56、projects/detail.vue:253、供应商 404 截图。
2. 原则 #6 — 诚实：建立金额单位、状态、风险和评分的语义契约，删除或改写所有无行为按钮、夸大标签和原值错标“万元”的展示。证据：customer-finance/invoices/index.vue:20-22,147-148、contracts/index.vue:222-224。
3. 原则 #10 — 尽可能少：只保留一套全局导航，退役旧 /invoices、重复合同路径、旧供应商页和重复页面 Tab/侧栏 affordance。证据：routes/index.ts:7-16,36、综合看板运行截图。
4. 原则 #8 — 细致：把可点击卡片和表格行改成语义化键盘控件，补 skip link，并把主要文本对比度统一提高到 WCAG AA；供应商错误必须在模块内恢复或给出明确迁移。证据：alert-strip.vue:3-8、contracts/index.vue:197-205、最低对比度 2.17:1。
5. 原则 #9 — 资源克制：按业务路由拆分上游模块，设置首屏 JS、请求数和 TTI 性能预算，部署后以真实构建指纹和性能烟测验收。证据：初始 JS 4.07MB、87 请求、TTI >60s。

Redesign principles in priority order:
1. Principle #2 useful — 每个一级业务任务从唯一菜单进入，核心任务不经过 404、隐藏旧页或兼容层。
2. Principle #4 understandable — 用户始终知道自己在哪、从哪里来、返回哪里；同一对象只存在一个规范 URL 和名称。
3. Principle #6 honest — 金额、状态、风险、评分和按钮名称与真实数据和行为一一对应。
4. Principle #10 as little design as possible — 只保留一套全局导航和一套业务页面；每个元素都能证明必要性。
5. Principle #9 environmentally friendly — 首屏 JS 和请求数有预算，路由按需加载，稳定达到可交互标准。

Deliverables for the plan:
- New information architecture not derived from the old menu; include a canonical route registry with owner, path, component, visibility, old redirects, and retirement date.
- New primary flow low-fi wireframe for dashboard → contract list → contract detail → project detail → return, compared side-by-side to current.
- Secondary flow for customer invoice → detail → receipt → return, plus supplier list → detail → finance objects → return.
- Data display contract for IDs, amount units, statuses, risk labels, verification timestamp, and unknown values.
- Token decisions: type scale, spacing scale, semantic colors with WCAG AA, color-count cap, table density, and number formatting.
- States checklist: empty, loading, error, success, focus, disabled, unauthorized, stale-build, and data-unverified.
- Accessibility plan: semantic clickable controls, full keyboard path, landmarks, skip link, mobile and dark-mode verification.
- Performance budgets for initial JS, request count, TTI, and route chunks.
- Migration path for users currently on old /invoices, /projects, duplicate contract paths, and old supplier routes.
- Cutover criteria: route E2E green, old paths only redirect, deployed SHA matches, foreign-key/data checks pass, and user acceptance completed.

Out of scope for the first redesign plan:
- Replacing Vue/Vben/FastAPI.
- Adding new business modules.
- Silently auto-correcting uncertain contract or financial data.
- Redesigning remote production infrastructure beyond versioned build/deploy verification.

Anti-patterns to guard against:
- Porting the old structure under new styling.
- Keeping old and new designs behind a flag indefinitely.
- Redesigning to follow a trend rather than the principles above.
- Treating the Preserve list as optional.
- Starting implementation before the canonical route registry and data display contract are approved.
```
