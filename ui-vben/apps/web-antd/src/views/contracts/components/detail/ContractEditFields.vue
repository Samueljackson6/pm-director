<template>
  <a-form :model="form" layout="vertical">
    <h3 class="section-title">基本信息</h3>
    <div class="grid grid-cols-2 gap-4">
      <a-form-item label="合同编号"><a-input v-model:value="form.contract_id" disabled /></a-form-item>
      <a-form-item label="合同金额（万元）"><a-input-number v-model:value="form.contract_amount" :precision="2" class="w-full" /></a-form-item>
      <a-form-item label="项目名称"><a-input v-model:value="form.project_name" /></a-form-item>
      <a-form-item label="项目类型"><a-select v-model:value="form.project_type"><a-select-option value="科研类">科研类</a-select-option><a-select-option value="服务类">服务类</a-select-option><a-select-option value="物资类">物资类</a-select-option><a-select-option value="施工类">施工类</a-select-option></a-select></a-form-item>
    </div>

    <h3 class="section-title">签约信息</h3>
    <div class="grid grid-cols-2 gap-4">
      <a-form-item label="甲方"><a-input v-model:value="form.party_a" /></a-form-item>
      <a-form-item label="乙方"><a-input v-model:value="form.party_b" /></a-form-item>
      <a-form-item label="签订日期"><a-date-picker v-model:value="form.sign_date" value-format="YYYY-MM-DD" class="w-full" /></a-form-item>
      <a-form-item label="到期日期"><a-date-picker v-model:value="form.expiry_date" value-format="YYYY-MM-DD" class="w-full" /></a-form-item>
      <a-form-item label="税率（%）"><a-input-number v-model:value="form.tax_rate" :min="0" :max="100" class="w-full" /></a-form-item>
      <a-form-item label="合同状态"><a-select v-model:value="form.contract_status"><a-select-option value="signed">已签订</a-select-option><a-select-option value="active">执行中</a-select-option><a-select-option value="completed">已完成</a-select-option><a-select-option value="expired">已到期</a-select-option><a-select-option value="terminated">已终止</a-select-option></a-select></a-form-item>
      <a-form-item label="甲方联系人"><a-input v-model:value="form.party_a_contact" /></a-form-item>
      <a-form-item label="甲方电话"><a-input v-model:value="form.party_a_phone" /></a-form-item>
      <a-form-item label="乙方联系人"><a-input v-model:value="form.party_b_contact" /></a-form-item>
      <a-form-item label="乙方电话"><a-input v-model:value="form.party_b_phone" /></a-form-item>
      <a-form-item label="签订地点"><a-input v-model:value="form.sign_location" /></a-form-item>
      <a-form-item label="服务期限"><a-input v-model:value="form.service_period" /></a-form-item>
    </div>

    <h3 class="section-title">服务与验收</h3>
    <a-form-item label="服务内容"><a-textarea v-model:value="form.service_content" :rows="3" /></a-form-item>
    <div class="grid grid-cols-2 gap-4">
      <a-form-item label="服务方式"><a-input v-model:value="form.service_method" /></a-form-item>
      <a-form-item label="服务地点"><a-input v-model:value="form.service_location" /></a-form-item>
      <a-form-item label="服务进度"><a-input v-model:value="form.service_schedule" /></a-form-item>
      <a-form-item label="服务质量"><a-input v-model:value="form.service_quality" /></a-form-item>
      <a-form-item label="验收方式"><a-input v-model:value="form.acceptance_method" /></a-form-item>
      <a-form-item label="验收地点"><a-input v-model:value="form.acceptance_location" /></a-form-item>
    </div>
    <a-form-item label="验收标准"><a-textarea v-model:value="form.acceptance_criteria" :rows="3" /></a-form-item>

    <h3 class="section-title">关联信息</h3>
    <div class="grid grid-cols-2 gap-4">
      <a-form-item label="正式名称"><a-input v-model:value="form.official_name" /></a-form-item>
      <a-form-item label="财务编号"><a-input v-model:value="form.financial_id" /></a-form-item>
      <a-form-item label="项目负责人"><a-input v-model:value="form.project_leader" /></a-form-item>
      <a-form-item label="SGSC编号"><a-input v-model:value="form.sgsc_id" /></a-form-item>
    </div>

    <template v-if="form.project_type === '科研类'">
      <h3 class="section-title">研究阶段</h3>
      <div v-for="(stage, index) in form.editStages" :key="stage.stage_id || index" class="mb-2 grid grid-cols-[1fr_1fr_auto] gap-2">
        <a-input v-model:value="stage.stage_name" placeholder="阶段名称" />
        <a-select v-model:value="stage.status"><a-select-option value="completed">已完成</a-select-option><a-select-option value="in_progress">进行中</a-select-option><a-select-option value="pending">待开始</a-select-option></a-select>
        <a-button danger @click="removeStage(Number(index))">删除</a-button>
      </div>
      <a-button type="dashed" block @click="addStage">添加阶段</a-button>

      <h3 class="section-title">交付物</h3>
      <div v-for="(deliverable, index) in form.editDeliverables" :key="deliverable.deliverable_id || index" class="mb-2 grid grid-cols-[1fr_1fr_auto] gap-2">
        <a-input v-model:value="deliverable.deliverable_name" placeholder="交付物名称" />
        <a-select v-model:value="deliverable.status"><a-select-option value="completed">已完成</a-select-option><a-select-option value="pending">待交付</a-select-option></a-select>
        <a-button danger @click="removeDeliverable(Number(index))">删除</a-button>
      </div>
      <a-button type="dashed" block @click="addDeliverable">添加交付物</a-button>
    </template>
  </a-form>
</template>

<script lang="ts" setup>
const props = defineProps(['form'])
function addStage() { props.form.editStages.push({ stage_name: '', status: 'pending', stage_number: props.form.editStages.length + 1 }) }
function removeStage(index: number) { props.form.editStages.splice(index, 1) }
function addDeliverable() { props.form.editDeliverables.push({ deliverable_name: '', deliverable_type: '报告', status: 'pending' }) }
function removeDeliverable(index: number) { props.form.editDeliverables.splice(index, 1) }
</script>

<style scoped>
.section-title { margin: 16px 0 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; font-size: 14px; font-weight: 600; color: #6b7280; }
</style>
