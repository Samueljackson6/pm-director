<template>
  <div class="p-4 space-y-4">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold">合同详情</h2>
      <a-button @click="goBack">返回列表</a-button>
    </div>

    <!-- 统一三态：loading / error / 正常内容 -->
    <state-block :loading="loading" :error="error" error-title="合同详情加载失败" @retry="load">
      <!-- 第1行：基本信息 + 财务汇总 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- 基本信息卡片 -->
        <a-card title="基本信息" class="lg:col-span-2" size="small">
          <div v-if="c" class="space-y-4">
            <!-- 合同标题与状态 -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <a-tag v-if="c.contract_status" :color="statusColor(c.contract_status)">
                  {{ statusLabel(c.contract_status) }}
                </a-tag>
                <a-tag v-if="c.project_type" color="blue">{{ c.project_type }}</a-tag>
              </div>
              <div class="text-sm text-muted-foreground">
                合同编号：{{ c.contract_id }}
              </div>
            </div>

            <!-- 分组1：基础信息 -->
            <a-divider orientation="left" class="text-xs font-semibold">基础信息</a-divider>
            <a-descriptions :column="2" size="small">
              <a-descriptions-item label="项目名称" :span="2">
                <a class="text-primary font-medium">{{ c.project_name }}</a>
              </a-descriptions-item>
              <a-descriptions-item label="合同金额">
                <span class="font-semibold text-lg text-primary">{{ c.contract_amount?.toFixed(2) }}</span>
                <span class="text-sm text-muted-foreground"> 万元</span>
              </a-descriptions-item>
              <a-descriptions-item label="甲方" :span="2">{{ clean(c.party_a) }}</a-descriptions-item>
              <a-descriptions-item label="乙方" :span="2">{{ clean(c.party_b) }}</a-descriptions-item>
            </a-descriptions>

            <!-- 分组2：签约信息 -->
            <a-divider orientation="left" class="text-xs font-semibold">签约信息</a-divider>
            <a-descriptions :column="2" size="small">
              <a-descriptions-item label="签订日期">{{ c.sign_date || '-' }}</a-descriptions-item>
              <a-descriptions-item label="到期日期">{{ c.expiry_date || '未设置' }}</a-descriptions-item>
              <a-descriptions-item label="税率">{{ c.tax_rate ? c.tax_rate + '%' : '-' }}</a-descriptions-item>
              <a-descriptions-item label="SGSC编号">{{ c.sgsc_id || '-' }}</a-descriptions-item>
            </a-descriptions>

            <!-- 分组3：服务信息 -->
            <a-divider orientation="left" class="text-xs font-semibold">服务信息</a-divider>
            <a-descriptions :column="1" size="small">
              <a-descriptions-item label="服务期限">{{ c.service_period || '-' }}</a-descriptions-item>
              <a-descriptions-item label="服务内容">{{ c.service_content || '-' }}</a-descriptions-item>
            </a-descriptions>
          </div>
        </a-card>

        <!-- 财务汇总卡片 -->
        <a-card v-if="finance" title="财务汇总" size="small">
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-muted-foreground">合同金额</span>
              <span class="font-bold text-lg">{{ fmt(finance.contract_total) }} 万元</span>
            </div>
            <a-divider class="my-2" />
            <div class="flex justify-between">
              <span class="text-muted-foreground">已开票</span>
              <span class="font-semibold" :style="{ color: 'var(--finance-invoiced)' }">{{ fmt(finance.invoice_total) }} 万元</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">已回款</span>
              <span class="font-semibold" :style="{ color: 'var(--finance-received)' }">{{ fmt(finance.payment_total) }} 万元</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">未回款</span>
              <span class="font-semibold" :style="{ color: 'var(--finance-unreceived)' }">{{ fmt(finance.payment_unreceived) }} 万元</span>
            </div>
            <!-- 简易进度条 -->
            <div class="mt-2">
              <div class="flex justify-between text-xs text-muted-foreground mb-1">
                <span>回款率</span>
                <span>{{ receiptRate }}%</span>
              </div>
              <div class="h-2 rounded-full bg-gray-200 overflow-hidden">
                <div class="h-full rounded-full transition-all"
                  :style="{ width: Math.min(receiptRate, 100) + '%', background: 'var(--finance-received)' }"></div>
              </div>
            </div>
          </div>
        </a-card>
      </div>

      <!-- 第2行：关联项目 + 合同文件 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <a-card title="关联项目" size="small">
          <template v-if="projects.length">
            <div v-for="p in projects" :key="p.project_id" class="flex items-center justify-between py-3 border-b border-dashed last:border-0">
              <div class="flex-1">
                <a class="text-primary font-medium cursor-pointer hover:underline" @click="router.push({ name: 'ProjectDetail', params: { id: p.project_id } })">
                  {{ p.project_name }}
                </a>
                <div class="text-xs text-muted-foreground mt-1">
                  <a-tag size="small">{{ p.project_type }}</a-tag>
                  <a-tag size="small" :color="p.project_status === 'active' ? 'green' : 'default'">{{ p.project_status }}</a-tag>
                </div>
              </div>
              <a-button size="small" type="link" @click="router.push({ name: 'ProjectDetail', params: { id: p.project_id } })">
                查看详情 →
              </a-button>
            </div>
          </template>
          <div v-else class="py-4 text-center text-muted-foreground text-sm">暂无关联项目</div>
        </a-card>

        <a-card title="合同文件" size="small">
          <div class="mb-3 flex justify-end">
            <a-upload
              :before-upload="beforeUpload"
              :show-upload-list="false"
              :disabled="uploading"
            >
              <a-button size="small" type="primary" :loading="uploading">
                上传文件
              </a-button>
            </a-upload>
          </div>
          <template v-if="files.length">
            <div v-for="f in files" :key="f.file_id"
              class="flex items-center justify-between py-3 border-b border-dashed last:border-0 hover:bg-gray-50 rounded px-2">
              <div class="flex items-center gap-3">
                <a-icon :type="fileIcon(f.file_type)" :style="{ fontSize: '24px', color: fileColor(f.file_type) }" />
                <div>
                  <div class="font-medium text-sm">{{ f.file_name }}</div>
                  <div class="text-xs text-muted-foreground">
                    {{ f.file_type?.toUpperCase() }} · {{ formatSize(f.file_size) }}
                    <span v-if="f.upload_time">· {{ f.upload_time?.slice(0, 10) }}</span>
                  </div>
                </div>
              </div>
              <a-button size="small" type="link" :href="downloadUrl(f.file_id)" target="_blank">
                预览
              </a-button>
            </div>
          </template>
          <div v-else class="py-4 text-center text-muted-foreground text-sm">暂无合同文件</div>
        </a-card>
      </div>

      <!-- 阶段进度 - 甘特图（真实排期，替代假百分比条形） -->
      <a-card title="阶段进度（甘特图）" size="small" v-if="stages.length && hasValidStages">
        <stage-gantt :stages="validStages" />
      </a-card>
      <a-card title="阶段进度（甘特图）" size="small" v-else-if="stages.length && !hasValidStages">
        <div class="py-4 text-center text-muted-foreground text-sm">
          <a-icon type="warning" style="color: #faad14; margin-right: 8px;" />
          阶段数据待完善（当前数据来自 OCR 识别，需人工校验）
        </div>
      </a-card>

      <!-- 付款时间线 -->
      <a-card title="付款时间线" size="small" v-if="payments.length">
        <a-timeline>
          <a-timeline-item v-for="p in payments" :key="p.payment_id" :color="timelineColor(p.status)">
            <div class="font-medium">{{ p.payment_stage }}</div>
            <div>计划金额：{{ fmtMoney(p.planned_amount) }} 万元</div>
            <div v-if="p.actual_amount != null">实际金额：{{ fmtMoney(p.actual_amount) }} 万元</div>
            <div class="text-muted-foreground text-xs">{{ p.payment_condition }}</div>
          </a-timeline-item>
        </a-timeline>
      </a-card>

      <!-- 交付物 -->
      <a-card title="交付物" size="small" v-if="deliverables.length && hasValidDeliverables">
        <a-table :columns="deliverableCols" :data-source="deliverables" row-key="deliverable_id" size="small" :pagination="false" />
      </a-card>
      <a-card title="交付物" size="small" v-else-if="deliverables.length && !hasValidDeliverables">
        <div class="py-4 text-center text-muted-foreground text-sm">
          <a-icon type="warning" style="color: #faad14; margin-right: 8px;" />
          交付物数据待完善（将从合同原始文档中重新提取）
        </div>
      </a-card>

      <!-- 违约/罚款条款（#3 数据补全新增） -->
      <a-card title="违约 / 罚款条款" size="small">
        <div v-if="nonConfidentialClauses.length" class="space-y-4">
          <div v-for="g in nonConfidentialGroups" :key="g.key">
            <div class="clause-group-title">{{ g.label }}</div>
            <div class="space-y-2">
              <div v-for="cl in g.items" :key="cl.clause_id" class="clause-item">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="font-medium">{{ cl.trigger_type || '—' }}</span>
                  <a-tag v-if="cl.rate_pct != null" color="orange">
                    违约金 {{ cl.rate_pct }}%{{ cl.clause_category === 'overdue' ? '/天' : '' }}
                  </a-tag>
                  <a-tag v-if="cl.threshold_days" color="red">逾期超 {{ cl.threshold_days }} 日解除</a-tag>
                  <a-tag v-if="cl.refund_full" class="refund-tag">退还全部款项</a-tag>
                </div>
                <div v-if="cl.clause_text" class="clause-text">{{ cl.clause_text }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="py-4 text-center text-muted-foreground text-sm">暂无违约/罚款条款</div>
      </a-card>

      <!-- 保密条款（单独展示） -->
      <a-card title="保密条款" size="small" v-if="confidentialClauses.length">
        <div class="space-y-2">
          <div v-for="cl in confidentialClauses" :key="cl.clause_id" class="clause-item">
            <div class="flex flex-wrap items-center gap-2">
              <a-tag color="purple">保密</a-tag>
              <span class="font-medium">{{ cl.trigger_type || '—' }}</span>
              <a-tag v-if="cl.rate_pct != null" color="orange">违约金 {{ cl.rate_pct }}%</a-tag>
            </div>
            <div v-if="cl.clause_text" class="clause-text">{{ cl.clause_text }}</div>
          </div>
        </div>
      </a-card>
    </state-block>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getContractDetailApi, uploadContractFileApi, contractFileDownloadUrl } from '#/api/contracts'
