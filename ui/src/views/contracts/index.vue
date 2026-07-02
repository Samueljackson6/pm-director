<template>
  <div class="p-4">
    <Grid />
  </div>
</template>

<script lang="ts" setup>
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import { getContractsApi, type ContractItem } from '#/api/contracts'
import { useRouter } from 'vue-router'

const router = useRouter()

const gridOptions: VxeGridProps<ContractItem> = {
  columns: [
    { field: 'contract_id', title: '合同编号', width: 200, fixed: 'left' },
    { field: 'project_name', title: '项目名称', minWidth: 250, showOverflow: true },
    { field: 'project_type', title: '类型', width: 90 },
    {
      field: 'contract_amount',
      title: '金额(万元)',
      width: 130,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'invoice_total',
      title: '已开票(万元)',
      width: 130,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'payment_total',
      title: '已回款(万元)',
      width: 130,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'sign_date',
      title: '签订日期',
      width: 110,
    },
    {
      field: 'party_a',
      title: '甲方',
      minWidth: 200,
      showOverflow: true,
      formatter: ({ cellValue }) => (cellValue ?? '').replace(/[（(].*[)）]/g, '') || '-',
    },
  ],
  proxyConfig: {
    ajax: {
      query: async ({ page }) => {
        const data = await getContractsApi({
          page: page.currentPage,
          size: page.pageSize,
        })
        return { items: data.items ?? [], total: data.total ?? 0 }
      },
    },
  },
  toolbarConfig: {
    refresh: true,
    zoom: true,
    custom: true,
  },
  pagerConfig: {
    pageSize: 20,
    pageSizes: [10, 20, 50, 100],
  },
  sortConfig: { multiple: true },
  rowConfig: { isHover: true, height: 44 },
}

const [Grid, gridApi] = useVbenVxeGrid({ gridOptions })

// 双击行跳转详情
gridApi.on('cell-dblclick', ({ row }: { row: ContractItem }) => {
  router.push({ name: 'ContractDetail', params: { id: row.contract_id } })
})
</script>
