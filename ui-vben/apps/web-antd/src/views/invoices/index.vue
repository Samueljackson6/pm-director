<template>
  <div class="p-6 bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <!-- 页面标题和操作按钮 -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">发票管理</h1>
        <p class="text-sm text-gray-500 mt-1">管理客户发票和供应商发票</p>
      </div>
      <a-button type="primary" size="large" @click="openAddInvoice(activeTab)">
        <template #icon><span class="text-lg">+</span></template>
        新增发票
      </a-button>
    </div>

    <!-- 财务汇总卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-xs text-gray-400 mb-1">累计开票</div>
            <div class="text-2xl font-bold text-gray-900">{{ summary.totalInvoiced.toFixed(2) }}</div>
            <div class="text-xs text-gray-400 mt-1">万元</div>
          </div>
          <div class="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center">
            <span class="text-2xl">📄</span>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-xs text-gray-400 mb-1">累计回款</div>
            <div class="text-2xl font-bold text-green-600">{{ summary.totalReceived.toFixed(2) }}</div>
            <div class="text-xs text-gray-400 mt-1">万元</div>
          </div>
          <div class="w-12 h-12 rounded-full bg-green-50 flex items-center justify-center">
            <span class="text-2xl">💰</span>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-xs text-gray-400 mb-1">回款率</div>
            <div class="text-2xl font-bold" :class="summary.receiptRateClass">{{ summary.receiptRate }}</div>
          </div>
          <div class="w-12 h-12 rounded-full bg-purple-50 flex items-center justify-center">
            <span class="text-2xl">📊</span>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-xs text-gray-400 mb-1">未开票金额</div>
            <div class="text-2xl font-bold text-orange-600">{{ summary.pendingAmount.toFixed(2) }}</div>
            <div class="text-xs text-gray-400 mt-1">万元</div>
          </div>
          <div class="w-12 h-12 rounded-full bg-orange-50 flex items-center justify-center">
            <span class="text-2xl">⏳</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 发票列表卡片 -->
    <a-card class="rounded-xl shadow-sm" :body-style="{ padding: '0' }">
      <a-tabs v-model:activeKey="activeTab" class="invoice-tabs">
        <a-tab-pane key="outbound">
          <template #tab>
            <span class="flex items-center gap-2">
              <span class="text-lg">📤</span>
              客户发票
              <a-badge :count="outboundCount" :number-style="{ backgroundColor: '#1677ff' }" />
            </span>
          </template>
          <OutboundGrid v-if="activeTab === 'outbound'">
            <template #outbound_type="{ row }">
              <a-tag :color="row.invoice_type === '客户回款' ? 'green' : 'blue'" class="rounded-full">
                {{ row.invoice_type === '客户回款' ? '回款' : '开票' }}
              </a-tag>
            </template>
            <template #status="{ row }">
              <a-tag v-if="row.status === '已开'" color="processing" class="rounded-full">{{ row.status }}</a-tag>
              <a-tag v-else-if="row.status === '已回款'" color="success" class="rounded-full">{{ row.status }}</a-tag>
              <a-tag v-else color="default" class="rounded-full">{{ row.status }}</a-tag>
            </template>
          </OutboundGrid>
        </a-tab-pane>
        <a-tab-pane key="inbound">
          <template #tab>
            <span class="flex items-center gap-2">
              <span class="text-lg">📥</span>
              供应商发票
              <a-badge :count="inboundCount" :number-style="{ backgroundColor: '#52c41a' }" />
            </span>
          </template>
          <InboundGrid v-if="activeTab === 'inbound'">
            <template #status="{ row }">
              <a-tag v-if="row.status === '已开'" color="processing" class="rounded-full">{{ row.status }}</a-tag>
              <a-tag v-else-if="row.status === '已付款'" color="success" class="rounded-full">{{ row.status }}</a-tag>
              <a-tag v-else color="default" class="rounded-full">{{ row.status }}</a-tag>
            </template>
          </InboundGrid>
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <!-- 添加发票弹窗 -->
    <a-modal
      v-model:open="addInvoiceVisible"
      :title="(invoiceForm.direction === 'outbound' ? '新增客户发票' : '新增供应商发票')"
      :confirm-loading="invoiceSaving"
      @ok="saveInvoice"
      ok-text="保存"
      cancel-text="取消"
      width="700px"
      :body-style="{ padding: '24px' }"
    >
      <a-form :model="invoiceForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="项目编号" required>
              <a-input v-model:value="invoiceForm.project_id" placeholder="如：ZH02-202601001" size="large" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="发票号">
              <a-input v-model:value="invoiceForm.invoice_no" placeholder="可选，如：INV-2026-001" size="large" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="发票日期" required>
              <a-date-picker v-model:value="invoiceForm.invoice_date" value-format="YYYY-MM-DD" class="w-full" size="large" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="发票类型" required>
              <a-select v-model:value="invoiceForm.invoice_type" size="large">
                <a-select-option v-if="invoiceForm.direction === 'outbound'" value="客户开票">客户开票</a-select-option>
                <a-select-option v-if="invoiceForm.direction === 'outbound'" value="客户回款">客户回款</a-select-option>
                <a-select-option v-if="invoiceForm.direction === 'inbound'" value="供应商开票">供应商开票</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="金额（元）" required>
              <a-input-number v-model:value="invoiceForm.amount" :precision="2" :min="0" class="w-full" placeholder="发票金额（元）" size="large" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="税率（%）">
              <a-input-number v-model:value="invoiceForm.tax_rate" :precision="2" :min="0" :max="100" class="w-full" placeholder="如：6" size="large" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态">
              <a-select v-model:value="invoiceForm.status" size="large">
                <a-select-option value="已开">已开</a-select-option>
                <a-select-option value="已回款">已回款</a-select-option>
                <a-select-option value="待开">待开</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="回款日期">
              <a-date-picker v-model:value="invoiceForm.received_date" value-format="YYYY-MM-DD" class="w-full" size="large" />
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="备注">
              <a-textarea v-model:value="invoiceForm.notes" :rows="3" placeholder="补充说明..." />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import {
  getInvoicesApi,
  getInvoiceSummaryApi,
  createInvoiceApi,
  type InvoiceItem,
} from '#/api/invoices'
import { message } from 'ant-design-vue'

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

