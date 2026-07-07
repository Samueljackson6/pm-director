export function createHash() { return { update: () => ({}), digest: () => '' }; }
export function randomBytes(size: number) { return Buffer.alloc(size); }
export function randomUUID() { return crypto.randomUUID(); }
export function createCipheriv() { return { update: () => '', final: () => '' }; }
export function createDecipheriv() { return { update: () => '', final: () => '' }; }
export function createSign() { return { update: () => ({}), sign: () => '' }; }
export function createVerify() { return { update: () => ({}), verify: () => true }; }
export function createHmac() { return { update: () => ({}), digest: () => '' }; }
export function generateKeyPairSync() { return { publicKey: '', privateKey: '' }; }
export const webcrypto = crypto;
