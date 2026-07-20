import { requestClient } from '#/api/request'

export interface ContractItem {
  contract_id: string
  project_name: string
  project_type: string
  contract_amount: number
  party_a: string
  party_b: string
  sign_date: string
  invoice_total: number
  payment_total: number
  official_name?: string
}

export interface ContractDetail {
  budgets?: any[]
  clauses?: any[]
  contract: ContractItem & { service_content: string; service_period: string }
  deliverables: any[]
  files: any[]
  finance: any
  invoices?: any[]
  payments: any[]
  projects: any[]
  stages: any[]
}

export interface ContractQueryParams {
  page?: number
  size?: number
  search?: string
  sort?: string
  project_type?: string
  contract_status?: string
  min_amount?: number
  max_amount?: number
}

export interface PaginatedResult<T> {
  items: T[]
  total: number
  page: number
  size: number
}

/** 合同列表（分页），requestClient 自动解包 data 字段 */
export async function getContractsApi(params?: ContractQueryParams) {
  return requestClient.get<PaginatedResult<ContractItem>>('/api/contracts', { params })
}

/** 合同详情 */
export async function getContractDetailApi(id: string) {
  return requestClient.get<ContractDetail>('/api/contracts/' + id)
}

/** 上传合同文件（multipart/form-data） */
export async function uploadContractFileApi(contractId: string, file: File) {
  const fd = new FormData()
  fd.append('file', file)
  return requestClient.post<{ file_id: string; file_name: string }>(
    `/api/contracts/${contractId}/files`,
    fd,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
}

/** 合同文件下载地址 */
export function contractFileDownloadUrl(contractId: string, fileId: string): string {
  return `/api/contracts/${contractId}/files/${fileId}/download`
}

/** 统计数据 */
export async function getStatsApi() {
  return requestClient.get('/api/stats')
}

/** 合同类型分布 */
export async function getTypesApi() {
  return requestClient.get('/api/stats/types')
}

/** 更新合同 */
export async function updateContractApi(id: string, data: Record<string, any>) {
  return requestClient.put(`/api/contracts/${id}`, data)
}

/** 新增合同 */
export async function createContractApi(data: Record<string, any>) {
  return requestClient.post('/api/contracts', data)
}

/** 合同团队信息 */
export async function getContractTeamApi(id: string) {
  return requestClient.get(`/api/contracts/${id}/team`)
}

/** 合同付款列表 */
export async function getContractPaymentsApi(id: string) {
  return requestClient.get(`/api/contracts/${id}/payments`)
}

/** 新增付款记录 */
export async function createPaymentApi(contractId: string, data: Record<string, any>) {
  return requestClient.post(`/api/contracts/${contractId}/payments`, data)
}

/** 更新付款记录 */
export async function updatePaymentApi(contractId: string, paymentId: string, data: Record<string, any>) {
  return requestClient.put(`/api/contracts/${contractId}/payments/${paymentId}`, data)
}

/** 删除付款记录 */
export async function deletePaymentApi(contractId: string, paymentId: string) {
  return requestClient.delete(`/api/contracts/${contractId}/payments/${paymentId}`)
}
