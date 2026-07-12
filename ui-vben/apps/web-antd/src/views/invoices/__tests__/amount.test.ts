import { describe, expect, it } from 'vitest'

import { yuanToWan } from '../amount'

describe('yuanToWan', () => {
  it('将持久化的元转换为万元', () => {
    expect(yuanToWan(31076.5)).toBe(3.10765)
  })
})
