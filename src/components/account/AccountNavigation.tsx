export type AccountSection = 'profile' | 'addresses' | 'orders';
const sections: { id: AccountSection; label: string }[] = [
  { id: 'profile', label: 'Profile' },
  { id: 'addresses', label: 'Addresses' },
  { id: 'orders', label: 'Orders' },
];

export default function AccountNavigation({ selected, onSelect, hideOrders = false }: {
  hideOrders?: boolean; selected: AccountSection; onSelect: (section: AccountSection) => void;
}) {
  return <nav aria-label="Account sections" className="flex flex-wrap gap-2 border-b border-[#EDE4D0] pb-4">
    {sections.filter(section => !hideOrders || section.id !== 'orders').map(section => <button key={section.id} type="button"
      aria-current={selected === section.id ? 'page' : undefined}
      aria-controls={`account-${section.id}`}
      onClick={() => onSelect(section.id)}
      className={`rounded-full px-5 py-2.5 text-sm font-semibold ${selected === section.id ? 'bg-[#C4622D] text-white' : 'border border-[#EDE4D0] bg-white text-[#5C3D2E] hover:border-[#C4622D]'}`}>
      {section.label}
    </button>)}
  </nav>;
}
