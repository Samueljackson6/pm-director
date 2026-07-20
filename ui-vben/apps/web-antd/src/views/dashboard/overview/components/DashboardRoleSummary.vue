<template>
  <section aria-label="角色摘要" class="dashboard-panel">
    <div class="dashboard-panel__header">
      <div>
        <p class="dashboard-panel__kicker">角色视角</p>
        <h2 class="dashboard-panel__title">每个角色的当前第一步</h2>
      </div>
    </div>
    <div class="dashboard-role-grid">
      <article v-for="item in items" :key="item.role" class="dashboard-role-card">
        <h3>{{ item.role }}</h3>
        <p>{{ item.summary }}</p>
        <span>{{ item.note }}</span>
      </article>
    </div>
  </section>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

import type { DashboardOverview } from '#/api/dashboard'

const props = defineProps<{ overview: DashboardOverview }>()

const items = computed(() => {
  const tasks = props.overview.pending_tasks
  const execution = props.overview.project_execution
  return [
    {
      role: '项目总监 / 管理层',
      summary: `需优先决策 ${props.overview.risk_actions.length} 项风险与财务缺口。`,
      note: `近期需处理 ${props.overview.task_actions.length} 项任务`,
    },
    {
      role: '项目经理',
      summary: `待交付 ${execution.pending_deliverables} 项，逾期阶段 ${execution.overdue_stages} 项。`,
      note: `缺失项目责任人 ${execution.missing_manager_projects} 条`,
    },
    {
      role: '财务',
      summary: `未匹配回款 ${tasks.unmatched_payments} 笔，逾期付款 ${tasks.overdue_payments} 项。`,
      note: `累计未回款 ${props.overview.summary.unreceived_amount.toFixed(2)} 万元`,
    },
    {
      role: '数据核验人员',
      summary: `待回溯核验 ${props.overview.verification_actions.length} 项。`,
      note: '金额、来源与映射需按对象回到原件或运营表。',
    },
  ]
})
</script>
