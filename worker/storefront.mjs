import {safePath,isPrivatePath,routeDecision,loadRouteMetadata} from '../src/lib/seo/urlPolicy.mjs';
async function shell(request,env,status) {
  const url=new URL(request.url);url.pathname='/app-shell.html';url.search='';
  const asset=await env.ASSETS.fetch(new Request(url,{method:request.method}));
  const headers=new Headers(asset.headers);headers.set('X-Robots-Tag','noindex, nofollow');headers.set('Cache-Control','no-store');
  return new Response(request.method==='HEAD' ? null:asset.body,{status,headers});
}
export default {
  async fetch(request,env) {
    const url=new URL(request.url);
    if(!['GET','HEAD'].includes(request.method)) return new Response('Method not allowed',{status:405,headers:{Allow:'GET, HEAD'}});
    if(url.pathname.startsWith('/assets/') || /\.(?:xml|txt|png|jpg|jpeg|svg|webp|ico|woff2?)$/.test(url.pathname)) return env.ASSETS.fetch(request);
    let pathname;
    try {pathname=safePath(url.pathname);} catch {return shell(request,env,404);}
    if(isPrivatePath(pathname)) return shell(request,env,200);
    let stage='configuration';
    try {
      const configUrl=new URL('/routing-policy.json',url);
      const config=await env.ASSETS.fetch(new Request(configUrl));
      if(!config.ok) throw new Error('Routing policy missing');
      const policy=await config.json();
      if(policy.comingSoon) return pathname==='/' ? env.ASSETS.fetch(request):shell(request,env,404);
      stage='resolver';
      const metadata=await loadRouteMetadata(policy.apiBase,pathname+url.search);
      stage='decision';
      const decision=routeDecision(url,metadata);
      if(decision.status===301) {
        stage='redirect-target';
        const target=await loadRouteMetadata(policy.apiBase,decision.target);
        if((target.httpStatus ?? 200)!==200 || safePath(target.canonicalPath)!==decision.target) throw new Error('Redirect target is not canonical');
        return new Response(null,{status:301,headers:{Location:decision.location,'Cache-Control':'no-store',...(!policy.indexing ? {'X-Robots-Tag':'noindex, nofollow'}:{})}});
      }
      if(decision.status!==200) return shell(request,env,decision.status);
      if(decision.query) return shell(request,env,200);
      const asset=await env.ASSETS.fetch(request);
      // Newly published API content remains usable, but never substitutes stale generated HTML.
      if(asset.status===404) return shell(request,env,200);
      return asset;
    } catch(error) {console.error('SEO_ROUTE_FAILURE',stage,error?.name || 'UnknownError');return shell(request,env,503);}
  },
};
