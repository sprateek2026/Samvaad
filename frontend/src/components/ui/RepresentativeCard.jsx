import { Phone, Info } from 'lucide-react';
import RepresentativeAvatar from '../RepresentativeAvatar';

const TYPE_LABEL = { corporator: 'Corporator', mla: 'MLA', mp: 'MP' };
const TYPE_COLOR = {
  corporator: 'bg-primary-100 text-primary-700',
  mla:        'bg-saffron-100 text-saffron-700',
  mp:         'bg-emerald-100 text-emerald-700',
};

export default function RepresentativeCard({ rep, type }) {
  if (!rep) return null;
  const label = TYPE_LABEL[type] || type;
  const colorClass = TYPE_COLOR[type] || 'bg-gray-100 text-gray-600';
  const name = rep.name || rep.mla_name || rep.mp_name || '—';
  const party = rep.party || rep.mla_party || rep.mp_party || '';
  const photoPath = rep.photo_path;

  return (
    <div className="ds-card p-4 flex flex-col items-center text-center gap-3 min-w-[140px] snap-start">
      <RepresentativeAvatar
        photoPath={photoPath}
        name={name}
        type={type}
        size="lg"
        showHover
      />
      <div className="space-y-1 min-w-0 w-full">
        <span className={`inline-flex items-center text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wide ${colorClass}`}>
          {label}
        </span>
        <p className="text-sm font-semibold text-gray-900 leading-tight truncate">{name}</p>
        {party && <p className="text-xs text-gray-500 truncate">{party}</p>}
      </div>
      <div className="flex gap-2 w-full">
        {rep.contact && (
          <a href={`tel:${rep.contact}`}
            className="flex-1 flex items-center justify-center gap-1 py-1.5 text-xs font-medium
                       rounded-lg border border-gray-200 text-gray-600 hover:border-primary-300
                       hover:text-primary-600 hover:bg-primary-50 transition-colors">
            <Phone className="w-3 h-3" /> Call
          </a>
        )}
        <button
          className="flex-1 flex items-center justify-center gap-1 py-1.5 text-xs font-medium
                     rounded-lg border border-gray-200 text-gray-600 hover:border-primary-300
                     hover:text-primary-600 hover:bg-primary-50 transition-colors">
          <Info className="w-3 h-3" /> Profile
        </button>
      </div>
    </div>
  );
}
