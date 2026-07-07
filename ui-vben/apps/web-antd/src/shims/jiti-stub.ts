/**
 * Browser-safe stub for the `jiti` package.
 *
 * jiti is a Node.js runtime TypeScript/ESM loader that should never
 * execute in the browser. This stub provides inert implementations
 * so imports resolve without crashing at runtime.
 */

// createJiti returns a jiti instance with paths and other expected properties
export function createJiti(_filename: string, _opts?: any) {
  return {
    import: async () => ({}),
    resolve: () => '',
    transform: () => '',
    paths: [],
    filename: _filename,
    opts: _opts || {},
  };
}

// Default export is the createJiti function
export default createJiti;

// createRequire is used by jiti internally
export function createRequire(_url: string) {
  const requireFn = (id: string) => {
    if (id === 'jiti') return { createJiti, createRequire };
    return {};
  };
  requireFn.resolve = () => '';
  requireFn.cache = {};
  requireFn.main = undefined;
  return requireFn;
}
