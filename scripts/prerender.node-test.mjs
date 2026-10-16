import test from 'node:test';
import assert from 'node:assert/strict';
import { apiBase, validatePublicPath, getPublicRoutes } from './prerender-routes.mjs';
import { pageDocument, serializePublicData } from './prerender.mjs';

test('public paths reject traversal, private routes and external URLs', () => {
  for (const value of ['/../secret', '/admin', '//evil.test', '/products/%2e%2e', '/account/settings', '/product?secret=x']) assert.throws(() => validatePublicPath(value));
  assert.equal(validatePublicPath('/products/bunny'), '/products/bunny');
});
test('build API configuration rejects credentials and non HTTP URLs', () => {
  for (const value of ['file:///etc/passwd', 'https://user:secret@api.test', 'https://api.test?q=x']) assert.throws(() => apiBase(value));
});
test('snapshot rejects duplicates and nonpublic metadata', async () => {
  const item = { path: '/', metadata: { title: 'Home', description: 'Public', robots: 'index,follow' } };
  await assert.rejects(getPublicRoutes('https://api.test', async () => ({ ok: true, json: async () => ({ versionHash: 'a'.repeat(16), items: [item, item], totalCount: 2, totalPages: 1 }) })));
  await assert.rejects(getPublicRoutes('https://api.test', async () => ({ ok: false, status: 503 })));
});
test('HTML retains React markup and escapes script-breaking API content', () => {
  const bootstrap = { path: '/', metadata: { title: 'A < B', description: 'Hello', canonicalUrl: 'https://store.test/', robots: 'index,follow' }, content: '</script><script>alert(1)</script>' };
  const html = pageDocument('<head><title>Old</title><meta name="robots" content="index,follow"></head><div id="root"></div>', '<h1>Visible</h1>', bootstrap);
  assert.ok(html.includes('<div id="root"><h1>Visible</h1></div>'));
  assert.equal((html.match(/name="robots"/g) || []).length, 1);
  assert.ok(html.includes('A &lt; B'));
  assert.ok(!serializePublicData(bootstrap).includes('</script>'));
  assert.deepEqual(JSON.parse(serializePublicData(bootstrap)), bootstrap);
});

test('paginated snapshot fails closed when its version changes', async () => {
  const fetcher = async url => ({ ok: true, json: async () => ({
    page: Number(new URL(url).searchParams.get('page')), totalPages: 2, totalCount: 2,
    versionHash: (url.includes('page=1') ? 'a' : 'b').repeat(16),
    items: [{ path: url.includes('page=1') ? '/' : '/shop', metadata: { title: 'Public', description: 'Public', robots: 'index,follow' } }],
  }) });
  await assert.rejects(getPublicRoutes('https://api.test', fetcher), /version changed/);
});

test('missing public pages return real 404; private pages receive noindex CSR shell', async () => {
  const worker = (await import('../worker/storefront.mjs')).default;
  const env = { ASSETS: { fetch: async request => {
    if(new URL(request.url).pathname === '/routing-policy.json') return Response.json({comingSoon:true});
    assert.equal(new URL(request.url).pathname, '/app-shell.html');
    return new Response('<div id="root"></div>', { headers: { 'Content-Type': 'text/html' } });
  } } };
  for (const [path, status] of [['/products/deleted', 404], ['/account', 200], ['/admin/products', 200], ['/unknown', 404]]) {
    const response = await worker.fetch(new Request(`https://store.test${path}`), env);
    assert.equal(response.status, status);
    assert.equal(response.headers.get('X-Robots-Tag'), 'noindex, nofollow');
    assert.ok(!(await response.text()).includes('storefront-bootstrap'));
  }
});

test('rendering never uses previously generated page content as a template', () => {
  assert.throws(() => pageDocument('<div id="root"><h1>Old content</h1></div>', '', {}), /pristine app shell/);
});

test('initial social tags share runtime values, escape content and reject unsafe images', async () => {
  const {socialMetadata}=await import('../src/lib/seo/socialMetadata.mjs');
  const metadata={title:'Rose "bouquet"',description:'Saved <summary>',canonicalPath:'/products/rose',canonicalUrl:'https://store.test/products/rose',pageType:'product',robots:'index,follow',imageUrl:'https://media.test/rose.png',imageAlt:'Red <roses>',imageWidth:800,imageHeight:1000,imageType:'image/png'};
  const template='<head><meta property="og:image" content="old"><meta name="twitter:card" content="old"></head><div id="root"></div>';
  const html=pageDocument(template,'<h1>Rose</h1>',{metadata});
  for(const key of Object.keys(socialMetadata(metadata,metadata.canonicalUrl))) {
    assert.equal((html.match(new RegExp(`(?:property|name)="${key}"`,'g'))||[]).length,1,key);
  }
  assert.ok(html.includes('content="Red &lt;roses&gt;"'));
  assert.ok(html.includes('name="twitter:image:alt"'));
  assert.ok(html.includes('property="og:image:width" content="800"'));
  for(const imageUrl of [null,'javascript:alert(1)','data:image/png;base64,abc','https://user:secret@media.test/p.png','//media.test/p.png','/relative.png']) {
    const tags=socialMetadata({...metadata,imageUrl},metadata.canonicalUrl);
    assert.equal(tags['og:image'],undefined);
    assert.equal(tags['twitter:card'],'summary');
  }
  for(const canonicalPath of ['/account','/admin/orders','/track']) {
    assert.equal(socialMetadata({...metadata,canonicalPath},metadata.canonicalUrl)['og:image'],undefined);
  }
  for(const httpStatus of [404,410]) assert.equal(socialMetadata({...metadata,httpStatus},metadata.canonicalUrl)['og:image'],undefined);
  const unknown=socialMetadata({...metadata,imageWidth:-1,imageType:'text/html'},metadata.canonicalUrl);
  assert.equal(unknown['og:image:width'],undefined);
  assert.equal(unknown['og:image:type'],undefined);
});
