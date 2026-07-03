import { requestClient } from '#/api/request'

export interface ProjectItem {
  project_id: string
  project_name: string
  customer_name: string
  project_type: string
  total_contract_amount: number
  project_status: string
  project_manager: string
  overall_progress: number
  risk_level: string
  planned_start: string
  planned_end: string
  tech_lead: string
  sales_lead: string
}

export interface ProjectContract {
  contract_id: string
  project_name: string
  contract_amount: number
  sign_date: string
  stages_count: number
  payments_count: number
  deliverables_count: number
}

export interface ProjectDetail {
  project: ProjectItem
  contracts: ProjectContract[]
}

export interface ProjectProgress {
  stage_rate: number
  payment_rate: number
  deliverable_rate: number
  overall: number
  total_stages: number
  completed_stages: number
  in_progress_stages: number
  pending_stages: number
}

export interface PaginatedResult<T> {
  items: T[]
  total: number
  page: number
  size: number
}

/** 项目列表（分页），requestClient 自动解包 data 字段 */
export async function getProjectsApi(params?: any) {
  return requestClient.get<PaginatedResult<ProjectItem>>('/api/projects', { params })
}

/** 项目详情 */
export async function getProjectDetailApi(id: string) {
  return requestClient.get<ProjectDetail>('/api/projects/' + id)
}

/** 项目阶段列表 */
export async function getProjectStagesApi(id: string) {
  return requestClient.get<any[]>('/api/projects/' + id + '/stages')
}

/** 项目付款计划 */
export async function getProjectPaymentsApi(id: string) {
  return requestClient.get<any[]>('/api/projects/' + id + '/payments')
}

/** 项目交付物 */
export async function getProjectDeliverablesApi(id: string) {
  return requestClient.get<any[]>('/api/projects/' + id + '/deliverables')
}

/** 项目进度 */
export async function getProjectProgressApi(id: string) {
  return requestClient.get<ProjectProgress>('/api/projects/' + id + '/progress')
}
