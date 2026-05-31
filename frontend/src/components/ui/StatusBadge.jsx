import { useTranslation } from 'react-i18next';

const STATUS_CONFIG = {
  submitted:    { bg: 'bg-amber-50',   text: 'text-amber-700',  dot: 'bg-amber-400'  },
  under_review: { bg: 'bg-blue-50',    text: 'text-blue-700',   dot: 'bg-blue-400'   },
  assigned:     { bg: 'bg-violet-50',  text: 'text-violet-700', dot: 'bg-violet-400' },
  in_progress:  { bg: 'bg-orange-50',  text: 'text-orange-700', dot: 'bg-orange-400' },
  escalated:    { bg: 'bg-red-50',     text: 'text-red-700',    dot: 'bg-red-400'    },
  resolved:     { bg: 'bg-emerald-50', text: 'text-emerald-700',dot: 'bg-emerald-400'},
  closed:       { bg: 'bg-gray-100',   text: 'text-gray-600',   dot: 'bg-gray-400'   },
  reopened:     { bg: 'bg-pink-50',    text: 'text-pink-700',   dot: 'bg-pink-400'   },
};

export default function StatusBadge({ status, size = 'md' }) {
  const { t } = useTranslation();
  const cfg = STATUS_CONFIG[status] || { bg: 'bg-gray-100', text: 'text-gray-600', dot: 'bg-gray-400' };
  const label = STATUS_CONFIG[status] ? t(`complaint.${status}`) : status;
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5 gap-1' : 'text-xs px-2.5 py-1 gap-1.5';
  return (
    <span className={`inline-flex items-center font-medium rounded-full ${sizeClass} ${cfg.bg} ${cfg.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${cfg.dot}`} />
      {label}
    </span>
  );
}
