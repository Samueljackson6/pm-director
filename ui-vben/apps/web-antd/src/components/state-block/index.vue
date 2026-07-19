<script lang="ts" setup>
/**
 * 共享状态容器：统一 loading / error / empty 三态。
 * 详情页用它包裹业务内容，保证系统状态可见性（ardot design-rules §6）。
 */
defineProps<{
  empty?: boolean;
  emptyText?: string;
  error?: string;
  errorTitle?: string;
  loading?: boolean;
}>();

defineEmits<{ retry: [] }>();
</script>

<template>
  <div>
    <!-- Loading 态 -->
    <div
      v-if="loading"
      aria-live="polite"
      class="flex items-center justify-center py-20 text-muted-foreground"
      role="status"
    >
      <a-spin />
      <span class="ml-2">加载中…</span>
    </div>

    <!-- Error 态（带重试） -->
    <div
      v-else-if="error"
      class="rounded-lg border border-destructive/50 bg-destructive/10 p-6 text-center"
      role="alert"
    >
      <p class="font-medium text-destructive">{{ errorTitle || '加载失败' }}</p>
      <p class="mt-1 text-sm text-muted-foreground">{{ error }}</p>
      <button
        class="mt-3 rounded border px-3 py-1 text-sm hover:bg-accent"
        @click="$emit('retry')"
      >
        重试
      </button>
    </div>

    <!-- Empty 态 -->
    <div
      v-else-if="empty"
      aria-live="polite"
      class="flex flex-col items-center justify-center py-20 text-muted-foreground"
      role="status"
    >
      <span class="text-4xl opacity-40">∅</span>
      <p class="mt-2 text-sm">{{ emptyText || '暂无数据' }}</p>
    </div>

    <!-- 正常内容 -->
    <slot v-else></slot>
  </div>
</template>
