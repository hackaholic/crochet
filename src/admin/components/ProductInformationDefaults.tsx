import {useEffect,useState} from 'react';
import {getProductDefaults,saveProductDefaults} from '../services/catalogue';
import {informationValues,validInformation,type ProductInformation} from '../../lib/products/information';
import ProductInformationFields from './ProductInformationFields';
import {actionClass} from './CatalogueFields';
export default function ProductInformationDefaults(){
 const [value,setValue]=useState<ProductInformation>();const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [notice,setNotice]=useState('');const [retry,setRetry]=useState(0);
 useEffect(()=>{let active=true;getProductDefaults().then(v=>{if(active){setValue(informationValues(v));setError('');}}).catch(()=>{if(active)setError('Defaults could not be loaded.');});return()=>{active=false;};},[retry]);
 return <section aria-label="Product information defaults" className="rounded-xl border border-[#E8E0D8] bg-white p-5 space-y-4"><h2 className="font-serif text-xl">New product defaults</h2><p className="text-sm">These values prefill new products only. Existing products keep their saved details. Verify materials, dimensions and delivery claims for each listing.</p>
 {value?<form className="space-y-4" onSubmit={async e=>{e.preventDefault();if(busy||!validInformation(value))return;setBusy(true);setError('');setNotice('');try{setValue(informationValues(await saveProductDefaults(value)));setNotice('Defaults saved. Existing products are unchanged.');}catch{setError('Defaults could not be saved. Your edits are preserved.');}finally{setBusy(false);}}}><ProductInformationFields value={value} onChange={setValue} disabled={busy}/><button className={actionClass} disabled={busy}>{busy?'Saving…':'Save defaults'}</button></form>:error?<button className="underline" onClick={()=>setRetry(x=>x+1)}>Retry defaults</button>:<p role="status">Loading defaults…</p>}
 {error&&<p role="alert">{error}</p>}{notice&&<p role="status">{notice}</p>}</section>;
}
