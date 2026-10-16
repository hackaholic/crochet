/** Only the public SEO API determines build routes. No catalog content belongs here. */
export function validatePublicPath(value) {
  if (typeof value !== 'string' || !/^\/(?:[a-z0-9-]+\/)*[a-z0-9-]*$/.test(value)
    || /\/(?:admin|account|cart|checkout|wishlist|auth|track)(?:\/|$)/.test(value)) {
    throw new Error('Invalid public snapshot path');
  }
  return value;
}
export function apiBase(value) {
  const url = new URL(value);
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
    throw new Error('SEO_API_BASE_URL must be a credential-free HTTP(S) API URL');
  }
  return url.href.replace(/\/$/, '');
}
export async function getJson(base, resource, fetcher = fetch) {
  const response = await fetcher(`${base}${resource}`, { signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`Public build API failed (${response.status})`);
  return response.json();
}
export async function getPublicRoutes(base, fetcher = fetch) {
  const items = [];
  let expected;
  let version;
  for (let page = 1; page <= 1000; page++) {
    const data = await getJson(base, `/seo/snapshot?page=${page}&limit=200`, fetcher);
    if (!Array.isArray(data.items) || !Number.isInteger(data.totalCount) || data.totalCount < 1
      || data.totalCount > 200000 || !Number.isInteger(data.totalPages) || data.totalPages < page
      || (expected !== undefined && expected !== data.totalCount)) throw new Error('Invalid or changing public snapshot');
    if (typeof data.versionHash !== 'string' || !/^[a-f0-9]{16,64}$/.test(data.versionHash)
      || (version !== undefined && version !== data.versionHash)) throw new Error('Public snapshot version changed between pages');
    version = data.versionHash;
    expected = data.totalCount;
    for (const item of data.items) {
      validatePublicPath(item.path);
      if (!['index,follow', 'noindex,nofollow'].includes(item.metadata?.robots) || typeof item.metadata.title !== 'string'
        || typeof item.metadata.description !== 'string') throw new Error('Invalid public metadata');
      items.push(item);
    }
    if (page === data.totalPages) {
      if (items.length !== expected || new Set(items.map(item => item.path)).size !== expected) throw new Error('Incomplete public snapshot');
      Object.defineProperty(items, 'versionHash', { value: version });
      return items;
    }
  }
  throw new Error('Public snapshot pagination exceeded build limit');
}
