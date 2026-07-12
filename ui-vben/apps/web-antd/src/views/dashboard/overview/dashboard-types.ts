import type {
  DashboardOverview,
  PendingTasks,
  ProjectExecutionOverview,
  DashboardSummary,
  RecentContract,
} from '#/api/dashboard';

/** 四个视图的 key */
export type ViewKey = 'all' | 'management' | 'projects' | 'finance';

export const VIEW_KEYS: ViewKey[] = ['all', 'management', 'projects', 'finance'];

export function isValidViewKey(v: unknown): v is ViewKey {
  return typeof v === 'string' && (VIEW_KEYS as string[]).includes(v);
}

/** 语义化颜色（与 finance token 对齐） */
export const DASH_COLORS = {
  primary: '#1677FF',
  received: '#16A36A',
  invoiced: '#0F8FA8',
  warning: '#D98E04',
  danger: '#D64545',
};

export type DashTone = 'primary' | 'received' | 'invoiced' | 'warning' | 'danger' | 'none';

/** 月度开票/回款趋势系列定义（跨页一致） */
export const FINANCE_SERIES = [
  { name: '已开票', valueField: 'invoiced_wan', color: '#0F8FA8' },
  { name: '已回款', valueField: 'received_wan', color: '#16A36A' },
];

/** 金额格式化（万元），保留 2 位；null/NaN 显示破折号 */
export function fmtMoney(v: number | null | undefined, digits = 2): string {
  if (v == null || Number.isNaN(v)) return '—';
  return Number(v).toFixed(digits);
}

/** 比率格式化（%），保留 1 位 */
export function fmtRate(v: number | null | undefined, digits = 1): string {
  if (v == null || Number.isNaN(v)) return '—';
  return Number(v).toFixed(digits);
}

/** 安全百分比（避免除零），返回带 % 的字符串或破折号 */
export function pctSafe(
  numerator: number | null | undefined,
  denominator: number | null | undefined,
  digits = 1,
): string {
  const d = denominator ?? 0;
  const n = numerator ?? 0;
  if (d === 0) return '—';
  return `${((n / d) * 100).toFixed(digits)}%`;
}

/** 风险等级 → 语义色调 */
export function riskTone(level: string): DashTone {
  const l = (level || '').toLowerCase();
  if (l.includes('high') || l.includes('高')) return 'danger';
  if (l.includes('mid') || l.includes('medium') || l.includes('中')) return 'warning';
  if (l.includes('low') || l.includes('低')) return 'received';
  return 'none';
}

/** 风险等级 → a-tag color */
export function riskTagColor(level: string): string {
  const t = riskTone(level);
  return t === 'danger' ? 'red' : t === 'warning' ? 'orange' : t === 'received' ? 'green' : 'default';
}

export type {
  DashboardOverview,
  PendingTasks,
  ProjectExecutionOverview,
  DashboardSummary,
  RecentContract,
};
