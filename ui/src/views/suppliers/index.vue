<template>
  <div class="p-4">
    <!-- 财务汇总卡片 -->
    <a-card class="mb-4" title="供应商财务汇总" :loading="summaryLoading">
      <a-row :gutter="16">
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">供应商总数</div>
            <div class="summary-value text-blue">{{ summary.totalSuppliers }}</div>
          </div>
        </a-col>
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">合同总额 (万元)</div>
            <div class="summary-value text-orange">{{ formatWanYuan(summary.totalContractAmount) }}</div>
          </div>
        </a-col>
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">已开票 (万元)</div>
            <div class="summary-value text-green">{{ formatWanYuan(summary.totalInvoiced) }}</div>
          </div>
        </a-col>
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">已付款 (万元)</div>
            <div class="summary-value text-green">{{ formatWanYuan(summary.totalPaid) }}</div>
          </div>
        </a-col>
      </a-row>
    </a-card>

    <!-- 供应商列表 -->
    <Grid />
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import { formatWanYuan } from '@/utils/formatAmount'
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import { getSuppliersApi, type SupplierItem } from '#/api/suppliers'

// ---- 汇总数据 ----
const summaryLoading = ref(false)
const summary = reactive({
  totalSuppliers: 0,
  totalContractAmount: 0,
  totalInvoiced: 0,
  totalPaid: 0,
})

async function loadSummary() {
  summaryLoading.value = true
  try {
    const data = await getSuppliersApi()
    const items = data.items ?? []
    let totalContract = 0
    let totalInvoiced = 0
    let totalPaid = 0
    for (const item of items) {
      totalContract += item.total_contract_amount ?? 0
      totalInvoiced += item.total_invoiced ?? 0
      totalPaid += item.total_paid ?? 0
    }
    summary.totalSuppliers = items.length
    summary.totalContractAmount = totalContract
    summary.totalInvoiced = totalInvoiced
    summary.totalPaid = totalPaid
  } finally {
    summaryLoading.value = false
  }
}

onMounted(loadSummary)

// ---- 表格配置 ----
const gridOptions: VxeGridProps<SupplierItem> = {
  columns: [
    { field: 'supplier_name', title: '供应商名称', minWidth: 250, showOverflow: true, fixed: 'left' },
    { field: 'short_name', title: '简称', width: 120 },
    { field: 'category', title: '类别', width: 100 },
    {
      field: 'total_contract_amount',
      title: '合同总额(万元)',
      width: 130,
      align: 'right',
      sortable: true,
      formatter: ({ cellValue }) => formatWanYuan(cellValue),
    },
    {
      field: 'total_invoiced',
      title: '已开票(万元)',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => formatWanYuan(cellValue),
    },
    {
      field: 'total_paid',
      title: '已付款(万元)',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => formatWanYuan(cellValue),
    },
    {
      field: 'total_unpaid',
      title: '未付款(万元)',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => formatWanYuan(cellValue),
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

<style scoped>
.summary-item {
  text-align: center;
  padding: 8px 0;
}
.summary-label {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 4px;
}
.summary-value {
  font-size: 22px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.text-blue {
  color: #1677ff;
}
.text-green {
  color: #52c41a;
}
.text-orange {
  color: #fa8c16;
}
.mb-4 {
  margin-bottom: 16px;
}
</style>
