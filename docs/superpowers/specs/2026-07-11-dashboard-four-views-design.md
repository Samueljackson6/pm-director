# 综合驾驶舱四视图重构设计

> 日期：2026-07-11
> 状态：用户已确认

## 目标

将当前单一综合看板重构为一个统一的驾驶舱中心，在同一路由下提供四个可切换视图：

1. 全域总览：面向全部用户，展示经营、项目、财务、风险和近期变化。
2. 经营管理：面向负责人，突出规模、回款、客户集中度和异常合同。
3. 项目执行：面向项目经理，突出项目状态、风险、负责人缺失、阶段和交付物。
4. 财务回款：面向财务，突出合同→开票→回款漏斗、趋势和待办异常。

## 核心决策

- 保留 `/dashboard/overview/index` 单一路由。
- 使用四个 Tab，通过 `?view=all|management|projects|finance` 保存视图状态。
- 不引入新依赖，不实现拖拽和用户自定义布局。
- 复用现有 ECharts、VxeTable、StateBlock 和 dashboard 图表组件。
- 后端现有字段保持兼容，只新增 `project_execution` 聚合对象。
- 所有金额展示统一为万元。
- 全域视图负责全量信息，三个场景视图负责聚焦，不重复复制页面逻辑。

## 信息架构

### 公共头部

- 页面名称和一句话说明。
- 数据生成时间与金额单位。
- 手动刷新按钮。
- 四视图 Tab。

### 全域总览

- 六个核心指标：合同额、合同数、已开票、已回款、回款率、待办总数。
- 四项行动预警：未匹配回款、待交付、逾期付款、未开票合同。
- 合同类型、状态、客户结构。
- 月度财务趋势。
- 项目执行摘要。
- 最近合同列表。

### 经营管理

- 六项经营 KPI。
- 合同类型与状态分布。
- Top 客户。
- 月度开票/回款趋势。
- 经营异常摘要。

### 项目执行

- 项目总数、进行中、已完成、高风险、缺负责人、待交付。
- 项目状态与风险分布。
- 最近项目列表。
- 数据缺失必须显示为待补充，不生成虚假进度。

### 财务回款

- 合同总额→已开票→已回款漏斗。
- 未开票、未回款、回款率。
- 月度趋势和批次趋势。
- 发票状态分布。
- 财务待办和异常提示。

## 视觉系统

- 专业运营控制台，不使用炫酷大屏风格。
- 主色 `#1677FF`，回款 `#16A36A`，开票 `#0F8FA8`，预警 `#D98E04`，风险 `#D64545`。
- 优先使用主题 class/token；图表颜色集中配置，不在视图中散落硬编码。
- KPI 卡片建立主次：关键金额卡更宽，预警卡更紧凑。
- 响应式支持 1440px、1024px 和窄屏，不允许横向溢出。

## 数据接口

现有 `/api/dashboard/overview` 保持兼容，新增：

```ts
project_execution: {
  total_projects: number
  active_projects: number
  completed_projects: number
  high_risk_projects: number
  missing_manager_projects: number
  overdue_stages: number
  pending_deliverables: number
  status_distribution: Array<{ status: string; count: number }>
  risk_distribution: Array<{ risk_level: string; count: number }>
  recent_projects: Array<{
    project_id: string
    project_name: string
    customer_name: string
    project_status: string
    risk_level: string
    overall_progress: number
    project_manager: string
    planned_end: string
    total_contract_amount: number
  }>
}
```

聚合查询必须在后端单次完成，禁止对每个项目调用详情接口。

## 错误与空状态

- 页面统一使用 StateBlock 管理 loading/error。
- 每个图表组件负责自己的空数据状态。
- 项目团队或时间缺失显示“待补充”，不能用 0 或正常状态掩盖。
- 刷新失败保留当前视图并显示可重试错误。

## 验收标准

- 四个 Tab 可切换并写入 URL Query。
- 刷新页面后保留当前视图。
- 后端旧字段完全兼容。
- 全域、经营、项目、财务四个视图均有明确主次。
- 加载、错误、空数据状态完整。
- 无新增 console error、pageerror、HTTP 失败。
- 后端测试、前端 Vitest、生产构建通过。
- dashboard 相关 TypeScript 错误为 0。
- Playwright 验证 1440px 与窄屏无横向溢出。
