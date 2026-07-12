# 合同详情页 A2 改造 —— P1 实施 Spec

> 本文档是 lite 子代理的组装蓝图。**按图组装，不要自行设计**。所有模板块用注释标记定位（如 `<!-- 付款进度 -->`），不要用行号（行号会漂移）。
> 主会话负责验收：读组件 + 构建验证。

## 0. 背景与边界

- 架构 A2：`detail.vue`(外壳) 按 `project_type` 切换 `ResearchContent.vue` / `ServiceContent.vue`。
- 外壳保留公共块：标题栏 / KPI / 基本信息(仅签约·双方·验收·中标·分包) / 项目团队 / 合同条款 / 关联项目 / 文件。
- 服务字段(6个)、阶段、预算、交付物、付款 → 移入子组件。
- 付款 CRUD 两类相同但本阶段各自内联（P1d 再抽共享 `PaymentEditor.vue`）。

## 1. 通用约定

### 1.1 文件位置
```
ui-vben/apps/web-antd/src/views/contracts/components/
├── stage-gantt.vue          (已存在，复用)
├── ServiceContent.vue       (新建, P1a)
└── ResearchContent.vue      (新建, P1b)
```

### 1.2 props / emits 规范
- 子组件**不自己 fetch 数据**，数据由外壳传入。
- 付款增删后需要刷新：子组件 `emit('reload')`，外壳监听后调 `load()`。
- `contractId` 单独传入（用于付款 API 调用）。

### 1.3 共享依赖（两个子组件都要 import）
```ts
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import { createPaymentApi, deletePaymentApi } from '#/api/contracts'
```
- `fmtMoney`：每个子组件各自复制（4 行，不值得抽公共）：
  ```ts
  function fmtMoney(n: number | null | undefined): string {
    if (n == null) return '0.00'
    return n.toFixed(2)
  }
  ```

### 1.4 付款 CRUD（每个子组件内联一份）
从 `detail.vue` 复制付款相关 state + 方法，做一处修改：`load()` → `emit('reload')`。
```ts
const addPaymentVisible = ref(false)
const paymentSaving = ref(false)
const paymentForm = ref<Record<string, any>>({})

function openAddPaymentModal() {
  paymentForm.value = { payment_stage: '', planned_amount: 0, planned_date: '', status: 'pending', payment_condition: '' }
  addPaymentVisible.value = true
}
async function savePayment() {
  paymentSaving.value = true
  try {
    await createPaymentApi(props.contractId, paymentForm.value)
    message.success('付款记录已添加')
    addPaymentVisible.value = false
    emit('reload')   // ← 唯一修改：原 load() 改为 emit
  } catch (e: any) {
    message.error('添加失败: ' + (e?.message || '未知错误'))
  } finally { paymentSaving.value = false }
}
async function deletePayment(p: any) {
  if (!p?.payment_id) return
  try {
    await deletePaymentApi(props.contractId, p.payment_id)
    message.success('付款记录已删除')
    emit('reload')   // ← 同上
  } catch (e: any) { message.error('删除失败: ' + (e?.message || '未知错误')) }
}
```

### 1.5 paymentsView / paymentsTotal（每个子组件内联一份）
从 `detail.vue` 复制，把 `payments.value` 改为 `props.payments`：
```ts
const paymentsView = computed(() => {
  return props.payments.map((p: any) => {
    const isPaid = p.status === 'paid' || p.status === 'completed' || p.status === '已支付'
    const plannedAmount = Number(p.planned_amount) || 0
    const statusLabel = p.status === 'paid' || p.status === '已支付' ? '已支付'
      : p.status === 'pending' || p.status === '待支付' ? '待支付' : p.status || '待支付'
    return { ...p, planned_amount: plannedAmount, isPaid, statusLabel }
  })
})
const paymentsTotal = computed(() => {
  const planned = paymentsView.value.reduce((sum: number, p: any) => sum + (p.planned_amount || 0), 0)
  return { planned, paid: 0 }
})
```

### 1.6 添加付款弹窗模板（每个子组件内联一份）
从 `detail.vue` 的 `<!-- ============ 添加付款弹窗 ============ -->` 区块复制，字段保持：payment_stage / planned_amount / planned_date / status / payment_condition。无需修改。

---

## 2. ServiceContent.vue (P1a) —— 技术服务类

### 2.1 props / emits
```ts
const props = defineProps<{
  contract: Record<string, any> | null
  payments: any[]
  contractId: string
}>()
const emit = defineEmits<{ (e: 'reload'): void }>()
```

