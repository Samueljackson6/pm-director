<script lang="ts" setup>
import { IconifyIcon } from '@vben/icons';

import { reviewSnapshot } from '../review-data';

const statusLabels = {
  blocked: '尚无事实数据',
  needs_review: '待核验',
  partial: '部分具备',
  verified: '已核验',
} as const;
</script>

<template>
  <div class="finance-lanes">
    <section class="finance-lane finance-lane--customer">
      <div class="finance-lane__heading">
        <span class="finance-lane__icon">
          <IconifyIcon icon="lucide:landmark" />
        </span>
        <div>
          <strong>客户应收链</strong>
          <p>国网合同约定驱动开票与实际回款</p>
        </div>
      </div>
      <div class="finance-lane__steps">
        <div
          v-for="(step, index) in reviewSnapshot.customerLane"
          :key="step.label"
          class="finance-step"
          :data-status="step.status"
        >
          <span class="finance-step__index">{{ index + 1 }}</span>
          <strong>{{ step.label }}</strong>
          <small>{{ statusLabels[step.status] }}</small>
        </div>
      </div>
    </section>

    <section class="finance-lane finance-lane--supplier">
      <div class="finance-lane__heading">
        <span class="finance-lane__icon">
          <IconifyIcon icon="lucide:package-check" />
        </span>
        <div>
          <strong>供应商应付链</strong>
          <p>只展示项目下游采购、收票与付款事实</p>
        </div>
      </div>
      <div class="finance-lane__steps">
        <div
          v-for="(step, index) in reviewSnapshot.supplierLane"
          :key="step.label"
          class="finance-step"
          :data-status="step.status"
        >
          <span class="finance-step__index">{{ index + 1 }}</span>
          <strong>{{ step.label }}</strong>
          <small>{{ statusLabels[step.status] }}</small>
        </div>
      </div>
      <div class="finance-lane__warning">
        <IconifyIcon icon="lucide:triangle-alert" />
        当前供应商付款为 0，历史 inbound 记录不得作为供应商发票使用。
      </div>
    </section>
  </div>
</template>
