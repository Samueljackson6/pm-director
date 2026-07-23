export function formatWanYuan(value: number | null | undefined): string {
  if (value == null) return '-'
  return (Number(value) / 10000).toFixed(2)
}

export function yuanToWan(value: number | null | undefined): number | null {
  if (value == null) return null
  return Math.round((value / 10000) * 100) / 100
}
