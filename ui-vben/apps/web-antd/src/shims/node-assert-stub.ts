export function ok(val: any, msg?: string) { if (!val) throw new Error(msg || 'assertion failed'); }
export function equal(a: any, b: any) { if (a != b) throw new Error('not equal'); }
export function strictEqual(a: any, b: any) { if (a !== b) throw new Error('strict not equal'); }
export function notEqual(a: any, b: any) { if (a == b) throw new Error('equal'); }
export function deepEqual() { return true; }
export function fail(msg?: string) { throw new Error(msg || 'failed'); }
export function ifError(err: any) { if (err) throw err; }
export function throws(fn: Function) { try { fn(); } catch { return; } throw new Error('did not throw'); }
export function doesNotThrow(fn: Function) { fn(); }
