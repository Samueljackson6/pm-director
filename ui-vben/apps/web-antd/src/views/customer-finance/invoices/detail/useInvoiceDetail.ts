import { computed, onMounted, ref, watch } from 'vue';
import { message } from 'ant-design-vue';
import { useRoute } from 'vue-router';
import { getInvoiceDetailApi } from '#/api/invoices';
import { requestClient } from '#/api/request';
import type {
  InvoiceFile,
  InvoiceReceipt,
  InvoiceRecord,
  ParsedInvoiceNotes,
} from './types';

function extractErrorMessage(caught: unknown): string {
  if (typeof caught === 'object' && caught !== null && 'response' in caught) {
    const response = caught.response;
    if (
      typeof response === 'object' &&
      response !== null &&
      'data' in response
    ) {
      const data = response.data;
      if (
        typeof data === 'object' &&
        data !== null &&
        'message' in data &&
        typeof data.message === 'string'
      ) {
        return data.message;
      }
    }
  }
  return caught instanceof Error ? caught.message : '未知错误';
}

function calculateTaxAmount(value: InvoiceRecord | null): number | null {
  if (!value) return null;
  if (value.tax_amount != null)
    return value.tax_amount;
  if (value.amount == null || value.tax_rate == null) return null;
  const rate = value.tax_rate;
  const decimalRate = rate <= 1 ? rate : rate / 100;
  return (value.amount * decimalRate) / (1 + decimalRate);
}

function parseNotes(value: InvoiceRecord | null): ParsedInvoiceNotes | null {
  const notes = value?.notes;
  if (!notes) return null;
  const pattern =
    /^([A-Z0-9-]+)(客户开票|客户回款|供应商开票)(\d{4}[-/]\d{1,2}[-/]\d{1,2})(已开|已回款|待开)-(未匹配|已匹配|部分匹配)(\w+)([\d\s:-]+)$/;
  const result = notes.trim().match(pattern);
  if (!result) return null;
  return {
    contractNo: result[1] || '-',
    invoiceType: result[2] || '-',
    invoiceDate: result[3] || '-',
    status: result[4] || '-',
    matchStatus: result[5] || '-',
    source: result[6] || '-',
    processTime: result[7]?.trim() || '-',
  };
}

export function useInvoiceDetail() {
  const route = useRoute();
  const invoice = ref<InvoiceRecord | null>(null);
  const loading = ref(true);
  const error = ref('');
  const invoiceFiles = ref<InvoiceFile[]>([]);
  const linkedReceipts = ref<InvoiceReceipt[]>([]);
  const showLinkReceipt = ref(false);
  const matchedAmount = computed<number | null>(() => {
    const amounts = linkedReceipts.value.map(
      (receipt) => receipt.link_amount ?? receipt.amount,
    );
    if (amounts.some((amount) => amount == null)) return null;
    return amounts.reduce<number>((sum, amount) => sum + Number(amount), 0);
  });
  const calculatedTaxAmount = computed(() => calculateTaxAmount(invoice.value));
  const calculatedTotalWithTax = computed(() => {
    if (!invoice.value) return null;
    return invoice.value.total_with_tax ?? invoice.value.amount ?? null;
  });
  const parsedNotes = computed(() => parseNotes(invoice.value));

  async function loadLinkedReceipts(): Promise<void> {
    if (!invoice.value) return;
    try {
      const data = await requestClient.get<{ receipts?: InvoiceReceipt[] }>(
        `/api/invoices/${invoice.value.invoice_id}/receipts`,
      );
      linkedReceipts.value = data.receipts ?? [];
    } catch {
      linkedReceipts.value = [];
    }
  }

  async function loadInvoiceFiles(): Promise<void> {
    if (!invoice.value) return;
    try {
      const data = await requestClient.get(
        `/api/invoices/${invoice.value.invoice_id}/files`,
      );
      invoiceFiles.value = data.files ?? [];
    } catch {
      invoiceFiles.value = [];
    }
  }

  async function load(): Promise<void> {
    loading.value = true;
    error.value = '';
    try {
      const id = route.params.id || route.query.id;
      const data = await getInvoiceDetailApi(Number(id));
      invoice.value = data.invoice ?? null;
      if (!invoice.value) error.value = '未找到该发票';
      else await Promise.all([loadInvoiceFiles(), loadLinkedReceipts()]);
    } catch (caught: unknown) {
      error.value = extractErrorMessage(caught);
    } finally {
      loading.value = false;
    }
  }

  async function handleFileChange(event: Event): Promise<void> {
    const input = event.target;
    if (!(input instanceof HTMLInputElement) || !invoice.value) return;
    const file = input.files?.[0];
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append('file', file);
      await requestClient.post(
        `/api/invoices/${invoice.value.invoice_id}/files`,
        formData,
      );
      message.success('文件上传成功');
      await loadInvoiceFiles();
    } catch (caught: unknown) {
      message.error(`上传失败: ${extractErrorMessage(caught)}`);
    } finally {
      input.value = '';
    }
  }

  async function downloadFile(file: InvoiceFile): Promise<void> {
    if (!invoice.value) return;
    try {
      const response = await fetch(
        `/api/invoices/${invoice.value.invoice_id}/files/${file.file_id}`,
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = file.file_name;
      anchor.click();
      window.URL.revokeObjectURL(url);
    } catch (caught: unknown) {
      message.error(`下载失败: ${extractErrorMessage(caught)}`);
    }
  }

  async function deleteFile(file: InvoiceFile): Promise<void> {
    if (!invoice.value) return;
    try {
      await requestClient.delete(
        `/api/invoices/${invoice.value.invoice_id}/files/${file.file_id}`,
      );
      message.success('文件已删除');
      await loadInvoiceFiles();
    } catch (caught: unknown) {
      message.error(`删除失败: ${extractErrorMessage(caught)}`);
    }
  }

  async function unlinkReceipt(receipt: InvoiceReceipt): Promise<void> {
    if (!invoice.value) return;
    try {
      await requestClient.delete(
        `/api/invoices/${invoice.value.invoice_id}/receipts/${receipt.receipt_id}`,
      );
      message.success('已取消关联');
      await loadLinkedReceipts();
    } catch (caught: unknown) {
      message.error(`操作失败: ${extractErrorMessage(caught)}`);
    }
  }

  onMounted(load);
  watch(
    () => route.params.id || route.query.id,
    (current, previous) => {
      if (current && current !== previous) void load();
    },
  );

  return {
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
  };
}
