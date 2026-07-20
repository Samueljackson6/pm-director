<template>
  <section class="space-y-4">
    <div class="flex items-center justify-between gap-4">
      <div class="flex min-w-0 items-center gap-4">
        <a-button type="text" class="h-9 w-9 rounded-lg border border-gray-200" @click="emit('back')">←</a-button>
        <div class="min-w-0">
          <h2 class="text-xl font-semibold text-gray-800">合同详情</h2>
          <p class="mt-0.5 truncate text-sm text-gray-500">{{ contract?.contract_id }} · {{ contract?.official_name || contract?.project_name }}</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a-tag v-if="contract?.contract_status" :color="statusColor(contract.contract_status)">{{ statusLabel(contract.contract_status) }}</a-tag>
        <a-button type="primary" size="small" ghost @click="visible = true">编辑</a-button>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3 md:grid-cols-5">
      <article v-for="item in metrics" :key="item.label" class="rounded-lg border border-gray-200 bg-white p-4 text-center">
        <p class="mb-1 text-xs text-gray-400">{{ item.label }}</p>
        <p class="text-2xl font-bold" :class="item.className">{{ item.value }}</p>
        <p class="mt-0.5 text-xs text-gray-400">万元</p>
      </article>
    </div>

    <nav class="sticky top-0 z-20 -mx-6 overflow-x-auto border-y border-gray-200 bg-white/90 px-6 py-2 backdrop-blur-sm">
      <button
        v-for="anchor in anchors"
        :key="anchor.id"
        class="mr-1 whitespace-nowrap rounded-md px-3 py-1.5 text-sm transition-colors"
        :class="activeAnchor === anchor.id ? 'bg-blue-50 font-medium text-blue-600' : 'text-gray-500 hover:bg-gray-100'"
        @click="scrollTo(anchor.id)"
      >
        {{ anchor.label }}
      </button>
    </nav>

    <a-card id="overview" title="基本信息" size="small" :body-style="{ padding: '16px' }">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <p class="mb-2 text-xs font-semibold tracking-wider text-gray-500">签约信息</p>
          <div class="grid grid-cols-2 gap-3 text-sm"><span>签订日期：{{ contract?.sign_date || '-' }}</span><span>到期日期：{{ contract?.expiry_date || '未设置' }}</span><span>税率：{{ contract?.tax_rate ? `${contract.tax_rate}%` : '-' }}</span><span>SGSC编号：{{ contract?.sgsc_id || '-' }}</span></div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="rounded-lg bg-blue-50 p-3"><p class="text-xs text-blue-600">甲方</p><p class="mt-1 font-medium">{{ clean(contract?.party_a) }}</p><p class="mt-1 text-xs text-gray-500">{{ contract?.party_a_contact || '-' }} {{ contract?.party_a_phone ? `· ${contract.party_a_phone}` : '' }}</p></div>
          <div class="rounded-lg bg-green-50 p-3"><p class="text-xs text-green-600">乙方</p><p class="mt-1 font-medium">{{ clean(contract?.party_b) }}</p><p class="mt-1 text-xs text-gray-500">{{ contract?.party_b_contact || '-' }} {{ contract?.party_b_phone ? `· ${contract.party_b_phone}` : '' }}</p></div>
        </div>
      </div>
      <template v-if="contract?.acceptance_criteria || contract?.acceptance_method">
        <a-divider />
        <p class="mb-2 text-xs font-semibold tracking-wider text-gray-500">验收标准</p>
        <p v-if="contract?.acceptance_criteria" class="whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-sm text-gray-700">{{ contract.acceptance_criteria }}</p>
        <p v-if="contract?.acceptance_method" class="mt-2 text-xs text-gray-500">验收方式：{{ contract.acceptance_method }} {{ contract.acceptance_location ? `· ${contract.acceptance_location}` : '' }}</p>
      </template>
      <template v-if="contract?.bidder || contract?.bid_amount || contract?.subcontract_company">
        <a-divider />
        <div class="grid grid-cols-1 gap-4 text-sm md:grid-cols-2">
          <div v-if="contract?.bidder || contract?.bid_amount"><p class="mb-2 text-xs font-semibold tracking-wider text-gray-500">中标信息</p><p>{{ contract?.bidder || '-' }} · {{ contract?.bid_amount || '-' }} 万元 · {{ contract?.bid_date || '-' }}</p></div>
          <div v-if="contract?.subcontract_company"><p class="mb-2 text-xs font-semibold tracking-wider text-gray-500">分包信息</p><p>{{ contract?.subcontract_company }} · {{ contract?.subcontract_contact || '-' }} · {{ contract?.subcontract_amount || '-' }} 万元</p></div>
        </div>
      </template>
    </a-card>

    <ContractEditModal
      v-model:open="visible"
      :contract="contract"
      :contract-id="contractId"
      :stages="stages"
      :deliverables="deliverables"
      @updated="emit('updated')"
    />
  </section>
</template>

<script lang="ts" setup>
import { computed, nextTick, onUnmounted, ref, watch } from 'vue'
import ContractEditModal from '#/views/contracts/components/detail/ContractEditModal.vue'

const props = defineProps(['contract', 'contractId', 'finance', 'stages', 'deliverables'])
const emit = defineEmits(['back', 'updated'])
const visible = ref(false)
const activeAnchor = ref('overview')
const anchors = [
  { id: 'overview', label: '概览' },
  { id: 'finance', label: '财务' },
  { id: 'relations', label: '项目与文件' },
  { id: 'fulfillment', label: '履约' },
]
let observer: IntersectionObserver | undefined
const metrics = computed(() => {
  const finance = props.finance ?? {}
  return [
    { label: '合同含税总额', value: format(props.contract?.contract_amount), className: 'text-gray-900' },
    { label: '已开票', value: format(finance.invoice_total), className: 'text-blue-600' },
    { label: '已回款', value: format(finance.payment_total), className: 'text-green-600' },
    { label: '已开票未回款', value: format(finance.payment_unreceived), className: 'text-red-500' },
    {
      label: '合同总额未回款',
      value: format(subtractKnown(finance.contract_total ?? props.contract?.contract_amount, finance.payment_total)),
      className: 'text-orange-500',
    },
  ]
})
function format(value: unknown) {
  if (value === null || value === undefined || value === '') return '待核验'
  return Number(value).toFixed(2)
}
function subtractKnown(left: unknown, right: unknown) {
  if (left === null || left === undefined || left === '' || right === null || right === undefined || right === '') return null
  return Number(left) - Number(right)
}
function clean(value: unknown) { return String(value || '-').replace(/[\n\r]+/g, ' ').trim() }
function statusColor(status: string) { return ({ signed: 'green', active: 'blue', completed: 'default', expired: 'red', terminated: 'orange', pending: 'gray' }[status] || 'default') }
function statusLabel(status: string) { return ({ signed: '已签订', active: '执行中', completed: '已完成', expired: '已到期', terminated: '已终止', pending: '待签订' }[status] || status) }
function scrollTo(id: string) {
  const target = document.getElementById(id)
  if (!target) return
  window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - 64, behavior: 'smooth' })
}
function observeAnchors() {
  observer?.disconnect()
  observer = new IntersectionObserver((entries) => {
    for (const entry of entries) if (entry.isIntersecting) activeAnchor.value = entry.target.id
  }, { rootMargin: '-64px 0px -70% 0px' })
  for (const anchor of anchors) {
    const target = document.getElementById(anchor.id)
    if (target) observer.observe(target)
  }
}
watch(() => props.contract, () => nextTick(observeAnchors), { flush: 'post' })
onUnmounted(() => observer?.disconnect())
</script>
