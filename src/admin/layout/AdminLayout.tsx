import type { ReactNode } from 'react';
import type { AdminPage, DateRangePreset } from '../types';
import AdminSidebar from './AdminSidebar';
import AdminTopBar from './AdminTopBar';

interface Props {
  currentPage: AdminPage;
  onNavigate: (page: AdminPage) => void;
  onExitAdmin: () => void;
  onSearch?: (q: string) => void;
  datePreset?: DateRangePreset;
  onDateChange?: (preset: DateRangePreset) => void;
  children: ReactNode;
}

export default function AdminLayout({ currentPage, onNavigate, onExitAdmin, onSearch, datePreset, onDateChange, children }: Props) {
  return (
    <div className="flex h-screen overflow-hidden bg-[#F8F4EF]" style={{ fontFamily: 'var(--font-sans)' }}>
      <AdminSidebar currentPage={currentPage} onNavigate={onNavigate} onExitAdmin={onExitAdmin} />
      <div className="min-w-0 flex-1 flex flex-col overflow-hidden">
        <AdminTopBar
          currentPage={currentPage}
          onSearch={onSearch}
          datePreset={datePreset}
          onDateChange={onDateChange}
        />
        <main className="flex-1 overflow-y-auto p-5 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
