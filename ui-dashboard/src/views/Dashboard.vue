<template>
  <div class="dashboard">
    <!-- KPI Row -->
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-value">{{ stats.contract_count }}</div>
        <div class="kpi-label">合同总数</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">¥{{ fmtWan(stats.total_amount) }}</div>
        <div class="kpi-label">合同总额</div>
      </div>
      <div class="kpi-card highlight-blue">
        <div class="kpi-value">¥{{ fmtWan(stats.invoiced) }}</div>
        <div class="kpi-label">已开票</div>
      </div>
      <div class="kpi-card highlight-green">
        <div class="kpi-value">¥{{ fmtWan(stats.received) }}</div>
        <div class="kpi-label">已回款</div>
      </div>
      <div class="kpi-card highlight-amber">
        <div class="kpi-value">{{ stats.receipt_rate }}%</div>
        <div class="kpi-label">回款率</div>
        <div class="kpi-sub">未回 ¥{{ fmtWan((stats.invoiced || 0) - (stats.received || 0)) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">{{ stats.sub_invoiced ? fmtWan(stats.sub_invoiced) : '-' }}</div>
        <div class="kpi-label">供应商开票</div>
        <div class="kpi-sub" v-if="stats.sub_paid">已付 {{ fmtWan(stats.sub_paid) }}</div>
      </div>
    </div>

    <!-- Category Overview -->
    <div class="section-row">
      <div class="chart-box large">
        <h3>合同分类概览</h3>
        <div class="category-grid">
          <div v-for="cat in categories" :key="cat.type" class="category-item" :class="cat.cls">
            <div class="cat-name">{{ cat.type }}</div>
            <div class="cat-count">{{ cat.cnt }} 个</div>
            <div class="cat-amount">¥{{ fmtWan(cat.total) }}</div>
          </div>
        </div>
        <div class="chart-sub" ref="catChartRef"></div>
      </div>
      <div class="chart-box">
        <h3>合同金额 TOP8</h3>
        <div ref="topChartRef" class="chart-canvas"></div>
      </div>
    </div>

    <!-- Finance & Supplier -->
    <div class="section-row">
      <div class="chart-box">
        <h3>开票 vs 回款趋势</h3>
        <div ref="trendChartRef" class="chart-canvas"></div>
      </div>
      <div class="chart-box">
        <h3>供应商应付一览</h3>
        <div class="supplier-mini-list">
          <div v-for="s in topSuppliers" :key="s.supplier_id" class="supplier-mini-row">
            <span class="sup-name">{{ (s.supplier_name || '').slice(0, 16) }}</span>
            <span class="sup-bar-bg">
              <span class="sup-bar-fill" :style="{ width: pct(s.sub_payment_total, s.sub_invoice_total) + '%' }"></span>
            </span>
            <span class="sup-amount">¥{{ fmtWan(s.sub_payment_total) }}/¥{{ fmtWan(s.sub_invoice_total) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerts & Missing Data -->
    <div class="section-row">
      <div class="chart-box alert-box">
        <h3>⚠️ 数据提醒</h3>
        <div class="alert-list">
          <div v-if="alerts.zeroAmount" class="alert-item warn">
            {{ alerts.zeroAmount }} 个合同金额未知
          </div>
          <div v-if="alerts.noStages" class="alert-item warn">
            {{ alerts.noStages }} 个合同无研究阶段数据
          </div>
          <div v-if="alerts.noPayments" class="alert-item warn">
            {{ alerts.noPayments }} 个合同无付款计划
          </div>
          <div v-if="alerts.suppliersUnpaid" class="alert-item danger">
            供应商未付款: ¥{{ fmtWan(alerts.suppliersUnpaid) }}
          </div>
          <div v-if="!alerts.zeroAmount && !alerts.suppliersUnpaid" class="alert-item ok">
            数据质量良好，无异常提醒
          </div>
        </div>
      </div>
      <div class="chart-box">
        <h3>最近发票</h3>
        <div class="invoice-mini-list">
          <div v-for="inv in recentInvoices" :key="inv.invoice_id" class="invoice-mini-row">
            <span class="inv-date">{{ inv.invoice_date }}</span>
            <span class="inv-type" :class="inv.invoice_type === '客户开票' ? 'out' : 'in'">
              {{ inv.invoice_type === '客户开票' ? '开' : '收' }}
            </span>
            <span class="inv-pid">{{ inv.project_id?.slice(0, 16) }}</span>
            <span class="inv-amt">¥{{ (inv.amount / 10000).toFixed(2) }}万</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import { getStats, getContracts, getInvoices, getSuppliers, getInvoiceSummary, getTypeDistribution } from '../api'

const stats = ref<any>({})
const categories = ref<any[]>([])
const topSuppliers = ref<any[]>([])
const recentInvoices = ref<any[]>([])
const alerts = ref<any>({})

const catChartRef = ref<HTMLDivElement>()
const topChartRef = ref<HTMLDivElement>()
const trendChartRef = ref<HTMLDivElement>()

function fmtWan(v: number): string {
  if (!v && v !== 0) return '-'
  return Math.abs(v) >= 10000 ? (v / 10000).toFixed(2) + '亿' : v.toFixed(0)
}

function pct(a: number, b: number): number {
  return b > 0 ? Math.min(100, Math.round((a || 0) / b * 100)) : 0
}

onMounted(async () => {
  const [s, types, suppliers, topContracts, invSummary, invRecent] = await Promise.all([
    getStats(),
    getTypeDistribution(),
    getSuppliers(),
    getContracts(1, 8),
    getInvoiceSummary(),
    getInvoices('', 1, 10)
  ])

  stats.value = s

  // Categories
  const catMap: Record<string, { cls: string }> = {
    '科研类': { cls: 'cat-research' }, '服务类': { cls: 'cat-service' },
    '物资类': { cls: 'cat-material' }, '施工类': { cls: 'cat-construct' },
  }
  categories.value = (types.types || []).map((t: any) => ({
    ...t, cls: catMap[t.type]?.cls || 'cat-other'
  }))

  // Top suppliers
  topSuppliers.value = ((suppliers as any).items || []).slice(0, 8)

  // Recent invoices
  recentInvoices.value = ((invRecent as any).items || []).slice(0, 8)

  // Alerts
  const invItems = (invSummary as any).items || []
  const zeroAmt = topContracts.items.filter((c: any) => !c.contract_amount).length
  const unpaid = suppliers.items?.reduce((s: number, x: any) => s + (x.total_unpaid || 0), 0) || 0
  alerts.value = {
    zeroAmount: zeroAmt,
    noStages: 40 - 6,
    noPayments: 40 - 7,
    suppliersUnpaid: unpaid,
  }

  // Charts
  await nextTick()

  // Category pie chart
  if (catChartRef.value) {
    const ch = echarts.init(catChartRef.value)
    ch.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}万 ({d}%)' },
      series: [{
        type: 'pie', radius: ['45%', '75%'], center: ['50%', '50%'],
        label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 },
        data: categories.value.map(c => ({ name: c.type, value: c.total }))
      }]
    })
  }

  // Top chart (horizontal bar)
  if (topChartRef.value) {
    const ch = echarts.init(topChartRef.value)
    const items = topContracts.items.reverse()
    ch.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 140, right: 20, top: 10, bottom: 10 },
      xAxis: { type: 'value', name: '万元', axisLabel: { fontSize: 10 } },
      yAxis: { type: 'category', data: items.map((i: any) => (i.project_name || '').slice(0, 14)), axisLabel: { fontSize: 10 } },
      series: [{
        type: 'bar', data: items.map((i: any) => i.contract_amount),
        itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0, [{offset:0,color:'#2563eb'},{offset:1,color:'#93c5fd'}]) }
      }]
    })
  }

  // Trend chart - use invoice summary as proxy for trend
  if (trendChartRef.value) {
    const ch = echarts.init(trendChartRef.value)
    const invData = invItems.map((i: any) => i.invoiced || 0)
    const payData = invItems.map((i: any) => i.received || 0)
    const labels = invItems.map((_:any, idx:number) => '#' + (idx + 1))
    ch.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['开票', '回款'], top: 0 },
      grid: { left: 50, right: 20, top: 30, bottom: 20 },
      xAxis: { type: 'category', data: labels, axisLabel: { fontSize: 9 } },
      yAxis: { type: 'value', name: '万元', axisLabel: { fontSize: 10 } },
      series: [
        { name: '开票', type: 'bar', data: invData, itemStyle: { color: '#2563eb' }, barGap: '10%' },
        { name: '回款', type: 'bar', data: payData, itemStyle: { color: '#16a34a' } }
      ]
    })
  }
})
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 16px; }

