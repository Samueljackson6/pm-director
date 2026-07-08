<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import type { MonthlyTrend } from '#/api/dashboard';
import type { ECOption } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = withDefaults(defineProps<{ data?: MonthlyTrend[] }>(), {
  data: () => [],
});

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function buildOption(): ECOption {
  return {
    tooltip: { trigger: 'axis', valueFormatter: (value) => `${value} 万元` },
    legend: { data: ['已开票', '已回款'], bottom: 0 },
    grid: { left: '3%', right: '3%', bottom: 50, top: 20, containLabel: true },
    xAxis: {
      type: 'category',
      data: (props.data ?? []).map((d) => d.month),
      boundaryGap: false,
      axisLabel: { rotate: 45 },
    },
    yAxis: { type: 'value', name: '万元' },
    series: [
      {
        name: '已开票',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.15 },
        itemStyle: { color: '#5ab1ef' },
        data: (props.data ?? []).map((d) => d.invoiced_wan),
      },
      {
        name: '已回款',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.15 },
        itemStyle: { color: '#019680' },
        data: (props.data ?? []).map((d) => d.received_wan),
      },
    ],
  };
}

onMounted(() => renderEcharts(buildOption()));
watch(() => props.data, () => renderEcharts(buildOption()), { deep: true });
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
