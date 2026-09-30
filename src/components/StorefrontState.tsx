interface Action {
  label: string;
  onClick: () => void;
}

interface EmptyStateProps {
  icon: string;
  title: string;
  description: string;
  action?: Action;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="py-24 text-center">
      <div className="mb-6 text-7xl" aria-hidden="true">{icon}</div>
      <h2 className="mb-3 text-2xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{title}</h2>
      <p className="mb-8 text-[#8B6B4A]">{description}</p>
      {action && (
        <button onClick={action.onClick} className="rounded-full bg-[#C4622D] px-8 py-3.5 font-semibold text-white transition-colors hover:bg-[#D4795A]">
          {action.label}
        </button>
      )}
    </div>
  );
}

export function LoadingState({ label = 'Loading something handmade…' }: { label?: string }) {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center gap-4 text-center" role="status" aria-live="polite">
      <span className="h-9 w-9 animate-spin rounded-full border-4 border-[#EDE4D0] border-t-[#C4622D]" aria-hidden="true" />
      <p className="text-sm text-[#8B6B4A]">{label}</p>
    </div>
  );
}

export function ErrorState({ title = 'We could not load this right now.', description = 'Please try again in a moment.', action }: Omit<EmptyStateProps, 'icon'>) {
  return (
    <div className="rounded-2xl border border-[#F2C4CE] bg-white p-8 text-center" role="alert">
      <p className="mb-2 text-lg font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{title}</p>
      <p className="mb-5 text-sm text-[#8B6B4A]">{description}</p>
      {action && (
        <button onClick={action.onClick} className="rounded-full border border-[#C4622D] px-5 py-2 text-sm font-semibold text-[#C4622D] transition-colors hover:bg-[#C4622D] hover:text-white">
          {action.label}
        </button>
      )}
    </div>
  );
}
