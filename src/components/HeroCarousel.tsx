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
      <section className="relative h-[46rem] overflow-hidden bg-[#2C1810] pt-28 sm:h-[50rem] lg:h-[720px]" aria-busy={loading}>
        <div className="absolute inset-x-0 bottom-0 h-[calc(100%-7rem)] animate-pulse bg-gradient-to-br from-[#2C1810] via-[#5C3D2E] to-[#8B6B4A]" aria-hidden="true" />
        <div className="relative mx-auto flex h-[calc(100%-7rem)] max-w-7xl items-start px-5 pb-24 pt-10 sm:px-8 sm:pt-14 lg:px-10 lg:pt-12" aria-hidden="true">
          <div className="w-full max-w-2xl">
            <div className="h-8 w-36 animate-pulse rounded-full bg-white/20" />
            <div className="mt-7 h-12 w-full max-w-xl animate-pulse rounded-xl bg-white/18" />
            <div className="mt-3 h-12 w-4/5 max-w-lg animate-pulse rounded-xl bg-white/18" />
            <div className="mt-7 h-5 w-full max-w-xl animate-pulse rounded bg-white/15" />
            <div className="mt-3 h-5 w-3/4 max-w-md animate-pulse rounded bg-white/15" />
            <div className="mt-14 flex gap-3">
              <div className="h-12 w-44 animate-pulse rounded-full bg-white/22" />
              <div className="h-12 w-56 animate-pulse rounded-full border border-white/20 bg-white/10" />
            </div>
          </div>
        </div>
        <span className="sr-only">{loading ? 'Loading homepage campaigns' : 'No homepage campaigns are currently active'}</span>
      </section>
    );
  }

  const showPrevious = () => setActiveIndex(current => (current - 1 + campaigns.length) % campaigns.length);
  const showNext = () => setActiveIndex(current => (current + 1) % campaigns.length);

  return (
    <section
      className="relative h-[46rem] overflow-hidden bg-[#2C1810] pt-28 sm:h-[50rem] lg:h-[720px]"
      aria-roledescription="carousel"
      aria-label="Featured Sulocraft campaigns"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={event => {
        if (!event.currentTarget.contains(event.relatedTarget)) setPaused(false);
      }}
    >
      <img
        data-testid="hero-image"
        key={activeCampaign.id}
        src={activeCampaign.imageUrl}
        alt={activeCampaign.imageAlt}
        className="absolute inset-x-0 bottom-0 h-[calc(100%-7rem)] w-full object-cover object-[70%_center] motion-safe:animate-[fade-in_350ms_ease-out] sm:object-center"
        loading="eager"
        decoding="async"
        sizes="100vw"
      />
      <div className="absolute inset-x-0 bottom-0 h-[calc(100%-7rem)] bg-gradient-to-r from-[#1F100B]/95 via-[#2C1810]/68 to-[#2C1810]/5" />
      <div className="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-[#1F100B]/65 to-transparent" />

      <div data-testid="hero-slide-frame" className="relative mx-auto flex h-[calc(100%-7rem)] max-w-7xl items-start px-5 pb-24 pt-10 sm:px-8 sm:pt-14 lg:px-10 lg:pt-12">
        <div className="flex w-full max-w-3xl flex-col text-white lg:max-w-2xl">
          <div className="h-8">
            <p className={`inline-flex rounded-full border border-white/25 bg-white/12 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-white backdrop-blur-sm ${activeCampaign.eyebrow ? '' : 'invisible'}`}>
              {activeCampaign.eyebrow || 'Featured'}
            </p>
          </div>
          <div className="mt-5 h-[17rem] sm:h-[16rem] lg:h-[14rem]">
            <h1 className="max-w-2xl text-4xl font-medium leading-[1.04] text-white drop-shadow-lg sm:text-5xl" style={{ fontFamily: 'var(--font-serif)' }}>
              {activeCampaign.title}
              {activeCampaign.emphasis && <><br /><em className="text-[#F6D7C9]">{activeCampaign.emphasis}</em></>}
            </h1>
            <p className="mt-4 max-w-xl text-base leading-relaxed text-white/85 drop-shadow sm:text-lg lg:text-base">{activeCampaign.description}</p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={onShop} className="flex items-center gap-2 rounded-full bg-[#C4622D] px-7 py-3.5 font-semibold text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-[#D4795A]">
              Shop Collection <ArrowRightIcon size={18} />
            </button>
            <button onClick={onCustom} className="rounded-full border-2 border-white/80 bg-black/10 px-7 py-3.5 font-semibold text-white backdrop-blur-sm transition hover:bg-white hover:text-[#2C1810]">
              Create Something Custom
            </button>
          </div>

          <p className="sr-only" aria-live="polite">Slide {activeIndex + 1} of {campaigns.length}: {activeCampaign.title}</p>
        </div>

      </div>

      {campaigns.length > 1 && (
        <div
          className="absolute bottom-4 flex justify-center px-4"
          style={{ left: 0, right: 0, width: '100%' }}
          aria-label="Choose featured campaign"
        >
          <div className="flex items-center gap-3 rounded-full border border-white/20 bg-black/25 p-2 backdrop-blur-md">
            <button onClick={showPrevious} aria-label="Previous promotion" className="flex h-9 w-9 items-center justify-center rounded-full border border-white/35 text-white transition hover:border-white hover:bg-white hover:text-[#2C1810]"><ChevronLeftIcon size={18} /></button>
            <div className="flex gap-2">
              {campaigns.map((campaign, index) => (
                <button
                  key={campaign.id}
                  onClick={() => setActiveIndex(index)}
                  aria-label={`Show ${campaign.eyebrow ?? campaign.title}`}
                  aria-current={index === activeIndex ? 'true' : undefined}
                  className={`h-2.5 rounded-full transition-all ${index === activeIndex ? 'w-7 bg-white' : 'w-2.5 bg-white/45 hover:bg-white/75'}`}
                />
              ))}
            </div>
            <button onClick={showNext} aria-label="Next promotion" className="flex h-9 w-9 items-center justify-center rounded-full border border-white/35 text-white transition hover:border-white hover:bg-white hover:text-[#2C1810]"><ChevronRightIcon size={18} /></button>
          </div>
        </div>
      )}
    </section>
  );
}
