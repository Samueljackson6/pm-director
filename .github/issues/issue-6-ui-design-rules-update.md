# Issue #6：更新项目规范和开发约束（UI 设计规范）

## 问题描述
当前项目缺乏明确的 UI 设计规范，导致前端组件使用不一致，视觉效果差。

## 规范要求（新增）

### 1. 组件库使用规范
- **必须使用 Vben Admin 5 的组件库**，优先使用以下组件：
  - `a-card` / `a-descriptions` / `a-table` / `a-timeline` / `a-tag` / `a-progress`
  - `a-collapse` / `a-tabs` / `a-badge` / `a-statistic`
  - Vben 自带的 `VbenCard` / `VbenDescriptions` 等封装组件
- **禁止使用**：
  - 自定义 `.panel` 类（已废弃，改用 `a-card`）
  - 未定义 CSS token（如 `var(--border)` 等，除非已在全局定义）
  - 硬编码颜色值（应使用 Vben 的主题色变量）

### 2. 动画/图形效果规范
- **必须使用 Vben Admin 5 的动画/图形效果**：
  - 页面切换动画（`transition` / `animate.css`）
  - 数据加载骨架屏（`a-skeleton`）
  - 图表组件（`echarts` / `v-charts`）
  - 进度条动画（`a-progress` / 自定义 CSS 动画）
- **甘特图/时间线**：使用专业组件（如 `v-gantt-chart` 或自定义 SVG）

### 3. 数据展示规范
- **结构化展示**：
  - 基本信息：使用 `a-descriptions`（bordered 模式）
  - 列表数据：使用 `a-table`（带分页、排序、筛选）
  - 时间线：使用 `a-timeline`（带状态颜色）
  - 统计卡片：使用 `a-statistic` + 图标
- **视觉层次**：
  - 重要数据：大字号 + 颜色强调
  - 次要数据：小字号 + 灰色
  - 状态标签：使用 `a-tag` 颜色区分

### 4. 响应式设计
- 使用 `grid grid-cols-1 lg:grid-cols-N` 响应式布局
- 移动端适配（Vben Admin 5 已内置）

### 5. 代码规范
- 组件文件必须包含 `<style scoped>`（避免全局污染）
- 使用 TypeScript（禁止 `any` 类型）
- 使用 `computed` 处理复杂逻辑（禁止模板内复杂表达式）

## 更新文件
- `RULES.md`（项目规范）
- `docs/开发约束.md`（开发约束）

## 优先级
高（影响所有前端开发）

## 验收标准
- [ ] `RULES.md` 新增 UI 设计规范章节
- [ ] `docs/开发约束.md` 更新组件库使用规范
- [ ] 所有前端组件符合新规范（逐步重构）
- [ ] 新增组件必须使用 Vben 组件库
