export function safePath(value) {
  if (typeof value !== 'string' || !/^\/(?:[a-z0-9-]+\/)*[a-z0-9-]*$/i.test(value)) throw new Error('Invalid storefront path');
  return value.toLowerCase().replace(/\/+$/, '') || '/';
}
export const isPrivatePath = value => /^\/(?:admin|account|cart|checkout|wishlist|auth|track)(?:\/|$)/.test(value);
export function canonicalMetadata(metadata, policy) {
  if (!policy?.origin) return metadata;
  const origin = new URL(policy.origin);
  if (!['http:', 'https:'].includes(origin.protocol) || origin.username || origin.password || origin.pathname !== '/' || origin.search || origin.hash) throw new Error('Invalid public SEO origin');
  let path;
  try { path=safePath(metadata.canonicalPath); } catch(error) {
    if(metadata.robots !== 'noindex,nofollow') throw error;
    return {...metadata,canonicalPath:'/',canonicalUrl:null,httpStatus:404};
  }
  return { ...metadata, canonicalUrl: new URL(path, origin).href,
    robots: policy.indexing ? metadata.robots : 'noindex,nofollow' };
}
export function routeDecision(url, metadata) {
  const path = safePath(url.pathname);
  const status = metadata.httpStatus ?? 200;
  if (![200,301,404,410].includes(status)) throw new Error('Invalid SEO route status');
  if (status === 404 || status === 410) return {status};
  const target = safePath(status === 301 ? metadata.redirectTo : metadata.canonicalPath);
  if (isPrivatePath(target)) throw new Error('Private redirect target');
  if (status === 301 && target === path) throw new Error('Redirect loop');
  const page = url.searchParams.get('page');
  if (page !== null && page !== '1') return {status:404};
  if (target !== path || url.pathname !== path) {
    const query = new URLSearchParams(url.search);
    if (target.startsWith('/categories/')) query.delete('category');
    if (target.startsWith('/collections/')) query.delete('collection');
    return {status:301,target,location:target+(query.size ? `?${query}`:'')};
  }
  return {status:200,query: Boolean(url.search)};
}
export async function loadRouteMetadata(apiBase, requestPath, fetcher = fetch) {
  const base = new URL(apiBase);
  if (!['http:', 'https:'].includes(base.protocol) || base.username || base.password || base.search || base.hash) throw new Error('Invalid public SEO API');
  // Only taxonomy selectors affect resolver canonicals; never relay login/tracking/search tokens.
  const requested = new URL(requestPath, 'http://routing.invalid');
  const selectors = new URLSearchParams();
  for (const key of ['category','collection','occasion']) {
    const value=requested.searchParams.get(key);
    if(value && /^[a-z0-9-]+$/i.test(value)) selectors.set(key,value);
  }
  const publicPath=requested.pathname+(selectors.size ? `?${selectors}`:'');
  const response = await fetcher(`${base.href.replace(/\/$/,'')}/seo/resolve?path=${encodeURIComponent(publicPath)}`, {signal:AbortSignal.timeout(5000),redirect:'manual'});
  if (!response.ok) throw new Error('SEO API unavailable');
  return response.json();
}
