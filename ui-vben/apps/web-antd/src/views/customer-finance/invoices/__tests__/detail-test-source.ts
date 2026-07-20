import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { basename, extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

export type DetailSource = {
  readonly filePath: string;
  readonly source: string;
};

const invoiceViewRoot = fileURLToPath(new URL('../', import.meta.url));
const detailEntryPath = join(invoiceViewRoot, 'detail.vue');
const supportingDirectories = [
  join(invoiceViewRoot, 'detail'),
  join(invoiceViewRoot, 'components'),
] as const;
const sourceExtensions = new Set(['.ts', '.vue']);

function collectSources(directory: string): readonly string[] {
  if (!existsSync(directory)) {
    return [];
  }

  const paths: string[] = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const entryPath = join(directory, entry.name);
    if (entry.isDirectory()) {
      paths.push(...collectSources(entryPath));
    } else if (sourceExtensions.has(extname(entry.name))) {
      paths.push(entryPath);
    }
  }
  return paths;
}

export function readDetailSources(): readonly DetailSource[] {
  const paths = [
    detailEntryPath,
    ...supportingDirectories.flatMap(collectSources),
  ];

  return paths.map((filePath) => ({
    filePath,
    source: readFileSync(filePath, 'utf8'),
  }));
}

export function readDetailCorpus(): string {
  return readDetailSources()
    .map(({ source }) => source)
    .join('\n');
}

export function readDetailEntry(): DetailSource {
  return {
    filePath: detailEntryPath,
    source: readFileSync(detailEntryPath, 'utf8'),
  };
}

export function readSupportingDetailSources(): readonly DetailSource[] {
  return readDetailSources().filter(
    ({ filePath }) => basename(filePath) !== 'detail.vue',
  );
}

export function countPureLines(source: string): number {
  return source.split(/\r?\n/u).filter((line) => {
    const trimmed = line.trim();
    return (
      trimmed.length > 0 &&
      !trimmed.startsWith('//') &&
      !trimmed.startsWith('<!--') &&
      !trimmed.startsWith('-->') &&
      !trimmed.startsWith('/*') &&
      !trimmed.startsWith('*') &&
      !trimmed.startsWith('*/')
    );
  }).length;
}
