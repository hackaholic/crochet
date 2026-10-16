import { socialMetadata } from '../src/lib/seo/socialMetadata.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { canonicalMetadata } from '../src/lib/seo/urlPolicy.mjs';
import { apiBase, getJson, getPublicRoutes } from './prerender-routes.mjs';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char]));
export const serializePublicData = value => JSON.stringify(value).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');

export function pageDocument(template, html, bootstrap, schema) {
  if (!template.includes('<div id="root"></div>')) throw new Error('Public render requires a pristine app shell');
  const metadata = bootstrap.metadata;
  const canonical = new URL(metadata.canonicalUrl);
  if (!['http:', 'https:'].includes(canonical.protocol) || canonical.username || canonical.password) throw new Error('Invalid canonical URL');
  const head = `<title>${escape(metadata.title)}</title>
<meta name="description" content="${escape(metadata.description)}">
<meta name="robots" content="${escape(metadata.robots)}">
<link rel="canonical" href="${escape(canonical.href)}">
${Object.entries(socialMetadata(metadata, canonical.href)).map(([key, content]) =>
  `<meta ${key.startsWith('og:') ? 'property' : 'name'}="${key}" content="${escape(content)}">`).join('\n')}
${schema ? Object.entries(schema).map(([id, value]) => `<script id="${escape(id)}" type="application/ld+json"${id === 'sulocraft-product-schema' ? ' data-seo="product"' : ''}>${serializePublicData(value)}</script>`).join('\n') : ''}`;
  return template.replace(/<title>[\s\S]*?<\/title>/gi, '')
    .replace(/<meta\s+(?:name|property)="(?:description|robots|og:[^"]*|twitter:[^"]*)"[^>]*>/gi, '')
    .replace('</head>', `${head}</head>`)
    .replace('<div id="root"></div>', `<div id="root">${html}</div><script id="storefront-bootstrap" type="application/json">${serializePublicData(bootstrap)}</script>`);
}

export async function prerender({ repositoryRoot = process.cwd(), baseUrl = process.env.SEO_API_BASE_URL || process.env.VITE_API_BASE_URL, fetcher = fetch, policy } = {}) {
  if (!baseUrl) throw new Error('SEO_API_BASE_URL is required for public-page rendering');
  const base = apiBase(baseUrl);
  const routes = await getPublicRoutes(base, fetcher);
  const products = [];
  for (let page = 1; page <= 2000; page++) {
    const batch = await getJson(base, `/products?page=${page}&limit=100`, fetcher);
    if (!Array.isArray(batch)) throw new Error('Invalid public catalogue');
    products.push(...batch);
    if (new Set(products.map(product => product.id)).size !== products.length) throw new Error('Catalogue pagination did not advance');
    if (batch.length < 100) break;
    if (page === 2000) throw new Error('Catalogue build limit exceeded');
  }
  const [categories, collections, home] = await Promise.all([
    getJson(base, '/categories?flat=false&includeEmpty=false', fetcher),
    getJson(base, '/collections', fetcher), getJson(base, '/storefront/home', fetcher),
  ]);
  if (!Array.isArray(categories) || !Array.isArray(collections) || !Array.isArray(home.hero) || !Array.isArray(home.sections)) throw new Error('Invalid public storefront data');
  // Reject changes both within pagination and while fetching supplemental public data.
  const after = await getPublicRoutes(base, fetcher);
  if (routes.versionHash !== after.versionHash || JSON.stringify(routes) !== JSON.stringify(after)) throw new Error('Public snapshot changed during build; retry');
  const renderer = await import(pathToFileURL(path.join(repositoryRoot, '.seo-render/entry-server.js')).href);
  const dist = path.join(repositoryRoot, 'dist');
  const template = await fs.readFile(path.join(dist, 'app-shell.html'), 'utf8');
  const catalogue = products.map(renderer.toProduct);
  const documents = [];
  for (const route of routes) {
    const entity = route.metadata.productEntity;
    const product = entity && catalogue.find(item => item.id === entity.id);
    if (entity && (!product || product.price !== entity.price || product.name !== entity.name)) throw new Error('Catalogue and SEO product snapshot disagree');
    const metadata = canonicalMetadata(route.metadata, policy);
    const bootstrap = { policy, path: route.path, metadata, products: catalogue, categories, collections, home };
    documents.push({ path: route.path, html: pageDocument(template, renderer.render(bootstrap), bootstrap, renderer.pageSchemas(metadata, metadata.canonicalUrl, product, categories)) });
  }
  // Do not publish partial output when rendering any route fails.
  await fs.writeFile(path.join(dist, 'app-shell.html'), template.replace('index,follow', 'noindex,nofollow'));
  for (const document of documents) {
    const target = path.join(dist, document.path === '/' ? 'index.html' : `${document.path.slice(1)}/index.html`);
    await fs.mkdir(path.dirname(target), { recursive: true });
    await fs.writeFile(target, document.html);
  }
  console.log(`[sulocraft] Rendered ${documents.length} API-backed public pages`);
}
