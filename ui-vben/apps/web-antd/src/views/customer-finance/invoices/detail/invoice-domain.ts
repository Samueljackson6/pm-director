import type { InvoiceRecord } from './types';

export function isCustomerInvoiceDomainConflict(
  invoice: InvoiceRecord,
): boolean {
  const isInboundDirection = invoice.direction === 'inbound';
  const isHistoricalWrongType =
    invoice.invoice_type === '客户回款' ||
    invoice.invoice_type === '供应商开票';

  return (
    isInboundDirection ||
    isHistoricalWrongType ||
    invoice.direction !== 'outbound' ||
    invoice.invoice_type !== '客户开票'
  );
}

export function calculateNetInvoiceAmount(
  invoice: InvoiceRecord,
): number | null {
  if (invoice.amount == null || invoice.tax_rate == null) return null;
  const rate = invoice.tax_rate <= 1 ? invoice.tax_rate : invoice.tax_rate / 100;
  return invoice.amount / (1 + rate);
}
