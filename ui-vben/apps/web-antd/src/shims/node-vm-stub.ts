export function compileFunction(code: string, params?: string[]) { return new Function(...(params||[]), code); }
export function runInThisContext(code: string) { return eval(code); }
export function runInNewContext(code: string) { return eval(code); }
export function createContext() { return {}; }
export function isContext() { return false; }
export const Script = class { constructor() {} runInThisContext() {} runInNewContext() {} };
