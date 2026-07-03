<template>
  <div class="p-4">
    <a-card title="项目详情" :bordered="false" :loading="loading">
      <template #extra>
        <a-button @click="goBack">返回列表</a-button>
      </template>

      <!-- 项目基本信息 -->
      <a-descriptions v-if="project" :column="2" size="small" bordered>
        <a-descriptions-item label="项目编号" :span="2">{{ project.project_id }}</a-descriptions-item>
        <a-descriptions-item label="项目名称" :span="2">{{ project.project_name }}</a-descriptions-item>
        <a-descriptions-item label="客户名称">{{ project.customer_name }}</a-descriptions-item>
        <a-descriptions-item label="项目类型">{{ project.project_type }}</a-descriptions-item>
        <a-descriptions-item label="合同总额">{{ project.total_contract_amount?.toFixed(2) }} 万元</a-descriptions-item>
        <a-descriptions-item label="项目状态">
          <a-tag :color="statusColor(project.project_status)">{{ statusLabel(project.project_status) }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="计划开始">{{ project.planned_start || '-' }}</a-descriptions-item>
        <a-descriptions-item label="计划结束">{{ project.planned_end || '-' }}</a-descriptions-item>
        <a-descriptions-item label="项目经理">{{ project.project_manager || '-' }}</a-descriptions-item>
        <a-descriptions-item label="技术负责人">{{ project.tech_lead || '-' }}</a-descriptions-item>
        <a-descriptions-item label="销售负责人">{{ project.sales_lead || '-' }}</a-descriptions-item>
        <a-descriptions-item label="总体进度">
          <a-progress :percent="project.overall_progress ?? 0" size="small" style="width: 200px" />
        </a-descriptions-item>
        <a-descriptions-item label="风险等级">
          <a-tag :color="riskColor(project.risk_level)">{{ riskLabel(project.risk_level) }}</a-tag>
        </a-descriptions-item>
      </a-descriptions>

      <!-- 关联合同 -->
      <a-card title="关联合同" size="small" class="mt-4" v-if="contracts.length">
        <ContractGrid />
      </a-card>

      <!-- 阶段进度 -->
      <a-card title="阶段进度" size="small" class="mt-4" v-if="stages.length">
        <a-steps :current="completedStagesCount" size="small">
          <a-step
            v-for="s in stages"
            :key="s.stage_id"
            :title="s.stage_name"
            :status="stageStepStatus(s)"
          />
        </a-steps>
      </a-card>

      <!-- 付款计划 -->
      <a-card title="付款计划" size="small" class="mt-4" v-if="payments.length">
        <a-timeline>
          <a-timeline-item
            v-for="p in payments"
            :key="p.payment_id"
            :color="p.status === 'paid' ? 'green' : 'blue'"
          >
            <p class="font-medium">{{ p.payment_stage }}</p>
            <p v-if="p.payment_condition" class="text-gray-500">{{ p.payment_condition }}</p>
            <p>金额：{{ (p.planned_amount ?? 0).toFixed(2) }} 万元</p>
            <p>状态：{{ p.status === 'paid' ? '已付款' : '待付款' }}</p>
          </a-timeline-item>
        </a-timeline>
      </a-card>

      <!-- 交付物 -->
      <a-card title="交付物" size="small" class="mt-4" v-if="deliverables.length">
        <DeliverableGrid />
      </a-card>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import {
  getProjectDetailApi,
  getProjectStagesApi,
  getProjectPaymentsApi,
  getProjectDeliverablesApi,
  type ProjectItem,
  type ProjectContract,
} from '#/api/projects'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const id = computed(() => route.params.id as string)

const project = ref<ProjectItem | null>(null)
const contracts = ref<ProjectContract[]>([])
const stages = ref<any[]>([])
const payments = ref<any[]>([])
const deliverables = ref<any[]>([])

// 状态标签映射
const statusColorMap: Record<string, string> = {
  active: 'green',
  paused: 'orange',
  completed: 'blue',
  cancelled: 'gray',
}
const statusLabelMap: Record<string, string> = {
  active: '进行中',
  paused: '已暂停',
  completed: '已完成',
  cancelled: '已取消',
}
function statusColor(s: string): string {
  return statusColorMap[s] || 'default'
}
function statusLabel(s: string): string {
  return statusLabelMap[s] || s || '-'
}
const riskColorMap: Record<string, string> = {
  low: 'green',
  medium: 'yellow',
  high: 'orange',
  critical: 'red',
}
const riskLabelMap: Record<string, string> = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '严重',
}
function riskColor(r: string): string {
  return riskColorMap[r] || 'default'
}
function riskLabel(r: string): string {
  return riskLabelMap[r] || r || '-'
}

// 已完成阶段数量（用于 a-steps current）
const completedStagesCount = computed(() => {
  return stages.value.filter((s) => s.status === 'completed').length
})

function stageStepStatus(s: any): 'finish' | 'process' | 'wait' {
  if (s.status === 'completed') return 'finish'
  if (s.status === 'in_progress') return 'process'
  return 'wait'
}

// 关联合同表格
const contractColumns: VxeGridProps<ProjectContract>['columns'] = [
  { field: 'contract_id', title: '合同编号', width: 200 },
  { field: 'project_name', title: '项目名称', minWidth: 200, showOverflow: true },
  { field: 'contract_amount', title: '金额(万元)', width: 130, align: 'right',
    formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2) },
  { field: 'sign_date', title: '签订日期', width: 110 },
]

const contractGridOptions: VxeGridProps<ProjectContract> = {
  columns: contractColumns,
  pagerConfig: false,
  toolbarConfig: false,
  sortConfig: false,
  rowConfig: { isHover: true, height: 40 },
}

const [ContractGrid, contractGridApi] = useVbenVxeGrid({ gridOptions: contractGridOptions })

// 交付物表格
const deliverableColumns: VxeGridProps<any>['columns'] = [
  { field: 'deliverable_name', title: '交付物名称', minWidth: 200, showOverflow: true },
  { field: 'deliverable_type', title: '类型', width: 100 },
  { field: 'quantity', title: '数量', width: 70, align: 'right' },
  { field: 'planned_date', title: '计划日期', width: 110 },
  {
    field: 'status',
    title: '状态',
    width: 90,
    formatter: ({ cellValue }) => {
      const map: Record<string, string> = { delivered: '已交付', pending: '待交付', delayed: '逾期' }
      return map[cellValue] || cellValue || '-'
    },
  },
]

const deliverGridOptions: VxeGridProps<any> = {
  columns: deliverableColumns,
  pagerConfig: false,
  toolbarConfig: false,
  sortConfig: false,
  rowConfig: { isHover: true, height: 40 },
}

const [DeliverableGrid, deliverGridApi] = useVbenVxeGrid({ gridOptions: deliverGridOptions })

onMounted(async () => {
  try {
    const [detailRes, stagesRes, paymentsRes, deliverablesRes] = await Promise.all([
      getProjectDetailApi(id.value),
      getProjectStagesApi(id.value),
      getProjectPaymentsApi(id.value),
      getProjectDeliverablesApi(id.value),
    ])

    project.value = detailRes.project
    contracts.value = detailRes.contracts ?? []
    stages.value = stagesRes ?? []
    payments.value = paymentsRes ?? []
    deliverables.value = deliverablesRes ?? []

    contractGridApi.setGridOptions({ data: contracts.value })
    deliverGridApi.setGridOptions({ data: deliverables.value })
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.push({ name: 'ProjectList' })
}
</script>
