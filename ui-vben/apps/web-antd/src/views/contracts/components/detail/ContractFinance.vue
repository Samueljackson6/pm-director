<template>
  <section id="finance" class="grid grid-cols-1 gap-4 lg:grid-cols-2">
    <a-card title="关联发票（时间正序）" size="small" :body-style="{ padding: '12px' }">
      <template #extra>
        <a-button type="primary" size="small" ghost @click="visible = true">+ 新增发票</a-button>
      </template>
      <div v-if="sortedInvoices.length" class="max-h-[400px] space-y-2 overflow-y-auto">
        <button
          v-for="invoice in sortedInvoices"
          :key="invoice.invoice_id"
          class="flex w-full items-center justify-between rounded-lg bg-gray-50 p-3 text-left hover:bg-blue-50"
          @click="openInvoice(invoice.invoice_id)"
        >
          <span>
            <strong class="text-sm">{{ invoice.invoice_no || '发票' }}</strong>
            <small class="ml-2 text-gray-400">{{ invoice.invoice_date || '日期未知' }}</small>
          </span>
          <span class="text-right">
            <strong>{{ formatInTenThousands(invoice.amount) }} 万</strong>
            <a-tag class="ml-2" :color="statusColor(invoice.status)">{{ statusLabel(invoice.status) }}</a-tag>
          </span>
        </button>
      </div>
      <a-empty v-else description="暂无关联发票" class="py-8" />
    </a-card>

    <a-card title="合同财务快照" size="small" :body-style="{ padding: '12px' }">
      <dl class="grid grid-cols-2 gap-4 text-sm">
        <template v-for="item in financeItems" :key="item.label">
          <dt class="text-gray-500">{{ item.label }}</dt>
          <dd class="text-right font-medium">{{ item.value }} 万元</dd>
        </template>
      </dl>
      <p class="mt-4 text-xs text-gray-400">财务快照仅反映当前已同步数据，明细以发票与回款原始记录为准。</p>
    </a-card>

    <ContractInvoiceModal
      v-model:open="visible"
      :contract="contract"
      :contract-id="contractId"
      @updated="emit('updated')"
    />
  </section>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import ContractInvoiceModal from '#/views/contracts/components/detail/ContractInvoiceModal.vue'

const props = defineProps(['contract', 'contractId', 'finance', 'invoices'])
const emit = defineEmits(['updated'])
const router = useRouter()
const visible = ref(false)
const sortedInvoices = computed(() => {
  return [...(props.invoices ?? [])].sort((left, right) => {
    return String(left.invoice_date || '9999-99-99').localeCompare(String(right.invoice_date || '9999-99-99'))
  })
})
const financeItems = computed(() => [
  { label: '合同总额', value: format(props.finance?.contract_total ?? props.contract?.contract_amount) },
  { label: '已开票', value: format(props.finance?.invoice_total) },
  { label: '已回款', value: format(props.finance?.payment_total) },
  { label: '未回款', value: format(props.finance?.payment_unreceived) },
])

function format(value: unknown) {
  if (value === null || value === undefined || value === '') return '待核验'
  return Number(value).toFixed(2)
}

function formatInTenThousands(value: unknown) {
  if (value === null || value === undefined || value === '') return format(value)
  return format(Number(value) / 10000)
}
function openInvoice(id: unknown) { router.push({ name: 'CustomerInvoiceDetail', query: { id: String(id) } }) }
function statusColor(status: unknown) { return status === '已回款' || status === 'paid' ? 'green' : status === '已开' ? 'blue' : 'default' }
function statusLabel(status: unknown) { return String(status || '未知') }
</script>
