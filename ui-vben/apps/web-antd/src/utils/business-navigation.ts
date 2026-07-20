type QueryValue = null | string | readonly (null | string)[] | undefined;

type QueryRecord = Readonly<Record<string, QueryValue>>;

interface NamedLocation {
  name: string;
  query: Record<string, string>;
}

interface DetailLocationOptions {
  from: {
    name?: unknown;
    query: QueryRecord;
  };
  id: string;
  name: string;
}

interface ListReturnLocationOptions {
  currentDetailName: string;
  detailQuery: QueryRecord;
  fallbackName: string;
}

type DetailIdResult =
  | { id: string; status: 'ready' }
  | {
      reason: 'missing' | 'multiple' | 'unsupported';
      status: 'invalid';
    };

function firstQueryValue(value: QueryValue): null | string {
  if (typeof value === 'string') {
    return value;
  }
  return null;
}

export function buildDetailLocation(
  options: DetailLocationOptions,
): NamedLocation {
  const query: Record<string, string> = { id: options.id.trim() };
  const sourceName =
    typeof options.from.name === 'string' ? options.from.name.trim() : '';

  if (sourceName) {
    query.from = sourceName;
  }

  for (const [key, value] of Object.entries(options.from.query)) {
    const normalized = firstQueryValue(value);
    if (normalized !== null) {
      query[`return_${key}`] = normalized;
    }
  }

  return { name: options.name, query };
}

export function buildListReturnLocation(
  options: ListReturnLocationOptions,
): NamedLocation {
  const sourceName = firstQueryValue(options.detailQuery.from)?.trim();
  const name =
    sourceName && sourceName !== options.currentDetailName
      ? sourceName
      : options.fallbackName;
  const query: Record<string, string> = {};

  for (const [key, value] of Object.entries(options.detailQuery)) {
    if (!key.startsWith('return_')) {
      continue;
    }

    const normalized = firstQueryValue(value);
    if (normalized !== null) {
      query[key.slice('return_'.length)] = normalized;
    }
  }

  return { name, query };
}

export function parseDetailId(
  query: Readonly<Record<string, unknown>>,
): DetailIdResult {
  const { id } = query;

  if (Array.isArray(id)) {
    return { reason: 'multiple', status: 'invalid' };
  }
  if (typeof id !== 'string') {
    return {
      reason: id === null || id === undefined ? 'missing' : 'unsupported',
      status: 'invalid',
    };
  }

  const normalized = id.trim();
  if (!normalized) {
    return { reason: 'missing', status: 'invalid' };
  }

  return { id: normalized, status: 'ready' };
}
