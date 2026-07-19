<template>
  <section
    id="receipts"
    class="scroll-mt-16 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"
  >
    <header
      class="flex flex-wrap items-center gap-2 border-b border-slate-100 bg-slate-50/80 px-4 py-3 sm:px-5"
    >
      <span class="h-4 w-1 rounded-full bg-emerald-500"></span
      ><span class="text-sm font-semibold text-slate-700">关联回款</span
      ><span class="ml-auto text-xs text-slate-400"
        >已匹配 {{ fmtMoney(matchedAmount) }} 元</span
      >
    </header>
    <div class="px-4 py-4 sm:px-5">
      <template v-if="linkedReceipts.length"
        ><div class="space-y-2">
          <div
            v-for="receipt in linkedReceipts"
            :key="receipt.receipt_id"
            class="flex cursor-pointer flex-col gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3 transition-colors hover:border-emerald-200 hover:bg-emerald-50/60 sm:flex-row sm:items-center sm:justify-between"
            @click="openReceipt(receipt.receipt_id)"
          >
            <div>
              <div class="truncate text-sm font-medium text-slate-900">
                {{ receipt.receipt_no || '回款 #' + receipt.receipt_id }}
              </div>
              <div class="mt-1 text-xs text-slate-500">
                {{ receipt.receipt_date }} · {{ receipt.receipt_method || '-' }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm font-semibold text-emerald-600"
                >{{ fmtMoney(receipt.link_amount ?? receipt.amount) }} 元</span
              ><a-button
                type="link"
                size="small"
                danger
                @click.stop="$emit('unlinkReceipt', receipt)"
                >取消关联</a-button
              >
            </div>
          </div>
        </div>
        <div class="mt-3 border-t border-slate-100 pt-3 text-sm text-slate-600">
          <span class="text-gray-500">匹配状态：</span
          ><a-tag
            v-if="
              invoiceAmount != null &&
              matchedAmount != null &&
              matchedAmount >= invoiceAmount
            "
            color="success"
            >完全匹配</a-tag
          ><a-tag
            v-else-if="matchedAmount != null && matchedAmount > 0"
            color="warning"
            >部分匹配 ({{ fmtMoney(matchedAmount) }}/{{
              fmtMoney(invoiceAmount)
            }})</a-tag
          ><a-tag v-else-if="matchedAmount === 0">未匹配</a-tag
          ><a-tag v-else>待核验</a-tag>
        </div></template
      >
      <div v-else class="py-6 text-center">
        <a-empty description="暂无关联回款" /><a-button
          type="link"
          size="small"
          @click="$emit('linkReceipt')"
          >+ 关联回款</a-button
        >
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import type { InvoiceReceipt } from './types';

defineEmits<{ linkReceipt: []; unlinkReceipt: [receipt: InvoiceReceipt] }>();
defineProps<{
  readonly linkedReceipts: readonly InvoiceReceipt[];
  readonly matchedAmount: number | null;
  readonly invoiceAmount: number | null | undefined;
  readonly fmtMoney: (value: number | null | undefined) => string;
}>();

const router = useRouter();
function openReceipt(id: number): void {
  router.push({ name: 'CustomerReceiptDetail', query: { id } });
}
</script>
