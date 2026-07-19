<template>
  <section
    id="receipts"
    class="scroll-mt-16 overflow-hidden rounded-lg border border-gray-200 bg-white"
  >
    <header
      class="flex items-center gap-2 border-b border-gray-100 bg-gray-50/50 px-5 py-3"
    >
      <span class="h-4 w-1 rounded-full bg-green-500"></span
      ><span class="text-sm font-semibold text-gray-700">关联回款</span
      ><span class="ml-auto text-xs text-gray-400"
        >已匹配 {{ fmtMoney(matchedAmount) }} 元</span
      >
    </header>
    <div class="px-5 py-4">
      <template v-if="linkedReceipts.length"
        ><div class="space-y-2">
          <div
            v-for="receipt in linkedReceipts"
            :key="receipt.receipt_id"
            class="flex cursor-pointer items-center justify-between rounded-lg bg-gray-50 p-3 transition-colors hover:bg-green-50/50"
            @click="openReceipt(receipt.receipt_id)"
          >
            <div>
              <div class="text-sm font-medium text-gray-900">
                {{ receipt.receipt_no || '回款 #' + receipt.receipt_id }}
              </div>
              <div class="text-xs text-gray-400">
                {{ receipt.receipt_date }} · {{ receipt.receipt_method || '-' }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm font-semibold text-green-600"
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
        <div class="mt-3 border-t border-gray-100 pt-3 text-sm">
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
