import { useEffect, useState } from 'react';
import { accountApi, type OrderOut } from '../../lib/api/orders';
export default function OrderItems({orderNumber}: {orderNumber:string}) {
  const [attempt,setAttempt] = useState(0);
  const [order,setOrder] = useState<OrderOut>();
  const [error,setError] = useState(false);
  useEffect(()=>{let active=true;setOrder(undefined);setError(false);accountApi.order(orderNumber).then(value=>{if(active)setOrder(value);}).catch(()=>{if(active)setError(true);});return()=>{active=false;};},[orderNumber,attempt]);
  return <section aria-label="Ordered items" className="rounded-2xl border bg-white p-5"><h2 className="font-serif text-xl">Ordered items</h2>{error ? <div><p role="alert">Order items could not be loaded.</p><button type="button" onClick={()=>setAttempt(value=>value+1)} className="underline">Retry order items</button></div> : !order ? <p role="status">Loading order items…</p> : !order.items?.length ? <p>No item details available.</p> : <ul className="mt-3 space-y-3">{order.items.map(item=><li key={item.id} className="flex justify-between gap-3"><span>{item.productName} × {item.quantity}</span><span>₹{item.lineTotal.toLocaleString('en-IN')}</span></li>)}</ul>}</section>;
}
