import { requestClient } from '#/api/request'

export interface InvoiceItem {
  invoice_id: number
  project_id: string
  invoice_type: string
  invoice_date: string
  amount: number
  tax_rate?: number
  tax_amount?: number
  status: string
  invoice_no?: string
  supplier_id?: string
  supplier_name?: string
  direction?: string
  payment_status?: string
  verification_status?: string
  notes?: string
}

export interface InvoiceSummaryItem {
  project_id: string
  project_name: string
  contract_amount: number
  invoiced: number
  received: number
  inv_count: number
  pay_count: number
}

export interface UnmatchedInvoiceItem extends InvoiceItem {
  project_name?: string
  supplier_name?: string
}

export interface MatchingSuggestion {
  payment_id: number
  supplier_id?: string
  project_id: string
  payment_date: string
  amount: number
  match_reason: string
}

export interface AutoMatchResult {
  matched: boolean
  matches: Array<{ payment_id: number; match_type: string; amount: number }>
  message: string
}

/** 发票详情 */
export interface InvoiceDetail {
  invoice: InvoiceItem
}

/** 发票详情 */
export async function getInvoiceDetailApi(id: number) {
  return requestClient.get<InvoiceDetail>('/api/invoices/' + id)
}

/** 发票列表 */
export async function getInvoicesApi(params?: {
  page?: number
  size?: number
  project_id?: string
  direction?: 'outbound' | 'inbound'
  invoice_type?: string
}) {
  return requestClient.get('/api/invoices', { params })
}

/** 发票汇总（按项目） */
export async function getInvoiceSummaryApi() {
  return requestClient.get<{ items: InvoiceSummaryItem[]; total: number }>('/api/invoices/summary')
}

/** 更新发票 */
export async function updateInvoiceApi(id: number, data: Record<string, any>) {
  return requestClient.put('/api/invoices/' + id, data)
}

/** 新增发票 */
export async function createInvoiceApi(data: Record<string, any>) {
  return requestClient.post('/api/invoices', data)
}

/** 删除发票 */
export async function deleteInvoiceApi(id: number) {
  return requestClient.delete('/api/invoices/' + id)
}

/** 获取未匹配的供应商发票 */
export async function getUnmatchedInvoicesApi(params?: { page?: number; size?: number }) {
  return requestClient.get('/api/supplier-invoices/unmatched', { params })
}

/** 获取发票匹配建议 */
export async function getMatchingSuggestionsApi(invoiceId: number) {
  return requestClient.get(`/api/supplier-invoices/matching-suggestions/${invoiceId}`)
}

/** 自动匹配发票到付款 */
export async function autoMatchInvoiceApi(invoiceId: number) {
  return requestClient.post<AutoMatchResult>(`/api/supplier-invoices/auto-match/${invoiceId}`)
}

/** 更新发票状态 */
export async function updateInvoiceStatusApi(id: number, status: string) {
  return requestClient.put(`/api/supplier-invoices/${id}/status`, { status })
}

/** 获取发票关联的付款记录 */
export async function getLinkedPaymentsApi(invoiceId: number) {
  return requestClient.get(`/api/supplier-invoices/${invoiceId}/linked-payments`)
}
