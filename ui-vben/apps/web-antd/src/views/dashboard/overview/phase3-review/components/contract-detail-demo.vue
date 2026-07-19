<script lang="ts" setup>
import type { ReviewContract } from '../review-data';

import { IconifyIcon } from '@vben/icons';

import EvidenceRail from './evidence-rail.vue';
import FinanceLanes from './finance-lanes.vue';

defineProps<{
  contract: ReviewContract;
}>();

defineEmits<{
  back: [];
}>();
</script>

<template>
  <div class="space-y-4">
    <section class="review-panel contract-detail-hero">
      <div class="review-panel__heading">
        <div>
          <a-button type="link" class="detail-back" @click="$emit('back')">
            <IconifyIcon icon="lucide:arrow-left" />
            返回档案总览
          </a-button>
          <span class="review-eyebrow">CONTRACT EVIDENCE PROFILE</span>
          <h2>{{ contract.projectName }}</h2>
          <div class="mt-2 flex flex-wrap gap-2">
            <a-tag color="cyan">{{ contract.contractId.value }}</a-tag>
            <a-tag>{{ contract.stateGridId }}</a-tag>
            <a-tag color="blue">{{ contract.legalForm }}</a-tag>
            <a-tag color="gold">{{ contract.deliveryType }}</a-tag>
            <a-tag color="orange">关键字段待核验</a-tag>
          </div>
        </div>
        <div class="detail-source-stamp">
          <IconifyIcon icon="lucide:database-zap" />
          <div>
            <strong>评审快照</strong>
            <span>不写生产数据</span>
          </div>
        </div>
      </div>
      <EvidenceRail :items="contract.evidence" />
    </section>

    <div class="contract-detail-grid">
      <section class="review-panel">
        <div class="review-panel__heading">
          <div>
            <span class="review-eyebrow">双轴合同画像</span>
            <h2>合同约定与执行形态</h2>
          </div>
          <a-tag color="processing">来源可追溯</a-tag>
        </div>
        <a-descriptions :column="2" bordered size="small">
          <a-descriptions-item label="内部编号">
            {{ contract.contractId.value }}
          </a-descriptions-item>
          <a-descriptions-item label="国网编号">
            {{ contract.stateGridId }}
          </a-descriptions-item>
          <a-descriptions-item label="交易形式">
            {{ contract.legalForm }}
          </a-descriptions-item>
          <a-descriptions-item label="执行形态">
            {{ contract.deliveryType }}
          </a-descriptions-item>
          <a-descriptions-item label="甲方" :span="2">
            {{ contract.partyA }}
          </a-descriptions-item>
          <a-descriptions-item label="金额口径">
            {{ contract.amountLabel }}
          </a-descriptions-item>
          <a-descriptions-item label="付款模式">
            {{ contract.paymentPattern }}
          </a-descriptions-item>
        </a-descriptions>
      </section>

      <section class="review-panel discrepancy-card">
        <span class="review-eyebrow">SOURCE DIFFERENCE</span>
        <h2>付款条款采用值</h2>
        <div class="discrepancy-row">
          <span>合同原文</span>
          <strong>验收合格后支付合同款</strong>
          <a-tag>原件</a-tag>
        </div>
        <div class="discrepancy-row">
          <span>业务候选</span>
          <strong>{{ contract.paymentPattern }}</strong>
          <a-tag color="orange">推断</a-tag>
        </div>
        <div class="discrepancy-row">
          <span>当前采用</span>
          <strong>保留原文，等待业务确认</strong>
          <a-tag color="gold">待核验</a-tag>
        </div>
        <div class="discrepancy-note">
          <IconifyIcon icon="lucide:shield-check" />
          系统不静默覆盖合同原文，采用值需记录规则、核验人和时间。
        </div>
      </section>
    </div>

    <section class="review-panel">
      <div class="review-panel__heading">
        <div>
          <span class="review-eyebrow">MILESTONE ≠ PAYMENT</span>
          <h2>项目阶段与付款触发</h2>
          <p>科研类允许 N:1，服务类允许验收、发票、资料归档等复合条件。</p>
        </div>
        <a-tag color="orange">当前 stage_payment_link = 0</a-tag>
      </div>
      <a-steps :current="1" responsive size="small">
        <a-step title="研究方案" description="成果已识别" />
        <a-step title="中期考核" description="付款候选待核验" />
        <a-step title="论文/专利/软著" description="可多阶段合并" />
        <a-step title="最终验收" description="触发条件待确认" />
      </a-steps>
    </section>

    <FinanceLanes />
  </div>
</template>
