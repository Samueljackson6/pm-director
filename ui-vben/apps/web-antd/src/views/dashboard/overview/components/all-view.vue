<template>
  <div class="space-y-4">
    <!-- Layer1: KPI 卡片 -->
    <div class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
      <metric-card
        label="合同总额"
        :value="s?.contract_total_amount"
        unit="万元"
        tone="primary"
      />
      <metric-card label="合同数量" :value="s?.contract_count" unit="个" :digits="0" />
      <metric-card
        label="已开票"
        :value="s?.invoiced_amount"
        unit="万元"
        tone="invoiced"
      />
      <metric-card
        label="已回款"
        :value="s?.received_amount"
        unit="万元"
        tone="received"
      />
      <metric-card
        label="回款率"
        :value="s?.receipt_rate"
        unit="%"
        :digits="1"
        tone="received"
      />
      <metric-card
        label="风险与待处理"
        :value="riskTotal"
        unit="项"
        :digits="0"
        tone="danger"
      />
    </div>

    <!-- Layer2: 待处理告警条 -->
    <alert-strip :tasks="overview.pending_tasks" @navigate="(k) => $emit('navigate', k)" />

    <!-- Layer3: 类型/状态/Top客户 -->
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="mb-2 font-medium text-card-foreground">合同类型分布</div>
        <contract-type-pie :data="overview.contracts_by_type ?? []" />
      </div>
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="mb-2 font-medium text-card-foreground">合同状态分布</div>
        <div class="space-y-3">
          <div v-for="b in statusBars" :key="b.status" class="space-y-1">
            <div class="flex justify-between text-sm">
              <span class="text-card-foreground">{{ b.status }}</span>
              <span class="text-xs text-muted-foreground"
                >{{ fmtMoney(b.amount) }} 万元 · {{ b.count }} 个</span
              >
            </div>
            <div class="h-2 w-full rounded bg-accent">
              <div
                class="h-2 rounded dash-bg-primary"
                :style="{ width: b.pct + '%' }"
              ></div>
            </div>
          </div>
          <div v-if="!statusBars.length" class="text-sm text-muted-foreground">
            暂无数据
          </div>
        </div>
      </div>
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="mb-2 font-medium text-card-foreground">Top 客户</div>
        <top-customers-bar :data="overview.top_customers ?? []" />
        <div class="mt-2 text-xs text-muted-foreground">
          客户集中度：{{ concentration }}
        </div>
      </div>
    </div>

    <!-- Layer4: 趋势 + 批次趋势 -->
    <div class="rounded-lg border bg-card p-4 shadow-sm">
      <div class="mb-2 font-medium text-card-foreground">
        月度开票 / 回款趋势
      </div>
      <trend-chart
        :data="overview.invoice_monthly ?? []"
        x-field="month"
        :series="financeSeries"
        :x-rotate="45"
        :legend-bottom="10"
      />
    </div>
    <a-collapse :default-active-key="[]">
      <a-collapse-panel key="finance" header="财务批次趋势（次级信息）">
        <trend-chart
          :data="overview.finance_trend ?? []"
          x-field="batch_id"
          :series="financeSeries"
        />
      </a-collapse-panel>
    </a-collapse>

    <!-- Layer5: 最近合同 -->
    <recent-contracts :rows="overview.recent_contracts" />
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import type { DashboardOverview } from '#/api/dashboard';
import ContractTypePie from '#/views/dashboard/components/contract-type-pie.vue';
import TopCustomersBar from '#/views/dashboard/components/top-customers-bar.vue';
import TrendChart from '#/views/dashboard/components/trend-chart.vue';
import MetricCard from './metric-card.vue';
import AlertStrip from './alert-strip.vue';
import RecentContracts from './recent-contracts.vue';
import { FINANCE_SERIES, fmtMoney, pctSafe } from '../dashboard-types';

const props = defineProps<{ overview: DashboardOverview }>();
defineEmits<{ navigate: [key: string] }>();

const financeSeries = FINANCE_SERIES;

const s = computed(() => props.overview.summary);

const riskTotal = computed(() => {
  const t = props.overview.pending_tasks;
  if (!t) return 0;
  return (
    t.unmatched_payments +
    t.pending_deliverables +
    t.overdue_payments +
    t.uninvoiced_contracts
  );
});

const statusBars = computed(() => {
  const arr = props.overview.contracts_by_status ?? [];
  const max = Math.max(1, ...arr.map((d) => d.amount || 0));
  return arr.map((d) => ({
    status: d.contract_status || '未分类',
    amount: d.amount,
    count: d.count,
    pct: ((d.amount || 0) / max) * 100,
  }));
});

const concentration = computed(() =>
  pctSafe(
    props.overview.top_customers?.[0]?.total_amount,
    props.overview.summary?.contract_total_amount,
  ),
);
</script>
