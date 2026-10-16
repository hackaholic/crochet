import fs from 'node:fs/promises';
import path from 'node:path';
import {apiBase} from './prerender-routes.mjs';
import {resourcePolicy} from './seo-resources.mjs';
import {serializePublicData} from './prerender.mjs';
export async function writeRoutingPolicy(root,mode,environment) {
  const policy=resourcePolicy(mode,environment);
  const comingSoon=environment.VITE_LAUNCH_MODE==='coming-soon';
  const base=environment.SEO_EDGE_API_BASE_URL || environment.VITE_API_BASE_URL;
  if(!comingSoon && !base) throw new Error('Full storefront requires SEO_EDGE_API_BASE_URL or public VITE_API_BASE_URL');
  if(!policy.origin) throw new Error('Storefront requires SEO_PUBLIC_ORIGIN');
  const result={origin:policy.origin,indexing:policy.indexing,comingSoon,...(base ? {apiBase:apiBase(base)}:{})};
  if(mode==='production' && result.apiBase && !result.apiBase.startsWith('https://')) throw new Error('Production routing API requires HTTPS');
  const dist=path.join(root,'dist');
  await fs.writeFile(path.join(dist,'routing-policy.json'),serializePublicData(result));
  const index=path.join(dist,'index.html');
  const template=await fs.readFile(index,'utf8');
  const html=template.replace('</head>',`<script id="storefront-policy" type="application/json">${serializePublicData(result)}</script></head>`);
  await fs.writeFile(index,html);await fs.writeFile(path.join(dist,'app-shell.html'),html.replace('index,follow','noindex,nofollow'));
  return result;
}
