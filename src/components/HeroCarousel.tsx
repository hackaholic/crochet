import { useEffect, useState } from 'react';
import { ArrowRightIcon, ChevronLeftIcon, ChevronRightIcon } from './Icons';
import type { HomepageCampaign } from '../lib/api/storefront';

interface HeroCarouselProps {
  campaigns: HomepageCampaign[];
  loading?: boolean;
  onShop: () => void;
  onCustom: () => void;
}

const ROTATION_INTERVAL_MS = 6000;

export default function HeroCarousel({ campaigns, loading = false, onShop, onCustom }: HeroCarouselProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const activeCampaign = campaigns[activeIndex];

  useEffect(() => setActiveIndex(0), [campaigns]);

  useEffect(() => {
    if (paused || campaigns.length < 2 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const timer = window.setInterval(
      () => setActiveIndex(current => (current + 1) % campaigns.length),
      ROTATION_INTERVAL_MS,
    );
    return () => window.clearInterval(timer);
  }, [campaigns.length, paused]);

  if (!activeCampaign) {
    return (
      <section className="min-h-[70vh] bg-[#FAF7F2] pt-28" aria-busy={loading}>
        <div className="mx-auto grid min-h-[60vh] max-w-7xl items-center gap-12 px-4 py-16 lg:grid-cols-2">
          <div className="space-y-5" aria-hidden="true">
            <div className="h-8 w-40 animate-pulse rounded-full bg-[#EDE4D0]" />
            <div className="h-36 max-w-xl animate-pulse rounded-3xl bg-[#EDE4D0]" />
            <div className="h-20 max-w-lg animate-pulse rounded-2xl bg-[#EDE4D0]" />
          </div>
          <div className="aspect-[4/5] max-h-[620px] animate-pulse rounded-3xl bg-[#EDE4D0]" aria-hidden="true" />
          <span className="sr-only">{loading ? 'Loading homepage campaigns' : 'No homepage campaigns are currently active'}</span>
        </div>
      </section>
    );
  }

  const showPrevious = () => setActiveIndex(current => (current - 1 + campaigns.length) % campaigns.length);
  const showNext = () => setActiveIndex(current => (current + 1) % campaigns.length);

  return (
    <section
      className="relative min-h-screen overflow-hidden bg-[#FAF7F2] pt-28"
      aria-roledescription="carousel"
      aria-label="Featured Sulocraft campaigns"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={event => {
        if (!event.currentTarget.contains(event.relatedTarget)) setPaused(false);
      }}
    >
      <div className="absolute inset-0 bg-[radial-gradient(#8B6B4A10_1px,transparent_1px)] bg-[size:24px_24px]" />
      <div className="relative mx-auto grid max-w-7xl items-center gap-10 px-4 py-12 md:py-16 lg:grid-cols-2 lg:gap-16">
        <div className="order-2 lg:order-1">
          {activeCampaign.eyebrow && (
            <p className="inline-flex rounded-full bg-[#F2C4CE]/40 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-[#C4622D]">
              {activeCampaign.eyebrow}
            </p>
          )}
          <h1 className="mt-6 text-5xl font-medium leading-tight text-[#2C1810] lg:text-7xl" style={{ fontFamily: 'var(--font-serif)' }}>
            {activeCampaign.title}
            {activeCampaign.emphasis && <><br /><em>{activeCampaign.emphasis}</em></>}
          </h1>
          <p className="mt-6 max-w-lg text-lg leading-relaxed text-[#5C3D2E]">{activeCampaign.description}</p>

          <div className="mt-10 flex flex-wrap gap-4">
            <button onClick={onShop} className="flex items-center gap-2 rounded-full bg-[#C4622D] px-8 py-4 font-semibold text-white transition hover:-translate-y-0.5 hover:bg-[#D4795A] hover:shadow-lg">
              Shop Collection <ArrowRightIcon size={18} />
            </button>
            <button onClick={onCustom} className="rounded-full border-2 border-[#2C1810] px-8 py-4 font-semibold text-[#2C1810] transition hover:bg-[#2C1810] hover:text-white">
              Create Something Custom
            </button>
          </div>

          {campaigns.length > 1 && (
            <div className="mt-8 flex items-center gap-3" aria-label="Choose featured campaign">
              <button onClick={showPrevious} aria-label="Previous promotion" className="rounded-full border border-[#D9C9B8] p-2 text-[#5C3D2E] transition hover:border-[#C4622D] hover:text-[#C4622D]"><ChevronLeftIcon size={18} /></button>
              <div className="flex gap-2">
                {campaigns.map((campaign, index) => (
                  <button
                    key={campaign.id}
                    onClick={() => setActiveIndex(index)}
                    aria-label={`Show ${campaign.eyebrow ?? campaign.title}`}
                    aria-current={index === activeIndex ? 'true' : undefined}
                    className={`h-2.5 rounded-full transition-all ${index === activeIndex ? 'w-7 bg-[#C4622D]' : 'w-2.5 bg-[#D9C9B8] hover:bg-[#8B6B4A]'}`}
                  />
                ))}
              </div>
              <button onClick={showNext} aria-label="Next promotion" className="rounded-full border border-[#D9C9B8] p-2 text-[#5C3D2E] transition hover:border-[#C4622D] hover:text-[#C4622D]"><ChevronRightIcon size={18} /></button>
            </div>
          )}
          <p className="sr-only" aria-live="polite">Slide {activeIndex + 1} of {campaigns.length}: {activeCampaign.title}</p>
        </div>

        <div className="relative order-1 mx-auto w-full max-w-xl overflow-hidden rounded-3xl shadow-xl lg:order-2" style={{ aspectRatio: '4/5' }}>
          <img
            key={activeCampaign.id}
            src={activeCampaign.imageUrl}
            alt={activeCampaign.imageAlt}
            className="h-full w-full object-cover motion-safe:animate-[fade-in_350ms_ease-out]"
            loading="eager"
            decoding="async"
            sizes="(min-width: 1024px) 50vw, 100vw"
          />
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#2C1810]/25 to-transparent" />
        </div>
      </div>
    </section>
  );
}
