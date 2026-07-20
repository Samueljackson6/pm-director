import { describe, expect, it } from 'vitest';

import { readDetailCorpus } from './detail-test-source';

describe('客户发票详情页领域真值契约', () => {
  it('金额或税额缺失时应明确标记待核验，已知零值仍显示为 0.00', () => {
    // Given：金额和税额都可能缺失，而零是已经确认的业务值。
    const corpus = readDetailCorpus();

    // When：详情页格式化金额并呈现金额相关区域。
    // Then：缺失值不能伪装成 0.00，且零值要被保留为金额值。
    expect(corpus).toMatch(/function fmtMoney[\s\S]*value == null[\s\S]*(?:待核验|数据缺失)/u);
    expect(corpus).toMatch(/value === 0[\s\S]*0\.00/u);
    expect(corpus).toMatch(/(?:tax_amount|calculatedTaxAmount)[\s\S]*(?:待核验|数据缺失)/u);
  });

  it('payment_status 缺失时应显示待核验或未提供，不能冒充未匹配', () => {
    // Given：接口没有提供匹配状态。
    const corpus = readDetailCorpus();

    // When：详情页显示匹配状态标签。
    // Then：用户能够分辨未知状态和确认为未匹配的状态。
    expect(corpus).toMatch(
      /payment_status\s*\|\|\s*['"](?:待核验|未提供)['"]/u,
    );
    expect(corpus).not.toMatch(/payment_status\s*\|\|\s*['"]未匹配['"]/u);
  });

  it('关联金额的已知零值不会被其他金额覆盖，缺失值也不伪装为零', () => {
    const corpus = readDetailCorpus();

    expect(corpus).not.toMatch(/link_amount\s*\|\|\s*(?:receipt\.)?amount/u);
    expect(corpus).toMatch(/link_amount\s*\?\?\s*(?:receipt\.)?amount/u);
    expect(corpus).not.toMatch(/link_amount\s*\?\?\s*(?:receipt\.)?amount\s*\?\?\s*0/u);
  });

  it.each([
    'inbound',
    '客户回款',
    '供应商开票',
  ])('遇到 %s 记录时应显示领域冲突，而非作为客户发票正常呈现', (invalidDomain) => {
    // Given：客户发票详情只接受 outbound 且发票类型为客户开票的记录。
    const corpus = readDetailCorpus();

    // When：接口返回了其他财务领域的记录。
    // Then：页面必须标识领域冲突，避免把错误记录包装成客户发票。
    expect(corpus).toMatch(/领域冲突/u);
    expect(corpus).toMatch(
      new RegExp(`(?:direction|invoice_type)[\\s\\S]*${invalidDomain}`, 'u'),
    );
  });

  it('来源和更新时间缺失时应显示明确数据状态', () => {
    // Given：来源、更新时间和导入时间均可能为空。
    const corpus = readDetailCorpus();

    // When：详情页呈现系统信息。
    // Then：不能用无语义的横线掩盖数据缺失。
    expect(corpus).toMatch(/invoice\.source\s*\|\|\s*['"](?:待核验|未提供|数据缺失)['"]/u);
    expect(corpus).toMatch(
      /(?:updated_at\s*\|\|\s*invoice\.import_time)[\s\S]*(?:待核验|未提供|数据缺失)/u,
    );
  });

  it('页面加载只读取详情和关联数据，不自动触发匹配或写操作', () => {
    // Given：页面首次挂载和路由标识变化都会触发 load。
    const corpus = readDetailCorpus();

    // When：检查由生命周期自动执行的加载函数。
    // Then：自动流程只读，不调用自动匹配或 POST、PATCH、DELETE。
    expect(corpus).toMatch(/onMounted\s*\(\s*load\s*\)/u);
    expect(corpus).not.toMatch(/(?:auto-match|autoMatch|自动匹配)/iu);
    const loadFunction = corpus.match(
      /async function load\s*\(\s*\)\s*:\s*Promise<void>\s*\{[\s\S]*?\n  \}\n\n  async function handleFileChange/u,
    );
    const loadSource = loadFunction?.[0] ?? '';

    expect(loadSource).toMatch(/getInvoiceDetailApi/u);
    expect(loadSource).not.toMatch(/requestClient\.(?:post|patch|delete)\s*\(/iu);
  });
});
