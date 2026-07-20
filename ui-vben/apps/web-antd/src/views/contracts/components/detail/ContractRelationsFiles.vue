<template>
  <section id="relations" class="space-y-4">
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <a-card title="关联项目" size="small" :body-style="{ padding: '12px' }">
        <div v-if="projects?.length">
          <div v-for="project in projects" :key="project.project_id" class="flex items-center justify-between border-b border-dashed border-gray-200 py-3 last:border-0">
            <span>
              <a class="cursor-pointer font-medium text-primary" @click="openProject(project.project_id)">{{ project.project_name }}</a>
              <small class="mt-1 block text-gray-400">{{ project.project_type }} · {{ project.project_status }}</small>
            </span>
            <a-button type="link" size="small" @click="openProject(project.project_id)">查看详情 →</a-button>
          </div>
        </div>
        <a-empty v-else description="暂无关联项目" class="py-8" />
      </a-card>

      <a-card title="合同文件" size="small" :body-style="{ padding: '12px' }">
        <div class="mb-3 flex justify-end">
          <a-upload :before-upload="upload" :show-upload-list="false" :disabled="uploading">
            <a-button type="primary" size="small" :loading="uploading">上传文件</a-button>
          </a-upload>
        </div>
        <div v-if="files?.length">
          <div v-for="file in files" :key="file.file_id" class="flex items-center justify-between border-b border-dashed border-gray-200 py-3 last:border-0">
            <span>
              <strong class="text-sm">{{ file.file_name }}</strong>
              <small class="ml-2 text-gray-400">{{ file.file_type?.toUpperCase() }} · {{ size(file.file_size) }}</small>
            </span>
            <a-button type="link" size="small" :href="contractFileDownloadUrl(contractId, file.file_id)" target="_blank">预览</a-button>
          </div>
        </div>
        <a-empty v-else description="暂无合同文件" class="py-8" />
      </a-card>
    </div>

    <a-card id="team" title="项目团队" size="small">
      <div v-if="teamMembers?.length" class="grid grid-cols-1 gap-3 md:grid-cols-3">
        <div v-for="member in teamMembers" :key="member.role" class="rounded-lg bg-gray-50 p-3">
          <small class="text-gray-400">{{ member.role_label }}</small>
          <p class="mt-1 font-medium">{{ member.person_name }}</p>
          <small class="text-gray-400">{{ member.phone || '-' }}</small>
        </div>
      </div>
      <a-empty v-else description="暂无团队成员数据" class="py-6" />
    </a-card>

    <a-card id="clauses" title="合同条款" size="small">
      <a-collapse v-if="groups.length">
        <a-collapse-panel v-for="group in groups" :key="group.key" :header="group.label">
          <div v-for="clause in group.items" :key="clause.clause_id" class="mb-3 rounded-lg border border-gray-200 bg-gray-50 p-3 last:mb-0">
            <a-tag v-if="clause.rate_pct != null" color="orange">违约金 {{ clause.rate_pct }}%</a-tag>
            <a-tag v-if="clause.threshold_days" color="red">逾期超 {{ clause.threshold_days }} 日</a-tag>
            <p v-if="clause.clause_text" class="mt-2 whitespace-pre-wrap text-sm text-gray-600">{{ clause.clause_text }}</p>
          </div>
        </a-collapse-panel>
      </a-collapse>
      <a-empty v-else description="暂无违约/罚款条款" class="py-8" />
    </a-card>

    <a-card v-if="confidentialClauses.length" title="保密条款" size="small">
      <div v-for="clause in confidentialClauses" :key="clause.clause_id" class="mb-3 rounded-lg border border-gray-200 bg-gray-50 p-3 last:mb-0">
        <a-tag color="purple">保密</a-tag>
        <a-tag v-if="clause.rate_pct != null" color="orange">违约金 {{ clause.rate_pct }}%</a-tag>
        <p v-if="clause.clause_text" class="mt-2 whitespace-pre-wrap text-sm text-gray-600">{{ clause.clause_text }}</p>
      </div>
    </a-card>
  </section>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { contractFileDownloadUrl, uploadContractFileApi } from '#/api/contracts'

interface ContractClause {
  clause_category?: string
  [key: string]: any
}

const props = defineProps<{
  clauses?: ContractClause[]
  contractId: string
  files?: any[]
  projects?: any[]
  teamMembers?: readonly any[]
}>()
const emit = defineEmits(['updated'])
const router = useRouter()
const uploading = ref(false)
const confidentialClauses = computed(() => {
  return (props.clauses ?? []).filter((clause) =>
    ['confidentiality', 'confidential'].includes(clause.clause_category ?? ''),
  )
})
const groups = computed(() => {
  const labels: Record<string, string> = {
    breach_liability: '违约责任',
    liquidated_damages: '违约金',
    penalty: '罚款',
    overdue: '逾期',
    compensation: '赔偿',
    ip: '知识产权',
    force_majeure: '不可抗力',
    termination: '解除/终止',
    dispute: '争议解决',
  }
  const groupsByCategory = new Map<string, ContractClause[]>()
  for (const clause of (props.clauses ?? []).filter(
    (item) => !['confidentiality', 'confidential'].includes(item.clause_category ?? ''),
  )) {
    const category = clause.clause_category ?? 'other'
    groupsByCategory.set(category, [
      ...(groupsByCategory.get(category) ?? []),
      clause,
    ])
  }
  return [...groupsByCategory].map(([key, items]) => ({
    key,
    label: labels[key] ?? key,
    items,
  }))
})

function openProject(id: unknown) { router.push({ name: 'ProjectDetail', query: { id: String(id) } }) }
function size(bytes: unknown) { const value = Number(bytes || 0); return value ? `${(value / 1024).toFixed(1)} KB` : '0 B' }
function upload(file: File) {
  uploading.value = true
  uploadContractFileApi(props.contractId, file)
    .then(() => { message.success('文件上传成功'); emit('updated') })
    .catch((cause: unknown) => { message.error(cause instanceof Error ? `文件上传失败：${cause.message}` : '文件上传失败') })
    .finally(() => { uploading.value = false })
  return false
}
</script>
