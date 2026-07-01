<template>
  <div class="contract-list">
    <div class="list-header">
      <h2>合同台账</h2>
      <div class="list-controls">
        <input v-model="search" placeholder="搜索合同编号/名称/甲方..." class="search-input" @input="onSearch" />
        <select v-model="sort" class="sort-select" @change="loadData">
          <option value="amount_desc">金额 ↓</option>
          <option value="amount_asc">金额 ↑</option>
          <option value="name">名称 A-Z</option>
        </select>
      </div>
    </div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>项目编号</th><th>项目名称</th><th>类型</th><th>金额(万)</th><th>甲方</th><th>已开票</th><th>已回款</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in contracts" :key="c.contract_id" @click="$router.push('/contracts/'+c.contract_id)" class="clickable">
            <td class="mono">{{ c.contract_id }}</td>
            <td class="name-cell">{{ c.project_name }}</td>
            <td><span :class="'type-tag ' + (c.project_type||'')">{{ c.project_type }}</span></td>
            <td class="mono">¥{{ c.contract_amount?.toFixed(2) }}</td>
            <td class="ellipsis">{{ c.party_a?.replace(/[（(].*[)）]/g,'') }}</td>
            <td class="mono">{{ c.invoice_total?.toFixed(2) }}</td>
            <td class="mono">{{ c.payment_total?.toFixed(2) }}</td>
          </tr>
          <tr v-if="!contracts.length"><td colspan="7" class="empty">无数据</td></tr>
        </tbody>
      </table>
    </div>
    <div class="pagination">
      <span>共 {{ total }} 条</span>
      <button :disabled="page<=1" @click="page--; loadData()">上一页</button>
      <span class="page-info">{{ page }} / {{ maxPage }}</span>
      <button :disabled="page>=maxPage" @click="page++; loadData()">下一页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getContracts } from '../api'

const contracts = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const search = ref('')
const sort = ref('amount_desc')
const pageSize = 20
const maxPage = ref(1)

let searchTimer: any

onMounted(() => loadData())

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; loadData() }, 300)
}

async function loadData() {
  const res = await getContracts(page.value, pageSize, search.value, sort.value)
  contracts.value = res.items
  total.value = res.total
  maxPage.value = Math.ceil(res.total / pageSize)
}
</script>

<style scoped>
.contract-list { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.list-header h2 { font-size: 18px; font-weight: 600; }
.list-controls { display: flex; gap: 12px; }
.search-input { padding: 8px 16px; border: 1px solid #d1d5db; border-radius: 8px; width: 320px; font-size: 13px; outline: none; }
.search-input:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
.sort-select { padding: 8px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 13px; outline: none; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 12px 8px; border-bottom: 2px solid #e5e7eb; color: #666; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 12px 8px; border-bottom: 1px solid #f3f4f6; }
.data-table tr:hover td { background: #f8fafc; }
.clickable { cursor: pointer; }
.mono { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; }
.name-cell { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ellipsis { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.type-tag { padding: 2px 10px; border-radius: 12px; font-size: 12px; }
.type-tag.科研类 { background: #dbeafe; color: #1d4ed8; }
.type-tag.服务类 { background: #d1fae5; color: #047857; }
.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 20px; font-size: 13px; color: #666; }
.pagination button { padding: 6px 16px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
.pagination button:hover:not(:disabled) { background: #f3f4f6; }
.empty { text-align: center; color: #999; padding: 40px !important; }
</style>
