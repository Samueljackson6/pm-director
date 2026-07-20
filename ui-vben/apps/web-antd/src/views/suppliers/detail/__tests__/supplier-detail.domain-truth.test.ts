import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

const DETAIL_DIRECTORY = dirname(dirname(fileURLToPath(import.meta.url)));
const PAGE_PATH = join(DETAIL_DIRECTORY, 'index.vue');

function readDetailPageSourceOnly(): string {
  return readFileSync(PAGE_PATH, 'utf8');
}

describe('供应商详情领域真值契约', () => {
  it('以路由 supplier_id 调用领域详情接口，而非直接查询企查查', () => {
    const source = readDetailPageSourceOnly();

    expect(source).toMatch(/route\.query\.id/);
    expect(source).toMatch(/getSupplierDetailApi\(supplierId\)/);
    expect(source).not.toContain('getSupplierQccInfoApi');
  });

  it('消费供应商领域聚合的全部数据分区', () => {
    const source = readDetailPageSourceOnly();

    for (const field of [
      'supplier',
      'contracts',
      'supplier_invoices',
      'payments',
      'contacts',
      'qcc_data',
      'data_states',
    ]) {
      expect(source).toContain(`data.${field}`);
    }
  });

  it('将未建立或待核验的数据诚实呈现，而非虚构零风险或高评分', () => {
    const source = readDetailPageSourceOnly();

    expect(source).toMatch(/待核验|数据源未建立|已建立但无记录/);
    expect(source).not.toMatch(/recordedFactors\s*\|\|\s*0/);
    expect(source).not.toMatch(/recordedFactors\s*===\s*0\)\s*return\s*['"]优秀/);
    expect(source).not.toMatch(/if\s*\(!info\)\s*return\s*\{[^}]*overall:\s*3/);
  });

  it('详情加载不触发企查查刷新、自动匹配或任何写操作', () => {
    const source = readDetailPageSourceOnly();

    expect(source).not.toMatch(/qcc[^\n]*(?:refresh|刷新)/i);
    expect(source).not.toMatch(/(?:auto-match|自动匹配)/i);
    expect(source).not.toMatch(/\.\s*(?:post|patch|delete)\s*\(/i);
  });
});
