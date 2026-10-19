import DestinationLink from './DestinationLink';
import { pagePath } from '../lib/routes';
import { useState, useEffect, useRef } from 'react';
import { useHeaderOffset } from '../hooks/useHeaderOffset';
import { useNavigate } from 'react-router';
import { SearchIcon, HeartIcon, ShoppingBagIcon, UserIcon, MenuIcon, XIcon, YarnLogo } from './Icons';
import type { AppPage } from '../lib/routes';
import { useCatalogue } from './CatalogueProvider';

type Page = AppPage;

interface NavLink {
  label: string;
  page?: Page;
  href?: string;
}

interface HeaderProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  cartCount: number;
  wishlistCount: number;
  onSearchOpen: () => void;
  onCartOpen: () => void;
  onAccountOpen: () => void;
}

const baseNavLinks: NavLink[] = [
  { label: 'Home', page: 'home' as Page },
  { label: 'Shop', page: 'shop' as Page },
];

function useSafeNavigate() {
  try {
    return useNavigate();
  } catch {
    return null;
  }
}

export default function Header({ currentPage, onNavigate, cartCount, wishlistCount, onSearchOpen, onCartOpen, onAccountOpen }: HeaderProps) {
  const headerRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  useHeaderOffset(headerRef, menuRef);
  const navigate = useSafeNavigate();
  const { categories } = useCatalogue();
  const navLinks: NavLink[] = [
    ...baseNavLinks,
    ...categories.filter(category => category.isActive !== false).slice(0, 3).map(category => ({ label: category.name, href: `/categories/${encodeURIComponent(category.slug)}` })),
    { label: 'Custom Orders', href: '/contact?subject=custom-order' },
    { label: 'About Us', page: 'about' as Page },
  ];
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleNavClick = (page?: Page, href?: string) => {
    if (href) {
      if (navigate) {
        navigate(href);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        window.location.assign(href);
      }
    } else if (page) {
      onNavigate(page);
    }
  };

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 60);
    window.addEventListener('scroll', handler);
    return () => window.removeEventListener('scroll', handler);
  }, []);

  return (
    <div ref={headerRef} data-testid="storefront-fixed-header" className="fixed top-0 left-0 right-0 z-50">
      {/* Announcement bar */}
      <div className="bg-[#2C1810] text-white text-center py-2 text-xs font-medium tracking-wide">
        <span>Free shipping on orders above ₹999</span>
        <span className="mx-3 opacity-40">|</span>
        <span>Handmade with love in India 🇮🇳</span>
      </div>

      {/* Main header */}
      <header
        className={`storefront-nav transition-all duration-300 ${scrolled ? 'bg-white/95 backdrop-blur-md shadow-sm py-3' : 'bg-[#FAF7F2] py-4'}`}
        style={{ borderBottom: '1px solid #EDE4D0' }}
      >
        <div className="storefront-nav-row storefront-shell flex items-center justify-between gap-4">
          {/* Logo */}
          <DestinationLink href="/"
            onNavigate={() => onNavigate('home')}
            aria-label="Sulocraft home"
            className="storefront-nav-brand flex items-center gap-2.5 shrink-0"
          >
            <YarnLogo size={38} wordmark />
          </DestinationLink>

          {/* Desktop nav */}
          <nav className="hidden lg:flex items-center gap-6">
            {navLinks.map(({ label, page, href }) => (
              <DestinationLink href={href ?? pagePath(page as Exclude<Page, 'product' | 'notFound'>)}
                key={label}
                onNavigate={() => handleNavClick(page, href)}
                aria-current={currentPage === page ? 'page' : undefined}
                className={`text-sm font-medium transition-colors hover:text-[#C4622D] ${currentPage === page && label === 'Home' ? 'text-[#C4622D]' : 'text-[#5C3D2E]'}`}
              >
                {label}
              </DestinationLink>
            ))}
          </nav>

          {/* Icons */}
          <div className="storefront-nav-actions flex items-center gap-1">
            <button onClick={onSearchOpen} className="p-2.5 rounded-full hover:bg-[#F5EDE0] text-[#5C3D2E] hover:text-[#C4622D] transition-colors" aria-label="Search">
              <SearchIcon size={20} />
            </button>
            <button onClick={onAccountOpen} className="p-2.5 rounded-full hover:bg-[#F5EDE0] text-[#5C3D2E] hover:text-[#C4622D] transition-colors hidden md:flex" aria-label="Account">
              <UserIcon size={20} />
            </button>
            <button
              onClick={() => onNavigate('wishlist')}
              className="p-2.5 rounded-full hover:bg-[#F5EDE0] text-[#5C3D2E] hover:text-[#C4622D] transition-colors relative"
              aria-label="Wishlist"
            >
              <HeartIcon size={20} />
              {wishlistCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-[#C4622D] text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                  {wishlistCount}
                </span>
              )}
            </button>
            <button
              onClick={onCartOpen}
              className="p-2.5 rounded-full hover:bg-[#F5EDE0] text-[#5C3D2E] hover:text-[#C4622D] transition-colors relative"
              aria-label="Cart"
            >
              <ShoppingBagIcon size={20} />
              {cartCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-[#C4622D] text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </button>
            {/* Mobile hamburger */}
            <button
              className="p-2.5 rounded-full hover:bg-[#F5EDE0] text-[#5C3D2E] lg:hidden"
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label="Menu"
              aria-expanded={mobileOpen}
              aria-controls="storefront-mobile-menu"
            >
              {mobileOpen ? <XIcon size={22} /> : <MenuIcon size={22} />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div ref={menuRef} id="storefront-mobile-menu" className="lg:hidden border-t border-[#EDE4D0] bg-white px-4 pb-4 pt-2">
            {navLinks.map(({ label, page, href }) => (
              <DestinationLink href={href ?? pagePath(page as Exclude<Page, 'product' | 'notFound'>)}
                key={label}
                onNavigate={() => { handleNavClick(page, href); setMobileOpen(false); }}
                className="block w-full text-left py-3 text-sm font-medium text-[#5C3D2E] border-b border-[#F5EDE0] hover:text-[#C4622D] transition-colors"
              >
                {label}
              </DestinationLink>
            ))}
            <button
              onClick={() => { onNavigate('cart'); setMobileOpen(false); }}
              className="block w-full text-left py-3 text-sm font-medium text-[#5C3D2E] hover:text-[#C4622D] transition-colors"
            >
              Cart {cartCount > 0 && `(${cartCount})`}
            </button>
            <button
              onClick={() => { onAccountOpen(); setMobileOpen(false); }}
              className="block w-full text-left py-3 text-sm font-medium text-[#5C3D2E] hover:text-[#C4622D] transition-colors"
            >
              Account
            </button>
          </div>
        )}
      </header>
    </div>
  );
}
