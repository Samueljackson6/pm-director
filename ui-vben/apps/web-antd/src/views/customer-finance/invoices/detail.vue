<template>
  <div class="p-6 space-y-4 bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between">
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
        <a-tag v-if="inv?.payment_status" :color="paymentStatusColor(inv.payment_status)" class="rounded-full px-2 py-0.5 text-xs">
          {{ inv.payment_status }}
        </a-tag>
        <a-button type="primary" size="small" ghost @click="openEditModal">编辑</a-button>
        <a-popconfirm title="确定要删除这张发票吗？" ok-text="确定" cancel-text="取消" @confirm="deleteInvoice">
          <a-button type="primary" size="small" danger ghost>删除</a-button>
        </a-popconfirm>
      </div>
    </div>

    <!-- 三态容器 -->
    <state-block :loading="loading" :error="error" error-title="发票详情加载失败" @retry="load">
      <template v-if="inv">
        <!-- KPI 指标行（紧凑现代化） -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">发票金额（含税）</div>
            <div class="text-2xl font-bold text-gray-900">{{ fmtMoney(inv.amount) }}</div>
            <div class="text-xs text-gray-400 mt-0.5">元</div>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">税率</div>
            <div class="text-2xl font-bold text-blue-600">{{ inv.tax_rate ? inv.tax_rate.toFixed(0) + '%' : '-' }}</div>
            <div class="text-xs text-gray-400 mt-0.5">百分比</div>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">税额</div>
            <div class="text-2xl font-bold text-orange-600">{{ fmtMoney(calculatedTaxAmount) }}</div>
            <div class="text-xs text-gray-400 mt-0.5">元</div>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">价税合计</div>
            <div class="text-2xl font-bold text-green-600">{{ fmtMoney(calculatedTotalWithTax) }}</div>
            <div class="text-xs text-gray-400 mt-0.5">元</div>
          </div>
        </div>

        <!-- 吸顶锚点条 -->
        <div class="sticky top-0 z-20 bg-white/85 backdrop-blur-sm border-y border-gray-200 -mx-6 px-6">
          <div class="flex gap-1 py-2 overflow-x-auto">
            <button
              v-for="a in anchors"
              :key="a.id"
              @click="scrollToAnchor(a.id)"
              :class="[
                'px-3 py-1.5 text-sm rounded-md whitespace-nowrap transition-colors',
                activeAnchor === a.id ? 'bg-blue-50 text-blue-600 font-medium' : 'text-gray-500 hover:bg-gray-100'
              ]"
            >
              {{ a.label }}
            </button>
          </div>
        </div>

        <!-- 1. 项目信息 -->
        <div id="project" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
          <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
            <span class="w-1 h-4 rounded-full bg-blue-500"></span>
            <span class="text-sm font-semibold text-gray-700">项目信息</span>
          </div>
          <div class="px-5 py-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-400 mb-1">项目编号</div>
                <router-link
                  :to="{ name: 'ContractDetail', query: { id: inv.project_id } }"
                  class="text-blue-600 hover:underline text-sm font-medium"
                >
                  {{ inv.project_id }}
                </router-link>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">项目名称</div>
                <div class="text-sm text-gray-900">{{ inv.project_name || '-' }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">客户名称</div>
                <div class="text-sm text-gray-900">{{ inv.customer_name || '-' }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">方向</div>
                <a-tag :color="inv.direction === 'outbound' ? 'blue' : 'green'" class="rounded-full text-xs">
                  {{ inv.direction === 'outbound' ? '客户发票' : '供应商发票' }}
                </a-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. 发票信息 -->
        <div id="invoice" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
          <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
            <span class="w-1 h-4 rounded-full bg-teal-500"></span>
            <span class="text-sm font-semibold text-gray-700">发票信息</span>
          </div>
          <div class="px-5 py-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-400 mb-1">发票编号</div>
                <div class="text-sm font-mono text-gray-900">{{ inv.invoice_no || '-' }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">发票类型</div>
                <a-tag :color="invoiceTypeColor(inv.invoice_type)" class="rounded-full text-xs">
                  {{ inv.invoice_type || '-' }}
                </a-tag>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">开票日期</div>
                <div class="text-sm text-gray-900">{{ inv.invoice_date || '-' }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">状态</div>
                <a-tag :color="statusColor(inv.status)" class="rounded-full text-xs">
                  {{ inv.status || '-' }}
                </a-tag>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">匹配状态</div>
                <a-tag :color="paymentStatusColor(inv.payment_status)" class="rounded-full text-xs">
                  {{ inv.payment_status || '未匹配' }}
                </a-tag>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">回款日期</div>
                <div class="text-sm text-gray-900">{{ inv.received_date || '-' }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. 金额信息 -->
        <div id="amount" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
          <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
            <span class="w-1 h-4 rounded-full bg-amber-500"></span>
            <span class="text-sm font-semibold text-gray-700">金额信息</span>
          </div>
          <div class="px-5 py-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-400 mb-1">发票金额（含税，元）</div>
                <div class="text-sm font-semibold text-gray-900">{{ fmtMoney(inv.amount) }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">税率</div>
                <div class="text-sm text-gray-900">{{ inv.tax_rate ? inv.tax_rate.toFixed(0) + '%' : '-' }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">税额（元）</div>
                <div class="text-sm text-orange-600 font-semibold">{{ fmtMoney(calculatedTaxAmount) }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">不含税金额（元）</div>
                <div class="text-sm text-gray-900">{{ fmtMoney(inv.amount / (1 + (inv.tax_rate || 0) / 100)) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. 关联回款 -->
        <div id="receipts" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
          <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
            <span class="w-1 h-4 rounded-full bg-green-500"></span>
            <span class="text-sm font-semibold text-gray-700">关联回款</span>
            <span class="ml-auto text-xs text-gray-400">已匹配 {{ fmtMoney(matchedAmount) }} 元</span>
          </div>
          <div class="px-5 py-4">
            <template v-if="linkedReceipts.length">
              <div class="space-y-2">
                <div
                  v-for="rec in linkedReceipts"
                  :key="rec.receipt_id"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-green-50/50 cursor-pointer transition-colors"
                  @click="router.push({ name: 'CustomerReceiptDetail', query: { id: rec.receipt_id } })"
                >
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-sm">💰</div>
                    <div>
                      <div class="font-medium text-sm text-gray-900">{{ rec.receipt_no || '回款 #' + rec.receipt_id }}</div>
                      <div class="text-xs text-gray-400">{{ rec.receipt_date }} · {{ rec.receipt_method || '-' }}</div>
                    </div>
                  </div>
                  <div class="text-right flex items-center gap-2">
                    <div class="font-semibold text-sm text-green-600">{{ fmtMoney(rec.link_amount || rec.amount) }} 元</div>
                    <a-button type="link" size="small" danger @click.stop="unlinkReceipt(rec)">取消关联</a-button>
                  </div>
                </div>
              </div>
              <div class="mt-3 pt-3 border-t border-gray-100">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-500">匹配状态：</span>
                  <span>
                    <a-tag v-if="matchedAmount >= inv.amount" color="success" class="rounded-full">完全匹配</a-tag>
                    <a-tag v-else-if="matchedAmount > 0" color="warning" class="rounded-full">
                      部分匹配 ({{ fmtMoney(matchedAmount) }}/{{ fmtMoney(inv.amount) }})
                    </a-tag>
                    <a-tag v-else color="default" class="rounded-full">未匹配</a-tag>
                  </span>
                </div>
              </div>
            </template>
            <div v-else class="text-center py-6">
              <a-empty description="暂无关联回款" />
              <a-button type="link" size="small" @click="showLinkReceipt = true">+ 关联回款</a-button>
            </div>
          </div>
        </div>

        <!-- 5. 发票文件 -->
        <div id="files" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
          <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
            <span class="w-1 h-4 rounded-full bg-gray-400"></span>
            <span class="text-sm font-semibold text-gray-700">发票文件</span>
            <a-button type="link" size="small" class="ml-auto" @click="$refs.fileUpload?.handleUpload()">
              上传文件
            </a-button>
          </div>
          <div class="px-5 py-4">
            <input
              ref="fileUpload"
              type="file"
              style="display:none"
              @change="handleFileChange"
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            />
            <template v-if="invoiceFiles.length">
              <div class="space-y-2">
                <div
                  v-for="f in invoiceFiles"
                  :key="f.file_id"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded bg-blue-100 flex items-center justify-center text-sm">
                      {{ fileIcon(f.file_type) }}
                    </div>
                    <div>
                      <div class="font-medium text-sm text-gray-900">{{ f.file_name }}</div>
                      <div class="text-xs text-gray-400">{{ f.file_type?.toUpperCase() || 'FILE' }} · {{ formatSize(f.file_size) }}</div>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <a-button size="small" type="link" @click="downloadFile(f)">下载</a-button>
                    <a-popconfirm title="确定删除此文件？" ok-text="确定" cancel-text="取消" @confirm="deleteFile(f)">
                      <a-button size="small" type="link" danger>删除</a-button>
                    </a-popconfirm>
                  </div>
                </div>
              </div>
            </template>
            <a-empty v-else description="暂无发票文件" />
          </div>
        </div>

        <!-- 6. 系统信息 -->
        <div id="system" class="bg-white rounded-lg border border-gray-200 overflow-hidden scroll-mt-16">
          <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-100 bg-gray-50/50">
            <span class="w-1 h-4 rounded-full bg-slate-400"></span>
            <span class="text-sm font-semibold text-gray-700">系统信息</span>
          </div>
          <div class="px-5 py-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-400 mb-1">来源</div>
                <div class="text-sm text-gray-900">{{ inv.source || '-' }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">创建时间</div>
                <div class="text-sm text-gray-900">{{ inv.created_at || '-' }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">更新/导入时间</div>
                <div class="text-sm text-gray-900">{{ inv.updated_at || inv.import_time || '-' }}</div>
              </div>
            </div>
            <div v-if="parsedNotes" class="mt-4 pt-4 border-t border-gray-100">
              <div class="text-xs text-gray-400 mb-2">结构化数据（自动解析）</div>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-2 bg-gray-50 rounded-lg p-3 text-sm">
                <div><span class="text-gray-500">合同编号：</span><span class="font-medium">{{ parsedNotes.contractNo }}</span></div>
                <div><span class="text-gray-500">开票类型：</span><span class="font-medium">{{ parsedNotes.invoiceType }}</span></div>
                <div><span class="text-gray-500">开票日期：</span><span class="font-medium">{{ parsedNotes.invoiceDate }}</span></div>
                <div><span class="text-gray-500">状态：</span><span class="font-medium">{{ parsedNotes.status }}</span></div>
                <div><span class="text-gray-500">匹配状态：</span><span class="font-medium">{{ parsedNotes.matchStatus }}</span></div>
                <div><span class="text-gray-500">来源：</span><span class="font-medium">{{ parsedNotes.source }}</span></div>
                <div class="col-span-2 md:col-span-3"><span class="text-gray-500">处理时间：</span><span class="font-medium">{{ parsedNotes.processTime }}</span></div>
              </div>
            </div>
            <div v-else-if="inv.notes" class="mt-4 pt-4 border-t border-gray-100">
              <div class="text-xs text-gray-400 mb-1">备注</div>
              <div class="text-sm text-gray-600 whitespace-pre-wrap">{{ inv.notes }}</div>
            </div>
          </div>
        </div>
      </template>
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
            <a-form-item label="发票编号"><a-input v-model:value="editForm.invoice_no" /></a-form-item>
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
            <a-form-item label="备注"><a-textarea v-model:value="editForm.notes" :rows="2" /></a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed, nextTick, onUnmounted } from 'vue'
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
const linkedReceipts = ref<any[]>([])
const showLinkReceipt = ref(false)
const editModalVisible = ref(false)
const editSaving = ref(false)
const editForm = ref<Record<string, any>>({})

// 锚点导航
const anchors = [
  { id: 'project', label: '项目' },
  { id: 'invoice', label: '发票' },
  { id: 'amount', label: '金额' },
  { id: 'receipts', label: '回款' },
  { id: 'files', label: '文件' },
  { id: 'system', label: '系统' },
]
const activeAnchor = ref('project')
let anchorObserver: IntersectionObserver | null = null

function scrollToAnchor(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  const y = el.getBoundingClientRect().top + window.pageYOffset - 56
  window.scrollTo({ top: y, behavior: 'smooth' })
}

// 匹配金额
const matchedAmount = computed(() =>
  linkedReceipts.value.reduce((sum: number, rec: any) => sum + (rec.link_amount || rec.amount || 0), 0)
)

/** 计算税额 */
const calculatedTaxAmount = computed(() => {
  if (!inv.value) return 0
  if (inv.value.tax_amount != null && inv.value.tax_amount !== 0) {
    return inv.value.tax_amount
  }
  const amount = inv.value.amount || 0
  const rate = inv.value.tax_rate || 0
  const taxRate = rate <= 1 ? rate : rate / 100
  return amount * taxRate / (1 + taxRate)
})

/** 计算价税合计 */
const calculatedTotalWithTax = computed(() => {
  if (!inv.value) return 0
  if (inv.value.total_with_tax != null && inv.value.total_with_tax !== 0) {
    return inv.value.total_with_tax
  }
  return inv.value.amount || 0
})

/** 解析备注中的结构化数据 */
const parsedNotes = computed(() => {
  const notes = inv.value?.notes
  if (!notes || typeof notes !== 'string') return null
  const pattern = /^([A-Z0-9-]+)(客户开票|客户回款|供应商开票|客户发票)(\d{4}[-/]\d{1,2}[-/]\d{1,2})(已开|已回款|待开)-(未匹配|已匹配|部分匹配)(\w+)([\d\s:-]+)$/
  const m = notes.trim().match(pattern)
  if (!m) return null
  return {
    contractNo: m[1],
    invoiceType: m[2],
    invoiceDate: m[3],
    status: m[4],
    matchStatus: m[5],
    source: m[6],
    processTime: m[7]?.trim() || '-',
  }
})

async function load() {
  loading.value = true; error.value = ''
  try {
    const id = route.params.id || route.query.id
    const data: any = await getInvoiceDetailApi(Number(id))
    inv.value = data.invoice ?? null
    if (!inv.value) error.value = '未找到该发票'
    else {
      await Promise.all([loadInvoiceFiles(), loadLinkedReceipts()])
    }
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally { loading.value = false }
}

async function loadLinkedReceipts() {
  try {
    const data: any = await requestClient.get(`/api/invoices/${inv.value.invoice_id}/receipts`)
    linkedReceipts.value = data.receipts ?? []
  } catch { linkedReceipts.value = [] }
}

async function loadInvoiceFiles() {
  try {
    const data: any = await requestClient.get(`/api/invoices/${inv.value.invoice_id}/files`)
    invoiceFiles.value = data.files ?? []
  } catch { invoiceFiles.value = [] }
}

function openEditModal() {
  if (!inv.value) return
  editForm.value = {
    invoice_no: inv.value.invoice_no || '', invoice_date: inv.value.invoice_date || '',
    amount: inv.value.amount || null, tax_rate: inv.value.tax_rate || null,
    tax_amount: inv.value.tax_amount || null, total_with_tax: inv.value.total_with_tax || null,
    status: inv.value.status || '已开', received_date: inv.value.received_date || '',
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
  } finally { editSaving.value = false }
}

async function deleteInvoice() {
  if (!inv.value) return
  try {
    await deleteInvoiceApi(inv.value.invoice_id)
    message.success('发票已删除')
    router.push({ name: 'CustomerInvoices' })
  } catch (e: any) {
    message.error('删除失败: ' + (e?.message || '未知错误'))
  }
}

async function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !inv.value) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    await requestClient.post(`/api/invoices/${inv.value.invoice_id}/files`, formData)
    message.success('文件上传成功')
    await loadInvoiceFiles()
  } catch (e: any) {
    message.error('上传失败: ' + (e?.response?.data?.message || e?.message || '未知错误'))
  } finally { uploading.value = false }
  target.value = ''
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

async function unlinkReceipt(rec: any) {
  try {
    await requestClient.delete(`/api/invoices/${inv.value.invoice_id}/receipts/${rec.receipt_id}`)
    message.success('已取消关联')
    await loadLinkedReceipts()
  } catch (e: any) {
    message.error('操作失败: ' + (e?.message || '未知错误'))
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

function goBack() { router.push({ name: 'CustomerInvoices' }) }

function fmtMoney(n: number | null | undefined): string {
  return n == null ? '0.00' : n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function statusColor(status: string): string {
  const map: Record<string, string> = { '已开': 'blue', '已回款': 'green', '待开': 'orange' }
  return map[status] || 'default'
}

function paymentStatusColor(status: string): string {
  const map: Record<string, string> = { '已匹配': 'green', '未匹配': 'default' }
  return map[status] || 'default'
}

function invoiceTypeColor(type: string): string {
  const map: Record<string, string> = { '客户开票': 'blue', '客户回款': 'green', '供应商开票': 'orange' }
  return map[type] || 'default'
}

// 锚点 IntersectionObserver
watch(() => inv.value, () => {
  nextTick(() => {
    anchorObserver?.disconnect()
    anchorObserver = new IntersectionObserver(
      entries => {
        entries.forEach(e => {
          if (e.isIntersecting) activeAnchor.value = (e.target as HTMLElement).id
        })
      },
      { rootMargin: '-56px 0px -70% 0px' },
    )
    anchors.forEach(a => {
      const el = document.getElementById(a.id)
      if (el) anchorObserver?.observe(el)
    })
  })
}, { flush: 'post' })

onUnmounted(() => anchorObserver?.disconnect())
onMounted(load)
watch(
  () => route.params.id || route.query.id,
  (n, o) => { if (n && n !== o) load() },
  { immediate: false },
)
</script>

<style scoped>
.scroll-mt-16 { scroll-margin-top: 64px; }
</style>
