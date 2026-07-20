import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { loadScript } from '../resources';

const testJsPath = 'https://example.test/test.js';

// 通过拦截 append 防止 happy-dom 真实加载外部脚本，仅验证 loadScript 的事件与去重约定。
describe('loadScript', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should resolve when the script loads successfully', async () => {
    const append = vi
      .spyOn(document.head, 'append')
      .mockImplementation(() => {});
    const promise = loadScript(testJsPath);
    const script = append.mock.calls[0]?.[0] as HTMLScriptElement;

    expect(script).toBeTruthy();
    script.dispatchEvent(new Event('load'));

    await expect(promise).resolves.toBeUndefined();
  });

  it('should not insert duplicate script and resolve immediately if already loaded', async () => {
    const existing = document.createElement('script');
    existing.src = testJsPath;
    const append = vi
      .spyOn(document.head, 'append')
      .mockImplementation(() => {});
    vi.spyOn(document, 'querySelector').mockReturnValue(existing);

    await expect(loadScript(testJsPath)).resolves.toBeUndefined();
    expect(append).not.toHaveBeenCalled();
  });

  it('should reject when the script fails to load', async () => {
    const append = vi
      .spyOn(document.head, 'append')
      .mockImplementation(() => {});
    const promise = loadScript(testJsPath);
    const script = append.mock.calls[0]?.[0] as HTMLScriptElement;

    expect(script).toBeTruthy();
    script.dispatchEvent(new Event('error'));

    await expect(promise).rejects.toThrow(
      `Failed to load script: ${testJsPath}`,
    );
  });

  it('should handle multiple concurrent calls and only insert one script tag', async () => {
    const append = vi
      .spyOn(document.head, 'append')
      .mockImplementation(() => {});
    let firstScript: HTMLScriptElement | null = null;
    vi.spyOn(document, 'querySelector').mockImplementation(() => {
      if (firstScript) {
        return firstScript;
      }
      return null;
    });

    const p1 = loadScript(testJsPath);
    firstScript = append.mock.calls[0]?.[0] as HTMLScriptElement;
    const p2 = loadScript(testJsPath);

    expect(append).toHaveBeenCalledTimes(1);
    firstScript.dispatchEvent(new Event('load'));

    await expect(p1).resolves.toBeUndefined();
    await expect(p2).resolves.toBeUndefined();
  });
});
