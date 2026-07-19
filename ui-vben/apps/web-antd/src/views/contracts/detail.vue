<template>
  <div class="min-h-screen space-y-4 bg-gradient-to-b from-gray-50 to-gray-100 p-6">
    <ContractHeaderEvidence
      :contract="contract"
      :contract-id="contractId"
      :finance="finance"
      :stages="stages"
      :deliverables="deliverables"
      @back="goBack"
      @updated="load"
    />

    <StateBlock :loading="loading" :error="error" error-title="合同详情加载失败" @retry="load">
      <template v-if="contract">
        <ContractFinance
          :contract="contract"
          :contract-id="contractId"
          :finance="finance"
          :invoices="invoices"
          @updated="load"
        />
        <ContractRelationsFiles
          :contract-id="contractId"
          :projects="projects"
          :files="files"
          :team-members="teamMembers"
          :clauses="clauses"
          @updated="load"
        />
        <ContractFulfillment
          :contract="contract"
          :contract-id="contractId"
          :stages="stages"
          :budgets="budgets"
          :deliverables="deliverables"
          :payments="payments"
          @updated="load"
        />
      </template>
    </StateBlock>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContractDetailApi, getContractTeamApi } from '#/api/contracts'
import StateBlock from '#/components/state-block/index.vue'
import ContractFinance from '#/views/contracts/components/detail/ContractFinance.vue'
import ContractFulfillment from '#/views/contracts/components/detail/ContractFulfillment.vue'
import ContractHeaderEvidence from '#/views/contracts/components/detail/ContractHeaderEvidence.vue'
import ContractRelationsFiles from '#/views/contracts/components/detail/ContractRelationsFiles.vue'

const route = useRoute()
const router = useRouter()
const detail = ref<Record<string, unknown> | null>(null)
const teamMembers = ref<readonly Record<string, unknown>[]>([])
const loading = ref(true)
const error = ref('')

const contract = computed(() => detail.value?.contract)
const contractId = computed(() => String(route.query.id ?? contract.value?.contract_id ?? ''))
const finance = computed(() => detail.value?.finance)
const stages = computed(() => detail.value?.stages ?? [])
const budgets = computed(() => detail.value?.budgets ?? [])
const deliverables = computed(() => detail.value?.deliverables ?? [])
const payments = computed(() => detail.value?.payments ?? [])
const invoices = computed(() => detail.value?.invoices ?? [])
const projects = computed(() => detail.value?.projects ?? [])
const files = computed(() => detail.value?.files ?? [])
const clauses = computed(() => detail.value?.clauses ?? [])

function goBack() {
  router.push({ name: 'ContractList' })
}

async function loadTeam() {
  if (!contractId.value) return
  try {
    const response = await getContractTeamApi(contractId.value)
    teamMembers.value = response?.key_members ?? []
  } catch {
    teamMembers.value = []
  }
}

async function load() {
  if (!contractId.value) return
  loading.value = true
  error.value = ''
  try {
    detail.value = await getContractDetailApi(contractId.value)
    await loadTeam()
  } catch (cause: unknown) {
    error.value = errorMessage(cause)
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.query.id, load)

function errorMessage(cause: unknown): string {
  if (!isRecord(cause)) return '未知错误'
  const response = cause.response
  if (isRecord(response) && isRecord(response.data) && typeof response.data.message === 'string') {
    return response.data.message
  }
  return typeof cause.message === 'string' ? cause.message : '未知错误'
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}
</script>
