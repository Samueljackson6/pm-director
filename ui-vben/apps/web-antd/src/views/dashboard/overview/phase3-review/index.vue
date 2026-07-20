<script lang="ts" setup>
import type { ReviewContract } from './review-data';

import { ref } from 'vue';

import { Page } from '@vben/common-ui';
import { IconifyIcon } from '@vben/icons';

import { Segmented } from 'ant-design-vue';

import ContractDetailDemo from './components/contract-detail-demo.vue';
import ContractWorkbench from './components/contract-workbench.vue';
import FinanceLanes from './components/finance-lanes.vue';
import MobileTaskDemo from './components/mobile-task-demo.vue';
import ReviewCenter from './components/review-center.vue';
import { reviewContracts, reviewSnapshot } from './review-data';

import './evidence-finance.css';
import './phase3-review.css';
import './phase3-review-detail.css';
import './phase3-review-mobile.css';

type ReviewScreen = 'detail' | 'mobile' | 'review' | 'workbench';

const activeScreen = ref<ReviewScreen>('workbench');
const selectedContract = ref<null | ReviewContract>(null);

const screenOptions = [
  { label: '档案总览', value: 'workbench' },
  { label: '合同详情', value: 'detail' },
  { label: '数据核验', value: 'review' },
  { label: '移动任务', value: 'mobile' },
];

function openDetail(contract: ReviewContract) {
  selectedContract.value = contract;
  activeScreen.value = 'detail';
}

function showWorkbench() {
  activeScreen.value = 'workbench';
}

function openFirstContract() {
  const firstContract = reviewContracts[0];
  if (firstContract) openDetail(firstContract);
}
</script>

<template>
  <Page auto-content-height class="phase3-review">
    <div class="review-shell">
      <header class="review-hero">
        <div
          class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between"
        >
          <div class="max-w-4xl">
            <span class="review-eyebrow">PHASE 3 · Vben Native Review</span>
            <h1>合同档案与数据核验工作台</h1>
            <p>
              从合同原件和低质量表格出发，把原值、推断、核验、履约、客户应收和供应商应付放回正确的业务关系中。
            </p>
          </div>
          <div class="flex flex-wrap gap-2">
            <a-tag color="cyan">真实 Vben 组件</a-tag>
            <a-tag color="gold">浅色优先</a-tag>
            <a-tag>不写生产数据</a-tag>
          </div>
        </div>

        <div class="review-demo-banner" role="status">
          <IconifyIcon icon="lucide:badge-info" />
          <span>
            <strong>评审 Demo：</strong>{{ reviewSnapshot.capturedAt }} ·
            {{ reviewSnapshot.source }} · 数字不代表实时经营口径。
          </span>
        </div>

        <div class="review-metrics">
          <article
            v-for="metric in reviewSnapshot.metrics"
            :key="metric.key"
            class="review-metric"
            :data-tone="metric.tone"
          >
            <span class="review-metric__label">{{ metric.label }}</span>
            <div class="review-metric__value">{{ metric.value }}</div>
            <span class="review-metric__note">{{ metric.note }}</span>
          </article>
        </div>
      </header>

      <div class="review-screen-nav">
        <div>
          <span class="review-eyebrow">REVIEW SCREENS</span>
          <p class="mt-1 text-sm text-muted-foreground">
            四个任务屏验证业务模型、Vben 兼容和多端边界
          </p>
        </div>
        <Segmented
          v-model:value="activeScreen"
          :options="screenOptions"
          size="large"
        />
      </div>

      <ContractWorkbench
        v-if="activeScreen === 'workbench'"
        @open-detail="openDetail"
      />

      <ContractDetailDemo
        v-else-if="activeScreen === 'detail' && selectedContract"
        :contract="selectedContract"
        @back="showWorkbench"
      />

      <section
        v-else-if="activeScreen === 'detail'"
        class="review-panel detail-empty-state"
      >
        <IconifyIcon icon="lucide:mouse-pointer-click" />
        <h2>请先从合同档案选择一条记录</h2>
        <p>详情会展示证据轨道、多编号、双轴类型、付款采用值和两条资金链。</p>
        <a-button type="primary" @click="openFirstContract">
          打开首个脱敏样例
        </a-button>
      </section>

      <ReviewCenter v-else-if="activeScreen === 'review'" />
      <MobileTaskDemo v-else-if="activeScreen === 'mobile'" />

      <section v-if="activeScreen === 'workbench'" class="mt-4">
        <FinanceLanes />
      </section>
    </div>
  </Page>
</template>
