<template>
  <div class="p-6 bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-4">
        <a-button
          type="text"
          class="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-100"
          @click="goBack"
        >
          <span class="text-lg">&#8592;</span>
        </a-button>
        <div>
          <h2 class="text-xl font-semibold text-gray-800">发票详情</h2>
          <div v-if="inv" class="text-sm text-gray-500 mt-0.5">
            {{ inv.invoice_no || '发票 #' + inv.invoice_id }}
          </div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a-tag v-if="inv?.status" :color="statusColor(inv.status)" class="rounded-full px-3 py-0.5 text-xs">
          {{ inv.status }}
        </a-tag>
        <a-button type="primary" size="small" ghost @click="openEditModal">编辑</a-button>
        <a-popconfirm
          title="确定要删除这张发票吗？"
          ok-text="确定"
          cancel-text="取消"
          @confirm="deleteInvoice"
        >
          <a-button type="primary" size="small" danger ghost>删除</a-button>
        </a-popconfirm>
      </div>
    </div>

    <!-- 三态：loading / error / 正常内容 -->
    <state-block :loading="loading" :error="error" error-title="发票详情加载失败" @retry="load">
      <!-- KPI 指标行 -->
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
          <a-descriptions-item label="发票编号" :span="2">
            <span class="font-mono">{{ inv.invoice_no || '-' }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="项目编号" :span="2">
            <router-link :to="{ name: 'ContractDetail', query: { id: inv.project_id } }" class="text-blue-600 hover:underline">
              {{ inv.project_id }}
            </router-link>
          </a-descriptions-item>
          <a-descriptions-item label="发票类型">
            <a-tag :color="invoiceTypeColor(inv.invoice_type)">{{ inv.invoice_type || '-' }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="方向">
            <a-tag :color="inv.direction === 'outbound' ? 'blue' : 'green'">
              {{ inv.direction === 'outbound' ? '客户发票' : '供应商发票' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="开票日期">{{ inv.invoice_date || '-' }}</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="statusColor(inv.status)">{{ inv.status || '-' }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="回款日期">{{ inv.received_date || '-' }}</a-descriptions-item>
          <a-descriptions-item label="付款状态">
            <a-tag :color="paymentStatusColor(inv.payment_status)">{{ inv.payment_status || '-' }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="来源">{{ inv.source || '-' }}</a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ inv.created_at || '-' }}</a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">{{ inv.notes || '-' }}</a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 发票文件上传 -->
      <a-card v-if="inv" title="发票文件" class="rounded-lg" size="small">
        <div class="mb-3 flex justify-end">
          <a-upload
            :before-upload="beforeUpload"
            :show-upload-list="false"
            :disabled="uploading"
          >
            <a-button type="primary" size="small" :loading="uploading">
              <span class="mr-1">&#8593;</span> 上传发票文件
            </a-button>
          </a-upload>
        </div>
        <template v-if="invoiceFiles.length">
          <div class="space-y-2">
            <div
              v-for="f in invoiceFiles"
              :key="f.file_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
            >
              <div class="flex items-center gap-3">
                <span class="text-2xl">{{ fileIcon(f.file_type) }}</span>
                <div>
                  <div class="font-medium text-sm">{{ f.file_name }}</div>
                  <div class="text-xs text-gray-400">{{ f.file_type?.toUpperCase() }} · {{ formatSize(f.file_size) }}</div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <a-button size="small" type="link" @click="downloadFile(f)">下载</a-button>
                <a-popconfirm
                  title="确定删除此文件？"
                  ok-text="确定"
                  cancel-text="取消"
                  @confirm="deleteFile(f)"
                >
                  <a-button size="small" type="link" danger>删除</a-button>
                </a-popconfirm>
              </div>
            </div>
          </div>
        </template>
        <a-empty v-else description="暂无发票文件" />
      </a-card>
    </state-block>

    <!-- 编辑弹窗 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑发票"
      :confirm-loading="editSaving"
      @ok="saveEdit"
      ok-text="保存"
      cancel-text="取消"
      width="600px"
    >
      <a-form :model="editForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="发票编号">
              <a-input v-model:value="editForm.invoice_no" placeholder="发票编号" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="发票日期">
              <a-date-picker v-model:value="editForm.invoice_date" value-format="YYYY-MM-DD" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="金额（元）">
              <a-input-number v-model:value="editForm.amount" :precision="2" :min="0" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="税率（%）">
              <a-input-number v-model:value="editForm.tax_rate" :precision="2" :min="0" :max="100" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="税额（元）">
              <a-input-number v-model:value="editForm.tax_amount" :precision="2" :min="0" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="价税合计（元）">
              <a-input-number v-model:value="editForm.total_with_tax" :precision="2" :min="0" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态">
              <a-select v-model:value="editForm.status">
                <a-select-option value="已开">已开</a-select-option>
                <a-select-option value="已回款">已回款</a-select-option>
                <a-select-option value="待开">待开</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="回款日期">
              <a-date-picker v-model:value="editForm.received_date" value-format="YYYY-MM-DD" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="备注">
              <a-textarea v-model:value="editForm.notes" :rows="2" placeholder="补充说明..." />
            </a-form-item>
          </a-col>
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
import { requestClient } from '#/api/request'
import StateBlock from '#/components/state-block/index.vue'

const route = useRoute()
const router = useRouter()
const inv = ref<any>(null)
const loading = ref(true)
const error = ref('')
const uploading = ref(false)
const invoiceFiles = ref<any[]>([])

// 编辑弹窗
const editModalVisible = ref(false)
const editSaving = ref(false)
const editForm = ref<Record<string, any>>({})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id || route.query.id
    const data: any = await getInvoiceDetailApi(Number(id))
    inv.value = data.invoice ?? null
    if (!inv.value) error.value = '未找到该发票'
    else {
      // 加载发票文件
      await loadInvoiceFiles()
    }
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally {
    loading.value = false
  }
}

async function loadInvoiceFiles() {
  try {
    const data: any = await requestClient.get(`/api/invoices/${inv.value.invoice_id}/files`)
    invoiceFiles.value = data.files ?? []
  } catch (e) {
    invoiceFiles.value = []
  }
}

function openEditModal() {
  if (!inv.value) return
  editForm.value = {
    invoice_no: inv.value.invoice_no || '',
    invoice_date: inv.value.invoice_date || '',
    amount: inv.value.amount || null,
    tax_rate: inv.value.tax_rate || null,
    tax_amount: inv.value.tax_amount || null,
    total_with_tax: inv.value.total_with_tax || null,
    status: inv.value.status || '已开',
    received_date: inv.value.received_date || '',
    notes: inv.value.notes || '',
  }
  editModalVisible.value = true
}

async function saveEdit() {
  if (!inv.value) return
  editSaving.value = true
  try {
    await updateInvoiceApi(inv.value.invoice_id, editForm.value)
    message.success('发票更新成功')
    editModalVisible.value = false
    load()
  } catch (e: any) {
    message.error('更新失败: ' + (e?.message || '未知错误'))
  } finally {
    editSaving.value = false
  }
}

async function deleteInvoice() {
  if (!inv.value) return
  try {
    await deleteInvoiceApi(inv.value.invoice_id)
    message.success('发票已删除')
    router.push({ name: 'InvoiceList' })
  } catch (e: any) {
    message.error('删除失败: ' + (e?.message || '未知错误'))
  }
}

async function beforeUpload(file: File) {
  if (!inv.value) return false
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    await requestClient.post(`/api/invoices/${inv.value.invoice_id}/files`, formData)
    message.success('文件上传成功')
    await loadInvoiceFiles()
  } catch (e: any) {
    message.error('上传失败: ' + (e?.response?.data?.message || e?.message || '未知错误'))
  } finally {
    uploading.value = false
  }
  return false
}

async function downloadFile(file: any) {
  try {
    const url = `/api/invoices/${inv.value.invoice_id}/files/${file.file_id}`
    const response = await fetch(url)
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = file.file_name
    a.click()
    window.URL.revokeObjectURL(downloadUrl)
  } catch (e: any) {
    message.error('下载失败: ' + (e?.message || '未知错误'))
  }
}

async function deleteFile(file: any) {
  try {
    await requestClient.delete(`/api/invoices/${inv.value.invoice_id}/files/${file.file_id}`)
    message.success('文件已删除')
    await loadInvoiceFiles()
  } catch (e: any) {
    message.error('删除失败: ' + (e?.message || '未知错误'))
  }
}

function fileIcon(type: string): string {
  if (!type) return '📄'
  const t = type.toLowerCase()
  if (t.includes('pdf')) return '📑'
  if (t.includes('image')) return '🖼️'
  return '📄'
}

function formatSize(bytes: number): string {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i]
}

onMounted(load)

// 监听路由参数变化
watch(
  () => route.params.id || route.query.id,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      load()
    }
  },
  { immediate: false },
)

function goBack() {
  router.push({ name: 'InvoiceList' })
}

function fmtMoney(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toFixed(2)
}

function statusColor(status: string): string {
  const map: Record<string, string> = {
    '已开': 'blue',
    '已回款': 'green',
    '待开': 'orange',
  }
  return map[status] || 'default'
}

function paymentStatusColor(status: string): string {
  const map: Record<string, string> = {
    '已匹配': 'green',
    '未匹配': 'default',
  }
  return map[status] || 'default'
}

function invoiceTypeColor(type: string): string {
  const map: Record<string, string> = {
    '客户开票': 'blue',
    '客户回款': 'green',
    '供应商开票': 'orange',
  }
  return map[type] || 'default'
}
</script>

<style scoped>
.text-lg {
  font-size: 1.125rem;
}
.w-full {
  width: 100%;
}
</style>