### 2.2 模板结构
```
<a-card title="服务内容">
  6 字段网格 grid-cols-1 md:grid-cols-2 gap-4:
    1. 服务内容 service_content   (长文本可折叠, 复用 detail.vue 110-131 的折叠逻辑, c→props.contract, serviceExpanded 本地 ref)
    2. 服务方式 service_method
    3. 服务地点 service_location
    4. 服务期限 service_period
    5. 服务进度 service_schedule   ← 新增(原本无渲染)
    6. 服务质量 service_quality    ← 新增(原本无渲染)
  每个字段块结构:
    <div v-if="props.contract?.<field>">
      <div class="text-xs text-gray-400 mb-1"><标签></div>
      <div class="font-medium text-gray-900 text-sm">{{ props.contract.<field> }}</div>
    </div>
  标签映射: service_content→服务内容, service_method→服务方式, service_location→服务地点,
           service_period→服务期限, service_schedule→服务进度, service_quality→服务质量
</a-card>

<a-card title="付款进度">  ← 从 detail.vue 470-562 整块复制, payments→props.payments, 其余不变
  ... (付款汇总 + 付款卡片列表 + 添加付款按钮 + 空状态)
</a-card>

<!-- 添加付款弹窗 -->  ← 1.6
```

### 2.3 关键修复
- **G1**: service_schedule / service_quality 必须渲染（之前完全没显示）。
- **G4**: service_period 只在本组件显示一次，外壳 basic info 不再放 service_period（外壳侧由 P1c 处理）。
- 服务内容折叠：`serviceExpanded = ref(false)` 本地持有。

### 2.4 不要做的事
- 不要渲染阶段/预算/交付物（那是 ResearchContent）。
- 不要加"对应阶段"列（那是科研类 R1）。

---

## 3. ResearchContent.vue (P1b) —— 科研类

### 3.1 props / emits
```ts
const props = defineProps<{
  contract: Record<string, any> | null
  stages: any[]
  budgets: any[]
  deliverables: any[]
  payments: any[]
  contractId: string
}>()
const emit = defineEmits<{ (e: 'reload'): void }>()
```

### 3.2 需要复制的逻辑（从 detail.vue）
- `StageGantt` import: `import StageGantt from '#/views/contracts/components/stage-gantt.vue'`
- `hasValidStages` / `validStages`：复制，`stages.value` → `props.stages`
  ```ts
  const hasValidStages = computed(() => {
    if (!props.stages.length) return false
    return props.stages.some((s: any) => s.start_time || s.end_time)
  })
  const validStages = computed(() => props.stages.filter((s: any) => s.start_time || s.end_time))
  ```
- `stageColumns`：原样复制
  ```ts
  const stageColumns = [
    { title: '阶段', key: 'stage_number', width: 130 },
    { title: '阶段内容', key: 'remarks', ellipsis: true },
    { title: '考核目标', key: 'acceptance_criteria', ellipsis: true },
    { title: '时间', key: 'time', width: 200 },
    { title: '状态', key: 'status', width: 80, align: 'center' as const },
  ]
  ```
- `parseCriteriaText` / `extractStageTime`：原样复制（纯函数，无依赖）

### 3.3 R1 新增：对应阶段解析函数
```ts
// 从 payment_condition 解析"研究阶段5.x~5.y"用于 R1 对应阶段列
function parseStageRef(condition: string | null | undefined): string {
  if (!condition) return ''
  const m = condition.match(/研究阶段\s*5\.\d+(?:\s*[~至\-–]\s*5\.\d+)?/)
  return m ? m[0] : ''
}
```

### 3.4 模板结构
```
<!-- 阶段进度 - 甘特图 -->  ← 从 detail.vue 405-468 整块复制, stages→props.stages, validStages/hasValidStages 用本地
<a-card title="阶段进度（甘特图）">
  <stage-gantt :stages="validStages" :deliverables="props.deliverables" v-if="hasValidStages" />
  <阶段详情表 ... />  (columns=stageColumns, dataSource=props.stages)
  <空状态 v-if="!props.stages.length" />
</a-card>

<!-- 交付物 -->  ← 从 detail.vue 564-606 整块复制, deliverables→props.deliverables
<a-card title="交付物成果" v-if="props.deliverables.length > 0"> ... </a-card>
<a-card v-else title="交付物成果"><a-empty /></a-card>

<!-- 经费预算 -->  ← 从 detail.vue 608-636 整块复制, budgets→props.budgets
<a-card v-if="props.budgets.length > 0" title="经费预算"> <a-table :data-source="props.budgets" .../> </a-card>

<!-- 付款进度 (R1) -->  ← 从 detail.vue 470-562 复制 + 在付款卡片内加"对应阶段"徽标
<a-card title="付款进度">
  <付款汇总 ... />
  <付款卡片列表 v-for="(p, idx) in paymentsView">
    ... 原有内容 ...
    <!-- R1 新增: 对应阶段徽标, 放在 payment_stage 旁边 -->
    <a-tag v-if="parseStageRef(p.payment_condition)" color="cyan" size="small" class="ml-2">
      {{ parseStageRef(p.payment_condition) }}
    </a-tag>
    ...
  </付款卡片列表>
  <添加付款按钮 @click="openAddPaymentModal" />
  <空状态 v-else />
</a-card>

<!-- 添加付款弹窗 -->  ← 1.6
```

