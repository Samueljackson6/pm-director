<template>
  <div class="dashboard-view-stack">
    <DashboardDataContract :contract="overview.data_contract" />
    <DashboardActionQueue
      :actions="overview.verification_actions"
      empty-text="没有已识别的核验缺口；这不代表数据已完整核验。"
      kicker="核验队列"
      title="可回溯的数据缺口"
    />
    <section aria-label="指标口径明细" class="dashboard-panel">
      <div class="dashboard-panel__header">
        <div>
          <p class="dashboard-panel__kicker">指标明细</p>
          <h2 class="dashboard-panel__title">金额口径与数据截止</h2>
        </div>
      </div>
      <div class="dashboard-metric-contracts">
        <article v-for="metric in overview.data_contract.metrics" :key="metric.key">
          <h3>{{ metric.label }} <span>{{ metric.unit }}</span></h3>
          <p>{{ metric.definition }}</p>
          <dl>
            <div><dt>来源</dt><dd>{{ metric.source.join(' · ') }}</dd></div>
            <div><dt>覆盖</dt><dd>{{ metric.coverage }}</dd></div>
            <div><dt>核验</dt><dd>待核验</dd></div>
            <div><dt>数据截止</dt><dd>{{ formatTime(metric.data_as_of) }}</dd></div>
          </dl>
        </article>
      </div>
    </section>
  </div>
</template>

<script lang="ts" setup>
import type { DashboardOverview } from '#/api/dashboard'

import DashboardActionQueue from './DashboardActionQueue.vue'
import DashboardDataContract from './DashboardDataContract.vue'

defineProps<{ overview: DashboardOverview }>()

function formatTime(value: null | string): string {
  return value ? value.replace('T', ' ').slice(0, 16) : '待补充'
}
</script>
