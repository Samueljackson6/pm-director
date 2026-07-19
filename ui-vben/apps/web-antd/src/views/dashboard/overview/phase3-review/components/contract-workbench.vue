<script lang="ts" setup>
import type { ReviewContract } from '../review-data';

import type { VxeGridListeners, VxeGridProps } from '#/adapter/vxe-table';

import { useVbenVxeGrid } from '#/adapter/vxe-table';

import { reviewContracts } from '../review-data';

const emit = defineEmits<{
  openDetail: [contract: ReviewContract];
}>();

const gridOptions: VxeGridProps<ReviewContract> = {
  border: false,
  columns: [
    {
      field: 'rowKey',
      fixed: 'left',
      title: '内部编号',
      width: 190,
      formatter: ({ row }) => row.contractId.value,
    },
    {
      field: 'stateGridId',
      title: '国网编号',
      width: 190,
    },
    {
      field: 'projectName',
      minWidth: 260,
      showOverflow: true,
      title: '合同/项目名称',
    },
    {
      field: 'legalForm',
      title: '交易形式',
      width: 130,
    },
    {
      field: 'deliveryType',
      title: '执行形态',
      width: 100,
    },
    {
      field: 'amountLabel',
      title: '金额口径',
      width: 140,
    },
    {
      field: 'paymentPattern',
      minWidth: 260,
      showOverflow: true,
      title: '付款条件',
    },
  ],
  data: reviewContracts.map((contract) => contract),
  height: 286,
  pagerConfig: {
    enabled: false,
  },
  rowConfig: {
    height: 52,
    isCurrent: true,
    isHover: true,
    keyField: 'rowKey',
  },
  showOverflow: true,
  toolbarConfig: {
    custom: true,
    refresh: false,
    zoom: true,
  },
};

const gridEvents: VxeGridListeners<ReviewContract> = {
  cellClick({ row }) {
    emit('openDetail', row);
  },
};

const [Grid] = useVbenVxeGrid({
  gridEvents,
  gridOptions,
  tableTitle: '脱敏合同评审样例',
});
</script>

<template>
  <section class="review-panel review-panel--table">
    <div class="review-panel__heading">
      <div>
        <span class="review-eyebrow">VBEN VXEGRID · 只读</span>
        <h2>合同档案工作台</h2>
        <p>一行同时展示内部编号、国网编号、双轴类型、付款条件与核验口径。</p>
      </div>
      <a-tag color="cyan">点击任意行查看详情</a-tag>
    </div>
    <Grid />
  </section>
</template>
