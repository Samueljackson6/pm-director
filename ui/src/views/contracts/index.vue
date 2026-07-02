<template>
  <a-card title='Contracts'>
    <a-table :columns='cols' :data-source='items' :loading='loading' row-key='contract_id' size='small'
      :pagination='{ current: page, pageSize: 20, total: total }' @change='onTable'></a-table>
  </a-card>
</template>
<script lang='ts' setup>
import { ref,onMounted } from 'vue'
import { getContractsApi } from '#/api/contracts'
const items=ref<any[]>([]);const total=ref(0);const page=ref(1);const loading=ref(false)
const cols=[{title:'ID',dataIndex:'contract_id',width:180},{title:'Project',dataIndex:'project_name',ellipsis:true},{title:'Type',dataIndex:'project_type',width:80},{title:'Amount',dataIndex:'contract_amount',width:100}]
onMounted(()=>load())
function onTable(pag:any){page.value=pag.current;load()}
async function load(){loading.value=true;try{const r:any=await getContractsApi({page:page.value,size:20});const d=r?.data?.data||r?.data||r;items.value=d?.items||[];total.value=d?.total||0}finally{loading.value=false}}
</script>
