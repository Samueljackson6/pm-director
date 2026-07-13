<template>
  <div class="p-6 bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-4">
        <a-button type="text" class="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-100" @click="goBack">
          <span class="text-lg">←</span>
        </a-button>
        <div>
          <h2 class="text-xl font-semibold text-gray-800">供应商发票详情</h2>
          <div v-if="inv" class="text-sm text-gray-500 mt-0.5">{{ inv.invoice_no || '发票 #' + inv.invoice_id }}</div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a-tag v-if="inv?.status" :color="statusColor(inv.status)" class="rounded-full px-3 py-0.5 text-xs">{{ inv.status }}</a-tag>
        <a-button type="primary" size="small" ghost @click="openEditModal">编辑</a-button>
        <a-popconfirm title="确定要删除这张发票吗？" ok-text="确定" cancel-text="取消" @confirm="deleteInvoice">
          <a-button type="primary" size="small" danger ghost>删除</a-button>
        </a-popconfirm>
      </div>
    </div>

    <state-block :loading="loading" :error="error" error-title="发票详情加载失败" @retry="load">
      <!-- KPI 指标 -->
      <div v-if="inv" class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">金额（元）</div>
          <div class="text-2xl font-bold text-gray-900">{{ fmtMoney(inv.amount) }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">税率</div>
          <div class="text-2xl font-bold text-blue-600">{{ inv.tax_rate ? (inv.tax_rate * 100).toFixed(0) + '%' : '-' }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">税额（元）</div>
          <div class="text-2xl font-bold text-orange-600">{{ fmtMoney(inv.tax_amount) }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">价税合计（元）</div>
          <div class="text-2xl font-bold text-green-600">{{ fmtMoney(inv.total_with_tax) }}</div>
        </div>
      </div>

      <!-- 基本信息 -->
      <a-card v-if="inv" title="基本信息" class="rounded-lg mb-4" size="small">
        <a-descriptions :column="2" size="small" bordered>
          <a-descriptions-item label="发票编号" :span="2"><span class="font-mono">{{ inv.invoice_no || '-' }}</span></a-descriptions-item>
          <a-descriptions-item label="项目编号" :span="2">
            <router-link :to="{ name: 'ContractDetail', query: { id: inv.project_id } }" class="text-blue-600 hover:underline">{{ inv.project_id }}</router-link>
          </a-descriptions-item>
          <a-descriptions-item label="供应商">{{ inv.supplier_name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="发票类型">{{ inv.invoice_type || '-' }}</a-descriptions-item>
          <a-descriptions-item label="开票日期">{{ inv.invoice_date || '-' }}</a-descriptions-item>
          <a-descriptions-item label="状态"><a-tag :color="statusColor(inv.status)">{{ inv.status || '-' }}</a-tag></a-descriptions-item>
          <a-descriptions-item label="来源">{{ inv.source || '-' }}</a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ inv.created_at || '-' }}</a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">{{ inv.notes || '-' }}</a-descriptions-item>
        </a-descriptions>
      </a-card>
    </state-block>

    <!-- 编辑弹窗 -->
    <a-modal v-model:open="editModalVisible" title="编辑供应商发票" :confirm-loading="editSaving" @ok="saveEdit" ok-text="保存" cancel-text="取消" width="600px">
      <a-form :model="editForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12"><a-form-item label="发票编号"><a-input v-model:value="editForm.invoice_no" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="发票日期"><a-date-picker v-model:value="editForm.invoice_date" value-format="YYYY-MM-DD" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="金额（元）"><a-input-number v-model:value="editForm.amount" :precision="2" :min="0" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="状态"><a-select v-model:value="editForm.status"><a-select-option value="已开">已开</a-select-option><a-select-option value="已付款">已付款</a-select-option></a-select></a-form-item></a-col>
          <a-col :span="24"><a-form-item label="备注"><a-textarea v-model:value="editForm.notes" :rows="2" /></a-form-item></a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getInvoiceDetailApi, updateInvoiceApi, deleteInvoiceApi } from '#/api/invoices'
import StateBlock from '#/components/state-block/index.vue'

const route = useRoute()
const router = useRouter()
const inv = ref<any>(null)
const loading = ref(true)
const error = ref('')
const editModalVisible = ref(false)
const editSaving = ref(false)
const editForm = ref<Record<string, any>>({})

async function load() {
  loading.value = true; error.value = ''
  try {
    const id = route.query.id
    const data: any = await getInvoiceDetailApi(Number(id))
    inv.value = data.invoice ?? null
    if (!inv.value) error.value = '未找到该发票'
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally { loading.value = false }
}

function openEditModal() {
  if (!inv.value) return
  editForm.value = {
    invoice_no: inv.value.invoice_no || '', invoice_date: inv.value.invoice_date || '',
    amount: inv.value.amount || null, status: inv.value.status || '已开', notes: inv.value.notes || '',
  }
  editModalVisible.value = true
}

async function saveEdit() {
  if (!inv.value) return
  editSaving.value = true
  try {
    await updateInvoiceApi(inv.value.invoice_id, editForm.value)
    message.success('发票更新成功'); editModalVisible.value = false; load()
  } catch (e: any) { message.error('更新失败: ' + (e?.message || '未知错误'))
  } finally { editSaving.value = false }
}

async function deleteInvoice() {
  if (!inv.value) return
  try {
    await deleteInvoiceApi(inv.value.invoice_id)
    message.success('发票已删除'); router.push({ name: 'SupplierInvoices' })
  } catch (e: any) { message.error('删除失败: ' + (e?.message || '未知错误')) }
}

function goBack() { router.push({ name: 'SupplierInvoices' }) }
function fmtMoney(n: number | null | undefined): string { return n == null ? '0.00' : n.toFixed(2) }
function statusColor(status: string): string {
  const map: Record<string, string> = { '已付款': 'green', '已开': 'blue' }
  return map[status] || 'default'
}

onMounted(load)
watch(() => route.query.id, (n, o) => { if (n && n !== o) load() })
</script>

<style scoped>
.text-lg { font-size: 1.125rem; }
.w-full { width: 100%; }
</style>
