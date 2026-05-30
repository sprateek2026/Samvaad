import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Megaphone, Bell, ChevronDown, Menu, X,
  LayoutDashboard, FilePlus2, FileSearch, Users, LogOut,
  FileText, Settings,
} from 'lucide-react';
import { dashboardAPI } from '../api';
import DrawerPanel from './DrawerPanel';
import NotificationDrawer from './ui/NotificationDrawer';

const LANGS = ['en', 'hi', 'mr'];
const LANG_LABELS = { en: 'EN', hi: 'HI', mr: 'MR' };

export default function Layout({ children, user, onLogout }) {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();

  const [notifications, setNotifications]     = useState([]);
  const [notifOpen, setNotifOpen]             = useState(false);
  const [profileOpen, setProfileOpen]         = useState(false);
  const [mobileOpen, setMobileOpen]           = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    if (!user) return;
    dashboardAPI.notifications()
      .then(r => setNotifications(r.data?.notifications || []))
      .catch(() => {});
  }, [user]);

  useEffect(() => {
    function handleClick(e) {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  if (!user) return <>{children}</>;

  const unread = notifications.filter(n => !n.is_read).length;

  function isActive(path) {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  }

  const navLinks = [
    { to: '/',          label: t('nav.dashboard'),  icon: LayoutDashboard, show: true },
    { to: '/raise',     label: t('nav.raise_issue'), icon: FilePlus2, show: user.role === 'citizen' },
    { to: '/complaints',label: 'My Complaints',      icon: FileSearch, show: user.role === 'citizen' },
  ];

  function handleLogout() { onLogout(); navigate('/login'); }

  return (
    <div className="min-h-screen bg-[#f4f6fb]">
      {/* ── Top Navigation Bar ── */}
      <nav className="fixed top-0 inset-x-0 z-40 h-14"
           style={{ background: 'linear-gradient(to right, #0f172a, #1e1b4b, #0f172a)', borderBottom: '1px solid rgba(255,255,255,0.07)' }}>
        <div className="max-w-7xl mx-auto px-4 h-full flex items-center justify-between gap-4">

          {/* ── Logo ── */}
          <Link to="/" className="flex items-center gap-2.5 flex-shrink-0 group">
            <div className="w-8 h-8 rounded-lg bg-saffron-500/20 border border-saffron-500/30 flex items-center justify-center
                            group-hover:bg-saffron-500/30 transition-colors">
              <Megaphone className="w-4 h-4 text-saffron-400" />
            </div>
            <div className="leading-tight">
              <div className="text-white font-bold text-base tracking-tight leading-none">Samvaad</div>
              <div className="text-white/40 text-[10px] leading-none mt-0.5 hidden sm:block">Govt. of Maharashtra</div>
            </div>
          </Link>

          {/* ── Desktop Nav Links ── */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.filter(l => l.show).map(({ to, label, icon: Icon }) => (
              <Link key={to} to={to}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-150
                  ${isActive(to)
                    ? 'bg-white/10 text-white'
                    : 'text-white/60 hover:text-white hover:bg-white/8'}`}>
                <Icon className="w-3.5 h-3.5" />
                {label}
              </Link>
            ))}
          </div>

          {/* ── Right Controls ── */}
          <div className="flex items-center gap-1.5">

            {/* Language toggle */}
            <div className="hidden sm:flex items-center gap-0.5 bg-white/8 rounded-lg p-0.5">
              {LANGS.map(lng => (
                <button key={lng} onClick={() => i18n.changeLanguage(lng)}
                  className={`px-2 py-1 rounded-md text-xs font-semibold transition-all duration-150
                    ${i18n.language === lng
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-white/60 hover:text-white'}`}>
                  {LANG_LABELS[lng]}
                </button>
              ))}
            </div>

            {/* Notification bell */}
            <button onClick={() => setNotifOpen(true)}
              className="relative w-9 h-9 rounded-lg flex items-center justify-center text-white/60
                         hover:text-white hover:bg-white/10 transition-all duration-150">
              <Bell className="w-4.5 h-4.5 w-[18px] h-[18px]" />
              {unread > 0 && (
                <span className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-amber-400 text-[9px] font-bold
                                 text-gray-900 flex items-center justify-center leading-none">
                  {unread > 9 ? '9+' : unread}
                </span>
              )}
            </button>

            {/* Profile dropdown */}
            <div ref={profileRef} className="relative">
              <button onClick={() => setProfileOpen(p => !p)}
                className="flex items-center gap-2 pl-2 pr-2.5 py-1.5 rounded-lg
                           hover:bg-white/10 transition-all duration-150 group">
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-saffron-500
                                flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                  {user.full_name?.[0]?.toUpperCase() || 'U'}
                </div>
                <span className="hidden sm:block text-sm text-white/80 font-medium max-w-[120px] truncate group-hover:text-white">
                  {user.full_name?.split(' ')[0]}
                </span>
                <ChevronDown className={`w-3.5 h-3.5 text-white/50 transition-transform duration-150 ${profileOpen ? 'rotate-180' : ''}`} />
              </button>

              {profileOpen && (
                <div className="absolute right-0 top-full mt-1.5 w-48 bg-white rounded-xl shadow-modal border border-gray-100
                                py-1 z-50 animate-scale-in origin-top-right">
                  <div className="px-3 py-2 border-b border-gray-100 mb-1">
                    <p className="text-xs font-semibold text-gray-900 truncate">{user.full_name}</p>
                    <p className="text-[10px] text-gray-400 capitalize">{user.role}</p>
                  </div>
                  <Link to="/complaints" onClick={() => setProfileOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-colors">
                    <FileText className="w-4 h-4 text-gray-400" /> My Complaints
                  </Link>
                  <button className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-colors">
                    <Settings className="w-4 h-4 text-gray-400" /> Settings
                  </button>
                  <div className="border-t border-gray-100 mt-1 pt-1">
                    <button onClick={handleLogout}
                      className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">
                      <LogOut className="w-4 h-4" /> {t('nav.logout')}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Mobile hamburger */}
            <button onClick={() => setMobileOpen(p => !p)}
              className="md:hidden w-9 h-9 rounded-lg flex items-center justify-center text-white/60
                         hover:text-white hover:bg-white/10 transition-all duration-150">
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* ── Mobile Menu ── */}
        {mobileOpen && (
          <div className="md:hidden border-t border-white/10 bg-slate-900/95 backdrop-blur-sm px-4 py-3 space-y-1 animate-fade-in">
            {navLinks.filter(l => l.show).map(({ to, label, icon: Icon }) => (
              <Link key={to} to={to}
                className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors
                  ${isActive(to) ? 'bg-white/10 text-white' : 'text-white/70 hover:text-white hover:bg-white/8'}`}>
                <Icon className="w-4 h-4" /> {label}
              </Link>
            ))}
            <div className="pt-2 border-t border-white/10 flex items-center gap-1">
              {LANGS.map(lng => (
                <button key={lng} onClick={() => i18n.changeLanguage(lng)}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-colors
                    ${i18n.language === lng ? 'bg-white text-gray-900' : 'text-white/60 hover:text-white'}`}>
                  {LANG_LABELS[lng]}
                </button>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* ── Page Content (offset for fixed nav) ── */}
      <main className="pt-14 min-h-screen">
        {children}
      </main>

      {/* ── Notification Drawer ── */}
      <DrawerPanel
        isOpen={notifOpen}
        onClose={() => setNotifOpen(false)}
        title={`Notifications${unread > 0 ? ` (${unread})` : ''}`}
      >
        <NotificationDrawer notifications={notifications} />
      </DrawerPanel>
    </div>
  );
}
