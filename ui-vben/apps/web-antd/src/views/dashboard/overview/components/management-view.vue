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

    <!-- 管理者行动区 -->
    <div class="rounded-lg border bg-card p-4 shadow-sm">
      <div class="mb-3 font-medium text-card-foreground">管理者行动区 · 异常合同关注</div>
      <div v-if="actionItems.length" class="space-y-2">
        <div
          v-for="(item, idx) in actionItems"
          :key="idx"
          class="flex items-center justify-between rounded-lg border border-border p-3"
          :class="`dash-bg-${item.tone}`"
        >
          <div class="min-w-0">
            <div class="text-sm font-medium" :class="`dash-text-${item.tone}`">
              {{ item.title }}
            </div>
            <div class="text-xs text-muted-foreground">{{ item.detail }}</div>
          </div>
          <span class="shrink-0 text-xs text-muted-foreground">{{ item.metric }}</span>
        </div>
      </div>
      <div v-else class="py-4 text-center text-sm text-muted-foreground">
        暂无需关注的异常合同
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import type { DashboardOverview, RecentContract } from '#/api/dashboard';
import ContractTypePie from '#/views/dashboard/components/contract-type-pie.vue';
import TopCustomersBar from '#/views/dashboard/components/top-customers-bar.vue';
import TrendChart from '#/views/dashboard/components/trend-chart.vue';
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

interface ActionItem {
  tone: 'danger' | 'warning';
  title: string;
  detail: string;
  metric: string;
}

const actionItems = computed<ActionItem[]>(() => {
  const list: ActionItem[] = [];
  const rows = props.overview.recent_contracts ?? [];
  for (const r of rows as RecentContract[]) {
    if (r.invoice_total > 0 && r.payment_total < r.invoice_total * 0.5) {
      list.push({
        tone: 'danger',
        title: `回款率偏低 · ${r.contract_id}`,
        detail: r.project_name,
        metric: `回款率 ${pctSafe(r.payment_total, r.invoice_total)}`,
      });
    }
    if (r.invoice_total > r.contract_amount) {
      list.push({
        tone: 'warning',
        title: `开票率异常 · ${r.contract_id}`,
        detail: r.project_name,
        metric: `开票 ${fmtMoney(r.invoice_total)} / 合同 ${fmtMoney(r.contract_amount)}`,
      });
    }
  }
  // 大额无回款：合同额最大且回款为 0
  const maxContract = Math.max(0, ...rows.map((r) => r.contract_amount || 0));
  for (const r of rows as RecentContract[]) {
    if (maxContract > 0 && r.contract_amount === maxContract && r.payment_total === 0) {
      list.push({
        tone: 'warning',
        title: `大额无回款 · ${r.contract_id}`,
        detail: r.project_name,
        metric: `合同额 ${fmtMoney(r.contract_amount)} 万元`,
      });
    }
  }
  return list;
});
</script>
