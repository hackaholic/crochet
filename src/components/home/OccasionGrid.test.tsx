import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import OccasionGrid from './OccasionGrid';

describe('OccasionGrid', () => {
  it('renders backend occasion order unchanged so active seasonal cards can lead', () => {
    const onNavigate = vi.fn();
    render(<OccasionGrid
      section={{
        id: 1, order: 4, enabled: true, type: 'occasion_grid', title: 'Gift by Occasion',
        occasions: [
          { id: 'diwali', name: 'Diwali', imageUrl: '/diwali.png' },
          { id: 'birthday', name: 'Birthday', imageUrl: '/birthday.png' },
        ],
      }}
      onNavigate={onNavigate}
    />);

    const cards = screen.getAllByRole('button');
    expect(cards.map(card => card.textContent)).toEqual(['Diwali', 'Birthday']);
    fireEvent.click(cards[0]);
    expect(onNavigate).toHaveBeenCalledWith('/shop?occasion=diwali');
  });

  it('shows the API-provided icon instead of a broken image when an occasion asset fails', () => {
    const { container } = render(<OccasionGrid
      section={{
        id: 1, order: 4, enabled: true, type: 'occasion_grid', title: 'Gift by Occasion',
        occasions: [{ id: 'babyshower', name: 'Baby Shower', icon: '🍼', imageUrl: '/missing-image.png' }],
      }}
      onNavigate={vi.fn()}
    />);

    fireEvent.error(container.querySelector('img')!);

    expect(screen.queryByRole('img', { hidden: true })).not.toBeInTheDocument();
    expect(screen.getByText('🍼')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Shop gifts for Baby Shower' })).toBeInTheDocument();
  });
});
