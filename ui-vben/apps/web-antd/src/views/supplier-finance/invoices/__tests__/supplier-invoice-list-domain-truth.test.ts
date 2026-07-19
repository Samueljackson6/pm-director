import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const directory = dirname(fileURLToPath(new URL('../index.vue', import.meta.url)))
const source = readFileSync(join(directory, 'index.vue'), 'utf8')

describe('供应商收票列表领域真值', () => {
  it('保护资金语义与分轨边界', () => {
    expect(source).toContain("direction: 'inbound'")
    expect(source).toContain("invoice_type: '供应商开票'")
    expect(source).toContain('客户回款不计入本列表')
  })

  it('区分数据源、零值与待核验', () => {
    expect(source).toContain('source_not_established')
    expect(source).toContain('known_zero')
    expect(source).toContain('pending_verification')
    expect(source).toContain('待核验')
  })
})
