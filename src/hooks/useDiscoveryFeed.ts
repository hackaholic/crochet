import { discoveryLimits } from '../config/discovery';
import { useCallback, useEffect, useRef, useState } from 'react';
import { getProductDiscovery, type DiscoveryContext, type DiscoverySection } from '../lib/api/productDiscovery';

/** One bounded request at a time; append unique API products in server order. */
export function useDiscoveryFeed(open: boolean, context: DiscoveryContext) {
  const [compatibility,setCompatibility]=useState(false);
  const [sections,setSections]=useState<DiscoverySection[]>([]);
  const [loading,setLoading]=useState(false);
  const [failed,setFailed]=useState(false);
  const [hasMore,setHasMore]=useState(false);
  const pages=useRef(0);
  const cursor=useRef<string|null>(null);
  const seenCursors=useRef(new Set<string>());
  const controller=useRef<AbortController|null>(null);
  const active=useRef(false);
  const sentinel=useRef<HTMLDivElement|null>(null);
  const load=useCallback(async()=>{
    if (!active.current || controller.current || pages.current >= discoveryLimits.maxPages) return;
    const request=new AbortController();controller.current=request;
    const timeout=window.setTimeout(()=>request.abort(),discoveryLimits.timeoutMs);
    setLoading(true);setFailed(false);
    try {
      const page=await getProductDiscovery(context,cursor.current,request.signal);
      if (!active.current || request.signal.aborted || controller.current !== request) return;
      setCompatibility(page.compatibility === true);
      setSections(previous=>{
        const result=previous.map(s=>({...s,products:[...s.products]}));
        const seen=new Set(result.flatMap(s=>s.products.map(p=>p.id)));
        for (const row of page.sections) {
          const products=row.products.filter(p=>{if(seen.has(p.id))return false;seen.add(p.id);return true;});
          const existing=result.find(s=>s.id===row.id);
          if(existing) existing.products.push(...products); else result.push({...row,products});
        }
        return result;
      });
      pages.current++;
      const next=page.nextCursor;
      const advances=pages.current < discoveryLimits.maxPages && next !== null && next !== cursor.current && !seenCursors.current.has(next);
      if (next) seenCursors.current.add(next);
      cursor.current=next;setHasMore(advances);
    } catch {
      if(active.current && controller.current===request) setFailed(true);
    } finally {
      window.clearTimeout(timeout);
      if(controller.current===request){controller.current=null;if(active.current)setLoading(false);}
    }
  },[context]);
  useEffect(()=>{
    active.current=open;pages.current=0;cursor.current=null;seenCursors.current.clear();setSections([]);setCompatibility(false);setHasMore(false);setFailed(false);setLoading(false);
    if(open) void load();
    return ()=>{active.current=false;controller.current?.abort();controller.current=null;};
  },[open,load]);
  useEffect(()=>{
    if(!open || !hasMore || loading || failed || !sentinel.current || typeof IntersectionObserver==='undefined')return;
    const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting))void load();},{rootMargin:'160px'});
    observer.observe(sentinel.current);return ()=>observer.disconnect();
  },[open,hasMore,loading,failed,load]);
  return {sections,compatibility,loading,failed,hasMore,load,sentinel};
}
