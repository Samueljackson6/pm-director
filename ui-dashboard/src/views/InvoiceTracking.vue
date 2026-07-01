<template>
  <div class="invoice-page">
    <div class="page-header">
      <h2>发票追踪</h2>
      <div class="header-stats">
        <span>开票: ¥{{ fmtWan(summary.invoiced) }}</span>
        <span>回款: ¥{{ fmtWan(summary.received) }}</span>
        <span>未回: ¥{{ fmtWan((summary.invoiced||0) - (summary.received||0)) }}</span>
      </div>
    </div>

    <div class="invoice-table-wrap">
      <table class="invoice-table">
        <thead>
          <tr><th>日期</th><th>类型</th><th>项目编号</th><th>金额(万)</th><th>状态</th></tr>
        </thead>
        <tbody>
          <tr v-for="inv in invoices" :key="inv.invoice_id" :class="inv.invoice_type === '客户回款' ? 'row-payment' : ''">
            <td>{{ inv.invoice_date }}</td>
            <td><span class="tag" :class="inv.invoice_type==='客户开票'?'out':'in'">{{ inv.invoice_type==='客户开票'?'开票':'回款' }}</span></td>
            <td class="mono">{{ inv.project_id }}</td>
            <td class="mono amount">{{ (inv.amount / 10000).toFixed(2) }}</td>
            <td>{{ inv.notes || inv.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pager">
      <button :disabled="page<=1" @click="page--; load()">上一页</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page>=totalPages" @click="page++; load()">下一页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getInvoices, getInvoiceSummary } from '../api'

const invoices = ref<any[]>([])
const summary = ref<any>({})
const page = ref(1)
const pageSize = 50
const total = ref(0)
const totalPages = computed(() => Math.ceil(total.value / pageSize))

function fmtWan(v: number): string { return v ? v.toFixed(0) : '-' }

onMounted(async () => {
  const [invRes, sumRes] = await Promise.all([
    getInvoices('', page.value, pageSize),
    getInvoiceSummary()
  ])
  invoices.value = invRes.items
  total.value = invRes.total
  const items = sumRes.items || []
  summary.value = {
    invoiced: items.reduce((s: number, i: any) => s + (i.invoiced || 0), 0),
    received: items.reduce((s: number, i: any) => s + (i.received || 0), 0),
  }
})

async function load() {
  const res = await getInvoices('', page.value, pageSize)
  invoices.value = res.items
  total.value = res.total
}
</script>

<style scoped>
.invoice-page { background: white; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { font-size: 18px; font-weight: 600; }
.header-stats { display: flex; gap: 20px; font-size: 13px; color: #666; }
.invoice-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.invoice-table th { text-align: left; padding: 10px 8px; border-bottom: 2px solid #e5e7eb; color: #666; font-weight: 600; }
.invoice-table td { padding: 10px 8px; border-bottom: 1px solid #f3f4f6; }
.row-payment { background: #f0fdf4; }
.mono { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; }
.amount { text-align: right; }
.tag { padding: 2px 8px; border-radius: 10px; font-size: 11px; }
.tag.out { background: #dbeafe; color: #1d4ed8; }
.tag.in { background: #dcfce7; color: #166534; }
.pager { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 16px; font-size: 13px; }
.pager button { padding: 6px 16px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; }
.pager button:disabled { opacity: 0.5; }
</style>
