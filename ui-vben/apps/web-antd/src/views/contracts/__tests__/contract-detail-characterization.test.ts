import { describe, expect, it } from 'vitest'

import { readContractDetailBundle } from './contract-detail-source-fixture'

describe('合同详情现有业务能力特征锁定', () => {
  it('在页面重构后仍保留详情加载、三态反馈与编辑保存能力', () => {
    // Given：合同详情父页及其可拆分子组件组成的源码集合。
    const source = readContractDetailBundle()

    // When：检索现有详情读取、状态反馈与保存契约。
    const hasDetailQuery = source.includes('getContractDetailApi')
    const hasStateFeedback =
      source.includes('StateBlock') &&
      source.includes(':loading') &&
      source.includes(':error') &&
      source.includes('@retry')
    const hasEditSave = source.includes('updateContractApi')

    // Then：重排布局不能删除用户已经依赖的核心能力。
    expect(hasDetailQuery).toBe(true)
    expect(hasStateFeedback).toBe(true)
    expect(hasEditSave).toBe(true)
  })

  it('在页面重构后仍保留履约、交付物与付款维护能力', () => {
    // Given：合同详情父页及其可拆分子组件组成的源码集合。
    const source = readContractDetailBundle()

    // When：检索合同类型内容、阶段、交付物和付款维护契约。
    const hasTypedFulfillment =
      source.includes('ResearchContent') && source.includes('ServiceContent')
    const hasFulfillmentData =
      source.includes('stages') && source.includes('deliverables')
    const hasPaymentMaintenance =
      source.includes('payments') &&
      source.includes('createPaymentApi') &&
      source.includes('deletePaymentApi')

    // Then：服务类与科研类履约链及付款维护均应继续可用。
    expect(hasTypedFulfillment).toBe(true)
    expect(hasFulfillmentData).toBe(true)
    expect(hasPaymentMaintenance).toBe(true)
  })

  it('在页面重构后仍保留发票、项目与合同文件关系操作', () => {
    // Given：合同详情父页及其可拆分子组件组成的源码集合。
    const source = readContractDetailBundle()

    // When：检索财务与关系对象的新增、跳转、上传和下载契约。
    const hasInvoiceFlow =
      source.includes('createInvoiceApi') &&
      source.includes('CustomerInvoiceDetail')
    const hasProjectRelation =
      source.includes('projects') && source.includes('ProjectDetail')
    const hasFileFlow =
      source.includes('files') &&
      source.includes('uploadContractFileApi') &&
      source.includes('contractFileDownloadUrl')

    // Then：详情页仍能作为合同关联对象的真实工作入口。
    expect(hasInvoiceFlow).toBe(true)
    expect(hasProjectRelation).toBe(true)
    expect(hasFileFlow).toBe(true)
  })
})
