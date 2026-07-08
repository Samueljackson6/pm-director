<template>
  <div class="p-4">
    <!-- 财务汇总卡片 -->
    <a-card class="mb-4" title="财务汇总" :loading="summaryLoading">
      <a-row :gutter="16">
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">累计开票 (万元)</div>
            <div class="summary-value text-blue">{{ summary.totalInvoiced.toFixed(2) }}</div>
          </div>
        </a-col>
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">累计回款 (万元)</div>
            <div class="summary-value text-green">{{ summary.totalReceived.toFixed(2) }}</div>
          </div>
        </a-col>
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">回款率</div>
            <div class="summary-value" :class="summary.receiptRateClass">
              {{ summary.receiptRate }}
            </div>
          </div>
        </a-col>
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">未开票金额 (万元)</div>
            <div class="summary-value text-orange">{{ summary.pendingAmount.toFixed(2) }}</div>
          </div>
        </a-col>
      </a-row>
    </a-card>

    <!-- 双标签切换：客户发票 / 供应商发票 -->
    <a-tabs v-model:activeKey="activeTab">
      <a-tab-pane key="outbound" tab="客户发票">
        <OutboundGrid v-if="activeTab === 'outbound'">
          <template #outbound_type="{ row }">
            <a-tag :color="row.invoice_type === '客户回款' ? 'green' : 'blue'">
              {{ row.invoice_type === '客户回款' ? '回款' : '开票' }}
            </a-tag>
          </template>
          <template #status="{ row }">
            <a-tag v-if="row.status === '已开'" color="processing">{{ row.status }}</a-tag>
            <a-tag v-else color="default">{{ row.status }}</a-tag>
          </template>
        </OutboundGrid>
      </a-tab-pane>
      <a-tab-pane key="inbound" tab="供应商发票">
        <InboundGrid v-if="activeTab === 'inbound'">
          <template #status="{ row }">
            <a-tag v-if="row.status === '已开'" color="processing">{{ row.status }}</a-tag>
            <a-tag v-else color="default">{{ row.status }}</a-tag>
          </template>
        </InboundGrid>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import { useRouter } from 'vue-router'
import {
  getInvoicesApi,
  getInvoiceSummaryApi,
  type InvoiceItem,
} from '#/api/invoices'

// 当前激活的 tab
const activeTab = ref('outbound')

// ---- 汇总数据 ----
const summaryLoading = ref(false)
const summary = reactive({
  totalInvoiced: 0,
  totalReceived: 0,
  receiptRate: '0%',
  receiptRateClass: 'text-green',
  pendingAmount: 0,
})

async function loadSummary() {
  summaryLoading.value = true
  try {
    const data = await getInvoiceSummaryApi()
    const items = data.items ?? []
    let totalInvoiced = 0
    let totalReceived = 0
    let totalContract = 0
    for (const item of items) {
      totalInvoiced += item.invoiced ?? 0
      totalReceived += item.received ?? 0
      totalContract += item.contract_amount ?? 0
    }
    const totalPending = Math.max(0, totalContract - totalInvoiced)
    const rate = totalInvoiced > 0 ? (totalReceived / totalInvoiced) * 100 : 0
    summary.totalInvoiced = totalInvoiced
    summary.totalReceived = totalReceived
    summary.receiptRate = rate.toFixed(1) + '%'
    summary.receiptRateClass =
      rate >= 80 ? 'text-green' : rate >= 50 ? 'text-orange' : 'text-red'
    summary.pendingAmount = totalPending
  } finally {
    summaryLoading.value = false
  }
}

onMounted(loadSummary)

// ---- 出站表格：客户发票 ----
const outboundGridOptions: VxeGridProps<InvoiceItem> = {
  columns: [
    { field: 'invoice_date', title: '日期', width: 110, sortable: true },
    {
      field: 'invoice_type',
      title: '类型',
      width: 90,
      slots: { default: 'outbound_type' },
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
      field: 'tax_rate',
      title: '税率',
      width: 80,
      align: 'right',
      formatter: ({ cellValue }) => {
        if (cellValue == null) return '-'
        const pct = cellValue <= 1 ? cellValue * 100 : cellValue
        return pct.toFixed(0) + '%'
      },
    },
    {
      field: 'tax_amount',
      title: '税额(万元)',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'status',
      title: '状态',
      width: 80,
      slots: { default: 'status' },
    },
    { field: 'invoice_no', title: '发票号', width: 160, showOverflow: true,
      cellRender: { name: 'CellRouterLink', props: { name: 'InvoiceDetail', idField: 'invoice_id', field: 'invoice_no' } } },
  ],
  proxyConfig: {
    response: { result: 'items', total: 'total' },
    ajax: {
      query: async ({ page }) => {
        const data = await getInvoicesApi({
          page: page.currentPage,
          size: page.pageSize,
          direction: 'outbound',
        })
        return { items: data.items ?? [], total: data.total ?? 0 }
      },
    },
  },
  toolbarConfig: { refresh: true, zoom: true, custom: true },
  pagerConfig: { pageSize: 50, pageSizes: [20, 50, 100] },
  sortConfig: { multiple: true },
  rowConfig: { isHover: true, height: 44 },
}

// ---- 入站表格：供应商发票 ----
const inboundGridOptions: VxeGridProps<InvoiceItem> = {
  columns: [
    { field: 'invoice_date', title: '日期', width: 110, sortable: true },
    {
      field: 'supplier_name',
      title: '供应商',
      minWidth: 160,
      showOverflow: true,
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
      field: 'tax_rate',
      title: '税率',
      width: 80,
      align: 'right',
      formatter: ({ cellValue }) => {
        if (cellValue == null) return '-'
        const pct = cellValue <= 1 ? cellValue * 100 : cellValue
        return pct.toFixed(0) + '%'
      },
    },
    {
      field: 'tax_amount',
      title: '税额(万元)',
      width: 120,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'status',
      title: '状态',
      width: 80,
      slots: { default: 'status' },
    },
    { field: 'invoice_no', title: '发票号', width: 160, showOverflow: true,
      cellRender: { name: 'CellRouterLink', props: { name: 'InvoiceDetail', idField: 'invoice_id', field: 'invoice_no' } } },
  ],
  proxyConfig: {
    response: { result: 'items', total: 'total' },
    ajax: {
      query: async ({ page }) => {
        const data = await getInvoicesApi({
          page: page.currentPage,
          size: page.pageSize,
          direction: 'inbound',
        })
        return { items: data.items ?? [], total: data.total ?? 0 }
      },
    },
  },
  toolbarConfig: { refresh: true, zoom: true, custom: true },
  pagerConfig: { pageSize: 50, pageSizes: [20, 50, 100] },
  sortConfig: { multiple: true },
  rowConfig: { isHover: true, height: 44 },
}

const router = useRouter()

function navigateInvoice(row: any) {
  if (row?.invoice_id != null) {
    router.push({ name: 'InvoiceDetail', query: { id: row.invoice_id } })
  }
}

const [OutboundGrid] = useVbenVxeGrid({
  gridOptions: outboundGridOptions,
  gridEvents: {
    cellClick({ row }: any) {
      navigateInvoice(row)
    },
  },
})
const [InboundGrid] = useVbenVxeGrid({
  gridOptions: inboundGridOptions,
  gridEvents: {
    cellClick({ row }: any) {
      navigateInvoice(row)
    },
  },
})
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
.text-red {
  color: #ff4d4f;
}
.mb-4 {
  margin-bottom: 16px;
}
</style>
