import { requestClient } from '#/api/request'

/**
 * 经营与任务驾驶舱聚合接口（GET /api/dashboard/overview）。
 * 所有金额均以「万元」返回，具体口径以 data_contract 为准。
 */

export interface DashboardSummary {
  contract_count: number
  contract_total_amount: number
  invoiced_amount: number
  received_amount: number
  unreceived_amount: number
  receipt_rate: number
  uninvoiced_amount: number
  sub_invoiced_amount: number
  sub_paid_amount: number
  currency_unit: string
}

export interface ContractTypeGroup {
  project_type: string
  count: number
  amount: number
}

export interface ContractStatusGroup {
  contract_status: string
  count: number
  amount: number
}

export interface InvoiceStatusGroup {
  status: string
  count: number
  amount_wan: number
}

export interface MonthlyTrend {
  month: string
  invoiced_wan: number
  received_wan: number
}

export interface FinanceTrendPoint {
  batch_id: string
  import_time: string
  invoiced_wan: number
  received_wan: number
}

export interface TopCustomer {
  customer: string
  count: number
  total_amount: number
}

export interface PendingTasks {
  unmatched_payments: number
  pending_deliverables: number
  overdue_payments: number
  uninvoiced_contracts: number
}

export interface RecentContract {
  contract_id: string
  project_name: string
  contract_amount: number
  party_a: string
  sign_date: string
  project_type: string
  contract_status: string
  invoice_total: number
  payment_total: number
}

export interface DashboardFilters {
  period: string
  from: string | null
  to: string | null
  project_type: string | null
}

export interface DashboardTarget {
  path: string
  query: Record<string, string>
}

/** 驾驶舱中可直接下钻的任务、风险或核验缺口。 */
export interface DashboardAction {
  action_id: string
  category: 'risk' | 'task' | 'verification'
  title: string
  object_type: string
  object_id: string
  reason: string
  due_date: string | null
  owner: string | null
  status: string
  target: DashboardTarget
}

export interface DashboardMetricContract {
  key: string
  label: string
  unit: string
  definition: string
  source: string[]
  coverage: string
  verification_status: string
  data_as_of: string | null
}

export interface DashboardSourceContract {
  key: string
  label: string
  source: string[]
  coverage: string
  verification_status: string
  data_as_of: string | null
}

export interface DashboardDataContract {
  generated_at: string
  metrics: DashboardMetricContract[]
  sources: DashboardSourceContract[]
  verification_summary: {
    status: string
    pending_action_count: number
    description: string
  }
}

export interface DashboardRecentChange {
  object_type: 'contract' | 'project'
  object_id: string
  title: string
  changed_at: string | null
  change_type: string
  target: DashboardTarget
}

export interface ProjectExecutionProject {
  project_id: string
  project_name: string
  customer_name: string
  project_status: string
  risk_level: string
  overall_progress: number
  project_manager: string
  planned_end: string
  total_contract_amount: number
}

export interface ProjectExecutionOverview {
  total_projects: number
  active_projects: number
  completed_projects: number
  high_risk_projects: number
  missing_manager_projects: number
  overdue_stages: number
  pending_deliverables: number
  status_distribution: Array<{ status: string; count: number }>
  risk_distribution: Array<{ risk_level: string; count: number }>
  recent_projects: ProjectExecutionProject[]
}

export interface DashboardOverview {
  generated_at: string
  filters: DashboardFilters
  summary: DashboardSummary
  contracts_by_type: ContractTypeGroup[]
  contracts_by_status: ContractStatusGroup[]
  invoice_status_distribution: InvoiceStatusGroup[]
  invoice_monthly: MonthlyTrend[]
  finance_trend: FinanceTrendPoint[]
  top_customers: TopCustomer[]
  pending_tasks: PendingTasks
  recent_contracts: RecentContract[]
  recent_changes: DashboardRecentChange[]
  project_execution: ProjectExecutionOverview
  task_actions: DashboardAction[]
  risk_actions: DashboardAction[]
  verification_actions: DashboardAction[]
  data_contract: DashboardDataContract
}

export interface DashboardQueryParams {
  period?: string
  from?: string
  to?: string
  project_type?: string
}

/** requestClient 会自动解包 Vben 响应的 data 字段。 */
export function getDashboardOverviewApi(params?: DashboardQueryParams) {
  return requestClient.get<DashboardOverview>('/api/dashboard/overview', { params })
}
