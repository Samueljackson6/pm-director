<template>
  <div class="rounded-lg border bg-card p-4 shadow-sm">
    <div class="text-sm text-muted-foreground">{{ label }}</div>
    <div class="mt-1 text-2xl font-bold" :class="valueClass">
      {{ displayValue
      }}<span class="ml-1 text-sm font-normal text-muted-foreground">{{ unit }}</span>
    </div>
    <div v-if="sub" class="mt-1 text-xs text-muted-foreground">{{ sub }}</div>
    <div v-if="ratio" class="mt-0.5 text-xs text-muted-foreground">{{ ratio }}</div>
    <div v-if="hint" class="mt-0.5 text-xs text-muted-foreground/80">{{ hint }}</div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import type { DashTone } from '../dashboard-types';

const props = withDefaults(
  defineProps<{
    label: string;
    value: number | null | undefined;
    unit?: string;
    digits?: number;
    sub?: string;
    ratio?: string;
    tone?: DashTone;
    hint?: string;
  }>(),
  { digits: 2, unit: '', tone: 'none' },
);

const valueClass = computed(() =>
  props.tone !== 'none' ? `dash-text-${props.tone}` : 'text-card-foreground',
);

const displayValue = computed(() => {
  const v = props.value;
  if (v == null || Number.isNaN(v)) return '—';
  return Number(v).toFixed(props.digits);
});
</script>
