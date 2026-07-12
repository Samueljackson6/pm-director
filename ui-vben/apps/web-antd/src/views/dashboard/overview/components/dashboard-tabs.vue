<template>
  <div class="flex gap-2 overflow-x-auto whitespace-nowrap pb-1">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      class="shrink-0 rounded-lg border px-4 py-2 text-sm font-medium transition-colors"
      :class="
        modelValue === tab.key
          ? 'dash-bg-primary border-primary dash-text-primary'
          : 'border-border bg-card text-muted-foreground hover:bg-accent'
      "
      @click="select(tab.key)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<script lang="ts" setup>
import type { ViewKey } from '../dashboard-types';

const props = defineProps<{ modelValue: ViewKey }>();
const emit = defineEmits<{
  'update:modelValue': [value: ViewKey];
  change: [value: ViewKey];
}>();

const tabs: Array<{ key: ViewKey; label: string }> = [
  { key: 'all', label: '全域总览' },
  { key: 'management', label: '经营管理' },
  { key: 'projects', label: '项目执行' },
  { key: 'finance', label: '财务回款' },
];

function select(key: ViewKey) {
  emit('update:modelValue', key);
  if (key !== props.modelValue) emit('change', key);
}
</script>
