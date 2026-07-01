<template>
  <div v-if="loading" class="loading">加载中...</div>
  <div v-else class="detail">
    <button class="back-btn" @click="$router.push('/contracts')">← 返回</button>
    
    <div class="detail-header">
      <div>
        <h2>{{ detail?.contract?.project_name }}</h2>
        <div class="header-meta">
          <span class="meta-item">{{ detail?.contract?.contract_id }}</span>
          <span :class="'type-tag ' + (detail?.contract?.project_type||'')">{{ detail?.contract?.project_type }}</span>
        </div>
      </div>
      <div class="amount-display">
        <div class="amount-value">¥{{ detail?.contract?.contract_amount?.toFixed(2) }}<span class="amount-unit">万</span></div>
        <div class="amount-label">合同金额</div>
      </div>
    </div>

    <div class="info-grid">
      <div class="info-card">
        <h3>基本信息</h3>
        <div class="info-row"><label>甲方</label><span>{{ detail?.contract?.party_a?.replace(/[（(].*[)）]/g,'') || '-' }}</span></div>
        <div class="info-row"><label>乙方</label><span>{{ detail?.contract?.party_b?.replace(/[（(].*[)）]/g,'') || '-' }}</span></div>
        <div class="info-row"><label>签订日期</label><span>{{ detail?.contract?.sign_date || '-' }}</span></div>
        <div class="info-row"><label>类型</label><span>{{ detail?.contract?.project_type }}</span></div>
      </div>
      <div class="info-card">
        <h3>财务概况</h3>
        <div class="info-row"><label>已开票</label><span>¥{{ (detail?.finance?.invoice_total || 0).toFixed(2) }}万</span></div>
        <div class="info-row"><label>已回款</label><span>¥{{ (detail?.finance?.payment_total || 0).toFixed(2) }}万</span></div>
        <div class="info-row"><label>未回款</label><span>¥{{ (detail?.finance?.payment_unreceived || 0).toFixed(2) }}万</span></div>
        <div v-if="detail?.finance?.subcontractor" class="info-row"><label>供应商</label><span>{{ detail?.finance?.subcontractor }}</span></div>
      </div>
    </div>

    <div v-if="detail?.stages?.length" class="section">
      <h3>研究阶段 ({{ detail.stages.length }})</h3>
      <div class="stage-list">
        <div v-for="s in detail.stages" :key="s.stage_id" class="stage-item">
          <div class="stage-header">
            <span class="stage-num">阶段 {{ s.stage_number }}</span>
            <span :class="'stage-status ' + (s.status||'pending')">{{ statusMap[s.status||'pending'] }}</span>
          </div>
          <div class="stage-content">{{ s.stage_name || s.acceptance_criteria?.slice(0, 100) }}</div>
          <div v-if="s.start_time" class="stage-time">⏱ {{ s.start_time }}</div>
        </div>
      </div>
    </div>

    <div v-if="detail?.payments?.length" class="section">
      <h3>付款计划 ({{ detail.payments.length }})</h3>
      <div class="payment-list">
        <div v-for="p in detail.payments" :key="p.payment_id" class="payment-item">
          <div class="payment-left">
            <div class="payment-cond">{{ p.payment_condition || '付款' }}</div>
            <div v-if="p.payment_date" class="payment-date">📅 {{ p.payment_date }}</div>
          </div>
          <div class="payment-right">
            <div class="payment-amount">¥{{ (p.planned_amount || 0).toFixed(2) }}万</div>
            <div :class="'payment-status ' + (p.status||'pending')">{{ statusMap[p.status||'pending'] }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="detail?.deliverables?.length" class="section">
      <h3>交付物 ({{ detail.deliverables.length }})</h3>
      <div class="deliverable-list">
        <span v-for="d in detail.deliverables" :key="d.deliverable_id" class="deliverable-tag">
          {{ d.deliverable_name }} {{ d.quantity > 1 ? '×'+d.quantity : '' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getContract } from '../api'

const route = useRoute()
const detail = ref<any>(null)
const loading = ref(true)

const statusMap: Record<string, string> = { pending: '待开始', active: '进行中', completed: '已完成', delayed: '已延期' }

onMounted(async () => {
  detail.value = await getContract(route.params.id as string)
  loading.value = false
})
</script>

<style scoped>
.detail { display: flex; flex-direction: column; gap: 20px; }
.loading { text-align: center; padding: 60px; color: #999; }
.back-btn { padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px; background: white; cursor: pointer; font-size: 13px; align-self: flex-start; }
.back-btn:hover { background: #f3f4f6; }
.detail-header { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: flex-start; }
.detail-header h2 { font-size: 20px; font-weight: 600; margin-bottom: 8px; }
.header-meta { display: flex; gap: 12px; align-items: center; }
.meta-item { font-family: monospace; font-size: 12px; color: #666; }
.type-tag { padding: 2px 10px; border-radius: 12px; font-size: 12px; }
.type-tag.科研类 { background: #dbeafe; color: #1d4ed8; }
.type-tag.服务类 { background: #d1fae5; color: #047857; }
.amount-display { text-align: right; }
.amount-value { font-size: 28px; font-weight: 700; color: #2563eb; }
.amount-unit { font-size: 14px; font-weight: 400; color: #666; }
.amount-label { font-size: 12px; color: #999; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.info-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.info-card h3 { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: #333; }
.info-row { display: flex; padding: 6px 0; font-size: 13px; }
.info-row label { width: 80px; color: #666; flex-shrink: 0; }
.section { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.section h3 { font-size: 15px; font-weight: 600; margin-bottom: 16px; }
.stage-list, .payment-list { display: flex; flex-direction: column; gap: 12px; }
.stage-item { border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }
.stage-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.stage-num { font-weight: 600; font-size: 13px; }
.stage-status { font-size: 12px; padding: 2px 8px; border-radius: 10px; }
.stage-status.pending { background: #f3f4f6; color: #666; }
.stage-status.completed { background: #d1fae5; color: #047857; }
.stage-content { font-size: 13px; color: #444; line-height: 1.5; }
.stage-time { font-size: 12px; color: #999; margin-top: 6px; }
.payment-item { display: flex; justify-content: space-between; align-items: center; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }
.payment-cond { font-size: 13px; color: #444; }
.payment-date { font-size: 12px; color: #999; margin-top: 4px; }
.payment-amount { font-size: 16px; font-weight: 600; color: #2563eb; text-align: right; }
.payment-status { font-size: 12px; padding: 2px 8px; border-radius: 10px; text-align: center; margin-top: 4px; }
.payment-status.pending { background: #f3f4f6; color: #666; }
.deliverable-list { display: flex; flex-wrap: wrap; gap: 8px; }
.deliverable-tag { background: #f3f4f6; padding: 6px 14px; border-radius: 16px; font-size: 13px; color: #444; }
</style>
