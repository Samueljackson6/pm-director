import { requestClient } from '#/api/request'

/**
 * Dashboard 聚合接口（T8 后端 `GET /api/dashboard/overview`）。
 *
 * 该端点在单次请求中返回财务仪表盘所需的全部 KPI / 图表 / 列表数据，
 * 所有金额字段单位均为「万元」（见 `DashboardSummary.currency_unit`）。
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
}

export interface DashboardQueryParams {
  period?: string
  from?: string
  to?: string
  project_type?: string
}

/** 财务仪表盘聚合数据（requestClient 自动解包 data 字段） */
export function getDashboardOverviewApi(params?: DashboardQueryParams) {
  return requestClient.get<DashboardOverview>('/api/dashboard/overview', {
    params,
  })
}
