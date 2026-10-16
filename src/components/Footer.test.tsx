import { cleanup, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { afterEach, expect, it, vi } from 'vitest';
import Footer from './Footer';
vi.mock('./CatalogueProvider', () => ({ useCatalogue: () => ({ categories: [{id:1,name:'Flowers',slug:'flowers',isActive:true},{id:2,name:'Disabled',slug:'disabled',isActive:false}], collections:[{id:1,name:'Gifts',slug:'gifts'}] }) }));
vi.mock('../lib/seo/bootstrap',()=>({ usePublicBootstrap:()=>({home:{brand:{instagramUrl:'https://instagram.com/example',name:'Brand'}}}) }));
vi.mock('./BrandLogo',()=>({ default:()=> <span>Logo</span> }));
afterEach(cleanup);
it('renders real catalogue destinations, policy links and configured socials only',()=>{
  render(<MemoryRouter><Footer onNavigate={vi.fn()} /></MemoryRouter>);
  expect(screen.getByRole('link',{name:'Flowers'})).toHaveAttribute('href','/categories/flowers');
  expect(screen.getByRole('link',{name:'Gifts'})).toHaveAttribute('href','/collections/gifts');
  expect(screen.queryByText('Disabled')).not.toBeInTheDocument();
  expect(screen.getByRole('link',{name:'Privacy'})).toHaveAttribute('href','/privacy-policy');
  expect(screen.queryByRole('link',{name:'New Arrivals'})).not.toBeInTheDocument();
  expect(screen.getByRole('button',{name:'Subscribe'})).toBeInTheDocument();
  expect(screen.queryByRole('link',{name:'Facebook'})).not.toBeInTheDocument();
});
