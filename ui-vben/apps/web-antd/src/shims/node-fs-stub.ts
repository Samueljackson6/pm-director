export function existsSync(p: string): boolean { return false; }
export function readFileSync(): string { return ''; }
export function statSync() { return { isFile: () => false, isDirectory: () => false, size: 0, mtime: new Date() }; }
export function realpathSync(p: string): string { return p; }
export function mkdirSync() {}
export function writeFileSync() {}
export function readdirSync(): string[] { return []; }
export function readlinkSync(): string { return ''; }
export function lstatSync() { return { isFile: () => false, isDirectory: () => false, isSymbolicLink: () => false }; }
export const constants = { F_OK: 0, R_OK: 4, W_OK: 2, X_OK: 1 };
export function accessSync() {}
export function chmodSync() {}
export function unlinkSync() {}
export function rmdirSync() {}
export function renameSync() {}
export function copyFileSync() {}
export function appendFileSync() {}
