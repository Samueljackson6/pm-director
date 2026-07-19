<template>
  <a-modal
    :open="visible"
    title="风险与待处理详情"
    :footer="null"
    width="720px"
    @update:open="$emit('update:visible', $event)"
  >
    <div class="space-y-4">
      <div
        v-for="item in riskItems"
        :key="item.key"
        class="rounded-lg border p-4 cursor-pointer transition-colors hover:bg-accent"
        :class="`dash-bg-${item.tone}`"
        @click="handleNavigate(item.key)"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full flex items-center justify-center text-white text-lg font-bold"
              :style="{ backgroundColor: toneColor(item.tone) }">
              {{ item.count }}
            </div>
            <div>
              <div class="font-medium text-card-foreground">{{ item.label }}</div>
              <div class="text-xs text-muted-foreground mt-0.5">{{ item.description }}</div>
            </div>
          </div>
          <div class="flex items-center gap-2 text-primary">
            <span class="text-sm">查看详情</span>
            <span class="text-lg">&#8594;</span>
          </div>
        </div>
      </div>
    </div>
    <div class="mt-4 pt-4 border-t text-center text-xs text-muted-foreground">
      点击卡片可跳转到对应筛选页面
    </div>
  </a-modal>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import type { PendingTasks } from '#/api/dashboard';
import { DASH_COLORS, type DashTone } from '../dashboard-types';

const props = defineProps<{
  visible: boolean;
  tasks: PendingTasks;
}>();

const emit = defineEmits<{
  'update:visible': [boolean];
}>();

const router = useRouter();

interface RiskItem {
  key: string;
  label: string;
  description: string;
  count: number;
  tone: DashTone;
  targetPath: string;
  filterParam?: string;
}

const riskItems = computed<RiskItem[]>(() => [
  {
    key: 'unmatched_payments',
    label: '待匹配回款',
    description: '发票/回款记录未正确匹配到合同，需人工核对',
    count: props.tasks?.unmatched_payments ?? 0,
    tone: 'danger',
    targetPath: '/customer-finance/invoices',
    filterParam: 'payment_status=未匹配',
  },
  {
    key: 'pending_deliverables',
    label: '待交付成果',
    description: '项目交付物尚未完成交付',
    count: props.tasks?.pending_deliverables ?? 0,
    tone: 'warning',
    targetPath: '/contracts/list',
    filterParam: 'deliverable_status=pending',
  },
  {
    key: 'overdue_payments',
    label: '逾期付款',
    description: '计划付款日期已过但未全额收到款项',
    count: props.tasks?.overdue_payments ?? 0,
    tone: 'danger',
    targetPath: '/contracts/list',
    filterParam: 'payment_overdue=true',
  },
  {
    key: 'uninvoiced_contracts',
    label: '未开票合同',
    description: '合同金额大于已开票金额，存在未开票部分',
    count: props.tasks?.uninvoiced_contracts ?? 0,
    tone: 'warning',
    targetPath: '/contracts/list',
    filterParam: 'invoice_status=uninvoiced',
  },
]);

function toneColor(tone: DashTone): string {
  return tone === 'none' ? DASH_COLORS.primary : DASH_COLORS[tone];
}

function handleNavigate(key: string) {
  const item = riskItems.value.find(r => r.key === key);
  if (!item) return;

  const path = item.filterParam
    ? `${item.targetPath}?${item.filterParam}`
    : item.targetPath;
  router.push(path);
  emit('update:visible', false);
}
</script>