import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import Sparkline from './Sparkline';

const COLOR_MAP = {
  indigo:  { wrap: 'kpi-indigo',  spark: '#a5b4fc' },
  saffron: { wrap: 'kpi-saffron', spark: '#fed7aa' },
  emerald: { wrap: 'kpi-emerald', spark: '#6ee7b7' },
  gold:    { wrap: 'kpi-gold',    spark: '#fde68a' },
  purple:  { wrap: 'kpi-purple',  spark: '#d8b4fe' },
  rose:    { wrap: 'kpi-rose',    spark: '#fda4af' },
};

export default function KpiCard({ label, value, delta, icon: Icon, color = 'indigo', sparkData, onClick }) {
  const { wrap, spark } = COLOR_MAP[color] || COLOR_MAP.indigo;

  const DeltaIcon = delta > 0 ? TrendingUp : delta < 0 ? TrendingDown : Minus;
  const deltaColor = delta > 0 ? 'text-white/90' : delta < 0 ? 'text-red-200' : 'text-white/60';

  return (
    <button
      type="button"
      onClick={onClick}
      className={`${wrap} rounded-2xl p-5 flex flex-col gap-3 text-left w-full
                  transition-all duration-200 hover:-translate-y-0.5 group
                  focus:outline-none focus:ring-2 focus:ring-white/40
                  ${onClick ? 'cursor-pointer' : 'cursor-default'}`}
      style={{ boxShadow: '0 4px 20px rgba(0,0,0,0.12)' }}
    >
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-1 min-w-0">
          <span className="text-white/70 text-xs font-medium tracking-wide uppercase truncate">
            {label}
          </span>
          <span className="text-3xl font-bold text-white leading-none tabular-nums">
            {value ?? '—'}
          </span>
        </div>
        {Icon && (
          <div className="p-2.5 rounded-xl bg-white/15 flex-shrink-0">
            <Icon className="w-5 h-5 text-white/90" />
          </div>
        )}
      </div>

      {sparkData && sparkData.length > 1 && (
        <div className="h-7 -mx-1">
          <Sparkline data={sparkData} color={spark} />
        </div>
      )}

      {delta !== undefined && delta !== null && (
        <div className={`flex items-center gap-1 text-xs font-medium ${deltaColor}`}>
          <DeltaIcon className="w-3.5 h-3.5" />
          <span>{Math.abs(delta)}% vs last period</span>
        </div>
      )}
    </button>
  );
}
