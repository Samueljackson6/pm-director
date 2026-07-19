import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

const receiptListSource = readFileSync(
  fileURLToPath(new URL('../index.vue', import.meta.url)),
  'utf8',
);

describe('客户回款列表返回上下文源码契约', () => {
  it('从合法 query 恢复分页，并将非法分页回退到默认值', () => {
    expect(receiptListSource).toMatch(
      /function\s+readPositivePageQuery\s*\([\s\S]*?Number\.isSafeInteger[\s\S]*?>\s*0[\s\S]*?fallback/s,
    );
    expect(receiptListSource).toMatch(
      /const\s+currentPage\s*=\s*ref\(\s*readPositivePageQuery\(\s*route\.query\.page\s*,\s*1\s*\)\s*\)/,
    );
    expect(receiptListSource).toMatch(
      /const\s+pageSize\s*=\s*ref\(\s*readPositivePageQuery\(\s*route\.query\.pageSize\s*,\s*20\s*\)\s*\)/,
    );
  });

  it('将分页受控绑定到表格，避免 UI 仍回到默认第一页', () => {
    expect(receiptListSource).toMatch(
      /:pagination="\{[\s\S]*?current:\s*currentPage[\s\S]*?pageSize:\s*pageSize[\s\S]*?\}"/,
    );
  });

  it('翻页和改页容量时同步 query，使刷新与详情返回均可恢复', () => {
    const changeHandler = receiptListSource.match(
      /function\s+handleTableChange\s*\([\s\S]*?\n\}/,
    )?.[0];

    expect(changeHandler, '应保留分页事件处理函数').toBeDefined();
    expect(changeHandler).toMatch(/currentPage\.value\s*=\s*pagination\.current/);
    expect(changeHandler).toMatch(/pageSize\.value\s*=\s*pagination\.pageSize/);
    expect(changeHandler).toMatch(
      /router\.replace\(\s*\{[\s\S]*?query:\s*\{[\s\S]*?\.\.\.route\.query[\s\S]*?page:\s*String\(currentPage\.value\)[\s\S]*?pageSize:\s*String\(pageSize\.value\)/,
    );
  });

  it('该契约只读取组件源码，不调用业务 API 或写入数据', () => {
    expect(receiptListSource).toContain('getReceiptsApi');
  });
});
