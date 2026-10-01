import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { getPublicRoutes } from './prerender-routes.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repositoryRoot = path.resolve(__dirname, '..');
const distDir = path.join(repositoryRoot, 'dist');

test('getPublicRoutes inventory structure', () => {
  const routes = getPublicRoutes();
  assert.ok(routes.length >= 35, `Expected at least 35 public routes, got ${routes.length}`);

  // Core static pages
  const paths = new Set(routes.map(r => r.path));
  assert.ok(paths.has('/'), 'Must include home /');
  assert.ok(paths.has('/shop'), 'Must include /shop');
  assert.ok(paths.has('/about'), 'Must include /about');
  assert.ok(paths.has('/contact'), 'Must include /contact');
  assert.ok(paths.has('/shipping-policy'), 'Must include /shipping-policy');
  assert.ok(paths.has('/return-policy'), 'Must include /return-policy');
  assert.ok(paths.has('/privacy-policy'), 'Must include /privacy-policy');
  assert.ok(paths.has('/terms'), 'Must include /terms');

  // Must NOT include private or customer routes
  assert.strictEqual(paths.has('/cart'), false, 'Private /cart must not be pre-rendered');
  assert.strictEqual(paths.has('/checkout'), false, 'Private /checkout must not be pre-rendered');
  assert.strictEqual(paths.has('/account'), false, 'Private /account must not be pre-rendered');
  assert.strictEqual(paths.has('/admin'), false, 'Private /admin must not be pre-rendered');
  assert.strictEqual(paths.has('/wishlist'), false, 'Private /wishlist must not be pre-rendered');

  // Must include all 16 controlled products
  const expectedProducts = [
    'forever-crochet-rose-bouquet',
    'crochet-tulip-bouquet',
    'heart-bear',
    'couple-bunny-set',
    'mini-panda-amigurumi',
    'crochet-bunny',
    'crochet-marigold-garland',
    'sunflower-bouquet',
    'crochet-hanging-planter',
    'boho-wall-hanging',
    'love-letter-crochet-set',
    'mini-rose-box',
    'lotus-mala',
    'crochet-toran',
    'daisy-coaster-set',
    'mini-teddy-bear',
  ];

  for (const slug of expectedProducts) {
    const pPath = `/products/${slug}`;
    assert.ok(paths.has(pPath), `Must include controlled product route ${pPath}`);
    const r = routes.find(x => x.path === pPath);
    assert.ok(r.title.includes('Sulocraft'), `Product title must include brand: ${r.title}`);
    assert.ok(r.price > 0, `Product must have valid positive price: ${r.price}`);
    assert.strictEqual(r.currency, 'INR');
    assert.ok(r.sku && r.sku.startsWith('SULO-'), `Product must have valid SKU: ${r.sku}`);
  }

  // Must include canonical categories
  assert.ok(paths.has('/categories/flowers'), 'Must include flowers category');
  assert.ok(paths.has('/categories/amigurumi'), 'Must include amigurumi category');
  assert.ok(paths.has('/categories/baby'), 'Must include baby category');
  assert.ok(paths.has('/categories/home-decor'), 'Must include home-decor category');
  assert.ok(paths.has('/categories/pooja-devotional'), 'Must include pooja-devotional category');

  // Validate SEO fields on all routes
  for (const r of routes) {
    assert.ok(r.title && r.title.length > 5, `Route ${r.path} must have meaningful title`);
    assert.ok(r.description && r.description.length > 10, `Route ${r.path} must have meaningful description`);
    assert.ok(r.canonicalPath.startsWith('/'), `Route ${r.path} must have absolute canonicalPath`);
    assert.ok(Array.isArray(r.breadcrumbs) && r.breadcrumbs.length > 0, `Route ${r.path} must have breadcrumbs`);
  }
});

test('prerender execution writes static HTML with metadata and schema', async () => {
  // Ensure dist directory exists with a template
  fs.mkdirSync(distDir, { recursive: true });
  const templatePath = path.join(distDir, 'index.html');
  const dummyTemplate = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Sulocraft Template</title></head><body><div id="root"></div></body></html>';
  fs.writeFileSync(templatePath, dummyTemplate, 'utf8');

  // Import and run prerender
  const { prerender } = await import('./prerender.mjs');
  prerender();

  // Verify Shop static page
  const shopPath = path.join(distDir, 'shop', 'index.html');
  assert.ok(fs.existsSync(shopPath), 'dist/shop/index.html must exist');
  const shopHtml = fs.readFileSync(shopPath, 'utf8');
  assert.ok(shopHtml.includes('<title>Shop Handcrafted Crochet Creations | Sulocraft</title>'), 'Shop title injected');
  assert.ok(shopHtml.includes('<link rel="canonical" href="https://sulocraft.com/shop">'), 'Shop canonical injected');
  assert.ok(shopHtml.includes('id="sulocraft-breadcrumb-schema"'), 'Shop breadcrumb schema injected');
  assert.ok(shopHtml.includes('All Products'), 'Shop initial markup injected');

  // Verify Product static page
  const prodPath = path.join(distDir, 'products', 'heart-bear', 'index.html');
  assert.ok(fs.existsSync(prodPath), 'dist/products/heart-bear/index.html must exist');
  const prodHtml = fs.readFileSync(prodPath, 'utf8');
  assert.ok(prodHtml.includes('<title>Heart Bear | Sulocraft</title>'), 'Product title injected');
  assert.ok(prodHtml.includes('<link rel="canonical" href="https://sulocraft.com/products/heart-bear">'), 'Product canonical injected');
  assert.ok(prodHtml.includes('id="sulocraft-product-schema"'), 'Product Schema.org JSON-LD injected');
  assert.ok(prodHtml.includes('"price":1799'), 'Product price in Schema.org JSON-LD');
  assert.ok(prodHtml.includes('₹1799'), 'Product price in initial body markup');

  // Verify Category static page
  const catPath = path.join(distDir, 'categories', 'flowers', 'index.html');
  assert.ok(fs.existsSync(catPath), 'dist/categories/flowers/index.html must exist');
  const catHtml = fs.readFileSync(catPath, 'utf8');
  assert.ok(catHtml.includes('Flowers | Handcrafted Crochet | Sulocraft'), 'Category title injected');
  assert.ok(catHtml.includes('https://sulocraft.com/categories/flowers'), 'Category canonical injected');

  // Verify private routes are NOT generated
  assert.strictEqual(fs.existsSync(path.join(distDir, 'cart', 'index.html')), false, 'Cart must not be pre-rendered');
  assert.strictEqual(fs.existsSync(path.join(distDir, 'admin', 'index.html')), false, 'Admin must not be pre-rendered');
  assert.strictEqual(fs.existsSync(path.join(distDir, 'checkout', 'index.html')), false, 'Checkout must not be pre-rendered');
});
