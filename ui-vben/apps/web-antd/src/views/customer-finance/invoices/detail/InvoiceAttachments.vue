<template>
  <section
    id="files"
    class="scroll-mt-16 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"
  >
    <header
      class="flex flex-wrap items-center gap-2 border-b border-slate-100 bg-slate-50/80 px-4 py-3 sm:px-5"
    >
      <span class="h-4 w-1 rounded-full bg-slate-400"></span
      ><span class="text-sm font-semibold text-slate-700">发票文件</span
      ><a-button
        type="link"
        size="small"
        class="ml-auto"
        @click="fileInput?.click()"
        >上传文件</a-button
      >
    </header>
    <div class="px-4 py-4 sm:px-5">
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
        @change="handleFileChange"
      /><template v-if="invoiceFiles.length"
        ><div class="space-y-2">
          <div
            v-for="file in invoiceFiles"
            :key="file.file_id"
            class="flex flex-col gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <div class="truncate text-sm font-medium text-slate-900">
                {{ fileIcon(file.file_type) }} {{ file.file_name }}
              </div>
              <div class="mt-1 text-xs text-slate-500">
                {{ file.file_type?.toUpperCase() || 'FILE' }} ·
                {{ formatSize(file.file_size) }}
              </div>
            </div>
            <div>
              <a-button
                size="small"
                type="link"
                @click="$emit('downloadFile', file)"
                >下载</a-button
              ><a-popconfirm
                title="确定删除此文件？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="$emit('deleteFile', file)"
                ><a-button size="small" type="link" danger
                  >删除</a-button
                ></a-popconfirm
              >
            </div>
          </div>
        </div></template
      ><a-empty v-else description="暂无发票文件" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { InvoiceFile } from './types';

const fileInput = ref<HTMLInputElement>();
const emit = defineEmits<{
  uploadFile: [event: Event];
  downloadFile: [file: InvoiceFile];
  deleteFile: [file: InvoiceFile];
}>();
defineProps<{
  readonly invoiceFiles: readonly InvoiceFile[];
  readonly fileIcon: (value: string | undefined) => string;
  readonly formatSize: (value: number | undefined) => string;
}>();
function handleFileChange(event: Event): void {
  emit('uploadFile', event);
}
</script>
