import { useEffect, useRef, useState, type ChangeEvent } from 'react';
import type { User } from '../lib/api/auth';
import { accountProfileApi } from '../lib/api/account';

const emptyForm = { firstName: '', lastName: '', email: '', phone: '', line1: '', line2: '', city: '', state: '', postalCode: '', landmark: '' };
type Form = typeof emptyForm;

function contactValues(customer?: Pick<User, 'name' | 'fullName' | 'email' | 'phone'> | null) {
  const [firstName = '', ...lastName] = (customer?.name || customer?.fullName || '').trim().split(/\s+/);
  return { firstName, lastName: lastName.join(' '), email: customer?.email ?? '', phone: customer?.phone ?? '' };
}

/** Hydrate only untouched contact fields; never persist drafts across identities. */
export function useCheckoutForm(customer?: User | null) {
  const [form, setForm] = useState<Form>(() => ({ ...emptyForm, ...contactValues(customer) }));
  const edited = useRef(new Set<keyof Form>());
  const owner = useRef(customer?.id ?? null);
  useEffect(() => {
    const nextOwner = customer?.id ?? null;
    if (owner.current !== null && owner.current !== nextOwner) {
      edited.current.clear();
      setForm({ ...emptyForm });
    }
    owner.current = nextOwner;
    if (!customer) return;
    let active = true;
    const hydrate = (contact: ReturnType<typeof contactValues>) => setForm(previous => {
      if (!active || owner.current !== customer.id) return previous;
      const next = { ...previous };
      for (const key of ['firstName', 'lastName', 'email', 'phone'] as const) {
        if (!edited.current.has(key)) next[key] = contact[key];
      }
      return next;
    });
    hydrate(contactValues(customer));
    accountProfileApi.overview().then(({ profile }) => {
      if (active && owner.current === customer.id && profile.id === customer.id) hydrate(contactValues(profile));
    }).catch(() => { /* Auth user remains a safe fallback; profile availability must not block checkout. */ });
    return () => { active = false; };
  }, [customer?.id, customer?.name, customer?.fullName, customer?.email, customer?.phone]);

  const input = (name: keyof Form) => ({ value: form[name], onChange: (event: ChangeEvent<HTMLInputElement>) => {
    edited.current.add(name);
    setForm(previous => ({ ...previous, [name]: event.target.value }));
  } });
  return { form, input };
}
