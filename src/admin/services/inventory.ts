import { adminRequest, type AdminProductVariant } from '../../lib/api/admin';
export const adjustStock = (id: number, adjustment: number) => adminRequest<AdminProductVariant>(
  `/admin/variants/${id}/inventory`, { method: 'PATCH', body: JSON.stringify({ adjustment }) },
);
