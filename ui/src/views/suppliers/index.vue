<template>
<a-card title='Suppliers' :bordered='false'>
  <a-row :gutter='[16,16]'>
    <a-col v-for='s in items' :key='s.supplier_id' :xs='24' :sm='12' :md='8' :lg='6'>
      <a-card :hoverable='true' size='small'>
        <template #title>{{(s.supplier_name||'').slice(0,16)}}</template>
        <a-statistic title='Contract' :value='(s.total_contract_amount||0).toFixed(2)' suffix='k' />
      </a-card>
    </a-col>
  </a-row>
</a-card>
</template>
<script lang='ts' setup>
import { ref,onMounted } from 'vue';import{getSuppliersApi}from'#/api/suppliers'
const items=ref<any[]>([])
onMounted(async()=>{const r:any=await getSuppliersApi();items.value=r?.items||[]})
</script>
