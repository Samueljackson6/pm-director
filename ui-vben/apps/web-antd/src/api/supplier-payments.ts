import { requestClient } from '#/api/request'

export interface SupplierPaymentItem {
  payment_id: number
  supplier_id: string
  project_id: string
  payment_date: string
  amount: number
  payment_method?: string
  status: string
  notes?: string
  supplier_name?: string
  short_name?: string
}

/** 供应商付款列表 */
export async function getSupplierPaymentsApi(params?: {
  page?: number
  size?: number
  supplier_id?: string
}) {
  return requestClient.get('/api/suppliers/payments', { params })
}

/** 付款详情 */
export async function getSupplierPaymentDetailApi(id: number) {
  return requestClient.get('/api/suppliers/payments/' + id)
}

/** 新增付款 */
export async function createSupplierPaymentApi(data: Record<string, any>) {
  return requestClient.post('/api/suppliers/payments', data)
}

/** 更新付款 */
export async function updateSupplierPaymentApi(id: number, data: Record<string, any>) {
  return requestClient.put('/api/suppliers/payments/' + id, data)
}

/** 删除付款 */
export async function deleteSupplierPaymentApi(id: number) {
  return requestClient.delete('/api/suppliers/payments/' + id)
}
