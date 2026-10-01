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
    expect(container.querySelector('section')).toHaveClass('h-[46rem]', 'overflow-hidden', 'bg-[#2C1810]');
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

  it('moves between campaigns using accessible controls', () => {
    render(<HeroCarousel campaigns={campaigns} onShop={vi.fn()} onCustom={vi.fn()} />);
    const frame = screen.getByTestId('hero-slide-frame');
    expect(frame).toHaveClass('h-[calc(100%-7rem)]', 'max-w-7xl');
    expect(screen.getByLabelText('Choose featured campaign')).toHaveClass('justify-center', 'bottom-4');
    expect(screen.getByLabelText('Choose featured campaign')).toHaveStyle({ left: '0px', right: '0px', width: '100%' });
    expect(screen.getByTestId('hero-image')).toHaveAttribute('src', campaigns[0].imageUrl);
    fireEvent.click(screen.getByRole('button', { name: /next promotion/i }));
    expect(screen.getByText('Second campaign')).toBeInTheDocument();
    expect(screen.getByTestId('hero-slide-frame')).toBe(frame);
    expect(screen.getByTestId('hero-image')).toHaveAttribute('src', campaigns[1].imageUrl);
    fireEvent.click(screen.getByRole('button', { name: /previous promotion/i }));
    expect(screen.getByText('First campaign')).toBeInTheDocument();
  });
});
