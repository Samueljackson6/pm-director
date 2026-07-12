<template>
  <StateBlock
    :loading="loading"
    :error="error"
    error-title="综合看板加载失败"
    empty-text="暂无数据"
    @retry="load"
  >
    <div class="space-y-4 p-4">
      <dashboard-header
        :generated-at="overview?.generated_at"
        :unit="overview?.summary?.currency_unit"
        :loading="loading"
        @refresh="load"
      />
      <dashboard-tabs v-model="activeView" @change="onTabChange" />
      <all-view v-if="activeView === 'all'" :overview="currentOverview" @navigate="onAlertNavigate" />
      <management-view
        v-else-if="activeView === 'management'"
        :overview="currentOverview"
      />
      <project-view v-else-if="activeView === 'projects'" :overview="currentOverview" />
      <finance-view v-else :overview="currentOverview" />
    </div>
  </StateBlock>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { getDashboardOverviewApi } from '#/api/dashboard';
import type { DashboardOverview } from '#/api/dashboard';
import StateBlock from '#/components/state-block/index.vue';

import DashboardHeader from './components/dashboard-header.vue';
import DashboardTabs from './components/dashboard-tabs.vue';
import AllView from './components/all-view.vue';
import ManagementView from './components/management-view.vue';
import ProjectView from './components/project-view.vue';
import FinanceView from './components/finance-view.vue';
import { isValidViewKey, type ViewKey } from './dashboard-types';

const route = useRoute();
const router = useRouter();

const overview = ref<DashboardOverview | null>(null);
const loading = ref(true);
const error = ref('');

const activeView = ref<ViewKey>(
  isValidViewKey(route.query.view) ? (route.query.view as ViewKey) : 'all',
);

const currentOverview = computed(() => overview.value as DashboardOverview);

function load() {
  loading.value = true;
  error.value = '';
  getDashboardOverviewApi()
    .then((res) => {
      overview.value = res;
    })
    .catch((e: any) => {
      error.value = e?.response?.data?.message || e?.message || '未知错误';
    })
    .finally(() => {
      loading.value = false;
    });
}

onMounted(load);

const NAV_MAP: Record<string, string> = {
  unmatched_payments: '/invoices',
  pending_deliverables: '/projects',
  overdue_payments: '/projects',
  uninvoiced_contracts: '/contracts',
};

function onAlertNavigate(key: string) {
  const path = NAV_MAP[key];
  if (path) router.push(path);
}

function onTabChange(v: ViewKey) {
  activeView.value = v;
  router.replace({ query: { ...route.query, view: v } });
}

watch(
  () => route.query.view,
  (v) => {
    if (isValidViewKey(v) && v !== activeView.value) {
      activeView.value = v;
    }
  },
);
</script>

<style>
:root {
  --dash-primary: #1677ff;
  --dash-received: #16a36a;
  --dash-invoiced: #0f8fa8;
  --dash-warning: #d98e04;
  --dash-danger: #d64545;
}
.dark {
  --dash-primary: #4096ff;
  --dash-received: #3cc787;
  --dash-invoiced: #36c5d6;
  --dash-warning: #e8a33d;
  --dash-danger: #f27272;
}
.dash-text-primary {
  color: var(--dash-primary);
}
.dash-text-received {
  color: var(--dash-received);
}
.dash-text-invoiced {
  color: var(--dash-invoiced);
}
.dash-text-warning {
  color: var(--dash-warning);
}
.dash-text-danger {
  color: var(--dash-danger);
}
.dash-bg-primary {
  background: color-mix(in srgb, var(--dash-primary) 12%, transparent);
}
.dash-bg-received {
  background: color-mix(in srgb, var(--dash-received) 12%, transparent);
}
.dash-bg-invoiced {
  background: color-mix(in srgb, var(--dash-invoiced) 12%, transparent);
}
.dash-bg-warning {
  background: color-mix(in srgb, var(--dash-warning) 12%, transparent);
}
.dash-bg-danger {
  background: color-mix(in srgb, var(--dash-danger) 12%, transparent);
}
</style>