### 3.5 关键修复
- **G3 显示侧**: 阶段表已有 remarks 列（stageColumns 含 '阶段内容' key='remarks'），保持渲染 `record.remarks`。编辑侧 G3 留 P2。
- **R1**: 付款卡片显示"对应阶段"徽标（从 payment_condition 解析）。

---

## 4. detail.vue 外壳重构 (P1c)

### 4.1 新增 import
```ts
import ResearchContent from '#/views/contracts/components/ResearchContent.vue'
import ServiceContent from '#/views/contracts/components/ServiceContent.vue'
```

### 4.2 新增 computed
```ts
const isResearch = computed(() => c.value?.project_type === '科研类')
const isService = computed(() => c.value?.project_type === '技术服务类')
```

### 4.3 模板：要删除的区块
从 `detail.vue` 模板中**删除**以下区块（它们移入子组件）：
1. `<!-- 服务信息 -->` 区块（含 service_period 单字段）
2. `<!-- 服务内容（长文本可折叠） -->` 区块
3. `<!-- 服务详情（服务类合同） -->` 区块（含 service_period/method/location）
4. `<!-- ============ 阶段进度 - 甘特图 ============ -->` 整个 a-card
5. `<!-- ============ 付款进度 ============ -->` 整个 a-card
6. `<!-- ============ 交付物 ============ -->` 整个 a-card（含 v-if 和 v-else 两个）
7. `<!-- ============ 经费预算（科研类） ============ -->` 整个 a-card
8. `<!-- ============ 添加付款弹窗 ============ -->` 整个 a-modal

### 4.4 模板：在删除位置插入类型切换
在原"阶段进度"卡片的位置（删除区上方/下方均可，建议放在基本信息卡之后、项目团队之前）插入：
```html
<!-- ============ 按合同类型切换内容区 ============ -->
<ResearchContent
  v-if="isResearch"
  :contract="c"
  :stages="stages"
  :budgets="budgets"
  :deliverables="deliverables"
  :payments="payments"
  :contract-id="contractId"
  @reload="load"
/>
<ServiceContent
  v-else-if="isService"
  :contract="c"
  :payments="payments"
  :contract-id="contractId"
  @reload="load"
/>
```

### 4.5 script：可删除的项（已移入子组件）
删除以下仅被移走区块使用的逻辑（保留外壳仍需要的）：
- `serviceExpanded` ref（移入 ServiceContent）
- `stageColumns` / `hasValidStages` / `validStages` / `parseCriteriaText` / `extractStageTime`（移入 ResearchContent）
- 付款 CRUD：`addPaymentVisible` / `paymentSaving` / `paymentForm` / `openAddPaymentModal` / `savePayment` / `deletePayment`（移入两个子组件）
- `paymentsView` / `paymentsTotal`（移入两个子组件）

**保留**外壳仍用的：`fmtMoney`（KPI 用）、`c`/`stages`/`payments`/`deliverables`/`budgets` computed（传给子组件）、`load()`、`contractId`、其余 KPI/团队/条款/文件逻辑。

> ⚠️ 注意：`payments` computed 仍需保留（传给子组件 props）。`stages`/`budgets`/`deliverables` 同理保留。

### 4.6 验证清单（P1c 完成后）
- [ ] `pnpm run build:antd` 零错误
- [ ] 科研类合同详情页：显示阶段甘特图+表+预算+交付物+付款(带对应阶段徽标)
- [ ] 服务类合同详情页：显示6服务字段(含schedule/quality)+付款(无对应阶段)
- [ ] basic info 卡不再出现 service_period（G4 修复）
- [ ] 添加付款/删除付款仍可用（通过 emit reload 刷新）

---

## 5. 全局验证清单（P1a+b+c 全部完成后）
- [ ] 构建零错误
- [ ] 两类合同详情页渲染正确
- [ ] G1 修复: service_schedule/quality 可见
- [ ] G3 显示侧: 阶段 remarks 列可见
- [ ] G4 修复: service_period 不重复
- [ ] R1: 科研类付款显示对应阶段徽标
- [ ] 付款增删功能正常（emit reload 链路通）
- [ ] 外壳公共块（KPI/团队/条款/文件）不受影响
