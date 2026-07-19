<template>
  <div class="min-h-screen overflow-x-hidden bg-slate-50 px-4 py-4 md:px-6">
    <!-- 页面标题 -->
    <div class="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">客户回款</h1>
        <p class="text-sm text-gray-500 mt-1">管理客户的付款记录</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <a-button size="large" @click="autoMatch">
          <template #icon><span>??</span></template>自动匹配（写入关联）
        </a-button>
        <a-button type="primary" size="large" @click="openAddReceipt">
          <template #icon><span>+</span></template>新增回款
        </a-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="text-xs text-gray-400">累计回款（万元）</div>
        <div class="text-2xl font-bold text-green-600 mt-1">{{ formatSummaryAmount(receiptSummary.receipt_total) }}</div>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="text-xs text-gray-400">已匹配（万元）</div>
        <div class="text-2xl font-bold text-blue-600 mt-1">{{ formatSummaryAmount(receiptSummary.matched_total) }}</div>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div class="text-xs text-gray-400">未匹配（万元）</div>
        <div class="text-2xl font-bold text-orange-600 mt-1">{{ formatSummaryAmount(receiptSummary.unmatched_total) }}</div>
      </div>
    </div>

    <!-- 回款列表 -->
    <a-card class="overflow-hidden rounded-xl border border-slate-200 shadow-sm" :body-style="{ padding: '0' }">
      <div class="flex flex-col gap-2 border-b border-slate-100 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5">
        <h3 class="text-base font-semibold text-gray-800">回款记录</h3>
      </div>
      <div class="overflow-x-auto">
        <a-table
          :data-source="receipts"
          :columns="columns"
          :loading="loading"
          row-key="receipt_id"
          size="middle"
          :scroll="{ x: 1100 }"
          :pagination="{ current: currentPage, pageSize: pageSize, total, showSizeChanger: true, showTotal: t => '共 ' + t + ' 条' }"
          @change="handleTableChange"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'status'">
              <a-tag :color="record.status === '已收到' ? 'green' : 'default'">{{ record.status || '-' }}</a-tag>
            </template>
            <template v-else-if="column.key === 'project_id'">
              <a class="text-blue-600 hover:underline cursor-pointer" @click="viewDetail(record)">{{ record.project_id }}</a>
            </template>
            <template v-else-if="column.key === 'amount'">
              <span class="font-mono">{{ (record.amount || 0).toFixed(2) }}</span>
            </template>
            <template v-else-if="column.key === 'action'">
              <div class="flex flex-wrap gap-2">
                <a-button type="link" size="small" @click="viewDetail(record)">详情</a-button>
                <a-button type="link" size="small" @click="openEditReceipt(record)">编辑</a-button>
                <a-popconfirm title="确定删除此回款记录？" @confirm="deleteReceipt(record)">
                  <a-button type="link" size="small" danger>删除</a-button>
                </a-popconfirm>
              </div>
            </template>
          </template>
        </a-table>
      </div>
    </a-card>

    <!-- 新增/编辑弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="editingId ? '编辑回款' : '新增回款'"
      :confirm-loading="saving"
      @ok="saveReceipt"
      ok-text="保存"
      cancel-text="取消"
      width="600px"
    >
      <a-form :model="form" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="项目编号" required>
              <a-input v-model:value="form.project_id" placeholder="如：ZH02-202601001" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="回款单号">
              <a-input v-model:value="form.receipt_no" placeholder="可选" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="回款日期" required>
              <a-date-picker v-model:value="form.receipt_date" value-format="YYYY-MM-DD" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="回款金额（元）" required>
              <a-input-number v-model:value="form.amount" :precision="2" :min="0" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="付款方">
              <a-input v-model:value="form.payer_name" placeholder="付款方名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="收款方式">
              <a-select v-model:value="form.receipt_method">
                <a-select-option value="银行转账">银行转账</a-select-option>
                <a-select-option value="电汇">电汇</a-select-option>
                <a-select-option value="支票">支票</a-select-option>
                <a-select-option value="现金">现金</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态">
              <a-select v-model:value="form.status">
                <a-select-option value="已收到">已收到</a-select-option>
                <a-select-option value="待确认">待确认</a-select-option>
                <a-select-option value="逾期">逾期</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="备注">
              <a-textarea v-model:value="form.notes" :rows="2" placeholder="备注信息" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import type { ReceiptSummary } from '#/api/receipts'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { buildDetailLocation } from '#/utils/business-navigation'
