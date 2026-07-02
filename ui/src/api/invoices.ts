import { requestClient } from '#/api/request'

export interface InvoiceItem {
  invoice_id: number
  project_id: string
  invoice_type: string
  invoice_date: string
  amount: number
  status: string
}

export interface InvoiceSummary {
  project_id: string
  project_name: string
  invoiced: number
  received: number
}

/** 发票列表 */
export async function getInvoicesApi(params?: any) {
  return requestClient.get('/api/invoices', { params })
}

/** 发票汇总（按项目） */
export async function getInvoiceSummaryApi() {
  return requestClient.get('/api/invoices/summary')
}
