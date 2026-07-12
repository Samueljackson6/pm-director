<template>
  <div class="p-4 max-w-7xl mx-auto">
    <!-- 面包屑 -->
    <div class="flex items-center gap-2 mb-4 text-sm text-gray-500">
      <a-button type="link" size="small" @click="goBack">← 项目列表</a-button>
      <span>/</span>
      <span class="text-gray-900 font-medium truncate">{{ project?.project_name || '项目详情' }}</span>
    </div>

    <!-- 三态 -->
    <div v-if="loading" class="flex justify-center py-20"><a-spin size="large" /></div>
    <div v-else-if="error" class="text-center py-20 text-red-500">{{ error }}</div>
    <template v-else-if="project">
      <!-- ========== KPI 指标 ========== -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div class="bg-white rounded-xl border border-gray-100 p-4 text-center shadow-sm">
          <div class="text-xs text-gray-500 mb-1">总体进度</div>
          <div class="text-2xl font-bold text-blue-600">{{ project.overall_progress ?? 0 }}%</div>
        </div>
        <div class="bg-white rounded-xl border border-gray-100 p-4 text-center shadow-sm">
          <div class="text-xs text-gray-500 mb-1">合同总额</div>
          <div class="text-2xl font-bold text-gray-900">¥{{ fmtMoney(project.total_contract_amount) }} 万</div>
        </div>
        <div class="bg-white rounded-xl border border-gray-100 p-4 text-center shadow-sm">
          <div class="text-xs text-gray-500 mb-1">阶段进度</div>
          <div class="text-2xl font-bold text-green-600">{{ completedStages }}/{{ stages.length }}</div>
          <div class="text-xs text-gray-400">已完成</div>
        </div>
        <div class="bg-white rounded-xl border border-gray-100 p-4 text-center shadow-sm">
          <div class="text-xs text-gray-500 mb-1">风险等级</div>
          <div class="text-2xl font-bold" :style="{ color: riskColor(project.risk_level) }">
            {{ riskLabel(project.risk_level) }}
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- 左列：基本信息 + 团队 -->
        <div class="lg:col-span-2 space-y-4">
          <!-- 基本信息 -->
          <a-card title="基本信息" size="small" class="rounded-xl shadow-sm">
            <div class="grid grid-cols-2 gap-3">
              <div><span class="text-xs text-gray-500">项目编号</span><div class="font-mono text-sm">{{ project.project_id }}</div></div>
              <div><span class="text-xs text-gray-500">项目类型</span><div>{{ project.project_type || '-' }}</div></div>
              <div class="col-span-2"><span class="text-xs text-gray-500">项目名称</span><div class="font-medium">{{ project.project_name }}</div></div>
              <div><span class="text-xs text-gray-500">客户名称</span><div>{{ project.customer_name || '-' }}</div></div>
              <div><span class="text-xs text-gray-500">项目状态</span><div><a-tag :color="statusColor(project.project_status)">{{ statusLabel(project.project_status) }}</a-tag></div></div>
              <div><span class="text-xs text-gray-500">计划开始</span><div>{{ project.planned_start || '-' }}</div></div>
              <div><span class="text-xs text-gray-500">计划结束</span><div>{{ project.planned_end || '-' }}</div></div>
            </div>
          </a-card>

          <!-- 阶段进度 -->
          <a-card title="阶段进度" size="small" class="rounded-xl shadow-sm">
            <template #extra>
              <a-button size="small" type="primary" ghost @click="showStageForm=null; newStage={}">+ 添加阶段</a-button>
            </template>
            <!-- 阶段时间线 -->
            <div class="space-y-3">
              <div v-for="(s, idx) in stages" :key="s.stage_id" class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
                    :style="{ backgroundColor: s.status==='completed'?'#52c41a':s.status==='in_progress'?'#1677ff':'#d9d9d9' }">
                    {{ idx + 1 }}
                  </div>
                  <div v-if="idx < stages.length - 1" class="w-0.5 flex-1 min-h-[20px]" :style="{ backgroundColor: s.status==='completed'?'#52c41a':'#e5e7eb' }" />
                </div>
                <div class="flex-1 bg-gray-50 rounded-lg p-3">
                  <div class="flex justify-between items-start">
                    <div>
                      <span class="font-medium">{{ s.stage_name }}</span>
                      <div class="text-xs text-gray-400 mt-1">{{ s.start_time || '?' }} ~ {{ s.end_time || '?' }}</div>
                    </div>
                    <a-tag :color="s.status==='completed'?'green':s.status==='in_progress'?'blue':'default'" size="small">
                      {{ s.status==='completed'?'已完成':s.status==='in_progress'?'进行中':'待开始' }}
                    </a-tag>
                  </div>
                  <div v-if="s.acceptance_criteria" class="text-xs text-gray-500 mt-2 border-t pt-2">{{ parseCriteriaText(s.acceptance_criteria) }}</div>
                </div>
              </div>
              <a-empty v-if="!stages.length" description="暂无阶段数据" />
            </div>
          </a-card>

          <!-- 交付物 -->
          <a-card title="交付物" size="small" class="rounded-xl shadow-sm">
            <template #extra>
              <a-button size="small" type="primary" ghost>+ 上传交付物</a-button>
            </template>
            <div class="space-y-2">
              <div v-for="d in deliverables" :key="d.deliverable_id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold"
                    :style="{ backgroundColor: deliverableColor(d.deliverable_type), color: '#fff' }">
                    {{ deliverableIcon(d.deliverable_type) }}
                  </div>
                  <div class="min-w-0">
                    <div class="font-medium text-sm truncate">{{ d.deliverable_name }}</div>
                    <div class="text-xs text-gray-400">{{ d.deliverable_type }} · {{ d.planned_date || '未排期' }}</div>
                  </div>
                </div>
                <a-tag :color="d.status==='completed'?'green':d.status==='delivered'?'green':'orange'" size="small">
                  {{ d.status==='completed'||d.status==='delivered'?'已交付':'待交付' }}
                </a-tag>
              </div>
              <a-empty v-if="!deliverables.length" description="暂无交付物" />
            </div>
          </a-card>
        </div>

        <!-- 右列：财务 + 团队 + 关联合同 -->
        <div class="space-y-4">
          <!-- 付款计划 -->
          <a-card title="付款计划" size="small" class="rounded-xl shadow-sm">
            <div class="space-y-3">
              <div v-for="p in payments" :key="p.payment_id" class="p-3 bg-gray-50 rounded-lg">
                <div class="flex justify-between items-center mb-1">
                  <span class="font-medium text-sm">{{ p.payment_stage }}</span>
                  <a-tag :color="p.status==='paid'?'green':'orange'" size="small">{{ p.status==='paid'?'已付':'待付' }}</a-tag>
                </div>
                <div class="text-xs text-gray-400 mb-1">{{ p.payment_condition }}</div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">金额</span>
                  <span class="font-semibold">¥{{ fmtMoney(p.planned_amount) }} 万</span>
                </div>
              </div>
              <a-empty v-if="!payments.length" description="暂无付款计划" />
            </div>
          </a-card>

          <!-- 团队信息 -->
          <a-card title="项目团队" size="small" class="rounded-xl shadow-sm">
            <div class="space-y-3">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold">PM</div>
                <div><div class="text-sm font-medium">{{ project.project_manager || '未指定' }}</div><div class="text-xs text-gray-400">项目经理</div></div>
              </div>
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-sm font-bold">TL</div>
                <div><div class="text-sm font-medium">{{ project.tech_lead || '未指定' }}</div><div class="text-xs text-gray-400">技术负责人</div></div>
              </div>
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-sm font-bold">SL</div>
                <div><div class="text-sm font-medium">{{ project.sales_lead || '未指定' }}</div><div class="text-xs text-gray-400">销售负责人</div></div>
              </div>
            </div>
          </a-card>

          <!-- 关联合同 -->
          <a-card title="关联合同" size="small" class="rounded-xl shadow-sm">
            <div class="space-y-2">
              <div v-for="c in contracts" :key="c.contract_id"
                class="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-blue-50/50"
                @click="router.push('/web/contracts/detail?id=' + c.contract_id)">
                <div class="font-medium text-sm truncate">{{ c.project_name || c.contract_id }}</div>
                <div class="flex justify-between items-center mt-1">
                  <span class="text-xs text-gray-400">{{ c.contract_id }}</span>
                  <span class="font-semibold text-sm" v-if="c.contract_amount">¥{{ (c.contract_amount || 0).toFixed(2) }} 万</span>
                </div>
              </div>
              <a-empty v-if="!contracts.length" description="暂无关联合同" />
            </div>
          </a-card>
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getProjectDetailApi,
  getProjectStagesApi,
  getProjectPaymentsApi,
  getProjectDeliverablesApi,
  type ProjectItem,
  type ProjectContract,
  type ProjectStage,
  type ProjectPayment,
  type ProjectDeliverable,
} from '#/api/projects'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const id = computed(() => route.params.id as string)