import StageGantt from '#/views/contracts/components/stage-gantt.vue'
import StateBlock from '#/components/state-block/index.vue'

const route = useRoute()
const router = useRouter()
const detail = ref<any>(null)
const loading = ref(true)
const error = ref('')
const uploading = ref(false)

const c = computed(() => detail.value?.contract ?? null)
const stages = computed(() => detail.value?.stages ?? [])
const payments = computed(() => detail.value?.payments ?? [])
const deliverables = computed(() => detail.value?.deliverables ?? [])
const finance = computed(() => detail.value?.finance ?? null)
const projects = computed(() => detail.value?.projects ?? [])
const files = computed(() => detail.value?.files ?? [])
const clauses = computed(() => detail.value?.clauses ?? [])

// 保密条款单独展示
const confidentialClauses = computed(() =>
  clauses.value.filter((cl: any) => cl.clause_category === 'confidentiality')
)
const nonConfidentialClauses = computed(() =>
  clauses.value.filter((cl: any) => cl.clause_category !== 'confidentiality')
)

// 非保密条款分组（按 clause_category）
const nonConfidentialGroups = computed(() => {
  const CAT_LABELS: Record<string, string> = {
    breach_liability: '违约责任', liquidated_damages: '违约金', penalty: '罚款',
    overdue: '逾期', compensation: '赔偿', ip: '知识产权',
    force_majeure: '不可抗力', termination: '解除/终止',
  }
  const CAT_ORDER = ['breach_liability', 'liquidated_damages', 'penalty', 'overdue',
    'compensation', 'ip', 'force_majeure', 'termination']
  const map: Record<string, any[]> = {}
  for (const cl of nonConfidentialClauses.value) (map[cl.clause_category] ||= []).push(cl)
  return CAT_ORDER.filter((c) => map[c]).map((c) => ({ key: c, label: CAT_LABELS[c], items: map[c] }))
})

