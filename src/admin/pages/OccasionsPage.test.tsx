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

  it('lets admin hide a year-round occasion without a frontend always-on override', async () => {
    vi.mocked(api.getAdminOccasions).mockResolvedValue(occasions);
    render(<OccasionsPage />);

    vi.mocked(api.updateAdminOccasion).mockResolvedValue({...occasions[0], isEnabled:false});
    const toggle = await screen.findByRole('checkbox', { name: 'Show Birthday on storefront' });
    expect(toggle).toBeChecked();
    expect(toggle).toBeEnabled();
    fireEvent.click(toggle);
    await waitFor(() => expect(api.updateAdminOccasion).toHaveBeenCalledWith('birthday', {isEnabled:false}));
    await waitFor(() => expect(screen.getByRole('checkbox', {name:'Show Birthday on storefront'})).not.toBeChecked());
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

    const start = (await screen.findAllByLabelText('Starts (India time)'))[1];
    const end = screen.getAllByLabelText('Ends (India time)')[1];
    fireEvent.change(start, { target: { value: '2026-10-10' } });
    fireEvent.change(end, { target: { value: '' } });
    fireEvent.click(screen.getAllByRole('button', { name: 'Save schedule' })[1]);

    await waitFor(() => expect(api.updateAdminOccasion).toHaveBeenCalledWith('seasonal-1', {
      startsAt: '2026-10-10T00:00:00+05:30', endsAt: null,
    }));
  });

  it('keeps the server state and reports a rejected visibility update', async () => {
    vi.mocked(api.getAdminOccasions).mockResolvedValue([occasions[0]]);
    vi.mocked(api.updateAdminOccasion).mockRejectedValue(new Error('Forbidden'));
    render(<OccasionsPage />);
    fireEvent.click(await screen.findByRole('checkbox', {name:'Show Birthday on storefront'}));
    expect(await screen.findByRole('alert')).toHaveTextContent('The change was not saved');
    expect(screen.getByRole('checkbox', {name:'Show Birthday on storefront'})).toBeChecked();
    expect(api.getAdminOccasions).toHaveBeenCalledTimes(1);
  });

  it('does not require legacy evergreen metadata for server-controlled visibility', async () => {
    vi.mocked(api.getAdminOccasions).mockResolvedValue([{ ...occasions[0], isEvergreen: null }]);
    render(<OccasionsPage />);

    expect(await screen.findByRole('checkbox', { name: 'Show Birthday on storefront' })).toBeEnabled();
    expect(screen.getByLabelText('Starts (India time)')).toBeEnabled();
  });
});
