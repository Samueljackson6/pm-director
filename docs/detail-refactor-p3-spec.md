# 合同详情页 P3 视觉改版 —— 实施 Spec

> 方向：A 经典仪表盘骨架（KPI 横排 + 双列网格）+ B 吸顶锚点条 + 科研类保留甘特图
> 目标：让页面"看起来变了"——紧凑现代卡片、清晰层级、快捷导航、更好留白
> 当前应用为浅色模式，本 spec 聚焦浅色现代化；深色主题留作后续

## 1. 卡片样式规范（统一应用到所有区块）

**废弃**：`rounded-xl shadow-sm` + ant-design `a-card` 的默认阴影
**改用**自定义 div 卡片：

```
容器: bg-white rounded-lg border border-gray-200 overflow-hidden
头部: flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50
  ├ 左色条: w-1 h-4 rounded-full bg-<区块色>
  ├ 标题: text-sm font-semibold text-gray-700
  └ 右侧操作(可选): extra slot
体: px-5 py-4
```

**区块色映射**（左色条颜色，区分区块语义）：
| 区块 | 色 | Tailwind |
|------|----|---------|
| 基本信息 | 蓝 | bg-blue-500 |
| 服务内容/阶段 | 青 | bg-teal-500 |
| 付款进度 | 橙 | bg-amber-500 |
| 项目团队 | 紫 | bg-purple-500 |
| 关联项目·文件 | 灰 | bg-gray-400 |
| 合同条款 | 石板 | bg-slate-400 |

## 2. KPI 紧凑现代化

旧：5 个大卡片，三行（标签/数字/单位）
新：更紧凑，大数字 + 小标签 + 语义色

```
卡: bg-white rounded-lg border border-gray-200 p-4 text-center
标签: text-xs text-gray-400 mb-1
数字: text-2xl font-bold + 语义色
单位: text-xs text-gray-400 mt-0.5
```
数字语义色：合同金额(text-gray-900) / 已开票(text-blue-600) / 已回款(text-green-600) / 未回款(text-red-500) / 执行进度(text-purple-600)

## 3. 吸顶锚点条（新增，B 的精华）

**位置**：KPI 行下方，sticky 吸顶
**结构**：
```
容器: sticky top-0 z-20 bg-white/80 backdrop-blur-sm border-y border-gray-200
按钮组: flex gap-1 px-4 py-2 overflow-x-auto
  每个锚点按钮: px-3 py-1.5 text-sm rounded-md whitespace-nowrap
  默认: text-gray-500 hover:bg-gray-100
  当前高亮: bg-blue-50 text-blue-600 font-medium
```
**锚点项**：概览 · 服务内容 · 阶段 · 付款 · 团队 · 条款
（服务类无"阶段"，动态隐藏该项）

**JS 交互**（scroll spy）：
- 用 IntersectionObserver 监听各区块（id=overview/content/payment/team/clauses）
- 进入视口则高亮对应锚点
- 点击锚点 → `scrollIntoView({behavior:'smooth', block:'start'})`，预留吸顶高度

## 4. 布局结构（A 骨架）

```
┌──────────────────────────────────────────┐
│ 标题栏（sticky top-0 z-30）               │
│   ← 返回 | 合同名·编号·状态 | [编辑][导出] │
├──────────────────────────────────────────┤
│ KPI 行（5 卡横排，全宽）            id 无  │
├──────────────────────────────────────────┤
│ 锚点条（sticky top-[标题栏高] z-20）       │
├──────────────────────────────────────────┤
│ 基本信息（全宽，紧凑横排单卡）    id=overview
├──────────────────────────────────────────┤
│ 【类型切换区】（全宽，主内容）    id=content
│   服务类 → ServiceContent(6字段)          │
│   科研类 → ResearchContent(阶段+甘特+预算) │
├──────────────────────────────────────────┤
│ 付款进度（全宽）                  id=payment
├──────────────────┬───────────────────────┤
│ 项目团队（6/12）  │ 关联项目·文件（6/12）  │ id=team
├──────────────────┴───────────────────────┤
│ 合同条款·保密（全宽，折叠）       id=clauses
└──────────────────────────────────────────┘
```

**网格**：双列行用 `grid grid-cols-1 md:grid-cols-2 gap-4`；全宽区块直接堆叠。

## 5. 改造清单

### 5.1 detail.vue（外壳，主战场）
- 标题栏加 `sticky top-0 z-30 bg-white/90 backdrop-blur`
- KPI 卡片 class 更新为新规范（§2）
- 新增锚点条模板 + scroll spy 脚本（§3）
- 各区块套用新卡片样式（§1）+ 加 id 锚点
- 项目团队 / 关联项目 改为双列网格（§4）
- 保留：类型切换区 `<ResearchContent>/<ServiceContent>` 逻辑、付款、条款功能不变

### 5.2 ServiceContent.vue / ResearchContent.vue（子组件）
- 内部卡片对齐 §1 新样式规范（左色条 + 头部 + 体）
- ResearchContent 的甘特图卡片强化：标题"阶段进度（甘特图）"保留，色条用青色
- 功能/props/emits 不变

### 5.3 不动的东西
- 所有数据逻辑、API、props、emit 链路
- 编辑弹窗（P2 已做，不动）
- 甘特图组件本身（stage-gantt.vue）

## 6. 执行分工

| 部分 | 执行方 | 理由 |
|------|--------|------|
| 锚点条 + scroll spy JS | **主会话** | 视觉交互核心，需 IntersectionObserver 逻辑，不宜委托 |
| detail.vue 外壳卡片样式 + KPI + 双列 | lite 子代理 | 按 spec 机械套用 class，可委托 |
| 子组件卡片样式对齐 | lite 子代理 | 机械套用 |

## 7. 验证清单
- [ ] `pnpm run build:antd` 零错误
- [ ] 两类合同详情页视觉明显现代化（卡片紧凑、色条、层级清晰）
- [ ] 锚点条吸顶 + 点击平滑滚动 + 滚动高亮联动
- [ ] KPI 数字语义色正确
- [ ] 双列布局在宽屏生效、窄屏回退单列
- [ ] 编辑/付款/条款等功能不受影响
