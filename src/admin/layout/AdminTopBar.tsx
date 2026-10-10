import { useState } from 'react';
import type { AdminPage, DateRangePreset } from '../types';

const PAGE_TITLES: Record<AdminPage, string> = {
  dashboard: 'Dashboard', orders: 'Orders', 'order-detail': 'Order Detail', products: 'Products',
  inventory: 'Inventory', customers: 'Customers', finance: 'Finance & Analytics', returns: 'Returns', occasions: 'Gift by Occasion', settings: 'Settings',
};
const DATE_PRESETS: { id: DateRangePreset; label: string }[] = [
  { id: 'today', label: 'Today' }, { id: 'yesterday', label: 'Yesterday' }, { id: '7d', label: 'Last 7 Days' },
  { id: '30d', label: 'Last 30 Days' }, { id: 'this_month', label: 'This Month' }, { id: 'prev_month', label: 'Previous Month' },
];
const PAGES_WITH_DATE: AdminPage[] = ['dashboard', 'finance'];

interface Props {
  currentPage: AdminPage;
  onSearch?: (q: string) => void;
  datePreset?: DateRangePreset;
  onDateChange?: (preset: DateRangePreset) => void;
}

export default function AdminTopBar({ currentPage, onSearch, datePreset = '30d', onDateChange }: Props) {
  const [search, setSearch] = useState('');
  const showDate = PAGES_WITH_DATE.includes(currentPage);
  const handleSearch = (value: string) => { setSearch(value); onSearch?.(value); };

  return (
    <header className="sticky top-0 z-30 flex min-h-14 shrink-0 items-center gap-4 border-b border-[#E8E0D8] bg-white px-4 sm:px-5">
      <h1 className="mr-1 shrink-0 font-serif text-base font-bold text-[#1A1108]">{PAGE_TITLES[currentPage]}</h1>
      {currentPage !== 'products' && currentPage !== 'inventory' && currentPage !== 'customers' && <div className="relative min-w-0 max-w-sm flex-1">
        <span aria-hidden="true" className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[#9C8B7E]">⌕</span>
        <input type="search" value={search} onChange={event => handleSearch(event.target.value)} aria-label="Search orders" placeholder="Search orders…" className="w-full rounded-lg border border-[#E8E0D8] bg-[#FDFAF7] py-2 pl-9 pr-4 text-sm text-[#1A1108] outline-none placeholder:text-[#9C8B7E] focus:border-[#C4622D]" />
      </div>}
      <div className="flex-1" />
      {showDate && onDateChange && <label className="flex shrink-0 items-center gap-2 text-xs text-[#6B5B4E]"><span className="hidden sm:inline">Period</span><select aria-label="Date range" value={datePreset} onChange={event => onDateChange(event.target.value as DateRangePreset)} className="max-w-32 rounded-lg border border-[#E8E0D8] bg-white px-2.5 py-2 text-xs outline-none focus:border-[#C4622D]">{DATE_PRESETS.map(preset => <option key={preset.id} value={preset.id}>{preset.label}</option>)}</select></label>}
      <span className="flex shrink-0 items-center gap-2 rounded-full bg-[#F5F0EA] px-3 py-2 text-xs font-medium text-[#6B5B4E]"><span className="grid h-6 w-6 place-items-center rounded-full bg-[#C4622D] text-[10px] font-bold text-white">S</span><span className="hidden sm:inline">Sulocraft Admin</span></span>
    </header>
  );
}
