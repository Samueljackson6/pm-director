<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import type { ECOption } from '@vben/plugins/echarts';

import { computed, onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

interface TrendSeries {
  /** 系列名称（图例） */
  name: string;
  /** 取值字段 */
  valueField: string;
  /** 颜色（建议引用 finance token 对应值，保持跨页一致） */
  color: string;
}

const props = withDefaults(
  defineProps<{
    /** 数据数组 */
    data?: Record<string, any>[];
    /** x 轴取值字段 */
    xField: string;
    /** 系列定义 */
    series: TrendSeries[];
    /** x 轴标签旋转角度 */
    xRotate?: number;
    /** 图例距底部距离 */
    legendBottom?: number;
    /** y 轴单位 */
    unit?: string;
  }>(),
  {
    data: () => [],
    xRotate: 0,
    legendBottom: 0,
    unit: '万元',
  },
);

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function buildOption(): ECOption {
  return {
    tooltip: { trigger: 'axis', valueFormatter: (value) => `${value} ${props.unit}` },
    legend: { data: props.series.map((s) => s.name), bottom: props.legendBottom },
    grid: { left: '3%', right: '3%', bottom: 40 + props.legendBottom, top: 20, containLabel: true },
    xAxis: {
      type: 'category',
      data: (props.data ?? []).map((d) => d[props.xField]),
      boundaryGap: false,
      axisLabel: props.xRotate ? { rotate: props.xRotate } : undefined,
    },
    yAxis: { type: 'value', name: props.unit },
    series: props.series.map((s) => ({
      name: s.name,
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.15 },
      itemStyle: { color: s.color },
      data: (props.data ?? []).map((d) => d[s.valueField]),
    })),
  };
}

onMounted(() => renderEcharts(buildOption()));
watch(
  () => [props.data, props.series],
  () => renderEcharts(buildOption()),
  { deep: true },
);

// 供父组件在容器尺寸变化时重绘
const option = computed(() => buildOption());
defineExpose({ option });
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
