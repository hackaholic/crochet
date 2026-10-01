import { useState, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router';
import Header from './components/Header';
import Footer from './components/Footer';
import CartDrawer from './components/CartDrawer';
import SearchOverlay from './components/SearchOverlay';
import HomePage from './pages/HomePage';
import ShopPage from './pages/ShopPage';
import ProductPage from './pages/ProductPage';
import CartPage from './pages/CartPage';
import WishlistPage from './pages/WishlistPage';
import CheckoutPage from './pages/CheckoutPage';
import AboutPage from './pages/AboutPage';
import InfoPage from './pages/InfoPage';
import AccountPage from './pages/AccountPage';
import AdminPage from './pages/AdminPage';
import type { Product } from './data/products';
import { pageFromPath, pagePath, productPath, productSlug, type AppPage } from './lib/routes';
import { useCatalogue } from './components/CatalogueProvider';
import { ErrorState, LoadingState } from './components/StorefrontState';
import { useCart } from './components/CartProvider';
import AuthModal from './components/AuthModal';
import type { User } from './lib/api/auth';
import { useWishlist } from './components/WishlistProvider';
import SeoManager from './components/SeoManager';

export default function App() {
  const location = useLocation();
  const navigateTo = useNavigate();
  const page = pageFromPath(location.pathname);
  const { products, loading: catalogueLoading, error: catalogueError, retry: retryCatalogue } = useCatalogue();
  const selectedProduct = page === 'product'
    ? products.find(product => productSlug(product) === location.pathname.split('/').pop()) ?? null
    : null;
  const showNotFound = page === 'notFound' || (page === 'product' && selectedProduct === null);
  const { items: cart, add: addCartItem, update: updateCartItem, remove: removeCartItem, refresh: refreshCart } = useCart();
  const { ids: wishlist, toggle: toggleServerWishlist, refresh: refreshWishlist } = useWishlist();
  const [cartOpen, setCartOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [couponCode, setCouponCode] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const openAuth = useCallback(() => setAuthOpen(true), []);

  const navigate = useCallback((p: AppPage) => {
    navigateTo(p === 'product' || p === 'notFound' ? '/shop' : pagePath(p));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [navigateTo]);

  const addToCart = useCallback((product: Product, quantity = 1) => {
    void addCartItem(product, quantity);
    setCartOpen(true);
  }, [addCartItem]);

  const updateCartQty = useCallback((id: number, qty: number) => {
    void updateCartItem(id, qty);
  }, [updateCartItem]);

  const removeFromCart = useCallback((id: number) => {
    void removeCartItem(id);
  }, [removeCartItem]);

  const toggleWishlist = useCallback((product: Product) => { toggleServerWishlist(product); }, [toggleServerWishlist]);

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
      <SeoManager page={showNotFound ? 'notFound' : page} pathname={location.pathname} product={selectedProduct} />
      <a href="#main-content" className="sr-only fixed left-4 top-4 z-100 rounded-full bg-[#2C1810] px-5 py-3 text-sm font-semibold text-white focus:not-sr-only">
        Skip to content
      </a>
      <Header
        currentPage={page}
        onNavigate={navigate}
        cartCount={cartCount}
        wishlistCount={wishlist.length}
        onSearchOpen={() => setSearchOpen(true)}
        onCartOpen={() => setCartOpen(true)}
        onAccountOpen={() => user ? navigate('account') : openAuth()}
      />

      <main id="main-content" tabIndex={-1}>
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
            onAddToCart={addToCart}
            onToggleWishlist={toggleWishlist}
            wishlist={wishlist}
            onProductClick={handleProductClick}
          />
        )}
        {page === 'product' && (
          <ProductPage
            product={selectedProduct}
            onAddToCart={addToCart}
            onToggleWishlist={toggleWishlist}
            wishlist={wishlist}
            onProductClick={handleProductClick}
            onNavigate={navigate}
          />
        )}
        {page === 'cart' && (
          <CartPage
            items={cart}
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
            items={cart}
            onComplete={() => { void refreshCart(); }}
            couponCode={couponCode}
            onNavigate={navigate}
          />
        )}
        {page === 'account' && <AccountPage key={user?.id ?? 'guest'} onSignIn={openAuth} />}
        {page === 'admin' && <AdminPage onSignIn={openAuth} />}
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

      {/* Show footer on all pages except checkout */}
      {page !== 'checkout' && <Footer onNavigate={navigate} />}

      {/* Cart Drawer */}
      <CartDrawer
        open={cartOpen}
        onClose={() => setCartOpen(false)}
        items={cart}
        onUpdateQty={updateCartQty}
        onRemove={removeFromCart}
        onWishlist={toggleWishlist}
        onCheckout={handleCheckout}
      />

      {/* Search Overlay */}
      <SearchOverlay
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
        onProductClick={handleProductClick}
      />
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} onSignedIn={signedInUser => { setUser(signedInUser); void refreshCart(); void refreshWishlist(); }} />
    </div>
  );
}
