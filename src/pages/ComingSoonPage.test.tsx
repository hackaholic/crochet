import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import ComingSoonPage from './ComingSoonPage';

describe('ComingSoonPage', () => {
  it('introduces Sulocraft without requiring the storefront API', () => {
    render(<ComingSoonPage />);
    expect(screen.getByRole('heading', { name: /something beautiful/i })).toBeInTheDocument();
    expect(screen.getByText(/Sulocraft is bringing/i)).toBeInTheDocument();
  });
});