// 合同状态标签
function statusColor(status: string): string {
  const map: Record<string, string> = {
    signed: 'green', active: 'blue', completed: 'default',
    expired: 'red', terminated: 'orange', pending: 'gray',
  }
  return map[status] || 'default'
}
function statusLabel(status: string): string {
  const map: Record<string, string> = {
    signed: '已签订', active: '执行中', completed: '已完成',
    expired: '已到期', terminated: '已终止', pending: '待签订',
  }
  return map[status] || status
}

// 文件图标和颜色
function fileIcon(fileType: string): string {
  if (!fileType) return 'file'
  const t = fileType.toLowerCase()
  if (t.includes('pdf')) return 'file-pdf'
  if (t.includes('doc') || t.includes('word')) return 'file-word'
  if (t.includes('xls') || t.includes('excel')) return 'file-excel'
  if (t.includes('ppt') || t.includes('powerpoint')) return 'file-ppt'
  if (t.includes('image') || t.includes('jpg') || t.includes('png')) return 'file-image'
  return 'file'
}
function fileColor(fileType: string): string {
  if (!fileType) return '#666'
  const t = fileType.toLowerCase()
  if (t.includes('pdf')) return '#ff4d4f'
  if (t.includes('doc') || t.includes('word')) return '#1890ff'
  if (t.includes('xls') || t.includes('excel')) return '#52c41a'
  if (t.includes('ppt') || t.includes('powerpoint')) return '#fa8c16'
  return '#666'
}
function formatSize(bytes: number): string {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i]
}

