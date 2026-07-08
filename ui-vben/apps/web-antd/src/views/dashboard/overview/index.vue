<template>
  <div class="p-4">
    <!-- Loading 态 -->
    <div
      v-if="loading"
      class="flex items-center justify-center py-20 text-muted-foreground"
    >
      <span>加载中…</span>
    </div>

    <!-- Error 态 -->
    <div
      v-else-if="error"
      class="rounded-lg border border-destructive/50 bg-destructive/10 p-6 text-center"
    >
      <p class="font-medium text-destructive">仪表盘数据加载失败</p>
      <p class="mt-1 text-sm text-muted-foreground">{{ error }}</p>
      <button
        class="mt-3 rounded border px-3 py-1 text-sm hover:bg-accent"
        @click="load"
      >
        重试
      </button>
    </div>

    <!-- 仪表盘主体 -->
    <template v-else-if="overview">
      <!-- KPI 卡片行 -->
      <div class="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <div
          v-for="kpi in kpiCards"
          :key="kpi.label"
          class="rounded-lg border bg-card p-4 shadow-sm"
        >
          <div class="text-muted-foreground text-sm">{{ kpi.label }}</div>
          <div class="mt-1 text-2xl font-bold">
            {{ formatNumber(kpi.value, kpi.digits) }}
            <span class="ml-1 text-sm font-normal text-muted-foreground">{{
              kpi.unit
            }}</span>
          </div>
        </div>
      </div>

      <!-- 三个图表并排：类型饼 / 发票饼 / Top 客户 -->
      <div class="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div class="rounded-lg border bg-card p-4 shadow-sm">
          <div class="mb-2 font-medium">合同类型分布（万元）</div>
          <contract-type-pie :data="overview.contracts_by_type ?? []" />
        </div>
        <div class="rounded-lg border bg-card p-4 shadow-sm">
          <div class="mb-2 font-medium">发票状态分布（万元）</div>
          <invoice-status-pie
            :data="overview.invoice_status_distribution ?? []"
          />
        </div>
        <div class="rounded-lg border bg-card p-4 shadow-sm">
          <div class="mb-2 font-medium">Top 客户（合同额·万元）</div>
          <top-customers-bar :data="overview.top_customers ?? []" />
        </div>
      </div>

      <!-- 财务快照趋势（全宽） -->
      <div class="mb-4 rounded-lg border bg-card p-4 shadow-sm">
        <div class="mb-2 font-medium">财务批次趋势（万元）</div>
        <finance-trend-chart :data="overview.finance_trend ?? []" />
      </div>

      <!-- 月度开票/回款趋势（全宽） -->
      <div class="mb-4 rounded-lg border bg-card p-4 shadow-sm">
        <div class="mb-2 font-medium">月度开票 / 回款趋势（万元）</div>
        <monthly-trend-chart :data="overview.invoice_monthly ?? []" />
      </div>

      <!-- 最近合同表 -->
      <div class="rounded-lg border bg-card shadow-sm">
        <div class="border-b px-4 py-3 font-medium">最近合同</div>
        <VxeTable
          v-if="overview.recent_contracts"
          :data="overview.recent_contracts"
          :column-config="{ minWidth: 120 }"
          :row-config="{ height: 44, isHover: true }"
          size="small"
          height="400"
        >
          <VxeColumn
            field="contract_id"
            title="合同编号"
            width="150"
            showOverflow
          />
          <VxeColumn
            field="project_name"
            title="项目名称"
            minWidth="250"
            showOverflow
          />
          <VxeColumn
            field="party_a"
            title="甲方"
            minWidth="180"
            showOverflow
          />
          <VxeColumn field="project_type" title="类型" width="100" />
          <VxeColumn field="contract_status" title="状态" width="100" />
          <VxeColumn field="sign_date" title="签订日期" width="110" />
          <VxeColumn
            field="contract_amount"
            title="合同额(万元)"
            width="130"
            align="right"
            :formatter="({ cellValue }) => cellValue != null ? Number(cellValue).toFixed(2) : '-'"
          />
          <VxeColumn
            field="invoice_total"
            title="已开票(万元)"
            width="120"
            align="right"
            :formatter="({ cellValue }) => cellValue != null ? Number(cellValue).toFixed(2) : '-'"
          />
          <VxeColumn
            field="payment_total"
            title="已回款(万元)"
            width="120"
            align="right"
            :formatter="({ cellValue }) => cellValue != null ? Number(cellValue).toFixed(2) : '-'"
          />
        </VxeTable>
        <div v-else class="py-4 text-center text-sm text-muted-foreground">
          暂无最近合同数据
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import { getDashboardOverviewApi } from '#/api/dashboard';
import type { DashboardOverview } from '#/api/dashboard';

import ContractTypePie from '#/views/dashboard/components/contract-type-pie.vue';
import InvoiceStatusPie from '#/views/dashboard/components/invoice-status-pie.vue';
import FinanceTrendChart from '#/views/dashboard/components/finance-trend-chart.vue';
import MonthlyTrendChart from '#/views/dashboard/components/monthly-trend-chart.vue';
import TopCustomersBar from '#/views/dashboard/components/top-customers-bar.vue';
import { VxeTable, VxeColumn } from '#/adapter/vxe-table';

/** 生命周期 */
const loading = ref(true);
const error = ref('');
const overview = ref<DashboardOverview | null>(null);

async function load() {
  loading.value = true;
  error.value = '';
  try {
    overview.value = await getDashboardOverviewApi();
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误';
  } finally {
    loading.value = false;
  }
}

onMounted(load);

/** KPI 卡片列表 */
const kpiCards = computed(() => {
  const s = overview.value?.summary;
  if (!s) return [];
  const unit = s.currency_unit || '万元';
  return [
    { label: '合同总数', value: s.contract_count, digits: 0, unit: '个' },
    { label: '合同总额', value: s.contract_total_amount, digits: 2, unit },
    { label: '已开票', value: s.invoiced_amount, digits: 2, unit },
    { label: '已回款', value: s.received_amount, digits: 2, unit },
    { label: '未回款', value: s.unreceived_amount, digits: 2, unit },
    { label: '回款率', value: s.receipt_rate, digits: 1, unit: '%' },
    { label: '分包已开票', value: s.sub_invoiced_amount, digits: 2, unit },
    { label: '分包已付款', value: s.sub_paid_amount, digits: 2, unit },
  ];
});

/** 格式化数字显示 */
function formatNumber(
  value: number | null | undefined,
  digits = 2,
): string {
  if (value == null || Number.isNaN(value)) return '-';
  return Number(value).toFixed(digits);
}
</script>
