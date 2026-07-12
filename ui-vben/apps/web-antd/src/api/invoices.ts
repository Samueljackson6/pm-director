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
