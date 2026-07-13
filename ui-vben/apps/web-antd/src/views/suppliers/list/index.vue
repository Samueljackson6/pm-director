<template>
  <div class="p-6">
    <a-card title="供应商列表" :bordered="false">
      <template #extra>
        <a-space>
          <a-input-search
            v-model:value="searchText"
            placeholder="搜索供应商名称"
            style="width: 200px"
            @search="handleSearch"
          />
          <a-button type="primary" @click="openAddModal">
            <template #icon><PlusOutlined /></template>
            新增供应商
          </a-button>
        </a-space>
      </template>

      <vxe-table
        :data="filteredSuppliers"
        :loading="loading"
        stripe
        highlight-hover-row
        @cell-click="handleCellClick"
      >
        <vxe-column field="supplier_name" title="供应商名称" min-width="200">
          <template #default="{ row }">
            <a class="text-blue-600 hover:underline">{{ row.supplier_name }}</a>
          </template>
        </vxe-column>
        <vxe-column field="short_name" title="简称" width="120" />
        <vxe-column field="category" title="分类" width="100">
          <template #default="{ row }">
            <a-tag :color="categoryColor(row.category)">{{ row.category || '未分类' }}</a-tag>
          </template>
        </vxe-column>
        <vxe-column field="total_contract_amount" title="合同总额（万元）" width="140" align="right">
          <template #default="{ row }">
            <span class="font-semibold">{{ formatMoney(row.total_contract_amount) }}</span>
          </template>
        </vxe-column>
        <vxe-column field="contract_count" title="合同数" width="80" align="center" />
        <vxe-column field="total_invoiced" title="已开票（万元）" width="120" align="right">
          <template #default="{ row }">
            <span class="text-blue-600">{{ formatMoney(row.total_invoiced) }}</span>
          </template>
        </vxe-column>
        <vxe-column field="total_paid" title="已付款（万元）" width="120" align="right">
          <template #default="{ row }">
            <span class="text-green-600">{{ formatMoney(row.total_paid) }}</span>
          </template>
        </vxe-column>
        <vxe-column field="total_unpaid" title="未付款（万元）" width="120" align="right">
          <template #default="{ row }">
            <span class="text-red-500 font-semibold">{{ formatMoney(row.total_unpaid) }}</span>
          </template>
        </vxe-column>
        <vxe-column field="status" title="状态" width="80" align="center">
          <template #default="{ row }">
            <a-tag :color="row.status === 'active' ? 'green' : 'default'">
              {{ row.status === 'active' ? '合作中' : '已停用' }}
            </a-tag>
          </template>
        </vxe-column>
        <vxe-column title="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <a-button type="link" size="small" @click.stop="viewDetail(row)">
              详情
            </a-button>
          </template>
        </vxe-column>
      </vxe-table>
    </a-card>

    <!-- 新增供应商弹窗 -->
    <a-modal
      v-model:open="addModalVisible"
      title="新增供应商"
      width="600px"
      :confirm-loading="addSaving"
      @ok="handleAddSupplier"
      ok-text="确定"
      cancel-text="取消"
    >
      <a-form :model="addForm" layout="vertical">
        <a-form-item label="是否从企查查获取企业信息">
          <a-switch v-model:checked="addForm.fetchFromQcc" />
          <span class="ml-2 text-xs text-gray-400">
            开启后，输入统一社会信用代码自动填充企业信息
          </span>
        </a-form-item>

        <a-form-item v-if="addForm.fetchFromQcc" label="统一社会信用代码" required>
          <a-input
            v-model:value="addForm.creditCode"
            placeholder="请输入统一社会信用代码"
            @blur="handleFetchQccInfo"
          />
          <div v-if="qccLoading" class="mt-2 text-xs text-blue-600">
            <LoadingOutlined spin /> 正在从企查查获取企业信息...
          </div>
        </a-form-item>

        <a-divider />

        <a-form-item label="供应商名称" required>
          <a-input
            v-model:value="addForm.supplier_name"
            placeholder="供应商全称"
            :disabled="addForm.fetchFromQcc && qccDataFilled"
          />
        </a-form-item>

        <a-form-item label="简称">
          <a-input v-model:value="addForm.short_name" placeholder="供应商简称" />
        </a-form-item>

        <a-form-item label="统一社会信用代码" :required="!addForm.fetchFromQcc">
          <a-input
            v-model:value="addForm.credit_code"
            placeholder="18位统一社会信用代码"
            :disabled="addForm.fetchFromQcc"
          />
        </a-form-item>

        <a-form-item label="分类">
          <a-select v-model:value="addForm.category" placeholder="选择供应商分类">
            <a-select-option value="服务类">服务类</a-select-option>
            <a-select-option value="物资类">物资类</a-select-option>
            <a-select-option value="施工类">施工类</a-select-option>
            <a-select-option value="科研类">科研类</a-select-option>
            <a-select-option value="其他">其他</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="联系人">
          <a-input v-model:value="addForm.contact_person" placeholder="联系人姓名" />
        </a-form-item>

        <a-form-item label="联系电话">
          <a-input v-model:value="addForm.contact_phone" placeholder="联系电话" />
        </a-form-item>

        <a-form-item label="注册地址">
          <a-input
            v-model:value="addForm.address"
            placeholder="企业注册地址"
            :disabled="addForm.fetchFromQcc && qccDataFilled"
          />
        </a-form-item>

        <a-form-item label="备注">
          <a-textarea v-model:value="addForm.notes" placeholder="备注信息" :rows="3" />
        </a-form-item>

        <!-- 企查查数据预览 -->
        <template v-if="addForm.fetchFromQcc && qccPreview">
          <a-divider>企查查数据预览</a-divider>
          <div class="bg-gray-50 rounded-lg p-3 text-xs space-y-2">
            <div><span class="text-gray-500">法定代表人:</span> {{ qccPreview.法定代表人 }}</div>
            <div><span class="text-gray-500">注册资本:</span> {{ qccPreview.注册资本 }}</div>
            <div><span class="text-gray-500">成立日期:</span> {{ qccPreview.成立日期 }}</div>
            <div><span class="text-gray-500">登记状态:</span> {{ qccPreview.登记状态 }}</div>
            <div v-if="qccRiskSummary" :class="qccRiskSummary.includes('无记录') ? 'text-green-600' : 'text-red-600'">
              <span class="text-gray-500">风险扫描:</span> {{ qccRiskSummary }}
            </div>
          </div>
        </template>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { PlusOutlined, LoadingOutlined } from '@ant-design/icons-vue'
