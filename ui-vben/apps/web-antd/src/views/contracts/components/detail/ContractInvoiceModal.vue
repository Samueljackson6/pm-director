<template>
  <a-modal
    v-model:open="open"
    title="添加发票"
    :confirm-loading="saving"
    ok-text="保存"
    cancel-text="取消"
    @ok="save"
  >
    <a-form :model="form" layout="vertical">
      <div class="grid grid-cols-2 gap-4">
        <a-form-item label="发票号">
          <a-input v-model:value="form.invoice_no" placeholder="如：INV-2026-001" />
        </a-form-item>
        <a-form-item label="发票日期">
          <a-date-picker v-model:value="form.invoice_date" value-format="YYYY-MM-DD" class="w-full" />
        </a-form-item>
        <a-form-item label="金额（万元）">
          <a-input-number v-model:value="form.amount" :precision="2" :min="0" class="w-full" />
        </a-form-item>
        <a-form-item label="税率（%）">
          <a-input-number v-model:value="form.tax_rate" :precision="2" :min="0" :max="100" class="w-full" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="form.status">
            <a-select-option value="已开">已开</a-select-option>
            <a-select-option value="待开">待开</a-select-option>
          </a-select>
        </a-form-item>
      </div>
      <a-form-item label="备注">
        <a-textarea v-model:value="form.notes" :rows="2" placeholder="补充说明..." />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import { createInvoiceApi } from '#/api/invoices'

const props = defineProps(['open', 'contract', 'contractId'])
const emit = defineEmits(['update:open', 'updated'])
const saving = ref(false)
const form = ref(createForm())
const open = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value),
})

function createForm() {
  return {
    invoice_no: '',
    invoice_date: '',
    amount: null,
    tax_rate: props.contract?.tax_rate ?? null,
    status: '已开',
    notes: '',
  }
}

watch(open, (isOpen) => {
  if (isOpen) form.value = createForm()
})

async function save() {
  saving.value = true
  try {
    await createInvoiceApi({
      ...form.value,
      amount: form.value.amount === null ? null : form.value.amount * 10_000,
      invoice_type: '客户开票',
      direction: 'outbound',
      project_id: props.contractId,
    })
    message.success('发票已创建')
    open.value = false
    emit('updated')
  } catch (cause: unknown) {
    message.error(cause instanceof Error ? `创建失败：${cause.message}` : '创建失败')
  } finally {
    saving.value = false
  }
}
</script>
