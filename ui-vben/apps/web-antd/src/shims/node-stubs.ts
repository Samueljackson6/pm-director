/**
 * Comprehensive browser-safe stubs for Node.js core modules.
 *
 * Vite 7.x auto-externalizes node:* modules for browser compatibility.
 * jiti (used by @vben/vite-config at build time) imports APIs from
 * multiple node:* modules. Those imports are tree-shaken at runtime
 * in the browser, but Vite's resolve phase still needs them to exist.
 *
 * Each stub exports the specific function/property that jiti references,
 * returning a safe default value. The stubs are never actually called
 * in the browser — they simply satisfy Vite's module resolution.
 */

// node:module
export const createRequire: ((url: string) => any) | undefined = undefined;

// node:os
export function platform(): string { return 'browser'; }
export function type(): string { return 'Browser'; }
export function release(): string { return '0.0.0'; }
export function hostname(): string { return 'localhost'; }
export function arch(): string { return 'x86_64'; }
export function tmpdir(): string { return '/tmp'; }
export function homedir(): string { return '/home'; }
export function endianness(): string { return 'LE'; }
export const EOL = '\n';
export const freemem = () => 0;
export const totalmem = () => 0;
export const cpus = () => [];
export const networkInterfaces = () => ({});

// node:url
export function pathToFileURL(p: string): URL { return new URL('file://' + p); }
export function fileURLToPath(u: string | URL): string { return String(u); }
export function format(value?: unknown, ..._args: any[]): string { return typeof value === 'string' ? value : ''; }
export const URL = globalThis.URL;

// node:path
export function resolve(...args: string[]): string { return args.join('/') || '.'; }
export function join(...args: string[]): string { return args.join('/'); }
export function dirname(p: string): string { return p.split('/').slice(0, -1).join('/') || '.'; }
export function basename(p: string): string { return p.split('/').pop() || ''; }
export function extname(p: string): string { const i = p.lastIndexOf('.'); return i >= 0 ? p.slice(i) : ''; }
export function relative(_from: string, to: string): string { return to; }
export function isAbsolute(p: string): boolean { return p.startsWith('/'); }
export function normalize(p: string): string { return p; }
export const sep = '/';
export const delimiter = ':';

// node:fs (minimal — only sync methods jiti might reference)
export function existsSync(_p: string): boolean { return false; }
export function readFileSync(): string { return ''; }
export function statSync() { return { isFile: () => false, isDirectory: () => false, size: 0 }; }
export function realpathSync(p: string): string { return p; }
export function mkdirSync() {}
export function writeFileSync() {}
export const constants = { F_OK: 0, R_OK: 4, W_OK: 2, X_OK: 1 };

// node:process
export const process = {
  env: { NODE_ENV: 'production' },
  cwd: () => '/',
  platform: 'browser',
  arch: 'x86_64',
  argv: [],
  stdout: { write: () => true },
  stderr: { write: () => true },
  exit: () => {},
  nextTick: (cb: Function) => Promise.resolve().then(() => cb()),
  version: '',
  versions: { node: '' },
};
export default process;

// node:assert
export function ok(val: any, msg?: string) { if (!val) throw new Error(msg || 'assertion failed'); }
export function equal(a: any, b: any) { if (a != b) throw new Error('not equal'); }
export function strictEqual(a: any, b: any) { if (a !== b) throw new Error('strict not equal'); }
export function deepEqual() { return true; }
export function fail(msg?: string) { throw new Error(msg || 'failed'); }

// node:util
export function inherits() {}
export function promisify(fn: Function) { return fn; }
export function deprecate(fn: Function) { return fn; }
export function types() { return {}; }
export const inspect = (x: any) => String(x);

// node:crypto
export function createHash() { return { update: () => ({}), digest: () => '' }; }
export function randomBytes(size: number) { return new Uint8Array(size); }
export function createCipheriv() { return { update: () => '', final: () => '' }; }
export function createDecipheriv() { return { update: () => '', final: () => '' }; }
export const webcrypto = globalThis.crypto;

// node:vm
export function compileFunction(code: string) { return new Function(code); }
export function runInThisContext(code: string) { return eval(code); }
export const Script = class Script { constructor() {} runInThisContext() {} };

// node:v8
export function getHeapStatistics() { return {}; }
export function getHeapSpaceStatistics() { return []; }

// node:tty
export function isatty() { return false; }

// node:perf_hooks
export function performanceNow() { return performance.now(); }
export const performance = globalThis.performance;
