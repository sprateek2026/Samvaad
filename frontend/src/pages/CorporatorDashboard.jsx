import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { dashboardAPI } from "../api";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { FileText, Clock, CheckCircle2, Star, Shield, MessageSquare } from "lucide-react";
import KpiCard from "../components/ui/KpiCard";
import StatusBadge from "../components/ui/StatusBadge";
import PageHeader from "../components/ui/PageHeader";

const STATUS_COLORS = { submitted: "#f59e0b", under_review: "#3b82f6", assigned: "#8b5cf6", in_progress: "#f97316", escalated: "#ef4444", resolved: "#22c55e", closed: "#6b7280", reopened: "#f97316" };

export default function CorporatorDashboard({ user }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);

  useEffect(() => { if (user) fetchStats(); }, [user]);

  const mapContainer = useRef(null);
  const map = useRef(null);

  async function fetchStats() {
    try { const res = await dashboardAPI.corporatorStats(); setStats(res.data); } catch {}
  }

  useEffect(() => {
    if (!map.current && mapContainer.current && stats) {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: `https://api.maptiler.com/maps/streets/style.json?key=${import.meta.env.VITE_MAPTILER_API_KEY}`,
        center: [73.8567, 18.5204],
        zoom: 12
      });
      map.current.addControl(new maplibregl.NavigationControl(), "top-left");
    }
  }, [stats]);

  useEffect(() => {
    if (!map.current || !stats?.heatmap_data) return;
    const markers = document.getElementsByClassName("maplibregl-marker");
    while (markers.length > 0) markers[0].remove();

    stats.heatmap_data.forEach(p => {
      if (!p.lat || !p.lng) return;
      const el = document.createElement("div");
      el.className = "w-3 h-3 rounded-full border border-white shadow-sm";
      el.style.backgroundColor = STATUS_COLORS[p.status] || "#6b7280";
      new maplibregl.Marker({ element: el })
        .setLngLat([p.lng, p.lat])
        .addTo(map.current);
    });
  }, [stats]);

  if (!stats) return <div className="text-center py-12 text-gray-400">{t("dashboard.loading")}</div>;

  const byCategoryData = stats.by_category
    ? Object.entries(stats.by_category).map(([name, count]) => ({ name: name.split("/")[0].trim(), count }))
    : [];
  const STATUS_PIE_COLORS = { submitted: "#f59e0b", under_review: "#3b82f6", in_progress: "#f97316", resolved: "#22c55e" };
  const pieData = stats.by_status
    ? Object.entries(stats.by_status)
        .filter(([s]) => ["submitted","under_review","in_progress","resolved"].includes(s))
        .map(([s, v]) => ({ name: t("complaint." + s), value: v, fill: STATUS_PIE_COLORS[s] }))
    : [];
  const trendData = stats.trend_last_30 || [];

  return (
    <div className="page-content">
      <PageHeader
        title={stats.ward_name || t("app_name")}
        subtitle={stats.corporator_name}
        breadcrumb={["Corporator Dashboard"]}
      />

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        <KpiCard label={t("dashboard.total")} value={stats.total} icon={FileText} color="indigo" onClick={() => navigate("/complaints?status_group=total")} />
        <KpiCard label={t("dashboard.pending")} value={stats.pending} icon={Clock} color="saffron" onClick={() => navigate("/complaints?status_group=pending")} />
        <KpiCard label={t("dashboard.resolved")} value={stats.resolved} icon={CheckCircle2} color="emerald" onClick={() => navigate("/complaints?status_group=resolved")} />
        <KpiCard label={t("dashboard.satisfaction")} value={`${stats.satisfaction_score}%`} icon={Star} color="gold" />
        <KpiCard label={t("dashboard.sla")} value={`${stats.sla_compliance}%`} icon={Shield} color="purple" />
        <KpiCard label={t("dashboard.suggestions")} value={stats.total_suggestions || 0} icon={MessageSquare} color="rose" />
      </div>

      {stats.overdue > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-red-700 text-sm">
          ⚠️ {stats.overdue} past SLA deadline ⏰
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="ds-card p-6">
          <h3 className="font-semibold text-gray-700 mb-4">{t("dashboard.by_category")}</h3>
          {byCategoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byCategoryData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={100} />
                <Tooltip />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-400 text-sm">{t("dashboard.no_data")}</p>}
        </div>
        <div className="ds-card p-6">
          <h3 className="font-semibold text-gray-700 mb-4">{t("dashboard.pending")} vs {t("dashboard.resolved")}</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                {pieData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {trendData.length > 0 && (
        <div className="ds-card p-6 mb-6">
          <h3 className="font-semibold text-gray-700 mb-4">{t("dashboard.trend_days_30")}</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="ds-card p-6 mb-6">
        <h3 className="font-semibold text-gray-700 mb-4">{t("dashboard.heatmap")}</h3>
        <div ref={mapContainer} className="w-full h-64 rounded-xl overflow-hidden border border-gray-200" />
        {stats.heatmap_data?.length === 0 && <p className="text-gray-400 text-sm mt-2">{t("dashboard.no_data")}</p>}
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="ds-card p-6">
          <h3 className="font-semibold text-gray-700 mb-4">{t("dashboard.recent_complaints")}</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2">{t("dashboard.id")}</th>
                  <th className="pb-2">{t("dashboard.title")}</th>
                  <th className="pb-2">{t("complaint.status")}</th>
                  <th className="pb-2">{t("dashboard.citizen")}</th>
                  <th className="pb-2">{t("dashboard.age")}</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_complaints?.map((c) => (
                  <tr key={c.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 font-mono text-xs">{c.complaint_id}</td>
                    <td className="py-2">
                      <Link to={`/complaint/${c.complaint_id}`} className="text-indigo-600 hover:underline">
                        {c.title?.substring(0, 40)}
                      </Link>
                    </td>
                    <td className="py-2"><StatusBadge status={c.status} /></td>
                    <td className="py-2">{c.citizen_name}</td>
                    <td className="py-2 text-gray-500">{Math.floor((Date.now() - new Date(c.created_at).getTime()) / 86400000)}d</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="ds-card p-6">
          <h3 className="font-semibold text-gray-700 mb-4">{t("dashboard.recent_suggestions")}</h3>
          {stats.recent_suggestions?.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_suggestions.map((s) => (
                <div key={s.id} className="border border-gray-100 rounded-xl p-3">
                  <p className="font-medium text-gray-800 text-sm">{s.title}</p>
                  <p className="text-xs text-gray-500 mt-1">{s.description?.substring(0, 80)}</p>
                  <p className="text-xs text-gray-400 mt-1">— {s.citizen_name}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">{t("dashboard.no_suggestions")}</p>
          )}
        </div>
      </div>
    </div>
  );
}
