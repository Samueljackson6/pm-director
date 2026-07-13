<template>
  <div class="p-6 bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-4">
        <a-button type="text" class="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-200 hover:bg-gray-100" @click="goBack">
          <span class="text-lg">←</span>
        </a-button>
        <div>
          <h2 class="text-xl font-semibold text-gray-800">付款详情</h2>
          <div v-if="payment" class="text-sm text-gray-500 mt-0.5">付款 #{{ payment.payment_id }}</div>
        </div>
      </div>
      <a-button type="primary" size="small" ghost @click="editPayment">编辑</a-button>
    </div>

    <state-block :loading="loading" :error="error" error-title="付款详情加载失败" @retry="load">
      <!-- KPI 指标 -->
      <div v-if="payment" class="grid grid-cols-3 gap-3 mb-4">
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">付款金额（元）</div>
          <div class="text-2xl font-bold text-blue-600">{{ fmtMoney(payment.amount) }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">供应商</div>
          <div class="text-lg font-bold text-gray-800">{{ payment.supplier_name || payment.supplier_id || '-' }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">状态</div>
          <div class="text-lg font-bold">
            <a-tag :color="payment.status === '已完成' ? 'success' : 'default'" class="rounded-full">{{ payment.status }}</a-tag>
          </div>
        </div>
      </div>

      <!-- 基本信息 -->
      <a-card v-if="payment" title="基本信息" class="rounded-lg mb-4" size="small">
        <a-descriptions :column="2" size="small" bordered>
          <a-descriptions-item label="供应商编号">{{ payment.supplier_id || '-' }}</a-descriptions-item>
          <a-descriptions-item label="供应商名称">{{ payment.supplier_name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="项目编号" :span="2">
            <router-link :to="{ name: 'ContractDetail', query: { id: payment.project_id } }" class="text-blue-600 hover:underline">{{ payment.project_id }}</router-link>
          </a-descriptions-item>
          <a-descriptions-item label="付款日期">{{ payment.payment_date || '-' }}</a-descriptions-item>
          <a-descriptions-item label="付款方式">{{ payment.payment_method || '-' }}</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="payment.status === '已完成' ? 'success' : 'default'">{{ payment.status }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ payment.created_at || '-' }}</a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">{{ payment.notes || '-' }}</a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 关联发票 -->
      <a-card v-if="payment" title="关联发票" class="rounded-lg" size="small">
        <template v-if="linkedInvoices.length">
          <div class="space-y-2">
            <div v-for="inv in linkedInvoices" :key="inv.invoice_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-blue-50/50 cursor-pointer"
              @click="router.push({ name: 'SupplierInvoiceDetail', query: { id: inv.invoice_id } })">
              <div class="flex items-center gap-3">
                <span class="text-2xl">📄</span>
                <div>
                  <div class="font-medium text-sm">{{ inv.invoice_no || '发票 #' + inv.invoice_id }}</div>
                  <div class="text-xs text-gray-400">{{ inv.invoice_date }} · {{ inv.project_id }}</div>
                </div>
              </div>
              <div class="font-semibold text-sm text-blue-600">{{ fmtMoney(inv.amount) }} 元</div>
            </div>
          </div>
        </template>
        <a-empty v-else description="暂无关联发票" />
      </a-card>
    </state-block>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getSupplierPaymentDetailApi } from '#/api/supplier-payments'
import StateBlock from '#/components/state-block/index.vue'

const route = useRoute()
const router = useRouter()
const payment = ref<any>(null)
const linkedInvoices = ref<any[]>([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true; error.value = ''
  try {
    const id = route.query.id
    const data: any = await getSupplierPaymentDetailApi(Number(id))
    payment.value = data.payment ?? null
    linkedInvoices.value = data.linked_invoices ?? []
    if (!payment.value) error.value = '未找到该付款记录'
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally { loading.value = false }
}

function goBack() { router.push({ name: 'SupplierPayments' }) }
function editPayment() { message.info('编辑功能开发中') }
function fmtMoney(n: number | null | undefined): string { return n == null ? '0.00' : n.toFixed(2) }

onMounted(load)
watch(() => route.query.id, (n, o) => { if (n && n !== o) load() })
</script>

<style scoped>
.text-lg { font-size: 1.125rem; }
</style>
