<template>
  <div class="dashboard-view-stack">
    <!-- 首屏顺序固定：任务、风险、可信度、角色、变化。 -->
    <DashboardActionQueue
      :actions="overview.task_actions"
      empty-text="当前未识别到带对象的任务缺口。"
      kicker="任务 / 缺口"
      title="现在需要推进的事项"
    />
    <DashboardActionQueue
      :actions="overview.risk_actions"
      empty-text="当前未识别到带对象的风险或到期事项。"
      kicker="风险 / 到期"
      title="需优先核对的财务与合同缺口"
    />
    <DashboardDataContract :contract="overview.data_contract" />
    <DashboardRoleSummary :overview="overview" />
    <DashboardRecentChanges :changes="overview.recent_changes" />

    <section aria-label="经营快照" class="dashboard-panel">
      <div class="dashboard-panel__header">
        <div>
          <p class="dashboard-panel__kicker">经营快照</p>
          <h2 class="dashboard-panel__title">合同与资金的当前覆盖</h2>
        </div>
      </div>
      <div class="dashboard-summary-grid">
        <MetricCard label="合同总额" :value="summary.contract_total_amount" unit="万元" tone="primary" />
        <MetricCard label="累计开票" :value="summary.invoiced_amount" unit="万元" tone="invoiced" />
        <MetricCard label="累计回款" :value="summary.received_amount" unit="万元" tone="received" />
        <MetricCard label="未回款" :value="summary.unreceived_amount" unit="万元" tone="warning" />
      </div>
    </section>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

import type { DashboardOverview } from '#/api/dashboard'

import DashboardActionQueue from './DashboardActionQueue.vue'
import DashboardDataContract from './DashboardDataContract.vue'
import DashboardRecentChanges from './DashboardRecentChanges.vue'
import DashboardRoleSummary from './DashboardRoleSummary.vue'
import MetricCard from './metric-card.vue'

const props = defineProps<{ overview: DashboardOverview }>()
const summary = computed(() => props.overview.summary)
</script>
