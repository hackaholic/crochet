import { useState } from 'react';
import type { AdminPage } from '../types';
import { YarnLogo } from '../../components/Icons';

interface NavItem {
  id: AdminPage;
  label: string;
  icon: string;
  badge?: number;
}

const NAV: NavItem[] = [
  { id: 'dashboard',  label: 'Dashboard',  icon: '◈' },
  { id: 'orders',     label: 'Orders',     icon: '📋' },
  { id: 'products',   label: 'Products',   icon: '🧶' },
  { id: 'inventory',  label: 'Inventory',  icon: '📦' },
  { id: 'customers',  label: 'Customers',  icon: '👤' },
  { id: 'finance',    label: 'Finance',    icon: '₹' },
  { id: 'returns',    label: 'Returns',    icon: '↩' },
  { id: 'occasions',  label: 'Gift by Occasion', icon: '🎁' },
  { id: 'settings',   label: 'Settings',   icon: '⚙' },
];

interface Props {
  currentPage: AdminPage;
  onNavigate: (page: AdminPage) => void;
  onExitAdmin: () => void;
}

export default function AdminSidebar({ currentPage, onNavigate, onExitAdmin }: Props) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className="flex flex-col bg-[#1A1108] text-white transition-all duration-300 shrink-0"
      style={{ width: collapsed ? 64 : 220, minHeight: '100vh' }}
    >
      {/* Brand */}
      <div className={`flex items-center gap-2.5 px-4 py-5 border-b border-white/10 ${collapsed ? 'justify-center' : ''}`}>
        <YarnLogo size={30} />
        {!collapsed && (
          <div className="overflow-hidden">
            <p className="font-bold text-sm leading-tight text-white" style={{ fontFamily: 'var(--font-serif)' }}>Sulocraft</p>
            <p className="text-[10px] text-white/40 tracking-widest uppercase">Admin</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 overflow-y-auto">
        {NAV.map(item => {
          const active = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              aria-label={item.label}
              title={collapsed ? item.label : undefined}
              className={`w-full flex items-center gap-3 px-4 py-2.5 transition-all duration-150 text-left group relative
                ${active ? 'bg-[#C4622D]/20 text-white' : 'text-white/55 hover:text-white hover:bg-white/5'}`}
            >
              {/* Active indicator */}
              {active && <div className="absolute left-0 top-1 bottom-1 w-0.5 bg-[#C4622D] rounded-r" />}

              <span className={`text-base shrink-0 ${active ? 'text-[#C4622D]' : ''}`}>{item.icon}</span>

              {!collapsed && (
                <>
                  <span className="text-sm font-medium flex-1">{item.label}</span>
                  {item.badge !== undefined && (
                    <span className="text-[10px] font-bold bg-[#C4622D] text-white rounded-full w-4 h-4 flex items-center justify-center shrink-0">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
              {collapsed && item.badge !== undefined && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#C4622D] rounded-full" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom actions */}
      <div className="border-t border-white/10 p-3 space-y-1">
        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={`w-full flex items-center gap-3 px-3 py-2 text-white/40 hover:text-white hover:bg-white/5 rounded-lg transition-colors text-sm ${collapsed ? 'justify-center' : ''}`}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <span>{collapsed ? '→' : '←'}</span>
          {!collapsed && <span>Collapse</span>}
        </button>
        {/* Exit admin */}
        <button
          onClick={onExitAdmin}
          className={`w-full flex items-center gap-3 px-3 py-2 text-white/40 hover:text-white hover:bg-white/5 rounded-lg transition-colors text-sm ${collapsed ? 'justify-center' : ''}`}
          title="Back to store"
        >
          <span>🏪</span>
          {!collapsed && <span>Back to Store</span>}
        </button>
      </div>
    </aside>
  );
}
