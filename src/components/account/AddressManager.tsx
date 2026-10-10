import { AccountRequestError } from '../../lib/api/validationErrors';
import { useState } from 'react';
import { accountApi, type AddressCreate, type AddressOut } from '../../lib/api/orders';
import { normalizePhone, phoneError, pinError, textError } from './validation';
const blank: AddressCreate = {name:'',phone:'',line1:'',line2:'',city:'',state:'',postalCode:'',country:'IN'};
const fields = [ ['name','Recipient name',2,100], ['phone','Phone',0,20], ['line1','Address line',3,255], ['line2','Address line 2 (optional)',0,255], ['city','City',2,100], ['state','State',2,100], ['postalCode','PIN code',0,6] ] as const;

export default function AddressManager({ addresses, onChanged }: { addresses: AddressOut[]; onChanged: (addresses: AddressOut[]) => void }) {
  const [draft, setDraft] = useState<AddressCreate>(blank);
  const [editing, setEditing] = useState<number>();
  const [errors, setErrors] = useState<Record<string,string>>({});
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [deleting, setDeleting] = useState<number>();
  function reset() { setDraft(blank); setEditing(undefined); setErrors({}); }
  async function mutate(action: () => Promise<unknown>, success: string, clear = false) {
    if (busy) return;
    setBusy(true); setMessage('');
    try { await action(); const fresh = await accountApi.addresses(); onChanged(fresh); if(clear) reset(); setDeleting(undefined); setMessage(success); }
    catch (error) { if(error instanceof AccountRequestError) setErrors(error.fields); setMessage('We could not complete this change. Refresh your addresses before trying again.'); }
    finally { setBusy(false); }
  }
  function save(event: React.FormEvent) {
    event.preventDefault();
    const next: Record<string,string> = {};
    for(const [key,,min,max] of fields) {
      const value = draft[key] ?? '';
      next[key] = key === 'phone' ? phoneError(value) : key === 'postalCode' ? pinError(value) : key === 'line2' && !value.trim() ? '' : textError(value,min,max);
    }
    setErrors(next); if(Object.values(next).some(Boolean)) return;
    const payload = {...draft, name:draft.name.trim(), phone:normalizePhone(draft.phone), line1:draft.line1.trim(),line2:draft.line2?.trim(),city:draft.city.trim(),state:draft.state.trim(),postalCode:draft.postalCode.replace(/\s+/g,'')};
    void mutate(() => editing === undefined ? accountApi.createAddress(payload) : accountApi.updateAddress(editing,payload), 'Address saved.',true);
  }
  return <section id="account-addresses" aria-label="Addresses" className="rounded-2xl border border-[#EDE4D0] bg-white p-6">
    <h2 className="text-xl font-semibold">Saved addresses</h2>
    {!addresses.length && <p className="mt-3">No saved addresses yet.</p>}
    <div className="mt-4 grid gap-4 md:grid-cols-2">{addresses.map(item => <article key={item.id} className="rounded-xl border p-4 [overflow-wrap:anywhere]">
      <p className="font-semibold">{item.name}{item.isDefault && ' — Default'}</p><p>{item.line1}{item.line2 && `, ${item.line2}`}, {item.city}, {item.state} {item.postalCode}</p><p>{item.phone}</p>
      <div className="mt-3 flex flex-wrap gap-3"><button type="button" disabled={busy} onClick={() => {setDraft({name:item.name,phone:item.phone,line1:item.line1,line2:item.line2 ?? '',city:item.city,state:item.state,postalCode:item.postalCode,country:item.country ?? 'IN'});setEditing(item.id);setErrors({});setMessage('');}} aria-label={`Edit address for ${item.name}`} className="underline">Edit</button>
      {!item.isDefault && <button type="button" disabled={busy} onClick={() => void mutate(() => accountApi.setDefaultAddress(item.id),'Default address updated.')} aria-label={`Make address for ${item.name} default`} className="underline">Make default</button>}
      <button type="button" disabled={busy} onClick={() => setDeleting(item.id)} aria-label={`Delete address for ${item.name}`} className="underline">Delete</button></div>
      {deleting === item.id && <div role="group" aria-label="Confirm address deletion" className="mt-3"><p>Remove this saved address? Existing orders keep their delivery details.</p><button type="button" disabled={busy} onClick={() => void mutate(() => accountApi.deleteAddress(item.id),'Address removed.',editing === item.id)} className="mr-4 underline">Confirm deletion</button><button type="button" disabled={busy} onClick={() => setDeleting(undefined)}>Keep address</button></div>}
    </article>)}</div>
    <h3 className="mt-6 font-semibold">{editing === undefined ? 'Add address' : 'Edit address'}</h3>
    <form onSubmit={save} noValidate className="mt-3 grid gap-3 md:grid-cols-2">{fields.map(([key,label,,max]) => <label key={key}>{label}<input aria-label={label} value={draft[key] ?? ''} type={key === 'phone' ? 'tel' : 'text'} inputMode={key === 'postalCode' ? 'numeric' : undefined} maxLength={max} onChange={e => setDraft(current=>({...current,[key]:e.target.value}))} aria-invalid={!!errors[key]} aria-describedby={`address-error-${key}`} className="mt-1 block w-full rounded-lg border p-3" /><span id={`address-error-${key}`} className="text-sm text-red-700">{errors[key]}</span></label>)}
    <div className="flex gap-3 md:col-span-2"><button disabled={busy} className="rounded-full bg-[#C4622D] px-5 py-2.5 text-white disabled:opacity-50">{busy ? 'Saving…' : 'Save address'}</button><button type="button" disabled={busy} onClick={reset}>Cancel changes</button></div></form>
    {message && <p role="status" className="mt-3">{message}</p>}
    <button type="button" disabled={busy} onClick={() => void mutate(async () => {},'Addresses refreshed.')} className="mt-3 underline">Refresh addresses</button>
  </section>;
}
