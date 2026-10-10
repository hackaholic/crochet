/** Client feedback follows the account API; server validation remains authoritative. */
export function textError(value: string, minimum: number, maximum: number) {
  const text = value.trim();
  return text.length < minimum || text.length > maximum || /[\u0000-\u001f\u007f]/.test(text)
    ? `Enter ${minimum}–${maximum} characters without control characters.` : '';
}
export function normalizePhone(value: string) { return value.trim().replace(/[\s-]/g, ''); }
export function phoneError(value: string, optional = false) {
  const phone = normalizePhone(value);
  if (!phone && optional) return '';
  return /^(\+?[1-9]\d{7,14}|\d{10})$/.test(phone) ? '' : 'Enter a valid mobile number, including country code when needed.';
}
export function pinError(value: string) { return /^[1-9][0-9]{5}$/.test(value.trim().replace(/\s+/g, '')) ? '' : 'Enter a valid 6-digit Indian PIN code.'; }
