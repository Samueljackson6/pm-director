<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import type { ECOption } from '@vben/plugins/echarts';

import { computed, onMounted, ref, watch, nextTick } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

interface Stage {
  stage_id?: string;
  stage_name?: string;
  start_time?: string | null;
  end_time?: string | null;
  status?: string;
  stage_number?: number;
  acceptance_criteria?: string | null;
  remarks?: string | null;
  [key: string]: any;
}

interface Deliverable {
  deliverable_id?: string;
  deliverable_name?: string;
  deliverable_type?: string;
  planned_date?: string | null;
  status?: string;
  [key: string]: any;
}

const props = withDefaults(
  defineProps<{ stages?: Stage[]; deliverables?: Deliverable[] }>(),
  { stages: () => [], deliverables: () => [] },
);

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

const DELIVERABLE_COLOR: Record<string, string> = {
  '报告': '#722ed1',
  '软件': '#13c2c2',
  '专利': '#eb2f96',
  '样机': '#fa8c16',
  '论文': '#2f54eb',
  '系统': '#13c2c2',
  '模型': '#13c2c2',
  '装备': '#fa8c16',
  '其他': '#8c8c8c',
};

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const ganttFailed = ref(false);
const errorMsg = ref('');

function parseIsoDate(d?: string | null): number | null {
  if (!d) return null;
  const cleaned = String(d).replace(/(\d)\s+(?=\d)/g, '$1');
  const plain = Date.parse(cleaned);
  if (!Number.isNaN(plain)) return plain;
  let m = cleaned.match(/^(\d{4}-\d{2})$/);
  if (m) { const t = Date.parse(`${m[1]!}-01`); if (!Number.isNaN(t)) return t; }
  m = cleaned.match(/(\d{4})年(\d{1,2})月(\d{1,2})日?/);
  if (m) { const t = new Date(+m[1]!, +m[2]! - 1, +m[3]!).getTime(); if (!Number.isNaN(t)) return t; }
  m = cleaned.match(/(\d{4})年(\d{1,2})月/);
  if (m) { const t = new Date(+m[1]!, +m[2]! - 1, 1).getTime(); if (!Number.isNaN(t)) return t; }
  return null;
}

