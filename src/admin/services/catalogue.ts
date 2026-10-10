import { adminRequest, type AdminProduct, type AdminProductVariant } from '../../lib/api/admin';

export interface CatalogueProduct extends AdminProduct {
  description?: string;
  shortDescription?: string;
  primaryCategoryId?: number;
  categoryIds: number[];
  tagIds: number[];
  tagNames: string[];
  galleryImages: string[];
  galleryImageUrls?: string[];
}
export interface TaxonomyOption { id: number; name: string }
export interface ProductDraft {
  name: string; description: string; primaryImage: string;
  galleryImages: string[]; categoryIds: number[]; tagIds: number[]; primaryCategoryId?: number;
}
export interface VariantDraft { sku: string; name: string; price: number; stockQuantity: number }
export const getProduct = (id: number) => adminRequest<CatalogueProduct>(`/admin/products/${id}`);
export const getCategories = () => adminRequest<TaxonomyOption[]>('/admin/categories');
export const getTags = () => adminRequest<TaxonomyOption[]>('/admin/tags');
export const createTag = (name: string) => adminRequest<TaxonomyOption>('/admin/tags', { method: 'POST', body: JSON.stringify({ name }) });
export const saveProduct = (draft: ProductDraft, id?: number, variants?: VariantDraft[]) => adminRequest<CatalogueProduct>(
  id === undefined ? '/admin/products' : `/admin/products/${id}`,
  { method: id === undefined ? 'POST' : 'PATCH', body: JSON.stringify({ ...draft, ...(variants ? { variants } : {}) }) },
);
export const saveVariant = (productId: number, draft: VariantDraft, id?: number) => adminRequest<AdminProductVariant>(
  id === undefined ? `/admin/products/${productId}/variants` : `/admin/variants/${id}`,
  { method: id === undefined ? 'POST' : 'PATCH', body: JSON.stringify(draft) },
);
export async function uploadPhoto(file: File): Promise<{ key: string; url: string }> {
  const body = new FormData();
  body.append('file', file);
  const result = await adminRequest<{ key: string; url: string }>('/admin/images/upload', { method: 'POST', body });
  return result;
}

export const setProductStatus = (id: number, status: 'ACTIVE' | 'DRAFT') => adminRequest<CatalogueProduct>(
  `/admin/products/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) },
);
