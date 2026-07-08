<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import type { ECOption } from '@vben/plugins/echarts';

import { computed, onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

interface Stage {
  stage_id?: string;
  stage_name?: string;
  start_time?: string | null;
  end_time?: string | null;
  status?: string;
  [key: string]: any;
}

const props = withDefaults(
  defineProps<{ stages?: Stage[] }>(),
  { stages: () => [] },
);

/** 状态色板（与 finance-tokens.css 的状态 token 对齐） */
const STATUS_COLOR: Record<string, string> = {
  completed: '#52c41a',
  in_progress: '#1677ff',
  pending: '#d9d9d9',
};
const STATUS_LABEL: Record<string, string> = {
  completed: '已完成',
  in_progress: '进行中',
  pending: '待开始',
};

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

/** 仅保留有排期的阶段用于甘特图 */
const dated = computed(() => {
  const list = props.stages ?? [];
  return list
    .map((s) => {
      const range = parseRange(s.start_time) ?? parseRange(s.end_time);
      return range ? { ...s, _start: range.start, _end: range.end } : null;
    })
    .filter((x): x is NonNullable<typeof x> => x !== null);
});

/**
 * 解析阶段时间。支持两种来源：
 *  1) 标准日期串（如 '2026-05-01'）— Date.parse 直接解析；
 *  2) 中文区间文本（如 '2026-05 至 2026-10'）— 提取起止年月，
 *     起始取当月 1 号，结束取下月 1 号（使条带覆盖整月）。
 */
function parseRange(d?: string | null): { start: number; end: number } | undefined {
  if (!d) return undefined;
  const plain = Date.parse(d);
  if (!Number.isNaN(plain)) return { start: plain, end: plain };
  const m = d.match(/(\d{4}-\d{2})\s*至\s*(\d{4}-\d{2})/);
  if (m) {
    const start = Date.parse(`${m[1]}-01`);
    const [ey, em] = m[2].split('-').map(Number);
    const end = new Date(ey, em, 1).getTime(); // em 为真实月份(1-12)，JS 月份 0-based → 即下月 1 号
    if (!Number.isNaN(start) && !Number.isNaN(end)) return { start, end };
  }
  return undefined;
}

function buildOption(): ECOption {
  const rows = dated.value;
  const yData = rows.map((s) => s.stage_name || '阶段');
  const data = rows.map((s, i) => [
    i,
    s._start as number,
    s._end as number,
    s.status || 'pending',
  ]);

  return {
    tooltip: {
      formatter: (p: any) => {
        const s = rows[p.dataIndex];
        return `${s.stage_name}<br/>${s.start_time} ~ ${s.end_time}<br/>状态：${STATUS_LABEL[s.status || ''] || s.status || '-'}`;
      },
    },
    grid: { left: 8, right: 16, top: 16, bottom: 30, containLabel: true },
    xAxis: {
      type: 'time',
      axisLabel: { formatter: (v: number) => new Date(v).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }) },
    },
    yAxis: {
      type: 'category',
      data: yData,
      inverse: true,
      axisTick: { show: false },
      axisLine: { show: false },
    },
    series: [
      {
        type: 'custom',
        renderItem: (params: any, api: any) => {
          const catIdx = api.value(0) as number;
          const start = api.coord([api.value(1), catIdx]);
          const end = api.coord([api.value(2), catIdx]);
          const bandHeight = api.size([0, 1])[1];
          const barHeight = Math.min(Math.max(bandHeight * 0.5, 12), 20);
          const x = start[0];
          const width = Math.max(end[0] - start[0], 3);
          const y = start[1] - barHeight / 2;
          const color = STATUS_COLOR[api.value(3)] || '#d9d9d9';
          return {
            type: 'rect',
            shape: { x, y, width, height: barHeight, r: 4 },
            style: { fill: color },
          };
        },
        encode: { x: [1, 2], y: 0 },
        data,
      },
    ],
  };
}

onMounted(() => {
  if (dated.value.length) renderEcharts(buildOption());
});
watch(
  () => props.stages,
  () => {
    if (dated.value.length) renderEcharts(buildOption());
  },
  { deep: true },
);
</script>

<template>
  <div>
    <!-- 有排期：渲染甘特图 -->
    <EchartsUI v-if="dated.length" ref="chartRef" :style="{ height: Math.max(dated.length * 44, 120) + 'px' }" />

    <!-- 无排期：降级为状态清单，避免空白 -->
    <div v-else class="space-y-2">
      <div
        v-for="s in stages"
        :key="s.stage_id"
        class="flex items-center gap-3 text-sm"
      >
        <span
          class="inline-block h-2.5 w-2.5 rounded-full"
          :style="{ background: STATUS_COLOR[s.status || 'pending'] || '#d9d9d9' }"
        />
        <span class="font-medium truncate" :title="s.stage_name">{{ s.stage_name }}</span>
        <span class="text-xs text-muted-foreground">{{ STATUS_LABEL[s.status || ''] || s.status || '-' }}</span>
        <span class="text-xs text-muted-foreground">（未排期）</span>
      </div>
      <div v-if="!stages.length" class="py-4 text-center text-sm text-muted-foreground">
        暂无阶段数据
      </div>
    </div>
  </div>
</template>
