import { existsSync, readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

import {
  contractDetailComponentPath,
  countPureLines,
  readContractDetailRoot,
} from './contract-detail-source-fixture'

const REQUIRED_SECTIONS = [
  ['ContractHeaderEvidence.vue', 'ContractHeaderEvidence'],
  ['ContractFulfillment.vue', 'ContractFulfillment'],
  ['ContractFinance.vue', 'ContractFinance'],
  ['ContractRelationsFiles.vue', 'ContractRelationsFiles'],
] as const

describe('合同详情结构边界', () => {
  it('将标题证据、履约、财务、关系文件拆为可独立评审的组件', () => {
    // Given：1355 行的合同详情需要按业务责任拆分。
    const rootSource = readContractDetailRoot()

    // When：检查四个明确边界的组件文件及父页编排标签。
    const sectionResults = REQUIRED_SECTIONS.map(([fileName, componentName]) => {
      const path = contractDetailComponentPath(fileName)
      return {
        componentName,
        exists: existsSync(path),
        path,
      }
    })

    // Then：每个业务区必须真实存在，且由父页组合，而非只移动注释。
    for (const result of sectionResults) {
      expect(result.exists, `${result.componentName} 组件缺失`).toBe(true)
      expect(rootSource, `${result.componentName} 未被父页编排`).toContain(
        `<${result.componentName}`,
      )
    }
  })

  it('显著缩小父页并限制脚本为可审阅的编排层', () => {
    // Given：父页当前总计约 1355 行，脚本同时承担多个业务责任。
    const rootSource = readContractDetailRoot()

    // When：统计父页总行数与 script setup 的纯代码行数。
    const totalLines = rootSource.split(/\r?\n/u).length
    const scriptSource = rootSource.match(
      /<script\s+setup[^>]*>([\s\S]*?)<\/script>/u,
    )?.[1]

    // Then：父页至少缩减六成，脚本只保留可控的页面编排。
    expect(totalLines).toBeLessThanOrEqual(520)
    expect(scriptSource, '合同详情缺少 script setup').toBeDefined()
    expect(countPureLines(scriptSource ?? '')).toBeLessThanOrEqual(220)
  })

  it('保证拆分后的每个业务组件不再形成新的超大文件', () => {
    // Given：四个业务组件已经按责任边界建立。
    const sectionPaths = REQUIRED_SECTIONS.map(([fileName]) =>
      contractDetailComponentPath(fileName),
    )

    // When：只读取真实存在的组件并统计纯代码行。
    const existingSections = sectionPaths.filter(existsSync).map((path) => ({
      path,
      pureLines: countPureLines(readFileSync(path, 'utf8')),
    }))

    // Then：组件不可通过把巨型父页平移成另一个巨型文件来过关。
    expect(existingSections).toHaveLength(REQUIRED_SECTIONS.length)
    for (const section of existingSections) {
      expect(section.pureLines, `${section.path} 超过 250 纯代码行`).toBeLessThanOrEqual(
        250,
      )
    }
  })
})
