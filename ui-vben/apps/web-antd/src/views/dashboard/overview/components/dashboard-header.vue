<template>
  <div class="flex flex-wrap items-end justify-between gap-3">
    <div>
      <h1 class="text-xl font-bold text-card-foreground">综合驾驶舱</h1>
      <p class="mt-0.5 text-sm text-muted-foreground">
        合同、项目、财务及交付风险的统一监控中心
      </p>
      <p class="mt-1 text-xs text-muted-foreground">
        数据更新时间：{{ formattedTime }}
      </p>
    </div>
    <div class="flex items-center gap-2">
      <span
        class="rounded-full border border-border bg-accent px-3 py-1 text-xs text-muted-foreground"
      >
        单位：{{ unit || '万元' }}
      </span>
      <a-button :loading="loading" @click="$emit('refresh')">
        <template #icon><span class="text-base leading-none">↻</span></template>
        刷新
      </a-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';

const props = defineProps<{
  generatedAt?: string;
  unit?: string;
  loading?: boolean;
}>();

defineEmits<{ refresh: [] }>();

const formattedTime = computed(() => {
  const t = props.generatedAt;
  if (!t) return '—';
  return t.substring(0, 16).replace('T', ' ');
});
</script>