import {
  getReceiptsApi,
  createReceiptApi,
  updateReceiptApi,
  deleteReceiptApi,
  autoMatchReceiptsApi,
  type ReceiptSummary,
} from '#/api/receipts'

const route = useRoute()
const router = useRouter()

function readPositivePageQuery(value: unknown, fallback: number) {
  const parsed = typeof value === 'string' ? Number(value) : Number.NaN
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : fallback
}

// 列表数据
const receipts = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const currentPage = ref(readPositivePageQuery(route.query.page, 1))
const pageSize = ref(readPositivePageQuery(route.query.pageSize, 20))
const receiptSummary = ref<ReceiptSummary>({
  currency_unit: '?',
  status: 'pending_verification',
  receipt_total: null,
  matched_total: null,
  unmatched_total: null,
})

// 弹窗
const modalVisible = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Record<string, any>>({})

function formatSummaryAmount(value: number | null) {
  // ??????????????????????????
  if (value == null) return '待核验'
  return (Number(value) / 10_000).toFixed(2)
}

const columns = [
  { title: '回款日期', dataIndex: 'receipt_date', key: 'receipt_date', width: 110, sorter: true },
  { title: '回款单号', dataIndex: 'receipt_no', key: 'receipt_no', width: 150, ellipsis: true },
  { title: '项目编号', dataIndex: 'project_id', key: 'project_id', width: 200, ellipsis: true },
  { title: '付款方', dataIndex: 'payer_name', key: 'payer_name', width: 150, ellipsis: true },
  { title: '金额（元）', dataIndex: 'amount', key: 'amount', width: 130, align: 'right' as const, sorter: true },
  { title: '收款方式', dataIndex: 'receipt_method', key: 'receipt_method', width: 100 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 90 },
  { title: '操作', key: 'action', width: 220, fixed: 'right' as const },
]

async function loadData() {
  loading.value = true
  try {
    const data = await getReceiptsApi({ page: currentPage.value, size: pageSize.value })
    const items = data.items ?? []
    receipts.value = items
    total.value = data.total ?? 0
    receiptSummary.value = data.summary
  } catch (e: any) {
    message.error('加载失败: ' + (e?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

function handleTableChange(pagination: any) {
  currentPage.value = pagination.current
  pageSize.value = pagination.pageSize
  void router.replace({
    query: {
      ...route.query,
      page: String(currentPage.value),
      pageSize: String(pageSize.value),
    },
  })
  loadData()
}

function viewDetail(row: { receipt_id: number }) {
  router.push(
    buildDetailLocation({
      from: {
        name: route.name,
        query: {
          ...route.query,
          page: String(currentPage.value),
          pageSize: String(pageSize.value),
        },
      },
      id: String(row.receipt_id),
      name: 'CustomerReceiptDetail',
    }),
  )
}

function openAddReceipt() {
  editingId.value = null
  form.value = {
    project_id: '',
    receipt_no: '',
    receipt_date: '',
    amount: null,
    payer_name: '',
    receipt_method: '银行转账',
    status: '已收到',
    notes: '',
  }
  modalVisible.value = true
}

function openEditReceipt(row: any) {
  editingId.value = row.receipt_id
  form.value = { ...row }
  modalVisible.value = true
}

async function saveReceipt() {
  if (!form.value.project_id || !form.value.receipt_date || !form.value.amount) {
    message.error('请填写必填项')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await updateReceiptApi(editingId.value, form.value)
      message.success('更新成功')
    } else {
      await createReceiptApi(form.value)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadData()
  } catch (e: any) {
    message.error('保存失败: ' + (e?.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

async function deleteReceipt(row: any) {
  try {
    await deleteReceiptApi(row.receipt_id)
    message.success('删除成功')
    loadData()
  } catch (e: any) {
    message.error('删除失败: ' + (e?.message || '未知错误'))
  }
}

async function autoMatch() {
  try {
    const result: any = await autoMatchReceiptsApi()
    message.success(`自动匹配完成，匹配了 ${result.matched || 0} 条`)
    loadData()
  } catch (e: any) {
    message.error('匹配失败: ' + (e?.message || '未知错误'))
  }
}

onMounted(loadData)
</script>

<style scoped>
.w-full { width: 100%; }
</style>
