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
          <h2 class="text-xl font-semibold text-gray-800">供应商详情</h2>
          <div v-if="supplier" class="text-sm text-gray-500 mt-0.5">
            {{ supplier.supplier_name }}
          </div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a-tag v-if="supplier?.status" :color="supplier.status === 'active' ? 'green' : 'default'" class="rounded-full px-3 py-0.5 text-xs">
          {{ supplier.status === 'active' ? '合作中' : '已暂停' }}
        </a-tag>
        <a-button type="primary" size="small" ghost @click="openAddInvoice">+ 新增发票</a-button>
        <a-button type="primary" size="small" ghost @click="openAddPayment">+ 新增付款</a-button>
      </div>
    </div>

    <!-- 三态 -->
    <state-block :loading="loading" :error="error" error-title="供应商详情加载失败" @retry="load">
      <!-- KPI 指标行 -->
      <div v-if="supplier" class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">合同总额（万元）</div>
          <div class="text-2xl font-bold text-gray-900">{{ fmtMoney(supplier.total_contract_amount) }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">已开票（万元）</div>
          <div class="text-2xl font-bold text-blue-600">{{ fmtMoney(supplier.total_invoiced) }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">已付款（万元）</div>
          <div class="text-2xl font-bold text-green-600">{{ fmtMoney(supplier.total_paid) }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">未付款（万元）</div>
          <div class="text-2xl font-bold text-orange-600">{{ fmtMoney(supplier.total_unpaid) }}</div>
        </div>
      </div>

      <!-- 基本信息 -->
      <a-card v-if="supplier" title="基本信息" class="rounded-lg mb-4" size="small">
        <a-descriptions :column="2" size="small" bordered>
          <a-descriptions-item label="供应商名称" :span="2">{{ supplier.supplier_name }}</a-descriptions-item>
          <a-descriptions-item label="简称" :span="2">{{ supplier.short_name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="统一社会信用代码" :span="2">{{ supplier.credit_code || '-' }}</a-descriptions-item>
          <a-descriptions-item label="联系人">{{ supplier.contact_person || '-' }}</a-descriptions-item>
          <a-descriptions-item label="联系电话">{{ supplier.contact_phone || '-' }}</a-descriptions-item>
          <a-descriptions-item label="类别">{{ supplier.category || '-' }}</a-descriptions-item>
          <a-descriptions-item label="首次合作日期">{{ supplier.first_cooperation_date || '-' }}</a-descriptions-item>
          <a-descriptions-item label="评估" :span="2">{{ supplier.evaluation || '-' }}</a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 关联发票 -->
      <a-card title="供应商发票（供应商向我们开具）" class="rounded-lg mb-4" size="small">
        <template #extra>
          <a-button type="link" size="small" @click="openAddInvoice">+ 新增发票</a-button>
        </template>
        <template v-if="invoices.length">
          <div class="space-y-2 max-h-[300px] overflow-y-auto">
            <div
              v-for="inv in invoices"
              :key="inv.invoice_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-blue-50/50 cursor-pointer"
              @click="router.push({ name: 'InvoiceDetail', query: { id: inv.invoice_id } })"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-8 h-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-xs font-bold shrink-0">
                  发
                </div>
                <div class="min-w-0">
                  <div class="font-medium text-sm truncate">{{ inv.invoice_no || '发票 #' + inv.invoice_id }}</div>
                  <div class="text-xs text-gray-400">{{ inv.invoice_date || '日期未知' }} · {{ inv.project_id }}</div>
                </div>
              </div>
              <div class="text-right shrink-0">
                <div class="font-semibold text-sm text-orange-600">¥{{ fmtMoney(inv.amount) }} 元</div>
                <a-tag :color="invoiceStatusColor(inv.status)" size="small">{{ inv.status }}</a-tag>
              </div>
            </div>
          </div>
        </template>
        <a-empty v-else description="暂无供应商发票" />
      </a-card>

      <!-- 关联付款 -->
      <a-card title="付款记录（我们向供应商付款）" class="rounded-lg mb-4" size="small">
        <template #extra>
          <a-button type="link" size="small" @click="openAddPayment">+ 新增付款</a-button>
        </template>
        <template v-if="payments.length">
          <div class="space-y-2 max-h-[300px] overflow-y-auto">
            <div
              v-for="pay in payments"
              :key="pay.payment_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-green-50/50"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-xs font-bold shrink-0">
                  付
                </div>
                <div class="min-w-0">
                  <div class="font-medium text-sm truncate">{{ pay.payment_method || '银行转账' }}</div>
                  <div class="text-xs text-gray-400">{{ pay.payment_date || '日期未知' }} · {{ pay.project_id || '-' }}</div>
                </div>
              </div>
              <div class="text-right shrink-0">
                <div class="font-semibold text-sm text-green-600">¥{{ fmtMoney(pay.amount) }} 元</div>
                <a-tag :color="paymentStatusColor(pay.status)" size="small">{{ pay.status || '已完成' }}</a-tag>
              </div>
            </div>
          </div>
        </template>
        <a-empty v-else description="暂无付款记录" />
      </a-card>

      <!-- 关联合同 -->
      <a-card title="关联合同" class="rounded-lg" size="small">
        <template v-if="contracts.length">
          <a-table :columns="contractCols" :data-source="contracts" row-key="contract_id" size="small" :pagination="false">
            <template #bodyCell="{ column, record }">
              <template v-if="column.dataIndex === 'project_id'">
                <router-link :to="{ name: 'ContractDetail', query: { id: record.contract_id } }" class="text-blue-600 hover:underline">
                  {{ record.project_id }}
                </router-link>
              </template>
              <template v-else-if="column.dataIndex === 'contract_amount'">
                {{ fmtMoney(record.contract_amount) }} 万
              </template>
              <template v-else-if="column.dataIndex === 'invoice_total'">
                <span class="text-blue-600">{{ fmtMoney(record.invoice_total) }} 万</span>
              </template>
              <template v-else-if="column.dataIndex === 'payment_total'">
                <span class="text-green-600">{{ fmtMoney(record.payment_total) }} 万</span>
              </template>
            </template>
          </a-table>
        </template>
        <a-empty v-else description="暂无关联合同" />
      </a-card>
    </state-block>

    <!-- 新增发票弹窗 -->
    <a-modal
      v-model:open="addInvoiceVisible"
      title="新增供应商发票"
      :confirm-loading="invoiceSaving"
      @ok="saveInvoice"
      ok-text="保存"
      cancel-text="取消"
      width="600px"
    >
      <a-form :model="invoiceForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="项目编号" required>
              <a-input v-model:value="invoiceForm.project_id" placeholder="如：ZH02-202601001" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="发票号">
              <a-input v-model:value="invoiceForm.invoice_no" placeholder="可选" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="发票日期" required>
              <a-date-picker v-model:value="invoiceForm.invoice_date" value-format="YYYY-MM-DD" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="金额（元）" required>
              <a-input-number v-model:value="invoiceForm.amount" :precision="2" :min="0" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="税率（%）">
              <a-input-number v-model:value="invoiceForm.tax_rate" :precision="2" :min="0" :max="100" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态">
              <a-select v-model:value="invoiceForm.status">
                <a-select-option value="已开">已开</a-select-option>
                <a-select-option value="待开">待开</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="备注">
              <a-textarea v-model:value="invoiceForm.notes" :rows="2" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 新增付款弹窗 -->
    <a-modal
      v-model:open="addPaymentVisible"
      title="新增付款记录"
      :confirm-loading="paymentSaving"
      @ok="savePayment"
      ok-text="保存"
      cancel-text="取消"
      width="600px"
    >
      <a-form :model="paymentForm" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="项目编号" required>
              <a-input v-model:value="paymentForm.project_id" placeholder="如：ZH02-202601001" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="付款日期" required>
              <a-date-picker v-model:value="paymentForm.payment_date" value-format="YYYY-MM-DD" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="付款金额（元）" required>
              <a-input-number v-model:value="paymentForm.amount" :precision="2" :min="0" class="w-full" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="付款方式">
              <a-select v-model:value="paymentForm.payment_method">
                <a-select-option value="银行转账">银行转账</a-select-option>
                <a-select-option value="现金">现金</a-select-option>
                <a-select-option value="支票">支票</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="备注">
              <a-textarea v-model:value="paymentForm.notes" :rows="2" />
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
import { getSupplierDetailApi } from '#/api/suppliers'
import { createInvoiceApi } from '#/api/invoices'
import { requestClient } from '#/api/request'
import StateBlock from '#/components/state-block/index.vue'

const route = useRoute()
const router = useRouter()
const supplier = ref<any>(null)
const contracts = ref<any[]>([])
const invoices = ref<any[]>([])
const payments = ref<any[]>([])
const loading = ref(true)
const error = ref('')

// 新增发票
const addInvoiceVisible = ref(false)
const invoiceSaving = ref(false)
const invoiceForm = ref<Record<string, any>>({})

// 新增付款
const addPaymentVisible = ref(false)
const paymentSaving = ref(false)
const paymentForm = ref<Record<string, any>>({})

const contractCols = [
  { title: '项目编号', dataIndex: 'project_id', width: 160 },
  { title: '项目名称', dataIndex: 'project_name', minWidth: 200 },
  { title: '合同金额', dataIndex: 'contract_amount', width: 120, align: 'right' },
  { title: '已开票', dataIndex: 'invoice_total', width: 100, align: 'right' },
  { title: '已付款', dataIndex: 'payment_total', width: 100, align: 'right' },
  { title: '状态', dataIndex: 'status', width: 80 },
]

async function load() {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id || route.query.id
    const data: any = await getSupplierDetailApi(id as string)
    supplier.value = data.supplier ?? null
    contracts.value = data.contracts || []
    invoices.value = data.invoices || []
    payments.value = data.payments || []
    if (!supplier.value) error.value = '未找到该供应商'
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally {
    loading.value = false
  }
}

function openAddInvoice() {
  invoiceForm.value = {
    project_id: '',
    invoice_no: '',
    invoice_date: '',
    invoice_type: '供应商开票',
    direction: 'inbound',
    amount: null,
    tax_rate: null,
    status: '已开',
    notes: '',
  }
  addInvoiceVisible.value = true
}

async function saveInvoice() {
  if (!invoiceForm.value.project_id) {
    message.error('请输入项目编号')
    return
  }
  invoiceSaving.value = true
  try {
    await createInvoiceApi({
      ...invoiceForm.value,
      supplier_id: supplier.value?.supplier_id,
    })
    message.success('发票创建成功')
    addInvoiceVisible.value = false
    load()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.message || '未知错误'))
  } finally {
    invoiceSaving.value = false
  }
}

function openAddPayment() {
  paymentForm.value = {
    project_id: '',
    payment_date: '',
    amount: null,
    payment_method: '银行转账',
    status: '已完成',
    notes: '',
  }
  addPaymentVisible.value = true
}

async function savePayment() {
  if (!paymentForm.value.project_id) {
    message.error('请输入项目编号')
    return
  }
  if (!paymentForm.value.amount) {
    message.error('请输入付款金额')
    return
  }
  paymentSaving.value = true
  try {
    await requestClient.post('/api/supplier-payments', {
      ...paymentForm.value,
      supplier_id: supplier.value?.supplier_id,
    })
    message.success('付款记录创建成功')
    addPaymentVisible.value = false
    load()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.message || '未知错误'))
  } finally {
    paymentSaving.value = false
  }
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
  router.push({ name: 'SupplierList' })
}

function fmtMoney(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toFixed(2)
}

function invoiceStatusColor(status: string): string {
  const map: Record<string, string> = {
    '已开': 'blue',
    '已付款': 'green',
    '待开': 'orange',
  }
  return map[status] || 'default'
}

function paymentStatusColor(status: string): string {
  const map: Record<string, string> = {
    '已完成': 'green',
    '待支付': 'orange',
  }
  return map[status] || 'default'
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