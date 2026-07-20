<template>
  <div
    :class="[
      `dashboard-metric-card--${tone}`,
      { 'dashboard-metric-card--clickable': clickable },
    ]"
    class="dashboard-metric-card"
    role="group"
    @click="handleClick"
  >
    <div class="dashboard-metric-card__label">{{ label }}</div>
    <div class="dashboard-metric-card__value">
      {{ displayValue }}<span class="dashboard-metric-card__unit">{{ unit }}</span>
    </div>
    <div v-if="sub || ratio || hint" class="dashboard-metric-card__hint">
      {{ sub || ratio || hint }}
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

import type { DashTone } from '../dashboard-types'

const props = withDefaults(
  defineProps<{
    clickable?: boolean
    digits?: number
    hint?: string
    label: string
    ratio?: string
    sub?: string
    tone?: DashTone
    unit?: string
    value: number | null | undefined
  }>(),
  { clickable: false, digits: 2, tone: 'none', unit: '' },
)

const emit = defineEmits<{ click: [] }>()

const displayValue = computed(() => {
  if (props.value == null || Number.isNaN(props.value)) return '???'
  return Number(props.value).toLocaleString('zh-CN', {
    minimumFractionDigits: props.digits,
    maximumFractionDigits: props.digits,
  })
})

function handleClick() {
  if (props.clickable) emit('click')
}
</script>
