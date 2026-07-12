<template>
  <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
    <div
      v-for="item in items"
      :key="item.key"
      class="cursor-pointer rounded-lg border border-border p-3 shadow-sm transition-colors hover:bg-accent"
      :class="`dash-bg-${item.tone}`"
      @click="$emit('navigate', item.key)"
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
import type { PendingTasks } from '#/api/dashboard';

const props = defineProps<{ tasks: PendingTasks }>();
defineEmits<{ navigate: [key: string] }>();

const items = computed(() => [
  {
    key: 'unmatched_payments',
    label: '待匹配回款',
    tone: 'danger' as const,
    count: props.tasks?.unmatched_payments ?? 0,
  },
  {
    key: 'pending_deliverables',
    label: '待交付成果',
    tone: 'warning' as const,
    count: props.tasks?.pending_deliverables ?? 0,
  },
  {
    key: 'overdue_payments',
    label: '逾期付款',
    tone: 'danger' as const,
    count: props.tasks?.overdue_payments ?? 0,
  },
  {
    key: 'uninvoiced_contracts',
    label: '未开票合同',
    tone: 'warning' as const,
    count: props.tasks?.uninvoiced_contracts ?? 0,
  },
]);
</script>
