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
          <span class="text-lg">←</span>
        </a-button>
        <div>
          <h2 class="text-xl font-semibold text-gray-800">回款详情</h2>
          <div v-if="receipt" class="text-sm text-gray-500 mt-0.5">
            {{ receipt.receipt_no || '回款 #' + receipt.receipt_id }}
          </div>
        </div>
      </div>
      <a-button type="primary" size="small" ghost @click="editReceipt">编辑</a-button>
    </div>

    <!-- 三态 -->
    <state-block :loading="loading" :error="error" error-title="回款详情加载失败" @retry="load">
      <!-- KPI 指标 -->
      <div v-if="receipt" class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">回款金额（元）</div>
          <div class="text-2xl font-bold text-green-600">{{ fmtMoney(receipt.amount) }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">已匹配金额</div>
          <div class="text-2xl font-bold text-blue-600">{{ fmtMoney(matchedAmount) }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">未匹配金额</div>
          <div class="text-2xl font-bold text-orange-600">{{ fmtMoney(receipt.amount - matchedAmount) }}</div>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
          <div class="text-xs text-gray-400 mb-1">匹配状态</div>
          <div class="text-lg font-bold">
            <a-tag v-if="matchedAmount >= receipt.amount" color="success" class="rounded-full">完全匹配</a-tag>
            <a-tag v-else-if="matchedAmount > 0" color="warning" class="rounded-full">部分匹配</a-tag>
            <a-tag v-else color="default" class="rounded-full">未匹配</a-tag>
          </div>
        </div>
      </div>

      <!-- 基本信息 -->
      <a-card v-if="receipt" title="基本信息" class="rounded-lg mb-4" size="small">
        <a-descriptions :column="2" size="small" bordered>
          <a-descriptions-item label="回款单号">{{ receipt.receipt_no || '-' }}</a-descriptions-item>
          <a-descriptions-item label="回款日期">{{ receipt.receipt_date || '-' }}</a-descriptions-item>
          <a-descriptions-item label="项目编号" :span="2">
            <router-link :to="{ name: 'ContractDetail', query: { id: receipt.project_id } }" class="text-blue-600 hover:underline">
              {{ receipt.project_id }}
            </router-link>
          </a-descriptions-item>
          <a-descriptions-item label="付款方">{{ receipt.payer_name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="收款方式">{{ receipt.receipt_method || '-' }}</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="receipt.status === '已收到' ? 'success' : 'default'">{{ receipt.status }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ receipt.created_at || '-' }}</a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">{{ receipt.notes || '-' }}</a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 关联发票 -->
      <a-card title="关联发票" class="rounded-lg" size="small">
        <template #extra>
          <a-button type="link" size="small" @click="showLinkInvoice = true">+ 关联发票</a-button>
        </template>
        <template v-if="linkedInvoices.length">
          <div class="space-y-2">
            <div
              v-for="inv in linkedInvoices"
              :key="inv.invoice_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-blue-50/50 cursor-pointer"
              @click="router.push({ name: 'CustomerInvoiceDetail', query: { id: inv.invoice_id } })"
            >
              <div class="flex items-center gap-3">
                <span class="text-2xl">📄</span>
                <div>
                  <div class="font-medium text-sm">{{ inv.invoice_no || '发票 #' + inv.invoice_id }}</div>
                  <div class="text-xs text-gray-400">{{ inv.invoice_date }} · {{ inv.project_id }}</div>
                </div>
              </div>
              <div class="text-right">
                <div class="font-semibold text-sm text-blue-600">{{ fmtMoney(inv.amount) }} 元</div>
                <a-button type="link" size="small" danger @click.stop="unlinkInvoice(inv)">取消关联</a-button>
              </div>
            </div>
          </div>
        </template>
        <a-empty v-else description="暂无关联发票" />
      </a-card>
    </state-block>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getReceiptDetailApi } from '#/api/receipts'
import { requestClient } from '#/api/request'
import StateBlock from '#/components/state-block/index.vue'

const route = useRoute()
const router = useRouter()
const receipt = ref<any>(null)
const linkedInvoices = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const showLinkInvoice = ref(false)

const matchedAmount = computed(() => {
  return linkedInvoices.value.reduce((sum, inv) => sum + (inv.link_amount || inv.amount || 0), 0)
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const id = route.query.id
    const data: any = await getReceiptDetailApi(Number(id))
    receipt.value = data.receipt ?? null
    linkedInvoices.value = data.linked_invoices ?? []
    if (!receipt.value) error.value = '未找到该回款记录'
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push({ name: 'CustomerReceipts' })
}

function editReceipt() {
  message.info('编辑功能开发中')
}

async function unlinkInvoice(inv: any) {
  try {
    await requestClient.delete(`/api/receipts/${receipt.value.receipt_id}/invoices/${inv.invoice_id}`)
    message.success('已取消关联')
    load()
  } catch (e: any) {
    message.error('操作失败: ' + (e?.message || '未知错误'))
  }
}

function fmtMoney(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toFixed(2)
}

onMounted(load)

watch(
  () => route.query.id,
  (newId, oldId) => {
    if (newId && newId !== oldId) load()
  },
  { immediate: false }
)
</script>

<style scoped>
.text-lg {
  font-size: 1.125rem;
}
</style>