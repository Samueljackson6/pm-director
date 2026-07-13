<template>
  <div></div>
</template>

<script lang="ts" setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

onMounted(() => {
  const id = route.params.id || route.query.id
  router.replace({ name: 'CustomerInvoiceDetail', query: { id } })
})
</script>
