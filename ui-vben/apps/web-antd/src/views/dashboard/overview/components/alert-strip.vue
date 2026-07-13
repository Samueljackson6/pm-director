<template>
  <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
    <div
      v-for="item in items"
      :key="item.key"
      class="cursor-pointer rounded-lg border border-border p-3 shadow-sm transition-colors hover:bg-accent"
      :class="`dash-bg-${item.tone}`"
      @click="handleNavigate(item)"
    >
      <div class="text-xs text-muted-foreground">{{ item.label }}</div>
      <div class="mt-1 text-2xl font-bold" :class="`dash-text-${item.tone}`">
        {{ item.count }}
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import type { PendingTasks } from '#/api/dashboard';

const props = defineProps<{ tasks: PendingTasks }>();
const emit = defineEmits<{ navigate: [key: string] }>();

const router = useRouter();

interface AlertItem {
  key: string;
  label: string;
  tone: 'danger' | 'warning';
  count: number;
  targetPath: string;
  filterParam?: string;
}

const items = computed<AlertItem[]>(() => [
  {
    key: 'unmatched_payments',
    label: '待匹配回款',
    tone: 'danger',
    count: props.tasks?.unmatched_payments ?? 0,
    targetPath: '/customer-finance/invoices',
    filterParam: 'payment_status=未匹配',
  },
  {
    key: 'pending_deliverables',
    label: '待交付成果',
    tone: 'warning',
    count: props.tasks?.pending_deliverables ?? 0,
    targetPath: '/contracts/list',
    filterParam: 'deliverable_status=pending',
  },
  {
    key: 'overdue_payments',
    label: '逾期付款',
    tone: 'danger',
    count: props.tasks?.overdue_payments ?? 0,
    targetPath: '/contracts/list',
    filterParam: 'payment_overdue=true',
  },
  {
    key: 'uninvoiced_contracts',
    label: '未开票合同',
    tone: 'warning',
    count: props.tasks?.uninvoiced_contracts ?? 0,
    targetPath: '/contracts/list',
    filterParam: 'invoice_status=uninvoiced',
  },
]);

function handleNavigate(item: AlertItem) {
  // Emit the legacy event for backwards compatibility
  emit('navigate', item.key);
  // Navigate with filter parameters
  const path = item.filterParam
    ? `${item.targetPath}?${item.filterParam}`
    : item.targetPath;
  router.push(path);
}
</script>
