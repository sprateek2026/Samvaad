import { useTranslation } from 'react-i18next';
import { Bell, AlertTriangle, Clock, CheckCircle2, Info, Megaphone } from 'lucide-react';

const TYPE_ICON = {
  status_update:  CheckCircle2,
  escalation:     AlertTriangle,
  sla_breach:     Clock,
  new_complaint:  Bell,
  general:        Info,
  announcement:   Megaphone,
};

const TYPE_COLOR = {
  status_update:  'text-emerald-500 bg-emerald-50',
  escalation:     'text-red-500 bg-red-50',
  sla_breach:     'text-amber-500 bg-amber-50',
  new_complaint:  'text-primary-500 bg-primary-50',
  general:        'text-gray-500 bg-gray-100',
  announcement:   'text-saffron-500 bg-saffron-50',
};

function timeAgo(dateStr, t) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins  = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days  = Math.floor(diff / 86400000);
  if (mins  < 1)  return t('notif.just_now');
  if (mins  < 60) return t('notif.min_ago', { count: mins });
  if (hours < 24) return t('notif.hour_ago', { count: hours });
  return t('notif.day_ago', { count: days });
}

export default function NotificationDrawer({ notifications = [] }) {
  const { t } = useTranslation();
  if (notifications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3">
        <div className="w-14 h-14 rounded-2xl bg-gray-100 flex items-center justify-center">
          <Bell className="w-6 h-6 text-gray-400" />
        </div>
        <p className="text-sm font-medium text-gray-600">{t('notif.no_yet')}</p>
        <p className="text-xs text-gray-400 text-center max-w-[180px]">
          {t('notif.hint')}
        </p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-100">
      {notifications.map((n) => {
        const Icon = TYPE_ICON[n.type] || Bell;
        const iconClass = TYPE_COLOR[n.type] || TYPE_COLOR.general;
        return (
          <div
            key={n.id}
            className={`flex gap-3 px-4 py-3.5 hover:bg-gray-50 transition-colors cursor-pointer
                        ${!n.is_read ? 'bg-primary-50/40' : ''}`}
          >
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 ${iconClass}`}>
              <Icon className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className={`text-sm leading-snug ${!n.is_read ? 'font-semibold text-gray-900' : 'text-gray-700'}`}>
                {n.title}
              </p>
              {n.message && (
                <p className="text-xs text-gray-500 mt-0.5 leading-snug line-clamp-2">{n.message}</p>
              )}
              <p className="text-[10px] text-gray-400 mt-1 font-medium">{timeAgo(n.created_at, t)}</p>
            </div>
            {!n.is_read && (
              <div className="w-2 h-2 rounded-full bg-primary-500 flex-shrink-0 mt-2" />
            )}
          </div>
        );
      })}
    </div>
  );
}
