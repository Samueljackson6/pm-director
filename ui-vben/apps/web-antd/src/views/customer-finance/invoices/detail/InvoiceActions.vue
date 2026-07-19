<template>
  <div class="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm lg:flex-row lg:items-center lg:justify-between">
    <div class="flex items-center gap-4">
      <a-button
        type="text"
        class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-slate-600"
        @click="goBack"
        ><span class="text-lg">←</span></a-button
      >
      <div>
        <h2 class="truncate text-xl font-semibold text-slate-900">发票详情</h2>
        <div class="mt-1 truncate text-sm text-slate-500">
          {{
            props.invoice?.invoice_no ||
            (props.invoice ? '发票 #' + props.invoice.invoice_id : '')
          }}
        </div>
      </div>
    </div>
    <div class="flex flex-wrap items-center gap-2 lg:justify-end">
      <a-tag
        v-if="props.invoice?.status"
        :color="props.statusColor(props.invoice.status)"
        >{{ props.invoice.status }}</a-tag
      ><a-tag
        v-if="props.invoice?.payment_status"
        :color="props.paymentStatusColor(props.invoice.payment_status)"
        >{{ props.invoice.payment_status }}</a-tag
      ><a-button type="primary" size="small" ghost @click="openEditModal"
        >编辑</a-button
      ><a-popconfirm
        title="确定要删除这张发票吗？"
        ok-text="确定"
        cancel-text="取消"
        @confirm="deleteInvoice"
        ><a-button type="primary" size="small" danger ghost
          >删除</a-button
        ></a-popconfirm
      >
    </div>
  </div>
  <a-modal
    v-model:open="editModalVisible"
    title="编辑发票"
    :confirm-loading="editSaving"
    @ok="saveEdit"
    ok-text="保存"
    cancel-text="取消"
    width="600px"
    ><a-form :model="editForm" layout="vertical"
      ><a-row :gutter="16"
        ><a-col :span="12"
          ><a-form-item label="发票编号"
            ><a-input
              v-model:value="editForm.invoice_no" /></a-form-item></a-col
        ><a-col :span="12"
          ><a-form-item label="发票日期"
            ><a-date-picker
              v-model:value="editForm.invoice_date"
              value-format="YYYY-MM-DD"
              class="w-full" /></a-form-item></a-col
        ><a-col :span="12"
          ><a-form-item label="金额（元）"
            ><a-input-number
              v-model:value="editForm.amount"
              :precision="2"
              :min="0"
              class="w-full" /></a-form-item></a-col
        ><a-col :span="12"
          ><a-form-item label="税率（%）"
            ><a-input-number
              v-model:value="editForm.tax_rate"
              :precision="2"
              :min="0"
              :max="100"
              class="w-full" /></a-form-item></a-col
        ><a-col :span="12"
          ><a-form-item label="税额（元）"
            ><a-input-number
              v-model:value="editForm.tax_amount"
              :precision="2"
              :min="0"
              class="w-full" /></a-form-item></a-col
        ><a-col :span="12"
          ><a-form-item label="价税合计（元）"
            ><a-input-number
              v-model:value="editForm.total_with_tax"
              :precision="2"
              :min="0"
              class="w-full" /></a-form-item></a-col
        ><a-col :span="12"
          ><a-form-item label="状态"
            ><a-select v-model:value="editForm.status"
              ><a-select-option value="已开">已开</a-select-option
              ><a-select-option value="已回款">已回款</a-select-option
              ><a-select-option value="待开">待开</a-select-option></a-select
            ></a-form-item
          ></a-col
        ><a-col :span="12"
          ><a-form-item label="回款日期"
            ><a-date-picker
              v-model:value="editForm.received_date"
              value-format="YYYY-MM-DD"
              class="w-full" /></a-form-item></a-col
        ><a-col :span="24"
          ><a-form-item label="备注"
            ><a-textarea
              v-model:value="editForm.notes"
              :rows="2" /></a-form-item></a-col></a-row></a-form
  ></a-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import { deleteInvoiceApi, updateInvoiceApi } from '#/api/invoices';
import type { InvoiceEditForm, InvoiceRecord } from './types';

const emit = defineEmits<{ changed: [] }>();
const props = defineProps<{
  readonly invoice: InvoiceRecord | null;
  readonly statusColor: (value: string | undefined) => string;
  readonly paymentStatusColor: (value: string | undefined) => string;
}>();
const router = useRouter();
const editModalVisible = ref(false);
const editSaving = ref(false);
const editForm = ref<InvoiceEditForm>({
  invoice_no: '',
  invoice_date: '',
  amount: null,
  tax_rate: null,
  tax_amount: null,
  total_with_tax: null,
  status: '已开',
  received_date: '',
  notes: '',
});
function goBack(): void {
  router.push({ name: 'CustomerInvoices' });
}
function openEditModal(): void {
  if (!props.invoice) return;
  const value = props.invoice;
  editForm.value = {
    invoice_no: value.invoice_no || '',
    invoice_date: value.invoice_date || '',
    amount: value.amount ?? null,
    tax_rate: value.tax_rate ?? null,
    tax_amount: value.tax_amount ?? null,
    total_with_tax: value.total_with_tax ?? null,
    status: value.status || '已开',
    received_date: value.received_date || '',
    notes: value.notes || '',
  };
  editModalVisible.value = true;
}
async function saveEdit(): Promise<void> {
  if (!props.invoice) return;
  editSaving.value = true;
  try {
    await updateInvoiceApi(props.invoice.invoice_id, editForm.value);
    message.success('发票更新成功');
    editModalVisible.value = false;
    emit('changed');
  } catch (caught: unknown) {
    message.error(
      `更新失败: ${caught instanceof Error ? caught.message : '未知错误'}`,
    );
  } finally {
    editSaving.value = false;
  }
}
async function deleteInvoice(): Promise<void> {
  if (!props.invoice) return;
  try {
    await deleteInvoiceApi(props.invoice.invoice_id);
    message.success('发票已删除');
    router.push({ name: 'CustomerInvoices' });
  } catch (caught: unknown) {
    message.error(
      `删除失败: ${caught instanceof Error ? caught.message : '未知错误'}`,
    );
  }
}
</script>
