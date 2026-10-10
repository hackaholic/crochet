import { adminRequest, type AdminOrderList } from '../../lib/api/admin';
export interface Customer {
  id: number; name: string | null; email: string | null; phone: string | null;
  status: string; createdAt: string | null; lastLoginAt: string | null; orderCount: number;
}
export interface CustomerList { items: Customer[]; total: number; page: number; pageSize: number }
export const getCustomers = (q: string, page: number, signal?: AbortSignal) => adminRequest<CustomerList>(
  `/admin/customers?${new URLSearchParams({ q, page: String(page) })}`, { signal },
);
export const getCustomer = (id: number, signal?: AbortSignal) => adminRequest<Customer>(`/admin/customers/${id}`, { signal });
export const getCustomerOrders = (id: number, page: number, signal?: AbortSignal) => adminRequest<AdminOrderList>(`/admin/customers/${id}/orders?page=${page}`, { signal });
