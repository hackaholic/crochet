import type { AdminPage } from '../types';

const PAGE_INFO: Record<AdminPage, { icon: string; title: string; desc: string; milestone: string }> = {
  dashboard: { icon: '◈', title: 'Dashboard', desc: '', milestone: '' },
  orders: { icon: '📋', title: 'Orders', desc: '', milestone: '' },
  'order-detail': { icon: '📋', title: 'Order Detail', desc: '', milestone: '' },
  finance: { icon: '₹', title: 'Finance', desc: '', milestone: '' },
  returns: { icon: '↩', title: 'Returns', desc: '', milestone: '' },
  occasions: { icon: '🎁', title: 'Gift by Occasion', desc: '', milestone: '' },
  products: {
    icon: '🧶', title: 'Products',
    desc: 'Manage your full crochet product catalogue. Add listings, set prices, upload photos and manage variants.',
    milestone: 'Catalogue editing is not connected in this screen yet',
  },
  inventory: {
    icon: '📦', title: 'Inventory',
    desc: 'Track ready stock, made-to-order items, reserved quantities, and production queue.',
    milestone: 'Inventory editing is not connected in this screen yet',
  },
  customers: {
    icon: '👤', title: 'Customers',
    desc: 'View customer profiles, order history, contact details and lifetime value.',
    milestone: 'Customer tools are not connected in this screen yet',
  },
  settings: {
    icon: '⚙', title: 'Settings',
    desc: 'Configure store settings, admin roles, notification preferences, payment methods and shipping zones.',
    milestone: 'Settings are not connected in this screen yet',
  },
};

export default function PlaceholderPage({ page }: { page: AdminPage }) {
  const info = PAGE_INFO[page];
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center max-w-md mx-auto">
      <div className="w-20 h-20 bg-[#F5EDE0] rounded-2xl flex items-center justify-center text-4xl mb-6">
        {info.icon}
      </div>
      <h2 className="text-2xl font-bold text-[#1A1108] mb-2" style={{ fontFamily: 'var(--font-serif)' }}>
        {info.title}
      </h2>
      <p className="text-[#6B5B4E] text-sm leading-relaxed mb-6">{info.desc}</p>
      <div className="inline-flex items-center gap-2 bg-[#F8F4EF] border border-[#E8E0D8] rounded-full px-4 py-2">
        <span className="w-1.5 h-1.5 rounded-full bg-[#F59E0B]" />
        <span className="text-xs text-[#6B5B4E] font-medium">{info.milestone}</span>
      </div>
    </div>
  );
}
