import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const RECEIPTS_DIRECTORY = dirname(fileURLToPath(new URL('../index.vue', import.meta.url)))
const source = readFileSync(join(RECEIPTS_DIRECTORY, 'index.vue'), 'utf8')

describe('客户回款列表领域真值', () => {
  it('统计卡片直接使用后端全量汇总，不能从当前页 items 归约', () => {
    expect(source).toContain('data.summary')
    expect(source).not.toMatch(/items\.reduce\s*\(/u)
    expect(source).toContain('receiptSummary.value = data.summary')
  })

  it('待核验与已知零值必须区分展示，且将后端元统一转换为万元', () => {
    expect(source).toMatch(/function formatSummaryAmount[\s\S]*value == null[\s\S]*待核验/u)
    expect(source).toMatch(/Number\(value\)\s*\/\s*10_?000/u)
    expect(source).toMatch(/\.toFixed\(2\)/u)
  })

  it('挂载和加载仅发起读取，自动匹配只由按钮显式调用', () => {
    expect(source).toMatch(/onMounted\s*\(\s*loadData\s*\)/u)
    const loadData = source.match(/async function loadData\s*\(\s*\)\s*\{[\s\S]*?\n\}/u)?.[0] ?? ''
    expect(loadData).toContain('getReceiptsApi')
    expect(loadData).not.toContain('autoMatchReceiptsApi')
    expect(source).toMatch(/async function autoMatch[\s\S]*autoMatchReceiptsApi\s*\(/u)
    expect(source).toContain('自动匹配（写入关联）')
  })
})
