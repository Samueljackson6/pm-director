import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

const DETAIL_DIRECTORY = dirname(dirname(fileURLToPath(import.meta.url)));

function collectProductionSource(directory: string): string {
  return readdirSync(directory)
    .filter((entry) => entry !== '__tests__')
    .map((entry) => join(directory, entry))
    .flatMap((entryPath) => statSync(entryPath).isDirectory()
      ? collectProductionSource(entryPath)
      : ['.ts', '.vue'].includes(extname(entryPath)) ? readFileSync(entryPath, 'utf8') : '')
    .join('\n');
}

describe('供应商详情页真实领域契约', () => {
  const source = collectProductionSource(DETAIL_DIRECTORY);

  it('以供应商标识加载聚合详情，并保留三态反馈与重试入口', () => {
    expect(source).toContain('getSupplierDetailApi');
    expect(source).toContain('route.query.id');
    expect(source).toContain('onMounted(loadData)');
    expect(source).toContain('StateBlock');
    expect(source).toMatch(/:loading=["']loading["']/);
    expect(source).toMatch(/:error=["']error["']/);
    expect(source).toMatch(/@retry=["']loadData["']/);
  });

  it('映射供应商主档与本地工商归档，并在缺档时回退主档', () => {
    for (const field of ['data.supplier', 'data.qcc_data', 'buildBasicInfo', 'normalizeProfile']) {
      expect(source).toContain(field);
    }
    expect(source).toContain('企业名称');
    expect(source).toContain('统一社会信用代码');
    expect(source).toContain('法定代表人');
    expect(source).toContain('经营范围');
  });

  it('映射本地风险、知识产权、投资和供应链事实分区', () => {
    for (const field of ['normalizeRiskScan', 'normalizeSoftware', 'normalizeInvestments', 'data.supplier_invoices', 'data.data_states']) {
      expect(source).toContain(field);
    }
    expect(source).toContain('风险因子扫描');
    expect(source).toContain('软件著作权信息');
    expect(source).toContain('对外投资信息');
  });

  it('保留返回供应商列表的导航契约', () => {
    expect(source).toContain("name: 'SupplierList'");
    expect(source).toMatch(/(?:router\.push|router\.replace)\(\{\s*name:\s*'SupplierList'/);
  });

  it('确认测试扫描入口存在，避免空目录产生伪通过', () => {
    expect(existsSync(join(DETAIL_DIRECTORY, 'index.vue'))).toBe(true);
    expect(source.length).toBeGreaterThan(1_000);
  });
});
