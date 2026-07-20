<template>
  <div class="space-y-4">
    <!-- Metrics -->
    <div class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
      <metric-card
        label="合同总额"
        :value="s?.contract_total_amount"
        unit="万元"
        tone="primary"
        :sub="`共 ${s?.contract_count ?? 0} 个合同`"
      />
      <metric-card label="合同数量" :value="s?.contract_count" unit="个" :digits="0" />
      <metric-card
        label="已开票"
        :value="s?.invoiced_amount"
        unit="万元"
        tone="invoiced"
      />
      <metric-card
        label="未开票"
        :value="s?.uninvoiced_amount"
        unit="万元"
        tone="warning"
      />
      <metric-card
        label="已回款"
        :value="s?.received_amount"
        unit="万元"
        tone="received"
        :ratio="`占合同总额 ${receivedRatio}%`"
      />
      <metric-card
        label="未回款"
        :value="s?.unreceived_amount"
        unit="万元"
        tone="danger"
      />
      <metric-card
        label="回款率"
        :value="s?.receipt_rate"
        unit="%"
        :digits="1"
        tone="received"
      />
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div class="rounded-lg border bg-card p-4 shadow-sm">
        <div class="mb-2 font-medium text-card-foreground">合同类型金额结构</div>
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

    <!-- 趋势 -->
    <div class="rounded-lg border bg-card p-4 shadow-sm">
      <div class="mb-2 font-medium text-card-foreground">月度开票 / 回款趋势</div>
      <trend-chart
        :data="overview.invoice_monthly ?? []"
        x-field="month"
        :series="financeSeries"
        :x-rotate="45"
        :legend-bottom="10"
      />
    </div>

    <!-- 管理层需要的风险项目必须能进入真实合同或项目详情。 -->
    <DashboardActionQueue
      :actions="overview.risk_actions"
      empty-text="当前未识别到可下钻的经营风险或到期事项；这不代表不存在未记录的风险。"
      kicker="管理者行动"
      title="需优先决策的合同与资金缺口"
    />
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import type { DashboardOverview } from '#/api/dashboard';
import ContractTypePie from '#/views/dashboard/components/contract-type-pie.vue';
import TopCustomersBar from '#/views/dashboard/components/top-customers-bar.vue';
import TrendChart from '#/views/dashboard/components/trend-chart.vue';
import DashboardActionQueue from './DashboardActionQueue.vue';
import MetricCard from './metric-card.vue';
import { FINANCE_SERIES, fmtMoney, pctSafe } from '../dashboard-types';

const props = defineProps<{ overview: DashboardOverview }>();

const financeSeries = FINANCE_SERIES;
const s = computed(() => props.overview.summary);

const receivedRatio = computed(() =>
  pctSafe(s.value?.received_amount, s.value?.contract_total_amount),
);

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
    s.value?.contract_total_amount,
  ),
);


</script>
