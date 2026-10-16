import test from 'node:test';
import assert from 'node:assert/strict';
import {routeDecision,canonicalMetadata,loadRouteMetadata} from '../src/lib/seo/urlPolicy.mjs';
import worker from '../worker/storefront.mjs';

test('canonical case/slash and old aliases redirect directly; unsafe targets fail closed',()=>{
  assert.equal(routeDecision(new URL('https://store.test/PRODUCTS/OLD/'),{httpStatus:301,redirectTo:'/products/current'}).location,'/products/current');
  for(const target of ['https://evil.test','//evil.test','/admin','/products/old','/../secret','/products/new?redirect=evil']) assert.throws(()=>routeDecision(new URL('https://store.test/products/old'),{httpStatus:301,redirectTo:target}));
});
test('queries are nonindexing; unsupported pagination never masquerades as page1',()=>{
  assert.equal(routeDecision(new URL('https://store.test/shop?q=bunny'),{canonicalPath:'/shop'}).query,true);
  assert.equal(routeDecision(new URL('https://store.test/shop?page=2'),{canonicalPath:'/shop'}).status,404);
  assert.equal(routeDecision(new URL('https://store.test/shop?category=flowers'),{canonicalPath:'/categories/flowers'}).location,'/categories/flowers');
});
test('configured canonical origin and indexing override conflicting upstream defaults',()=>{
  const value=canonicalMetadata({canonicalPath:'/products/bunny',canonicalUrl:'https://wrong.test/products/bunny',robots:'index,follow'},{origin:'https://dev.test',indexing:false});
  assert.equal(value.canonicalUrl,'https://dev.test/products/bunny');assert.equal(value.robots,'noindex,nofollow');
  assert.throws(()=>canonicalMetadata({canonicalPath:'//evil.test'},{origin:'https://store.test',indexing:true}));
});
test('Worker checks lifecycle before serving generated HTML, handles queries and API failure',async()=>{
  const original=globalThis.fetch;
  const env={ASSETS:{fetch:async request=>{
    const path=new URL(request.url).pathname;
    if(path==='/routing-policy.json')return Response.json({apiBase:'https://api.test/api/v1'});
    return new Response(path==='/app-shell.html' ? '<div id="root"></div>':'<h1>Generated</h1>');
  }}};
  try {
    globalThis.fetch=async url=>{
      const path=new URL(url).searchParams.get('path');
      if(path==='/products/down')throw Error('offline');
      if(path==='/products/gone')return Response.json({httpStatus:410});
      if(path==='/products/missing')return Response.json({httpStatus:404});
      if(path==='/products/old')return Response.json({httpStatus:301,redirectTo:'/products/current'});
      return Response.json({httpStatus:200,canonicalPath:path.split('?')[0]});
    };
    for(const [path,status] of [['/products/gone',410],['/products/missing',404],['/products/down',503],['/products/current',200],['/shop?q=bunny',200],['/shop?page=2',404],['/account',200]]) {
      const response=await worker.fetch(new Request('https://store.test'+path),env);
      assert.equal(response.status,status,path);
      if(path!=='/products/current')assert.equal(response.headers.get('X-Robots-Tag'),'noindex, nofollow');
      if(path.includes('?'))assert.ok(!(await response.text()).includes('Generated'));
    }
    const moved=await worker.fetch(new Request('https://store.test/PRODUCTS/OLD/'),env);
    assert.equal(moved.status,301);assert.equal(moved.headers.get('Location'),'/products/current');
  }finally{globalThis.fetch=original;}
});

test('invalid noindex error paths do not crash the browser metadata fallback',()=>{
  const metadata=canonicalMetadata({canonicalPath:'/bad%20path',robots:'noindex,nofollow'},{origin:'https://store.test',indexing:false});
  assert.equal(metadata.httpStatus,404);assert.equal(metadata.canonicalUrl,null);
});

test('resolver uses Workers-compatible manual redirects and rejects upstream redirection',async()=>{
  for(const status of [301,302,307,308]) {
    await assert.rejects(loadRouteMetadata('https://api.test/api/v1','/shop',async (_url,options)=>{
      assert.equal(options.redirect,'manual');
      return new Response(null,{status,headers:{Location:'https://untrusted.test'}});
    }),/unavailable/);
  }
  const metadata=await loadRouteMetadata('https://api.test/api/v1','/shop',async (_url,options)=>{
    assert.equal(options.redirect,'manual');return Response.json({httpStatus:200,canonicalPath:'/shop'});
  });
  assert.equal(metadata.httpStatus,200);
});

test('resolver never relays sensitive or unrelated query values',async()=>{
  await loadRouteMetadata('https://api.test/api/v1','/shop?category=flowers&token=secret&q=private&tracking=secret',async url=>{
    assert.equal(new URL(url).searchParams.get('path'),'/shop?category=flowers');
    return Response.json({httpStatus:200,canonicalPath:'/categories/flowers'});
  });
});
