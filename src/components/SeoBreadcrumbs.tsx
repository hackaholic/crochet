import type { Category } from '../lib/api/catalogue';
import type { SeoMetadata } from '../lib/api/seo';
import { publicBreadcrumbs } from '../lib/seo/pageSchemas';

export default function SeoBreadcrumbs({ metadata, categories = [] }: { metadata?: SeoMetadata; categories?: Category[] }) {
  const trail = publicBreadcrumbs(metadata, categories);
  if (trail.length < 2) return null;
  return <nav aria-label="Breadcrumb" className="storefront-shell py-4 text-sm text-[#8B6B4A]">
    <ol className="flex flex-wrap items-center gap-2">
      {trail.map((item, index) => <li key={item.path} className="flex items-center gap-2">
        {index > 0 && <span aria-hidden="true">/</span>}
        {index === trail.length - 1 ? <span aria-current="page" className="text-[#2C1810]">{item.name}</span>
          : <a href={item.path} className="hover:text-[#C4622D]">{item.name}</a>}
      </li>)}
    </ol>
  </nav>;
}
