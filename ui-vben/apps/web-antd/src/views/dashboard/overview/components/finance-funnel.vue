<template>
  <div class="rounded-lg border bg-card p-4 shadow-sm">
    <div class="mb-3 font-medium text-card-foreground">合同 → 开票 → 回款 漏斗</div>
    <div class="flex flex-col gap-3 md:flex-row md:items-stretch">
      <div
        v-for="(stage, i) in stages"
        :key="stage.name"
        class="flex-1 rounded-lg border border-border p-3"
        :class="stage.tintClass"
      >
        <div class="text-xs text-muted-foreground">{{ stage.name }}</div>
        <div class="mt-1 text-xl font-bold" :class="stage.textClass">
          {{ fmtMoney(stage.value) }}
          <span class="text-xs font-normal text-muted-foreground">万元</span>
        </div>
        <div class="mt-2 h-2 w-full rounded bg-accent">
          <div
            class="h-2 rounded"
            :style="{ width: stage.widthPct + '%', background: stage.color }"
          ></div>
        </div>
        <div v-if="i > 0" class="mt-2 text-xs text-muted-foreground">
          较上一阶段转化：{{ stage.convPct }}%
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import { fmtMoney } from '../dashboard-types';

const props = defineProps<{
  contract: number;
  invoiced: number;
  received: number;
}>();

const stages = computed(() => {
  const raw = [
    { name: '合同总额', value: props.contract, tone: 'primary' as const },
    { name: '已开票', value: props.invoiced, tone: 'invoiced' as const },
    { name: '已回款', value: props.received, tone: 'received' as const },
  ];
  const max = Math.max(1, ...raw.map((r) => r.value || 0));
  return raw.map((r, i, arr) => {
    const prev = arr[i - 1];
    const conv = prev ? ((r.value || 0) / (prev.value || 1)) * 100 : 0;
    return {
      ...r,
      widthPct: ((r.value || 0) / max) * 100,
      convPct: i > 0 ? conv.toFixed(1) : '—',
      tintClass: `dash-bg-${r.tone}`,
      textClass: `dash-text-${r.tone}`,
      color: `var(--dash-${r.tone})`,
    };
  });
});
</script>
