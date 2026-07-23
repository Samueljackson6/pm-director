<template>
  <div class="pm-workbench-page min-h-screen p-4 sm:p-6">
    <header class="pm-page-header flex items-start justify-between gap-4">
      <div>
        <p class="pm-section-kicker">供应链资金</p>
        <h1>供应商收票</h1>
        <p class="pm-section-note">核对供应商已开票、待核验金额和项目归属；客户回款不纳入此口径。</p>
      </div>
      <a-space>
        <a-button type="primary" size="large" @click="openAdd">+ 新增发票</a-button>
        <a-button @click="showUnmatched = true">
          <template #icon><span>⚠️</span></template>
          未匹配发票 ({{ unmatchedCount }})
        </a-button>
      </a-space>
    </header>

    <!-- 数据状态提示 -->
    <a-alert v-if="dataState !== 'available'" class="mb-4" :type="dataState === 'pending_verification' ? 'warning' : 'info'" show-icon :message="dataStateText" />

    <!-- 发票列表 -->
    <a-card class="pm-table-surface" :body-style="{ padding: 0 }" aria-label="供应商收票列表">
      <div class="p-4 border-b border-gray-100">
        <h3 class="text-base font-semibold">发票列表</h3>
        <p class="mt-1 text-xs text-gray-500">仅展示资金方向为 inbound 且类型为供应商开票的收票记录；客户回款不计入本列表。</p>
      </div>
      <div class="p-4">
        <a-table :data-source="list" :columns="columns" :loading="loading" row-key="invoice_id" size="middle"
          :pagination="{ pageSize: 50, total, showSizeChanger: true, showTotal: (t: number) => '共 ' + t + ' 条' }"
          @change="handleChange">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'amount'"><span class="font-mono">{{ formatAmount(record.amount) }}</span></template>
            <template v-if="column.key === 'status'">
              <a-tag :color="record.status === '已开' ? 'blue' : record.status === '已付款' ? 'green' : 'default'">
                {{ record.status }}
              </a-tag>
            </template>
            <template v-if="column.key === 'unmatched'">
              <a-tag v-if="record._unmatched" color="orange">未匹配</a-tag>
              <a-tag v-else color="green">已匹配</a-tag>
            </template>
            <template v-if="column.key === 'action'">
              <a-button type="link" size="small" @click="viewDetail(record)">详情</a-button>
              <a-button type="link" size="small" @click="autoMatch(record)" v-if="record._unmatched">
                <template #icon><span>🔗</span></template>
                匹配
              </a-button>
              <a-button type="link" size="small" @click="editRecord(record)">编辑</a-button>
              <a-popconfirm title="删除此发票？" @confirm="deleteRecord(record)">
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </template>
          </template>
        </a-table>
      </div>
    </a-card>

    <!-- 未匹配发票弹窗 -->
    <a-modal v-model:open="showUnmatched" title="未匹配供应商发票" width="900px" :footer="null">
      <a-alert class="mb-4" type="warning" show-icon message="以下供应商发票尚未匹配到任何付款记录，请点击「匹配」尝试自动关联。" />
      <a-table :data-source="unmatchedList" :columns="unmatchedColumns" row-key="invoice_id" size="small"
        :pagination="{ pageSize: 20, total: unmatchedTotal }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'amount'"><span class="font-mono">{{ formatAmount(record.amount) }}</span></template>
          <template v-if="column.key === 'action'">
            <a-button type="link" size="small" @click="autoMatch(record)">
              <template #icon><span>🔗</span></template>
              匹配
            </a-button>
            <a-button type="link" size="small" @click="viewDetail(record)">详情</a-button>
          </template>
        </template>
      </a-table>
    </a-modal>

    <!-- 新增/编辑发票弹窗 -->
    <a-modal v-model:open="modalVisible" :title="editingId ? '编辑发票' : '新增发票'" :confirm-loading="saving" @ok="saveRecord" width="600px">
      <a-form :model="form" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12"><a-form-item label="项目编号" required><a-input v-model:value="form.project_id" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="发票日期" required><a-date-picker v-model:value="form.invoice_date" value-format="YYYY-MM-DD" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="金额（元）" required><a-input-number v-model:value="form.amount" :precision="2" :min="0" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="状态"><a-select v-model:value="form.status"><a-select-option value="已开">已开</a-select-option><a-select-option value="待开">待开</a-select-option><a-select-option value="已付款">已付款</a-select-option></a-select></a-form-item></a-col>
          <a-col :span="24"><a-form-item label="备注"><a-textarea v-model:value="form.notes" :rows="2" /></a-form-item></a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 匹配结果提示 -->
    <a-modal v-model:open="matchResultVisible" title="匹配结果" width="500px" :footer="null">
      <a-result :status="matchResult.success ? 'success' : 'info'" :title="matchResult.message" />
      <div v-if="matchResult.matches && matchResult.matches.length > 0" class="mt-4">
        <h4>匹配到的付款记录：</h4>
        <a-table :data-source="matchResult.matches" :columns="matchResultColumns" size="small" :pagination="false">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'match_type'">
              <a-tag :color="record.match_type === 'exact' ? 'green' : 'blue'">
                {{ record.match_type === 'exact' ? '精确匹配' : '模糊匹配' }}
              </a-tag>
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  getInvoicesApi, createInvoiceApi, updateInvoiceApi, deleteInvoiceApi,
  getUnmatchedInvoicesApi, autoMatchInvoiceApi, type InvoiceItem,
  type AutoMatchResult
} from '#/api/invoices'
import { buildDetailLocation } from '#/utils/business-navigation'

