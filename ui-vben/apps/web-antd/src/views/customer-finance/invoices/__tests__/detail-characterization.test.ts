import { describe, expect, it } from 'vitest';

import { readDetailCorpus } from './detail-test-source';

describe('客户发票详情页既有行为契约', () => {
  it('应在进入页面或发票编号变化时加载详情及关联数据', () => {
    // Given：详情页及未来拆出的子组件源码。
    // When：检查页面加载入口与详情请求契约。
    const corpus = readDetailCorpus();

    // Then：详情、文件和关联回款仍由页面加载流程触发。
    expect(corpus).toMatch(/getInvoiceDetailApi\s*\(\s*Number\(\s*id\s*\)\s*\)/u);
    expect(corpus).toMatch(/onMounted\s*\(\s*load\s*\)/u);
    expect(corpus).toMatch(/loadInvoiceFiles\s*\(\s*\)/u);
    expect(corpus).toMatch(/loadLinkedReceipts\s*\(\s*\)/u);
    expect(corpus).toMatch(/route\.(?:params|query)\.id/u);
  });

  it('应使用 StateBlock 呈现加载失败并提供重试', () => {
    // Given：详情页三态容器契约。
    // When：检查 StateBlock 的输入和重试事件。
    const corpus = readDetailCorpus();

    // Then：加载态、错误态和重试动作均保留。
    expect(corpus).toMatch(/<(?:state-block|StateBlock)\b/iu);
    expect(corpus).toMatch(/:loading="loading"/u);
    expect(corpus).toMatch(/:error="error"/u);
    expect(corpus).toMatch(/@retry="load"/u);
  });

  it('应展示关联回款并支持进入详情和取消关联', () => {
    // Given：发票与回款的关联区域。
    // When：检查关联查询、详情导航和解除关系动作。
    const corpus = readDetailCorpus();

    // Then：用户仍可查看并管理发票关联回款。
    expect(corpus).toMatch(/\/api\/invoices\/\$\{[^}]+\}\/receipts/u);
    expect(corpus).toContain("name: 'CustomerReceiptDetail'");
    expect(corpus).toMatch(/unlinkReceipt\s*\(/u);
    expect(corpus).toMatch(/requestClient\.delete\([\s\S]*\/receipts\/\$\{/u);
  });

  it('应保留发票文件的查询、上传、下载和删除能力', () => {
    // Given：发票附件区域。
    // When：检查文件端点和四类用户动作。
    const corpus = readDetailCorpus();

    // Then：文件管理能力不因视觉拆分而丢失。
    expect(corpus).toMatch(/\/api\/invoices\/\$\{[^}]+\}\/files/u);
    expect(corpus).toMatch(/type="file"/u);
    expect(corpus).toMatch(/handleFileChange\s*\(/u);
    expect(corpus).toMatch(/downloadFile\s*\(/u);
    expect(corpus).toMatch(/deleteFile\s*\(/u);
  });

  it('应保留编辑、删除和返回客户发票列表的行为', () => {
    // Given：详情页主操作区。
    // When：检查保存、删除和离开详情页的目标。
    const corpus = readDetailCorpus();

    // Then：写操作仍调用既有 API，返回目标仍是客户发票列表。
    expect(corpus).toMatch(/updateInvoiceApi\s*\(/u);
    expect(corpus).toMatch(/deleteInvoiceApi\s*\(/u);
    expect(corpus).toMatch(/editModalVisible\.value\s*=\s*true/u);
    expect(corpus).toContain("router.push({ name: 'CustomerInvoices' })");
  });
});
