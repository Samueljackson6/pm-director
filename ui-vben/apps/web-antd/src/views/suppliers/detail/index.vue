<script lang="ts" setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { message } from 'ant-design-vue';

import { getSupplierDetailApi } from '#/api/suppliers';
import StateBlock from '#/components/state-block/index.vue';

import SupplierBusinessProfileRisk from './components/SupplierBusinessProfileRisk.vue';
import SupplierCollaborationFinance from './components/SupplierCollaborationFinance.vue';
import SupplierOverview from './components/SupplierOverview.vue';
import type {
  SupplierBasicInfo,
  SupplierDetailResponse,
  SupplierExternalInvestment,
  SupplierLocalQccBasicInfo,
  SupplierLocalRiskScan,
  SupplierProfile,
  SupplierRiskScan,
  SupplierSoftwareCopyright,
} from './components/supplier-qcc';

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref('');
const basicInfo = ref<SupplierBasicInfo | null>(null);
const profile = ref<SupplierProfile | null>(null);
const riskScan = ref<SupplierRiskScan | null>(null);
const softwareList = ref<readonly SupplierSoftwareCopyright[]>([]);
const investmentList = ref<readonly SupplierExternalInvestment[]>([]);
const contracts = ref<readonly Record<string, unknown>[]>([]);
const supplierInvoices = ref<readonly Record<string, unknown>[]>([]);
const payments = ref<readonly Record<string, unknown>[]>([]);
const contacts = ref<readonly Record<string, unknown>[]>([]);
const dataStates = ref<Record<string, string>>({});
const qccDataAvailable = ref(false);
const activeAnchor = ref('basic');

const anchors = [
  { id: 'basic', label: '基本信息' },
  { id: 'risk', label: '风险扫描' },
  { id: 'software', label: '知识产权' },
  { id: 'investment', label: '对外投资' },
] as const;

const companyAge = computed(() => {
  const establishedAt = basicInfo.value?.成立日期;
  if (!establishedAt) return '待核验';
  const timestamp = new Date(establishedAt).getTime();
  if (Number.isNaN(timestamp)) return '待核验';
  return `${Math.max(0, Math.floor((Date.now() - timestamp) / 31_557_600_000))}年`;
});

const riskEvidenceComplete = computed(() =>
  riskScan.value?.有记录因子数 !== undefined && riskScan.value?.无记录因子数 !== undefined,
);
const riskLevel = computed(() => {
  const recordedFactors = riskScan.value?.有记录因子数;
  if (!riskEvidenceComplete.value || recordedFactors === undefined) return '待核验';
  if (recordedFactors === 0) return '风险扫描未发现记录';
  if (recordedFactors <= 2) return '需关注';
  return '高风险';
});
const riskLevelColor = computed(() => ({
  待核验: 'default',
  高风险: 'red',
  需关注: 'orange',
  风险扫描未发现记录: 'green',
}[riskLevel.value] ?? 'default'));
const riskLevelTextClass = computed(() => ({
  待核验: 'text-gray-600',
  高风险: 'text-red-600',
  需关注: 'text-orange-600',
  风险扫描未发现记录: 'text-green-600',
}[riskLevel.value] ?? 'text-gray-600'));

const rating = computed(() => {
  if (!basicInfo.value || !riskEvidenceComplete.value || companyAge.value === '待核验') return null;
  const recordedFactors = riskScan.value?.有记录因子数;
  if (recordedFactors === undefined) return null;
  const basic = basicInfo.value.实缴资本 ? 4 : 3;
  const risk = Math.max(1, 5 - recordedFactors * 0.5);
  const tech = softwareList.value.length > 0 ? 3 : 2;
  const stability = Number.parseInt(companyAge.value, 10) >= 5 ? 4 : 3;
  return { basic, risk, tech, stability, overall: (basic + risk + tech + stability) / 4 };
});

function displayText(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim() ? value : undefined;
}

function getChineseValue(record: Record<string, unknown> | null | undefined, key: string): string | undefined {
  return displayText(record?.[key]);
}

