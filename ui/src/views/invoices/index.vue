<template>
  <div class="p-4">
    <Grid>
      <template #invoice_type="{ row }">
        <a-tag :color="row.invoice_type === '客户回款' ? 'green' : 'blue'">
          {{ row.invoice_type === '客户回款' ? '回款' : '开票' }}
        </a-tag>
      </template>
      <template #status="{ row }">
        <a-tag v-if="row.status === '已开'" color="processing">{{ row.status }}</a-tag>
        <a-tag v-else color="default">{{ row.status }}</a-tag>
      </template>
    </Grid>
  </div>
</template>

<script lang="ts" setup>
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import { getInvoicesApi, type InvoiceItem } from '#/api/invoices'

const gridOptions: VxeGridProps<InvoiceItem> = {
  columns: [
    { field: 'invoice_date', title: '日期', width: 110, sortable: true },
    {
      field: 'invoice_type',
      title: '类型',
      width: 80,
      slots: { default: 'invoice_type' },
    },
    { field: 'project_id', title: '项目编号', minWidth: 200, showOverflow: true },
    {
      field: 'amount',
      title: '金额(万元)',
      width: 130,
      align: 'right',
      sortable: true,
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'status',
      title: '状态',
      width: 80,
      slots: { default: 'status' },
    },
    { field: 'invoice_no', title: '发票号', width: 160, showOverflow: true },
  ],
  proxyConfig: {
    response: { result: 'items', total: 'total' },
    ajax: {
      query: async ({ page }) => {
        const data = await getInvoicesApi({ page: page.currentPage, size: page.pageSize })
        return { items: data.items ?? [], total: data.total ?? 0 }
      },
    },
  },
  toolbarConfig: { refresh: true, zoom: true, custom: true },
  pagerConfig: { pageSize: 50, pageSizes: [20, 50, 100] },
  sortConfig: { multiple: true },
  rowConfig: { isHover: true, height: 44 },
}

const [Grid] = useVbenVxeGrid({ gridOptions })
</script>
