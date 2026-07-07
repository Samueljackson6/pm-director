/**
 * Browser-safe stub for node:os
 *
 * Vite 7.x auto-externalizes node:* modules for browser compatibility.
 * jiti internally imports from node:os, requiring at minimum a platform()
 * function to avoid runtime errors.
 */
export function platform(): string {
  return 'browser';
}
export function type(): string {
  return 'Browser';
}
export function release(): string {
  return '0.0.0';
}
export function hostname(): string {
  return 'localhost';
}
export function arch(): string {
  return 'x86_64';
}
export function tmpdir(): string {
  return '/tmp';
}
export function homedir(): string {
  return '/home';
}
export function endianness(): string {
  return 'LE';
}
export const EOL = '\n';
export default {
  platform,
  type,
  release,
  hostname,
  arch,
  tmpdir,
  homedir,
  endianness,
  EOL,
};
