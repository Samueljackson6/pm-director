<template>
  <div class="p-4">
    <a-form :model="filters" layout="inline" class="mb-2 flex flex-wrap gap-2">
      <a-form-item label="搜索">
        <a-input v-model:value="filters.search" placeholder="合同编号/项目名称" allow-clear style="width:200px" />
      </a-form-item>
      <a-form-item label="项目类型">
        <a-select v-model:value="filters.project_type" placeholder="全部" allow-clear style="width:120px">
          <a-select-option value="科研类">科研类</a-select-option>
          <a-select-option value="服务类">服务类</a-select-option>
          <a-select-option value="物资类">物资类</a-select-option>
          <a-select-option value="施工类">施工类</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="合同状态">
        <a-select v-model:value="filters.contract_status" placeholder="全部" allow-clear style="width:120px">
          <a-select-option value="signed">已签订</a-select-option>
          <a-select-option value="active">进行中</a-select-option>
          <a-select-option value="completed">已完成</a-select-option>
          <a-select-option value="terminated">已终止</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item label="金额范围">
        <a-input-number v-model:value="filters.min_amount" placeholder="最小值" :min="0" style="width:100px" />
        <span class="mx-1">-</span>
        <a-input-number v-model:value="filters.max_amount" placeholder="最大值" :min="0" style="width:100px" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" @click="handleSearch">查询</a-button>
        <a-button class="ml-2" @click="handleReset">重置</a-button>
      </a-form-item>
      <a-form-item>
        <a-button @click="handleExport">导出</a-button>
      </a-form-item>
    </a-form>
    <Grid />
  </div>
</template>

<script lang="ts" setup>
// ╔══════════════════════════════════════════════════════════╗
// ║  合同列表 - Vben Admin 5 + VxeTable 网格组件          ║
// ║  单元格点击通过CellRouterLink渲染器处理（adapter注册） ║
// ╚══════════════════════════════════════════════════════════╝
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import { getContractsApi, type ContractItem } from '#/api/contracts'
import { useRouter } from 'vue-router'
import { reactive } from 'vue'
import { message } from 'ant-design-vue'
import { formatWanYuan } from '@/utils/formatAmount'

const router = useRouter()

const filters = reactive({
  search: '',
  project_type: '',
  contract_status: '',
  min_amount: undefined as number | undefined,
  max_amount: undefined as number | undefined,
})

const gridOptions: VxeGridProps<ContractItem> = {
  columns: [
    { field: 'contract_id', title: '合同编号', width: 200, fixed: 'left' },
    {
      field: 'official_name',
      title: '合同名称',
      minWidth: 250,
      showOverflow: true,
      formatter: ({ cellValue, row }) => cellValue || row.project_name || '-',
      cellRender: {
        name: 'CellRouterLink',
        props: {
          name: 'ContractDetail',
          idField: 'contract_id',
          field: 'official_name',
        },
      },
    },
    { field: 'project_type', title: '类型', width: 90 },
    {
      field: 'contract_amount',
      title: '金额(万元)',
      width: 130,
      align: 'right',
      formatter: ({ cellValue }) => formatWanYuan(cellValue),
    },
    {
      field: 'invoice_total',
      title: '已开票(万元)',
      width: 130,
      align: 'right',
      formatter: ({ cellValue }) => formatWanYuan(cellValue),
    },
    {
      field: 'payment_total',
      title: '已回款(万元)',
      width: 130,
      align: 'right',
      formatter: ({ cellValue }) => formatWanYuan(cellValue),
    },
    {
      field: 'sign_date',
      title: '签订日期',
      width: 110,
    },
    {
      field: 'party_a',
      title: '甲方',
      minWidth: 200,
      showOverflow: true,
      formatter: ({ cellValue }) => (cellValue ?? '').replace(/[（(].*[)）]/g, '') || '-',
    },
  ],
  proxyConfig: {
    response: { result: 'items', total: 'total' },
    ajax: {
      query: async ({ page }) => {
        const f = filters
        const params: Record<string, any> = {
          page: page.currentPage,
          size: page.pageSize,
        }
        if (f.search) params.search = f.search
        if (f.project_type) params.project_type = f.project_type
        if (f.contract_status) params.contract_status = f.contract_status
        if (f.min_amount != null) params.min_amount = f.min_amount
        if (f.max_amount != null) params.max_amount = f.max_amount
        const data = await getContractsApi(params)
        return { items: data.items ?? [], total: data.total ?? 0 }
      },
    },
  },
  toolbarConfig: {
    refresh: true,
    zoom: true,
    custom: true,
  },
  pagerConfig: {
    pageSize: 20,
    pageSizes: [10, 20, 50, 100],
  },
  sortConfig: { multiple: true },
  rowConfig: { keyField: 'contract_id', isHover: true, height: 44 },
}

const [Grid, gridApi] = useVbenVxeGrid({
  gridOptions,
  gridEvents: {
    cellClick({ row }: any) {
      console.log('cellClick fired', row?.contract_id)
      if (row?.contract_id) {
        router.push({ name: 'ContractDetail', query: { id: row.contract_id } })
      }
    },
  },
})

function handleSearch() {
  gridApi.commitQuery()
}

function handleReset() {
  filters.search = ''
  filters.project_type = ''
  filters.contract_status = ''
  filters.min_amount = undefined
  filters.max_amount = undefined
  gridApi.commitQuery()
}

function handleExport() {
  message.info('功能开发中')
}
</script>
