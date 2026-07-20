<script lang="ts" setup>
import { computed } from 'vue';

import type { SupplierExternalInvestment, SupplierRiskFactor, SupplierRiskScan, SupplierSoftwareCopyright } from './supplier-qcc';

const props = defineProps<{
  readonly investmentList: readonly SupplierExternalInvestment[];
  readonly qccDataAvailable: boolean;
  readonly riskLevel: string;
  readonly riskLevelTextClass: string;
  readonly riskScan: SupplierRiskScan | null;
  readonly softwareList: readonly SupplierSoftwareCopyright[];
}>();

const riskFactors = computed<readonly SupplierRiskFactor[]>(() =>
  props.riskScan?.风险因子扫描?.filter((factor) => factor.条目数 > 0) ?? [],
);
const riskItems = computed(() => {
  if (!props.riskScan || props.riskScan.有记录因子数 === undefined || props.riskScan.无记录因子数 === undefined) return '待核验';
  return props.riskScan.有记录因子数 + props.riskScan.无记录因子数;
});
</script>

<template>
  <section class="space-y-4">
    <a-card id="risk" title="风险扫描" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '12px' }">
      <template v-if="props.riskScan && riskItems !== '待核验'"><div class="mb-4 text-center"><div class="text-2xl font-bold" :class="props.riskLevelTextClass">{{ props.riskLevel }}</div><div class="mt-1 text-xs text-gray-500">已扫描 {{ riskItems }} 项风险因子</div></div><div class="mb-4 grid grid-cols-2 gap-3"><div class="rounded-lg bg-red-50 p-3 text-center"><div class="text-2xl font-bold text-red-600">{{ props.riskScan.有记录因子数 }}</div><div class="mt-1 text-xs text-gray-500">有风险</div></div><div class="rounded-lg bg-green-50 p-3 text-center"><div class="text-2xl font-bold text-green-600">{{ props.riskScan.无记录因子数 }}</div><div class="mt-1 text-xs text-gray-500">无风险</div></div></div><div v-if="riskFactors.length" class="space-y-2"><div class="mb-2 text-xs font-semibold text-gray-500">风险因子详情</div><div v-for="factor in riskFactors.slice(0, 5)" :key="factor.风险因子" class="flex items-center justify-between rounded-lg bg-red-50 px-3 py-2"><span class="text-xs text-gray-700">{{ factor.风险因子 }}</span><a-tag color="red" size="small">{{ factor.条目数 }}条</a-tag></div></div><div v-else class="py-4 text-center text-sm text-gray-600">已完成扫描，未发现记录</div></template>
      <div v-else class="py-6 text-center text-sm text-gray-600">待核验：尚无可用于评级的本地风险扫描结果。</div>
    </a-card>
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <a-card id="software" title="软件著作权" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '12px' }"><template #extra><span class="text-xs text-gray-400">共 {{ props.softwareList.length }} 项</span></template><template v-if="props.softwareList.length"><div class="max-h-[400px] space-y-2 overflow-y-auto"><div v-for="(software, index) in props.softwareList.slice(0, 10)" :key="software.登记号 || index" class="flex items-center gap-3 rounded-lg bg-gray-50 p-2.5"><div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600">{{ index + 1 }}</div><div class="min-w-0"><div class="truncate text-sm font-medium">{{ software.软件全称 }}</div><div class="text-xs text-gray-400">{{ software.登记号 }} · {{ software.登记日期 }}</div></div></div></div></template><div v-else class="py-8 text-center text-sm text-gray-600">{{ props.qccDataAvailable ? '已建立但无记录' : '待核验' }}</div></a-card>
      <a-card id="investment" title="对外投资" size="small" class="rounded-xl shadow-sm" :body-style="{ padding: '12px' }"><template #extra><span class="text-xs text-gray-400">共 {{ props.investmentList.length }} 家企业</span></template><template v-if="props.investmentList.length"><div class="space-y-2"><div v-for="investment in props.investmentList" :key="investment.被投资企业名称" class="flex items-center justify-between rounded-lg bg-gray-50 p-3"><div class="min-w-0"><div class="text-sm font-medium text-gray-900">{{ investment.被投资企业名称 }}</div><div class="mt-1 text-xs text-gray-400">成立：{{ investment.成立日期 || '待核验' }}</div></div><div class="text-right"><div class="text-sm font-semibold text-purple-600">{{ investment.持股比例 || '待核验' }}</div><div class="text-xs text-gray-400">{{ investment.状态 || '待核验' }}</div></div></div></div></template><div v-else class="py-8 text-center text-sm text-gray-600">{{ props.qccDataAvailable ? '已建立但无记录' : '待核验' }}</div></a-card>
    </div>
  </section>
</template>
