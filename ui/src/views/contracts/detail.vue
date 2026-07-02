<template>
  <div class="p-4">
    <a-card title="合同详情" :bordered="false" :loading="loading">
      <template #extra>
        <a-button @click="goBack">返回列表</a-button>
      </template>

      <a-descriptions v-if="c" :column="2" size="small" bordered>
        <a-descriptions-item label="合同编号" :span="2">{{ c.contract_id }}</a-descriptions-item>
        <a-descriptions-item label="项目名称" :span="2">{{ c.project_name }}</a-descriptions-item>
        <a-descriptions-item label="合同金额">{{ c.contract_amount?.toFixed(2) }} 万元</a-descriptions-item>
        <a-descriptions-item label="项目类型">{{ c.project_type }}</a-descriptions-item>
        <a-descriptions-item label="甲方">{{ clean(c.party_a) }}</a-descriptions-item>
        <a-descriptions-item label="乙方">{{ clean(c.party_b) }}</a-descriptions-item>
        <a-descriptions-item label="签订日期">{{ c.sign_date || '-' }}</a-descriptions-item>
        <a-descriptions-item label="服务期限">{{ c.service_period || '-' }}</a-descriptions-item>
      </a-descriptions>

      <!-- 阶段表格 -->
      <a-card title="研究阶段" size="small" class="mt-4" v-if="stages.length">
        <a-table :columns="stageCols" :data-source="stages" row-key="stage_id" size="small" :pagination="false" />
      </a-card>

      <!-- 付款计划 -->
      <a-card title="付款计划" size="small" class="mt-4" v-if="payments.length">
        <a-table :columns="payCols" :data-source="payments" row-key="payment_id" size="small" :pagination="false" />
      </a-card>

      <!-- 交付物 -->
      <a-card title="交付物" size="small" class="mt-4" v-if="deliverables.length">
        <a-table :columns="deliverableCols" :data-source="deliverables" row-key="deliverable_id" size="small" :pagination="false" />
      </a-card>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContractDetailApi } from '#/api/contracts'

const route = useRoute()
const router = useRouter()
const detail = ref<any>(null)
const loading = ref(true)

const c = computed(() => detail.value?.contract ?? null)
const stages = computed(() => detail.value?.stages ?? [])
const payments = computed(() => detail.value?.payments ?? [])
const deliverables = computed(() => detail.value?.deliverables ?? [])

const stageCols = [
  { title: '阶段名称', dataIndex: 'stage_name' },
  { title: '阶段编号', dataIndex: 'stage_number', width: 80 },
  { title: '开始时间', dataIndex: 'start_time', width: 110 },
  { title: '结束时间', dataIndex: 'end_time', width: 110 },
  { title: '状态', dataIndex: 'status', width: 80 },
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

onMounted(async () => {
  try {
    detail.value = await getContractDetailApi(route.params.id as string)
  } finally {
    loading.value = false
  }
})

function clean(p: string): string {
  return (p || '').replace(/[（(].*[)）]/g, '') || '-'
}

function goBack() {
  router.push({ name: 'ContractList' })
}
</script>
