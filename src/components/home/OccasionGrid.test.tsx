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
});
