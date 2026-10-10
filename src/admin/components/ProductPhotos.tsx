import { useState } from 'react';
import { uploadPhoto } from '../services/catalogue';
import { controlClass } from './CatalogueFields';
export default function ProductPhotos({ primary, gallery, urls, onChange, onBusy }: {
  primary: string; gallery: string[]; urls: Record<string, string>; onChange: (primary: string, gallery: string[]) => void; onBusy: (busy: boolean) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [uploadedUrls, setUploadedUrls] = useState<Record<string, string>>({});
  const [error, setError] = useState('');
  const photos = [...new Set([primary, ...gallery].filter(Boolean))];
  async function upload(file: File) {
    setBusy(true); onBusy(true); setError('');
    try { const photo = await uploadPhoto(file); setUploadedUrls(current => ({ ...current, [photo.key]: photo.url })); onChange(primary || photo.key, [...new Set([...gallery, photo.key])]); }
    catch { setError('Photo upload failed. Your existing photos are unchanged. Try again.'); }
    finally { setBusy(false); onBusy(false); }
  }
  return <section aria-label="Product photos" className="space-y-3">
    <label className="block text-sm font-medium">Upload a photo<input className={controlClass} type="file" accept="image/jpeg,image/png,image/webp" disabled={busy} onChange={event => {
      const file = event.target.files?.[0]; if (file) void upload(file); event.target.value = '';
    }} /></label>
    {busy && <p role="status">Uploading photo…</p>}{error && <p role="alert">{error}</p>}
    <div className="flex flex-wrap gap-3">{photos.map(url => <div key={url} className="w-28 space-y-1">
      <img src={uploadedUrls[url] || urls[url] || (/^https?:\/\//.test(url) ? url : undefined)} alt="Product photo" className="aspect-square w-full rounded-lg object-cover" />
      <button type="button" className="text-xs underline" disabled={busy || url === primary} onClick={() => onChange(url, photos)}>{url === primary ? 'Primary photo' : 'Make primary'}</button>
      <button type="button" className="block text-xs underline" disabled={busy} onClick={() => { const next = photos.filter(photo => photo !== url); onChange(url === primary ? next[0] || '' : primary, next); }}>Remove photo</button>
    </div>)}</div>
  </section>;
}
