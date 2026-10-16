import { isPrivatePath } from './urlPolicy.mjs';

/** One public share contract for static HTML and client navigation. */
export function socialMetadata(metadata, canonicalUrl) {
  const tags = {
    'og:title': metadata.title,
    'og:description': metadata.description,
    'og:url': canonicalUrl,
    'og:type': metadata.pageType === 'product' ? 'product' : metadata.pageType === 'article' ? 'article' : 'website',
    'twitter:card': 'summary',
    'twitter:title': metadata.title,
    'twitter:description': metadata.description,
  };
  // Private/error pages must not inherit a catalogue image or its descriptive data.
  if (isPrivatePath(metadata.canonicalPath) || [404, 410].includes(metadata.httpStatus)) return tags;
  let image;
  try {
    image = new URL(metadata.imageUrl);
    if (!['https:', 'http:'].includes(image.protocol) || image.username || image.password) return tags;
  } catch { return tags; }
  tags['og:image'] = image.href;
  tags['og:image:alt'] = metadata.imageAlt?.trim() || metadata.title;
  tags['twitter:card'] = 'summary_large_image';
  tags['twitter:image'] = image.href;
  tags['twitter:image:alt'] = tags['og:image:alt'];
  if (Number.isSafeInteger(metadata.imageWidth) && metadata.imageWidth > 0 &&
      Number.isSafeInteger(metadata.imageHeight) && metadata.imageHeight > 0) {
    tags['og:image:width'] = String(metadata.imageWidth);
    tags['og:image:height'] = String(metadata.imageHeight);
  }
  if (/^image\/(?:png|jpeg|webp|gif)$/.test(metadata.imageType ?? '')) tags['og:image:type'] = metadata.imageType;
  return tags;
}
