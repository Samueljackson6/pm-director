<template>
  <a-modal v-model:open="open" title="编辑合同" width="800px" :confirm-loading="saving" ok-text="保存" cancel-text="取消" @ok="save">
    <ContractEditFields v-if="form" :form="form" />
  </a-modal>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import { updateContractApi } from '#/api/contracts'
import ContractEditFields from '#/views/contracts/components/detail/ContractEditFields.vue'

const props = defineProps(['open', 'contract', 'contractId', 'stages', 'deliverables'])
const emit = defineEmits(['update:open', 'updated'])
const saving = ref(false)
const form = ref()
const open = computed({ get: () => props.open, set: (value) => emit('update:open', value) })
watch(open, (isOpen) => {
  if (isOpen) form.value = {
    ...props.contract,
    editStages: structuredClone(props.stages ?? []),
    editDeliverables: structuredClone(props.deliverables ?? []),
  }
})
async function save() {
  if (!form.value) return
  saving.value = true
  try {
    const payload = { ...form.value }
    if (payload.project_type === '科研类') { payload.stages = payload.editStages; payload.deliverables = payload.editDeliverables }
    await updateContractApi(props.contractId, payload)
    message.success('合同更新成功')
    open.value = false
    emit('updated')
  } catch (cause: unknown) { message.error(cause instanceof Error ? `更新失败：${cause.message}` : '更新失败') }
  finally { saving.value = false }
}
</script>
