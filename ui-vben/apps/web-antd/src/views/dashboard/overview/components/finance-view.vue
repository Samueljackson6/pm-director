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

    <!-- 财务异常由后端动作契约提供对象 ID、原因和真实下钻目标。 -->
    <DashboardActionQueue
      :actions="financeActions"
      empty-text="当前未识别到可下钻的财务核对事项；这不代表财务数据已完成核验。"
      kicker="财务核对"
      title="需核对的回款、发票与付款条件"
    />

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
import type { DashboardOverview } from '#/api/dashboard';
import TrendChart from '#/views/dashboard/components/trend-chart.vue';
import TopCustomersBar from '#/views/dashboard/components/top-customers-bar.vue';
import DashboardActionQueue from './DashboardActionQueue.vue';
import MetricCard from './metric-card.vue';
import FinanceFunnel from './finance-funnel.vue';
import { DASH_COLORS, FINANCE_SERIES } from '../dashboard-types';

const props = defineProps<{ overview: DashboardOverview }>();

const financeSeries = FINANCE_SERIES;
const s = computed(() => props.overview.summary);

const diffData = computed(() =>
  (props.overview.invoice_monthly ?? []).map((d) => ({
    month: d.month,
    diff: (d.invoiced_wan ?? 0) - (d.received_wan ?? 0),
  })),
);

const diffSeries = [{ name: '差额', valueField: 'diff', color: DASH_COLORS.warning }];

const financeActions = computed(() =>
  [...(props.overview.risk_actions ?? []), ...(props.overview.task_actions ?? [])].filter(
    (action) => ['invoice', 'payment'].includes(action.object_type),
  ),
);

</script>