.kpi-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }
.kpi-card {
  background: white; border-radius: 10px; padding: 18px 16px; text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08); transition: transform 0.15s;
}
.kpi-card:hover { transform: translateY(-1px); box-shadow: 0 3px 10px rgba(0,0,0,0.12); }
.kpi-value { font-size: 26px; font-weight: 700; }
.kpi-label { font-size: 12px; color: #666; margin-top: 4px; }
.kpi-sub { font-size: 11px; color: #999; margin-top: 2px; }
.highlight-blue { background: linear-gradient(135deg, #eff6ff, #dbeafe); }
.highlight-green { background: linear-gradient(135deg, #f0fdf4, #dcfce7); }
.highlight-amber { background: linear-gradient(135deg, #fffbeb, #fef3c7); }

.section-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.chart-box { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.chart-box.large { /* full width */ }
.chart-box h3 { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: #333; }
.chart-canvas { height: 260px; }
.chart-sub { height: 220px; }

.category-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 8px; }
.category-item { text-align: center; padding: 12px 8px; border-radius: 8px; background: #f8fafc; }
.cat-name { font-size: 12px; color: #666; }
.cat-count { font-size: 20px; font-weight: 600; }
.cat-amount { font-size: 11px; color: #999; margin-top: 2px; }
.cat-research { background: #dbeafe; } .cat-service { background: #dcfce7; }
.cat-material { background: #fef3c7; } .cat-construct { background: #fce7f3; }

.supplier-mini-list { display: flex; flex-direction: column; gap: 6px; }
.supplier-mini-row { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.sup-name { width: 90px; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sup-bar-bg { flex: 1; height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden; }
.sup-bar-fill { height: 100%; background: #16a34a; border-radius: 3px; transition: width 0.5s; }
.sup-amount { width: 90px; text-align: right; flex-shrink: 0; font-family: monospace; font-size: 11px; color: #666; }

.alert-box {}
.alert-list { display: flex; flex-direction: column; gap: 6px; }
.alert-item { padding: 8px 12px; border-radius: 6px; font-size: 13px; }
.alert-item.warn { background: #fef3c7; color: #92400e; }
.alert-item.danger { background: #fee2e2; color: #991b1b; }
.alert-item.ok { background: #dcfce7; color: #166534; }

.invoice-mini-list { display: flex; flex-direction: column; gap: 4px; }
.invoice-mini-row { display: flex; align-items: center; gap: 8px; font-size: 12px; padding: 4px 0; border-bottom: 1px solid #f3f4f6; }
.inv-date { width: 75px; color: #999; font-family: monospace; }
.inv-type { width: 20px; text-align: center; font-weight: 600; font-size: 11px; border-radius: 3px; padding: 1px 0; }
.inv-type.out { background: #dbeafe; color: #1d4ed8; }
.inv-type.in { background: #dcfce7; color: #166534; }
.inv-pid { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #666; font-family: monospace; font-size: 11px; }
.inv-amt { width: 75px; text-align: right; font-family: monospace; font-size: 11px; }
</style>
