<template>
  <div class="p-4">
    <!-- 回款汇总 -->
    <a-card class="mb-4" title="回款汇总" :loading="summaryLoading">
      <a-row :gutter="16">
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">回款总额 (万元)</div>
            <div class="summary-value text-green">{{ formatWanYuan(summary.receiptTotal) }}</div>
          </div>
        </a-col>
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">已匹配 (万元)</div>
            <div class="summary-value text-blue">{{ formatWanYuan(summary.matchedTotal) }}</div>
          </div>
        </a-col>
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">未匹配 (万元)</div>
            <div class="summary-value text-orange">{{ formatWanYuan(summary.unmatchedTotal) }}</div>
          </div>
        </a-col>
        <a-col :span="6">
          <div class="summary-item">
            <div class="summary-label">状态</div>
            <div class="summary-value">
              <a-tag :color="summary.status === 'available' ? 'green' : 'orange'">
                {{ summary.status === 'available' ? '正常' : '待验证' }}
              </a-tag>
            </div>
          </div>
        </a-col>
      </a-row>
    </a-card>

    <!-- 回款列表 -->
    <Grid />
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import { formatWanYuan } from '@/utils/formatAmount'
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import { requestClient } from '#/api/request'

interface ReceiptItem {
  receipt_id: number
  project_id: string
  receipt_date: string
  amount: number
  receipt_no?: string
  payer_name?: string
  receipt_method?: string
  status: string
  notes?: string
}

const summaryLoading = ref(false)
const summary = reactive({
  receiptTotal: 0,
  matchedTotal: 0,
  unmatchedTotal: 0,
  status: 'available',
})

async function loadSummary() {
  summaryLoading.value = true
  try {
    const data = await requestClient.get('/api/receipts', { params: { page: 1, size: 1 } })
    const s = data.data?.summary ?? {}
    summary.receiptTotal = s.receipt_total ?? 0
    summary.matchedTotal = s.matched_total ?? 0
    summary.unmatchedTotal = s.unmatched_total ?? 0
    summary.status = s.status ?? 'available'
  } catch (_) {
    /* ignore */
  } finally {
    summaryLoading.value = false
  }
}

onMounted(loadSummary)

const gridOptions: VxeGridProps<ReceiptItem> = {
  columns: [
    { field: 'receipt_date', title: '日期', width: 110, sortable: true },
    { field: 'project_id', title: '项目编号', minWidth: 200, showOverflow: true },
    {
      field: 'amount',
      title: '金额(万元)',
      width: 130,
      align: 'right',
      sortable: true,
      formatter: ({ cellValue }) => formatWanYuan(cellValue),
    },
    { field: 'receipt_no', title: '回款单号', width: 160, showOverflow: true },
    { field: 'payer_name', title: '付款方', minWidth: 200, showOverflow: true },
    { field: 'receipt_method', title: '方式', width: 100 },
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
        const data = await requestClient.get('/api/receipts', {
          params: { page: page.currentPage, size: page.pageSize },
        })
        return { items: data.data?.items ?? [], total: data.data?.total ?? 0 }
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
