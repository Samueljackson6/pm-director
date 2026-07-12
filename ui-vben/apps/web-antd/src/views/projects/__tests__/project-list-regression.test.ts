import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const sourcePath = fileURLToPath(new URL('../index.vue', import.meta.url))
const source = readFileSync(sourcePath, 'utf8')

describe('项目列表 VxeGrid 回归契约', () => {
  it('应通过 gridEvents 注册双击事件，并使用 gridApi.query 刷新', () => {
    // 约束 Vben VxeGrid 的事件和查询 API，避免回退到不存在的旧接口。
    expect(source).toMatch(
      /useVbenVxeGrid\(\{[\s\S]*gridEvents:\s*\{[\s\S]*cellDblclick\s*\(/,
    )
    expect(source).not.toContain('gridApi.on(')
    expect(source).not.toContain('commitProxyQuery')
    expect(source.match(/gridApi\.query\(\)/g)).toHaveLength(2)
  })
})
