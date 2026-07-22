<template>
  <div class="pm-workbench-page p-4 sm:p-6">
    <header class="pm-page-header">
      <div>
        <p class="pm-section-kicker">供应链协作</p>
        <h1>供应商台账</h1>
        <p class="pm-section-note">按合作规模、付款缺口和履约关系定位需要跟进的供应商。</p>
      </div>
    </header>
    <section class="pm-table-surface" aria-label="供应商台账列表">
    <Grid>
      <template #status="{ row }">
        <a-tag v-if="row" :color="row.status === 'active' ? 'green' : 'default'">
          {{ row.status === 'active' ? '合作中' : '已暂停' }}
        </a-tag>
      </template>
    </Grid>
    </section>
  </div>
</template>

<script lang="ts" setup>
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import { getSuppliersApi, type SupplierItem } from '#/api/suppliers'
import { buildDetailLocation } from '#/utils/business-navigation'
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentPage = ref(1)
const currentPageSize = ref(20)

function supplierDetailLocation(supplierId: string) {
  return buildDetailLocation({
    from: {
      name: route.name,
      query: {
        ...route.query,
        page: String(currentPage.value),
        pageSize: String(currentPageSize.value),
      },
    },
    id: supplierId,
    name: 'SupplierDetail',
  })
}

const gridOptions: VxeGridProps<SupplierItem> = {
  columns: [
    { field: 'supplier_name', title: '供应商名称', minWidth: 250, showOverflow: true, fixed: 'left',
      cellRender: {
        name: 'CellRouterLink',
        props: {
          field: 'supplier_name',
          name: 'SupplierDetail',
          variableQuery: (row: SupplierItem) =>
            supplierDetailLocation(row.supplier_id).query,
        },
      } },
    { field: 'short_name', title: '简称', width: 120 },
    { field: 'category', title: '类别', width: 100 },
    {
      field: 'total_contract_amount',
      title: '合同总额',
      width: 130,
      align: 'right',
      sortable: true,
      formatter: ({ cellValue }) => formatWan(cellValue),
    },
    {
      field: 'total_invoiced',
      title: '已开票',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => formatWan(cellValue),
    },
    {
      field: 'total_paid',
      title: '已付款',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => formatWan(cellValue),
    },
    {
      field: 'total_unpaid',
      title: '未付款',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => formatWan(cellValue),
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
      query: async ({ page }) => {
        currentPage.value = page.currentPage
        currentPageSize.value = page.pageSize
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

function formatWan(value: number | null | undefined): string {
  if (value == null) return '-'
  return (Number(value) / 10000).toFixed(2)
}
</script>
