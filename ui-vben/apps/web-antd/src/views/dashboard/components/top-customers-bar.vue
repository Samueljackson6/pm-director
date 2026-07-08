<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import type { TopCustomer } from '#/api/dashboard';
import type { ECOption } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = withDefaults(defineProps<{ data?: TopCustomer[] }>(), {
  data: () => [],
});

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function buildOption(): ECOption {
  // 横向条形图：y 轴为类目（客户），按金额升序使最大值显示在最上方
  const sorted = [...(props.data ?? [])].sort(
    (a, b) => a.total_amount - b.total_amount,
  );
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value) => `${value} 万元` },
    grid: { left: '3%', right: '6%', bottom: 20, top: 20, containLabel: true },
    xAxis: { type: 'value', name: '万元' },
    yAxis: {
      type: 'category',
      data: sorted.map((d) => d.customer),
      axisLabel: { width: 150, overflow: 'truncate' },
    },
    series: [
      {
        name: '合同额',
        type: 'bar',
        itemStyle: { color: '#5ab1ef', borderRadius: [0, 4, 4, 0] },
        data: sorted.map((d) => d.total_amount),
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
