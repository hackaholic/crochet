export interface User {
  id: number;
  phone?: string | null;
  email?: string | null;
  name?: string | null;
  fullName?: string | null;
  role: string;
  status?: string;
  createdAt?: string;
  identities: string[];
}

export interface GoogleAuthPayload {
  credential: string;
  name?: string;
  email?: string;
  sub?: string;
}

export interface FacebookAuthPayload {
  accessToken: string;
  userId?: string;
  email?: string;
  name?: string;
}

import { apiUrl } from './client';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(apiUrl(`/auth${path}`), {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!r.ok) {
    const errorData = await r.json().catch(() => null);
    const message = errorData?.detail || `Authentication request failed (${r.status})`;
    throw new Error(message);
  }
  return r.json() as Promise<T>;
}

export const authApi = {
  me: () => request<User>('/me'),
  sendOtp: (phone: string) =>
    request<{ devOtp?: string; phone: string; cooldownSeconds: number }>('/phone/send-otp', {
      method: 'POST',
      body: JSON.stringify({ phone }),
    }),
  verifyOtp: (phone: string, otp: string, name?: string) =>
    request<{ user: User; cartMerged: boolean }>('/phone/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ phone, otp, name }),
    }),
  google: (payload: GoogleAuthPayload | string) => {
    const body = typeof payload === 'string' ? { credential: payload } : payload;
    return request<{ user: User; cartMerged: boolean }>('/google', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },
  facebook: (payload: FacebookAuthPayload) =>
    request<{ user: User; cartMerged: boolean }>('/facebook', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  logout: () => request<{ status: string; message: string }>('/logout', { method: 'POST' }),
};

