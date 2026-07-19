<template>
  <div class="dashboard-toolbar" aria-label="驾驶舱数据操作">
    <p>
      聚合生成时间：{{ formattedTime }}
      <span aria-hidden="true"> · </span>
      金额单位：{{ unit || '万元' }}
    </p>
    <a-button :loading="loading" @click="$emit('refresh')">刷新聚合</a-button>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

const props = defineProps<{
  generatedAt?: string
  loading?: boolean
  unit?: string
}>()

defineEmits<{ refresh: [] }>()

const formattedTime = computed(() => {
  if (!props.generatedAt) return '待加载'
  return props.generatedAt.replace('T', ' ').slice(0, 16)
})
</script>
