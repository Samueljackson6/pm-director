<template>
  <div class="rounded-lg border bg-card shadow-sm">
    <div class="border-b px-4 py-3 font-medium text-card-foreground">最近合同</div>
    <VxeTable
      v-if="rows && rows.length"
      :data="rows"
      :column-config="{ minWidth: 120 }"
      :row-config="{ height: 44, isHover: true }"
      size="small"
      height="400"
    >
      <VxeColumn field="contract_id" title="合同编号" width="150" showOverflow />
      <VxeColumn field="project_name" title="项目名称" minWidth="240" showOverflow />
      <VxeColumn field="party_a" title="甲方" minWidth="160" showOverflow />
      <VxeColumn field="project_type" title="类型" width="100" />
      <VxeColumn field="contract_status" title="状态" width="100" />
      <VxeColumn field="sign_date" title="签订日期" width="110" />
      <VxeColumn
        field="contract_amount"
        title="合同额(万元)"
        width="130"
        align="right"
        :formatter="({ cellValue }) => fmt(cellValue)"
      />
      <VxeColumn
        field="invoice_total"
        title="已开票(万元)"
        width="120"
        align="right"
        :formatter="({ cellValue }) => fmt(cellValue)"
      />
      <VxeColumn
        field="payment_total"
        title="已回款(万元)"
        width="120"
        align="right"
        :formatter="({ cellValue }) => fmt(cellValue)"
      />
    </VxeTable>
    <div v-else class="py-6 text-center text-sm text-muted-foreground">
      暂无最近合同数据
    </div>
  </div>
</template>

<script lang="ts" setup>
import { VxeTable, VxeColumn } from '#/adapter/vxe-table';
import type { RecentContract } from '#/api/dashboard';
import { fmtMoney } from '../dashboard-types';

defineProps<{ rows?: RecentContract[] }>();

function fmt(v: number | null | undefined): string {
  return fmtMoney(v, 2);
}
</script>
