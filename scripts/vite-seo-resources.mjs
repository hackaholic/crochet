import {safePath,isPrivatePath,routeDecision,loadRouteMetadata} from '../src/lib/seo/urlPolicy.mjs';
import { resourcePolicy, sitemapFiles } from './seo-resources.mjs';

/** Local HTTP delivery uses the same non-indexing policy as the asset build. */
export function localSeoResources(environment) {
  return {
    name: 'sulocraft-local-seo-resources',
    configureServer(server) {
      const policy = resourcePolicy('preprod', environment);
      server.middlewares.use((request, response, next) => {
        response.setHeader('X-Robots-Tag', 'noindex, nofollow');
        const url = new URL(request.url, 'http://local.invalid');
        const pathname = url.pathname;
        if (!['/robots.txt', '/sitemap.xml'].includes(pathname)) {
          if (pathname.startsWith('/api/') || pathname.includes('.') || pathname.startsWith('/@') || isPrivatePath(pathname.toLowerCase())) return next();
          let normalized;try { normalized=safePath(pathname); } catch { response.statusCode=404; return next(); }
          const api = environment.VITE_LOCAL_API_PROXY_TARGET || 'http://localhost:8000';
          loadRouteMetadata(`${api.replace(/\/$/,'')}/api/v1`,normalized+url.search).then(metadata => {
            const decision=routeDecision(url,metadata);
            if(decision.status===301) {response.statusCode=301;response.setHeader('Location',decision.location);return response.end();}
            if(decision.status!==200) {
              const writeHead=response.writeHead;
              response.writeHead=function(_status,...args) {return writeHead.call(this,decision.status,...args);};
              response.statusCode=decision.status;
            }
            next();
          }).catch(()=>{const writeHead=response.writeHead;response.writeHead=function(_status,...args){return writeHead.call(this,503,...args);};response.statusCode=503;next();});
          return;
        }
        if (!['GET', 'HEAD'].includes(request.method)) {
          response.statusCode = 405; response.setHeader('Allow', 'GET, HEAD'); return response.end();
        }
        const sitemap = pathname === '/sitemap.xml';
        response.setHeader('Content-Type', sitemap ? 'application/xml; charset=utf-8' : 'text/plain; charset=utf-8');
        response.end(request.method === 'HEAD' ? undefined : sitemap ? sitemapFiles(undefined, policy).get('sitemap.xml') : 'User-agent: *\nAllow: /\n');
      });
    },
  };
}
