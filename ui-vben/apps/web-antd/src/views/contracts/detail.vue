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
          <a-descriptions v-if="c" :column="2" size="small" bordered>
            <a-descriptions-item label="合同编号" :span="2">{{ c.contract_id }}</a-descriptions-item>
            <a-descriptions-item label="项目名称" :span="2">{{ c.project_name }}</a-descriptions-item>
            <a-descriptions-item label="合同金额">{{ c.contract_amount?.toFixed(2) }} 万元</a-descriptions-item>
            <a-descriptions-item label="项目类型">{{ c.project_type }}</a-descriptions-item>
            <a-descriptions-item label="合同状态">{{ c.contract_status || '-' }}</a-descriptions-item>
            <a-descriptions-item label="签订日期">{{ c.sign_date || '-' }}</a-descriptions-item>
            <a-descriptions-item label="服务期限" :span="2">{{ c.service_period || '-' }}</a-descriptions-item>
            <a-descriptions-item label="甲方" :span="2">{{ clean(c.party_a) }}</a-descriptions-item>
            <a-descriptions-item label="乙方" :span="2">{{ clean(c.party_b) }}</a-descriptions-item>
          </a-descriptions>
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
            <a-table :columns="projectCols" :data-source="projects" row-key="project_id" size="small" :pagination="false" />
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
              class="flex items-center justify-between py-2 border-b border-dashed last:border-0">
              <div>
                <div class="font-medium">{{ f.file_name }}</div>
                <div class="text-xs text-muted-foreground">{{ f.file_type }} · {{ formatSize(f.file_size) }}</div>
              </div>
              <a-button size="small" type="link" :href="downloadUrl(f.file_id)" target="_blank">预览</a-button>
            </div>
          </template>
          <div v-else class="py-4 text-center text-muted-foreground text-sm">暂无合同文件</div>
        </a-card>
      </div>

      <!-- 阶段进度 - 甘特图（真实排期，替代假百分比条形） -->
      <a-card title="阶段进度（甘特图）" size="small" v-if="stages.length">
        <stage-gantt :stages="stages" />
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
      <a-card title="交付物" size="small" v-if="deliverables.length">
        <a-table :columns="deliverableCols" :data-source="deliverables" row-key="deliverable_id" size="small" :pagination="false" />
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

const receiptRate = computed(() => {
  const f = finance.value
  if (!f || !f.contract_total) return 0
  return ((f.payment_total || 0) / f.contract_total * 100).toFixed(1)
})

const contractId = computed(() => (route.query.id as string) || c.value?.contract_id || '')

const projectCols = [
  { title: '项目编号', dataIndex: 'project_id', width: 160 },
  { title: '项目名称', dataIndex: 'project_name', minWidth: 200 },
  { title: '项目类型', dataIndex: 'project_type', width: 90 },
  { title: '项目状态', dataIndex: 'project_status', width: 90 },
]

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
