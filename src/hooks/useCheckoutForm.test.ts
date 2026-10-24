import { act, cleanup, renderHook, waitFor } from '@testing-library/react';
import type { ChangeEvent } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useCheckoutForm } from './useCheckoutForm';
import { accountProfileApi, type AccountOverviewOut } from '../lib/api/account';
import type { User } from '../lib/api/auth';
vi.mock('../lib/api/account', () => ({ accountProfileApi: { overview: vi.fn() } }));
const customer: User = { id: 1, name: 'Demo Customer', email: 'demo.customer@example.com', phone: '+919876543210', role: 'CUSTOMER', identities: ['email'] };
const response = (user: User): AccountOverviewOut => ({ profile: { ...user, status: 'ACTIVE', createdAt: '2026-01-01' }, totalOrders: 0, activeOrders: 0, savedAddresses: 0, wishlistItemsCount: 0 });
afterEach(() => { cleanup(); vi.resetAllMocks(); });
beforeEach(() => { vi.mocked(accountProfileApi.overview).mockRejectedValue(new Error('offline')); });
const change = (value: string) => ({ target: { value } } as ChangeEvent<HTMLInputElement>);

describe('checkout profile hydration', () => {
  it('prefills known identity synchronously, then refreshes the saved profile', async () => {
    vi.mocked(accountProfileApi.overview).mockResolvedValue(response({ ...customer, name: 'Anupama Sharma', phone: '+919000000000' }));
    const { result } = renderHook(() => useCheckoutForm(customer));
    expect(result.current.form.email).toBe(customer.email);
    await waitFor(() => expect(result.current.form.firstName).toBe('Anupama'));
    expect(result.current.form.lastName).toBe('Sharma');
    expect(result.current.form.phone).toBe('+919000000000');
    expect(result.current.form.line1).toBe('');
  });
  it('preserves edited and intentionally cleared fields during late profile arrival', async () => {
    let finish!: (value: AccountOverviewOut) => void;
    vi.mocked(accountProfileApi.overview).mockImplementation(() => new Promise(resolve => { finish = resolve; }));
    const { result } = renderHook(() => useCheckoutForm(customer));
    act(() => { result.current.input('firstName').onChange(change('Custom')); result.current.input('email').onChange(change('')); });
    await act(async () => finish(response({ ...customer, name: 'Updated Saved Name' })));
    expect(result.current.form.firstName).toBe('Custom');
    expect(result.current.form.email).toBe('');
    expect(result.current.form.lastName).toBe('Saved Name');
  });
  it('does not fetch guests and keeps typed guest details when login arrives', async () => {
    const { result, rerender } = renderHook(({ user }: { user: User | null }) => useCheckoutForm(user), { initialProps: { user: null as User | null } });
    expect(accountProfileApi.overview).not.toHaveBeenCalled();
    expect(result.current.form.email).toBe('');
    act(() => result.current.input('email').onChange(change('delivery@example.com')));
    rerender({ user: customer });
    await act(async () => {});
    expect(result.current.form.email).toBe('delivery@example.com');
    expect(result.current.form.firstName).toBe('Demo');
  });
  it('handles fullName, single names, absent fields and unavailable profile without fabricating values', async () => {
    const { result } = renderHook(() => useCheckoutForm({ ...customer, name: null, fullName: '  Anupama  ', phone: null }));
    await act(async () => {});
    expect(result.current.form.firstName).toBe('Anupama');
    expect(result.current.form.lastName).toBe('');
    expect(result.current.form.phone).toBe('');
    expect(result.current.form.email).toBe(customer.email);
  });
  it('rejects mismatched profile identity and ignores old requests across account switch/logout', async () => {
    let finishA!: (value: AccountOverviewOut) => void;
    vi.mocked(accountProfileApi.overview).mockImplementationOnce(() => new Promise(resolve => { finishA = resolve; })).mockResolvedValue(response({ ...customer, id: 999, name: 'Wrong Identity' }));
    const { result, rerender } = renderHook(({ user }: { user: User | null }) => useCheckoutForm(user), { initialProps: { user: customer as User | null } });
    act(() => result.current.input('line1').onChange(change('Private old address')));
    const other = { ...customer, id: 2, name: 'Other Person', email: 'other@example.com' };
    rerender({ user: other });
    await act(async () => { finishA(response({ ...customer, name: 'Stale Identity' })); });
    expect(result.current.form.email).toBe(other.email);
    expect(result.current.form.firstName).toBe('Other');
    expect(result.current.form.line1).toBe('');
    rerender({ user: null });
    expect(result.current.form.email).toBe('');
    expect(result.current.form.firstName).toBe('');
  });
});
