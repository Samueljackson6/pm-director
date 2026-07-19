<script lang="ts" setup>
import { ref } from 'vue';

import { IconifyIcon } from '@vben/icons';

type MobileTaskKey = 'acceptance' | 'capture' | 'review' | 'sync';

type MobileTask = {
  readonly badge: string;
  readonly icon: string;
  readonly key: MobileTaskKey;
  readonly label: string;
  readonly note: string;
};

const tasks: readonly MobileTask[] = [
  {
    key: 'capture',
    label: '拍照采集',
    note: '合同首页、验收单、发票与凭证',
    icon: 'lucide:scan-line',
    badge: '高频',
  },
  {
    key: 'review',
    label: '快速核验',
    note: '只确认本次任务必要字段',
    icon: 'lucide:list-checks',
    badge: '3 项',
  },
  {
    key: 'acceptance',
    label: '现场验收',
    note: '证据、异常、整改与签名',
    icon: 'lucide:clipboard-check',
    badge: '弱网',
  },
  {
    key: 'sync',
    label: '同步队列',
    note: '断点续传、失败重试与冲突',
    icon: 'lucide:refresh-cw',
    badge: '2 待传',
  },
];

const activeTask = ref<MobileTaskKey>('capture');
</script>

<template>
  <div class="mobile-demo-layout">
    <section class="review-panel mobile-demo-copy">
      <span class="review-eyebrow">MINI PROGRAM / APP</span>
      <h2>移动端不是缩小版后台</h2>
      <p>
        小程序负责今日任务、拍照采集、轻量核验与审批；App
        增加离线任务包、断点续传和完整现场验收。
      </p>
      <div class="mobile-principles">
        <div>
          <IconifyIcon icon="lucide:wifi-off" />
          <span>
            <strong>弱网优先</strong>
            <small>加密草稿、幂等键、同步游标</small>
          </span>
        </div>
        <div>
          <IconifyIcon icon="lucide:file-lock-2" />
          <span>
            <strong>最小缓存</strong>
            <small>不长期保存完整合同和敏感信息</small>
          </span>
        </div>
        <div>
          <IconifyIcon icon="lucide:workflow" />
          <span>
            <strong>同一领域规则</strong>
            <small>三端共享 API、状态和权限</small>
          </span>
        </div>
      </div>
      <div class="mobile-boundary">
        <strong>首期边界</strong>
        <p>
          仅面向内部项目经理、现场人员和管理层；客户/供应商门户另行评估租户隔离与审计。
        </p>
      </div>
    </section>

    <section class="mobile-device" aria-label="移动任务流评审样例">
      <div class="mobile-device__topbar">
        <span>09:42</span>
        <strong>今日任务</strong>
        <IconifyIcon icon="lucide:bell" />
      </div>
      <div class="mobile-device__summary">
        <span>星期三 · 评审样例</span>
        <strong>4 类任务等待处理</strong>
        <p>只展示与当前角色和项目相关的最小信息。</p>
      </div>
      <div class="mobile-task-list">
        <button
          v-for="task in tasks"
          :key="task.key"
          class="mobile-task"
          :data-active="activeTask === task.key"
          type="button"
          @click="activeTask = task.key"
        >
          <span class="mobile-task__icon">
            <IconifyIcon :icon="task.icon" />
          </span>
          <span>
            <strong>{{ task.label }}</strong>
            <small>{{ task.note }}</small>
          </span>
          <em>{{ task.badge }}</em>
        </button>
      </div>
      <div class="mobile-action-preview">
        <template v-if="activeTask === 'capture'">
          <span>采集流程</span>
          <strong>拍照 → 压缩 → 哈希 → OCR → 待核验</strong>
        </template>
        <template v-else-if="activeTask === 'review'">
          <span>核验原则</span>
          <strong>原值与候选值并排，不自动采用</strong>
        </template>
        <template v-else-if="activeTask === 'acceptance'">
          <span>现场证据</span>
          <strong>检查项、照片、异常、签名和位置留痕</strong>
        </template>
        <template v-else>
          <span>离线同步</span>
          <strong>2 条待传 · 网络恢复后断点续传</strong>
        </template>
      </div>
      <nav class="mobile-tabbar" aria-label="移动端主导航">
        <span class="is-active">
          <IconifyIcon icon="lucide:list-todo" />今日
        </span>
        <span><IconifyIcon icon="lucide:scan-line" />采集</span>
        <span><IconifyIcon icon="lucide:folder-kanban" />项目</span>
        <span><IconifyIcon icon="lucide:user-round" />我的</span>
      </nav>
    </section>
  </div>
</template>