function downloadUrl(fileId: string): string {
  return contractFileDownloadUrl(fileId)
}

const receiptRate = computed(() => {
  const f = finance.value
  if (!f || !f.contract_total) return 0
  return ((f.payment_total || 0) / f.contract_total * 100).toFixed(1)
})

const contractId = computed(() => (route.query.id as string) || c.value?.contract_id || '')

// 阶段数据质量检查（过滤 OCR 错误数据）
const hasValidStages = computed(() => {
  if (!stages.value.length) return false
  // 检查是否有有效的 start_time 或 end_time
  return stages.value.some((s: any) => s.start_time || s.end_time)
})
const validStages = computed(() => {
  // 只显示有有效日期的阶段
  return stages.value.filter((s: any) => s.start_time || s.end_time)
})

// 交付物数据质量检查
const hasValidDeliverables = computed(() => {
  if (!deliverables.value.length) return false
  // 检查是否有非空的 planned_date 或 status 不是全 pending
  return deliverables.value.some((d: any) => d.planned_date || d.status !== 'pending')
})

const deliverableCols = [
  { title: '交付物名称', dataIndex: 'deliverable_name', minWidth: 200 },
  { title: '类型', dataIndex: 'deliverable_type', width: 100 },
  { title: '数量', dataIndex: 'quantity', width: 60 },
  { title: '计划日期', dataIndex: 'planned_date', width: 110 },
  { title: '状态', dataIndex: 'status', width: 80 },
]

async function load() {
  loading.value = true
  error.value = ''
  try {
    detail.value = await getContractDetailApi(route.query.id as string)
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '未知错误'
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function beforeUpload(file: File) {
  if (!contractId.value) {
    message.error('缺少合同标识，无法上传')
    return false
  }
  uploading.value = true
  try {
    await uploadContractFileApi(contractId.value, file)
    message.success(`已上传：${file.name}`)
    await load()
  } catch (e: any) {
    message.error(e?.response?.data?.message || e?.message || '上传失败')
  } finally {
    uploading.value = false
  }
  return false // 阻止 antd 自动上传，改由我们手动调用
}

function downloadUrl(fileId: string): string {
  return contractFileDownloadUrl(contractId.value, fileId)
}

function clean(p: string): string {
  return (p || '').replace(/[（(].*[)）]/g, '') || '-'
}

function goBack() {
  router.push({ name: 'ContractList' })
}

function timelineColor(status: string): string {
  const map: Record<string, string> = { completed: 'green', in_progress: 'blue', pending: 'gray' }
  return map[status] || 'gray'
}

function fmtMoney(v: number | null | undefined): string {
  return (v ?? 0).toFixed(2)
}

function fmt(v: number | null | undefined): string {
  return (v ?? 0).toFixed(2)
}

function formatSize(bytes: number | null | undefined): string {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + 'B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB'
  return (bytes / 1024 / 1024).toFixed(1) + 'MB'
}
</script>

<style scoped>
.clause-group-title {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}
.clause-item {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fcfcfc;
}
.clause-text {
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
  white-space: pre-wrap;
  line-height: 1.6;
}
.refund-tag {
  color: #dc2626;
  border-color: #dc2626;
}
</style>