function buildBasicInfo(supplier: Record<string, unknown>, qccData: SupplierDetailResponse['qcc_data']): SupplierBasicInfo {
  const qccBasic = (qccData?.basic_info ?? {}) as SupplierLocalQccBasicInfo & Record<string, unknown>;
  return {
    企业名称: getChineseValue(qccBasic, '企业名称') ?? qccBasic.company_name ?? displayText(supplier.supplier_name),
    统一社会信用代码: getChineseValue(qccBasic, '统一社会信用代码') ?? qccBasic.credit_code ?? displayText(supplier.credit_code),
    法定代表人: getChineseValue(qccBasic, '法定代表人') ?? qccBasic.legal_representative,
    企业类型: getChineseValue(qccBasic, '企业类型') ?? qccBasic.company_type ?? displayText(supplier.category),
    纳税人资质: getChineseValue(qccBasic, '纳税人资质') ?? qccBasic.taxpayer_qualification,
    营业期限: getChineseValue(qccBasic, '营业期限'),
    注册资本: getChineseValue(qccBasic, '注册资本') ?? qccBasic.registered_capital ?? qccBasic.registration_capital,
    实缴资本: getChineseValue(qccBasic, '实缴资本') ?? qccBasic.paid_capital ?? qccBasic.paid_in_capital,
    成立日期: getChineseValue(qccBasic, '成立日期') ?? qccBasic.establishment_date,
    参保人数: qccBasic.参保人数 as number | string | undefined ?? qccBasic.insured_count,
    人员规模: getChineseValue(qccBasic, '人员规模') ?? qccBasic.personnel_scale,
    登记状态: getChineseValue(qccBasic, '登记状态') ?? qccBasic.business_status ?? qccBasic.registration_status ?? displayText(supplier.status),
    注册地址: getChineseValue(qccBasic, '注册地址') ?? qccBasic.registered_address,
    经营范围: getChineseValue(qccBasic, '经营范围') ?? qccBasic.business_scope,
  };
}

function normalizeProfile(value: unknown): SupplierProfile | null {
  const profile = value as { profile?: string; qcc_industry?: string; 简介?: string; 企查查行业?: string; 行业?: string } | null | undefined;
  if (!profile) return null;
  return { 简介: profile.简介 ?? profile.profile, 企查查行业: profile.企查查行业 ?? profile.qcc_industry ?? profile.行业 };
}

function normalizeRiskScan(value: unknown): SupplierRiskScan | null {
  const risk = value as SupplierLocalRiskScan & SupplierRiskScan | null | undefined;
  if (!risk) return null;
  return {
    有记录因子数: risk.有记录因子数 ?? risk.risk_factors_count,
    无记录因子数: risk.无记录因子数 ?? risk.clean_factors_count,
    风险因子扫描: risk.风险因子扫描,
  };
}

function normalizeSoftware(value: SupplierDetailResponse['qcc_data']): readonly SupplierSoftwareCopyright[] {
  const source = value?.software_copyrights;
  const records = source?.软件著作权信息 ?? source?.items ?? [];
  return records.map((item) => ({
    软件全称: displayText(item.软件全称) ?? displayText(item.software_name),
    登记号: displayText(item.登记号) ?? displayText(item.registration_number),
    登记日期: displayText(item.登记日期) ?? displayText(item.registration_date),
  }));
}

function normalizeInvestments(value: SupplierDetailResponse['qcc_data']): readonly SupplierExternalInvestment[] {
  const source = value?.external_investments;
  const records = source?.对外投资信息 ?? source?.items ?? [];
  return records.map((item) => ({
    被投资企业名称: displayText(item.被投资企业名称) ?? displayText(item.investee_name) ?? '',
    成立日期: displayText(item.成立日期) ?? displayText(item.investee_establishment_date) ?? displayText(item.establishment_date),
    持股比例: displayText(item.持股比例) ?? displayText(item.shareholding_ratio),
    状态: displayText(item.状态) ?? displayText(item.investee_status) ?? displayText(item.status),
    '认缴出资额/持股数': displayText(item['认缴出资额/持股数']) ?? displayText(item.subscribed_capital),
  }));
}

function scrollToAnchor(id: string): void {
  const element = document.getElementById(id);
  if (element) window.scrollTo({ top: element.getBoundingClientRect().top + window.pageYOffset - 56, behavior: 'smooth' });
}

function goBack(): void {
  router.push({ name: 'SupplierList' });
}

