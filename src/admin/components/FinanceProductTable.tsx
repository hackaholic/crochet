import AdminTable from './AdminTable';
import { useEffect, useState } from 'react';
import type { ProductSales } from '../services/financeAnalytics';
import { inr } from './AdminShared';
import FinanceTableHeader from './FinanceTableHeader';
function ProductPhoto({url,name}:{url:string|null;name:string}) {
  const [failed,setFailed]=useState(false);
  useEffect(()=>setFailed(false),[url]);
  return url && !failed ? <img src={url} alt={name} loading="lazy" className="h-12 w-12 shrink-0 rounded object-cover" onError={()=>setFailed(true)}/> : <span className="text-xs text-[#6B5B4E]">No photo</span>;
}
export default function FinanceProductTable({data,onSelectProduct}:{data:ProductSales;onSelectProduct?:(id:number)=>void}) {
  if(!data.items.length) return <p>No qualifying sales in this period.</p>;
  return <div className="finance-table-scroll"><AdminTable className="w-full text-left text-sm"><FinanceTableHeader columns={['Rank','Product','Units','Revenue','Orders']}/><tbody>{data.items.map((product,index)=><tr key={`${product.productId}-${product.sku}-${product.variantName}-${index}`} className="border-t border-[#F0EAE3]">
    <td className="p-2">{index+1}</td><th scope="row" className="text-left font-normal">{product.productId !== null && onSelectProduct ? <button type="button" className="admin-entity-link flex w-full min-w-40 items-center gap-3 p-2" onClick={()=>onSelectProduct(product.productId!)}><ProductPhoto url={product.imageUrl} name={product.productName}/><span className="break-words"><span className="block">{product.productName}</span><span className="block text-xs text-[#6B5B4E]">{product.sku || 'SKU unavailable'}{product.variantName && ` · ${product.variantName}`}</span></span></button> : <div className="flex min-w-40 items-center gap-3 p-2"><ProductPhoto url={product.imageUrl} name={product.productName}/><span className="break-words"><span className="block">{product.productName}</span><span className="block text-xs text-[#6B5B4E]">{product.sku || 'SKU unavailable'}{product.variantName && ` · ${product.variantName}`}</span></span></div>}</th><td className="p-2">{product.unitsSold}</td><td className="whitespace-nowrap p-2">{inr(product.productRevenuePaise/100)}</td><td className="p-2">{product.distinctOrders}</td>
  </tr>)}</tbody></AdminTable></div>;
}