const route = useRoute()
const router = useRouter()
const list = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const dataState = ref<'available' | 'known_zero' | 'pending_verification' | 'source_not_established'>('known_zero')
const dataStateText = computed(() => ({
  source_not_established: '收票数据源尚未建立，当前无法确认是否存在供应商收票',
  known_zero: '当前筛选范围内已知没有供应商收票',
  pending_verification: '存在金额缺失或异常的供应商收票，请人工核验',
  available: '',
})[dataState.value])

// 未匹配发票
const unmatchedList = ref<any[]>([])
const unmatchedTotal = ref(0)
const unmatchedCount = ref(0)
const showUnmatched = ref(false)

// 匹配结果
const matchResultVisible = ref(false)
const matchResult = ref<{ success: boolean; message: string; matches: any[] }>({
  success: false, message: '', matches: []
})

// 匹配结果表格列
const matchResultColumns = [
  { title: '付款日期', dataIndex: 'payment_date', key: 'payment_date', width: 110 },
  { title: '金额（元）', dataIndex: 'amount', key: 'amount', width: 130, align: 'right' as const },
  { title: '匹配类型', dataIndex: 'match_type', key: 'match_type', width: 100 },
]

const modalVisible = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Record<string, any>>({})

const columns = [
  { title: '发票日期', dataIndex: 'invoice_date', key: 'invoice_date', width: 110 },
  { title: '供应商', dataIndex: 'supplier_name', key: 'supplier_name', width: 160, ellipsis: true },
  { title: '项目编号', dataIndex: 'project_id', key: 'project_id', width: 200, ellipsis: true },
  { title: '金额（元）', dataIndex: 'amount', key: 'amount', width: 130, align: 'right' as const },
  { title: '状态', dataIndex: 'status', key: 'status', width: 90 },
  { title: '匹配', dataIndex: 'unmatched', key: 'unmatched', width: 80 },
  { title: '操作', key: 'action', width: 220, fixed: 'right' as const },
]

const unmatchedColumns = [
  { title: '发票日期', dataIndex: 'invoice_date', key: 'invoice_date', width: 110 },
  { title: '供应商', dataIndex: 'supplier_name', key: 'supplier_name', width: 160, ellipsis: true },
  { title: '项目编号', dataIndex: 'project_id', key: 'project_id', width: 200, ellipsis: true },
  { title: '金额（元）', dataIndex: 'amount', key: 'amount', width: 130, align: 'right' as const },
  { title: '操作', key: 'action', width: 150, fixed: 'right' as const },
]

async function load() {
  loading.value = true
  try {
    const data = await getInvoicesApi({ page: page.value, size: 50, direction: 'inbound' })
    list.value = data.items ?? []
    total.value = data.total ?? 0
    dataState.value = data.data_state ?? (list.value.length ? 'available' : 'known_zero')
    // 标记未匹配状态
    for (const item of list.value) {
      const linked = await checkIfLinked(item.invoice_id)
      item._unmatched = !linked
    }
  } catch { /* ignore */ } finally { loading.value = false }
}

async function loadUnmatched() {
  try {
    const res = await getUnmatchedInvoicesApi({ page: 1, size: 100 })
    const body = res.data ?? res
    unmatchedList.value = body.items ?? []
    unmatchedTotal.value = body.total ?? 0
    unmatchedCount.value = body.total ?? 0
  } catch {
    unmatchedCount.value = 0
  }
}

async function checkIfLinked(invoiceId: number): Promise<boolean> {
  try {
    const res = await getUnmatchedInvoicesApi({ page: 1, size: 1 })
    const body = res.data ?? res
    return !(body.items ?? []).some((i: any) => i.invoice_id === invoiceId)
  } catch {
    return true
  }
}

function formatAmount(value: number | null | undefined) {
  if (value == null) return '待核实'
  return Number(value).toFixed(2)
}

function handleChange(p: any) { page.value = p.current; load() }

function viewDetail(row: InvoiceItem) {
  router.push(
    buildDetailLocation({
      from: {
        name: route.name,
        query: { ...route.query, page: String(page.value), pageSize: '50' },
      },
      id: String(row.invoice_id),
      name: 'SupplierInvoiceDetail',
    }),
  )
}

function openAdd() {
  editingId.value = null
  form.value = {
    project_id: '', invoice_date: '', amount: null, status: '已开',
    direction: 'inbound', invoice_type: '供应商开票'
  }
  modalVisible.value = true
}

function editRecord(r: any) {
  editingId.value = r.invoice_id
  form.value = { ...r }
  modalVisible.value = true
}

async function saveRecord() {
  saving.value = true
  try {
    if (editingId.value) {
      await updateInvoiceApi(editingId.value, form.value)
    } else {
      await createInvoiceApi(form.value)
    }
    message.success('保存成功')
    modalVisible.value = false
    load()
    loadUnmatched()
  } catch (e: any) {
    message.error('失败: ' + (e?.message || ''))
  } finally {
    saving.value = false
  }
}

async function deleteRecord(r: any) {
  try {
    await deleteInvoiceApi(r.invoice_id)
    message.success('已删除')
    load()
    loadUnmatched()
  } catch (e: any) {
    message.error('删除失败: ' + (e?.message || ''))
  }
}

async function autoMatch(record: any) {
  try {
    const res = await autoMatchInvoiceApi(record.invoice_id)
    const body = res.data ?? res
    matchResult.value = {
      success: body.matched,
      message: body.message,
      matches: body.matches ?? []
    }
    matchResultVisible.value = true
    if (body.matched) {
      message.success(body.message)
      load()
      loadUnmatched()
    }
  } catch (e: any) {
    message.error('匹配失败: ' + (e?.message || '未知错误'))
  }
}

onMounted(() => {
  load()
  loadUnmatched()
})
</script>
