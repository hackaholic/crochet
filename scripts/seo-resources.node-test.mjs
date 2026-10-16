import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { resourcePolicy, sitemapFiles, writeSeoResources } from './seo-resources.mjs';
const indexed = overrides => resourcePolicy('production', { SEO_INDEXING_ENABLED: 'true', SEO_PUBLIC_ORIGIN: 'https://store.example', ...overrides });
const route = (path, more = {}) => ({ path, canonicalUrl: `https://store.example${path}`, ...more });
const inventory = routes => ({ totalRoutes: routes.length, routes });

test('indexing fails closed for missing, malformed and nonproduction configuration', () => {
  for (const [mode, environment] of [['production', {}], ['production', {SEO_INDEXING_ENABLED:'true'}], ['preprod', {SEO_INDEXING_ENABLED:'true'}], ['production', {SEO_INDEXING_ENABLED:'yes'}]]) assert.throws(() => resourcePolicy(mode, environment));
  for (const origin of ['http://store.example', 'https://user:secret@store.example', 'https://store.example/path', 'https://localhost']) assert.throws(() => indexed({SEO_PUBLIC_ORIGIN:origin}));
  assert.equal(resourcePolicy('preprod', {}).indexing, false);
});
test('non-indexing environments advertise no catalogue URLs', () => {
  const xml = sitemapFiles(undefined, resourcePolicy('preprod', {})).get('sitemap.xml');
  assert.ok(xml.includes('<urlset')); assert.ok(!xml.includes('<loc>'));
});
test('DB entity dates are preserved while generated static dates are omitted', () => {
  const xml = sitemapFiles(inventory([route('/', {lastmod:'2026-10-14'}), route('/products/bunny', {lastmod:'2026-10-01'})]), indexed()).get('sitemap.xml');
  assert.ok(xml.includes('<lastmod>2026-10-01</lastmod>')); assert.ok(!xml.includes('2026-10-14'));
});
test('splits at configured count and creates a same-origin sitemap index', () => {
  const files = sitemapFiles(inventory([route('/'), route('/shop'), route('/about')]), indexed({SEO_SITEMAP_MAX_URLS:'2'}));
  assert.equal(files.size, 3);
  assert.ok(files.get('sitemap.xml').includes('<sitemapindex'));
  assert.ok(files.get('sitemap.xml').includes('https://store.example/sitemap-2.xml'));
  assert.equal((files.get('sitemap-1.xml').match(/<url>/g)||[]).length, 2);
});
test('splits at byte boundaries and rejects oversize or invalid records', () => {
  const records = Array.from({length:10}, (_, i)=>route(`/products/${'b'.repeat(90)}-${i}`));
  const files = sitemapFiles(inventory(records), indexed({SEO_SITEMAP_MAX_BYTES:'1024'}));
  for (const file of files.values()) assert.ok(Buffer.byteLength(file)<=1024);
  for (const records of [[route('/admin')], [route('/'), route('/')], [route('/shop', {canonicalUrl:'https://evil.example/shop'})], [route('/products/bunny', {lastmod:'not-a-date'})], [route('/products/'+ 'a'.repeat(1500))]]) assert.throws(()=>sitemapFiles(inventory(records), indexed({SEO_SITEMAP_MAX_BYTES:'1024'})));
});
test('root resources are written without an API call for non-indexing builds', async () => {
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'sulocraft-seo-'));
  try {
    await fs.mkdir(path.join(root,'dist'));
    await writeSeoResources({repositoryRoot:root, mode:'preprod',environment:{},fetcher:()=>{throw Error('Unexpected API call');}});
    assert.equal(await fs.readFile(path.join(root,'dist/robots.txt'),'utf8'),'User-agent: *\nAllow: /\n');
    const headers=await fs.readFile(path.join(root,'dist/_headers'),'utf8');
    assert.ok(headers.includes('X-Robots-Tag: noindex, nofollow')); assert.ok(headers.includes('application/xml'));
  } finally {await fs.rm(root,{recursive:true,force:true});}
});
test('production rejects API failure and missing rendered routes before publication', async () => {
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'sulocraft-seo-'));
  try {
    await fs.mkdir(path.join(root,'dist'));
    const options={repositoryRoot:root, mode:'production',environment:{SEO_INDEXING_ENABLED:'true', SEO_PUBLIC_ORIGIN:'https://store.example', SEO_API_BASE_URL:'https://api.example/api/v1'}};
    await assert.rejects(writeSeoResources({...options,fetcher:async()=>({ok:false,status:503})}),/503/);
    await assert.rejects(writeSeoResources({...options,fetcher:async()=>({ok:true,json:async()=>inventory([route('/')])})}));
    await assert.rejects(fs.stat(path.join(root,'dist/sitemap.xml')));
  } finally {await fs.rm(root,{recursive:true,force:true});}
});

test('production exports only validated backend routes with correct root advertisement', async () => {
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'sulocraft-seo-'));
  try {
    await fs.mkdir(path.join(root,'dist'));
    await fs.writeFile(path.join(root,'dist/index.html'),'<meta name="robots" content="index,follow"><script id="storefront-bootstrap" type="application/json">{}</script>');
    await writeSeoResources({repositoryRoot:root,mode:'production',environment:{SEO_INDEXING_ENABLED:'true',SEO_PUBLIC_ORIGIN:'https://store.example',SEO_API_BASE_URL:'https://api.example/api/v1'},fetcher:async()=>({ok:true,json:async()=>inventory([route('/')])})});
    const xml=await fs.readFile(path.join(root,'dist/sitemap.xml'),'utf8');
    assert.ok(xml.includes('<loc>https://store.example/</loc>'));
    assert.ok((await fs.readFile(path.join(root,'dist/robots.txt'),'utf8')).includes('Sitemap: https://store.example/sitemap.xml'));
    assert.ok(!(await fs.readFile(path.join(root,'dist/_headers'),'utf8')).includes('X-Robots-Tag'));
  } finally {await fs.rm(root,{recursive:true,force:true});}
});
