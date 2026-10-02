// Shared lightweight admin components
import type { IssueSeverity } from '../types';

// ─── Metric Card ──────────────────────────────────────────────────────────────
interface MetricCardProps {
  label: string;
  value: string;
  prev?: string;
  change?: number; // positive = up, negative = down
  icon: string;
  accent?: string;
  loading?: boolean;
}
export function MetricCard({ label, value, prev, change, icon, accent = '#C4622D', loading }: MetricCardProps) {
  if (loading) return (
    <div className="bg-white rounded-xl border border-[#E8E0D8] p-5 animate-pulse">
      <div className="h-3 bg-[#F5EDE0] rounded w-24 mb-4" />
      <div className="h-7 bg-[#F5EDE0] rounded w-32 mb-2" />
      <div className="h-3 bg-[#F5EDE0] rounded w-20" />
    </div>
  );

  const isUp = change !== undefined && change > 0;
  const isDown = change !== undefined && change < 0;
  const absChange = change !== undefined ? Math.abs(change).toFixed(1) : null;

  return (
    <div className="bg-white rounded-xl border border-[#E8E0D8] p-5 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-medium text-[#6B5B4E] uppercase tracking-wider">{label}</p>
        <span className="text-lg" style={{ color: accent }}>{icon}</span>
      </div>
      <p className="text-2xl font-bold text-[#1A1108] mb-1.5" style={{ fontFamily: 'var(--font-serif)' }}>{value}</p>
      {prev && change !== undefined && (
        <div className="flex items-center gap-1.5 text-xs">
          {isUp && <span className="text-emerald-600 font-semibold">↑ {absChange}%</span>}
          {isDown && <span className="text-red-500 font-semibold">↓ {absChange}%</span>}
          {!isUp && !isDown && <span className="text-[#6B5B4E]">—</span>}
          <span className="text-[#9C8B7E]">vs {prev}</span>
        </div>
      )}
    </div>
  );
}

// ─── Empty State ──────────────────────────────────────────────────────────────
export function EmptyState({ icon = '📭', title, desc, action }: {
  icon?: string; title: string; desc?: string; action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="text-4xl mb-3 opacity-60">{icon}</div>
      <p className="font-semibold text-[#2C1810] text-sm mb-1">{title}</p>
      {desc && <p className="text-xs text-[#6B5B4E] max-w-xs leading-relaxed">{desc}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

// ─── Loading Skeleton ─────────────────────────────────────────────────────────
export function TableSkeleton({ rows = 5, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div className="animate-pulse">
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex gap-4 py-3 border-b border-[#F5F0EA]">
          {Array.from({ length: cols }).map((_, c) => (
            <div key={c} className="h-4 bg-[#F5EDE0] rounded flex-1" style={{ maxWidth: c === 0 ? 80 : undefined }} />
          ))}
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton({ n = 4 }: { n?: number }) {
  return (
    <div className={`grid grid-cols-2 lg:grid-cols-${n} gap-4 animate-pulse`}>
      {Array.from({ length: n }).map((_, i) => (
        <div key={i} className="bg-white rounded-xl border border-[#E8E0D8] p-5">
          <div className="h-3 bg-[#F5EDE0] rounded w-20 mb-4" />
          <div className="h-6 bg-[#F5EDE0] rounded w-28 mb-2" />
          <div className="h-3 bg-[#F5EDE0] rounded w-16" />
        </div>
      ))}
    </div>
  );
}

// ─── Confirmation Dialog ──────────────────────────────────────────────────────
interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}
export function ConfirmDialog({ open, title, message, confirmLabel = 'Confirm', danger, onConfirm, onCancel }: ConfirmDialogProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ zIndex: 9999 }}>
      <div className="absolute inset-0 bg-black/40" onClick={onCancel} />
      <div className="relative bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full">
        <h3 className="font-bold text-[#1A1108] text-base mb-2">{title}</h3>
        <p className="text-sm text-[#6B5B4E] mb-6 leading-relaxed">{message}</p>
        <div className="flex gap-3">
          <button onClick={onCancel} className="flex-1 py-2.5 border border-[#E8E0D8] rounded-lg text-sm font-medium text-[#6B5B4E] hover:bg-[#F5F0EA] transition-colors">
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className={`flex-1 py-2.5 rounded-lg text-sm font-semibold text-white transition-colors ${danger ? 'bg-red-600 hover:bg-red-700' : 'bg-[#C4622D] hover:bg-[#D4795A]'}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Section header ───────────────────────────────────────────────────────────
export function SectionHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="flex items-end justify-between mb-5">
      <div>
        <h2 className="text-base font-bold text-[#1A1108]" style={{ fontFamily: 'var(--font-serif)' }}>{title}</h2>
        {subtitle && <p className="text-xs text-[#6B5B4E] mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

// ─── Severity badge ───────────────────────────────────────────────────────────
export function SeverityBadge({ severity }: { severity: IssueSeverity }) {
  const map = {
    critical: { bg: '#FEF2F2', text: '#991B1B', label: 'Critical', dot: '#EF4444' },
    warning:  { bg: '#FFFBEB', text: '#92400E', label: 'Warning',  dot: '#F59E0B' },
    info:     { bg: '#EFF6FF', text: '#1D4ED8', label: 'Info',     dot: '#3B82F6' },
  };
  const c = map[severity];
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium" style={{ background: c.bg, color: c.text }}>
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: c.dot }} />
      {c.label}
    </span>
  );
}

// ─── INR formatter ────────────────────────────────────────────────────────────
export function inr(n: number): string {
  return '₹' + n.toLocaleString('en-IN');
}

export function pct(current: number, prev: number): number {
  if (prev === 0) return 0;
  return parseFloat(((current - prev) / prev * 100).toFixed(1));
}

// ─── Pagination ───────────────────────────────────────────────────────────────
export function Pagination({ page, pageSize, total, onPage }: { page: number; pageSize: number; total: number; onPage: (p: number) => void }) {
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) return null;
  const pages = Array.from({ length: Math.min(totalPages, 7) }, (_, i) => i + 1);
  return (
    <div className="flex items-center justify-between mt-4 text-sm">
      <span className="text-xs text-[#6B5B4E]">
        Showing {Math.min((page - 1) * pageSize + 1, total)}–{Math.min(page * pageSize, total)} of {total}
      </span>
      <div className="flex items-center gap-1">
        <button disabled={page === 1} onClick={() => onPage(page - 1)} className="px-2.5 py-1 rounded border border-[#E8E0D8] text-xs disabled:opacity-40 hover:bg-[#F5F0EA] transition-colors">←</button>
        {pages.map(p => (
          <button key={p} onClick={() => onPage(p)} className={`w-8 h-7 rounded border text-xs transition-colors ${p === page ? 'bg-[#C4622D] text-white border-[#C4622D]' : 'border-[#E8E0D8] hover:bg-[#F5F0EA]'}`}>{p}</button>
        ))}
        {totalPages > 7 && <span className="text-[#6B5B4E]">…</span>}
        <button disabled={page === totalPages} onClick={() => onPage(page + 1)} className="px-2.5 py-1 rounded border border-[#E8E0D8] text-xs disabled:opacity-40 hover:bg-[#F5F0EA] transition-colors">→</button>
      </div>
    </div>
  );
}
