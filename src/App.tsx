import { AuthLoading } from './components/AuthDialogFrame';
import { SearchLoading } from './components/SearchDialogFrame';
import { isPrivatePath } from './lib/seo/urlPolicy.mjs';
import { usePublicBootstrap } from './lib/seo/bootstrap';
import { useState, useCallback, useEffect, lazy, Suspense } from 'react';
import { useLocation, useNavigate } from 'react-router';
import Header from './components/Header';
import Footer from './components/Footer';
import CartDrawer from './components/CartDrawer';
const SearchOverlay = lazy(() => import('./components/SearchOverlay'));
import HomePage from './pages/HomePage';
import ShopPage from './pages/ShopPage';
import ProductPage from './pages/ProductPage';
import CartPage from './pages/CartPage';
import WishlistPage from './pages/WishlistPage';
const CheckoutPage = lazy(() => import('./pages/CheckoutPage'));
import AboutPage from './pages/AboutPage';
import InfoPage from './pages/InfoPage';
import GuestTrackingPage from './pages/GuestTrackingPage';
const AccountPage = lazy(() => import('./pages/AccountPage'));
const AdminPage = lazy(() => import('./pages/AdminPage'));
import type { Product } from './data/products';
import { normalizePathname, pageFromPath, pagePath, productPath, productSlug, type AppPage } from './lib/routes';
import { useCatalogue } from './components/CatalogueProvider';
import { ErrorState, LoadingState } from './components/StorefrontState';
import { useCart } from './components/CartProvider';
const AuthModal = lazy(() => import('./components/AuthModal'));
import { authApi, type User } from './lib/api/auth';
import { useWishlist } from './components/WishlistProvider';
import SeoManager from './components/SeoManager';
import type { SeoMetadata } from './lib/api/seo';

