import { Link } from 'react-router';
import { useEffect, useState } from 'react';
import { accountApi, type OrderOut } from '../../lib/api/orders';
export default function OrderItems({orderNumber}: {orderNumber:string}) {
  const [attempt,setAttempt] = useState(0);
  const [order,setOrder] = useState<OrderOut>();
  const [error,setError] = useState(false);
  useEffect(()=>{let active=true;setOrder(undefined);setError(false);accountApi.order(orderNumber).then(value=>{if(active)setOrder(value);}).catch(()=>{if(active)setError(true);});return()=>{active=false;};},[orderNumber,attempt]);
  return <section aria-label="Ordered items" className="rounded-2xl border bg-white p-5"><h2 className="font-serif text-xl">Ordered items</h2>{error ? <div><p role="alert">Order items could not be loaded.</p><button type="button" onClick={()=>setAttempt(value=>value+1)} className="underline">Retry order items</button></div> : !order ? <p role="status">Loading order items…</p> : !order.items?.length ? <p>No item details available.</p> : <div className="mt-3 overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-[#EFF6F0] text-[#305E46]"><tr>{['Product','Quantity','Total price'].map(label=><th key={label} scope="col" className="p-3 font-bold">{label}</th>)}</tr></thead><tbody>{order.items.map(item=><tr key={item.id} className="border-t hover:bg-[#FBF5E9]"><th scope="row" className="p-3 font-medium">{item.productSlug ? <Link to={`/products/${encodeURIComponent(item.productSlug)}`} className="flex items-center gap-3 text-[#C4622D] underline"><ItemPhoto url={item.productImage} name={item.productName}/>{item.productName}</Link> : <span className="flex items-center gap-3"><ItemPhoto url={item.productImage} name={item.productName}/>{item.productName}</span>}</th><td className="p-3">{item.quantity}</td><td className="whitespace-nowrap p-3">₹{item.lineTotal.toLocaleString('en-IN')}</td></tr>)}</tbody></table></div>}</section>;
}
function ItemPhoto({url,name}:{url?:string|null;name:string}) {
 const [failed,setFailed]=useState<string>();
 return url && /^https?:\/\//i.test(url) && failed!==url ? <img src={url} alt={name} width={48} height={48} loading="lazy" className="h-12 w-12 shrink-0 rounded-lg object-cover" onError={()=>setFailed(url)}/> : <span className="grid h-12 w-12 shrink-0 place-items-center rounded-lg bg-[#F5F0EA] text-center text-[10px]">No photo</span>;
}
