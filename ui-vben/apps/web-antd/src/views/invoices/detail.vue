<template>
  <div class="p-4">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold">发票详情</h2>
      <a-button @click="goBack">返回列表</a-button>
    </div>
    <state-block :loading="loading" :error="error" error-title="发票详情加载失败" empty-text="未找到该发票" @retry="load">
      <a-card title="基本信息" size="small" v-if="inv">
        <a-descriptions :column="2" size="small" bordered>
          <a-descriptions-item label="发票编号" :span="2">{{ inv.invoice_no || '-' }}</a-descriptions-item>
          <a-descriptions-item label="项目编号" :span="2">{{ inv.project_id }}</a-descriptions-item>
          <a-descriptions-item label="发票类型">{{ inv.invoice_type }}</a-descriptions-item>
          <a-descriptions-item label="方向">{{ inv.direction === 'outbound' ? '客户发票' : '供应商发票' }}</a-descriptions-item>
          <a-descriptions-item label="金额">{{ (inv.amount || 0).toFixed(2) }} 万元</a-descriptions-item>
          <a-descriptions-item label="税率">{{ inv.tax_rate ? (inv.tax_rate * 100).toFixed(0) + '%' : '-' }}</a-descriptions-item>
          <a-descriptions-item label="税额">{{ (inv.tax_amount || 0).toFixed(2) }}</a-descriptions-item>
          <a-descriptions-item label="价税合计">{{ (inv.total_with_tax || 0).toFixed(2) }}</a-descriptions-item>
          <a-descriptions-item label="开票日期">{{ inv.invoice_date || '-' }}</a-descriptions-item>
          <a-descriptions-item label="状态">{{ inv.status }}</a-descriptions-item>
          <a-descriptions-item label="来源">{{ inv.source || '-' }}</a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">{{ inv.notes || '-' }}</a-descriptions-item>
        </a-descriptions>
      </a-card>
    </state-block>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getInvoiceDetailApi } from '#/api/invoices'
import StateBlock from '#/components/state-block/index.vue'

const route = useRoute()
const router = useRouter()
const inv = ref<any>(null)
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data: any = await getInvoiceDetailApi(Number(route.query.id))
    inv.value = data.invoice ?? null
    if (!inv.value) error.value = '未找到该发票'
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally {
    loading.value = false
  }
}

onMounted(load)

function goBack() {
  router.push({ name: 'InvoiceList' })
}
</script>
