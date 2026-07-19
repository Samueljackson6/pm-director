<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
      <div class="rounded-lg border border-gray-200 bg-white p-4 text-center">
        <div class="mb-1 text-xs text-gray-400">发票金额（含税）</div>
        <div class="text-2xl font-bold text-gray-900">
          {{ fmtMoney(invoice.amount) }}
        </div>
        <div class="mt-0.5 text-xs text-gray-400">元</div>
      </div>
      <div class="rounded-lg border border-gray-200 bg-white p-4 text-center">
        <div class="mb-1 text-xs text-gray-400">税率</div>
        <div class="text-2xl font-bold text-blue-600">
          {{
            invoice.tax_rate != null
              ? invoice.tax_rate.toFixed(0) + '%'
              : '待核验'
          }}
        </div>
        <div class="mt-0.5 text-xs text-gray-400">百分比</div>
      </div>
      <div class="rounded-lg border border-gray-200 bg-white p-4 text-center">
        <div class="mb-1 text-xs text-gray-400">税额</div>
        <div class="text-2xl font-bold text-orange-600">
          {{ fmtMoney(calculatedTaxAmount) }}
        </div>
        <div class="mt-0.5 text-xs text-gray-400">元</div>
      </div>
      <div class="rounded-lg border border-gray-200 bg-white p-4 text-center">
        <div class="mb-1 text-xs text-gray-400">价税合计</div>
        <div class="text-2xl font-bold text-green-600">
          {{ fmtMoney(total_with_tax) }}
        </div>
        <div class="mt-0.5 text-xs text-gray-400">元</div>
      </div>
    </div>
    <a-alert
      v-if="isCustomerInvoiceDomainConflict(invoice)"
      class="border-amber-300 bg-amber-50"
      message="领域冲突：该记录不属于客户销项发票"
      type="warning"
      show-icon
    >
      <template #description>
        当前原始记录仍可查看，但不能按客户发票解读。发票类型：{{
          invoice.invoice_type || '待核验'
        }}；资金方向：{{ invoice.direction || '待核验' }}。
      </template>
    </a-alert>
    <section
      id="project"
      class="scroll-mt-16 rounded-lg border border-gray-200 bg-white"
    >
      <header class="section-title">
        <span class="bg-blue-500"></span>项目信息
      </header>
      <div class="section-grid">
        <div>
          <label>项目编号</label
          ><router-link
            :to="{ name: 'ContractDetail', query: { id: invoice.project_id } }"
            class="text-sm font-medium text-blue-600 hover:underline"
            >{{ invoice.project_id }}</router-link
          >
        </div>
        <div>
          <label>项目名称</label>
          <p>{{ invoice.project_name || '-' }}</p>
        </div>
        <div>
          <label>客户名称</label>
          <p>{{ invoice.customer_name || '-' }}</p>
        </div>
        <div>
          <label>方向</label
          ><a-tag
            :color="invoice.direction === 'outbound' ? 'blue' : 'orange'"
            >{{ invoice.direction || '待核验' }}</a-tag
          >
        </div>
      </div>
    </section>
    <section
      id="invoice"
      class="scroll-mt-16 rounded-lg border border-gray-200 bg-white"
    >
      <header class="section-title">
        <span class="bg-teal-500"></span>发票信息
      </header>
      <div class="section-grid">
        <div>
          <label>发票编号</label>
          <p class="font-mono">{{ invoice.invoice_no || '-' }}</p>
        </div>
        <div>
          <label>发票类型</label
          ><a-tag :color="invoiceTypeColor(invoice.invoice_type)">{{
            invoice.invoice_type || '-'
          }}</a-tag>
        </div>
        <div>
          <label>开票日期</label>
          <p>{{ invoice.invoice_date || '-' }}</p>
        </div>
        <div>
          <label>状态</label
          ><a-tag :color="statusColor(invoice.status)">{{
            invoice.status || '-'
          }}</a-tag>
        </div>
        <div>
          <label>匹配状态</label
          ><a-tag :color="paymentStatusColor(invoice.payment_status)">{{
            invoice.payment_status || '待核验'
          }}</a-tag>
        </div>
        <div>
          <label>回款日期</label>
          <p>{{ invoice.received_date || '-' }}</p>
        </div>
      </div>
    </section>
    <section
      id="amount"
      class="scroll-mt-16 rounded-lg border border-gray-200 bg-white"
    >
      <header class="section-title">
        <span class="bg-amber-500"></span>金额信息
      </header>
      <div class="section-grid">
        <div>
          <label>发票金额（含税，元）</label>
          <p class="font-semibold">{{ fmtMoney(invoice.amount) }}</p>
        </div>
        <div>
          <label>税率</label>
          <p>
            {{
              invoice.tax_rate != null
                ? invoice.tax_rate.toFixed(0) + '%'
                : '待核验'
            }}
          </p>
        </div>
        <div>
          <label>税额（元）</label>
          <p class="font-semibold text-orange-600">
            {{ fmtMoney(calculatedTaxAmount) }}
          </p>
        </div>
        <div>
          <label>不含税金额（元）</label>
          <p>{{ fmtMoney(calculateNetInvoiceAmount(invoice)) }}</p>
        </div>
      </div>
    </section>
    <section
      id="system"
      class="scroll-mt-16 rounded-lg border border-gray-200 bg-white"
    >
      <header class="section-title">
        <span class="bg-slate-400"></span>系统信息
      </header>
      <div class="section-grid">
        <div>
          <label>来源</label>
          <p>{{ invoice.source || '待核验' }}</p>
        </div>
        <div>
          <label>创建时间</label>
          <p>{{ invoice.created_at || '待核验' }}</p>
        </div>
        <div>
          <label>更新/导入时间</label>
          <p>{{ invoice.updated_at || invoice.import_time || '待核验' }}</p>
        </div>
      </div>
      <div v-if="parsedNotes" class="mx-5 mb-4 border-t border-gray-100 pt-4">
        <label class="mb-2">结构化数据（自动解析）</label>
        <div
          class="grid grid-cols-2 gap-2 rounded-lg bg-gray-50 p-3 text-sm md:grid-cols-3"
        >
          <div>
            <span class="text-gray-500">合同编号：</span
            ><span class="font-medium">{{ parsedNotes.contractNo }}</span>
          </div>
          <div>
            <span class="text-gray-500">开票类型：</span
            ><span class="font-medium">{{ parsedNotes.invoiceType }}</span>
          </div>
          <div>
            <span class="text-gray-500">开票日期：</span
            ><span class="font-medium">{{ parsedNotes.invoiceDate }}</span>
          </div>
          <div>
            <span class="text-gray-500">状态：</span
            ><span class="font-medium">{{ parsedNotes.status }}</span>
          </div>
          <div>
            <span class="text-gray-500">匹配状态：</span
            ><span class="font-medium">{{ parsedNotes.matchStatus }}</span>
          </div>
          <div>
            <span class="text-gray-500">来源：</span
            ><span class="font-medium">{{ parsedNotes.source }}</span>
          </div>
          <div class="col-span-2 md:col-span-3">
            <span class="text-gray-500">处理时间：</span
            ><span class="font-medium">{{ parsedNotes.processTime }}</span>
          </div>
        </div>
      </div>
      <div
        v-else-if="invoice.notes"
        class="mx-5 mb-4 border-t border-gray-100 pt-4"
      >
        <label>备注</label>
        <p class="whitespace-pre-wrap text-sm text-gray-600">
          {{ invoice.notes }}
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  calculateNetInvoiceAmount,
  isCustomerInvoiceDomainConflict,
} from './invoice-domain';
import type { InvoiceOverviewProps } from './types';

defineProps<InvoiceOverviewProps>();
</script>

<style scoped>
.section-title {
  @apply flex items-center gap-2 border-b border-gray-100 bg-gray-50/50 px-5 py-3 text-sm font-semibold text-gray-700;
}
.section-title span {
  @apply h-4 w-1 rounded-full;
}
.section-grid {
  @apply grid grid-cols-1 gap-4 px-5 py-4 md:grid-cols-2;
}
label {
  @apply mb-1 block text-xs text-gray-400;
}
p {
  @apply text-sm text-gray-900;
}
</style>
