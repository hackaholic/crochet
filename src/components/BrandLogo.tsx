import { useEffect, useState } from 'react';
import { getStorefrontContent } from '../lib/api/storefront';
let brandRequest: ReturnType<typeof getStorefrontContent> | undefined;
export default function BrandLogo({size=40}:{size?:number}) {
 const [url,setUrl]=useState<string>();
 const [failed,setFailed]=useState(false);
 useEffect(()=>{let active=true;brandRequest ??= getStorefrontContent();brandRequest.then(content=>{if(active && /^https?:\/\//i.test(content.brand.logoUrl||''))setUrl(content.brand.logoUrl!);}).catch(()=>{brandRequest=undefined;});return()=>{active=false;};},[]);
 return url && !failed ? <img src={url} alt="Sulocraft logo" width={size*2.5} height={size*1.4} style={{width:size*2.5,height:size*1.4}} className="shrink-0 rounded object-cover" onError={()=>setFailed(true)}/> : <span aria-label="Sulocraft logo" className="font-serif font-bold">S</span>;
}
