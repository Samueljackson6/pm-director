import { requestClient } from '#/api/request'

export interface SupplierItem {
  supplier_id: string
  supplier_name: string
  short_name: string
  total_contract_amount: number
  total_invoiced: number
  total_paid: number
  total_unpaid: number
  contract_count: number
  status: string
}

/** 供应商列表 */
export async function getSuppliersApi() {
  return requestClient.get('/suppliers')
}

/** 供应商详情 */
export async function getSupplierDetailApi(id: string) {
  return requestClient.get('/suppliers/' + id)
}
