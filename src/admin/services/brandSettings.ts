import { adminRequest } from '../../lib/api/admin';
export interface BrandSettings { name: string; ownerName: string; instagramUrl: string | null; whatsappUrl: string | null }
export const BRAND_LIMITS = { name: 100, url: 255 } as const;
export type BrandDraft = Record<keyof BrandSettings, string>;
export function brandDraft(brand: BrandSettings): BrandDraft {
  return { name: brand.name, ownerName: brand.ownerName, instagramUrl: brand.instagramUrl ?? '', whatsappUrl: brand.whatsappUrl ?? '' };
}
export function validateBrand(draft: BrandDraft): Partial<Record<keyof BrandDraft,string>> {
  const errors: Partial<Record<keyof BrandDraft,string>> = {};
  for (const key of ['name','ownerName'] as const) {
    const value = draft[key].trim();
    if (!value || value.length > BRAND_LIMITS.name || /[\u0000-\u001f\u007f]/.test(draft[key])) errors[key]='Enter a name between 1 and 100 characters without control characters.';
  }
  for (const key of ['instagramUrl','whatsappUrl'] as const) {
    const value=draft[key].trim(); if (!value) continue;
    try { const url=new URL(value); if (url.protocol!=='https:' || !url.hostname || url.username || url.password || value.length>BRAND_LIMITS.url || /\s/.test(value)) throw new Error(); }
    catch { errors[key]='Enter a full HTTPS link without credentials, or leave blank.'; }
  }
  return errors;
}
export const getBrandSettings = () => adminRequest<BrandSettings>('/admin/storefront/brand');
export const saveBrandSettings = (draft:BrandDraft) => adminRequest<BrandSettings>('/admin/storefront/brand',{method:'PUT',body:JSON.stringify(Object.fromEntries(Object.entries(draft).map(([key,value])=>[key,value.trim()]))) });
