<script lang="ts" setup>
interface SupplierRating { readonly basic: number; readonly risk: number; readonly stability: number; readonly tech: number; readonly overall: number; }

const props = defineProps<{
  readonly contacts: readonly Record<string, unknown>[];
  readonly contracts: readonly Record<string, unknown>[];
  readonly dataStates: Record<string, string>;
  readonly payments: readonly Record<string, unknown>[];
  readonly rating: SupplierRating | null;
  readonly supplierInvoices: readonly Record<string, unknown>[];
}>();

function stateText(key: string, count: number): string {
  const state = props.dataStates[key];
  if (state === 'source_not_established') return '数据源未建立';
  if (state === 'known_zero') return '已建立但无记录';
  return `${count} 条记录`;
}

function recordTitle(record: Record<string, unknown>, fields: string[]): string {
  for (const field of fields) {
    const value = record[field];
    if (typeof value === 'string' && value.trim()) return value;
  }
  return '待核验';
}
</script>

<template>
  <section class="space-y-4">
    <a-card title="协作与结算事实" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '16px' }">
      <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4"><div class="rounded-lg bg-gray-50 p-3"><div class="text-xs text-gray-500">关联合同</div><div class="mt-1 text-xl font-semibold">{{ props.contracts.length }}</div><div class="mt-1 text-xs text-gray-500">{{ stateText('contracts', props.contracts.length) }}</div></div><div class="rounded-lg bg-gray-50 p-3"><div class="text-xs text-gray-500">供应商收票</div><div class="mt-1 text-xl font-semibold">{{ props.supplierInvoices.length }}</div><div class="mt-1 text-xs text-gray-500">{{ stateText('supplier_invoices', props.supplierInvoices.length) }}</div></div><div class="rounded-lg bg-gray-50 p-3"><div class="text-xs text-gray-500">供应商付款</div><div class="mt-1 text-xl font-semibold">{{ props.payments.length }}</div><div class="mt-1 text-xs text-gray-500">{{ stateText('supplier_payments', props.payments.length) }}</div></div><div class="rounded-lg bg-gray-50 p-3"><div class="text-xs text-gray-500">联系人</div><div class="mt-1 text-xl font-semibold">{{ props.contacts.length }}</div><div class="mt-1 text-xs text-gray-500">{{ stateText('contacts', props.contacts.length) }}</div></div></div>
      <div class="mt-4 grid gap-4 md:grid-cols-2"><div><div class="mb-2 text-xs font-semibold text-gray-500">合同</div><div v-if="props.contracts.length" class="space-y-1"><div v-for="contract in props.contracts.slice(0, 3)" :key="String(contract.project_id)" class="rounded bg-gray-50 px-2 py-1 text-sm">{{ recordTitle(contract, ['project_name', 'project_id']) }}</div></div><div v-else class="text-sm text-gray-500">{{ stateText('contracts', 0) }}</div></div><div><div class="mb-2 text-xs font-semibold text-gray-500">联系人</div><div v-if="props.contacts.length" class="space-y-1"><div v-for="contact in props.contacts.slice(0, 3)" :key="String(contact.id)" class="rounded bg-gray-50 px-2 py-1 text-sm">{{ recordTitle(contact, ['name']) }} · {{ recordTitle(contact, ['phone', 'position']) }}</div></div><div v-else class="text-sm text-gray-500">{{ stateText('contacts', 0) }}</div></div></div>
    </a-card>
    <a-card title="综合评级" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '16px' }"><template v-if="props.rating"><div class="grid grid-cols-2 gap-4 md:grid-cols-5"><div v-for="item in [{ label: '基本资质', value: props.rating.basic }, { label: '风险状况', value: props.rating.risk }, { label: '技术实力', value: props.rating.tech }, { label: '经营稳定性', value: props.rating.stability }]" :key="item.label" class="text-center"><div class="mb-2 text-xs text-gray-400">{{ item.label }}</div><a-rate :value="item.value" disabled :count="5" allow-half /></div><div class="rounded-lg bg-blue-50 p-3 text-center"><div class="mb-2 text-xs text-gray-400">综合评分</div><div class="text-3xl font-bold text-blue-600">{{ props.rating.overall.toFixed(1) }}</div></div></div></template><div v-else class="py-4 text-center text-sm text-gray-600">待核验：证据不足，当前不生成综合评级。</div></a-card>
  </section>
</template>
