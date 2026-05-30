import { ChevronRight } from 'lucide-react';

export default function PageHeader({ title, subtitle, breadcrumb = [], action }) {
  return (
    <div className="flex items-start justify-between gap-4 mb-6">
      <div className="space-y-1 min-w-0">
        {breadcrumb.length > 0 && (
          <nav className="flex items-center gap-1 text-xs text-gray-400 font-medium mb-1">
            {breadcrumb.map((crumb, i) => (
              <span key={i} className="flex items-center gap-1">
                {i > 0 && <ChevronRight className="w-3 h-3" />}
                <span className={i === breadcrumb.length - 1 ? 'text-gray-600' : 'hover:text-gray-600 cursor-pointer'}>
                  {crumb}
                </span>
              </span>
            ))}
          </nav>
        )}
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight leading-tight">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  );
}
