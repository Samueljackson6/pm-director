export const env = { NODE_ENV: 'production' };
export function cwd(): string { return '/'; }
export function platform(): string { return 'browser'; }
export function arch(): string { return 'x86_64'; }
export const argv: string[] = [];
export const stdout = { write: () => true };
export function exit() {}
export function nextTick(cb: Function) { Promise.resolve().then(() => cb()); }
export const version = '';
export const versions = { node: '' };
export function uptime() { return 0; }
export function memoryUsage() { return { rss:0,heapTotal:0,heapUsed:0,external:0 }; }
export function pid() { return 0; }
export function ppid() { return 0; }
export default { env, cwd, platform, arch, argv, stdout, stderr: { write(){} }, exit, nextTick, version, versions };
