<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import type { ContractTypeGroup } from '#/api/dashboard';
import type { ECOption } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = withDefaults(defineProps<{ data?: ContractTypeGroup[] }>(), {
  data: () => [],
});

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function buildOption(): ECOption {
  return {
    tooltip: { trigger: 'item', valueFormatter: (value) => `${value} 万元` },
    legend: { bottom: 0, type: 'scroll' },
    series: [
      {
        name: '合同类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{d}%' },
        data: props.data.map((d) => ({
          name: d.project_type || '未分类',
          value: d.amount,
        })),
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
