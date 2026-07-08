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
  contract: ContractItem & { service_content: string; service_period: string }
  stages: any[]
  payments: any[]
  deliverables: any[]
  finance: any
  projects: any[]
  files: any[]
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
