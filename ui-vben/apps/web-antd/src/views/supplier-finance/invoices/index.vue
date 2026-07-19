<template>
  <div class="p-6 bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">供应商发票</h1>
        <p class="text-sm text-gray-500 mt-1">供应商向我们开具的发票</p>
      </div>
      <a-button type="primary" size="large" @click="openAdd">+ 新增发票</a-button>
    </div>
    <a-card class="rounded-lg" :body-style="{ padding: 0 }">
      <div class="p-4 border-b border-gray-100"><h3 class="text-base font-semibold">发票列表</h3></div>
      <div class="p-4">
        <a-table :data-source="list" :columns="columns" :loading="loading" row-key="invoice_id" size="middle"
          :pagination="{ pageSize: 50, total, showSizeChanger: true, showTotal: t => '共 ' + t + ' 条' }"
          @change="handleChange">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'amount'"><span class="font-mono">{{ (record.amount || 0).toFixed(2) }}</span></template>
            <template v-if="column.key === 'status'"><a-tag :color="record.status === '已开' ? 'blue' : 'default'">{{ record.status }}</a-tag></template>
            <template v-if="column.key === 'action'">
              <a-button type="link" size="small" @click="viewDetail(record)">详情</a-button>
              <a-button type="link" size="small" @click="editRecord(record)">编辑</a-button>
              <a-popconfirm title="删除此发票？" @confirm="deleteRecord(record)">
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </template>
          </template>
        </a-table>
      </div>
    </a-card>
    <a-modal v-model:open="modalVisible" :title="editingId ? '编辑发票' : '新增发票'" :confirm-loading="saving" @ok="saveRecord" width="600px">
      <a-form :model="form" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12"><a-form-item label="项目编号" required><a-input v-model:value="form.project_id" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="发票日期" required><a-date-picker v-model:value="form.invoice_date" value-format="YYYY-MM-DD" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="金额（元）" required><a-input-number v-model:value="form.amount" :precision="2" :min="0" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="状态"><a-select v-model:value="form.status"><a-select-option value="已开">已开</a-select-option><a-select-option value="待开">待开</a-select-option></a-select></a-form-item></a-col>
          <a-col :span="24"><a-form-item label="备注"><a-textarea v-model:value="form.notes" :rows="2" /></a-form-item></a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>
<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getInvoicesApi, createInvoiceApi, updateInvoiceApi, deleteInvoiceApi, type InvoiceItem } from '#/api/invoices'
import { buildDetailLocation } from '#/utils/business-navigation'

const route = useRoute()
const router = useRouter()
const list = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const modalVisible = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Record<string, any>>({})
const columns = [
  { title: '发票日期', dataIndex: 'invoice_date', key: 'invoice_date', width: 110 },
  { title: '供应商', dataIndex: 'supplier_name', key: 'supplier_name', width: 160, ellipsis: true },
  { title: '项目编号', dataIndex: 'project_id', key: 'project_id', width: 200, ellipsis: true },
  { title: '金额（元）', dataIndex: 'amount', key: 'amount', width: 130, align: 'right' as const },
  { title: '状态', dataIndex: 'status', key: 'status', width: 90 },
  { title: '操作', key: 'action', width: 200, fixed: 'right' as const },
]

async function load() {
  loading.value = true
  try {
    const data = await getInvoicesApi({ page: page.value, size: 50, direction: 'inbound' })
    list.value = data.items ?? []
    total.value = data.total ?? 0
  } catch { /* ignore */ } finally { loading.value = false }
}

function handleChange(p: any) { page.value = p.current; load() }
function viewDetail(row: InvoiceItem) {
  router.push(
    buildDetailLocation({
      from: {
        name: route.name,
        query: { ...route.query, page: String(page.value), pageSize: '50' },
      },
      id: String(row.invoice_id),
      name: 'SupplierInvoiceDetail',
    }),
  )
}
function openAdd() { editingId.value = null; form.value = { project_id: '', invoice_date: '', amount: null, status: '已开', direction: 'inbound', invoice_type: '供应商开票' }; modalVisible.value = true }
function editRecord(r: any) { editingId.value = r.invoice_id; form.value = { ...r }; modalVisible.value = true }
async function saveRecord() {
  saving.value = true
  try {
    editingId.value ? await updateInvoiceApi(editingId.value, form.value) : await createInvoiceApi(form.value)
    message.success('保存成功'); modalVisible.value = false; load()
  } catch (e: any) { message.error('失败: ' + (e?.message || ''))
  } finally { saving.value = false }
}
async function deleteRecord(r: any) {
  try { await deleteInvoiceApi(r.invoice_id); message.success('已删除'); load()
  } catch (e: any) { message.error('删除失败: ' + (e?.message || '')) }
}
onMounted(load)
</script>
