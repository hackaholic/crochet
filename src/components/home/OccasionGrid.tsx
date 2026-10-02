import type { OccasionGridSection } from '../../lib/api/storefront';

function uniqueOccasions(section: OccasionGridSection) {
  const ids = new Set<string>();
  const images = new Set<string>();
  return section.occasions.filter(occasion => {
    const image = occasion.imageUrl?.trim().split(/[?#]/, 1)[0].toLowerCase() ?? '';
    if (ids.has(occasion.id) || (image && images.has(image))) return false;
    ids.add(occasion.id);
    if (image) images.add(image);
    return true;
  });
}

export default function OccasionGrid({ section, onNavigate }: { section: OccasionGridSection; onNavigate: (url: string) => void }) {
  const occasions = uniqueOccasions(section);
  if (occasions.length === 0) return null;
  return <section className="bg-[#FAF7F2] py-14 sm:py-16"><div className="storefront-shell"><header className="mb-8 text-center sm:mb-10">{section.eyebrow && <p className="text-xs font-semibold uppercase tracking-widest text-[#C4622D]">{section.eyebrow}</p>}<h2 className="mt-3 text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{section.title}</h2>{section.description && <p className="mx-auto mt-3 max-w-2xl text-[#8B6B4A]">{section.description}</p>}</header><div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">{occasions.map(occasion => <button key={occasion.id} type="button" onClick={() => onNavigate(`/shop?occasion=${encodeURIComponent(occasion.id)}`)} aria-label={`Shop gifts for ${occasion.name}`} className="group relative aspect-[4/3] overflow-hidden rounded-2xl bg-[#EDE4D0] text-left">{occasion.imageUrl && <img src={occasion.imageUrl} alt="" className="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy" decoding="async" />}{!occasion.imageUrl && occasion.icon && <span aria-hidden="true" className="absolute inset-0 grid place-items-center text-5xl">{occasion.icon}</span>}<span className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/15 to-transparent" /><span className="absolute inset-x-0 bottom-0 p-3 text-sm font-semibold text-white">{occasion.name}</span></button>)}</div></div></section>;
}
