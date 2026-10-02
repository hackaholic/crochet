import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import OccasionsPage from './OccasionsPage';
import type { AdminOccasion } from '../types';
import * as api from '../services/api';

vi.mock('../services/api', () => ({
  getAdminOccasions: vi.fn(),
  updateAdminOccasion: vi.fn(),
}));

const occasions: AdminOccasion[] = [
  { id: 'birthday', name: 'Birthday', displayOrder: 1, isEnabled: true, isEvergreen: true, productCount: 2, productIds: [] },
  { id: 'seasonal-1', name: 'Festival', displayOrder: 2, isEnabled: false, isEvergreen: false, productCount: 1, productIds: [] },
];

describe('OccasionsPage', () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it('keeps backend-marked evergreen occasions always visible and locks their toggle', async () => {
    vi.mocked(api.getAdminOccasions).mockResolvedValue(occasions);
    render(<OccasionsPage />);

    const toggle = await screen.findByRole('checkbox', { name: 'Show Birthday on storefront' });
    expect(toggle).toBeChecked();
    expect(toggle).toBeDisabled();
    expect(screen.getByText('Always on')).toBeInTheDocument();
  });

  it('lets admin enable a seasonal occasion through the API', async () => {
    vi.mocked(api.getAdminOccasions).mockResolvedValue(occasions);
    vi.mocked(api.updateAdminOccasion).mockResolvedValue({ ...occasions[1], isEnabled: true });
    render(<OccasionsPage />);

    const toggle = await screen.findByRole('checkbox', { name: 'Show Festival on storefront' });
    fireEvent.click(toggle);

    await waitFor(() => expect(api.updateAdminOccasion).toHaveBeenCalledWith('seasonal-1', { isEnabled: true }));
    await waitFor(() => expect(screen.getByRole('checkbox', { name: 'Show Festival on storefront' })).toBeChecked());
  });

  it('saves seasonal dates as inclusive Asia/Kolkata boundaries and can clear a date', async () => {
    vi.mocked(api.getAdminOccasions).mockResolvedValue(occasions);
    vi.mocked(api.updateAdminOccasion).mockResolvedValue({ ...occasions[1], startsAt: '2026-10-10T00:00:00+05:30', endsAt: null });
    render(<OccasionsPage />);

    const start = await screen.findByLabelText('Starts (India time)');
    const end = screen.getByLabelText('Ends (India time)');
    fireEvent.change(start, { target: { value: '2026-10-10' } });
    fireEvent.change(end, { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save schedule' }));

    await waitFor(() => expect(api.updateAdminOccasion).toHaveBeenCalledWith('seasonal-1', {
      startsAt: '2026-10-10T00:00:00+05:30', endsAt: null,
    }));
  });

  it('fails closed when backend evergreen metadata is missing', async () => {
    vi.mocked(api.getAdminOccasions).mockResolvedValue([{ ...occasions[0], isEvergreen: null }]);
    render(<OccasionsPage />);

    expect(await screen.findByText(/backend has not identified evergreen status yet/i)).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: 'Show Birthday on storefront' })).toBeDisabled();
  });
});
