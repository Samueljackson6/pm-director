import { describe, expect, it } from 'vitest';

import legacyRoutes from '../modules/legacy-redirects';
import supplierLegacyRoutes from '../modules/suppliers';

function resolveRedirectTarget(
  redirect: (typeof legacyRoutes)[number]['redirect'],
): unknown {
  if (typeof redirect !== 'function') {
    return redirect;
  }

  return Reflect.apply(redirect, undefined, [{ query: { id: 'PRJ-001' } }]);
}

describe('业务详情路由安全契约', () => {
  it('/suppliers/detail 不得注册指回自身的 Legacy 重定向', () => {
    const detailRoute = supplierLegacyRoutes.find(
      (route) => route.path === '/suppliers/detail',
    );

    expect(detailRoute).toBeUndefined();
  });

  it('/projects/detail 不得误投合同详情，也不得指回自身形成循环', () => {
    const detailRoute = legacyRoutes.find(
      (route) => route.path === '/projects/detail',
    );

    if (!detailRoute) {
      return;
    }

    const target = resolveRedirectTarget(detailRoute.redirect);

    expect(target).not.toEqual('/contracts/detail');
    expect(target).not.toMatchObject({ path: '/contracts/detail' });
    expect(target).not.toEqual('/projects/detail');
    expect(target).not.toMatchObject({ path: '/projects/detail' });
  });
});
