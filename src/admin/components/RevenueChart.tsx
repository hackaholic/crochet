import { useState } from 'react';
import type { SalesDataPoint } from '../types';
import { inr } from './AdminShared';

type Metric = 'revenue' | 'orders' | 'avgOrderValue';

interface RevenueChartProps {
  data: SalesDataPoint[];
  loading?: boolean;
}

const METRIC_CONFIG: Record<Metric, { label: string; format: (v: number) => string; color: string }> = {
  revenue:       { label: 'Revenue',         format: v => inr(v),    color: '#C4622D' },
  orders:        { label: 'Orders',           format: v => String(v), color: '#8FAF8C' },
  avgOrderValue: { label: 'Avg Order Value',  format: v => inr(v),    color: '#8B6B4A' },
};

export default function RevenueChart({ data, loading }: RevenueChartProps) {
  const [metric, setMetric] = useState<Metric>('revenue');
  const [tooltip, setTooltip] = useState<{ x: number; y: number; point: SalesDataPoint } | null>(null);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
        <div className="h-4 bg-[#F5EDE0] rounded w-32 mb-4 animate-pulse" />
        <div className="h-52 bg-[#F5EDE0] rounded animate-pulse" />
      </div>
    );
  }

  if (data.length === 0) return <div className="rounded-xl border border-[#E8E0D8] bg-white p-5"><h3 className="mb-4 font-serif text-sm font-bold text-[#1A1108]">Sales Analytics</h3><div className="grid min-h-52 place-items-center rounded-lg bg-[#FAF7F3] text-sm text-[#9C8B7E]">No sales recorded in this period.</div></div>;

  const cfg = METRIC_CONFIG[metric];
  const values = data.map(d => d[metric] as number);
  const max = Math.max(...values) * 1.15 || 1;
  const min = 0;
  const W = 800;
  const H = 200;
  const PAD = { top: 12, right: 16, bottom: 32, left: 56 };
  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;

  const xScale = (i: number) => PAD.left + (i / (data.length - 1)) * innerW;
  const yScale = (v: number) => PAD.top + innerH - ((v - min) / (max - min)) * innerH;

  // Y grid lines
  const gridCount = 4;
  const gridLines = Array.from({ length: gridCount + 1 }, (_, i) => ({
    y: yScale(min + (i / gridCount) * (max - min)),
    label: cfg.format(Math.round(min + (i / gridCount) * (max - min))),
  }));

  // Line path
  const points = data.map((d, i) => `${xScale(i)},${yScale(d[metric] as number)}`).join(' ');

  // Area fill
  const areaPath = `M ${xScale(0)},${yScale(values[0])} ` +
    data.slice(1).map((d, i) => `L ${xScale(i + 1)},${yScale(d[metric] as number)}`).join(' ') +
    ` L ${xScale(data.length - 1)},${PAD.top + innerH} L ${xScale(0)},${PAD.top + innerH} Z`;

  // X labels (every 5th if >14 points)
  const labelStep = data.length > 14 ? 5 : data.length > 7 ? 2 : 1;

  return (
    <div className="bg-white rounded-xl border border-[#E8E0D8] p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <h3 className="font-bold text-[#1A1108] text-sm" style={{ fontFamily: 'var(--font-serif)' }}>Sales Analytics</h3>
        <div className="flex gap-1 bg-[#F5F0EA] rounded-lg p-0.5">
          {(Object.keys(METRIC_CONFIG) as Metric[]).map(m => (
            <button
              key={m}
              onClick={() => setMetric(m)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${metric === m ? 'bg-white text-[#1A1108] shadow-sm' : 'text-[#6B5B4E] hover:text-[#1A1108]'}`}
            >
              {METRIC_CONFIG[m].label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="relative">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="w-full"
          style={{ height: '220px', overflow: 'visible' }}
          onMouseLeave={() => setTooltip(null)}
        >
          <defs>
            <linearGradient id={`grad-${metric}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={cfg.color} stopOpacity="0.15" />
              <stop offset="100%" stopColor={cfg.color} stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {gridLines.map(({ y, label }, i) => (
            <g key={i}>
              <line x1={PAD.left} y1={y} x2={W - PAD.right} y2={y} stroke="#F0EAE3" strokeWidth="1" strokeDasharray={i === 0 ? undefined : '4,4'} />
              <text x={PAD.left - 6} y={y + 4} textAnchor="end" fontSize="10" fill="#9C8B7E">{label}</text>
            </g>
          ))}

          {/* Area fill */}
          <path d={areaPath} fill={`url(#grad-${metric})`} />

          {/* Line */}
          <polyline points={points} fill="none" stroke={cfg.color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />

          {/* Data points + hover zones */}
          {data.map((d, i) => {
            const cx = xScale(i);
            const cy = yScale(d[metric] as number);
            return (
              <g key={i}>
                {/* Invisible hit zone */}
                <rect
                  x={i === 0 ? cx : (cx + xScale(i - 1)) / 2}
                  y={PAD.top}
                  width={innerW / (data.length - 1)}
                  height={innerH}
                  fill="transparent"
                  onMouseEnter={() => setTooltip({ x: cx, y: cy, point: d })}
                />
                {/* Dot (only on hover) */}
                {tooltip?.point === d && (
                  <>
                    <line x1={cx} y1={PAD.top} x2={cx} y2={PAD.top + innerH} stroke={cfg.color} strokeWidth="1" strokeDasharray="4,4" opacity="0.4" />
                    <circle cx={cx} cy={cy} r="5" fill={cfg.color} stroke="white" strokeWidth="2" />
                  </>
                )}
              </g>
            );
          })}

          {/* X labels */}
          {data.map((d, i) => {
            if (i % labelStep !== 0) return null;
            return (
              <text key={i} x={xScale(i)} y={H - 6} textAnchor="middle" fontSize="10" fill="#9C8B7E">{d.label}</text>
            );
          })}
        </svg>

        {/* Tooltip */}
        {tooltip && (
          <div
            className="absolute z-10 bg-[#1A1108] text-white text-xs rounded-lg px-3 py-2 pointer-events-none shadow-xl"
            style={{
              left: `${(tooltip.x / W) * 100}%`,
              top: `${(tooltip.y / 220) * 100}%`,
              transform: 'translate(-50%, -120%)',
              minWidth: '100px',
            }}
          >
            <p className="font-bold text-[#F2C4CE] mb-0.5">{tooltip.point.label}</p>
            <p>{cfg.format(tooltip.point[metric] as number)}</p>
            {metric !== 'orders' && <p className="text-white/60">{tooltip.point.orders} order{tooltip.point.orders !== 1 ? 's' : ''}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
