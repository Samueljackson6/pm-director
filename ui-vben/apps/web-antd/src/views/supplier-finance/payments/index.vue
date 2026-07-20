<template>
  <div class="pm-workbench-page min-h-screen p-4 sm:p-6">
    <header class="pm-page-header flex items-start justify-between gap-4">
      <div>
        <p class="pm-section-kicker">供应链资金</p>
        <h1>供应商付款</h1>
        <p class="pm-section-note">优先处理待付款与待核验记录，保持客户回款与供应商付款分轨管理。</p>
      </div>
      <a-button type="primary" size="large" @click="openAdd">+ 新增付款</a-button>
    </header>
    <a-card class="pm-table-surface" :body-style="{ padding: 0 }" aria-label="供应商付款列表">
      <div class="p-4 border-b border-gray-100"><h3 class="text-base font-semibold">付款列表</h3><p class="mt-1 text-xs text-gray-500">仅展示供应商付款记录；客户回款与供应商收票分别管理，不会混入本列表。</p></div>
      <div class="p-4">
        <a-alert v-if="dataState !== 'available'" class="mb-4" :type="dataState === 'pending_verification' ? 'warning' : 'info'" show-icon :message="dataStateText" />
        <a-table :data-source="list" :columns="columns" :loading="loading" row-key="payment_id" size="middle"
          :pagination="{ pageSize: 50, total, showSizeChanger: true, showTotal: (t: number) => '共 ' + t + ' 条' }"
          @change="handleChange">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'amount'"><span class="font-mono">{{ formatAmount(record.amount) }}</span></template>
            <template v-if="column.key === 'status'"><a-tag :color="record.status === '已完成' ? 'green' : 'orange'">{{ record.status }}</a-tag></template>
            <template v-if="column.key === 'action'">
              <a-button type="link" size="small" @click="viewDetail(record)">详情</a-button>
              <a-button type="link" size="small" @click="editRecord(record)">编辑</a-button>
              <a-popconfirm title="删除此付款记录？" @confirm="deleteRecord(record)">
                <a-button type="link" size="small" danger>删除</a-button>
              </a-popconfirm>
            </template>
          </template>
        </a-table>
      </div>
    </a-card>
    <a-modal v-model:open="modalVisible" :title="editingId ? '编辑付款' : '新增付款'" :confirm-loading="saving" @ok="saveRecord" width="600px">
      <a-form :model="form" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12"><a-form-item label="项目编号" required><a-input v-model:value="form.project_id" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="付款日期" required><a-date-picker v-model:value="form.payment_date" value-format="YYYY-MM-DD" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="付款金额（元）" required><a-input-number v-model:value="form.amount" :precision="2" :min="0" class="w-full" /></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="付款方式"><a-select v-model:value="form.payment_method"><a-select-option value="银行转账">银行转账</a-select-option><a-select-option value="电汇">电汇</a-select-option></a-select></a-form-item></a-col>
          <a-col :span="12"><a-form-item label="状态"><a-select v-model:value="form.status"><a-select-option value="已完成">已完成</a-select-option><a-select-option value="待支付">待支付</a-select-option></a-select></a-form-item></a-col>
          <a-col :span="24"><a-form-item label="备注"><a-textarea v-model:value="form.notes" :rows="2" /></a-form-item></a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>
<script lang="ts" setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { requestClient } from '#/api/request'
import { buildDetailLocation } from '#/utils/business-navigation'

interface SupplierPaymentListItem {
  payment_id: number
}

const route = useRoute()
const router = useRouter()
const list = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const dataState = ref<'available' | 'known_zero' | 'pending_verification' | 'source_not_established'>('known_zero')
const dataStateText = computed(() => ({
  source_not_established: '付款数据源尚未建立，当前无法确认是否存在供应商付款。',
  known_zero: '当前筛选范围内已知没有供应商付款。',
  pending_verification: '存在金额缺失或异常的供应商付款，请人工核验。',
  available: '',
})[dataState.value])
const modalVisible = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Record<string, any>>({})
const columns = [
  { title: '付款日期', dataIndex: 'payment_date', key: 'payment_date', width: 110 },
  { title: '项目编号', dataIndex: 'project_id', key: 'project_id', width: 200, ellipsis: true },
  { title: '付款金额（元）', dataIndex: 'amount', key: 'amount', width: 130, align: 'right' as const },
  { title: '付款方式', dataIndex: 'payment_method', key: 'payment_method', width: 100 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 90 },
  { title: '操作', key: 'action', width: 150, fixed: 'right' as const },
]

async function load() {
  loading.value = true
  try {
    const data: any = await requestClient.get('/api/suppliers/payments', { params: { page: page.value, size: 50 } })
    list.value = data.items ?? []; total.value = data.total ?? 0
    dataState.value = data.data_state ?? (list.value.length ? 'available' : 'known_zero')
  } catch { /* ignore */ } finally { loading.value = false }
}
function formatAmount(value: number | null | undefined) { return value == null ? '待核验' : Number(value).toFixed(2) }
function handleChange(p: any) { page.value = p.current; load() }
function viewDetail(row: SupplierPaymentListItem) {
  router.push(
    buildDetailLocation({
      from: {
        name: route.name,
        query: { ...route.query, page: String(page.value), pageSize: '50' },
      },
      id: String(row.payment_id),
      name: 'SupplierPaymentDetail',
    }),
  )
}
function openAdd() { editingId.value = null; form.value = { project_id: '', payment_date: '', amount: null, payment_method: '银行转账', status: '已完成', notes: '' }; modalVisible.value = true }
function editRecord(r: any) { editingId.value = r.payment_id; form.value = { ...r }; modalVisible.value = true }
async function saveRecord() {
  saving.value = true
  try {
    if (editingId.value) { await requestClient.put('/api/suppliers/payments/' + editingId.value, form.value) }
    else { await requestClient.post('/api/suppliers/payments', form.value) }
    message.success('保存成功'); modalVisible.value = false; load()
  } catch (e: any) { message.error('失败: ' + (e?.message || ''))
  } finally { saving.value = false }
}
async function deleteRecord(r: any) {
  try { await requestClient.delete('/api/suppliers/payments/' + r.payment_id); message.success('已删除'); load()
  } catch (e: any) { message.error('删除失败: ' + (e?.message || '')) }
}
onMounted(load)
</script>
