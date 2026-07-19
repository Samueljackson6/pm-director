<script lang="ts" setup>
import type { EvidenceItem } from '../review-data';

defineProps<{
  items: readonly EvidenceItem[];
}>();

const statusLabels: Record<EvidenceItem['status'], string> = {
  available: '可追溯',
  needs_review: '待核验',
  verified: '已核验',
};
</script>

<template>
  <section class="evidence-rail" aria-label="合同证据轨道">
    <div v-for="(item, index) in items" :key="item.kind" class="evidence-node">
      <div class="evidence-node__marker" :data-status="item.status">
        <span>{{ index + 1 }}</span>
      </div>
      <div class="evidence-node__body">
        <div class="flex items-center justify-between gap-2">
          <strong>{{ item.label }}</strong>
          <span class="evidence-node__status" :data-status="item.status">
            {{ statusLabels[item.status] }}
          </span>
        </div>
        <p>{{ item.note }}</p>
      </div>
    </div>
  </section>
</template>
