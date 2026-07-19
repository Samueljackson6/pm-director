import type {
  DashboardOverview,
  PendingTasks,
  ProjectExecutionOverview,
  DashboardSummary,
  RecentContract,
} from '#/api/dashboard'

/** 驾驶舱在同一个正式路由下的五个决策视角。 */
export type ViewKey = 'all' | 'management' | 'projects' | 'finance' | 'verification'

export const VIEW_KEYS: ViewKey[] = [
  'all',
  'management',
  'projects',
  'finance',
  'verification',
]

export function isValidViewKey(value: unknown): value is ViewKey {
  return typeof value === 'string' && (VIEW_KEYS as string[]).includes(value)
}

export type DashTone =
  | 'danger'
  | 'invoiced'
  | 'none'
  | 'primary'
  | 'received'
  | 'warning'

/** 图表系列色从集中 token 镜像取值，禁止业务组件新增色板。 */
export const DASH_COLORS: Record<Exclude<DashTone, 'none'>, string> = {
  primary: '#1D4ED8',
  received: '#067647',
  invoiced: '#0F766E',
  warning: '#934A00',
  danger: '#B42318',
}

export const FINANCE_SERIES = [
  { name: '已开票', valueField: 'invoiced_wan', color: DASH_COLORS.invoiced },
  { name: '已回款', valueField: 'received_wan', color: DASH_COLORS.received },
]

/** 金额统一以万元显示；空值不伪装为零。 */
export function fmtMoney(value: number | null | undefined, digits = 2): string {
  if (value == null || Number.isNaN(value)) return '待核验'
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
}

export function fmtRate(value: number | null | undefined, digits = 1): string {
  if (value == null || Number.isNaN(value)) return '待核验'
  return Number(value).toFixed(digits)
}

export function pctSafe(
  numerator: number | null | undefined,
  denominator: number | null | undefined,
  digits = 1,
): string {
  const divisor = denominator ?? 0
  const dividend = numerator ?? 0
  if (divisor === 0) return '待核验'
  return `${((dividend / divisor) * 100).toFixed(digits)}%`
}

export function riskTone(level: string): DashTone {
  const normalized = (level || '').toLowerCase()
  if (normalized.includes('high') || normalized.includes('高')) return 'danger'
  if (normalized.includes('mid') || normalized.includes('medium') || normalized.includes('中')) return 'warning'
  if (normalized.includes('low') || normalized.includes('低')) return 'received'
  return 'none'
}

export function riskTagColor(level: string): string {
  const tone = riskTone(level)
  if (tone === 'danger') return 'red'
  if (tone === 'warning') return 'orange'
  if (tone === 'received') return 'green'
  return 'default'
}

export type {
  DashboardOverview,
  DashboardSummary,
  PendingTasks,
  ProjectExecutionOverview,
  RecentContract,
}
