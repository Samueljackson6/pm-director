<template>
<a-card title='Invoices' :bordered='false'>
  <a-table :columns='cols' :data-source='items' size='small' row-key='invoice_id' :pagination='{pageSize:50}'>
    <template #bodyCell='{ column, record }'>
      <template v-if='column.key===&apos;type&apos;'>
        <a-tag :color='record.invoice_type===&apos;客户回款&apos;?&quot;green&quot;:&quot;blue&quot;'>{{record.invoice_type===&apos;客户回款&apos;?&apos;Recv&apos;:&apos;Bill&apos;}}</a-tag>
      </template>
    </template>
  </a-table>
</a-card>
</template>
<script lang='ts' setup>
import { ref,onMounted } from 'vue';import{getInvoicesApi}from'#/api/invoices'
const items=ref<any[]>([])
const cols=[{title:'Date',dataIndex:'invoice_date',width:110},{title:'Type',key:'type',width:80},{title:'Project',dataIndex:'project_id',ellipsis:true},{title:'Amount',dataIndex:'amount',width:100}]
onMounted(async()=>{const r:any=await getInvoicesApi();items.value=r?.items||[]})
</script>
