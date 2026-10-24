import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import SearchDialogFrame, { SearchLoading } from './SearchDialogFrame';
afterEach(cleanup);
describe('stable search dialog shell', () => {
  it('shares its shell and scroll-panel geometry hooks across loading and loaded states', () => {
    const { container, rerender } = render(<SearchLoading onClose={vi.fn()} />);
    const layer = container.firstElementChild?.className;
    const frame = container.querySelector('.search-dialog-frame')?.className;
    expect(container.querySelector('.search-dialog-results')).toBeInTheDocument();
    rerender(<SearchDialogFrame onClose={vi.fn()}><div className="search-dialog-results">Live content</div></SearchDialogFrame>);
    expect(container.firstElementChild?.className).toBe(layer);
    expect(container.querySelector('.search-dialog-frame')?.className).toBe(frame);
    expect(screen.getByRole('dialog', { name: 'Search products' })).toBeInTheDocument();
  });
  it('lets customers close the code-loading state with Escape or the close button', () => {
    const onClose = vi.fn();
    render(<SearchLoading onClose={onClose} />);
    const close = screen.getAllByRole('button', { name: 'Close search' })[1];
    expect(close).toHaveFocus();
    fireEvent.keyDown(close, { key: 'Escape' });
    fireEvent.click(close);
    expect(onClose).toHaveBeenCalledTimes(2);
  });
});
