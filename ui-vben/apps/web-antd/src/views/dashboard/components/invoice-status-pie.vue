<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import type { InvoiceStatusGroup } from '#/api/dashboard';
import type { ECOption } from '@vben/plugins/echarts';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = withDefaults(defineProps<{ data?: InvoiceStatusGroup[] }>(), {
  data: () => [],
});

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

const COLORS: Record<string, string> = {
  '已开': '#5ab1ef',
  '已回款': '#019680',
};

function buildOption(): ECOption {
  return {
    tooltip: { trigger: 'item', valueFormatter: (value) => `${value} 万元` },
    legend: { bottom: 0, type: 'scroll' },
    series: [
      {
        name: '发票状态',
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{d}%' },
        data: (props.data ?? []).map((d) => ({
          name: d.status,
          value: d.amount_wan,
          itemStyle: { color: COLORS[d.status] ?? '#c0c4cc' },
        })),
      },
    ] as any[],
  };
}

onMounted(() => renderEcharts(buildOption()));
watch(() => props.data, () => renderEcharts(buildOption()), { deep: true });
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
