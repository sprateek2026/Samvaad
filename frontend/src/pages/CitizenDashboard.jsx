import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { dashboardAPI, complaintAPI } from "../api";
import {
  BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import {
  FileText, Clock, CheckCircle2, Star, FilePlus2,
  Search, MapPin, ArrowRight, TrendingUp,
} from "lucide-react";
import KpiCard from "../components/ui/KpiCard";
import StatusBadge from "../components/ui/StatusBadge";
import RepresentativeCard from "../components/ui/RepresentativeCard";

const STATUS_PIE_COLORS = {
  submitted:    "#f59e0b",
  under_review: "#3b82f6",
  in_progress:  "#f97316",
  resolved:     "#10b981",
  escalated:    "#ef4444",
  closed:       "#6b7280",
};

const CATEGORY_COLORS = ["#6366f1","#f97316","#10b981","#f59e0b","#8b5cf6","#06b6d4","#ec4899","#14b8a6"];

function greeting(name) {
  const h = new Date().getHours();
  const prefix = h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
  return `${prefix}, ${name?.split(" ")[0] || "Citizen"}`;
}

function SkeletonCard() {
  return (
    <div className="ds-card p-5 space-y-3 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-2/3" />
      <div className="h-8 bg-gray-200 rounded w-1/2" />
      <div className="h-3 bg-gray-100 rounded w-full" />
    </div>
  );
}

export default function CitizenDashboard({ user }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { if (user) { fetchStats(); fetchComplaints(); } }, [user]);

  async function fetchStats() {
    try { const res = await dashboardAPI.citizenStats(); setStats(res.data); } catch {}
    finally { setLoading(false); }
  }
  async function fetchComplaints() {
    try { const res = await complaintAPI.list(); setComplaints(res.data.complaints || []); } catch {}
  }

  const byCategoryData = stats
    ? Object.entries(stats.by_category || {}).map(([name, count]) => ({ name, count }))
    : [];
  const pieData = stats
    ? Object.entries(stats.by_status || {})
        .filter(([s]) => STATUS_PIE_COLORS[s])
        .map(([s, v]) => ({ name: t("complaint." + s), value: v, fill: STATUS_PIE_COLORS[s] }))
    : [];
  const trendData = stats?.trend_last_7 || [];
  const trendNumbers = trendData.map(d => d.count ?? 0);

  const representatives = user?.representatives || {};
  const corporators = representatives.corporators?.filter(c => c?.name) || [];
  const mla = representatives.mla?.name ? representatives.mla : null;
  const mp  = representatives.mp?.name  ? representatives.mp  : null;

  const today = new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

  return (
    <div className="page-content">

      {/* ── Hero Banner ── */}
      <div className="relative overflow-hidden rounded-2xl mb-6 p-6 sm:p-8"
           style={{ background: "linear-gradient(135deg, #4f46e5 0%, #4338ca 40%, #312e81 100%)" }}>
        {/* Decorative circles */}
        <div className="absolute -top-8 -right-8 w-48 h-48 rounded-full opacity-10"
             style={{ background: "radial-gradient(circle, #fff 0%, transparent 70%)" }} />
        <div className="absolute -bottom-12 -left-6 w-36 h-36 rounded-full opacity-10"
             style={{ background: "radial-gradient(circle, #f97316 0%, transparent 70%)" }} />

        <div className="relative flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <p className="text-primary-200 text-sm font-medium mb-1">{today}</p>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight mb-1">
              {greeting(user?.full_name)}
            </h1>
            {user?.ward && (
              <div className="flex items-center gap-1.5 text-primary-200 text-sm">
                <MapPin className="w-3.5 h-3.5" />
                <span>Ward {user.ward.ward_number} — {user.ward.ward_name}</span>
              </div>
            )}
          </div>
          <div className="flex flex-wrap gap-2.5">
            <button onClick={() => navigate("/raise")}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm
                         bg-saffron-500 hover:bg-saffron-600 text-white transition-all duration-150"
              style={{ boxShadow: "0 4px 14px rgba(249,115,22,0.4)" }}>
              <FilePlus2 className="w-4 h-4" /> Raise Complaint
            </button>
            <button onClick={() => navigate("/complaints")}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm
                         bg-white/15 hover:bg-white/25 text-white border border-white/25 transition-all duration-150">
              <Search className="w-4 h-4" /> My Issues
            </button>
          </div>
        </div>
      </div>

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {loading ? (
          [1,2,3,4].map(i => <SkeletonCard key={i} />)
        ) : stats ? (
          <>
            <KpiCard label={t("dashboard.total")} value={stats.total} icon={FileText}
              color="indigo" sparkData={trendNumbers}
              onClick={() => navigate("/complaints?status_group=total")} />
            <KpiCard label={t("dashboard.pending")} value={stats.pending} icon={Clock}
              color="saffron" sparkData={trendNumbers}
              onClick={() => navigate("/complaints?status_group=pending")} />
            <KpiCard label={t("dashboard.resolved")} value={stats.resolved} icon={CheckCircle2}
              color="emerald" sparkData={trendNumbers}
              onClick={() => navigate("/complaints?status_group=resolved")} />
            <KpiCard label={t("dashboard.satisfaction")} value={stats.avg_rating ? `${stats.avg_rating}` : "—"}
              icon={Star} color="gold" />
          </>
        ) : null}
      </div>

      {/* ── Representative Strip ── */}
      {(corporators.length > 0 || mla || mp) && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Your Representatives</h2>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin snap-x">
            {corporators.map((c, i) => (
              <RepresentativeCard key={i} rep={c} type="corporator" />
            ))}
            {mla && <RepresentativeCard rep={mla} type="mla" />}
            {mp  && <RepresentativeCard rep={mp}  type="mp"  />}
          </div>
        </div>
      )}

      {/* ── Charts Row ── */}
      <div className="grid lg:grid-cols-2 gap-5 mb-5">
        {/* Donut — Status overview */}
        <div className="ds-card p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Complaint Status Overview</h3>
          {pieData.some(d => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name"
                     cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                     paddingAngle={3} stroke="none">
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Pie>
                <Tooltip formatter={(v, n) => [v, n]} contentStyle={{ borderRadius: 10, border: 'none', boxShadow: '0 4px 16px rgba(0,0,0,0.1)', fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">{t("dashboard.no_data")}</div>
          )}
        </div>

        {/* Area — Activity trend */}
        <div className="ds-card p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">{t("dashboard.trend_days")}</h3>
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={trendData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stopColor="#6366f1" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#9ca3af" }} tickLine={false} axisLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: "#9ca3af" }} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ borderRadius: 10, border: 'none', boxShadow: '0 4px 16px rgba(0,0,0,0.1)', fontSize: 12 }} />
                <Area type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2}
                  fill="url(#trendGrad)" dot={{ fill: "#6366f1", r: 3, strokeWidth: 0 }}
                  activeDot={{ r: 5, strokeWidth: 0 }} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">{t("dashboard.no_data")}</div>
          )}
        </div>
      </div>

      {/* ── Category Bar ── */}
      {byCategoryData.length > 0 && (
        <div className="ds-card p-5 mb-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">{t("dashboard.by_category")}</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={byCategoryData} margin={{ top: 0, right: 0, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#9ca3af" }} tickLine={false} axisLine={false} />
              <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: "#9ca3af" }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ borderRadius: 10, border: 'none', boxShadow: '0 4px 16px rgba(0,0,0,0.1)', fontSize: 12 }} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {byCategoryData.map((_, i) => (
                  <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* ── Recent Complaints ── */}
      <div className="ds-card overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700">Recent Complaints</h3>
          <Link to="/complaints" className="flex items-center gap-1 text-xs font-medium text-primary-600 hover:text-primary-700">
            View all <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {complaints.length === 0 ? (
          <div className="flex flex-col items-center py-12 gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gray-100 flex items-center justify-center">
              <FileText className="w-5 h-5 text-gray-400" />
            </div>
            <p className="text-sm text-gray-500">{t("dashboard.no_complaints")}</p>
            <Link to="/raise" className="btn-saffron text-sm px-4 py-2">
              {t("dashboard.raise_now")}
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {complaints.slice(0, 10).map((c) => {
              const ageDays = Math.floor((Date.now() - new Date(c.created_at)) / 86400000);
              return (
                <Link key={c.id} to={`/complaint/${c.complaint_id}`}
                  className="flex items-center gap-4 px-5 py-3.5 hover:bg-[#f8faff] transition-colors group">
                  {/* Status dot */}
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                    c.status === 'resolved' ? 'bg-emerald-400' :
                    c.status === 'in_progress' ? 'bg-saffron-400' :
                    c.status === 'escalated' ? 'bg-red-400' : 'bg-amber-400'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate group-hover:text-primary-700">{c.title}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      <span className="font-mono">#{c.complaint_id}</span>
                      {" · "}{ageDays === 0 ? "Today" : `${ageDays}d ago`}
                    </p>
                  </div>
                  <StatusBadge status={c.status} size="sm" />
                  <ArrowRight className="w-3.5 h-3.5 text-gray-300 group-hover:text-primary-500 flex-shrink-0 transition-colors" />
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
