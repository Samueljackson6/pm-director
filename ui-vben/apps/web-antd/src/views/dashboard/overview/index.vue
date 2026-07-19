<template>
  <Page
    class="pm-workbench-page dashboard-page"
    content-class="dashboard-page__content"
    description="从任务缺口、风险、数据口径进入合同、项目和财务对象。"
    title="经营与任务驾驶舱"
  >
    <template #extra>
      <DashboardHeader
        :generated-at="overview?.generated_at"
        :loading="loading"
        :unit="overview?.summary?.currency_unit"
        @refresh="load"
      />
    </template>

    <StateBlock
      :error="error"
      :loading="loading"
      empty-text="暂无可用的驾驶舱聚合数据"
      error-title="驾驶舱加载失败"
      @retry="load"
    >
      <div v-if="overview" class="dashboard-page__body">
        <DashboardTabs v-model="activeView" @change="onTabChange" />

        <section
          :id="`dashboard-panel-${activeView}`"
          :aria-labelledby="`dashboard-tab-${activeView}`"
          role="tabpanel"
        >
          <AllView v-if="activeView === 'all'" :overview="overview" />
          <ManagementView v-else-if="activeView === 'management'" :overview="overview" />
          <ProjectView v-else-if="activeView === 'projects'" :overview="overview" />
          <FinanceView v-else-if="activeView === 'finance'" :overview="overview" />
          <DataVerificationView v-else :overview="overview" />
        </section>
      </div>
    </StateBlock>
  </Page>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { Page } from '@vben/common-ui'

import { getDashboardOverviewApi, type DashboardOverview } from '#/api/dashboard'
import StateBlock from '#/components/state-block/index.vue'

import AllView from './components/all-view.vue'
import DashboardHeader from './components/dashboard-header.vue'
import DashboardTabs from './components/dashboard-tabs.vue'
import DataVerificationView from './components/DataVerificationView.vue'
import FinanceView from './components/finance-view.vue'
import ManagementView from './components/management-view.vue'
import ProjectView from './components/project-view.vue'
import { isValidViewKey, type ViewKey } from './dashboard-types'

const route = useRoute()
const overview = ref<DashboardOverview | null>(null)
const loading = ref(true)
const error = ref('')
const activeView = ref<ViewKey>(
  isValidViewKey(route.query.view) ? route.query.view : 'all',
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    overview.value = await getDashboardOverviewApi()
  } catch (cause: any) {
    error.value = cause?.response?.data?.message || cause?.message || '未知错误'
  } finally {
    loading.value = false
  }
}

function onTabChange(view: ViewKey) {
  // Update only the current hash query; do not remount or re-fetch the overview.
  const url = new URL(window.location.href)
  const [hashPath, hashQuery = ''] = url.hash.replace(/^#/, '').split('?')
  const query = new URLSearchParams(hashQuery)
  query.set('view', view)
  url.hash = `${hashPath}?${query.toString()}`
  window.history.replaceState(window.history.state, '', url)
}

watch(
  () => route.query.view,
  (value) => {
    if (isValidViewKey(value) && value !== activeView.value) {
      activeView.value = value
    }
  },
)

onMounted(() => {
  void load()
})
</script>
