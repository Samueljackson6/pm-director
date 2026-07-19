import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { dirname, extname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const CONTRACTS_DIRECTORY = dirname(
  fileURLToPath(new URL('../detail.vue', import.meta.url)),
)

const DETAIL_ROOT_PATH = join(CONTRACTS_DIRECTORY, 'detail.vue')
const SUPPORT_DIRECTORIES = [
  join(CONTRACTS_DIRECTORY, 'components'),
  join(CONTRACTS_DIRECTORY, 'detail'),
  join(CONTRACTS_DIRECTORY, 'detail-sections'),
] as const

function collectSourcePaths(directory: string): readonly string[] {
  if (!existsSync(directory)) {
    return []
  }

  const paths: string[] = []
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) {
      paths.push(...collectSourcePaths(path))
      continue
    }

    if (['.ts', '.vue'].includes(extname(entry.name))) {
      paths.push(path)
    }
  }
  return paths
}

export function readContractDetailBundle(): string {
  const paths = [
    DETAIL_ROOT_PATH,
    ...SUPPORT_DIRECTORIES.flatMap(collectSourcePaths),
  ]
  return paths.map((path) => readFileSync(path, 'utf8')).join('\n')
}

export function readContractDetailRoot(): string {
  return readFileSync(DETAIL_ROOT_PATH, 'utf8')
}

export function contractDetailComponentPath(fileName: string): string {
  return join(CONTRACTS_DIRECTORY, 'components', 'detail', fileName)
}

export function countPureLines(source: string): number {
  return source
    .split(/\r?\n/u)
    .filter((line) => {
      const trimmed = line.trim()
      return trimmed.length > 0 && !trimmed.startsWith('//')
    }).length
}
