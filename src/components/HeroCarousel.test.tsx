import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import HeroCarousel from './HeroCarousel';
import type { HomepageCampaign } from '../lib/api/storefront';

const campaigns: HomepageCampaign[] = [
  { id: 1, title: 'First campaign', emphasis: 'Handmade', description: 'First description', eyebrow: 'New', imageUrl: 'https://images.example/one.webp', imageAlt: 'First campaign image', priority: 1 },
  { id: 2, title: 'Second campaign', description: 'Second description', eyebrow: 'Festive', imageUrl: 'https://images.example/two.webp', imageAlt: 'Second campaign image', priority: 2 },
];

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', { writable: true, value: vi.fn().mockReturnValue({ matches: false }) });
});

afterEach(cleanup);

describe('HeroCarousel', () => {
  it('uses the full-width hero frame while campaign data is loading', () => {
    const { container } = render(<HeroCarousel campaigns={[]} loading onShop={vi.fn()} onCustom={vi.fn()} />);
    expect(screen.getByText('Loading homepage campaigns')).toBeInTheDocument();
    expect(container.querySelector('section')).toHaveClass('h-[408px]', 'sm:h-[540px]', 'lg:h-[620px]', 'overflow-hidden', 'bg-[#2C1810]');
    expect(container.querySelector('.lg\\:grid-cols-2')).not.toBeInTheDocument();
  });

  it('renders API campaign content and keeps both template actions', () => {
    const onShop = vi.fn();
    const onCustom = vi.fn();
    render(<HeroCarousel campaigns={campaigns} onShop={onShop} onCustom={onCustom} />);

    expect(screen.getByText('First campaign')).toBeInTheDocument();
    expect(screen.getByText('Handmade')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /shop collection/i }));
    fireEvent.click(screen.getByRole('button', { name: /create something custom/i }));
    expect(onShop).toHaveBeenCalledOnce();
    expect(onCustom).toHaveBeenCalledOnce();
  });

  it('keeps the mobile hero compact and prioritizes the single primary action', () => {
    render(<HeroCarousel campaigns={campaigns} onShop={vi.fn()} onCustom={vi.fn()} />);
    const section = screen.getByTestId('hero-section');
    expect(section).toHaveClass('h-[408px]', 'sm:h-[540px]', 'lg:h-[620px]');
    expect(section.className).not.toMatch(/h-\[(?:100vh|100svh)/);
    expect(screen.getByRole('button', { name: /create something custom/i })).toHaveClass('hidden', 'sm:inline-flex');
    expect(screen.getByTestId('hero-slide-frame')).toHaveClass('h-[calc(100%-6rem)]', 'sm:h-[calc(100%-7rem)]');
  });

  it('uses optional API mobile art and focal position while retaining the desktop fallback', () => {
    const campaign = {
      ...campaigns[0],
      mobileImageUrl: 'https://images.example/one-mobile.webp',
      mobileImagePosition: { x: 42, y: 35 },
    };
    const { container } = render(<HeroCarousel campaigns={[campaign]} onShop={vi.fn()} onCustom={vi.fn()} />);
    const source = container.querySelector('picture source');
    const image = screen.getByTestId('hero-image');

    expect(source).toHaveAttribute('media', '(max-width: 639px)');
    expect(source).toHaveAttribute('srcset', campaign.mobileImageUrl);
    expect(image).toHaveAttribute('src', campaign.imageUrl);
    expect(image.parentElement).toHaveStyle({ '--hero-mobile-object-position': '42% 35%' });
  });

  it('moves between campaigns using accessible controls', () => {
    render(<HeroCarousel campaigns={campaigns} onShop={vi.fn()} onCustom={vi.fn()} />);
    const frame = screen.getByTestId('hero-slide-frame');
    expect(frame).toHaveClass('h-[calc(100%-6rem)]', 'sm:h-[calc(100%-7rem)]', 'storefront-shell');
    expect(frame).not.toHaveClass('max-w-7xl');
    expect(screen.getByRole('group', { name: 'Choose featured campaign' })).toHaveClass('justify-center', 'bottom-2', 'sm:bottom-4');
    expect(screen.getByRole('group', { name: 'Choose featured campaign' })).toHaveStyle({ left: '0px', right: '0px', width: '100%' });
    expect(screen.getByTestId('hero-image')).toHaveAttribute('src', campaigns[0].imageUrl);
    fireEvent.click(screen.getByRole('button', { name: /next promotion/i }));
    expect(screen.getByText('Second campaign')).toBeInTheDocument();
    expect(screen.getByTestId('hero-slide-frame')).toBe(frame);
    expect(screen.getByTestId('hero-image')).toHaveAttribute('src', campaigns[1].imageUrl);
    expect(screen.getByTestId('hero-image')).toHaveAttribute('loading', 'lazy');
    expect(screen.getByTestId('hero-image')).toHaveAttribute('fetchpriority', 'low');
    fireEvent.click(screen.getByRole('button', { name: /previous promotion/i }));
    expect(screen.getByText('First campaign')).toBeInTheDocument();
  });

  it('supports touch swipe navigation on mobile devices without interfering with vertical scroll', () => {
    render(<HeroCarousel campaigns={campaigns} onShop={vi.fn()} onCustom={vi.fn()} />);
    const section = screen.getByTestId('hero-section');
    expect(section).toHaveClass('touch-pan-y');

    // Horizontal swipe left (next slide)
    fireEvent.touchStart(section, { touches: [{ clientX: 200, clientY: 100 }] });
    fireEvent.touchEnd(section, { changedTouches: [{ clientX: 130, clientY: 105 }] });
    expect(screen.getByText('Second campaign')).toBeInTheDocument();

    // Horizontal swipe right (previous slide)
    fireEvent.touchStart(section, { touches: [{ clientX: 100, clientY: 100 }] });
    fireEvent.touchEnd(section, { changedTouches: [{ clientX: 180, clientY: 105 }] });
    expect(screen.getByText('First campaign')).toBeInTheDocument();

    // Vertical swipe (should NOT change slide)
    fireEvent.touchStart(section, { touches: [{ clientX: 100, clientY: 100 }] });
    fireEvent.touchEnd(section, { changedTouches: [{ clientX: 105, clientY: 200 }] });
    expect(screen.getByText('First campaign')).toBeInTheDocument();
  });

  it('supports keyboard navigation using arrow keys', () => {
    render(<HeroCarousel campaigns={campaigns} onShop={vi.fn()} onCustom={vi.fn()} />);
    const section = screen.getByTestId('hero-section');

    fireEvent.keyDown(section, { key: 'ArrowRight' });
    expect(screen.getByText('Second campaign')).toBeInTheDocument();

    fireEvent.keyDown(section, { key: 'ArrowLeft' });
    expect(screen.getByText('First campaign')).toBeInTheDocument();
  });

  it('does not auto-advance when reduced motion is requested', () => {
    const originalMatchMedia = window.matchMedia;
    vi.useFakeTimers();
    window.matchMedia = vi.fn().mockReturnValue({ matches: true }) as unknown as typeof window.matchMedia;
    try {
      render(<HeroCarousel campaigns={campaigns} onShop={vi.fn()} onCustom={vi.fn()} />);
      vi.advanceTimersByTime(12_000);
      expect(screen.getByText('First campaign')).toBeInTheDocument();
    } finally {
      vi.useRealTimers();
      window.matchMedia = originalMatchMedia;
    }
  });

  it('keeps phone arrows touch-sized with compact pagination targets', () => {
    render(<HeroCarousel campaigns={campaigns} onShop={vi.fn()} onCustom={vi.fn()} />);
    const prevBtn = screen.getByRole('button', { name: /previous promotion/i });
    const nextBtn = screen.getByRole('button', { name: /next promotion/i });
    expect(prevBtn).toHaveClass('h-9', 'w-9', 'hero-control-hitbox');
    expect(nextBtn).toHaveClass('h-9', 'w-9', 'hero-control-hitbox');

    const dotBtn = screen.getByRole('button', { name: /show new/i });
    expect(dotBtn).toHaveClass('min-h-[44px]', 'min-w-[28px]');
  });

  it('optimizes first-slide LCP with eager loading and high fetch priority', () => {
    render(<HeroCarousel campaigns={campaigns} onShop={vi.fn()} onCustom={vi.fn()} />);
    const image = screen.getByTestId('hero-image');
    expect(image).toHaveAttribute('loading', 'eager');
    expect(image).toHaveAttribute('fetchpriority', 'high');
    expect(image).toHaveAttribute('decoding', 'async');
    expect(image).toHaveAttribute('sizes', '(max-width: 639px) 100vw, (max-width: 1023px) 100vw, 1280px');
  });
});
