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
}

export interface ContractDetail {
  contract: ContractItem & { service_content: string; service_period: string }
  stages: any[]
  payments: any[]
  deliverables: any[]
  finance: any
}

export interface PaginatedResult<T> {
  items: T[]
  total: number
  page: number
  size: number
}

/** 合同列表（分页），requestClient 自动解包 data 字段 */
export async function getContractsApi(params?: any) {
  return requestClient.get<PaginatedResult<ContractItem>>('/contracts', { params })
}

/** 合同详情 */
export async function getContractDetailApi(id: string) {
  return requestClient.get<ContractDetail>('/contracts/' + id)
}

/** 统计数据 */
export async function getStatsApi() {
  return requestClient.get('/stats')
}

/** 合同类型分布 */
export async function getTypesApi() {
  return requestClient.get('/stats/types')
}
