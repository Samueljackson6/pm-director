import { basename } from 'node:path';

import { describe, expect, it } from 'vitest';

import {
  countPureLines,
  readDetailEntry,
  readSupportingDetailSources,
} from './detail-test-source';

const componentContracts = [
  {
    fileName: /overview/iu,
    label: '概览组件',
    responsibility: /invoice_no|calculatedTaxAmount|total_with_tax/u,
  },
  {
    fileName: /relation|receipt/iu,
    label: '关联回款组件',
    responsibility: /linkedReceipts|CustomerReceiptDetail|\/receipts/u,
  },
  {
    fileName: /file|attachment/iu,
    label: '文件组件',
    responsibility: /invoiceFiles|handleFileChange|\/files/u,
  },
  {
    fileName: /action|operation/iu,
    label: '操作组件',
    responsibility: /updateInvoiceApi|deleteInvoiceApi|CustomerInvoices/u,
  },
] as const;

describe('客户发票详情页结构边界', () => {
  it.each(componentContracts)(
    '应拆出独立的$label并由其承载对应职责',
    ({ fileName, responsibility }) => {
      // Given：详情页入口之外的组件源码。
      const supportingSources = readSupportingDetailSources();

      // When：按语义文件名查找职责组件。
      const component = supportingSources.find(
        ({ filePath }) => fileName.test(basename(filePath)),
      );

      // Then：组件必须真实存在且包含对应业务职责，不能只建空壳文件。
      expect(component, `缺少语义匹配 ${fileName.source} 的详情子组件`).toBeDefined();
      expect(component?.source).toMatch(responsibility);
    },
  );

  it('父页面应仅承担编排职责并控制在 250 纯代码行以内', () => {
    // Given：客户发票详情入口文件。
    const entry = readDetailEntry();

    // When：按仓库架构规则统计非空、非注释代码行。
    const pureLineCount = countPureLines(entry.source);

    // Then：父页面应保持可一次审阅的编排规模。
    expect(pureLineCount).toBeLessThanOrEqual(250);
  });
});
