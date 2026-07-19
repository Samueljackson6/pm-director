# 阶段3旧 Demo 设计证据

> 审计对象与边界见 `00-scope.md`。本文件只记录可复核事实，不把模拟数据视为生产事实。

## 1. 结构与交互面

- 8 个正常数据页面去重后共有 96 个交互控件；逐页快照合计 215 个，其中共享壳层 17 个、页面专属 79 个。来源：`prototypes/phase3-ui-demo/index.html:11-90`、`prototypes/phase3-ui-demo/app.js:167-285`。
- 13 行列表各提供两个进入同一固定详情的重复入口，共 13 对、26 个控件。来源：`prototypes/phase3-ui-demo/app.js:200,211,268`。
- 个人更多、合同分页、发票行等至少 7 个按钮没有业务行为；合同状态与负责人虽然可选，但应用筛选只读取关键词。来源：`prototypes/phase3-ui-demo/app.js:204,206,258,356-433`。
- 任意合同、项目、供应商行分别进入同一硬编码详情，未携带对象 ID。来源：`prototypes/phase3-ui-demo/app.js:200,211,268,368-371`。
- “项目交付物逾期”先进入合同详情再进入项目；“6 笔回款等待匹配”错误进入供应商发票页。来源：`prototypes/phase3-ui-demo/app.js:187-188,243,360-370`。

## 2. 视觉系统与可读性

- CSS 和内联样式共出现 22 档间距值、17 档字号值、110 种显式颜色字面量；基础尺度缺乏收敛。来源：`prototypes/phase3-ui-demo/styles.css:1-1290`、`prototypes/phase3-ui-demo/app.js:190,244,262,285`。
- 桌面截图的 248px 深色侧栏占画布约 17.2%；移动端深色供应商详情截图暗像素约 91.8%。来源：`prototypes/phase3-ui-demo/styles.css:34,37-56,141-160`、`docs/audits/阶段3Demo浏览器验收-20260715.md:73-75`。
- 浅色主题的弱化文字 `#98a2b3/#fff` 为 2.58:1；10px 成功、警告、危险徽标分别约 3.07:1、2.94:1、3.54:1，未达到普通文本 4.5:1。来源：`prototypes/phase3-ui-demo/styles.css:584-592,985-987`。
- 设计已提供 `prefers-reduced-motion`，但仍有两个持续运行的状态环动画。来源：`prototypes/phase3-ui-demo/styles.css:256,1281`、`prototypes/phase3-ui-demo/index.html:50`。

## 3. 文案与诚实性

- 页面持续显示“经营数据已连接”“实时 · 2 分钟前”“实时口径”，README 同时声明 Demo 不连接生产 API。来源：`prototypes/phase3-ui-demo/index.html:50,77`、`prototypes/phase3-ui-demo/app.js:175`、`prototypes/phase3-ui-demo/README.md:3`。
- 健康度、同比、排序、核验时间、自动匹配和企查查核验均无公式、来源、核验人或接口。来源：`prototypes/phase3-ui-demo/app.js:16-53,184-191,239,259,279,283`。
- 导出、新建、标记已处理以真实主操作呈现，点击后才提示占位或模拟。来源：`prototypes/phase3-ui-demo/app.js:412-417`。
- 固定泛行业样例使用 `HT/XM/GY` 编号，没有国网 `ZH02/SGSC` 多编号、科研成果、服务验收、质保金和供应商上下游关系。来源：`prototypes/phase3-ui-demo/app.js:55-75,218-285`。
- 当前数据库事实为 45 份合同、0 条供应商付款、0 条阶段—付款关联；旧稿却展示成熟的供应商开票付款闭环和统一履约链。来源：`database/project_management.db` 的 2026-07-15 只读聚合；业务证据见 `docs/深度需求分析与架构设计-v2.md` 与 `docs/合同详情页整体改造方案-20260711.md`。

## 4. 重量与摩擦

- 静态 Demo 首屏只有 HTML/CSS/JS 三个请求，初始 JS 43,787B，冷缓存 `loadEnd` 中位数约 259ms；受限网络与 4 倍 CPU 下约 2.07s。该数据不包含 Vben、权限路由和 API，不可外推到生产包。
- 全局搜索没有输入查询监听，永远展示 3 个固定对象；搜索返回不保存来源，合同分页不翻页。来源：`prototypes/phase3-ui-demo/index.html:97-103`、`prototypes/phase3-ui-demo/app.js:104-119,206,335-343`。
- 移动表格容器宽 356px、内容宽 880px，需要横向滚动约 524px，未固定首列/操作列，容器不能直接获得焦点。来源：`prototypes/phase3-ui-demo/styles.css:953-968,1224-1273`。

## 5. 无障碍

- 存在有效 Skip Link、主导航和 main landmark；原生按钮的主要动作可由键盘触发。来源：`prototypes/phase3-ui-demo/index.html:11,44,93`。
- 搜索 Dialog 与移动抽屉都没有焦点约束；关闭搜索后焦点留在隐藏元素。来源：`prototypes/phase3-ui-demo/app.js:335-353,441-449`。
- 四视图使用按钮但没有 tablist/tab 方向键模型；分页和发票编号虽可聚焦却无执行结果。来源：`prototypes/phase3-ui-demo/app.js:167-188,206,258,356-433`。
- 移动端显式按钮虽基本达到 WCAG 24px 最低目标，但大量控件仅 30–40px，不适合高频触控操作。

## 6. 框架兼容边界

- 信息表现大多可由现有 Vben/Ant Design Vue 实现，但静态壳不能直接移植：侧栏应由 `BasicLayout` 和后端菜单生成，表格应使用 `useVbenVxeGrid`，图表应使用 `EchartsUI/useEcharts`，主题应使用 Vben Preferences。来源：`docs/vben-framework-rules.md`、`ui-vben/docs/src/components/layout-ui/page.md`、`ui-vben/docs/src/components/common-ui/vben-vxe-table.md`。
- 当前生产合同详情已使用 `StateBlock`，项目详情已有 Descriptions、Steps、Timeline 和 VxeGrid；兼容性需要在真实 Vben 页面中验证，不能由静态 HTML 的相似外观证明。

## 7. 证据缺口

- 未把仓库内合同原件全文纳入旧 Demo 审计；合同业务模型采用既有 DOCX 调研、规则库和数据库只读聚合。
- 未用真实屏幕阅读器、真实手机 WebView、小程序或原生 App 验证。
- 性能数据仅代表本地静态 Demo，不代表 Vben 生产构建。
