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

            <!-- 统计卡片网格（替代 a-descriptions） -->
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
              <a-card size="small" class="text-center">
                <a-statistic
                  title="合同金额"
                  :value="c.contract_amount || 0"
                  :precision="2"
                  suffix="万元"
                  :value-style="{ color: '#3f8600', fontSize: '20px' }"
                />
              </a-card>
              <a-card size="small" class="text-center">
                <a-statistic
                  title="税率"
                  :value="c.tax_rate || 0"
                  suffix="%"
                  :value-style="{ color: '#1677ff', fontSize: '20px' }"
                />
              </a-card>
              <a-card size="small" class="text-center">
                <a-statistic
                  title="SGSC编号"
                  :value="c.sgsc_id || '未设置'"
                  :value-style="{ color: '#666', fontSize: '16px' }"
                />
              </a-card>
            </div>

            <!-- 签约信息 -->
            <a-divider orientation="left" class="text-xs font-semibold">签约信息</a-divider>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <span class="text-xs text-muted-foreground">签订日期</span>
                <div class="font-medium">{{ c.sign_date || '-' }}</div>
              </div>
              <div>
                <span class="text-xs text-muted-foreground">到期日期</span>
                <div class="font-medium">{{ c.expiry_date || '未设置' }}</div>
              </div>
            </div>

            <!-- 服务信息 -->
            <a-divider orientation="left" class="text-xs font-semibold">服务信息</a-divider>
            <div class="space-y-2">
              <div>
                <span class="text-xs text-muted-foreground">服务期限</span>
                <div class="font-medium">{{ c.service_period || '-' }}</div>
              </div>
              <div>
                <span class="text-xs text-muted-foreground">服务内容</span>
                <div class="font-medium">{{ c.service_content || '-' }}</div>
              </div>
            </div>

            <!-- 合同双方 -->
            <a-divider orientation="left" class="text-xs font-semibold">合同双方</a-divider>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <a-card size="small" class="bg-blue-50">
                <div class="text-xs text-muted-foreground">甲方</div>
                <div class="font-medium">{{ clean(c.party_a) }}</div>
              </a-card>
              <a-card size="small" class="bg-green-50">
                <div class="text-xs text-muted-foreground">乙方</div>
                <div class="font-medium">{{ clean(c.party_b) }}</div>
              </a-card>
            </div>
          </div>
        </a-card>

        <!-- 财务汇总卡片 -->
        <a-card v-if="finance" title="财务汇总" size="small">
          <div class="space-y-3">
            <a-statistic
              title="合同总金额"
              :value="finance.contract_total || 0"
              :precision="2"
              suffix="万元"
              :value-style="{ fontSize: '24px' }"
            />
            <a-divider class="my-2" />
            <div class="flex justify-between">
              <span class="text-muted-foreground">已开票</span>
              <span class="font-semibold text-blue-600">{{ fmt(finance.invoice_total) }} 万元</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">已回款</span>
              <span class="font-semibold text-green-600">{{ fmt(finance.payment_total) }} 万元</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">未回款</span>
              <span class="font-semibold text-red-600">{{ fmt(finance.payment_unreceived) }} 万元</span>
            </div>
            <!-- 环形进度条 -->
            <div class="mt-4 flex flex-col items-center">
              <a-progress
                type="circle"
                :percent="parseFloat(receiptRate)"
                :size="80"
                :stroke-color="receiptRate >= 100 ? '#52c41a' : receiptRate >= 50 ? '#1677ff' : '#ff4d4f'"
              />
              <div class="mt-2 text-sm text-muted-foreground">回款率 {{ receiptRate }}%</div>
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

      <!-- 阶段进度 - 甘特图 -->
      <a-card title="阶段进度（甘特图）" size="small" v-if="stages.length">
        <stage-gantt :stages="validStages" />
        <div v-if="!hasValidStages" class="py-4 text-center text-muted-foreground text-sm">
          <a-icon type="warning" style="color: #faad14; margin-right: 8px;" />
          阶段数据待完善（当前数据来自 OCR 识别，需人工校验）
        </div>
      </a-card>

      <!-- 付款进度（结构化展示） -->
      <a-card title="付款进度" size="small" v-if="payments.length">
        <!-- 付款汇总统计 -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <a-card size="small" class="text-center">
            <a-statistic title="付款阶段" :value="payments.length" suffix="个" />
          </a-card>
          <a-card size="small" class="text-center">
            <a-statistic
              title="计划总额"
              :value="paymentsTotal.planned"
              :precision="2"
              suffix="万元"
              :value-style="{ color: '#1677ff' }"
            />
          </a-card>
          <a-card size="small" class="text-center">
            <a-statistic
              title="已付金额"
              :value="paymentsTotal.paid"
              :precision="2"
              suffix="万元"
              :value-style="{ color: '#52c41a' }"
            />
          </a-card>
          <a-card size="small" class="text-center">
            <a-statistic
              title="付款进度"
              :value="parseFloat(paymentProgress)"
              :precision="1"
              suffix="%"
              :value-style="{ color: paymentProgress >= 100 ? '#52c41a' : paymentProgress >= 50 ? '#1677ff' : '#ff4d4f' }"
            />
          </a-card>
        </div>

        <!-- 付款进度条 -->
        <div class="mb-4">
          <div class="flex justify-between text-sm mb-1">
            <span class="text-muted-foreground">累计付款进度</span>
            <span class="font-semibold">{{ paymentProgress }}%</span>
          </div>
          <a-progress
            :percent="parseFloat(paymentProgress)"
            :stroke-color="paymentProgress >= 100 ? '#52c41a' : paymentProgress >= 50 ? '#1677ff' : '#ff4d4f'"
            :format="(percent: number) => `${percent.toFixed(1)}%`"
            size="default"
          />
        </div>

        <!-- 付款阶段卡片（网格布局） -->
        <div class="space-y-3">
          <div v-for="(p, idx) in paymentsWithStatus" :key="p.payment_id" class="relative">
            <!-- 阶段序号 -->
            <div class="absolute -left-2 -top-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
              :style="{ backgroundColor: p.isPaid ? '#52c41a' : '#1677ff' }">
              {{ idx + 1 }}
            </div>
            <a-card size="small" class="ml-4" :class="p.isPaid ? 'border-green-200 bg-green-50' : 'border-blue-200 bg-blue-50'">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <!-- 左侧：阶段信息 -->
                <div class="md:col-span-2">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="font-semibold text-base">{{ p.payment_stage }}</span>
                    <a-tag :color="p.isPaid ? 'green' : 'orange'">
                      {{ p.statusLabel }}
                    </a-tag>
                  </div>
                  <div class="text-sm text-muted-foreground">
                    {{ p.payment_condition }}
                  </div>
                </div>

                <!-- 右侧：金额信息 -->
                <div class="flex flex-col justify-center space-y-2">
                  <div class="flex justify-between text-sm">
                    <span class="text-muted-foreground">计划金额</span>
                    <span class="font-semibold">{{ fmtMoney(p.planned_amount) }} 万元</span>
                  </div>
                  <div v-if="p.actual_amount != null" class="flex justify-between text-sm">
                    <span class="text-muted-foreground">实际金额</span>
                    <span class="font-semibold text-green-600">{{ fmtMoney(p.actual_amount) }} 万元</span>
                  </div>
                  <!-- 单阶段进度条 -->
                  <a-progress
                    v-if="p.planned_amount > 0"
                    :percent="p.progressPercent"
                    size="small"
                    :stroke-color="p.isPaid ? '#52c41a' : '#1677ff'"
                    :format="() => `${p.progressPercent.toFixed(0)}%`"
                  />
                </div>
              </div>

              <!-- 付款日期 -->
              <div class="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                <span v-if="p.planned_date">
                  📅 计划日期：{{ p.planned_date }}
                </span>
                <span v-if="p.actual_date">
                  ✅ 实际日期：{{ p.actual_date }}
                </span>
              </div>
            </a-card>
          </div>
        </div>
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

      <!-- 违约/罚款条款（折叠面板） -->
      <a-card title="违约 / 罚款条款" size="small">
        <a-collapse v-if="nonConfidentialClauses.length" :default-active-key="nonConfidentialGroups.map(g => g.key)">
          <a-collapse-panel v-for="g in nonConfidentialGroups" :key="g.key" :header="g.label">
            <div class="space-y-2">
              <div v-for="cl in g.items" :key="cl.clause_id" class="clause-item">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="font-medium">{{ cl.trigger_type || '—' }}</span>
                  <a-tag v-if="cl.rate_pct != null" color="orange">
                    违约金 {{ cl.rate_pct }}%{{ cl.clause_category === 'overdue' ? '/天' : '' }}
                  </a-tag>
                  <a-tag v-if="cl.threshold_days" color="red">逾期超 {{ cl.threshold_days }} 日解除</a-tag>
                  <a-tag v-if="cl.refund_full" color="red">退还全部款项</a-tag>
                </div>
                <div v-if="cl.clause_text" class="clause-text">{{ cl.clause_text }}</div>
              </div>
            </div>
          </a-collapse-panel>
        </a-collapse>
        <div v-else class="py-4 text-center text-muted-foreground text-sm">暂无违约/罚款条款</div>
      </a-card>

      <!-- 保密条款（单独卡片） -->
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

