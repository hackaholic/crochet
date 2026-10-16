import fs from 'node:fs/promises';
import path from 'node:path';
import { apiBase, getJson, validatePublicPath } from './prerender-routes.mjs';

const namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9';
const escapeXml = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[char]));
const documentXml = (type, entries) => `<?xml version="1.0" encoding="UTF-8"?>\n<${type} xmlns="${namespace}">\n${entries.join('\n')}\n</${type}>\n`;
function integer(value, fallback, max, name, min = 1) {
  const result = value === undefined || value === '' ? fallback : Number(value);
  if (!Number.isInteger(result) || result < min || result > max) throw new Error(`Invalid ${name}`);
  return result;
}
export function resourcePolicy(mode, environment) {
  if (!['production', 'preprod'].includes(mode)) throw new Error('Invalid SEO build mode');
  const raw = environment.SEO_INDEXING_ENABLED;
  if (raw !== undefined && !['true', 'false'].includes(raw)) throw new Error('SEO_INDEXING_ENABLED must be true or false');
  if (mode === 'production' && raw === undefined) throw new Error('Production requires explicit SEO_INDEXING_ENABLED');
  if (mode !== 'production' && raw === 'true') throw new Error('Nonproduction indexing is forbidden');
  const indexing = raw === 'true';
  let origin;
  if (environment.SEO_PUBLIC_ORIGIN) {
    const url = new URL(environment.SEO_PUBLIC_ORIGIN);
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash || url.pathname !== '/') throw new Error('Invalid SEO_PUBLIC_ORIGIN');
    if (indexing && (url.protocol !== 'https:' || ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname))) throw new Error('Indexed production requires a public HTTPS origin');
    origin = url.origin;
  }
  if (indexing && !origin) throw new Error('Indexed production requires SEO_PUBLIC_ORIGIN');
  return { indexing, origin,
    maxUrls: integer(environment.SEO_SITEMAP_MAX_URLS, 50000, 50000, 'sitemap URL limit'),
    maxBytes: integer(environment.SEO_SITEMAP_MAX_BYTES, 52428800, 52428800, 'sitemap byte limit', 512),
    cacheSeconds: integer(environment.SEO_RESOURCE_CACHE_SECONDS, 300, 86400, 'resource cache duration', 0),
  };
}
export function sitemapFiles(inventory, policy) {
  if (!policy.indexing) return new Map([['sitemap.xml', documentXml('urlset', [])]]);
  if (!Array.isArray(inventory.routes) || inventory.routes.length !== inventory.totalRoutes) throw new Error('Incomplete sitemap inventory');
  const seen = new Set();
  const entries = inventory.routes.map(route => {
    validatePublicPath(route.path);
    if (seen.has(route.path)) throw new Error('Duplicate sitemap path');
    seen.add(route.path);
    if (route.canonicalUrl !== `${policy.origin}${route.path}`) throw new Error('Sitemap canonical origin/path mismatch');
    // Backend currently uses generated-today for static content; that is not modification evidence.
    const entityRoute = /^\/(products|categories|collections|occasions)\//.test(route.path);
    let lastmod = '';
    if (entityRoute && route.lastmod) {
      if (!/^\d{4}-\d{2}-\d{2}(?:T[\d:.+-]+Z?)?$/.test(route.lastmod) || !Number.isFinite(Date.parse(route.lastmod))) throw new Error('Invalid sitemap lastmod');
      lastmod = `<lastmod>${escapeXml(route.lastmod)}</lastmod>`;
    }
    return `<url><loc>${escapeXml(route.canonicalUrl)}</loc>${lastmod}</url>`;
  });
  const chunks = [];
  let current = [];
  const envelopeBytes = Buffer.byteLength(documentXml('urlset', []));
  let currentBytes = envelopeBytes;
  for (const entry of entries) {
    const entryBytes = Buffer.byteLength(entry);
    if (envelopeBytes + entryBytes > policy.maxBytes) throw new Error('Sitemap entry exceeds byte limit');
    if (current.length && (current.length >= policy.maxUrls || currentBytes + entryBytes + (current.length ? 1 : 0) > policy.maxBytes)) {
      chunks.push(current); current = []; currentBytes = envelopeBytes;
    }
    currentBytes += entryBytes + (current.length ? 1 : 0);
    current.push(entry);
  }
  if (current.length || !chunks.length) chunks.push(current);
  if (chunks.length === 1) return new Map([['sitemap.xml', documentXml('urlset', chunks[0])]]);
  if (chunks.length > 50000) throw new Error('Sitemap index exceeds protocol limit');
  const files = new Map(chunks.map((chunk, index) => [`sitemap-${index + 1}.xml`, documentXml('urlset', chunk)]));
  const index = documentXml('sitemapindex', [...files.keys()].map(name => `<sitemap><loc>${escapeXml(`${policy.origin}/${name}`)}</loc></sitemap>`));
  if (Buffer.byteLength(index) > policy.maxBytes) throw new Error('Sitemap index exceeds byte limit');
  files.set('sitemap.xml', index);
  return files;
}
export async function writeSeoResources({ repositoryRoot, mode, environment, fetcher = fetch }) {
  const policy = resourcePolicy(mode, environment);
  const dist = path.join(repositoryRoot, 'dist');
  let inventory;
  if (policy.indexing) {
    const base = apiBase(environment.SEO_API_BASE_URL || environment.VITE_API_BASE_URL);
    inventory = await getJson(base, '/seo/routes', fetcher);
    for (const route of inventory.routes ?? []) {
      validatePublicPath(route.path);
      const file = path.join(dist, route.path === '/' ? 'index.html' : `${route.path.slice(1)}/index.html`);
      const html = await fs.readFile(file, 'utf8');
      if (!html.includes('id="storefront-bootstrap"') || !html.includes('name="robots" content="index,follow"')) throw new Error('Sitemap route has no indexable rendered page');
    }
  }
  const files = sitemapFiles(inventory, policy);
  const robots = `User-agent: *\nAllow: /\n${policy.indexing ? `\nSitemap: ${policy.origin}/sitemap.xml\n` : ''}`;
  files.set('robots.txt', robots);
  const headers = `${policy.indexing ? '' : '/*\n  X-Robots-Tag: noindex, nofollow\n\n'}/robots.txt\n  Content-Type: text/plain; charset=utf-8\n  Cache-Control: public, max-age=${policy.cacheSeconds}\n\n/sitemap*.xml\n  Content-Type: application/xml; charset=utf-8\n  Cache-Control: public, max-age=${policy.cacheSeconds}\n`;
  files.set('_headers', headers);
  for (const [name, content] of files) await fs.writeFile(path.join(dist, name), content);
  return [...files.keys()];
}
