<template>
<a-card title='Contract Detail' :bordered='false'>
  <a-descriptions v-if='!loading' :column='2' size='small'>
    <a-descriptions-item label='Project'>{{ c?.project_name }}</a-descriptions-item>
    <a-descriptions-item label='Amount'>{{ c?.contract_amount?.toFixed(2) }}k</a-descriptions-item>
    <a-descriptions-item label='Party A'>{{ clean(c?.party_a) }}</a-descriptions-item>
    <a-descriptions-item label='Party B'>{{ clean(c?.party_b) }}</a-descriptions-item>
    <a-descriptions-item label='Type'>{{ c?.project_type }}</a-descriptions-item>
    <a-descriptions-item label='Signed'>{{ c?.sign_date }}</a-descriptions-item>
  </a-descriptions>
</a-card>
</template>
<script lang='ts' setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getContractDetailApi } from '#/api/contracts'
const route = useRoute()
const detail = ref<any>(null)
const loading = ref(true)
const c = computed(() => detail.value?.contract)
onMounted(async () => { detail.value = await getContractDetailApi(route.params.id as string); loading.value = false })
function clean(p: string): string { return (p || '').replace(/[（(].*[)）]/g, '') || '-' }
</script>
