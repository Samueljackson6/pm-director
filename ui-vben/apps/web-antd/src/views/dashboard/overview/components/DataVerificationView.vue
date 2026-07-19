<template>
  <div class="dashboard-view-stack">
    <DashboardDataContract :contract="overview.data_contract" />
    <DashboardActionQueue
      :actions="overview.verification_actions"
      empty-text="&#x6CA1;&#x6709;&#x5DF2;&#x8BC6;&#x522B;&#x7684;&#x6838;&#x9A8C;&#x7F3A;&#x53E3;&#xFF1B;&#x8FD9;&#x4E0D;&#x4EE3;&#x8868;&#x6570;&#x636E;&#x5DF2;&#x5B8C;&#x6574;&#x6838;&#x9A8C;&#x3002;"
      kicker="&#x6838;&#x9A8C;&#x961F;&#x5217;"
      title="&#x53EF;&#x56DE;&#x6EAF;&#x7684;&#x6570;&#x636E;&#x7F3A;&#x53E3;"
    />
    <section
      aria-label="&#x6307;&#x6807;&#x53E3;&#x5F84;&#x660E;&#x7EC6;"
      class="dashboard-panel"
    >
      <div class="dashboard-panel__header">
        <div>
          <p class="dashboard-panel__kicker">
            &#x6307;&#x6807;&#x660E;&#x7EC6;
          </p>
          <h2 class="dashboard-panel__title">
            &#x91D1;&#x989D;&#x53E3;&#x5F84;&#x4E0E;&#x6570;&#x636E;&#x622A;&#x6B62;
          </h2>
        </div>
      </div>
      <div class="dashboard-metric-contracts">
        <article
          v-for="metric in overview.data_contract.metrics"
          :key="metric.key"
        >
          <h3>
            {{ metric.label }} <span>{{ metric.unit }}</span>
          </h3>
          <p>{{ metric.definition }}</p>
          <dl>
            <div>
              <dt>&#x6765;&#x6E90;</dt>
              <dd>{{ metric.source.join(' / ') }}</dd>
            </div>
            <div>
              <dt>&#x8986;&#x76D6;</dt>
              <dd>{{ metric.coverage }}</dd>
            </div>
            <div>
              <dt>&#x6838;&#x9A8C;</dt>
              <dd>&#x5F85;&#x6838;&#x9A8C;</dd>
            </div>
            <div>
              <dt>&#x6570;&#x636E;&#x622A;&#x6B62;</dt>
              <dd>
                {{ formatTime(metric.data_as_of) }}
                <span
                  v-if="isStale(metric.data_as_of)"
                  class="dashboard-stale-note"
                  >&#x5386;&#x53F2;&#x5FEB;&#x7167;&#xFF0C;&#x9700;&#x590D;&#x6838;</span
                >
              </dd>
            </div>
          </dl>
        </article>
      </div>
    </section>
  </div>
</template>

<script lang="ts" setup>
import type { DashboardOverview } from '#/api/dashboard';

import DashboardActionQueue from './DashboardActionQueue.vue';
import DashboardDataContract from './DashboardDataContract.vue';

defineProps<{ overview: DashboardOverview }>();

function formatTime(value: null | string): string {
  return value
    ? value.replace('T', ' ').slice(0, 16)
    : String.fromCodePoint(0x5f85, 0x8865, 0x5145);
}

function isStale(value: null | string): boolean {
  if (!value) return false;
  const timestamp = Date.parse(value);
  return (
    Number.isFinite(timestamp) && Date.now() - timestamp > 36 * 60 * 60 * 1000
  );
}
</script>
