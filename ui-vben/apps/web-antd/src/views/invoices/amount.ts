/** 将持久化的元金额转换为万元。 */
export function yuanToWan(amountYuan: number): number {
  return amountYuan / 10000
}