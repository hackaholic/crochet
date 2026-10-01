import type { PromoBannerSection } from '../../lib/api/storefront';

export default function PromoBanner({ section, onNavigate }: { section: PromoBannerSection; onNavigate: (url: string) => void }) {
  return <section className="px-4 py-8 sm:py-10"><div className="relative mx-auto min-h-72 max-w-7xl overflow-hidden rounded-3xl bg-[#2C1810] p-8 text-white md:p-14">{section.imageUrl && <img src={section.imageUrl} alt={section.imageAlt ?? ''} className="absolute inset-0 h-full w-full object-cover opacity-35" loading="lazy" decoding="async" />}<div className="relative max-w-xl"><h2 className="text-4xl font-medium" style={{ fontFamily: 'var(--font-serif)' }}>{section.title}</h2>{section.description && <p className="mt-4 text-white/80">{section.description}</p>}{section.ctaText && section.ctaUrl && <button onClick={() => onNavigate(section.ctaUrl!)} className="mt-7 rounded-full bg-white px-6 py-3 font-semibold text-[#2C1810]">{section.ctaText}</button>}</div></div></section>;
}
