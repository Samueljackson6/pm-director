<template>
  <div class="p-4">
    <!-- 统计卡片 -->
    <div class="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="text-muted-foreground text-sm">合同总数</div>
        <div class="mt-1 text-2xl font-bold">{{ stats.contract_count ?? '-' }}</div>
      </div>
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="text-muted-foreground text-sm">合同总额（万元）</div>
        <div class="mt-1 text-2xl font-bold">{{ formatMoney(stats.total_amount) }}</div>
      </div>
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="text-muted-foreground text-sm">已开票（万元）</div>
        <div class="mt-1 text-2xl font-bold">{{ formatMoney(stats.total_invoiced) }}</div>
      </div>
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="text-muted-foreground text-sm">已回款（万元）</div>
        <div class="mt-1 text-2xl font-bold">{{ formatMoney(stats.total_paid) }}</div>
      </div>
    </div>

    <!-- 最近合同 -->
    <div class="rounded-lg border bg-card shadow-sm">
      <div class="border-b px-4 py-3 font-medium">最近合同</div>
      <VxeTable
        :data="recentContracts"
        :column-config="{ minWidth: 120 }"
        :row-config="{ height: 44, isHover: true }"
        size="small"
        height="400"
      >
        <VxeColumn field="project_name" title="项目名称" minWidth="250" showOverflow />
        <VxeColumn field="contract_amount" title="金额(万元)" width="130" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.contract_amount) }}
          </template>
        </VxeColumn>
        <VxeColumn field="invoice_total" title="已开票(万元)" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.invoice_total) }}
          </template>
        </VxeColumn>
        <VxeColumn field="payment_total" title="已回款(万元)" width="120" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.payment_total) }}
          </template>
        </VxeColumn>
        <VxeColumn field="sign_date" title="签订日期" width="110" />
      </VxeTable>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { getContractsApi } from '#/api/contracts'
import { getStatsApi } from '#/api/contracts'
import { formatWanYuan } from '@/utils/formatAmount'

interface StatsData {
  contract_count: number
  total_amount: number
  total_invoiced: number
  total_paid: number
}

const stats = ref<StatsData>({
  contract_count: 0,
  total_amount: 0,
  total_invoiced: 0,
  total_paid: 0,
})
const recentContracts = ref<any[]>([])

function formatMoney(v: number | undefined | null): string {
  return formatWanYuan(v)
}

onMounted(async () => {
  try {
    const s = await getStatsApi() as any
    if (s) {
      stats.value = {
        contract_count: s.contract_count ?? 0,
        total_amount: s.total_amount ?? 0,
        total_invoiced: s.total_invoiced ?? 0,
        total_paid: s.total_paid ?? 0,
      }
    }
  } catch (_) { /* ignore */ }

  try {
    const data = await getContractsApi({ page: 1, size: 10 })
    recentContracts.value = data.items ?? []
  } catch (_) { /* ignore */ }
})
</script>
