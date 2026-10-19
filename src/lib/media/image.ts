export interface MediaVariant {
  url: string;
  width?: number | null;
  height?: number | null;
  contentType?: string | null;
  descriptor?: string | null;
}
export interface MediaMetadata {
  url: string;
  altText?: string | null;
  width?: number | null;
  height?: number | null;
  contentType?: string | null;
  variants?: MediaVariant[];
}

const dimension = (value: unknown): value is number => Number.isSafeInteger(value) && Number(value) > 0;
export function isSafeMediaUrl(url: string): boolean {
  if (!url || /[\s,\u0000-\u001f]/.test(url) || url.startsWith('//')) return false;
  if (url.startsWith('/')) return !url.includes('\\');
  try { const parsed = new URL(url); return ['https:', 'http:'].includes(parsed.protocol) && !parsed.username && !parsed.password; }
  catch { return false; }
}

/** Never apply one asset's dimensions or alt text to another gallery image. */
export function imageAttributes(src: string, metadata?: MediaMetadata | null, fallbackAlt = '') {
  if (!metadata || metadata.url !== src) return { alt: fallbackAlt };
  const dimensions = dimension(metadata.width) && dimension(metadata.height)
    ? { width: metadata.width, height: metadata.height } : {};
  const seen = new Set<number>();
  const variants = (metadata.variants ?? []).filter(variant => {
    if (!dimension(variant.width) || !isSafeMediaUrl(variant.url) || seen.has(variant.width)) return false;
    // Only width descriptors backed by actual dimensions; never infer derivatives.
    if (variant.descriptor && variant.descriptor !== `${variant.width}w`) return false;
    seen.add(variant.width);
    return true;
  }).sort((a, b) => a.width! - b.width!);
  return {
    alt: fallbackAlt === '' ? '' : metadata.altText?.trim() || fallbackAlt,
    ...dimensions,
    ...(variants.length ? { srcSet: variants.map(v => `${v.url} ${v.width}w`).join(', ') } : {}),
  };
}

/** Picture source metadata uses the same validation without an img-only alt attribute. */
export function sourceAttributes(src: string, metadata?: MediaMetadata | null) {
  const { alt: _alt, ...attributes } = imageAttributes(src, metadata);
  return attributes;
}
