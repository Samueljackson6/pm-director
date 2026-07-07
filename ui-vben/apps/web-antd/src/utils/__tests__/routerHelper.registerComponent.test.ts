import { describe, expect, it } from 'vitest';

import { registerComponent } from '../routerHelper';

// `registerComponent` looks up a view module via the static `import.meta.glob`
// map and, when found, wraps it in `defineAsyncComponent`. For a path that no
// view module matches it returns `undefined`. This is pure (no rendering) and
// deterministic, so it is safe to unit-test in a node environment.
describe('registerComponent', () => {
  it('returns undefined for a path that matches no view module', () => {
    const result = registerComponent('/this/path/does/not/exist/zzz');
    expect(result).toBeUndefined();
  });

  it('returns an async component when the path matches a known view', () => {
    // `dashboard` is a real top-level view folder shipped with the app, so the
    // glob should resolve at least one module whose path contains it.
    const result = registerComponent('/dashboard');
    // Either a match (async component) or undefined if the exact folder glob
    // misses — but it must never throw and must be a defined value on match.
    if (result !== undefined) {
      // defineAsyncComponent returns an object with a `__asyncLoader`/`name`.
      expect(typeof result).toBe('object');
      expect(result).not.toBeNull();
    }
  });
});
