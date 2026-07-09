# UI 设计规范

> Vben Admin 5 前端框架 UI 设计指南
> 最后更新：2026-07-09

## 1. 组件库使用规范

### 必须使用 Vben Admin 5 组件库

**优先使用以下组件**：

| 组件 | 用途 | 示例 |
|------|------|------|
| `a-card` | 卡片容器 | 基本信息、财务汇总、合同条款等区块 |
| `a-descriptions` | 结构化数据展示 | 合同基本信息、项目详情等 |
| `a-table` | 列表数据 | 合同列表、发票列表、交付物列表等 |
| `a-timeline` | 时间线 | 付款进度、项目阶段等 |
| `a-tag` | 状态标签 | 合同状态、发票状态、付款状态等 |
| `a-progress` | 进度条 | 回款率、项目进度等 |
| `a-statistic` | 统计卡片 | 合同金额、已开票、已回款等 |
| `a-collapse` | 折叠面板 | 合同条款分组展示 |
| `a-tabs` | 标签页 | 合同详情多区块切换 |
| `a-badge` | 徽标 | 未读消息、待处理任务等 |

**禁止使用**：

- ❌ 自定义 `.panel` 类（已废弃，改用 `a-card`）
- ❌ 未定义 CSS token（如 `var(--border)` 等，除非已在全局定义）
- ❌ 硬编码颜色值（应使用 Vben 的主题色变量）

### 组件使用示例

#### 基本信息卡片（推荐）

```vue
<a-card title="基本信息" size="small">
  <a-descriptions :column="2" size="small" bordered>
    <a-descriptions-item label="合同编号" :span="2">{{ contract.contract_id }}</a-descriptions-item>
    <a-descriptions-item label="合同金额">{{ contract.contract_amount?.toFixed(2) }} 万元</a-descriptions-item>
    <a-descriptions-item label="合同状态">
      <a-tag :color="statusColor(contract.contract_status)">{{ contract.contract_status }}</a-tag>
    </a-descriptions-item>
  </a-descriptions>
</a-card>
```

#### 统计卡片（推荐）

```vue
<a-card size="small">
  <a-statistic
    title="合同金额"
    :value="contract.contract_amount"
    :precision="2"
    suffix="万元"
    :value-style="{ color: '#3f8600' }"
  />
</a-card>
```

## 2. 动画/图形效果规范

### 必须使用动画/图形效果

- **页面切换动画**：使用 `transition` 或 `animate.css`
- **数据加载骨架屏**：使用 `a-skeleton`
- **图表展示**：使用 `echarts` 或 `v-charts`
- **进度展示**：使用 `a-progress` 或自定义 CSS 动画
- **甘特图/时间线**：使用专业组件（如 `v-gantt-chart` 或自定义 SVG）

### 骨架屏示例

```vue
<a-skeleton :loading="loading" active>
  <!-- 实际内容 -->
</a-skeleton>
```

### 页面切换动画

```vue
<transition name="fade" mode="out-in">
  <component :is="currentView" />
</transition>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
```

## 3. 数据展示规范

### 结构化展示

- **基本信息**：使用 `a-descriptions`（bordered 模式）
- **列表数据**：使用 `a-table`（带分页、排序、筛选）
- **时间线**：使用 `a-timeline`（带状态颜色）
- **统计卡片**：使用 `a-statistic` + 图标
- **状态标签**：使用 `a-tag` 颜色区分

### 视觉层次

- **重要数据**：大字号 + 颜色强调（如合同金额、回款率）
- **次要数据**：小字号 + 灰色（如创建时间、更新时间）
- **状态标签**：使用 `a-tag` 颜色区分
  - `green`：已完成/已签订
  - `blue`：进行中/执行中
  - `gray`：待处理/草稿
  - `red`：异常/逾期/已解除
  - `orange`：违约金/逾期

### 状态标签颜色规范

| 状态 | 颜色 | 使用场景 |
|------|------|----------|
| 已签订/已完成 | `green` | 合同状态、付款状态 |
| 执行中/进行中 | `blue` | 项目状态、阶段状态 |
| 待处理/草稿 | `gray` | 合同状态、发票状态 |
| 逾期/异常 | `red` | 付款逾期、合同异常 |
| 违约金/罚款 | `orange` | 合同条款、罚款金额 |

## 4. 响应式设计

### 栅格布局

```vue
<!-- 移动端：1 列，桌面端：2 列 -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
  <a-card>...</a-card>
  <a-card>...</a-card>
</div>
```

### 表单布局

```vue
<!-- 移动端：1 列，桌面端：2 列 -->
<a-form :label-col="{ span: 24 }" :wrapper-col="{ span: 24 }">
  <a-row :gutter="16">
    <a-col :xs="24" :sm="12" :md="8">
      <a-form-item label="合同编号">
        <a-input v-model="contract_id" />
      </a-form-item>
    </a-col>
  </a-row>
</a-form>
```

## 5. 代码规范

### 组件文件结构

```vue
<template>
  <!-- 使用 a-card 作为区块容器 -->
  <a-card title="区块标题" size="small">
    <!-- 内容 -->
  </a-card>
</template>

<script lang="ts" setup>
// 使用 TypeScript，禁止 any 类型
interface Contract {
  contract_id: string
  contract_amount: number
  // ...
}
</script>

<style scoped>
/* 使用 scoped 样式，避免全局污染 */
/* 禁止使用未定义 CSS token */
</style>
```

### 逻辑处理

- 使用 `computed` 处理复杂逻辑（禁止模板内复杂表达式）
- 使用 `ref` / `reactive` 管理状态
- 使用 `onMounted` / `onUnmounted` 管理生命周期

## 6. 检查清单

**每次前端开发完成后，必须检查**：

- [ ] 使用了 Vben Admin 5 组件库（非自定义类）
- [ ] 数据展示结构化（非一段文字）
- [ ] 状态标签颜色符合规范
- [ ] 有加载状态（骨架屏或 loading）
- [ ] 有错误状态（错误提示或空状态）
- [ ] 响应式布局（移动端适配）
- [ ] 使用 TypeScript（非 any 类型）
- [ ] 使用 scoped 样式（非全局污染）
