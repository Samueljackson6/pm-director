<template>
  <div class="pm-workbench-page min-h-screen p-4 sm:p-6">
    <header class="pm-page-header">
      <p class="pm-section-kicker">履约执行</p>
      <h1>项目台账</h1>
      <p class="pm-section-note">优先关注进度、风险与负责人缺失的履约任务。</p>
    </header>
    <!-- 搜索栏 -->
    <a-card class="pm-table-surface mb-4" :bordered="false">
      <a-row :gutter="16" align="middle">
        <a-col :span="6">
          <a-input v-model:value="searchText" placeholder="搜索项目名称/编号" allow-clear />
        </a-col>
        <a-col :span="4">
          <a-select v-model:value="statusFilter" placeholder="项目状态" allow-clear style="width: 100%">
            <a-select-option value="active">进行中</a-select-option>
            <a-select-option value="paused">已暂停</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
            <a-select-option value="cancelled">已取消</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="4">
          <a-select v-model:value="typeFilter" placeholder="项目类型" allow-clear style="width: 100%">
            <a-select-option value="engineering">工程类</a-select-option>
            <a-select-option value="consulting">咨询类</a-select-option>
            <a-select-option value="research">研发类</a-select-option>
            <a-select-option value="other">其他</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-space>
            <a-button type="primary" @click="handleSearch">查询</a-button>
            <a-button @click="handleReset">重置</a-button>
          </a-space>
        </a-col>
      </a-row>
    </a-card>

    <section class="pm-table-surface"><Grid>
      <template #statusSlot="{ row }">
        <a-tag :color="statusColor(row.project_status)">
          {{ statusLabel(row.project_status) }}
        </a-tag>
      </template>
      <template #riskSlot="{ row }">
        <a-tag :color="riskColor(row.risk_level)">
          {{ riskLabel(row.risk_level) }}
        </a-tag>
      </template>
      <template #progressSlot="{ row }">
        <a-progress :percent="row.overall_progress ?? 0" size="small" />
      </template>
    </Grid></section>
  </div>
</template>

<script lang="ts" setup>
import type { VxeGridProps } from '#/adapter/vxe-table'
import { useVbenVxeGrid } from '#/adapter/vxe-table'
import { getProjectsApi, type ProjectItem } from '#/api/projects'
import { buildDetailLocation } from '#/utils/business-navigation'
import { useRoute, useRouter } from 'vue-router'
import { ref } from 'vue'

const route = useRoute()
const router = useRouter()

// 搜索条件
const searchText = ref('')
const statusFilter = ref<string | undefined>()
const typeFilter = ref<string | undefined>()
const currentPage = ref(1)
const currentPageSize = ref(20)

function projectDetailLocation(projectId: string) {
  return buildDetailLocation({
    from: {
      name: route.name,
      query: {
        ...route.query,
        page: String(currentPage.value),
        pageSize: String(currentPageSize.value),
        search: searchText.value,
        status: statusFilter.value,
        type: typeFilter.value,
      },
    },
    id: projectId,
    name: 'ProjectDetail',
  })
}

// 状态标签映射
const statusColorMap: Record<string, string> = {
  active: 'green',
  paused: 'orange',
  completed: 'blue',
  cancelled: 'gray',
}

const statusLabelMap: Record<string, string> = {
  active: '进行中',
  paused: '已暂停',
  completed: '已完成',
  cancelled: '已取消',
}

function statusColor(s: string): string {
  return statusColorMap[s] || 'default'
}

function statusLabel(s: string): string {
  return statusLabelMap[s] || s || '-'
}

// 风险等级映射
const riskColorMap: Record<string, string> = {
  low: 'green',
  medium: 'yellow',
  high: 'orange',
  critical: 'red',
}

const riskLabelMap: Record<string, string> = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  critical: '严重',
}

function riskColor(r: string): string {
  return riskColorMap[r] || 'default'
}

function riskLabel(r: string): string {
  return riskLabelMap[r] || r || '-'
}

const gridOptions: VxeGridProps<ProjectItem> = {
  columns: [
    { field: 'project_id', title: '项目编号', width: 200, fixed: 'left' },
    {
      field: 'project_name',
      title: '项目名称',
      minWidth: 200,
      showOverflow: true,
      cellRender: {
        name: 'CellRouterLink',
        props: {
          field: 'project_name',
          name: 'ProjectDetail',
          variableQuery: (row: ProjectItem) =>
            projectDetailLocation(row.project_id).query,
        },
      },
    },
    { field: 'customer_name', title: '客户名称', width: 150, showOverflow: true },
    { field: 'project_type', title: '项目类型', width: 100 },
    {
      field: 'total_contract_amount',
      title: '合同总额(万元)',
      width: 140,
      align: 'right',
      formatter: ({ cellValue }) => (cellValue ?? 0).toFixed(2),
    },
    {
      field: 'project_status',
      title: '项目状态',
      width: 100,
      slots: { default: 'statusSlot' },
    },
    { field: 'project_manager', title: '项目经理', width: 110 },
    {
      field: 'overall_progress',
      title: '总体进度',
      width: 160,
      slots: { default: 'progressSlot' },
    },
    {
      field: 'risk_level',
      title: '风险等级',
      width: 100,
      slots: { default: 'riskSlot' },
    },
  ],
  proxyConfig: {
    response: { result: 'items', total: 'total' },
    ajax: {
      query: async ({ page }) => {
        currentPage.value = page.currentPage
        currentPageSize.value = page.pageSize
        const data = await getProjectsApi({
          page: page.currentPage,
          size: page.pageSize,
          search: searchText.value || undefined,
          status: statusFilter.value || undefined,
          type: typeFilter.value || undefined,
        })
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
  rowConfig: { isHover: true, height: 44 },
}

const [Grid, gridApi] = useVbenVxeGrid({
  gridOptions,
  gridEvents: {
    // 双击行跳转详情
    cellDblclick({ row }: { row: ProjectItem }) {
      router.push(projectDetailLocation(row.project_id))
    },
  },
})

function handleSearch() {
  gridApi.query()
}

function handleReset() {
  searchText.value = ''
  statusFilter.value = undefined
  typeFilter.value = undefined
  gridApi.query()
}
</script>
