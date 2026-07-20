export function resolve(...args: string[]): string { return args.join('/') || '.'; }
export function join(...args: string[]): string { return args.join('/'); }
export function dirname(p: string): string { const s = p.replace(/\\/g,'/').split('/'); s.pop(); return s.join('/')||'.'; }
export function basename(p: string): string { return p.replace(/\\/g,'/').split('/').pop()||''; }
export function extname(p: string): string { const i = p.lastIndexOf('.'); return i >= 0 ? p.slice(i) : ''; }
export function relative(_from: string, to: string): string { return to; }
export function isAbsolute(p: string): boolean { return /^[/\\]/.test(p); }
export function normalize(p: string): string { return p; }
export function parse(_p: string) { return {root:'/',dir:'',base:'',ext:'',name:''}; }
export const sep = '/';
export const delimiter = ':';
