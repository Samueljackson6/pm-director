<template>
  <div class="p-4">
    <a-card title="合同详情" :bordered="false" :loading="loading">
      <template #extra>
        <a-space>
          <a-button @click="goBack">返回列表</a-button>
          <a-button type="primary" :disabled="!c">编辑</a-button>
          <a-button @click="handleNewContract">新增</a-button>
        </a-space>
      </template>

      <!-- 基本信息 -->
      <a-descriptions v-if="c" :column="2" size="small" bordered>
        <a-descriptions-item label="合同编号" :span="2">{{ c.contract_id }}</a-descriptions-item>
        <a-descriptions-item label="项目名称" :span="2">{{ c.project_name }}</a-descriptions-item>
        <a-descriptions-item label="合同金额">{{ formatWanYuan(c.contract_amount) }} 万元</a-descriptions-item>
        <a-descriptions-item label="项目类型">{{ c.project_type }}</a-descriptions-item>
        <a-descriptions-item label="甲方">{{ clean(c.party_a) }}</a-descriptions-item>
        <a-descriptions-item label="乙方">{{ clean(c.party_b) }}</a-descriptions-item>
        <a-descriptions-item label="签订日期">{{ c.sign_date || '-' }}</a-descriptions-item>
        <a-descriptions-item label="服务期限">{{ c.service_period || '-' }}</a-descriptions-item>
      </a-descriptions>

      <!-- 阶段进度（甘特图） -->
      <a-card title="阶段进度" size="small" class="mt-4" v-if="stages.length">
        <a-table
          :columns="ganttCols"
          :data-source="stages"
          row-key="stage_id"
          size="small"
          :pagination="false"
          :scroll="{ x: 800 }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'duration'">
              {{ computeDuration(record) }}
            </template>
            <template v-else-if="column.dataIndex === 'progress'">
              <a-progress :percent="computeProgress(record)" size="small" />
            </template>
            <template v-else-if="column.dataIndex === 'status'">
              <a-tag :color="timelineColor(record.status)">{{ statusLabel(record.status) }}</a-tag>
            </template>
          </template>
        </a-table>
      </a-card>

      <!-- 付款时间线 -->
      <a-card title="付款时间线" size="small" class="mt-4" v-if="payments.length">
        <a-timeline>
          <a-timeline-item
            v-for="p in payments"
            :key="p.payment_id"
            :color="timelineColor(p.status)"
          >
            <div style="font-weight:500">{{ p.payment_stage }}</div>
            <div>计划金额：{{ formatWanYuan(p.planned_amount) }} 万元</div>
            <div v-if="p.actual_amount != null">实际金额：{{ formatWanYuan(p.actual_amount) }} 万元</div>
            <div style="color:#999">{{ p.payment_condition }}</div>
          </a-timeline-item>
        </a-timeline>
      </a-card>

      <!-- 付款计划 -->
      <a-card title="付款计划" size="small" class="mt-4" v-if="payments.length">
        <a-table :columns="payCols" :data-source="payments" row-key="payment_id" size="small" :pagination="false" />
      </a-card>

      <!-- 交付物 -->
      <a-card title="交付物" size="small" class="mt-4" v-if="deliverables.length">
        <a-table :columns="deliverableCols" :data-source="deliverables" row-key="deliverable_id" size="small" :pagination="false" />
      </a-card>

      <!-- 合同条款（页尾） -->
      <a-card title="合同条款" size="small" class="mt-4" v-if="clauses.length">
        <a-table :columns="clauseCols" :data-source="clauses" row-key="clause_id" size="small" :pagination="false" />
      </a-card>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContractDetailApi } from '#/api/contracts'
import { formatWanYuan } from '@/utils/formatAmount'

const route = useRoute()
const router = useRouter()
const detail = ref<any>(null)
const loading = ref(true)

const c = computed(() => detail.value?.contract ?? null)
const stages = computed(() => detail.value?.stages ?? [])
const payments = computed(() => detail.value?.payments ?? [])
const deliverables = computed(() => detail.value?.deliverables ?? [])
const clauses = computed(() => detail.value?.clauses ?? [])

const ganttCols = [
  { title: '阶段名称', dataIndex: 'stage_name', width: 200 },
  { title: '开始时间', dataIndex: 'start_time', width: 120 },
  { title: '结束时间', dataIndex: 'end_time', width: 120 },
  { title: '工期', dataIndex: 'duration', width: 80 },
  { title: '进度', dataIndex: 'progress', width: 150 },
  { title: '状态', dataIndex: 'status', width: 100 },
]

const payCols = [
  { title: '付款阶段', dataIndex: 'payment_stage', width: 100 },
  { title: '付款条件', dataIndex: 'payment_condition', minWidth: 200 },
  { title: '计划金额', dataIndex: 'planned_amount', width: 120, align: 'right' },
  { title: '状态', dataIndex: 'status', width: 80 },
]

const deliverableCols = [
  { title: '交付物名称', dataIndex: 'deliverable_name', minWidth: 200 },
  { title: '类型', dataIndex: 'deliverable_type', width: 100 },
  { title: '数量', dataIndex: 'quantity', width: 60 },
  { title: '计划日期', dataIndex: 'planned_date', width: 110 },
  { title: '状态', dataIndex: 'status', width: 80 },
]

const clauseCols = [
  { title: '条款类别', dataIndex: 'clause_category', width: 120 },
  { title: '触发类型', dataIndex: 'trigger_type', width: 100 },
  { title: '费率(%)', dataIndex: 'rate_pct', width: 80, align: 'right' },
  { title: '阈值天数', dataIndex: 'threshold_days', width: 80, align: 'right' },
  { title: '条款内容', dataIndex: 'clause_text', minWidth: 300 },
]

function computeDuration(stage: any): string {
  if (!stage.start_time || !stage.end_time) return '-'
  try {
    const start = new Date(stage.start_time)
    const end = new Date(stage.end_time)
    const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
    return `${days}天`
  } catch {
    return '-'
  }
}

function computeProgress(stage: any): number {
  if (!stage.start_time || !stage.end_time) return 0
  try {
    const start = new Date(stage.start_time).getTime()
    const end = new Date(stage.end_time).getTime()
    const now = Date.now()
    if (now <= start) return 0
    if (now >= end) return 100
    return Math.round(((now - start) / (end - start)) * 100)
  } catch {
    return 0
  }
}

function clean(p: string): string {
  return (p || '').replace(/[（(].*[)）]/g, '') || '-'
}

function goBack() {
  router.push({ name: 'ContractList' })
}

function handleNewContract() {
  router.push({ name: 'ContractCreate' })
}

function statusLabel(status: string): string {
  const map: Record<string, string> = { completed: '已完成', in_progress: '进行中', pending: '待开始' }
  return map[status] || status
}

function timelineColor(status: string): string {
  const map: Record<string, string> = { completed: 'green', in_progress: 'blue', pending: 'gray' }
  return map[status] || 'gray'
}

onMounted(async () => {
  try {
    detail.value = await getContractDetailApi(route.query.id as string)
  } finally {
    loading.value = false
  }
})
</script>
