import { describe, expect, it } from 'vitest';

import { getRawRoute } from '../routerHelper';

// `getRawRoute` is a pure function: it clones a route and reduces its
// `matched` array to only the serialisable bits (meta/name/path), dropping
// heavy runtime fields such as component definitions. No Vue/DOM needed.
describe('getRawRoute', () => {
  it('returns the input untouched when the route is falsy', () => {
    expect(getRawRoute(null as unknown as never)).toBeNull();
    // @ts-expect-error intentionally passing undefined
    expect(getRawRoute(undefined)).toBeUndefined();
  });

  it('keeps top-level fields and reduces matched to meta/name/path', () => {
    const route = {
      path: '/dashboard/analytics',
      name: 'analytics',
      fullPath: '/dashboard/analytics?tab=1',
      query: { tab: '1' },
      matched: [
        {
          meta: { title: 'Dashboard' },
          name: 'dashboard',
          path: '/dashboard',
          // heavy runtime-only fields that must be stripped
          components: { default: { render: () => null } },
          instances: { default: {} },
        },
        {
          meta: { title: 'Analytics' },
          name: 'analytics',
          path: '/dashboard/analytics',
          components: { default: { render: () => null } },
          instances: { default: {} },
        },
      ],
    } as unknown as Parameters<typeof getRawRoute>[0];

    const raw = getRawRoute(route);

    // top-level scalar fields survive
    expect(raw.path).toBe('/dashboard/analytics');
    expect(raw.name).toBe('analytics');
    expect(raw.fullPath).toBe('/dashboard/analytics?tab=1');
    expect(raw.query).toEqual({ tab: '1' });

    // matched is reduced and stripped
    expect(raw.matched).toHaveLength(2);
    expect(raw.matched?.[0]).toEqual({
      meta: { title: 'Dashboard' },
      name: 'dashboard',
      path: '/dashboard',
    });
    expect(raw.matched?.[1]).toEqual({
      meta: { title: 'Analytics' },
      name: 'analytics',
      path: '/dashboard/analytics',
    });
    // heavy fields must NOT be present
    expect((raw.matched?.[0] as Record<string, unknown>).components).toBeUndefined();
    expect((raw.matched?.[0] as Record<string, unknown>).instances).toBeUndefined();
  });

  it('preserves an undefined matched array', () => {
    const route = { path: '/x', matched: undefined } as unknown as Parameters<
      typeof getRawRoute
    >[0];
    const raw = getRawRoute(route);
    expect(raw.path).toBe('/x');
    expect(raw.matched).toBeUndefined();
  });
});
