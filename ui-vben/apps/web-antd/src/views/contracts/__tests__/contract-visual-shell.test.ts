import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const source = readFileSync(fileURLToPath(new URL('../index.vue', import.meta.url)), 'utf8')

describe('G004 visual shell', () => {
  it('uses the shared workbench layout without page gradients', () => {
    expect(source).toContain('pm-workbench-page')
    expect(source).toContain('pm-page-header')
    expect(source).toContain('pm-table-surface')
    expect(source).not.toContain('bg-gradient-to-b')
  })
})