// 统计数量
const outboundCount = ref(0)
const inboundCount = ref(0)

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
      rate >= 80 ? 'text-green-600' : rate >= 50 ? 'text-orange-600' : 'text-red-600'
    summary.pendingAmount = totalPending
  } finally {
    summaryLoading.value = false
  }
}

onMounted(loadSummary)

// ---- 新增发票弹窗 ----
const addInvoiceVisible = ref(false)
const invoiceSaving = ref(false)
const invoiceForm = ref<Record<string, any>>({})

function openAddInvoice(direction: string) {
  invoiceForm.value = {
    project_id: '',
    invoice_no: '',
    invoice_date: '',
    invoice_type: direction === 'outbound' ? '客户开票' : '供应商开票',
    direction: direction,
    amount: null,
    tax_rate: null,
    status: '已开',
    received_date: '',
    notes: '',
  }
  addInvoiceVisible.value = true
}

async function saveInvoice() {
  if (!invoiceForm.value.project_id) {
    message.error('请输入项目编号')
    return
  }
  if (!invoiceForm.value.invoice_date) {
    message.error('请选择发票日期')
    return
  }
  if (!invoiceForm.value.amount) {
    message.error('请输入金额')
    return
  }

  invoiceSaving.value = true
  try {
    await createInvoiceApi(invoiceForm.value)
    message.success('发票创建成功')
    addInvoiceVisible.value = false
    // 刷新列表
    loadSummary()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.message || '未知错误'))
  } finally {
    invoiceSaving.value = false
  }
}

// ---- 出站表格：客户发票 ----
const outboundGridOptions: VxeGridProps<InvoiceItem> = {
  columns: [
    { field: 'invoice_date', title: '日期', width: 120, sortable: true },
    {
      field: 'invoice_type',
      title: '类型',
      width: 100,
      slots: { default: 'outbound_type' },
    },
    { field: 'project_id', title: '项目编号', minWidth: 220, showOverflow: true,
      cellRender: { name: 'CellRouterLink', props: { name: 'CustomerInvoiceDetail', idField: 'invoice_id', field: 'project_id' } } },
    {
      field: 'amount',
      title: '金额(万元)',
      width: 140,
      align: 'right',
      sortable: true,
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'tax_rate',
      title: '税率',
      width: 90,
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
      width: 130,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'status',
      title: '状态',
      width: 100,
      slots: { default: 'status' },
    },
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
        outboundCount.value = data.total ?? 0
        return { items: data.items ?? [], total: data.total ?? 0 }
      },
    },
  },
  toolbarConfig: { refresh: true, zoom: true, custom: true },
  pagerConfig: { pageSize: 50, pageSizes: [20, 50, 100] },
  sortConfig: { multiple: true },
  rowConfig: { isHover: true, height: 48 },
}

// ---- 入站表格：供应商发票 ----
const inboundGridOptions: VxeGridProps<InvoiceItem> = {
  columns: [
    { field: 'invoice_date', title: '日期', width: 120, sortable: true },
    {
      field: 'supplier_name',
      title: '供应商',
      minWidth: 180,
      showOverflow: true,
    },
    { field: 'project_id', title: '项目编号', minWidth: 220, showOverflow: true,
      cellRender: { name: 'CellRouterLink', props: { name: 'CustomerInvoiceDetail', idField: 'invoice_id', field: 'project_id' } } },
    {
      field: 'amount',
      title: '金额(万元)',
      width: 140,
      align: 'right',
      sortable: true,
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'tax_rate',
      title: '税率',
      width: 90,
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
      width: 130,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'status',
      title: '状态',
      width: 100,
      slots: { default: 'status' },
    },
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
        inboundCount.value = data.total ?? 0
        return { items: data.items ?? [], total: data.total ?? 0 }
      },
    },
  },
  toolbarConfig: { refresh: true, zoom: true, custom: true },
  pagerConfig: { pageSize: 50, pageSizes: [20, 50, 100] },
  sortConfig: { multiple: true },
  rowConfig: { isHover: true, height: 48 },
}

const [OutboundGrid] = useVbenVxeGrid({ gridOptions: outboundGridOptions })
const [InboundGrid] = useVbenVxeGrid({ gridOptions: inboundGridOptions })
</script>

<style scoped>
.w-full {
  width: 100%;
}

.invoice-tabs :deep(.ant-tabs-nav) {
  margin: 0;
  padding: 0 24px;
  background: #fafafa;
}

.invoice-tabs :deep(.ant-tabs-tab) {
  padding: 16px 0;
  font-size: 15px;
  font-weight: 500;
}

.invoice-tabs :deep(.ant-tabs-content) {
  padding: 16px 24px 24px;
}
</style>
