<template>
  <section aria-label="最近变化" class="dashboard-panel">
    <div class="dashboard-panel__header">
      <div>
        <p class="dashboard-panel__kicker">系统记录</p>
        <h2 class="dashboard-panel__title">最近变化</h2>
      </div>
      <span class="dashboard-panel__count">{{ changes.length }} 条</span>
    </div>
    <ul v-if="changes.length" class="dashboard-change-list">
      <li v-for="change in changes" :key="`${change.object_type}-${change.object_id}`">
        <div>
          <strong>{{ change.title }}</strong>
          <span>{{ change.change_type }} · {{ formatTime(change.changed_at) }}</span>
        </div>
        <a-button type="link" @click="navigate(change)">查看</a-button>
      </li>
    </ul>
    <div v-else class="dashboard-panel__empty">没有可显示的存储记录时间。</div>
  </section>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router'

import type { DashboardRecentChange } from '#/api/dashboard'

withDefaults(defineProps<{ changes?: DashboardRecentChange[] }>(), { changes: () => [] })
const router = useRouter()

function navigate(change: DashboardRecentChange) {
  router.push({ path: change.target.path, query: change.target.query })
}

function formatTime(value: null | string): string {
  return value ? value.replace('T', ' ').slice(0, 16) : '待补充'
}
</script>
