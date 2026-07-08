<template>
  <div class="p-4">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold">供应商详情</h2>
      <a-button @click="goBack">返回列表</a-button>
    </div>
    <a-spin :spinning="loading">
      <template v-if="supplier">
        <!-- 基本信息 -->
        <a-card title="基本信息" size="small">
          <a-descriptions :column="2" size="small" bordered>
            <a-descriptions-item label="供应商名称" :span="2">{{ supplier.supplier_name }}</a-descriptions-item>
            <a-descriptions-item label="简称" :span="2">{{ supplier.short_name || '-' }}</a-descriptions-item>
            <a-descriptions-item label="统一社会信用代码" :span="2">{{ supplier.credit_code || '-' }}</a-descriptions-item>
            <a-descriptions-item label="联系人">{{ supplier.contact_person || '-' }}</a-descriptions-item>
            <a-descriptions-item label="联系电话">{{ supplier.contact_phone || '-' }}</a-descriptions-item>
            <a-descriptions-item label="类别">{{ supplier.category || '-' }}</a-descriptions-item>
            <a-descriptions-item label="状态">{{ supplier.status === 'active' ? '合作中' : '已暂停' }}</a-descriptions-item>
            <a-descriptions-item label="首次合作日期">{{ supplier.first_cooperation_date || '-' }}</a-descriptions-item>
            <a-descriptions-item label="评估" :span="2">{{ supplier.evaluation || '-' }}</a-descriptions-item>
          </a-descriptions>
        </a-card>

        <!-- 财务汇总 -->
        <a-card title="财务汇总" size="small" class="mt-4">
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 text-center">
            <div>
              <div class="text-muted-foreground text-sm">合同总额</div>
              <div class="text-lg font-bold">{{ (supplier.total_contract_amount || 0).toFixed(2) }} 万元</div>
            </div>
            <div>
              <div class="text-muted-foreground text-sm">已开票</div>
              <div class="text-lg font-bold text-blue">{{ (supplier.total_invoiced || 0).toFixed(2) }} 万元</div>
            </div>
            <div>
              <div class="text-muted-foreground text-sm">已付款</div>
              <div class="text-lg font-bold text-green">{{ (supplier.total_paid || 0).toFixed(2) }} 万元</div>
            </div>
            <div>
              <div class="text-muted-foreground text-sm">未付款</div>
              <div class="text-lg font-bold text-orange">{{ (supplier.total_unpaid || 0).toFixed(2) }} 万元</div>
            </div>
          </div>
        </a-card>

        <!-- 关联合同 -->
        <a-card title="关联合同" size="small" class="mt-4" v-if="contracts.length">
          <a-table :columns="contractCols" :data-source="contracts" row-key="id" size="small" :pagination="false" />
        </a-card>
      </template>
    </a-spin>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSupplierDetailApi } from '#/api/suppliers'

const route = useRoute()
const router = useRouter()
const supplier = ref<any>(null)
const contracts = ref<any[]>([])
const loading = ref(true)

const contractCols = [
  { title: '项目编号', dataIndex: 'project_id', width: 160 },
  { title: '项目名称', dataIndex: 'project_name', minWidth: 200 },
  { title: '合同金额', dataIndex: 'contract_amount', width: 120, align: 'right' },
  { title: '已开票', dataIndex: 'invoice_total', width: 100, align: 'right' },
  { title: '已付款', dataIndex: 'payment_total', width: 100, align: 'right' },
  { title: '未付款', dataIndex: 'unpaid', width: 100, align: 'right' },
  { title: '状态', dataIndex: 'status', width: 80 },
]

onMounted(async () => {
  try {
    const data: any = await getSupplierDetailApi(route.query.id as string)
    supplier.value = data.supplier
    contracts.value = data.contracts || []
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.push({ name: 'SupplierList' })
}
</script>
