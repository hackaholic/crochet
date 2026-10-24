import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import AuthDialogFrame, { AuthDialogHeader, AuthLoading } from './AuthDialogFrame';
afterEach(cleanup);
describe('stable centered authentication shell', () => {
  it('uses the same frame/header/body for lazy loading and the live form', () => {
    const close = vi.fn();
    const { container, rerender } = render(<AuthLoading onClose={close} />);
    const layer = container.firstElementChild?.className;
    const frame = container.querySelector('.auth-dialog-frame')?.className;
    expect(screen.getByRole('status')).toHaveTextContent('Loading sign-in');
    rerender(<AuthDialogFrame onClose={close}><AuthDialogHeader onClose={close} /><div className="auth-dialog-body">Live form</div></AuthDialogFrame>);
    expect(container.firstElementChild?.className).toBe(layer);
    expect(container.querySelector('.auth-dialog-frame')?.className).toBe(frame);
    expect(screen.getByRole('dialog', { name: 'Welcome to Sulocraft' })).toBeInTheDocument();
  });
  it('supports Escape and an explicit close button during loading', () => {
    const close = vi.fn();
    render(<AuthLoading onClose={close} />);
    const button = screen.getAllByRole('button', { name: 'Close sign in' })[1];
    expect(button).toHaveFocus();
    fireEvent.keyDown(button, { key: 'Escape' });
    fireEvent.click(button);
    expect(close).toHaveBeenCalledTimes(2);
  });
  it('contains keyboard focus and restores the original trigger on unmount', () => {
    const trigger = document.createElement('button');
    document.body.append(trigger); trigger.focus();
    const close = vi.fn();
    const { unmount } = render(<AuthDialogFrame onClose={close}><AuthDialogHeader onClose={close} /><div className="auth-dialog-body"><input aria-label="Email" /><button>Continue</button></div></AuthDialogFrame>);
    const first = screen.getAllByRole('button', { name: 'Close sign in' })[1];
    fireEvent.keyDown(first, { key: 'Tab', shiftKey: true });
    expect(screen.getByRole('button', { name: 'Continue' })).toHaveFocus();
    fireEvent.keyDown(screen.getByRole('button', { name: 'Continue' }), { key: 'Tab' });
    expect(first).toHaveFocus();
    unmount(); expect(trigger).toHaveFocus(); trigger.remove();
  });
});
