<template>
  <!-- ============ 阶段进度 - 甘特图 ============ -->
  <div
    id="content"
    class="bg-white rounded-lg border border-gray-200 overflow-hidden"
  >
    <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
      <div class="w-1 h-4 rounded-full bg-teal-500"></div>
      <span class="text-sm font-semibold text-gray-700">阶段进度（甘特图）</span>
    </div>
    <div class="px-5 py-4">
      <template v-if="hasValidStages">
        <stage-gantt :stages="validStages" :deliverables="props.deliverables" />
      </template>
      <!-- 阶段详情表：所有阶段都展示，不限是否有日期 -->
      <div v-if="props.stages.length" class="mt-4 border-t pt-4">
        <div class="text-sm font-medium text-gray-700 mb-3">阶段详情</div>
        <a-table
          :columns="stageColumns"
          :data-source="props.stages"
          :pagination="false"
          size="small"
          row-key="stage_id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'stage_number'">
              <div>
                <div class="font-mono text-xs font-medium" :style="{ color: record.stage_name?.includes('研究阶段') ? '#8c8c8c' : '#333' }">
                  {{ record.stage_name || ('阶段 ' + record.stage_number) }}
                </div>
                <div class="text-xs text-gray-400 mt-0.5">阶段 {{ record.stage_number }}</div>
              </div>
            </template>
            <template v-if="column.key === 'remarks'">
              <div class="text-sm whitespace-pre-wrap text-gray-700">{{ record.remarks || '—' }}</div>
            </template>
            <template v-if="column.key === 'acceptance_criteria'">
              <div v-if="record.acceptance_criteria" class="text-sm whitespace-pre-wrap text-gray-700">
                {{ parseCriteriaText(record.acceptance_criteria) }}
              </div>
              <div v-else class="text-xs text-gray-400">暂无考核目标</div>
            </template>
            <template v-if="column.key === 'status'">
              <a-tag
                :color="record.status === 'completed' ? 'green' : record.status === 'in_progress' ? 'blue' : 'default'"
                size="small"
              >
                {{ record.status === 'completed' ? '已完成' : record.status === 'in_progress' ? '进行中' : '待开始' }}
              </a-tag>
            </template>
            <template v-if="column.key === 'time'">
              <span v-if="!record.start_time && !record.end_time" class="text-xs text-gray-400">数据待补</span>
              <span v-else class="text-xs">{{ extractStageTime(record) }}</span>
            </template>
          </template>
        </a-table>
      </div>
      <template v-if="!props.stages.length">
        <div class="py-8 flex flex-col items-center text-center">
          <a-empty description="暂无阶段数据">
            <template #description>
              <div class="text-gray-500 mb-2">暂无阶段数据</div>
              <div class="text-sm text-gray-400">阶段数据来自 OCR 识别，需人工校验后显示</div>
            </template>
          </a-empty>
        </div>
      </template>
    </div>
  </div>

  <!-- ============ 交付物 ============ -->
  <div
    v-if="props.deliverables.length > 0"
    class="bg-white rounded-lg border border-gray-200 overflow-hidden"
  >
    <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
      <div class="w-1 h-4 rounded-full bg-blue-500"></div>
      <span class="text-sm font-semibold text-gray-700">交付物成果</span>
    </div>
    <div class="px-5 py-4">
      <div class="space-y-3">
        <div
          v-for="d in props.deliverables"
          :key="d.deliverable_id"
          class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-blue-50/50 transition-colors"
        >
          <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-semibold shrink-0 mt-0.5">
            {{ props.deliverables.indexOf(d) + 1 }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-medium text-gray-800">{{ d.deliverable_name || '未命名交付物' }}</span>
              <a-tag v-if="d.deliverable_type" :color="d.deliverable_type === '专利' ? 'purple' : d.deliverable_type === '论文' ? 'green' : d.deliverable_type === '报告' ? 'blue' : 'default'" size="small">
                {{ d.deliverable_type }}
              </a-tag>
              <a-tag v-if="d.status" :color="d.status === 'completed' ? 'green' : d.status === 'pending' ? 'orange' : 'default'" size="small">
                {{ d.status === 'completed' ? '已完成' : d.status === 'pending' ? '进行中' : d.status }}
              </a-tag>
            </div>
            <div v-if="d.description" class="text-sm text-gray-500 mt-1">{{ d.description }}</div>
            <div class="flex gap-4 text-xs text-gray-400 mt-1">
              <span v-if="d.planned_date">计划: {{ d.planned_date }}</span>
              <span v-if="d.quantity">数量: {{ d.quantity }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div
    v-else
    class="bg-white rounded-lg border border-gray-200 overflow-hidden"
  >
    <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
      <div class="w-1 h-4 rounded-full bg-blue-500"></div>
      <span class="text-sm font-semibold text-gray-700">交付物成果</span>
    </div>
    <div class="px-5 py-4">
      <a-empty description="暂无交付物数据" />
    </div>
  </div>

  <!-- ============ 经费预算（科研类） ============ -->
  <div
    v-if="props.budgets.length > 0"
    class="bg-white rounded-lg border border-gray-200 overflow-hidden"
  >
    <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
      <div class="w-1 h-4 rounded-full bg-purple-500"></div>
      <span class="text-sm font-semibold text-gray-700">经费预算</span>
    </div>
    <div class="px-5 py-4">
      <a-table
        :data-source="props.budgets"
        :columns="[
          { title: '科目', dataIndex: 'category', key: 'category' },
          { title: '预算金额(万元)', dataIndex: 'amount_total', key: 'amount_total' },
          { title: '甲方拨款', dataIndex: 'amount_party_a', key: 'amount_party_a' },
          { title: '乙方自筹', dataIndex: 'amount_self', key: 'amount_self' },
        ]"
        :pagination="false"
        size="small"
        bordered
        row-key="budget_id"
        :scroll="{ x: 600 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'amount_total' || column.dataIndex === 'amount_party_a' || column.dataIndex === 'amount_self'">
            {{ record[column.dataIndex] != null ? Number(record[column.dataIndex]).toFixed(2) : '-' }}
          </template>
        </template>
      </a-table>
    </div>
  </div>

  <!-- ============ 付款进度 ============ -->
  <div
    id="payment"
    class="bg-white rounded-lg border border-gray-200 overflow-hidden"
  >
    <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
      <div class="w-1 h-4 rounded-full bg-amber-500"></div>
      <span class="text-sm font-semibold text-gray-700">付款进度</span>
      <div class="ml-auto">
        <a-button type="link" size="small" @click="openAddPaymentModal">+ 添加付款</a-button>
      </div>
    </div>
    <div class="px-5 py-4">
      <template v-if="props.payments.length">
      <!-- 付款汇总统计 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div class="bg-gray-50 rounded-lg p-3 text-center">
          <div class="text-xs text-gray-400 mb-1">付款阶段</div>
          <div class="text-2xl font-bold text-gray-900">{{ props.payments.length }}</div>
          <div class="text-xs text-gray-400">个</div>
        </div>
        <div class="bg-gray-50 rounded-lg p-3 text-center">
          <div class="text-xs text-gray-400 mb-1">计划总额</div>
          <div class="text-2xl font-bold text-blue-600">{{ fmtMoney(paymentsTotal.planned) }}</div>
          <div class="text-xs text-gray-400">万元</div>
        </div>
      </div>

      <!-- 付款阶段列表（flex 布局，序号不 absolute） -->
      <div class="space-y-4">
        <div
          v-for="(p, idx) in paymentsView"
          :key="p.payment_id"
          class="flex gap-3"
        >
          <!-- 序号圆圈（flex 行内） -->
          <div
            class="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white"
            :style="{ backgroundColor: p.isPaid ? '#52c41a' : '#1677ff' }"
          >
             {{ Number(idx) + 1 }}
          </div>
          <!-- 阶段卡片 -->
          <a-card
            size="small"
            class="flex-1"
            :class="p.isPaid ? 'border-green-200' : 'border-blue-200'"
            :body-style="{ padding: '12px', backgroundColor: p.isPaid ? '#f0fdf4' : '#eff6ff' }"
          >
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <!-- 左侧：阶段信息 -->
              <div class="md:col-span-2">
                <div class="flex items-center gap-2 mb-2">
                  <span class="font-semibold text-base">{{ p.payment_stage }}</span>
                  <!-- R1 新增: 对应阶段徽标, 放在 payment_stage 旁边 -->
                  <a-tag v-if="parseStageRef(p)" color="cyan" size="small" class="ml-2">
                    {{ parseStageRef(p) }}
                  </a-tag>
                  <a-tag :color="p.isPaid ? 'green' : 'orange'">
                    {{ p.statusLabel }}
                  </a-tag>
                </div>
                <div class="text-sm text-gray-500">
                  {{ p.payment_condition || '—' }}
                </div>
              </div>

              <!-- 右侧：金额信息 -->
              <div class="flex flex-col justify-center space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">计划金额</span>
                  <span class="font-semibold">{{ fmtMoney(p.planned_amount) }} 万元</span>
                </div>
              </div>
            </div>

            <!-- 付款日期 -->
            <div class="flex items-center gap-4 mt-3 text-xs text-gray-400 border-t border-dashed border-gray-200 pt-2">
              <span v-if="p.planned_date">
                <span class="mr-1">&#128197;</span> 计划日期：{{ p.planned_date }}
              </span>
              <a-button type="link" danger size="small" class="ml-auto" @click="deletePayment(p)">删除</a-button>
            </div>
          </a-card>
        </div>
      </div>
      </template>
      <template v-else>
      <div class="py-8 text-center">
        <a-empty description="暂无付款计划">
          <template #description>
            <div class="text-gray-500 mb-2">暂无付款计划</div>
            <div class="text-sm text-gray-400">可点击"添加付款"新增付款记录</div>
          </template>
        </a-empty>
      </div>
      </template>
    </div>
  </div>

  <!-- ============ 添加付款弹窗 ============ -->
  <a-modal
    v-model:open="addPaymentVisible"
    title="添加付款记录"
    :confirm-loading="paymentSaving"
    @ok="savePayment"
    :ok-text="'保存'"
    :cancel-text="'取消'"
  >
    <a-form :model="paymentForm" layout="vertical">
      <div class="grid grid-cols-2 gap-4">
        <a-form-item label="付款阶段">
          <a-input v-model:value="paymentForm.payment_stage" placeholder="如：第1阶段" />
        </a-form-item>
        <a-form-item label="计划金额（万元）">
          <a-input-number v-model:value="paymentForm.planned_amount" :precision="2" :min="0" class="w-full" />
        </a-form-item>
        <a-form-item label="计划日期">
          <a-date-picker v-model:value="paymentForm.planned_date" value-format="YYYY-MM-DD" class="w-full" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="paymentForm.status">
            <a-select-option value="pending">待支付</a-select-option>
            <a-select-option value="paid">已支付</a-select-option>
          </a-select>
        </a-form-item>
      </div>
      <a-form-item label="付款条件">
        <a-textarea v-model:value="paymentForm.payment_condition" :rows="2" placeholder="付款条件和说明..." />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import { createPaymentApi, deletePaymentApi } from '#/api/contracts'
import StageGantt from '#/views/contracts/components/stage-gantt.vue'

const props = defineProps<{
  contract: Record<string, any> | null
  stages: any[]
  budgets: any[]
  deliverables: any[]
  payments: any[]
  contractId: string
}>()
const emit = defineEmits<{ (e: 'reload'): void }>()

// 阶段数据质量检查
const hasValidStages = computed(() => {
  if (!props.stages.length) return false
  return props.stages.some((s: any) => s.start_time || s.end_time)
})
const validStages = computed(() => {
  return props.stages.filter((s: any) => s.start_time || s.end_time)
})

// 阶段详情表格列定义
const stageColumns = [
  { title: '阶段', key: 'stage_number', width: 130 },
  { title: '阶段内容', key: 'remarks', ellipsis: true },
  { title: '考核目标', key: 'acceptance_criteria', ellipsis: true },
  { title: '时间', key: 'time', width: 200 },
  { title: '状态', key: 'status', width: 80, align: 'center' as const },
]

// 解析验收标准文本：处理 Python list 格式或纯文本
function parseCriteriaText(criteria: string | null | undefined): string {
  if (!criteria) return ''
  const listMatch = criteria.match(/^\s*\[(.*)\]\s*$/s)
  if (listMatch) {
    const inner = listMatch[1] || ''
    const items = inner
      .split(/['"],\s*['"]/)
      .map((s) => s.replace(/^['"]|['"]$/g, '').trim())
      .filter(Boolean)
    return items.slice(0, 3).join('；') + (items.length > 3 ? ' ...' : '')
  }
  const text = criteria.trim()
  return text.length > 100 ? text.slice(0, 100) + '...' : text
}

// 从阶段数据中提取可读的时间范围（从 start_time 中解析结束部分补齐 end_time 为空的情况）
function extractStageTime(s: any): string {
  const raw = s.start_time || ''
  const end = s.end_time || ''
  if (!raw && !end) return '-'
  // 如果 start_time 包含 " — " 或 " 至 " 分段符，提取两端
  const cleaned = raw.replace(/(\d)\s+(?=\d)/g, '$1')
  const rangeMatch = cleaned.match(/^(.+?)\s*[—–至]\s*(.+)$/)
  if (rangeMatch) {
    return `${rangeMatch[1].trim()} ~ ${rangeMatch[2].trim()}`
  }
  if (end) return `${raw} ~ ${end}`
  return raw
}

// R1 新增: 从付款数据解析"研究阶段5.x~5.y"用于对应阶段徽标
// 同时查 payment_stage 和 payment_condition（不同合同阶段引用落点不同）
function parseStageRef(p: any): string {
  const text = `${p?.payment_stage || ''} ${p?.payment_condition || ''}`
  const m = text.match(/研究阶段\s*5\.\d+(?:\s*[~至\-–]\s*5\.\d+)?/)
  return m ? m[0] : ''
}

// fmtMoney
function fmtMoney(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toFixed(2)
}

// 付款数据结构化（DB 金额已统一为万元）
const paymentsView = computed(() => {
  return props.payments.map((p: any) => {
    const isPaid = p.status === 'paid' || p.status === 'completed' || p.status === '已支付'
    const plannedAmount = Number(p.planned_amount) || 0
    const statusLabel =
      p.status === 'paid' || p.status === '已支付'
        ? '已支付'
        : p.status === 'pending' || p.status === '待支付'
          ? '待支付'
          : p.status || '待支付'
    return {
      ...p,
      planned_amount: plannedAmount,
      isPaid,
      statusLabel,
    }
  })
})

// 付款汇总（仅计划总额，回款以 finance 为准）
const paymentsTotal = computed(() => {
  const planned = paymentsView.value.reduce((sum: number, p: any) => sum + (p.planned_amount || 0), 0)
  return { planned, paid: 0 }
})

// 付款 CRUD
const addPaymentVisible = ref(false)
const paymentSaving = ref(false)
const paymentForm = ref<Record<string, any>>({})

function openAddPaymentModal() {
  paymentForm.value = {
    payment_stage: '',
    planned_amount: 0,
    planned_date: '',
    status: 'pending',
    payment_condition: '',
  }
  addPaymentVisible.value = true
}

async function savePayment() {
  paymentSaving.value = true
  try {
    await createPaymentApi(props.contractId, paymentForm.value)
    message.success('付款记录已添加')
    addPaymentVisible.value = false
    emit('reload')
  } catch (e: any) {
    message.error('添加失败: ' + (e?.message || '未知错误'))
  } finally {
    paymentSaving.value = false
  }
}

async function deletePayment(p: any) {
  if (!p?.payment_id) return
  try {
    await deletePaymentApi(props.contractId, p.payment_id)
    message.success('付款记录已删除')
    emit('reload')
  } catch (e: any) {
    message.error('删除失败: ' + (e?.message || '未知错误'))
  }
}
</script>
