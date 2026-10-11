import { useEffect, useState } from 'react';
import { BRAND_LIMITS, brandDraft, getBrandSettings, saveBrandSettings, validateBrand, type BrandDraft } from '../services/brandSettings';
import { TableSkeleton } from '../components/AdminShared';
const fields: {key:keyof BrandDraft;label:string;optional?:boolean}[] = [
  {key:'name',label:'Store name'}, {key:'ownerName',label:'Owner name'},
  {key:'instagramUrl',label:'Instagram link',optional:true}, {key:'whatsappUrl',label:'WhatsApp link',optional:true},
];
export default function SettingsPage() {
  const [draft,setDraft]=useState<BrandDraft|null>(null), [saved,setSaved]=useState<BrandDraft|null>(null);
  const [loading,setLoading]=useState(true),[saving,setSaving]=useState(false),[attempt,setAttempt]=useState(0);
  const [error,setError]=useState(''),[success,setSuccess]=useState(false),[errors,setErrors]=useState<ReturnType<typeof validateBrand>>({});
  useEffect(()=>{let active=true;setLoading(true);setError('');getBrandSettings().then(data=>{if(active){const next=brandDraft(data);setDraft(next);setSaved(next);}}).catch(()=>{if(active)setError('Store settings could not be loaded.');}).finally(()=>{if(active)setLoading(false);});return()=>{active=false;};},[attempt]);
  const dirty=draft && saved && fields.some(({key})=>draft[key]!==saved[key]);
  async function submit(event:React.FormEvent) {
    event.preventDefault();if(!draft || saving)return;setSuccess(false);setError('');const invalid=validateBrand(draft);setErrors(invalid);if(Object.keys(invalid).length)return;
    setSaving(true);try {const next=brandDraft(await saveBrandSettings(draft));setDraft(next);setSaved(next);setSuccess(true);}catch{setError('Settings could not be saved. Your changes are kept; try again.');}finally{setSaving(false);}
  }
  return <section className="max-w-3xl rounded-xl border border-[#E8E0D8] bg-white p-5 sm:p-6" aria-labelledby="brand-settings-title">
    <h2 id="brand-settings-title" className="font-semibold text-[#1A1108]">Store profile</h2><p className="mt-1 text-sm text-[#6B5B4E]">Manage the brand details shown on your storefront.</p>
    {error && <div role="alert" className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm">{error}{!draft && <button type="button" className="ml-2 underline" onClick={()=>setAttempt(v=>v+1)}>Retry settings</button>}</div>}
    {success && <p role="status" className="mt-4 text-sm text-emerald-700">Store settings saved.</p>}
    {loading ? <TableSkeleton rows={4} cols={1}/> : draft && <form onSubmit={submit} noValidate className="mt-5 space-y-4">
      {fields.map(({key,label,optional})=><div key={key}><label htmlFor={`brand-${key}`} className="mb-1 block text-sm font-medium">{label}{optional && <span className="font-normal text-[#6B5B4E]"> (optional)</span>}</label><input id={`brand-${key}`} type={optional?'url':'text'} value={draft[key]} disabled={saving} aria-invalid={!!errors[key]} aria-describedby={errors[key]?`brand-${key}-error`:undefined} maxLength={optional?BRAND_LIMITS.url:BRAND_LIMITS.name} className="w-full rounded-lg border border-[#E8E0D8] px-3 py-2 text-sm focus:outline-2 focus:outline-[#C4622D]" onChange={event=>{setDraft({...draft,[key]:event.target.value});setErrors({...errors,[key]:undefined});setSuccess(false);}}/>{errors[key] && <p id={`brand-${key}-error`} className="mt-1 text-xs text-red-700">{errors[key]}</p>}</div>)}
      <div className="flex flex-wrap gap-3"><button disabled={saving || !dirty} className="rounded-lg bg-[#C4622D] px-4 py-2 text-sm text-white disabled:opacity-50">{saving?'Saving…':'Save settings'}</button><button type="button" disabled={saving || !dirty} className="rounded-lg border px-4 py-2 text-sm disabled:opacity-50" onClick={()=>{setDraft(saved);setErrors({});setError('');setSuccess(false);}}>Discard changes</button></div>
    </form>}
  </section>;
}
