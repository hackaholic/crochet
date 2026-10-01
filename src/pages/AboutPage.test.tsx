import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import AboutPage from './AboutPage';

describe('AboutPage', () => {
  it('renders the authentic Sulocraft family story without fictional team claims', () => {
    render(<AboutPage onNavigate={vi.fn()} />);

    expect(screen.getAllByText(/Anupama Sharma/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/named after my mother, Sulochana/i)).toBeInTheDocument();
    expect(screen.getByText(/still hanging at my aunt's house/i)).toBeInTheDocument();
    expect(screen.queryByText(/Kavya Reddy/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/12 artisans/i)).not.toBeInTheDocument();
  });
});
