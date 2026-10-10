import { AccountRequestError } from '../../lib/api/validationErrors';
import { useState } from 'react';
import { accountProfileApi, type ProfileOut } from '../../lib/api/account';
import { normalizePhone, phoneError, textError } from './validation';

export default function ProfileEditor({ profile, onSaved }: { profile: ProfileOut; onSaved: (profile: ProfileOut) => void }) {
  const [name, setName] = useState(profile.name ?? '');
  const [phone, setPhone] = useState(profile.phone ?? '');
  const [errors, setErrors] = useState({ name: '', phone: '' });
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const dirty = name !== (profile.name ?? '') || phone !== (profile.phone ?? '');
  async function save(event: React.FormEvent) {
    event.preventDefault();
    if (busy) return;
    const nextErrors = { name: textError(name, 2, 100), phone: phoneError(phone, true) };
    setErrors(nextErrors); setMessage('');
    if (Object.values(nextErrors).some(Boolean)) return;
    setBusy(true);
    try {
      const saved = await accountProfileApi.updateProfile({ name: name.trim(), phone: normalizePhone(phone) || null });
      onSaved(saved); setName(saved.name ?? ''); setPhone(saved.phone ?? ''); setMessage('Profile saved.');
    } catch (error) { if (error instanceof AccountRequestError) setErrors({name:error.fields.name ?? '',phone:error.fields.phone ?? ''}); setMessage(error instanceof Error && ['400','409'].includes(error.message) ? 'This phone number could not be saved. Please use another contact number.' : 'We could not save your profile. Please check your details and try again.'); }
    finally { setBusy(false); }
  }
  return <section id="account-profile" aria-label="Profile" className="rounded-2xl border border-[#EDE4D0] bg-white p-6">
    <h2 className="text-xl font-semibold">Profile</h2><p className="mt-1 text-sm text-[#8B6B4A]">Keep your delivery contact details up to date.</p>
    <form onSubmit={save} noValidate className="mt-5 grid gap-4">
      <label>Name<input aria-label="Name" value={name} onChange={e => setName(e.target.value)} maxLength={100} autoComplete="name" aria-invalid={!!errors.name} aria-describedby="profile-name-error" className="mt-1 block w-full rounded-lg border p-3" /><span id="profile-name-error" className="text-sm text-red-700">{errors.name}</span></label>
      <label>Email<input type="email" value={profile.email ?? ''} readOnly aria-describedby="profile-email-note" className="mt-1 block w-full rounded-lg border bg-[#FAF7F2] p-3" /></label>
      <p id="profile-email-note" className="text-sm text-[#8B6B4A]">Your email is used to sign in. Changing it requires verification.</p>
      <label>Phone<input aria-label="Phone" type="tel" value={phone} onChange={e => setPhone(e.target.value)} maxLength={20} autoComplete="tel" aria-invalid={!!errors.phone} aria-describedby="profile-phone-error" className="mt-1 block w-full rounded-lg border p-3" /><span id="profile-phone-error" className="text-sm text-red-700">{errors.phone}</span></label>
      <p className="text-sm text-[#8B6B4A]">Phone is for delivery contact. Existing addresses and orders keep their original details.</p>
      <div className="flex gap-3"><button disabled={busy || !dirty} className="rounded-full bg-[#C4622D] px-5 py-2.5 text-white disabled:opacity-50">{busy ? 'Saving…' : 'Save profile'}</button><button type="button" disabled={busy} onClick={() => {setName(profile.name ?? ''); setPhone(profile.phone ?? ''); setErrors({name:'',phone:''}); setMessage('');}} className="rounded-full border px-5 py-2.5">Cancel changes</button></div>
      {message && <p role="status">{message}</p>}
    </form>
  </section>;
}