export default function App() {
  const location = useLocation();
  const navigateTo = useNavigate();
  const initial = usePublicBootstrap();
  const [pageHeading, setPageHeading] = useState<{ path: string; h1?: string | null; metadata?: SeoMetadata } | undefined>(initial ? { path: initial.path, h1: initial.metadata.h1, metadata: initial.metadata } : undefined);
  const onSeoMetadata = useCallback((metadata: SeoMetadata) => setPageHeading({ path: normalizePathname(location.pathname), h1: metadata.h1, metadata }), [location.pathname]);
  const requestedPage = new URLSearchParams(location.search).get('page');
  const page = requestedPage !== null && requestedPage !== '1' && !isPrivatePath(location.pathname.toLowerCase().replace(/\/+$/, '') || '/') ? 'notFound' : pageFromPath(location.pathname);
  const { products, categories, loading: catalogueLoading, error: catalogueError, retry: retryCatalogue } = useCatalogue();
  const selectedProduct = page === 'product'
    ? products.find(product => productSlug(product) === normalizePathname(location.pathname).split('/').pop()) ?? null
    : null;
  const showNotFound = page === 'notFound' || (page === 'product' && selectedProduct === null);
  const { items: cart, add: addCartItem, update: updateCartItem, remove: removeCartItem, refresh: refreshCart } = useCart();
  const { ids: wishlist, toggle: toggleServerWishlist, refresh: refreshWishlist } = useWishlist();
  const [cartOpen, setCartOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [authError, setAuthError] = useState('');
  const [authChecked, setAuthChecked] = useState(false);
  const [couponCode, setCouponCode] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const openAuth = useCallback(() => setAuthOpen(true), []);

  useEffect(() => {
    const errorCode = new URLSearchParams(location.search).get('error');
    if (errorCode === 'invalid_link') {
      setAuthError('That sign-in link is invalid, expired, or has already been used. Request a new link below.');
      setAuthOpen(true);
      navigateTo(location.pathname, { replace: true });
    }
  }, [location.pathname, location.search, navigateTo]);

  useEffect(() => {
    let active = true;
    authApi.me()
      .then(currentUser => { if (active) setUser(currentUser); })
      .catch(() => { if (active) setUser(null); })
      .finally(() => { if (active) setAuthChecked(true); });
    return () => { active = false; };
  }, []);

  const navigate = useCallback((p: AppPage) => {
    navigateTo(p === 'product' || p === 'notFound' ? '/shop' : pagePath(p));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [navigateTo]);

  const signOut = useCallback(async () => {
    await authApi.logout();
    setUser(null);
    await Promise.all([refreshCart(), refreshWishlist()]);
    navigate('home');
  }, [navigate, refreshCart, refreshWishlist]);

  const addToCart = useCallback((product: Product, quantity = 1, personalization?: Record<string, unknown>) => {
    void addCartItem(product, quantity, personalization);
    setCartOpen(true);
  }, [addCartItem]);

  const updateCartQty = useCallback((id: number, qty: number) => {
    void updateCartItem(id, qty);
  }, [updateCartItem]);

  const removeFromCart = useCallback((id: number) => {
    void removeCartItem(id);
  }, [removeCartItem]);

  const toggleWishlist = useCallback((product: Product) => {
    if (user) {
      toggleServerWishlist(product);
    } else if (authChecked) {
      openAuth();
    }
  }, [authChecked, openAuth, toggleServerWishlist, user]);

  const handleProductClick = useCallback((product: Product) => {
    navigateTo(productPath(product));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [navigateTo]);

  const handleCheckout = useCallback(() => {
    setCartOpen(false);
    navigate('checkout');
  }, [navigate]);

  const cartCount = cart.reduce((s, i) => s + i.quantity, 0);

  return (
    <div className="min-h-screen" style={{ fontFamily: 'var(--font-sans)' }}>
      <SeoManager categories={categories} page={showNotFound ? 'notFound' : page} pathname={location.pathname} product={selectedProduct} onMetadata={onSeoMetadata} />
      <a href="#main-content" onClick={event => { if (page === 'tracking') { event.preventDefault(); const main = document.getElementById('main-content'); main?.focus(); main?.scrollIntoView(); } }} className="sr-only fixed left-4 top-4 z-100 rounded-full bg-[#2C1810] px-5 py-3 text-sm font-semibold text-white focus:not-sr-only">
        Skip to content
      </a>
      {page !== 'admin' && <Header
        currentPage={page}
        onNavigate={navigate}
        cartCount={cartCount}
        wishlistCount={wishlist.length}
        onSearchOpen={() => setSearchOpen(true)}
        onCartOpen={() => setCartOpen(true)}
        onAccountOpen={() => user ? navigate('account') : openAuth()}
      />}

      <Suspense fallback={<div className="min-h-screen bg-[#FAF7F2] pt-28"><LoadingState label="Loading page…" /></div>}>
      <main id="main-content" tabIndex={-1} className={page === 'admin' ? 'min-h-screen' : undefined}>
        {catalogueLoading && ['home', 'shop', 'product', 'wishlist'].includes(page) ? (
          <div className="min-h-screen bg-[#FAF7F2] pt-28"><LoadingState label="Loading the collection…" /></div>
        ) : catalogueError && ['home', 'shop', 'product', 'wishlist'].includes(page) ? (
          <div className="min-h-screen bg-[#FAF7F2] px-4 pt-36"><ErrorState title="The collection is unavailable right now." description="Please check your connection and try again." action={{ label: 'Try again', onClick: retryCatalogue }} /></div>
        ) : showNotFound ? (
          <InfoPage kind="notFound" onNavigate={navigate} />
        ) : (
          <>
        {page === 'home' && (
          <HomePage
            onNavigate={navigate}
            onAddToCart={addToCart}
            onToggleWishlist={toggleWishlist}
            wishlist={wishlist}
            onProductClick={handleProductClick}
          />
        )}
        {page === 'shop' && (
          <ShopPage
            seoMetadata={pageHeading?.path === normalizePathname(location.pathname) ? pageHeading.metadata : undefined}
            heading={pageHeading?.path === normalizePathname(location.pathname) ? pageHeading.h1 : undefined}
            onAddToCart={addToCart}
            onToggleWishlist={toggleWishlist}
            wishlist={wishlist}
            onProductClick={handleProductClick}
          />
        )}
        {page === 'product' && (
          <ProductPage
            product={selectedProduct}
            seoMetadata={pageHeading?.path === normalizePathname(location.pathname) ? pageHeading.metadata : undefined}
            onAddToCart={addToCart}
            onToggleWishlist={toggleWishlist}
            wishlist={wishlist}
            onProductClick={handleProductClick}
            onNavigate={navigate}
          />
        )}
        {page === 'cart' && (
          <CartPage
            onAddToCart={addCartItem}
            onProductClick={handleProductClick}
            items={cart}
            wishlist={wishlist}
            onUpdateQty={updateCartQty}
            onRemove={removeFromCart}
            onWishlist={toggleWishlist}
            onCheckout={handleCheckout}
            onCouponChange={setCouponCode}
            onNavigate={navigate}
          />
        )}
        {page === 'wishlist' && (
          <WishlistPage
            wishlist={wishlist}
            onAddToCart={addToCart}
            onToggleWishlist={toggleWishlist}
            onProductClick={handleProductClick}
            onNavigate={navigate}
          />
        )}
        {page === 'checkout' && (
          <CheckoutPage
            customer={user}
            wishlist={wishlist}
            onToggleWishlist={toggleWishlist}
            onAddToCart={addCartItem}
            onProductClick={handleProductClick}
            items={cart}
            onComplete={() => { void refreshCart(); }}
            couponCode={couponCode}
            onNavigate={navigate}
          />
        )}
        {page === 'tracking' && <GuestTrackingPage key={location.pathname} />}
        {page === 'account' && <AccountPage key={user?.id ?? 'guest'} onSignIn={openAuth} onLogout={signOut} isAdmin={user?.role?.toUpperCase() === 'ADMIN'} />}
        {page === 'admin' && <AdminPage key={user?.id ?? 'guest'} onSignIn={openAuth} onLogout={signOut} onExitAdmin={() => navigate('home')} />}
        {page === 'about' && (
          <AboutPage onNavigate={navigate} />
        )}
        {page === 'contact' && <InfoPage kind="contact" onNavigate={navigate} />}
        {page === 'shipping' && <InfoPage kind="shipping" onNavigate={navigate} />}
        {page === 'returns' && <InfoPage kind="returns" onNavigate={navigate} />}
        {page === 'privacy' && <InfoPage kind="privacy" onNavigate={navigate} />}
        {page === 'terms' && <InfoPage kind="terms" onNavigate={navigate} />}
          </>
        )}
      </main>
      </Suspense>

      {/* Show footer on all pages except checkout */}
      {page !== 'checkout' && page !== 'admin' && <Footer onNavigate={navigate} />}

      {/* Cart Drawer */}
      {page !== 'admin' && <CartDrawer
        open={cartOpen}
        onClose={() => setCartOpen(false)}
        items={cart}
        onUpdateQty={updateCartQty}
        onRemove={removeFromCart}
        onWishlist={toggleWishlist}
        onCheckout={handleCheckout}
        onProductClick={handleProductClick}
        onAddToCart={addCartItem}
      />}

      {/* Search Overlay */}
      {page !== 'admin' && searchOpen && <Suspense fallback={<SearchLoading onClose={() => setSearchOpen(false)} />}><SearchOverlay
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
        onProductClick={handleProductClick}
      /></Suspense>}
      {authOpen && <Suspense fallback={<AuthLoading onClose={() => setAuthOpen(false)} />}><AuthModal open={authOpen} initialError={authError} onClose={() => { setAuthOpen(false); setAuthError(''); }} onSignedIn={signedInUser => { setUser(signedInUser); setAuthError(''); void refreshCart(); void refreshWishlist(); }} /></Suspense>}
    </div>
  );
}
