import { apiUrl } from './client';

export interface ProfileOut {
  id: number;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  status: string;
  identities: string[];
  createdAt: string;
  lastLoginAt?: string | null;
}

export interface AccountOverviewOut {
  profile: ProfileOut;
  totalOrders: number;
  activeOrders: number;
  savedAddresses: number;
  wishlistItemsCount: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    credentials: 'include',
    headers: init?.body ? { 'Content-Type': 'application/json' } : undefined,
    ...init,
  });
  if (!response.ok) throw new Error(String(response.status));
  return response.json() as Promise<T>;
}

export const accountProfileApi = {
  overview: () => request<AccountOverviewOut>('/account/overview'),
  updateProfile: (profile: Pick<ProfileOut, 'name' | 'email'>) => request<ProfileOut>('/account/profile', {
    method: 'PATCH',
    body: JSON.stringify(profile),
  }),
};