// 非保密条款分组
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

// 阶段数据质量检查
const hasValidStages = computed(() => {
  if (!stages.value.length) return false
  return stages.value.some((s: any) => s.start_time || s.end_time)
})
const validStages = computed(() => {
  return stages.value.filter((s: any) => s.start_time || s.end_time)
})

// 交付物数据质量检查
const hasValidDeliverables = computed(() => {
  if (!deliverables.value.length) return false
  return deliverables.value.some((d: any) => d.planned_date || d.status !== 'pending')
})

// 财务汇总
const receiptRate = computed(() => {
  const f = finance.value
  if (!f || !f.contract_total) return 0
  return ((f.payment_total || 0) / f.contract_total * 100).toFixed(1)
})

const contractId = computed(() => (route.query.id as string) || c.value?.contract_id || '')

const deliverableCols = [
  { title: '交付物名称', dataIndex: 'deliverable_name', minWidth: 200 },
  { title: '类型', dataIndex: 'deliverable_type', width: 100 },
  { title: '数量', dataIndex: 'quantity', width: 60 },
  { title: '计划日期', dataIndex: 'planned_date', width: 110 },
  { title: '状态', dataIndex: 'status', width: 80 },
]

// 格式化金额
function fmt(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toFixed(2)
}
function fmtMoney(n: number | null | undefined): string {
  if (n == null) return '0.00'
  return n.toFixed(2)
}

