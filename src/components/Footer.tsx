import { useState } from 'react';
import { YarnLogo } from './Icons';

type Page = 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'about' | 'contact' | 'shipping' | 'returns' | 'privacy' | 'terms' | 'notFound';

interface FooterProps {
  onNavigate: (page: Page) => void;
}

const InstagramIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="2" width="20" height="20" rx="5" ry="5" /><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" /><line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
  </svg>
);
const PinterestIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/>
  </svg>
);
const WhatsAppIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/>
  </svg>
);
const FacebookIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
  </svg>
);

export default function Footer({ onNavigate }: FooterProps) {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) { setSubscribed(true); setEmail(''); }
  };

  return (
    <footer className="bg-[#2C1810] text-white mt-24">
      {/* Top wave */}
      <div className="bg-[#FAF7F2] h-12 relative">
        <svg viewBox="0 0 1440 48" preserveAspectRatio="none" className="absolute bottom-0 left-0 w-full h-full" fill="#2C1810">
          <path d="M0,48 L0,24 Q180,0 360,24 Q540,48 720,24 Q900,0 1080,24 Q1260,48 1440,24 L1440,48 Z" />
        </svg>
      </div>

      <div className="max-w-7xl mx-auto px-4 pt-16 pb-12">
        {/* Newsletter */}
        <div className="text-center mb-16 pb-16 border-b border-white/10">
          <p className="text-[#F2C4CE] text-xs tracking-widest uppercase mb-3">Stay Connected</p>
          <h3 className="text-3xl font-medium mb-4" style={{ fontFamily: 'var(--font-serif)' }}>
            A little handmade happiness in your inbox.
          </h3>
          <p className="text-white/60 text-sm mb-8">New arrivals, creative inspiration, and exclusive offers — curated with care.</p>
          {subscribed ? (
            <div className="inline-flex items-center gap-2 bg-[#8FAF8C]/20 text-[#C2D9BF] px-6 py-3 rounded-full text-sm font-medium">
              ✓ You're subscribed! Welcome to our little world.
            </div>
          ) : (
            <form onSubmit={handleSubscribe} className="flex max-w-md mx-auto gap-2">
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="Your email address"
                className="flex-1 px-5 py-3 rounded-full bg-white/10 border border-white/20 text-white placeholder-white/40 text-sm focus:outline-none focus:border-[#F2C4CE] transition-colors"
                required
              />
              <button
                type="submit"
                className="px-6 py-3 bg-[#C4622D] hover:bg-[#D4795A] rounded-full text-sm font-semibold whitespace-nowrap transition-colors"
              >
                Subscribe
              </button>
            </form>
          )}
        </div>

        {/* Links */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-10 mb-16">
          <div>
            <h4 className="text-[#F2C4CE] text-xs tracking-widest uppercase mb-4 font-semibold">Shop</h4>
            <ul className="space-y-2.5">
              {['All Products', 'New Arrivals', 'Best Sellers', 'Custom Orders'].map(item => (
                <li key={item}>
                  <button onClick={() => onNavigate('shop')} className="text-white/60 hover:text-white text-sm transition-colors">
                    {item}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-[#F2C4CE] text-xs tracking-widest uppercase mb-4 font-semibold">Collections</h4>
            <ul className="space-y-2.5">
              {['Flowers', 'Romantic Gifts', 'Pooja', 'Home Décor', 'Amigurumi'].map(item => (
                <li key={item}>
                  <button onClick={() => onNavigate('shop')} className="text-white/60 hover:text-white text-sm transition-colors">
                    {item}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-[#F2C4CE] text-xs tracking-widest uppercase mb-4 font-semibold">Help</h4>
            <ul className="space-y-2.5">
              {[
                { label: 'Contact Us', page: 'contact' as Page },
                { label: 'Shipping', page: 'shipping' as Page },
                { label: 'Returns', page: 'returns' as Page },
                { label: 'Privacy', page: 'privacy' as Page },
                { label: 'Terms', page: 'terms' as Page },
              ].map(({ label, page }) => (
                <li key={label}>
                  <button onClick={() => onNavigate(page)} className="text-white/60 hover:text-white text-sm transition-colors">{label}</button>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-[#F2C4CE] text-xs tracking-widest uppercase mb-4 font-semibold">About</h4>
            <ul className="space-y-2.5">
              {['Our Story', 'Handmade Process', 'Instagram', 'Sustainability', 'Packaging'].map(item => (
                <li key={item}>
                  <button onClick={() => item === 'Our Story' || item === 'Handmade Process' ? onNavigate('about') : undefined} className="text-white/60 hover:text-white text-sm transition-colors">
                    {item}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 pt-8 border-t border-white/10">
          <div className="flex items-center gap-2">
            <YarnLogo size={28} />
            <div>
              <div className="font-bold text-sm" style={{ fontFamily: 'var(--font-serif)' }}>Sulocraft</div>
              <div className="text-white/40 text-xs">Handmade with love in India</div>
            </div>
          </div>
          <p className="text-white/40 text-xs text-center">
            © 2026 Sulocraft. All rights reserved. Made with ❤️ in India.
          </p>
          {/* Social icons */}
          <div className="flex items-center gap-3">
            {[
              { icon: <InstagramIcon />, label: 'Instagram' },
              { icon: <PinterestIcon />, label: 'Pinterest' },
              { icon: <WhatsAppIcon />, label: 'WhatsApp' },
              { icon: <FacebookIcon />, label: 'Facebook' },
            ].map(({ icon, label }) => (
              <button
                key={label}
                aria-label={label}
                className="w-9 h-9 rounded-full bg-white/10 hover:bg-[#C4622D] flex items-center justify-center transition-colors"
              >
                {icon}
              </button>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
