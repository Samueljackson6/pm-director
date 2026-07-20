<template>
  <section id="fulfillment">
    <ResearchContent v-if="contract?.project_type === '科研类'" :contract="contract" :stages="stages" :budgets="budgets" :deliverables="deliverables" :payments="payments" :contract-id="contractId" @reload="emit('updated')" />
    <ServiceContent v-else-if="contract?.project_type === '服务类'" :contract="contract" :payments="payments" :contract-id="contractId" @reload="emit('updated')" />
    <a-empty v-else description="当前合同类型暂无履约模板" class="rounded-lg border border-gray-200 bg-white py-8" />
  </section>
</template>

<script lang="ts" setup>
import ResearchContent from '#/views/contracts/components/ResearchContent.vue'
import ServiceContent from '#/views/contracts/components/ServiceContent.vue'
defineProps(['contract', 'contractId', 'stages', 'budgets', 'deliverables', 'payments'])
const emit = defineEmits(['updated'])
</script>
