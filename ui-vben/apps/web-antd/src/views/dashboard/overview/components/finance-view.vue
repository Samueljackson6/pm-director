<template>
  <div class="space-y-4">
    <!-- Metrics -->
    <div class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
      <metric-card label="合同总额" :value="s?.contract_total_amount" unit="万元" tone="primary" />
      <metric-card label="已开票" :value="s?.invoiced_amount" unit="万元" tone="invoiced" />
      <metric-card label="未开票" :value="s?.uninvoiced_amount" unit="万元" tone="warning" />
      <metric-card label="已回款" :value="s?.received_amount" unit="万元" tone="received" />
      <metric-card label="未回款" :value="s?.unreceived_amount" unit="万元" tone="danger" />
      <metric-card
        label="回款率"
        :value="s?.receipt_rate"
        unit="%"
        :digits="1"
        tone="received"
      />
    </div>

    <!-- 漏斗 -->
    <finance-funnel
      :contract="s?.contract_total_amount ?? 0"
      :invoiced="s?.invoiced_amount ?? 0"
      :received="s?.received_amount ?? 0"
    />

    <!-- 趋势 -->
    <div class="rounded-lg border bg-card p-4 shadow-sm">
      <div class="mb-2 font-medium text-card-foreground">月度开票 / 回款</div>
      <trend-chart
        :data="overview.invoice_monthly ?? []"
        x-field="month"
        :series="financeSeries"
        :x-rotate="45"
        :legend-bottom="10"
      />
    </div>
    <div class="rounded-lg border bg-card p-4 shadow-sm">
      <div class="mb-2 font-medium text-card-foreground">开票与回款差额</div>
      <trend-chart
        :data="diffData"
        x-field="month"
        :series="diffSeries"
        :x-rotate="45"
        :legend-bottom="10"
      />
    </div>

    <!-- 异常区 -->
    <div class="rounded-lg border bg-card p-4 shadow-sm">
      <div class="mb-3 font-medium text-card-foreground">异常区</div>
      <div v-if="anomalies.length" class="space-y-2">
        <div
          v-for="(item, idx) in anomalies"
          :key="idx"
          class="flex items-center justify-between rounded-lg border border-border p-3"
          :class="`dash-bg-${item.tone}`"
        >
          <span class="text-sm" :class="`dash-text-${item.tone}`">{{ item.text }}</span>
        </div>
      </div>
      <div v-else class="py-4 text-center text-sm text-muted-foreground">
        未检测到明显异常
      </div>
    </div>

    <!-- 客户回款排行 -->
    <div class="rounded-lg border bg-card p-4 shadow-sm">
      <div class="mb-2 font-medium text-card-foreground">
        客户合同额排行
        <span class="ml-1 text-xs font-normal text-muted-foreground"
          >（API 仅提供合同额，回款按户维度暂未提供）</span
        >
      </div>
      <top-customers-bar :data="overview.top_customers ?? []" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import type { DashboardOverview, RecentContract } from '#/api/dashboard';
import TrendChart from '#/views/dashboard/components/trend-chart.vue';
import TopCustomersBar from '#/views/dashboard/components/top-customers-bar.vue';
import MetricCard from './metric-card.vue';
import FinanceFunnel from './finance-funnel.vue';
import { FINANCE_SERIES } from '../dashboard-types';

const props = defineProps<{ overview: DashboardOverview }>();

const financeSeries = FINANCE_SERIES;
const s = computed(() => props.overview.summary);

const diffData = computed(() =>
  (props.overview.invoice_monthly ?? []).map((d) => ({
    month: d.month,
    diff: (d.invoiced_wan ?? 0) - (d.received_wan ?? 0),
  })),
);

const diffSeries = [{ name: '差额', valueField: 'diff', color: '#D98E04' }];

const anomalies = computed(() => {
  const list: Array<{ tone: 'danger' | 'warning'; text: string }> = [];
  const rows = props.overview.recent_contracts ?? [];
  for (const r of rows as RecentContract[]) {
    if (r.invoice_total > r.contract_amount) {
      list.push({
        tone: 'warning',
        text: `开票率>100%：${r.contract_id} ${r.project_name}`,
      });
    }
    if (r.payment_total > r.invoice_total) {
      list.push({
        tone: 'danger',
        text: `回款>开票：${r.contract_id} ${r.project_name}`,
      });
    }
  }
  const up = props.overview.pending_tasks?.unmatched_payments;
  if (up && up > 0) {
    list.push({ tone: 'danger', text: `未匹配回款 ${up} 笔，需业务核对` });
  }
  return list;
});
</script>
