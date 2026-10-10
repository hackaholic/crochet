import { useEffect, useState } from 'react';
import { createTag, getTags, saveProduct, type CatalogueProduct, type ProductDraft, type TaxonomyOption, type VariantDraft } from '../services/catalogue';
import { actionClass, controlClass, Field, TaxonomySelect } from './CatalogueFields';
import ProductPhotos from './ProductPhotos';
import VariantEditor, { VariantFields } from './VariantEditor';
export default function ProductEditor({ product, categories, onSaved, onClose }: {
  product?: CatalogueProduct; categories: TaxonomyOption[]; onSaved: (product: CatalogueProduct) => void; onClose: () => void;
}) {
  const [draft, setDraft] = useState<ProductDraft>({ name: product?.name || '', description: product?.description || '', primaryImage: product?.primaryImage || '', galleryImages: product?.galleryImages || [], primaryCategoryId: product?.primaryCategoryId ?? product?.categoryIds[0], categoryIds: product?.categoryIds || [], tagIds: product?.tagIds || [] });
  const [variant, setVariant] = useState<VariantDraft>({ sku: '', name: '', price: 0, stockQuantity: 0 });
  const [tags, setTags] = useState<TaxonomyOption[]>([]);
  const [tagsState, setTagsState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [newTag, setNewTag] = useState('');
  const [tagBusy, setTagBusy] = useState(false);
  const [busy, setBusy] = useState(false);
  const [photoBusy, setPhotoBusy] = useState(false);
  const [error, setError] = useState('');
  const [tagRetry, setTagRetry] = useState(0);
  useEffect(() => {
    let active = true; setTagsState('loading');
    getTags().then(data => { if (active) { setTags(data); setTagsState('ready'); } }).catch(() => { if (active) setTagsState('error'); });
    return () => { active = false; };
  }, [tagRetry]);
  const disabled = busy || photoBusy || tagBusy;
  return <section className="rounded-xl border border-[#E8E0D8] bg-white p-5" aria-label="Product editor">
    <div className="mb-5 flex items-center justify-between"><h2 className="font-serif text-xl">{product ? 'Edit product' : 'Add product'}</h2><button type="button" disabled={disabled} onClick={onClose} className="text-sm underline">Back to catalogue</button></div>
    <form className="space-y-5" onSubmit={async event => {
      event.preventDefault(); if (disabled) return;
      if (!draft.categoryIds.length) { setError('Select at least one product category before saving.'); return; }
      if (!draft.primaryImage) { setError('Upload a primary product photo before saving.'); return; }
      setBusy(true); setError('');
      try { const saved = await saveProduct(draft, product?.id, product ? undefined : [variant]); onSaved(saved); }
      catch { setError('Product could not be saved. Your changes are still here. Check the fields and try again.'); }
      finally { setBusy(false); }
    }}>
      <fieldset disabled={disabled} className="space-y-4">
        <Field label="Product name"><input required minLength={2} maxLength={200} className={controlClass} value={draft.name} onChange={e => setDraft({ ...draft, name: e.target.value })} /></Field>
        <Field label="Description"><textarea className={controlClass} rows={4} value={draft.description} onChange={e => setDraft({ ...draft, description: e.target.value })} /></Field>
        <TaxonomySelect title="Categories" options={categories} selected={draft.categoryIds} onChange={categoryIds => setDraft({ ...draft, categoryIds, primaryCategoryId: categoryIds.includes(draft.primaryCategoryId ?? -1) ? draft.primaryCategoryId : categoryIds[0] })} />
        <Field label="Primary category"><select className={controlClass} value={draft.primaryCategoryId ?? ''} onChange={e => setDraft({ ...draft, primaryCategoryId: Number(e.target.value) })}><option value="">Select a category</option>{categories.filter(c => draft.categoryIds.includes(c.id)).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></Field>
        {tagsState === 'ready' && <TaxonomySelect title="Tags" options={tags} selected={draft.tagIds} onChange={tagIds => setDraft({ ...draft, tagIds })} />}
        {tagsState === 'loading' && <p role="status">Loading tags…</p>}
      </fieldset>
      {tagsState === 'error' && <div className="text-sm" role="status"><p>Tag management is unavailable. Existing product tags will be preserved.</p><button type="button" onClick={() => setTagRetry(x => x + 1)} className="underline">Retry tags</button></div>}
      {tagsState === 'ready' && <div className="flex items-end gap-3"><Field label="New tag"><input className={controlClass} value={newTag} disabled={disabled} onChange={e => setNewTag(e.target.value)} /></Field><button type="button" className={actionClass} disabled={disabled || !newTag.trim()} onClick={async () => {
        setTagBusy(true); setError('');
        try { const tag = await createTag(newTag.trim()); setTags(current => [...current.filter(t => t.id !== tag.id), tag]); setDraft(current => ({ ...current, tagIds: [...new Set([...current.tagIds, tag.id])] })); setNewTag(''); }
        catch { setError('Tag could not be created. Try again.'); } finally { setTagBusy(false); }
      }}>Add tag</button></div>}
      <fieldset disabled={busy || tagBusy}><ProductPhotos primary={draft.primaryImage} gallery={draft.galleryImages} urls={{ ...(product ? Object.fromEntries(product.galleryImages.map((key, index) => [key, product.galleryImageUrls?.[index] || ''])) : {}), ...(product?.primaryImageUrl ? { [product.primaryImage]: product.primaryImageUrl } : {}) }} onBusy={setPhotoBusy} onChange={(primaryImage, galleryImages) => setDraft(current => ({ ...current, primaryImage, galleryImages }))} /></fieldset>
      {!product && <fieldset disabled={disabled}><legend className="mb-3 font-semibold">First variant</legend><VariantFields draft={variant} onChange={setVariant} /></fieldset>}
      {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
      <button className={actionClass} disabled={disabled}>{busy ? 'Saving…' : 'Save product'}</button>
    </form>
    {product && <VariantEditor productId={product.id} variants={product.variants} onSaved={() => onSaved(product)} />}
  </section>;
}
