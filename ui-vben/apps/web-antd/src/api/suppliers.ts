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
  return requestClient.get('/api/suppliers')
}

/** 供应商详情 */
export async function getSupplierDetailApi(id: string) {
  return requestClient.get('/api/suppliers/' + id)
}

/** 更新供应商 */
export async function updateSupplierApi(id: string, data: Record<string, any>) {
  return requestClient.put('/api/suppliers/' + id, data)
}

/** 新增供应商 */
export async function createSupplierApi(data: Record<string, any>) {
  return requestClient.post('/api/suppliers', data)
}

/** 创建供应商付款记录 */
export async function createSupplierPaymentApi(data: Record<string, any>) {
  return requestClient.post('/api/suppliers/payments', data)
}

// ============ 供应商联系人 API ============

/** 获取供应商联系人列表 */
export async function getSupplierContactsApi(supplierId: string) {
  return requestClient.get(`/api/suppliers/${supplierId}/contacts`)
}

/** 新增联系人 */
export async function createContactApi(supplierId: string, data: Record<string, any>) {
  return requestClient.post(`/api/suppliers/${supplierId}/contacts`, data)
}

/** 更新联系人 */
export async function updateContactApi(supplierId: string, contactId: number, data: Record<string, any>) {
  return requestClient.put(`/api/suppliers/${supplierId}/contacts/${contactId}`, data)
}

/** 删除联系人 */
export async function deleteContactApi(supplierId: string, contactId: number) {
  return requestClient.delete(`/api/suppliers/${supplierId}/contacts/${contactId}`)
}

// ============ 企查查 MCP API ============

/**
 * 获取供应商企查查详细信息（5个维度聚合）
 *
 * 包含：
 * 1. 工商信息
 * 2. 企业简介
 * 3. 风险扫描
 * 4. 软件著作权
 * 5. 对外投资
 */
export async function getSupplierQccInfoApi(creditCode: string) {
  return requestClient.get(`/api/suppliers/qcc/${creditCode}`)
}

/** 企查查 MCP - 工商信息 */
export async function getQccBasicApi(creditCode: string) {
  return requestClient.get(`/api/suppliers/qcc/${creditCode}/basic`)
}

/** 企查查 MCP - 企业简介 */
export async function getQccProfileApi(creditCode: string) {
  return requestClient.get(`/api/suppliers/qcc/${creditCode}/profile`)
}

/** 企查查 MCP - 风险扫描 */
export async function getQccRiskApi(creditCode: string) {
  return requestClient.get(`/api/suppliers/qcc/${creditCode}/risk`)
}

/** 企查查 MCP - 软件著作权 */
export async function getQccSoftwareApi(creditCode: string) {
  return requestClient.get(`/api/suppliers/qcc/${creditCode}/software`)
}

/** 企查查 MCP - 对外投资 */
export async function getQccInvestmentApi(creditCode: string) {
  return requestClient.get(`/api/suppliers/qcc/${creditCode}/investment`)
}
