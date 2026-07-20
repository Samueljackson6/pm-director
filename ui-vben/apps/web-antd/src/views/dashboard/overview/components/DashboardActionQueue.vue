<template>
  <section :aria-label="title" class="dashboard-panel">
    <div class="dashboard-panel__header">
      <div>
        <p class="dashboard-panel__kicker">{{ kicker }}</p>
        <h2 class="dashboard-panel__title">{{ title }}</h2>
      </div>
      <span class="dashboard-panel__count">{{ actions.length }} 项</span>
    </div>

    <div v-if="actions.length" class="dashboard-action-list">
      <article v-for="action in actions" :key="action.action_id" class="dashboard-action-item">
        <div class="dashboard-action-item__body">
          <div class="dashboard-action-item__heading">
            <span :class="`dashboard-status dashboard-status--${tone(action.status)}`">
              {{ statusLabel(action.status) }}
            </span>
            <span class="dashboard-action-item__object">{{ objectLabel(action) }}</span>
          </div>
          <h3>{{ action.title }}</h3>
          <p>{{ action.reason }}</p>
          <dl class="dashboard-action-item__meta">
            <div><dt>截止</dt><dd>{{ action.due_date || '待补充' }}</dd></div>
            <div><dt>责任人</dt><dd>{{ action.owner || '待核验' }}</dd></div>
          </dl>
        </div>
        <a-button type="link" @click="navigate(action)">查看对象</a-button>
      </article>
    </div>
    <div v-else class="dashboard-panel__empty">{{ emptyText }}</div>
  </section>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router'

import type { DashboardAction } from '#/api/dashboard'

const props = withDefaults(
  defineProps<{
    actions?: DashboardAction[]
    emptyText?: string
    kicker: string
    title: string
  }>(),
  { actions: () => [], emptyText: '当前没有可下钻的记录。' },
)

const router = useRouter()

function navigate(action: DashboardAction) {
  router.push({ path: action.target.path, query: action.target.query })
}

function tone(status: string): 'danger' | 'neutral' | 'warning' {
  if (status === 'overdue') return 'danger'
  if (status === 'pending') return 'warning'
  return 'neutral'
}

function statusLabel(status: string): string {
  if (status === 'overdue') return '逾期'
  if (status === 'pending') return '待处理'
  return '待核验'
}

function objectLabel(action: DashboardAction): string {
  const labels: Record<string, string> = {
    contract: '合同',
    deliverable: '交付物',
    invoice: '发票',
    payment: '付款条件',
    project: '项目',
  }
  return `${labels[action.object_type] || '对象'} · ${action.object_id}`
}
</script>
