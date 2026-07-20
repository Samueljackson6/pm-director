<template>
  <nav aria-label="驾驶舱决策视角" class="dashboard-tabs" role="tablist">
    <button
      v-for="tab in tabs"
      :id="`dashboard-tab-${tab.key}`"
      :key="tab.key"
      :aria-controls="`dashboard-panel-${tab.key}`"
      :aria-selected="modelValue === tab.key"
      :class="{ 'dashboard-tabs__item--active': modelValue === tab.key }"
      class="dashboard-tabs__item"
      role="tab"
      type="button"
      @click="select(tab.key)"
    >
      {{ tab.label }}
    </button>
  </nav>
</template>

<script lang="ts" setup>
import type { ViewKey } from '../dashboard-types'

const props = defineProps<{ modelValue: ViewKey }>()
const emit = defineEmits<{
  change: [value: ViewKey]
  'update:modelValue': [value: ViewKey]
}>()

const tabs: Array<{ key: ViewKey; label: string }> = [
  { key: 'all', label: '综合' },
  { key: 'management', label: '经营' },
  { key: 'projects', label: '项目' },
  { key: 'finance', label: '财务' },
  { key: 'verification', label: '数据核验' },
]

function select(key: ViewKey) {
  emit('update:modelValue', key)
  if (key !== props.modelValue) emit('change', key)
}
</script>
