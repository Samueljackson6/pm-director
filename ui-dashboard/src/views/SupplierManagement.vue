<template>
  <div class="supplier-page">
    <div class="page-header">
      <h2>供应商管理</h2>
      <span class="count">{{ suppliers.length }} 家供应商</span>
    </div>
    <div class="supplier-grid">
      <div v-for="s in suppliers" :key="s.supplier_id" class="supplier-card" @click="selectSupplier(s)">
        <div class="card-header">
          <span class="supplier-name">{{ (s.supplier_name || '').slice(0, 20) }}</span>
          <span class="contract-count">{{ s.contract_count }}个项目</span>
        </div>
        <div class="card-amount">¥{{ fmtWan(s.total_contract_amount) }}万</div>
        <div class="card-progress">
          <div class="progress-row">
            <span>开票</span>
            <span class="progress-bar-bg"><span class="progress-bar-fill blue" :style="{width:pct(s.total_invoiced,s.total_contract_amount)+'%'}"></span></span>
            <span>{{ pct(s.total_invoiced, s.total_contract_amount) }}%</span>
          </div>
          <div class="progress-row">
            <span>付款</span>
            <span class="progress-bar-bg"><span class="progress-bar-fill green" :style="{width:pct(s.total_paid,s.total_contract_amount)+'%'}"></span></span>
            <span>{{ pct(s.total_paid, s.total_contract_amount) }}%</span>
          </div>
        </div>
        <div v-if="s.total_unpaid > 0" class="card-unpaid">未付: ¥{{ fmtWan(s.total_unpaid) }}万</div>
      </div>
    </div>

    <!-- Detail panel -->
    <div v-if="selected" class="detail-panel">
      <div class="detail-header">
        <h3>{{ selected.supplier_name }}</h3>
        <button @click="selected=null" class="close-btn">✕</button>
      </div>
      <div class="detail-stats">
        <div class="dstat"><label>合同总额</label><span>¥{{ fmtWan(selected.total_contract_amount) }}万</span></div>
        <div class="dstat"><label>已开票</label><span>¥{{ fmtWan(selected.total_invoiced) }}万</span></div>
        <div class="dstat"><label>已付款</label><span>¥{{ fmtWan(selected.total_paid) }}万</span></div>
        <div class="dstat warn"><label>未付款</label><span>¥{{ fmtWan(selected.total_unpaid) }}万</span></div>
      </div>
      <h4 style="margin:16px 0 8px">关联合同</h4>
      <div v-if="detailContracts.length" class="detail-contracts">
        <div v-for="sc in detailContracts" :key="sc.project_id" class="dc-row">
          <span class="dc-pid">{{ sc.project_id }}</span>
          <span class="dc-name">{{ (sc.project_name || '').slice(0, 24) }}</span>
          <span class="dc-amount">¥{{ fmtWan(sc.contract_amount) }}万</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSuppliers, getSupplier } from '../api'

const suppliers = ref<any[]>([])
const selected = ref<any>(null)
const detailContracts = ref<any[]>([])

function fmtWan(v: number): string { return v ? (v/10000).toFixed(2) : '0' }
function pct(a: number, b: number): number { return b > 0 ? Math.round(a / b * 100) : 0 }

onMounted(async () => {
  const res = await getSuppliers()
  suppliers.value = res.items || []
})

async function selectSupplier(s: any) {
  selected.value = s
  if (s.supplier_id) {
    const res = await getSupplier(s.supplier_id)
    detailContracts.value = res.contracts || []
  }
}
</script>

<style scoped>
.supplier-page { background: white; border-radius: 10px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { font-size: 18px; font-weight: 600; }
.count { font-size: 13px; color: #666; }
.supplier-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.supplier-card {
  border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; cursor: pointer;
  transition: all 0.15s;
}
.supplier-card:hover { border-color: #2563eb; box-shadow: 0 2px 8px rgba(37,99,235,0.1); }
.card-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.supplier-name { font-weight: 600; font-size: 14px; }
.contract-count { font-size: 11px; color: #999; }
.card-amount { font-size: 22px; font-weight: 700; color: #2563eb; margin-bottom: 12px; }
.card-progress { display: flex; flex-direction: column; gap: 6px; }
.progress-row { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.progress-row span:first-child { width: 30px; color: #999; }
.progress-row span:last-child { width: 30px; text-align: right; color: #666; }
.progress-bar-bg { flex: 1; height: 4px; background: #e5e7eb; border-radius: 2px; overflow: hidden; }
.progress-bar-fill { height: 100%; border-radius: 2px; }
.progress-bar-fill.blue { background: #2563eb; }
.progress-bar-fill.green { background: #16a34a; }
.card-unpaid { margin-top: 8px; font-size: 12px; color: #dc2626; }
.detail-panel {
  margin-top: 20px; border-top: 2px solid #e5e7eb; padding-top: 16px;
}
.detail-header { display: flex; justify-content: space-between; align-items: center; }
.detail-header h3 { font-size: 16px; }
.close-btn { border: none; background: none; font-size: 18px; cursor: pointer; color: #999; }
.detail-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 12px; }
.dstat { text-align: center; padding: 12px 8px; background: #f8fafc; border-radius: 8px; }
.dstat label { display: block; font-size: 12px; color: #999; margin-bottom: 4px; }
.dstat span { font-size: 16px; font-weight: 600; }
.dstat.warn span { color: #dc2626; }
.detail-contracts { display: flex; flex-direction: column; gap: 6px; }
.dc-row { display: flex; gap: 12px; align-items: center; padding: 8px; background: #f8fafc; border-radius: 6px; font-size: 13px; }
.dc-pid { font-family: monospace; font-size: 12px; color: #666; min-width: 160px; }
.dc-name { flex: 1; }
.dc-amount { font-weight: 600; color: #2563eb; }
</style>
