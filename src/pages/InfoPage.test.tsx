import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import InfoPage from './InfoPage';
import { getStorefrontContent } from '../lib/api/storefront';

vi.mock('../lib/api/storefront', () => ({ getStorefrontContent: vi.fn() }));

describe('Contact Us support email', () => {
  afterEach(() => cleanup());
  beforeEach(() => vi.resetAllMocks());

  it('renders the configured support mailbox as a mailto link', async () => {
    vi.mocked(getStorefrontContent).mockResolvedValueOnce({
      brand: { name: 'Sulocraft', ownerName: 'Anupama Sharma', supportEmail: 'support@sulocraft.com' },
      heroCampaigns: [],
    });

    render(<InfoPage kind="contact" onNavigate={vi.fn()} />);

    const link = await screen.findByRole('link', { name: 'support@sulocraft.com' });
    expect(link).toHaveAttribute('href', 'mailto:support@sulocraft.com');
  });

  it('omits the email link when the public configuration has no mailbox', async () => {
    vi.mocked(getStorefrontContent).mockResolvedValueOnce({
      brand: { name: 'Sulocraft', ownerName: 'Anupama Sharma', supportEmail: null },
      heroCampaigns: [],
    });

    render(<InfoPage kind="contact" onNavigate={vi.fn()} />);

    await waitFor(() => {
      expect(getStorefrontContent).toHaveBeenCalledOnce();
      expect(screen.queryByRole('link', { name: /support@sulocraft.com/i })).not.toBeInTheDocument();
    });
  });
});