const project = ref<ProjectItem | null>(null)
const contracts = ref<ProjectContract[]>([])
const stages = ref<ProjectStage[]>([])
const payments = ref<ProjectPayment[]>([])
const deliverables = ref<ProjectDeliverable[]>([])

// 表单状态
const showStageForm = ref<string | null>(null)
const newStage = ref<any>({})

const completedStages = computed(() => stages.value.filter((s) => s.status === 'completed').length)

const statusColorMap: Record<string, string> = { active: 'green', paused: 'orange', completed: 'blue', cancelled: 'gray' }
const statusLabelMap: Record<string, string> = { active: '进行中', paused: '已暂停', completed: '已完成', cancelled: '已取消' }
function statusColor(s: string): string { return statusColorMap[s] || 'default' }
function statusLabel(s: string): string { return statusLabelMap[s] || s || '-' }
const riskColorMap: Record<string, string> = { low: '#52c41a', medium: '#faad14', high: '#fa8c16', critical: '#ff4d4f' }
const riskLabelMap: Record<string, string> = { low: '低风险', medium: '中风险', high: '高风险', critical: '严重' }
function riskColor(r: string): string { return riskColorMap[r] || '#666' }
function riskLabel(r: string): string { return riskLabelMap[r] || r || '-' }

function fmtMoney(n: any): string { return (n ?? 0).toFixed(2) }

function parseCriteriaText(c: string | null): string {
  if (!c) return ''
  const m = c.match(/^\s*\[(.*)\]\s*$/s)
  if (m) {
    return (m[1]||'').split(/['"],\s*['"]/).map((s) => s.replace(/^['"]|['"]$/g,'').trim()).filter(Boolean).join('；')
  }
  return c.length > 120 ? c.slice(0,120)+'...' : c
}

function deliverableColor(type: string): string {
  const map: Record<string, string> = { '报告':'#722ed1','软件':'#13c2c2','专利':'#eb2f96','样机':'#fa8c16','论文':'#2f54eb' }
  return map[type] || '#8c8c8c'
}
function deliverableIcon(type: string): string {
  const map: Record<string, string> = { '报告':'报','软件':'软','专利':'专','样机':'样','论文':'论' }
  return map[type] || '其'
}

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
    stages.value = stagesRes.stages ?? []
    payments.value = paymentsRes.payments ?? []
    deliverables.value = deliverablesRes.deliverables ?? []
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
})

function goBack() { router.push({ name: 'ProjectList' }) }
</script>
