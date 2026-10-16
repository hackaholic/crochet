import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import DestinationLink from './DestinationLink';
afterEach(cleanup);
it('preserves href and calls SPA navigation only for ordinary clicks', () => {
  const navigate = vi.fn();
  render(<DestinationLink href="/categories/flowers" onNavigate={navigate}>Flowers</DestinationLink>);
  const link = screen.getByRole('link', { name: 'Flowers' });
  expect(link).toHaveAttribute('href', '/categories/flowers');
  fireEvent.click(link, { ctrlKey:true }); fireEvent.click(link, { metaKey:true }); fireEvent.click(link, { shiftKey:true }); fireEvent.click(link, { button:1 });
  expect(navigate).not.toHaveBeenCalled();
  fireEvent.click(link); expect(navigate).toHaveBeenCalledOnce();
});
it('rejects unsafe destinations without interactive anchors', () => {
  const { rerender } = render(<DestinationLink href="javascript:alert(1)">Bad</DestinationLink>);
  for (const href of ['//evil.example','/\\evil','https://user:password@example.com','/path\n']) {
    rerender(<DestinationLink href={href}>Bad</DestinationLink>);
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  }
});
