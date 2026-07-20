import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

const DETAIL_DIRECTORY = dirname(dirname(fileURLToPath(import.meta.url)));
const COMPONENT_DIRECTORY = join(DETAIL_DIRECTORY, 'components');
const PAGE_PATH = join(DETAIL_DIRECTORY, 'index.vue');

const EXPECTED_COMPONENTS = [
  'SupplierOverview.vue',
  'SupplierCollaborationFinance.vue',
  'SupplierBusinessProfileRisk.vue',
] as const;

describe('供应商详情页结构边界', () => {
  it.each(EXPECTED_COMPONENTS)('拆出职责组件 %s', (componentName) => {
    expect(existsSync(join(COMPONENT_DIRECTORY, componentName))).toBe(true);
  });

  it('父页只承担编排职责并控制在 250 行以内', () => {
    const pageSource = readFileSync(PAGE_PATH, 'utf8');
    const pageLines = pageSource.split(/\r?\n/).length;

    for (const componentName of EXPECTED_COMPONENTS) {
      expect(pageSource).toContain(componentName.replace('.vue', ''));
    }
    expect(pageLines).toBeLessThanOrEqual(250);
  });
});
