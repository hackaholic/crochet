import type { SeoMetadata } from '../lib/api/seo';

export default function CatalogueIntro({ metadata, pathname }: { metadata?: SeoMetadata; pathname: string }) {
  const path = pathname.replace(/\/+$/, '');
  const entity = metadata?.categoryEntity && path === `/categories/${encodeURIComponent(metadata.categoryEntity.slug)}`
    ? metadata.categoryEntity : metadata?.collectionEntity && path === `/collections/${encodeURIComponent(metadata.collectionEntity.slug)}` ? metadata.collectionEntity : undefined;
  const description = typeof entity?.description === 'string' ? entity.description.trim() : '';
  if (!description) return null;
  return <p className="catalogue-description max-w-3xl whitespace-pre-line break-words text-sm leading-7 text-[#5C3D2E]">{description}</p>;
}
