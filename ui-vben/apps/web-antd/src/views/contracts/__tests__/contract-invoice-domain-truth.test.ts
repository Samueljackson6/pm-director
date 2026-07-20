import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const CONTRACTS_DIRECTORY = dirname(
  fileURLToPath(new URL('../detail.vue', import.meta.url)),
)

function readDetailComponent(fileName: string): string {
  return readFileSync(
    join(CONTRACTS_DIRECTORY, 'components', 'detail', fileName),
    'utf8',
  )
}

describe('合同详情客户开票领域真值', () => {
  it('以万元录入的金额在创建前显式换算为元', () => {
    // 领域口径：界面显示和输入使用万元，发票存储与 API 提交统一使用元。
    const source = readDetailComponent('ContractInvoiceModal.vue')

    expect(source).toMatch(
      /createInvoiceApi\s*\(\s*\{[\s\S]*?amount\s*:\s*[^,}]*\*\s*10_?000[\s\S]*?\}\s*\)/u,
    )
  })

  it('合同详情入口只能创建客户销项发票，不能混入回款领域', () => {
    // 回款属于 receipts 域；本入口必须固定为客户开票和 outbound，不能给用户改写。
    const source = readDetailComponent('ContractInvoiceModal.vue')

    expect(source).toMatch(
      /createInvoiceApi\s*\(\s*\{[\s\S]*?invoice_type\s*:\s*['"]客户开票['"][\s\S]*?direction\s*:\s*['"]outbound['"][\s\S]*?\}\s*\)/u,
    )
    expect(source).not.toContain('客户回款')
    expect(source).not.toContain('value="inbound"')
    expect(source).not.toContain('received_date')
    expect(source).not.toContain('value="已回款"')
  })

  it('每次打开客户开票表单都会从新的默认值开始', () => {
    // 防止用户关闭后再次打开时，沿用上一张发票的金额、票号或备注。
    const source = readDetailComponent('ContractInvoiceModal.vue')

    expect(source).toMatch(
      /watch\s*\(\s*open\s*,[\s\S]*?if\s*\(\s*isOpen\s*\)[\s\S]*?form\.value\s*=\s*createForm\s*\(\s*\)/u,
    )
  })

  it('未知财务快照不会被伪装为 0.00，且已知零值仍可正常格式化', () => {
    // missing 与 0 是不同事实：前者应保持未知，后者才可显示 0.00。
    const financeSource = readDetailComponent('ContractFinance.vue')
    const headerSource = readDetailComponent('ContractHeaderEvidence.vue')

    for (const source of [financeSource, headerSource]) {
      expect(source).not.toMatch(/Number\s*\(\s*value\s*\|\|\s*0\s*\)/u)
      expect(source).toMatch(/Number\s*\(\s*value\s*\)\.toFixed\s*\(\s*2\s*\)/u)
    }
  })

  it('创建客户发票不会触发自动匹配', () => {
    // 自动匹配会把发票和回款域耦合，匹配应由独立流程显式发起。
    const source = readDetailComponent('ContractInvoiceModal.vue')

    expect(source).not.toMatch(/(?:auto)?match(?:Invoice|Payment)|自动匹配/iu)
  })
})
