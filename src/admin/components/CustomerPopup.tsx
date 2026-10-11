import { useEffect,useState } from 'react';
import { getCustomers } from '../services/customers';
import CustomerProfile from './CustomerProfile';
import AdminPreviewDialog from './AdminPreviewDialog';
export interface CustomerPreviewInput {id?:number;name?:string;email?:string;phone?:string}
export default function CustomerPopup({customer,onClose,onSelectOrder}:{customer:CustomerPreviewInput;onClose:()=>void;onSelectOrder:(id:string)=>void}) {
  const [id,setId]=useState(customer.id);const [loading,setLoading]=useState(!customer.id && !!customer.email);const [error,setError]=useState(false);const [attempt,setAttempt]=useState(0);
  useEffect(()=>{const controller=new AbortController();setId(customer.id);setError(false);
    if(customer.id || !customer.email){setLoading(false);return()=>controller.abort();}
    setLoading(true);const email=customer.email.trim().toLowerCase();
    getCustomers(email,1,controller.signal).then(data=>{if(!controller.signal.aborted){const matches=data.items.filter(c=>c.email?.trim().toLowerCase()===email);if(matches.length===1 && data.total<=data.pageSize)setId(matches[0].id);}}).catch(()=>{if(!controller.signal.aborted)setError(true);}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});return()=>controller.abort();
  },[customer.id,customer.email,attempt]);
  return <AdminPreviewDialog title="Customer profile" onClose={onClose}>{loading?<p role="status">Loading customer…</p>:error?<p role="alert">Customer unavailable. <button className="underline" onClick={()=>setAttempt(x=>x+1)}>Retry customer</button></p>:id!==undefined?<CustomerProfile id={id} onBack={onClose} onSelectOrder={onSelectOrder} hideBack/>:<div className="space-y-3"><h3>{customer.name || 'Guest customer'}</h3><p>{customer.email || 'Email not provided'}</p><p>{customer.phone || 'Phone not provided'}</p><p>No uniquely linked customer account found. These are the recorded order contact details.</p></div>}</AdminPreviewDialog>;
}
