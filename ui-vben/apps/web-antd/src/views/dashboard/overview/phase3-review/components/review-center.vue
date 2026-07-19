<script lang="ts" setup>
import type { ReviewIssue } from '../review-data';

import { computed, ref } from 'vue';

import { useVbenDrawer } from '@vben/common-ui';
import { IconifyIcon } from '@vben/icons';

import { reviewIssues } from '../review-data';

type IssueFilter = 'all' | 'critical' | 'warning';

const issueFilter = ref<IssueFilter>('all');
const selectedIssue = ref<null | ReviewIssue>(null);

const issueGroups: Record<IssueFilter, readonly ReviewIssue[]> = {
  all: reviewIssues,
  critical: reviewIssues.filter((issue) => issue.level === 'critical'),
  warning: reviewIssues.filter((issue) => issue.level === 'warning'),
};

const visibleIssues = computed(() => issueGroups[issueFilter.value]);

const [Drawer, drawerApi] = useVbenDrawer({
  class: 'w-[min(520px,92vw)]',
  footer: false,
  title: '数据核验任务',
});

function openIssue(issue: ReviewIssue) {
  selectedIssue.value = issue;
  drawerApi.setState({ title: issue.title });
  drawerApi.open();
}
</script>

<template>
  <section class="review-panel">
    <div class="review-panel__heading">
      <div>
        <span class="review-eyebrow">REVIEW QUEUE · Vben Drawer</span>
        <h2>数据核验中心</h2>
        <p>把原值、候选值、采用值和修订留痕放在同一任务中。</p>
      </div>
      <a-segmented
        v-model:value="issueFilter"
        :options="[
          { label: '全部', value: 'all' },
          { label: '阻断', value: 'critical' },
          { label: '提醒', value: 'warning' },
        ]"
      />
    </div>

    <div class="issue-grid">
      <button
        v-for="issue in visibleIssues"
        :key="issue.code"
        class="issue-card"
        :data-level="issue.level"
        type="button"
        @click="openIssue(issue)"
      >
        <span class="issue-card__icon">
          <IconifyIcon
            :icon="
              issue.level === 'critical'
                ? 'lucide:circle-alert'
                : 'lucide:scan-search'
            "
          />
        </span>
        <span class="issue-card__content">
          <span class="issue-card__meta">
            {{ issue.level === 'critical' ? '阻断问题' : '待补问题' }} ·
            {{ issue.count }} 条
          </span>
          <strong>{{ issue.title }}</strong>
          <small>{{ issue.description }}</small>
        </span>
        <IconifyIcon class="issue-card__arrow" icon="lucide:arrow-up-right" />
      </button>
    </div>

    <Drawer>
      <div v-if="selectedIssue" class="issue-drawer">
        <div class="issue-drawer__banner" :data-level="selectedIssue.level">
          <IconifyIcon icon="lucide:shield-alert" />
          <div>
            <strong>{{ selectedIssue.count }} 条记录等待人工确认</strong>
            <p>此评审 Demo 不执行迁移或数据库写入。</p>
          </div>
        </div>
        <a-descriptions :column="1" bordered size="small">
          <a-descriptions-item label="问题代码">
            {{ selectedIssue.code }}
          </a-descriptions-item>
          <a-descriptions-item label="当前状态">待核验</a-descriptions-item>
          <a-descriptions-item label="事实说明">
            {{ selectedIssue.description }}
          </a-descriptions-item>
          <a-descriptions-item label="建议动作">
            {{ selectedIssue.action }}
          </a-descriptions-item>
        </a-descriptions>
        <div class="issue-drawer__audit">
          <span>原始来源</span>
          <strong>财务 Excel 导入批次（历史）</strong>
          <span>核验边界</span>
          <strong>只生成候选，不自动采用</strong>
          <span>后续留痕</span>
          <strong>核验人 · 核验时间 · 采用理由</strong>
        </div>
      </div>
    </Drawer>
  </section>
</template>
