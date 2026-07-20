<script lang="ts" setup>
import type { SupplierBasicInfo, SupplierProfile } from './supplier-qcc';

const props = defineProps<{
  readonly basicInfo: SupplierBasicInfo;
  readonly companyAge: string;
  readonly investmentCount: number;
  readonly profile: SupplierProfile | null;
  readonly qccDataAvailable: boolean;
  readonly softwareCount: number;
}>();

function valueOrPending(value: string | number | undefined): string | number {
  return value === undefined || value === null || value === '' ? '待核验' : value;
}
</script>

<template>
  <section class="space-y-4">
    <div class="grid grid-cols-2 gap-3 md:grid-cols-5">
      <div class="rounded-lg border border-gray-200 bg-white p-4 text-center"><div class="mb-1 text-xs text-gray-400">注册资本</div><div class="text-2xl font-bold text-gray-900">{{ valueOrPending(props.basicInfo.注册资本) }}</div><div class="mt-0.5 text-xs text-gray-400">实缴：{{ valueOrPending(props.basicInfo.实缴资本) }}</div></div>
      <div class="rounded-lg border border-gray-200 bg-white p-4 text-center"><div class="mb-1 text-xs text-gray-400">成立年限</div><div class="text-2xl font-bold text-gray-900">{{ props.companyAge }}</div><div class="mt-0.5 text-xs text-gray-400">{{ valueOrPending(props.basicInfo.成立日期) }}</div></div>
      <div class="rounded-lg border border-gray-200 bg-white p-4 text-center"><div class="mb-1 text-xs text-gray-400">参保人数</div><div class="text-2xl font-bold text-blue-600">{{ valueOrPending(props.basicInfo.参保人数) }}</div><div class="mt-0.5 text-xs text-gray-400">人员规模：{{ valueOrPending(props.basicInfo.人员规模) }}</div></div>
      <div class="rounded-lg border border-gray-200 bg-white p-4 text-center"><div class="mb-1 text-xs text-gray-400">软件著作权</div><div class="text-2xl font-bold text-green-600">{{ props.qccDataAvailable ? props.softwareCount : '待核验' }}</div><div class="mt-0.5 text-xs text-gray-400">{{ props.qccDataAvailable ? '本地归档结果' : '数据未归档' }}</div></div>
      <div class="rounded-lg border border-gray-200 bg-white p-4 text-center"><div class="mb-1 text-xs text-gray-400">对外投资</div><div class="text-2xl font-bold text-purple-600">{{ props.qccDataAvailable ? props.investmentCount : '待核验' }}</div><div class="mt-0.5 text-xs text-gray-400">{{ props.qccDataAvailable ? '本地归档结果' : '数据未归档' }}</div></div>
    </div>
    <a-card id="basic" title="企业基本信息" class="rounded-lg" size="small" :body-style="{ padding: '16px' }">
      <div class="space-y-4"><div class="grid grid-cols-2 gap-4 md:grid-cols-3"><div><div class="mb-1 text-xs text-gray-400">企业名称</div><div class="text-sm font-medium text-gray-900">{{ valueOrPending(props.basicInfo.企业名称) }}</div></div><div><div class="mb-1 text-xs text-gray-400">统一社会信用代码</div><div class="text-xs font-medium text-gray-900">{{ valueOrPending(props.basicInfo.统一社会信用代码) }}</div></div><div><div class="mb-1 text-xs text-gray-400">法定代表人</div><div class="font-medium text-gray-900">{{ valueOrPending(props.basicInfo.法定代表人) }}</div></div><div><div class="mb-1 text-xs text-gray-400">企业类型</div><div class="text-xs font-medium text-gray-900">{{ valueOrPending(props.basicInfo.企业类型) }}</div></div><div><div class="mb-1 text-xs text-gray-400">纳税人资质</div><div class="font-medium text-gray-900">{{ valueOrPending(props.basicInfo.纳税人资质) }}</div></div><div><div class="mb-1 text-xs text-gray-400">营业期限</div><div class="text-xs font-medium text-gray-900">{{ valueOrPending(props.basicInfo.营业期限) }}</div></div></div><a-divider class="my-0" /><div v-if="props.profile"><div class="mb-2 text-xs font-semibold text-gray-500">企业简介</div><div class="rounded-lg bg-gray-50 p-3 text-sm leading-relaxed text-gray-700">{{ props.profile.简介 }}</div></div><div><div class="mb-2 text-xs font-semibold text-gray-500">注册地址</div><div class="text-sm text-gray-700">{{ valueOrPending(props.basicInfo.注册地址) }}</div></div><div><div class="mb-2 text-xs font-semibold text-gray-500">经营范围</div><div class="max-h-32 overflow-y-auto rounded-lg bg-gray-50 p-3 text-xs leading-relaxed text-gray-600">{{ valueOrPending(props.basicInfo.经营范围) }}</div></div></div>
    </a-card>
  </section>
</template>
