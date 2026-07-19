import { requestClient } from '#/api/request'

export interface ReceiptItem {
  receipt_id: number
  project_id: string | null
  receipt_date: string | null
  amount: number | null
  receipt_no?: string | null
  payer_name?: string | null
  receipt_method?: string | null
  status: string | null
  notes?: string | null
}

/** 回款列表的全量汇总；接口金额单位固定为元。 */
export interface ReceiptSummary {
  currency_unit: '元'
  status: 'available' | 'pending_verification'
  receipt_total: number | null
  matched_total: number | null
  unmatched_total: number | null
}

export interface ReceiptListResponse {
  total: number
  page: number
  size: number
  items: ReceiptItem[]
  summary: ReceiptSummary
}

/** 回款列表 */
export async function getReceiptsApi(params?: {
  page?: number
  size?: number
  project_id?: string
}) {
  return requestClient.get<ReceiptListResponse>('/api/receipts', { params })
}

/** 回款详情 */
export async function getReceiptDetailApi(id: number) {
  return requestClient.get('/api/receipts/' + id)
}

/** 新增回款 */
export async function createReceiptApi(data: Record<string, any>) {
  return requestClient.post('/api/receipts', data)
}

/** 更新回款 */
export async function updateReceiptApi(id: number, data: Record<string, any>) {
  return requestClient.put('/api/receipts/' + id, data)
}

/** 删除回款 */
export async function deleteReceiptApi(id: number) {
  return requestClient.delete('/api/receipts/' + id)
}

/** 自动匹配 */
export async function autoMatchReceiptsApi(projectId?: string) {
  return requestClient.post('/api/receipts/auto-match', null, {
    params: projectId ? { project_id: projectId } : {}
  })
}

/** 项目回款汇总 */
export async function getReceiptSummaryApi(projectId: string) {
  return requestClient.get('/api/receipts/project/' + projectId + '/summary')
}
