import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import BrandLogo from './BrandLogo';
vi.mock('../lib/api/storefront', () => ({ getStorefrontContent: vi.fn().mockResolvedValue({brand:{logoUrl:'/static/images/brand/logo.png'}}) }));
afterEach(cleanup);
it('loads the API-supplied same-origin logo without a loopback host', async () => {
  render(<BrandLogo />);
  expect(await screen.findByRole('img', {name:'Sulocraft logo'})).toHaveAttribute('src','/static/images/brand/logo.png');
});