async function loadData(): Promise<void> {
  loading.value = true;
  error.value = '';
  try {
    const supplierId = typeof route.query.id === 'string' ? route.query.id : '';
    if (!supplierId) throw new Error('缺少供应商标识');
    const data = await getSupplierDetailApi(supplierId) as SupplierDetailResponse;
    const qccData = data.qcc_data;
    qccDataAvailable.value = Boolean(qccData);
    basicInfo.value = data.supplier ? buildBasicInfo(data.supplier, qccData) : null;
    profile.value = normalizeProfile(qccData?.profile);
    riskScan.value = normalizeRiskScan(qccData?.risk_scan);
    softwareList.value = normalizeSoftware(qccData);
    investmentList.value = normalizeInvestments(qccData);
    contracts.value = data.contracts ?? [];
    supplierInvoices.value = data.supplier_invoices ?? data.invoices ?? [];
    payments.value = data.payments ?? [];
    contacts.value = data.contacts ?? [];
    dataStates.value = data.data_states ?? {};
  } catch (caughtError: unknown) {
    error.value = caughtError instanceof Error ? caughtError.message : '加载失败';
    message.error(`加载供应商数据失败：${error.value}`);
  } finally {
    loading.value = false;
  }
}

let anchorObserver: IntersectionObserver | undefined;
watch(basicInfo, () => nextTick(() => {
  anchorObserver?.disconnect();
  anchorObserver = new IntersectionObserver((entries) => entries.forEach((entry) => {
    if (entry.isIntersecting) activeAnchor.value = entry.target.id;
  }), { rootMargin: '-56px 0px -70% 0px' });
  anchors.forEach(({ id }) => document.getElementById(id) && anchorObserver?.observe(document.getElementById(id)!));
}), { flush: 'post' });

onMounted(loadData);
onBeforeUnmount(() => anchorObserver?.disconnect());
</script>

<template>
  <div class="pm-workbench-page min-h-screen space-y-5 p-4 sm:p-6">
    <div class="pm-page-header flex items-center justify-between gap-4">
      <div class="flex items-center gap-4"><a-button type="text" class="flex h-9 w-9 items-center justify-center rounded-lg border border-gray-200" @click="goBack">←</a-button><div><h2 class="text-xl font-semibold text-gray-800">供应商详情</h2><div class="mt-0.5 text-sm text-gray-500">{{ basicInfo?.企业名称 || '加载中…' }}</div></div></div>
      <div class="flex items-center gap-3"><a-tag v-if="basicInfo?.登记状态" class="rounded-full px-3 py-0.5 text-xs">{{ basicInfo.登记状态 }}</a-tag><a-tag :color="riskLevelColor" class="rounded-full px-3 py-0.5 text-xs">风险：{{ riskLevel }}</a-tag></div>
    </div>
    <StateBlock :loading="loading" :error="error" error-title="供应商数据加载失败" @retry="loadData">
      <template v-if="basicInfo">
        <SupplierOverview :basic-info="basicInfo" :profile="profile" :company-age="companyAge" :qcc-data-available="qccDataAvailable" :software-count="softwareList.length" :investment-count="investmentList.length" />
        <div class="sticky top-0 z-20 -mx-4 border-y border-slate-200 bg-white/95 px-4 shadow-sm backdrop-blur-sm sm:-mx-6 sm:px-6"><div class="flex gap-1 overflow-x-auto py-2"><button v-for="anchor in anchors" :key="anchor.id" :class="['whitespace-nowrap rounded-md px-3 py-1.5 text-sm transition-colors', activeAnchor === anchor.id ? 'bg-blue-50 font-medium text-blue-600' : 'text-gray-500 hover:bg-gray-100']" @click="scrollToAnchor(anchor.id)">{{ anchor.label }}</button></div></div>
        <SupplierBusinessProfileRisk :qcc-data-available="qccDataAvailable" :risk-scan="riskScan" :risk-level="riskLevel" :risk-level-text-class="riskLevelTextClass" :software-list="softwareList" :investment-list="investmentList" />
        <SupplierCollaborationFinance :contracts="contracts" :supplier-invoices="supplierInvoices" :payments="payments" :contacts="contacts" :data-states="dataStates" :rating="rating" />
      </template>
    </StateBlock>
  </div>
</template>
