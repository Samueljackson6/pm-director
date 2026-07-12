<template>
  <!-- ============ 服务内容 ============ -->
  <div
    id="content"
    class="bg-white rounded-lg border border-gray-200 overflow-hidden"
  >
    <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
      <div class="w-1 h-4 rounded-full bg-teal-500"></div>
      <span class="text-sm font-semibold text-gray-700">服务内容</span>
    </div>
    <div class="px-5 py-4">
      <div v-if="props.contract" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- 1. 服务内容（长文本可折叠） -->
        <div v-if="props.contract.service_content && props.contract.service_content.length > 150" class="md:col-span-2">
          <div class="text-xs text-gray-400 mb-1">服务内容</div>
          <div v-if="!serviceExpanded" class="relative">
            <div class="text-sm text-gray-700 leading-relaxed line-clamp-3 bg-gray-50 rounded-lg p-3 border border-gray-100">
              {{ props.contract.service_content }}
            </div>
            <a-button type="link" size="small" class="absolute bottom-0 right-0 bg-white" @click="serviceExpanded = true">
              展开全部 ↓
            </a-button>
          </div>
          <div v-else class="text-sm text-gray-700 leading-relaxed bg-gray-50 rounded-lg p-3 border border-gray-100 relative">
            {{ props.contract.service_content }}
            <a-button type="link" size="small" class="absolute bottom-0 right-0 bg-white" @click="serviceExpanded = false">
              收起 ↑
            </a-button>
          </div>
        </div>
        <div v-else-if="props.contract.service_content" class="md:col-span-2">
          <div class="text-xs text-gray-400 mb-1">服务内容</div>
          <div class="text-sm text-gray-700 leading-relaxed">{{ props.contract.service_content }}</div>
        </div>

        <!-- 2. 服务方式 -->
        <div v-if="props.contract.service_method">
          <div class="text-xs text-gray-400 mb-1">服务方式</div>
          <div class="font-medium text-gray-900 text-sm">{{ props.contract.service_method }}</div>
        </div>

        <!-- 3. 服务地点 -->
        <div v-if="props.contract.service_location">
          <div class="text-xs text-gray-400 mb-1">服务地点</div>
          <div class="font-medium text-gray-900 text-sm">{{ props.contract.service_location }}</div>
        </div>

        <!-- 4. 服务期限 -->
        <div v-if="props.contract.service_period">
          <div class="text-xs text-gray-400 mb-1">服务期限</div>
          <div class="font-medium text-gray-900 text-sm">{{ props.contract.service_period }}</div>
        </div>

        <!-- 5. 服务进度（新增字段） -->
        <div v-if="props.contract.service_schedule">
          <div class="text-xs text-gray-400 mb-1">服务进度</div>
          <div class="font-medium text-gray-900 text-sm">{{ props.contract.service_schedule }}</div>
        </div>

        <!-- 6. 服务质量（新增字段） -->
        <div v-if="props.contract.service_quality">
          <div class="text-xs text-gray-400 mb-1">服务质量</div>
          <div class="font-medium text-gray-900 text-sm">{{ props.contract.service_quality }}</div>
        </div>
      </div>
      <div v-else class="py-8 text-center">
        <a-empty description="暂无服务内容" />
      </div>
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

const props = defineProps<{
  contract: Record<string, any> | null
  payments: any[]
  contractId: string
}>()
const emit = defineEmits<{ (e: 'reload'): void }>()

// 服务内容折叠状态（本地持有）
const serviceExpanded = ref(false)

// 金额格式化
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
