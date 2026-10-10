/** Never display server messages/inputs: only map known validation fields to safe copy. */
export class AccountRequestError extends Error {
  constructor(public status: number, public fields: Record<string, string>) { super(String(status)); }
}
export async function accountResponseError(response: Response): Promise<AccountRequestError> {
  const fields: Record<string, string> = {};
  const allowed = ['name','phone','line1','line2','city','state','postalCode','postal_code','country'];
  if (response.status === 422) {
    try {
      const body = await response.json();
      if (Array.isArray(body.detail)) for (const entry of body.detail) {
        const field = Array.isArray(entry.loc) ? entry.loc.at(-1) : undefined;
        if (allowed.includes(field)) fields[field === 'postal_code' ? 'postalCode' : field] = 'Please check this value.';
      }
    } catch { /* Invalid error bodies remain a safe generic error. */ }
  }
  return new AccountRequestError(response.status, fields);
}
