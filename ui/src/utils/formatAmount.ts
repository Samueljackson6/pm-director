/**
 * 金额格式化工具 — 后端输出单位为元，前端统一转为万元展示。
 */

/** 将元转换为万元字符串（保留2位小数），null/None 返回 '-'。 */
export function formatWanYuan(value: number | null | undefined): string {
  if (value == null) return '-'
  return (value / 10000).toFixed(2)
}

/** 将元转换为万元数字（保留2位小数）。 */
export function yuanToWan(value: number | null | undefined): number | null {
  if (value == null) return null
  return Math.round((value / 10000) * 100) / 100
}
