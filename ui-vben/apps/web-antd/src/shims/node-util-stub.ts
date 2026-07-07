export function inherits() {}
export function promisify(fn: Function) { const f = (...args: any[]) => Promise.resolve(fn(...args)); return f; }
export function utilFormat(f: string, ...args: any[]): string { return f; }
export function deprecate(fn: Function) { return fn; }
export function types() { return {}; }
export function inspect(x: any): string { return String(x); }
export function callbackify(fn: Function) { return fn; }
export function getSystemErrorName() { return ''; }
export function getSystemErrorMap() { return new Map(); }
export const TextDecoder = globalThis.TextDecoder;
export const TextEncoder = globalThis.TextEncoder;
