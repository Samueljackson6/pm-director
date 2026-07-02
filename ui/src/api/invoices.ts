import { baseRequestClient } from '#/api/request'
export function getInvoicesApi(params?: any) { return baseRequestClient.get('/invoices', { params }) }
export function getInvoiceSummaryApi() { return baseRequestClient.get('/invoices/summary') }
