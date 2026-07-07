export function pathToFileURL(p: string): URL { try { return new URL('file://' + (p || '/')); } catch { return new URL('file:///'); } }
export function fileURLToPath(u: string | URL): string { return String(u); }
export function urlFormat(): string { return ''; }
export function URLParse(): any { return {}; }
export function resolve(): string { return ''; }