import { getSuppliersApi, createSupplierApi, getQccBasicApi, getQccRiskApi } from '#/api/suppliers'

const router = useRouter()

const loading = ref(false)
const suppliers = ref<any[]>([])
const searchText = ref('')

const filteredSuppliers = computed(() => {
  if (!searchText.value) return suppliers.value
  return suppliers.value.filter(s =>
    s.supplier_name?.includes(searchText.value) ||
    s.short_name?.includes(searchText.value)
  )
})

// 新增供应商
const addModalVisible = ref(false)
const addSaving = ref(false)
const qccLoading = ref(false)
const qccDataFilled = ref(false)
const qccPreview = ref<any>(null)
const qccRiskSummary = ref('')

const addForm = ref({
  fetchFromQcc: true,
  creditCode: '',
  supplier_name: '',
  short_name: '',
  credit_code: '',
  category: '',
  contact_person: '',
  contact_phone: '',
  address: '',
  notes: '',
})

function openAddModal() {
  addForm.value = {
    fetchFromQcc: true,
    creditCode: '',
    supplier_name: '',
    short_name: '',
    credit_code: '',
    category: '',
    contact_person: '',
    contact_phone: '',
    address: '',
    notes: '',
  }
  qccPreview.value = null
  qccRiskSummary.value = ''
  qccDataFilled.value = false
  addModalVisible.value = true
}

async function handleFetchQccInfo() {
  if (!addForm.value.creditCode || addForm.value.creditCode.length !== 18) {
    return
  }

  qccLoading.value = true
  try {
    // 并发查询工商信息和风险扫描
    const [basic, risk] = await Promise.all([
      getQccBasicApi(addForm.value.creditCode),
      getQccRiskApi(addForm.value.creditCode)
    ])

    if (basic) {
      // 自动填充表单
      addForm.value.supplier_name = basic.企业名称 || ''
      addForm.value.credit_code = basic.统一社会信用代码 || ''
      addForm.value.address = basic.注册地址 || ''

      // 预览数据
      qccPreview.value = basic
      qccDataFilled.value = true
    }

    if (risk) {
      qccRiskSummary.value = risk.摘要 || ''
    }

    message.success('企查查数据获取成功')
  } catch (e: any) {
    message.error('获取企查查数据失败: ' + (e?.message || '未知错误'))
  } finally {
    qccLoading.value = false
  }
}

async function handleAddSupplier() {
  if (!addForm.value.supplier_name) {
    message.error('请输入供应商名称')
    return
  }

  addSaving.value = true
  try {
    const supplierId = addForm.value.credit_code || `SUP${Date.now()}`

    await createSupplierApi({
      supplier_id: supplierId,
      supplier_name: addForm.value.supplier_name,
      short_name: addForm.value.short_name || addForm.value.supplier_name.substring(0, 4),
      category: addForm.value.category || '其他',
      contact_person: addForm.value.contact_person,
      contact_phone: addForm.value.contact_phone,
      notes: addForm.value.notes,
    })

    message.success('供应商创建成功')
    addModalVisible.value = false
    loadSuppliers()
  } catch (e: any) {
    message.error('创建失败: ' + (e?.message || '未知错误'))
  } finally {
    addSaving.value = false
  }
}

function handleSearch() {
  // 搜索逻辑已在 computed 中实现
}

function handleCellClick({ row }: any) {
  viewDetail(row)
}

function viewDetail(row: any) {
  router.push({
    path: '/suppliers/detail',
    query: { id: row.credit_code || row.supplier_id }
  })
}

function formatMoney(value: number) {
  if (!value) return '0.00'
  return value.toFixed(2)
}

function categoryColor(category: string): string {
  const colors: Record<string, string> = {
    '服务类': 'blue',
    '物资类': 'green',
    '施工类': 'orange',
    '科研类': 'purple',
    '其他': 'default'
  }
  return colors[category] || 'default'
}

async function loadSuppliers() {
  loading.value = true
  try {
    const data = await getSuppliersApi()
    suppliers.value = data.items || []
  } catch (e: any) {
    message.error('加载供应商列表失败: ' + (e?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

onMounted(loadSuppliers)
</script>

<style scoped>
</style>
