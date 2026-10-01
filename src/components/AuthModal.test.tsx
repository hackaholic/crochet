import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import AuthModal from './AuthModal';

describe('AuthModal', () => {
  it('keeps phone sign-in inside an accessible popup', () => {
    render(<AuthModal open onClose={vi.fn()} onSignedIn={vi.fn()} />);

    expect(screen.getByRole('dialog', { name: /welcome to sulocraft/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/mobile number/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /continue with google/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /continue with facebook/i })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/mobile number/i), { target: { value: '9876-543-210' } });
    expect(screen.getByRole('button', { name: /continue with phone/i })).toBeEnabled();
  });
});

