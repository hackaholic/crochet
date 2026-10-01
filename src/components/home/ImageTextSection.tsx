import type { ImageTextSectionData } from '../../lib/api/storefront';

export default function ImageTextSection({ section, onNavigate }: { section: ImageTextSectionData; onNavigate: (url: string) => void }) {
  return <section className="mx-auto grid max-w-7xl items-center gap-10 px-4 py-20 lg:grid-cols-2"><img src={section.imageUrl} alt={section.imageAlt} className={`aspect-[4/3] h-full w-full rounded-3xl object-cover ${section.imagePosition === 'right' ? 'lg:order-2' : ''}`} loading="lazy" decoding="async" /><div className={section.imagePosition === 'right' ? 'lg:order-1' : ''}><h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{section.title}</h2><p className="mt-5 leading-7 text-[#5C3D2E]">{section.description}</p>{section.ctaText && section.ctaUrl && <button onClick={() => onNavigate(section.ctaUrl!)} className="mt-7 rounded-full bg-[#C4622D] px-6 py-3 font-semibold text-white">{section.ctaText}</button>}</div></section>;
}
