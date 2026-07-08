<template>
  <div class="p-4">
    <Grid>
      <template #status="{ row }">
        <a-tag :color="row.status === 'active' ? 'green' : 'default'">
          {{ row.status === 'active' ? '合作中' : '已暂停' }}
        </a-tag>
      </template>
    </Grid>
  </div>
</template>

<script lang="ts" setup>
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import { getSuppliersApi, type SupplierItem } from '#/api/suppliers'

const gridOptions: VxeGridProps<SupplierItem> = {
  columns: [
    { field: 'supplier_name', title: '供应商名称', minWidth: 250, showOverflow: true, fixed: 'left',
      cellRender: { name: 'CellRouterLink', props: { name: 'SupplierDetail', idField: 'supplier_id', field: 'supplier_name' } } },
    { field: 'short_name', title: '简称', width: 120 },
    { field: 'category', title: '类别', width: 100 },
    {
      field: 'total_contract_amount',
      title: '合同总额',
      width: 130,
      align: 'right',
      sortable: true,
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'total_invoiced',
      title: '已开票',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'total_paid',
      title: '已付款',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'total_unpaid',
      title: '未付款',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    { field: 'contract_count', title: '合同数', width: 80, align: 'right' },
    {
      field: 'status',
      title: '状态',
      width: 90,
      slots: { default: 'status' },
    },
  ],
  proxyConfig: {
    response: { result: 'items', total: 'total' },
    ajax: {
      query: async () => {
        const data = await getSuppliersApi()
        return { items: data.items ?? [], total: (data.items ?? []).length }
      },
    },
  },
  toolbarConfig: { refresh: true, zoom: true, custom: true },
  pagerConfig: { pageSize: 20, pageSizes: [10, 20, 50] },
  sortConfig: { multiple: true },
  rowConfig: { isHover: true, height: 44 },
}

const [Grid] = useVbenVxeGrid({ gridOptions })
</script>