// 付款数据结构化
const paymentsWithStatus = computed(() => {
  return payments.value.map((p: any) => {
    const isPaid = p.status === 'paid'
    const progressPercent = (p.planned_amount > 0 && p.actual_amount != null)
      ? (p.actual_amount / p.planned_amount * 100)
      : (isPaid ? 100 : 0)
    const statusLabel = isPaid ? '已支付' : p.status === 'pending' ? '待支付' : p.status || '未知'
    return {
      ...p,
      isPaid,
      progressPercent,
      statusLabel,
    }
  })
})

// 付款汇总
const paymentsTotal = computed(() => {
  const planned = payments.value.reduce((sum: number, p: any) => sum + (p.planned_amount || 0), 0)
  const paid = payments.value
    .filter((p: any) => p.status === 'paid')
    .reduce((sum: number, p: any) => sum + (p.actual_amount || p.planned_amount || 0), 0)
  return { planned, paid }
})

// 付款进度百分比
const paymentProgress = computed(() => {
  if (paymentsTotal.value.planned === 0) return '0.0'
  return ((paymentsTotal.value.paid / paymentsTotal.value.planned) * 100).toFixed(1)
})

// 时间线颜色
function timelineColor(status: string): string {
  const map: Record<string, string> = {
    paid: 'green',
    pending: 'orange',
    planned: 'blue',
  }
  return map[status] || 'gray'
}

// 清理文本
function clean(s: string | null | undefined): string {
  if (!s) return '-'
  return s.replace(/[\n\r]+/g, ' ').trim()
}

// 导航
function goBack() {
  router.push({ name: 'ContractList' })
}

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
</script>

<style scoped>
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
</style>
