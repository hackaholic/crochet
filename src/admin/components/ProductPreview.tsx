import { useEffect,useState } from 'react';
import { getProduct,type CatalogueProduct } from '../services/catalogue';
import ProductThumbnail from './ProductThumbnail';
import { inr } from './AdminShared';
export default function ProductPreview({id,onEdit}:{id:number;onEdit:(id:number)=>void}) {
  const [product,setProduct]=useState<CatalogueProduct>();const [error,setError]=useState(false);const [attempt,setAttempt]=useState(0);
  useEffect(()=>{let active=true;setProduct(undefined);setError(false);getProduct(id).then(p=>{if(active)setProduct(p);}).catch(()=>{if(active)setError(true);});return()=>{active=false;};},[id,attempt]);
  if(error)return <p role="alert">Product unavailable. <button className="underline" onClick={()=>setAttempt(x=>x+1)}>Retry product</button></p>;
  if(!product)return <p role="status">Loading product…</p>;
  return <div className="space-y-4"><div className="flex items-center gap-4"><ProductThumbnail product={product}/><div><h3 className="font-semibold">{product.name}</h3><p>{product.status} · From {inr(product.minPrice)}</p></div></div><p className="whitespace-pre-wrap">{product.description || product.shortDescription || 'No description provided.'}</p><p>{product.categoryNames.join(', ')}</p><div className="flex flex-wrap gap-3"><button className="rounded bg-[#C4622D] px-4 py-2 text-white" onClick={()=>onEdit(id)}>Edit product</button>{product.slug && <a className="rounded border px-4 py-2" href={`/products/${encodeURIComponent(product.slug)}`} target="_blank" rel="noopener noreferrer">View storefront product</a>}</div></div>;
}