function parseCriteria(criteria?: string | null): string[] {
  if (!criteria) return [];
  const listMatch = criteria.match(/^\s*\[(.*)\]\s*$/s);
  if (listMatch) {
    const inner = listMatch[1] || '';
    const items = inner.split(/['"],\s*['"]/).map((s) => s.replace(/^['"]|['"]$/g, '').trim()).filter(Boolean);
    if (items.length) return items;
  }
  return [criteria.trim()];
}

function stageLabel(s: Stage): string {
  const name = s.stage_name || '';
  return name.length > 0 ? name : `阶段${s.stage_number || ''}`;
}

const dated = computed(() => {
  return (props.stages ?? [])
    .map((s) => {
      const startTs = parseIsoDate(s.start_time);
      const endTs = parseIsoDate(s.end_time);
      if (startTs === null && endTs === null) return null;
      const _start = startTs ?? endTs! - 30 * 86400000;
      let _end = endTs ?? _start;
      if (_end < _start) _end = _start;
      if (_end - _start < 2 * 86400000) _end = _start + 60 * 86400000;
      return { ...s, _start, _end };
    })
    .filter((x): x is NonNullable<typeof x> => x !== null);
});

const deliverableMarks = computed(() => {
  return (props.deliverables ?? [])
    .map((d) => {
      const t = d.planned_date ? Date.parse(d.planned_date) : NaN;
      return Number.isNaN(t) ? null : { ...d, _time: t };
    })
    .filter((x): x is NonNullable<typeof x> => x !== null);
});

function renderGantt() {
  const rows = dated.value;
  if (!rows.length) return;
  ganttFailed.value = false;
  errorMsg.value = '';

  const now = Date.now();
  const allStarts = rows.map((r) => r._start);
  const allEnds = rows.map((r) => r._end);
  const minTime = Math.min(...allStarts) - 15 * 86400000;
  const maxTime = Math.max(...allEnds, now) + 15 * 86400000;
  const yLabels = rows.map((s) => stageLabel(s));

  // 阶段条数据：[yCategoryIndex(0), startTime(1), endTime(2), status(3), rowIndex(4)]
  const stageData: Array<[number, number, number, string, number]> = rows.map((s, i) => [
    i, s._start, s._end, s.status || 'pending', i,
  ]);

  // 交付物数据
  const deliverableData: Array<[number, number, string, string]> = deliverableMarks.value.map((d) => {
    return [rows.length, d._time, d.deliverable_name || '未命名', d.deliverable_type || '其他'];
  });

  const opt: ECOption = {
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => {
        if (p.seriesName === '今日') return `<b>今日</b><br/>${new Date(now).toLocaleDateString('zh-CN')}`;
        const s = rows[p.dataIndex];
        if (!s) return '';
        const criteria = parseCriteria(s.acceptance_criteria);
        const cHtml = criteria.length
          ? '<br/><span style="color:#8c8c8c">验收：</span>' + criteria.map(c => '&bull; ' + c).join('<br/>&nbsp;&nbsp;')
          : '';
        const dNames = (props.deliverables ?? []).filter(d => d.deliverable_name).map(d => d.deliverable_name);
        const dHtml = dNames.length ? '<br/><span style="color:#8c8c8c">交付物：</span>' + dNames.join(', ') : '';
        return `<b>${stageLabel(s)}</b><br/>${s.start_time || '?'} ~ ${s.end_time || '?'}<br/>状态：${STATUS_LABEL[s.status || ''] || s.status || '-'}${cHtml}${dHtml}`;
      },
    },
    legend: {
      bottom: 0,
      data: ['已完成', '进行中', '待开始', ...(deliverableData.length ? ['交付物'] : [])],
      textStyle: { fontSize: 11 },
    },
    grid: { left: 160, right: 40, top: 20, bottom: 60 },
    xAxis: {
      type: 'time',
      min: minTime,
      max: maxTime,
      axisLabel: {
        formatter: (v: number) => {
          const d = new Date(v);
          return `${d.getFullYear()}/${(d.getMonth() + 1).toString().padStart(2, '0')}`;
        },
        fontSize: 11,
      },
      splitLine: { show: true, lineStyle: { type: 'dashed', color: '#f0f0f0' } },
    },
    yAxis: {
      type: 'category',
      data: yLabels,
      inverse: true,
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: { fontSize: 11, overflow: 'truncate', width: 150 },
    },
    series: [] as any[],
  };

  // ── 阶段条：用自定义 series ──
  // ★ 核心修复：api.coord 第二个参数用类别标签字符串而非数字索引
  opt.series.push({
    name: '阶段',
    type: 'custom',
    renderItem: (_params: any, api: any) => {
      try {
        const catIdx = api.value(0) as number;
        const startTs = api.value(1) as number;
        const endTs = api.value(2) as number;

        // ★ 关键：取类别标签字符串
        const catLabel = yLabels[catIdx] || yLabels[0];

        // 用类别标签计算坐标
        const startPx = api.coord([startTs, catLabel]);
        const endPx = api.coord([endTs, catLabel]);

        // 手动计算 bandHeight（防御性计算）
        const topPx = api.coord([startTs, catLabel]);
        let bandHeight = 40; // 默认高度
        if (catIdx < yLabels.length - 1) {
          const next = yLabels[catIdx + 1];
          const bottomPx = api.coord([startTs, next]);
          bandHeight = Math.abs((bottomPx?.[1] ?? 100) - (topPx?.[1] ?? 0));
        }
        bandHeight = Math.max(bandHeight, 24); // 确保最小高度

        const barHeight = Math.min(Math.max(bandHeight * 0.6, 16), 28);
        const x = (startPx?.[0] ?? 0);
        const width = Math.max((endPx?.[0] ?? 100) - x, 4);
        const y = (startPx?.[1] ?? 0) - barHeight / 2;
        const color = STATUS_COLOR[api.value(3)] || '#d9d9d9';

        return {
          type: 'group',
          children: [
            { type: 'rect', shape: { x, y, width, height: barHeight, r: 4 }, style: { fill: color, opacity: 0.85 } },
            ...(width > 60 ? [{
              type: 'text',
              style: {
                text: catLabel, x: x + 6, y: y + barHeight / 2,
                textVerticalAlign: 'middle', textAlign: 'left', fill: '#fff',
                font: 'bold 10px sans-serif, "Microsoft YaHei"',
              },
            }] : []),
          ],
        };
      } catch (e: any) {
        // renderItem 失败时返回空
        return { type: 'group', children: [], silent: true };
      }
    },
    encode: { x: [1, 2], y: 0 },
    data: stageData,
    z: 10,
  });

  // ── 今日标记线 ──
  opt.series.push({
    name: '今日',
    type: 'custom',
    renderItem: (_params: any, api: any) => {
      try {
        const firstLabel = yLabels[0];
        const lastLabel = yLabels[yLabels.length - 1];
        const topPx = api.coord([now, firstLabel]);
        const bottomPx = api.coord([now, lastLabel]);
        return {
          type: 'line',
          shape: {
            x1: topPx[0], y1: topPx[1] - 20,
            x2: topPx[0], y2: (bottomPx?.[1] ?? topPx[1]) + 20,
          },
          style: { stroke: '#ff4d4f', lineWidth: 1.5, lineDash: [4, 3] },
          silent: true,
        };
      } catch { return { type: 'group', children: [], silent: true }; }
    },
    data: [[0]],
    z: 100,
  });

  nextTick(() => {
    try {
      renderEcharts(opt);
      ganttFailed.value = false;
    } catch (e: any) {
      console.error('甘特图渲染失败', e);
      ganttFailed.value = true;
      errorMsg.value = e?.message || '渲染异常';
    }
  });
}

onMounted(renderGantt);
watch(
  () => [props.stages, props.deliverables],
  renderGantt,
  { deep: true },
);
</script>

<template>
  <div>
    <!-- 甘特图 ECharts -->
    <EchartsUI
      v-if="dated.length && !ganttFailed"
      ref="chartRef"
      :style="{ height: Math.max(dated.length * 48 + 80, 180) + 'px', width: '100%' }"
    />
    <div v-if="dated.length && !ganttFailed" class="flex items-center gap-4 mt-2 text-xs text-gray-400">
      <span>● 已完成</span><span>● 进行中</span><span>● 待开始</span><span class="text-red-400">--- 今日</span>
    </div>

    <!-- 降级清单 -->
    <div v-if="ganttFailed || (!dated.length && stages.length)" class="space-y-1">
      <div v-for="s in stages" :key="s.stage_id" class="flex items-center gap-3 text-sm py-1.5">
        <span class="inline-block h-2.5 w-2.5 rounded-full shrink-0" :style="{ background: STATUS_COLOR[s.status || 'pending'] || '#d9d9d9' }" />
        <span class="font-medium truncate" :title="s.stage_name">{{ stageLabel(s) }}</span>
        <span class="text-xs text-muted-foreground shrink-0">{{ STATUS_LABEL[s.status || ''] || s.status || '-' }}</span>
        <span v-if="s.start_time" class="text-xs text-muted-foreground shrink-0">
          {{ s.start_time }}{{ s.end_time ? ' ~ ' + s.end_time : '' }}
        </span>
        <span v-else class="text-xs text-muted-foreground shrink-0">（未排期）</span>
      </div>
    </div>
    <div v-if="!stages.length" class="py-4 text-center text-sm text-muted-foreground">暂无阶段数据</div>

    <!-- 交付物清单 -->
    <div v-if="deliverables.length" class="mt-4 pt-3 border-t border-dashed border-gray-200">
      <div class="text-xs font-medium text-gray-500 mb-2">本合同交付物</div>
      <div class="flex flex-wrap gap-2">
        <span v-for="dl in deliverables" :key="dl.deliverable_id || dl.deliverable_name"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs"
          :style="{
            background: (DELIVERABLE_COLOR[dl.deliverable_type || '其他'] || '#8c8c8c') + '20',
            color: DELIVERABLE_COLOR[dl.deliverable_type || '其他'] || '#8c8c8c',
          }">
          <span class="w-1.5 h-1.5 rounded-full shrink-0" :style="{ background: DELIVERABLE_COLOR[dl.deliverable_type || '其他'] || '#8c8c8c' }" />
          {{ dl.deliverable_name }}
          <span v-if="dl.deliverable_type" class="opacity-60">({{ dl.deliverable_type }})</span>
        </span>
      </div>
    </div>
  </div>
</template>
