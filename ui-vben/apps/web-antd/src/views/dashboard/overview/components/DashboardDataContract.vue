<template>
  <section aria-label="数据口径与覆盖范围" class="dashboard-panel">
    <div class="dashboard-panel__header">
      <div>
        <p class="dashboard-panel__kicker">数据口径</p>
        <h2 class="dashboard-panel__title">数据可信度</h2>
      </div>
      <span class="dashboard-status dashboard-status--neutral">待核验</span>
    </div>
    <p class="dashboard-contract__summary">{{ contract.verification_summary.description }}</p>
    <p class="dashboard-contract__summary dashboard-contract__summary--small">
      待处理核验缺口 {{ contract.verification_summary.pending_action_count }} 项
      <span aria-hidden="true">·</span>
      聚合生成时间 {{ formatTime(contract.generated_at) }}
    </p>
    <div class="dashboard-contract__sources">
      <article v-for="source in contract.sources" :key="source.key" class="dashboard-contract__source">
        <div>
          <h3>{{ source.label }}</h3>
          <p>{{ source.coverage }}</p>
        </div>
        <dl>
          <div><dt>来源</dt><dd>{{ source.source.join(' · ') }}</dd></div>
          <div><dt>数据截止</dt><dd>{{ formatTime(source.data_as_of) }}</dd></div>
        </dl>
      </article>
    </div>
  </section>
</template>

<script lang="ts" setup>
import type { DashboardDataContract } from '#/api/dashboard'

defineProps<{ contract: DashboardDataContract }>()

function formatTime(value: null | string): string {
  if (!value) return '待补充'
  return value.replace('T', ' ').slice(0, 16)
}
</script>
