import {useEffect,useId,useState} from 'react';
import {getProductInformation} from '../lib/api/catalogue';
import {informationFields,type ProductInformation} from '../lib/products/information';
export default function ProductInformationAccordion({productId}:{productId:string|number}){
 const id=useId();const [value,setValue]=useState<ProductInformation>();const [error,setError]=useState(false);const [retry,setRetry]=useState(0);const [open,setOpen]=useState<string|null>('handmadeDetails');
 useEffect(()=>{const controller=new AbortController();setValue(undefined);setError(false);setOpen('handmadeDetails');getProductInformation(productId,controller.signal).then(v=>{if(!controller.signal.aborted)setValue(v);}).catch(()=>{if(!controller.signal.aborted)setError(true);});return()=>controller.abort();},[productId,retry]);
 if(error)return <div role="status" className="text-sm"><p>Product details could not be loaded.</p><button className="underline" onClick={()=>setRetry(x=>x+1)}>Retry product information</button></div>;
 if(!value)return <p role="status" className="text-sm">Loading product information…</p>;
 return <div>{informationFields.filter(([key])=>value[key]?.trim()).map(([key,label])=><div key={key} className="border-b border-[#EDE4D0]"><button type="button" aria-expanded={open===key} aria-controls={`${id}-${key}`} onClick={()=>setOpen(open===key?null:key)} className="flex items-center justify-between w-full py-4 text-left"><span className="font-semibold text-[#2C1810] text-sm">{label}</span><span aria-hidden="true" className="text-[#8B6B4A] text-xl">{open===key?'−':'+'}</span></button><p id={`${id}-${key}`} hidden={open!==key} className="pb-4 text-sm text-[#5C3D2E] leading-relaxed whitespace-pre-line break-words">{value[key]}</p></div>)}</div>;
}
