<template>
  <div
    class="min-h-screen space-y-4 overflow-x-hidden bg-slate-50 px-4 py-4 md:px-6"
  >
    <InvoiceActions
      :invoice="invoice"
      :status-color="statusColor"
      :payment-status-color="paymentStatusColor"
      @changed="load"
    />
    <state-block
      :loading="loading"
      :error="error"
      error-title="发票详情加载失败"
      @retry="load"
    >
      <template v-if="invoice">
        <div
          class="sticky top-0 z-20 rounded-xl border border-slate-200 bg-white/90 px-4 shadow-sm backdrop-blur"
        >
          <div class="flex gap-2 overflow-x-auto py-3">
            <button
              v-for="anchor in anchors"
              :key="anchor.id"
              class="whitespace-nowrap rounded-md px-3 py-1.5 text-sm"
              :class="
                activeAnchor === anchor.id
                  ? 'bg-blue-50 font-medium text-blue-600'
                  : 'text-gray-500 hover:bg-gray-100'
              "
              @click="scrollToAnchor(anchor.id)"
            >
              {{ anchor.label }}
            </button>
          </div>
        </div>
        <InvoiceOverview
          :invoice="invoice"
          :parsed-notes="parsedNotes"
          :calculated-tax-amount="calculatedTaxAmount"
          :total_with_tax="calculatedTotalWithTax"
          :fmt-money="fmtMoney"
          :status-color="statusColor"
          :payment-status-color="paymentStatusColor"
          :invoice-type-color="invoiceTypeColor"
        />
        <InvoiceReceiptRelations
          :linked-receipts="linkedReceipts"
          :matched-amount="matchedAmount"
          :invoice-amount="invoice.amount ?? null"
          :fmt-money="fmtMoney"
          @unlink-receipt="unlinkReceipt"
          @link-receipt="showLinkReceipt = true"
        />
        <InvoiceAttachments
          :invoice-files="invoiceFiles"
          :file-icon="fileIcon"
          :format-size="formatSize"
          @upload-file="handleFileChange"
          @download-file="downloadFile"
          @delete-file="deleteFile"
        />
      </template>
    </state-block>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onUnmounted, ref, watch } from 'vue';
import StateBlock from '#/components/state-block/index.vue';
import InvoiceActions from './detail/InvoiceActions.vue';
import InvoiceAttachments from './detail/InvoiceAttachments.vue';
import InvoiceOverview from './detail/InvoiceOverview.vue';
import InvoiceReceiptRelations from './detail/InvoiceReceiptRelations.vue';
import { useInvoiceDetail } from './detail/useInvoiceDetail';

const {
  calculatedTaxAmount,
  calculatedTotalWithTax,
  deleteFile,
  downloadFile,
  error,
  handleFileChange,
  invoice,
  invoiceFiles,
  linkedReceipts,
  load,
  loading,
  matchedAmount,
  parsedNotes,
  showLinkReceipt,
  unlinkReceipt,
} = useInvoiceDetail();

const anchors = [
  { id: 'project', label: '项目' },
  { id: 'invoice', label: '发票' },
  { id: 'amount', label: '金额' },
  { id: 'receipts', label: '回款' },
  { id: 'files', label: '文件' },
  { id: 'system', label: '系统' },
] as const;
const activeAnchor = ref('project');
let anchorObserver: IntersectionObserver | null = null;

function scrollToAnchor(id: string): void {
  const element = document.getElementById(id);
  if (!element) return;
  window.scrollTo({
    top: element.getBoundingClientRect().top + window.pageYOffset - 56,
    behavior: 'smooth',
  });
}
function fmtMoney(value: number | null | undefined): string {
  if (value == null) return '待核验';
  if (value === 0) return '0.00';
  return value.toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
}
function statusColor(value: string | undefined): string {
  return (
    { 已开: 'blue', 已回款: 'green', 待开: 'orange' }[value || ''] || 'default'
  );
}
function paymentStatusColor(value: string | undefined): string {
  return { 已匹配: 'green', 未匹配: 'default' }[value || ''] || 'default';
}
function invoiceTypeColor(value: string | undefined): string {
  return (
    { 客户开票: 'blue', 客户回款: 'green', 供应商开票: 'orange' }[
      value || ''
    ] || 'default'
  );
}
function fileIcon(value: string | undefined): string {
  if (!value) return '📄';
  if (value.toLowerCase().includes('pdf')) return '📕';
  if (value.toLowerCase().includes('image')) return '🖼️';
  return '📄';
}
function formatSize(value: number | undefined): string {
  if (!value) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const index = Math.floor(Math.log(value) / Math.log(1024));
  return `${(value / Math.pow(1024, index)).toFixed(1)} ${units[index] || 'GB'}`;
}

watch(
  () => invoice.value,
  () => {
    nextTick(() => {
      anchorObserver?.disconnect();
      anchorObserver = new IntersectionObserver(
        (entries) =>
          entries.forEach((entry) => {
            if (entry.isIntersecting) activeAnchor.value = entry.target.id;
          }),
        { rootMargin: '-56px 0px -70% 0px' },
      );
      anchors.forEach((anchor) => {
        const element = document.getElementById(anchor.id);
        if (element) anchorObserver?.observe(element);
      });
    });
  },
  { flush: 'post' },
);
onUnmounted(() => anchorObserver?.disconnect());
</script>

<style scoped>
.scroll-mt-16 {
  scroll-margin-top: 64px;
}
</style>
