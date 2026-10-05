import { useEffect, useState, type CSSProperties } from 'react';
import { ArrowRightIcon, ChevronLeftIcon, ChevronRightIcon } from './Icons';
import type { HomepageCampaign } from '../lib/api/storefront';

interface HeroCarouselProps {
  campaigns: HomepageCampaign[];
  loading?: boolean;
  onShop: () => void;
  onCustom: () => void;
}

const ROTATION_INTERVAL_MS = 6000;

function mobileObjectPosition(position?: HomepageCampaign['mobileImagePosition']): string {
  if (!position || !Number.isFinite(position.x) || !Number.isFinite(position.y)) return '70% center';
  const x = Math.min(100, Math.max(0, position.x));
  const y = Math.min(100, Math.max(0, position.y));
  return `${x}% ${y}%`;
}

export default function HeroCarousel({ campaigns, loading = false, onShop, onCustom }: HeroCarouselProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const [touchStartX, setTouchStartX] = useState<number | null>(null);
  const [touchStartY, setTouchStartY] = useState<number | null>(null);
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
      <section
        data-testid="hero-section"
        className="relative h-[408px] overflow-hidden bg-[#2C1810] pt-24 sm:h-[540px] sm:pt-28 lg:h-[620px]"
        aria-busy={loading}
      >
        <div className="absolute inset-x-0 bottom-0 top-24 sm:top-28 animate-pulse bg-gradient-to-br from-[#2C1810] via-[#5C3D2E] to-[#8B6B4A]" aria-hidden="true" />
        <div className="storefront-shell relative flex h-[calc(100%-6rem)] sm:h-[calc(100%-7rem)] items-start pb-6 sm:pb-16 pt-3 sm:pt-6" aria-hidden="true">
          <div className="w-full max-w-2xl">
            <div className="h-6 w-28 sm:h-8 sm:w-36 animate-pulse rounded-full bg-white/20" />
            <div className="mt-3 sm:mt-5 h-8 sm:h-12 w-full max-w-xl animate-pulse rounded-xl bg-white/18" />
            <div className="mt-2 sm:mt-3 h-8 sm:h-12 w-4/5 max-w-lg animate-pulse rounded-xl bg-white/18" />
            <div className="mt-3 sm:mt-5 h-4 sm:h-5 w-full max-w-xl animate-pulse rounded bg-white/15" />
            <div className="mt-4 sm:mt-8 flex gap-3">
              <div className="h-10 sm:h-12 w-36 sm:w-44 animate-pulse rounded-full bg-white/22" />
              <div className="hidden sm:block h-12 w-56 animate-pulse rounded-full border border-white/20 bg-white/10" />
            </div>
          </div>
        </div>
        <span className="sr-only">{loading ? 'Loading homepage campaigns' : 'No homepage campaigns are currently active'}</span>
      </section>
    );
  }

  const showPrevious = () => setActiveIndex(current => (current - 1 + campaigns.length) % campaigns.length);
  const showNext = () => setActiveIndex(current => (current + 1) % campaigns.length);

  const handleTouchStart = (event: React.TouchEvent) => {
    setTouchStartX(event.touches[0].clientX);
    setTouchStartY(event.touches[0].clientY);
    setPaused(true);
  };

  const handleTouchEnd = (event: React.TouchEvent) => {
    if (touchStartX === null || touchStartY === null) {
      setPaused(false);
      return;
    }
    const touchEndX = event.changedTouches[0].clientX;
    const touchEndY = event.changedTouches[0].clientY;
    const deltaX = touchEndX - touchStartX;
    const deltaY = touchEndY - touchStartY;

    // Horizontal swipe threshold: 40px and more horizontal than vertical
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 40) {
      if (deltaX < 0) {
        showNext();
      } else {
        showPrevious();
      }
    }
    setTouchStartX(null);
    setTouchStartY(null);
    setPaused(false);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      showPrevious();
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      showNext();
    }
  };

  return (
    <section
      data-testid="hero-section"
      tabIndex={0}
      className="relative h-[408px] touch-pan-y overflow-hidden bg-[#2C1810] pt-24 focus:outline-none sm:h-[540px] sm:pt-28 lg:h-[620px]"
      aria-roledescription="carousel"
      aria-label="Featured Sulocraft campaigns"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={event => {
        if (!event.currentTarget.contains(event.relatedTarget)) setPaused(false);
      }}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onKeyDown={handleKeyDown}
    >
      <picture
        className="absolute inset-x-0 bottom-0 top-24 sm:top-28 h-[calc(100%-6rem)] sm:h-[calc(100%-7rem)] w-full"
        style={{ '--hero-mobile-object-position': mobileObjectPosition(activeCampaign.mobileImagePosition) } as CSSProperties}
      >
        {activeCampaign.mobileImageUrl && <source media="(max-width: 639px)" srcSet={activeCampaign.mobileImageUrl} sizes="100vw" />}
        <img
          data-testid="hero-image"
          key={activeCampaign.id}
          src={activeCampaign.imageUrl}
          alt={activeCampaign.imageAlt}
          className="hero-campaign-image h-full w-full object-cover object-[var(--hero-mobile-object-position,70%_center)] sm:object-center motion-safe:animate-[fade-in_350ms_ease-out]"
          loading={activeIndex === 0 ? 'eager' : 'lazy'}
          decoding="async"
          fetchPriority={activeIndex === 0 ? 'high' : 'low'}
          sizes="(max-width: 639px) 100vw, (max-width: 1023px) 100vw, 1280px"
        />
      </picture>
      <div className="absolute inset-x-0 bottom-0 top-24 sm:top-28 bg-gradient-to-r from-[#1F100B]/95 via-[#2C1810]/68 to-[#2C1810]/5" />
      <div className="absolute inset-x-0 bottom-0 h-32 sm:h-48 bg-gradient-to-t from-[#1F100B]/65 to-transparent" />

      <div data-testid="hero-slide-frame" className="storefront-shell relative flex h-[calc(100%-6rem)] sm:h-[calc(100%-7rem)] items-start pb-6 sm:pb-16 pt-3 sm:pt-6">
        <div className="flex w-full max-w-3xl flex-col text-white lg:max-w-2xl">
          <div className="h-6 sm:h-8">
            <p className={`inline-flex rounded-full border border-white/25 bg-white/12 px-3 py-1 text-[11px] sm:px-4 sm:py-1.5 sm:text-xs font-semibold uppercase tracking-widest text-white backdrop-blur-sm ${activeCampaign.eyebrow ? '' : 'invisible'}`}>
              {activeCampaign.eyebrow || 'Featured'}
            </p>
          </div>
          <div className="mt-2 sm:mt-4 min-h-[5.5rem] sm:min-h-[9rem] lg:min-h-[10rem]">
            <h1 className="max-w-2xl text-2xl font-medium leading-tight text-white drop-shadow-lg sm:text-4xl lg:text-5xl" style={{ fontFamily: 'var(--font-serif)' }}>
              {activeCampaign.title}
              {activeCampaign.emphasis && <><br /><em className="text-[#F6D7C9]">{activeCampaign.emphasis}</em></>}
            </h1>
            <p className="mt-2 max-w-xl text-xs leading-relaxed text-white/85 drop-shadow line-clamp-2 sm:text-base sm:line-clamp-none">{activeCampaign.description}</p>
          </div>

          <div className="mt-3 sm:mt-6 flex flex-wrap gap-2.5 sm:gap-3">
            <button onClick={onShop} className="flex items-center gap-2 rounded-full bg-[#C4622D] px-5 py-2.5 sm:px-7 sm:py-3.5 text-xs sm:text-base font-semibold text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-[#D4795A]">
              Shop Collection <ArrowRightIcon size={16} />
            </button>
            <button onClick={onCustom} className="hidden sm:inline-flex rounded-full border-2 border-white/80 bg-black/10 px-7 py-3.5 font-semibold text-white backdrop-blur-sm transition hover:bg-white hover:text-[#2C1810]">
              Create Something Custom
            </button>
          </div>

          <p className="sr-only" aria-live="polite">Slide {activeIndex + 1} of {campaigns.length}: {activeCampaign.title}</p>
        </div>

      </div>

      {campaigns.length > 1 && (
        <div
          className="absolute bottom-2 sm:bottom-4 flex justify-center px-4"
          style={{ left: 0, right: 0, width: '100%' }}
          role="group"
          aria-label="Choose featured campaign"
        >
          <div className="flex items-center gap-2 sm:gap-3 rounded-full border border-white/20 bg-black/25 p-1 sm:p-2 backdrop-blur-md">
            <button
              onClick={showPrevious}
              aria-label="Previous promotion"
              className="hero-control-hitbox relative flex h-9 w-9 items-center justify-center rounded-full border border-white/35 text-white transition hover:border-white hover:bg-white hover:text-[#2C1810]"
            >
              <ChevronLeftIcon size={18} />
            </button>
            <div className="flex items-center gap-1 sm:gap-2">
              {campaigns.map((campaign, index) => (
                <button
                  key={campaign.id}
                  onClick={() => setActiveIndex(index)}
                  aria-label={`Show ${campaign.eyebrow ?? campaign.title}`}
                  aria-current={index === activeIndex ? 'true' : undefined}
                  className="flex min-h-[44px] min-w-[28px] items-center justify-center p-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
                >
                  <span className={`block h-2 sm:h-2.5 rounded-full transition-all ${index === activeIndex ? 'w-5 sm:w-7 bg-white' : 'w-2 sm:w-2.5 bg-white/45 hover:bg-white/75'}`} />
                </button>
              ))}
            </div>
            <button
              onClick={showNext}
              aria-label="Next promotion"
              className="hero-control-hitbox relative flex h-9 w-9 items-center justify-center rounded-full border border-white/35 text-white transition hover:border-white hover:bg-white hover:text-[#2C1810]"
            >
              <ChevronRightIcon size={18} />
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
