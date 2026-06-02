import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { adminAPI, gisAPI, suggestionAPI, assetUrl } from "../api";
import RepresentativeAvatar from "../components/RepresentativeAvatar";
import SimpleDrawer from "../components/SimpleDrawer";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { MAP_STYLE, withStyleFallback } from "../mapStyle";
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { FileText, Clock, CheckCircle2, AlertTriangle, Timer, TrendingUp, Lightbulb } from "lucide-react";
import KpiCard from "../components/ui/KpiCard";
import StatusBadge from "../components/ui/StatusBadge";
import PageHeader from "../components/ui/PageHeader";

const STATUS_COLORS = { submitted: "#f59e0b", under_review: "#3b82f6", assigned: "#8b5cf6", in_progress: "#f97316", escalated: "#ef4444", resolved: "#22c55e", closed: "#6b7280", reopened: "#f97316" };
const CHART_COLORS = ["#6366f1", "#f59e0b", "#22c55e", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#14b8a6"];
const NOW = Date.now();
function daysAgo(dateStr) { return Math.floor((NOW - new Date(dateStr).getTime()) / 86400000); }

export default function AdminPage({ user }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [tab, setTab] = useState("dashboard");

  useEffect(() => {
    if (user && user.role !== "admin") { navigate("/login"); return; }
  }, [user, navigate]);

  if (!user) return null;
  if (user.role !== "admin") return null;

  return (
    <div className="page-content">
      <PageHeader title={t("admin.title")} subtitle={t("app_name")} />

      <div className="flex gap-1 mb-6 border-b border-gray-200">
        <button onClick={() => setTab("dashboard")} className={`px-5 py-2.5 text-sm font-medium transition-colors border-none bg-transparent cursor-pointer outline-none border-b-2 -mb-px ${tab === "dashboard" ? "text-indigo-700 font-semibold border-indigo-600" : "text-gray-600 hover:text-gray-800 border-transparent"}`}>{t("admin.dashboard")}</button>
        <button onClick={() => setTab("suggestions")} className={`px-5 py-2.5 text-sm font-medium transition-colors border-none bg-transparent cursor-pointer outline-none border-b-2 -mb-px ${tab === "suggestions" ? "text-indigo-700 font-semibold border-indigo-600" : "text-gray-600 hover:text-gray-800 border-transparent"}`}>{t("admin.suggestions")}</button>
        <button onClick={() => setTab("representatives")} className={`px-5 py-2.5 text-sm font-medium transition-colors border-none bg-transparent cursor-pointer outline-none border-b-2 -mb-px ${tab === "representatives" ? "text-indigo-700 font-semibold border-indigo-600" : "text-gray-600 hover:text-gray-800 border-transparent"}`}>{t("admin.representatives")}</button>
      </div>

      {tab === "dashboard" && <DashboardTab />}
      {tab === "suggestions" && <SuggestionsTab />}
      {tab === "representatives" && <RepresentativesTab />}
    </div>
  );
}

// ── Dashboard Tab ──────────────────────────────────────────────────

function DashboardTab() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [retrying, setRetrying] = useState(false);
  const [wards, setWards] = useState([]);
  const [wardFilter, setWardFilter] = useState("");
  const mapContainer = useRef(null);
  const map = useRef(null);
  const STATUS_PIE_COLORS = { submitted: "#f59e0b", under_review: "#3b82f6", in_progress: "#f97316", resolved: "#22c55e" };

  function loadDashboard(isRetry = false) {
    setLoadError("");
    setLoading(true);
    if (isRetry) setRetrying(true);
    adminAPI.dashboard(wardFilter ? { ward_id: parseInt(wardFilter) } : {})
      .then(r => { setData(r.data); setLoading(false); setRetrying(false); })
      .catch(err => {
        const isNetwork = !err?.response;
        if (isNetwork && !isRetry) {
          // Backend cold start — retry once after 8s
          setRetrying(true);
          setTimeout(() => loadDashboard(true), 8000);
          return;
        }
        setLoading(false);
        setRetrying(false);
        const status = err?.response?.status;
        const detail = err?.response?.data?.detail || err?.message || "Unknown error";
        setLoadError(`Failed to load dashboard (${status || "network error"}): ${detail}`);
        console.error("[AdminDashboard]", err);
      });
  }

  useEffect(() => {
    gisAPI.wards().then(r => setWards(r.data.wards)).catch(() => {});
  }, []);

  useEffect(() => { loadDashboard(); }, [wardFilter]);

  // Destroy map on unmount so WebGL context is released
  useEffect(() => {
    return () => { map.current?.remove(); map.current = null; };
  }, []);

  // Create map once when container and first data are ready
  useEffect(() => {
    if (!map.current && mapContainer.current && data) {
      map.current = withStyleFallback(new maplibregl.Map({
        container: mapContainer.current,
        style: MAP_STYLE,
        center: [73.8567, 18.5204],
        zoom: 11
      }));
      map.current.addControl(new maplibregl.NavigationControl(), "top-left");
    }
  }, [data]);

  // Render complaint dots. Markers are DOM overlays positioned via map.project,
  // so we render immediately and also on every styledata event — this keeps the
  // dots in place after a style swap (MapTiler → OpenFreeMap fallback) or reload.
  useEffect(() => {
    if (!map.current || !data?.heatmap_data) return;
    const m = map.current;
    const points = data.heatmap_data.filter(p => p.lat && p.lng);
    const renderFresh = () => {
      const markers = document.getElementsByClassName("maplibregl-marker");
      while (markers.length > 0) markers[0].remove();
      points.forEach(p => {
        const el = document.createElement("div");
        el.className = "w-3 h-3 rounded-full border border-white shadow-sm";
        el.style.backgroundColor = STATUS_COLORS[p.status] || "#6b7280";
        new maplibregl.Marker({ element: el }).setLngLat([p.lng, p.lat]).addTo(m);
      });
    };
    // Top-up only if the dots went missing (e.g. after a style swap cleared them).
    const renderIfMissing = () => {
      if (document.getElementsByClassName("maplibregl-marker").length !== points.length) renderFresh();
    };
    renderFresh();
    m.on("styledata", renderIfMissing);
    return () => m.off("styledata", renderIfMissing);
  }, [data]);

  if (!data) return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      {loadError ? (
        <>
          <div className="text-red-600 text-sm font-medium bg-red-50 border border-red-200 rounded-xl px-5 py-3 max-w-lg text-center">
            {loadError}
          </div>
          <button onClick={() => loadDashboard()}
            className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition-colors">
            Retry
          </button>
        </>
      ) : (
        <div className="flex flex-col items-center gap-3 text-gray-400">
          <div className="w-8 h-8 border-2 border-indigo-300 border-t-indigo-600 rounded-full animate-spin" />
          <span className="text-sm">{retrying ? "Backend is waking up, retrying…" : t("dashboard.loading")}</span>
        </div>
      )}
    </div>
  );

  const pieData = (data.by_status || [])
    .filter(s => ["submitted","under_review","in_progress","resolved"].includes(s.status))
    .map(s => ({ name: t("complaint." + s.status), value: s.count, fill: STATUS_PIE_COLORS[s.status] }));
  const byWardData = data.by_ward || [];
  const byCategoryData = data.by_category || [];
  const trendData = data.trend_last_30 || [];

  const selectedWardName = wardFilter ? wards.find(w => w.id === parseInt(wardFilter))?.ward_name : t("admin.all_wards");

  return (
    <div>
      <div className="ds-card p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <label className="text-xs font-medium text-gray-500 block mb-2">{t("admin.filter_by_ward")}</label>
            <select value={wardFilter} onChange={e => setWardFilter(e.target.value)} className="px-4 py-2 border border-gray-300 rounded-lg text-sm min-w-64">
              <option value="">{t("admin.all_wards")}</option>
              {wards.map(w => <option key={w.id} value={w.id}>#{w.ward_number} — {w.ward_name}</option>)}
            </select>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">{t("admin.currently_viewing")}</p>
            <p className="text-lg font-semibold text-indigo-700">{selectedWardName}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        <KpiCard label={t("dashboard.total")} value={data.total} icon={FileText} color="indigo" onClick={() => navigate("/complaints?status_group=total")} />
        <KpiCard label={t("dashboard.pending")} value={data.pending} icon={Clock} color="saffron" onClick={() => navigate("/complaints?status_group=pending")} />
        <KpiCard label={t("dashboard.resolved")} value={data.resolved} icon={CheckCircle2} color="emerald" onClick={() => navigate("/complaints?status_group=resolved")} />
        <KpiCard label={t("admin.overdue")} value={data.overdue} icon={AlertTriangle} color="rose" />
        <KpiCard label={t("admin.avg_time")} value={`${data.avg_resolution_time}h`} icon={Timer} color="purple" />
        <KpiCard label={t("admin.sla")} value={`${data.sla_compliance}%`} icon={TrendingUp} color="gold" />
      </div>

      {data.overdue > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-red-700 text-sm">
          ⚠️ {data.overdue} {t("admin.overdue")} —
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="ds-card p-6">
          <h3 className="font-semibold text-gray-700 mb-4">{wardFilter ? t("dashboard.by_category") : t("admin.by_ward")}</h3>
          {byWardData.length > 0 && !wardFilter ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byWardData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={120} />
                <Tooltip />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : byCategoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byCategoryData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={120} />
                <Tooltip />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="text-gray-400 text-sm">{t("dashboard.no_data")}</p>}
        </div>

        <div className="ds-card p-6">
          <h3 className="font-semibold text-gray-700 mb-4">{t("dashboard.pending")} {t("dashboard.vs")} {t("dashboard.resolved")}</h3>
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

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="ds-card p-6">
          <h3 className="font-semibold text-gray-700 mb-4">{t("dashboard.heatmap")}</h3>
          <div ref={mapContainer} className="w-full h-64 rounded-xl overflow-hidden border border-gray-200" />
          {data.heatmap_data?.length === 0 && <p className="text-gray-400 text-sm mt-2">{t("dashboard.no_data")}</p>}
        </div>

        <div className="ds-card p-6">
          <h3 className="font-semibold text-gray-700 mb-4">{t("dashboard.by_category")}</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {byCategoryData.map((item, i) => (
              <div key={item.name} className="flex items-center gap-2 text-sm">
                <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                <span className="flex-1">{item.name}</span>
                <span className="font-semibold">{item.count}</span>
              </div>
            ))}
            {byCategoryData.length === 0 && <p className="text-gray-400 text-sm">{t("dashboard.no_data")}</p>}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-4 gap-4 mb-6">
        <InsightCard icon="🏛️" label={t("admin.total_wards")} value={wards.length} color="bg-blue-50 text-blue-700" />
        <InsightCard icon="👥" label={t("admin.active_reps")} value={data.active_reps || "—"} color="bg-green-50 text-green-700" />
        <InsightCard icon="⭐" label={t("admin.avg_satisfaction")} value={data.avg_satisfaction ? `${data.avg_satisfaction}★` : "—"} color="bg-yellow-50 text-yellow-700" />
        <InsightCard icon="📊" label={t("admin.resolution_rate")} value={data.resolution_rate ? `${data.resolution_rate}%` : "—"} color="bg-purple-50 text-purple-700" />
      </div>

      <div className="ds-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-700">
            {t("dashboard.recent_complaints")}
            <span className="ml-2 text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
              {data.recent_complaints?.length} / {data.total} total
            </span>
          </h3>
          <button onClick={() => navigate("/complaints")}
            className="px-3 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors">
            {t("dashboard.view_all")} ({data.total}) →
          </button>
        </div>
        <div className="overflow-x-auto max-h-[420px] overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-white">
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2 pr-3 text-xs font-semibold uppercase tracking-wide">{t("dashboard.id")}</th>
                <th className="pb-2 pr-3 text-xs font-semibold uppercase tracking-wide">{t("dashboard.title")}</th>
                <th className="pb-2 pr-3 text-xs font-semibold uppercase tracking-wide">{t("complaint.status")}</th>
                <th className="pb-2 pr-3 text-xs font-semibold uppercase tracking-wide hidden sm:table-cell">{t("dashboard.citizen")}</th>
                <th className="pb-2 pr-3 text-xs font-semibold uppercase tracking-wide hidden md:table-cell">{t("area.ward")}</th>
                <th className="pb-2 text-xs font-semibold uppercase tracking-wide">{t("dashboard.age")}</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_complaints?.map(c => (
                <tr key={c.id}
                  onClick={() => navigate(`/complaint/${c.complaint_id}`)}
                  className="border-b border-gray-100 hover:bg-indigo-50/40 cursor-pointer transition-colors">
                  <td className="py-2 pr-3 font-mono text-xs text-gray-500 whitespace-nowrap">{c.complaint_id}</td>
                  <td className="py-2 pr-3 max-w-xs truncate font-medium text-gray-800">{c.title?.substring(0, 50)}</td>
                  <td className="py-2 pr-3 whitespace-nowrap"><StatusBadge status={c.status} /></td>
                  <td className="py-2 pr-3 text-gray-500 text-xs hidden sm:table-cell whitespace-nowrap">{c.citizen_name}</td>
                  <td className="py-2 pr-3 text-gray-500 text-xs hidden md:table-cell whitespace-nowrap">
                    {c.ward_number ? `#${c.ward_number}` : "—"}
                  </td>
                  <td className="py-2 text-gray-500 text-xs whitespace-nowrap">{daysAgo(c.created_at)}d ago</td>
                </tr>
              ))}
              {(!data.recent_complaints || data.recent_complaints.length === 0) && (
                <tr><td colSpan={6} className="py-4 text-center text-gray-400 text-sm">{t("dashboard.no_complaints")}</td></tr>
              )}
            </tbody>
          </table>
        </div>
        {data.recent_complaints?.length < data.total && (
          <div className="mt-3 text-center">
            <button onClick={() => navigate("/complaints")}
              className="text-xs text-indigo-600 hover:text-indigo-800 font-medium">
              + {data.total - data.recent_complaints.length} more complaints — View full list →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── SVG Avatar Placeholder ────────────────────────────────────────

function AvatarPlaceholder({ size = "w-10 h-10" }) {
  return (
    <div className={`${size} rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0`}>
      <svg className="w-3/5 h-3/5 text-gray-300" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
      </svg>
    </div>
  );
}

// ── Representatives Tab ────────────────────────────────────────────

const CORPORATOR_LABELS = ["A", "B", "C", "D"];

function RepresentativesTab() {
  const { t } = useTranslation();
  const [wards, setWards] = useState([]);
  const [wardId, setWardId] = useState("");
  const [reps, setReps] = useState([]);
  const [editing, setEditing] = useState(null);
  const [kycRep, setKycRep] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState("");
  const [partyFilter, setPartyFilter] = useState("");

  useEffect(() => {
    gisAPI.wards().then(r => setWards(r.data.wards)).catch(() => {});
  }, []);

  useEffect(() => {
    if (!wardId) return;
    let cancelled = false;
    adminAPI.listReps({ ward_id: parseInt(wardId) }).then(r => { if (!cancelled) setReps(r.data.representatives); }).catch(() => { if (!cancelled) setReps([]); });
    return () => { cancelled = true; };
  }, [wardId]);

  function repForLabel(label) {
    return filteredReps.find(r => r.type === "corporator" && r.label === label);
  }

  function repForType(type) {
    return filteredReps.find(r => r.type === type);
  }

  async function handleDelete(rep) {
    if (!confirm(t("admin.confirm_delete"))) return;
    try {
      await adminAPI.deleteRep(rep.id);
      setReps(prev => prev.filter(r => r.id !== rep.id));
    } catch {}
  }

  async function handleSave(formData, editingId) {
    setLoading(true);
    try {
      let res;
      if (editingId) {
        res = await adminAPI.updateRep(editingId, formData);
        setReps(prev => prev.map(r => r.id === editingId ? res.data : r));
      } else {
        res = await adminAPI.createRep(formData);
        setReps(prev => [...prev, res.data]);
      }
      setEditing(null);
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
    setLoading(false);
  }

  function openEditCorp(label) {
    const existing = repForLabel(label);
    setEditing(existing ? { ...existing, ward_id: parseInt(wardId) } : { ward_id: parseInt(wardId), type: "corporator", label, name: "", party: "", constituency: "", photo: null });
  }

  function openEdit(type) {
    const existing = repForType(type);
    setEditing(existing ? { ...existing, ward_id: parseInt(wardId) } : { ward_id: parseInt(wardId), type, name: "", party: "", constituency: "", photo: null });
  }

  const selectedWard = wards.find(w => w.id === parseInt(wardId));

  // Get unique parties for filter
  const parties = [...new Set(reps.filter(r => r.party).map(r => r.party))].sort();

  // Filter representatives
  const filteredReps = reps.filter(rep => {
    const matchesSearch = !searchText ||
      rep.name?.toLowerCase().includes(searchText.toLowerCase()) ||
      rep.party?.toLowerCase().includes(searchText.toLowerCase());
    const matchesParty = !partyFilter || rep.party === partyFilter;
    return matchesSearch && matchesParty;
  });

  return (
    <div>
      <div className="ds-card p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
          <select value={wardId} onChange={e => { setWardId(e.target.value); setSearchText(""); setPartyFilter(""); }} className="px-4 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="">{t("admin.select_ward")}</option>
            {wards.map(w => <option key={w.id} value={w.id}>#{w.ward_number} — {w.ward_name}</option>)}
          </select>

          <input
            type="text"
            placeholder={t("admin.search_name_party")}
            value={searchText}
            onChange={e => setSearchText(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />

          <select value={partyFilter} onChange={e => setPartyFilter(e.target.value)} className="px-4 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="">{t("admin.filter_by_party")}</option>
            {parties.map(party => <option key={party} value={party}>{party}</option>)}
          </select>
        </div>

        {selectedWard && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">{selectedWard.ward_name} — {filteredReps.length} {filteredReps.length === 1 ? t("admin.representative") : t("admin.representatives_plural")}</span>
            {(searchText || partyFilter) && (
              <button onClick={() => { setSearchText(""); setPartyFilter(""); }} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">{t("admin.clear_filters")}</button>
            )}
          </div>
        )}
      </div>

      {!wardId && <p className="text-gray-400 text-sm text-center py-12">{t("admin.select_ward")}</p>}

      {wardId && (
        <div>
          <h3 className="text-md font-semibold text-gray-700 mb-3">{t("admin.corporators_heading")}</h3>
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            {CORPORATOR_LABELS.map(label => {
              const rep = repForLabel(label);
              return (
                <div key={label} className={`ds-card p-4 flex items-center gap-3 ${rep ? "" : "border-2 border-dashed border-gray-200"}`}>
                  {rep ? (
                    <>
                      <div className="group">
                        <RepresentativeAvatar photoPath={rep.photo_path} name={rep.name} type={rep.type} size="md" showHover={true} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <p className="font-medium text-sm truncate">{rep.name}</p>
                          {rep.user_id ? (
                            <span className="w-1.5 h-1.5 rounded-full bg-green-400 flex-shrink-0" title={t("admin.user_exists")} />
                          ) : (
                            <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 flex-shrink-0" title={t("admin.no_login")} />
                          )}
                        </div>
                        {rep.party && <p className="text-xs text-gray-500">{rep.party}</p>}
                      </div>
                      <div className="flex gap-1 flex-shrink-0">
                        <button onClick={() => setKycRep(rep)} className="p-1.5 text-gray-400 hover:text-teal-600 hover:bg-teal-50 rounded-lg transition-colors" title={t("admin.know_your_corporator")}>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        </button>
                        <button onClick={() => openEditCorp(label)} className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors" title={t("admin.edit_rep")}>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                        </button>
                        <button onClick={() => handleDelete(rep)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title={t("admin.delete_rep")}>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <AvatarPlaceholder size="w-10 h-10" />
                      <div className="flex-1">
                        <p className="text-sm text-gray-400">{t("admin.slot_empty")} {label}</p>
                      </div>
                      <button onClick={() => openEditCorp(label)} className="px-8 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex-shrink-0 font-medium">{t("admin.add_rep")}</button>
                    </>
                  )}
                </div>
              );
            })}
          </div>

          <h3 className="text-md font-semibold text-gray-700 mb-3">{t("admin.mla_mp")}</h3>
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            {["mla", "mp"].map(type => {
              const rep = repForType(type);
              return (
                <div key={type} className="ds-card p-4 flex items-center gap-4">
                  {rep ? (
                    <>
                      <div className="group">
                        <RepresentativeAvatar photoPath={rep.photo_path} name={rep.name} type={rep.type} size="md" showHover={true} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-sm truncate">{rep.name}</p>
                          <span className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{t(`area.${type}`)}</span>
                        </div>
                        {rep.party && <p className="text-xs text-gray-500">{rep.party}</p>}
                        {rep.constituency && <p className="text-xs text-gray-400">{rep.constituency}</p>}
                      </div>
                      <div className="flex gap-1 flex-shrink-0">
                        <button onClick={() => setKycRep(rep)} className="p-1.5 text-gray-400 hover:text-teal-600 hover:bg-teal-50 rounded-lg transition-colors" title={t("admin.know_your_corporator")}>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        </button>
                        <button onClick={() => openEdit(type)} className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors" title={t("admin.edit_rep")}>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                        </button>
                        <button onClick={() => handleDelete(rep)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title={t("admin.delete_rep")}>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <AvatarPlaceholder size="w-10 h-10" />
                      <div className="flex-1">
                        <p className="text-sm text-gray-400">{t("admin.no_rep")} {t(`area.${type}`)}</p>
                      </div>
                      <button onClick={() => openEdit(type)} className="px-8 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex-shrink-0 font-medium">{t("admin.add_rep")}</button>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {kycRep && <KycModal rep={kycRep} onClose={() => setKycRep(null)} />}

      {editing && (
        <EditRepModal
          rep={editing}
          loading={loading}
          onSave={handleSave}
          onClose={() => setEditing(null)}
        />
      )}
    </div>
  );
}

// ── Edit Representative Modal ──────────────────────────────────────

function EditRepModal({ rep, loading, onSave, onClose }) {
  const { t } = useTranslation();
  const [form, setForm] = useState({
    name: rep.name || "",
    party: rep.party || "",
    constituency: rep.constituency || "",
    label: rep.label || "A",
    mobile: ""
  });
  const [photoFile, setPhotoFile] = useState(null);
  const [preview, setPreview] = useState(rep.photo_path ? assetUrl(rep.photo_path) : null);

  const showMobile = !rep.id || !rep.user_id;

  function handlePhotoChange(e) {
    const file = e.target.files[0];
    if (file) {
      setPhotoFile(file);
      setPreview(URL.createObjectURL(file));
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    const fd = new FormData();
    fd.append("ward_id", rep.ward_id);
    fd.append("type", rep.type);
    fd.append("name", form.name);
    fd.append("party", form.party);
    fd.append("constituency", form.constituency);
    fd.append("label", form.label);
    if (showMobile && form.mobile) fd.append("mobile", form.mobile);
    if (photoFile) fd.append("photo", photoFile);
    onSave(fd, rep.id);
  }

  return (
    <SimpleDrawer
      isOpen={true}
      onClose={onClose}
      title={`${rep.id ? t("admin.edit_rep") : t("admin.add_rep")} — ${t("area." + rep.type)}`}
    >
      <form onSubmit={handleSubmit}>
        <label className="block text-sm font-medium text-gray-700 mb-1">{t("auth.full_name")}</label>
        <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-3" />

        <label className="block text-sm font-medium text-gray-700 mb-1">{t("admin.party")}</label>
        <input type="text" value={form.party} onChange={e => setForm({ ...form, party: e.target.value })} placeholder="BJP / INC / NCP / ..." className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-3" />

        {rep.type === "corporator" && (
          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("admin.slot_label")}</label>
            <select value={form.label} onChange={e => setForm({ ...form, label: e.target.value })} className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm">
              {CORPORATOR_LABELS.map(l => <option key={l} value={l}>{t("admin.slot_" + l.toLowerCase())}</option>)}
            </select>
          </div>
        )}

        {rep.type !== "corporator" && (
          <>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("admin.constituency")}</label>
            <input type="text" value={form.constituency} onChange={e => setForm({ ...form, constituency: e.target.value })} className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-3" />
          </>
        )}

        {showMobile && (
          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("auth.mobile")} <span className="text-gray-400 font-normal">{t("admin.mobile_optional")}</span></label>
            <input type="tel" value={form.mobile} onChange={e => setForm({ ...form, mobile: e.target.value })} placeholder="9876543210" maxLength={10} className="w-full px-4 py-2 border border-gray-300 rounded-lg" />
            {rep.user_id ? null : <p className="text-xs text-gray-400 mt-1">{t("admin.mobile_hint")}</p>}
          </div>
        )}

        {rep.user_id ? (
          <div className="mb-3 text-xs text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2">{t("admin.user_exists")}</div>
        ) : null}

        <label className="block text-sm font-medium text-gray-700 mb-1">{t("admin.photo")}</label>
        <input type="file" accept="image/*" onChange={handlePhotoChange} className="w-full text-xs mb-2" />
        {preview && <img src={preview} alt="Preview" className="w-10 h-10 rounded-full object-cover mb-2 border" />}

        <div className="flex gap-3 mt-6 pt-4 border-t border-gray-200">
          <button type="button" onClick={onClose} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">{t("auth.back")}</button>
          <button onClick={handleSubmit} disabled={loading} className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">{loading ? t("admin.saving") : t("admin.save")}</button>
        </div>
      </form>
    </SimpleDrawer>
  );
}

// ── KYC Modal (Know Your Corporator) ──────────────────────────────

function KycModal({ rep, onClose }) {
  const { t } = useTranslation();
  return (
    <SimpleDrawer
      isOpen={true}
      onClose={onClose}
      title={t("admin.know_your", { type: t(`area.${rep.type}`) })}
    >
      <div className="flex items-center gap-4 mb-6">
        <RepresentativeAvatar photoPath={rep.photo_path} name={rep.name} type={rep.type} size="xl" showHover={false} />
        <div>
          <p className="text-xl font-bold text-gray-800">{rep.name}</p>
          <p className="text-sm text-gray-500">{t(`area.${rep.type}`)}{rep.label ? ` (${rep.label})` : ""}</p>
          {rep.party && <p className="text-sm text-gray-500">{rep.party}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        {rep.contact && (
          <div>
            <span className="text-gray-500 block">{t("admin.contact")}</span>
            <span className="font-medium">{rep.contact}</span>
          </div>
        )}
        {rep.term && (
          <div>
            <span className="text-gray-500 block">{t("admin.term")}</span>
            <span className="font-medium">{rep.term}</span>
          </div>
        )}
        {rep.constituency && (
          <div className="col-span-2">
            <span className="text-gray-500 block">{t("admin.constituency")}</span>
            <span className="font-medium">{rep.constituency}</span>
          </div>
        )}
        {rep.bio && (
          <div className="col-span-2">
            <span className="text-gray-500 block">{t("admin.bio")}</span>
            <p className="text-gray-700">{rep.bio}</p>
          </div>
        )}
        {rep.achievements && (
          <div className="col-span-2">
            <span className="text-gray-500 block">{t("admin.achievements")}</span>
            <p className="text-gray-700 whitespace-pre-line">{rep.achievements}</p>
          </div>
        )}
      </div>

      {!rep.contact && !rep.bio && !rep.term && !rep.achievements && (
        <p className="text-gray-400 text-sm text-center py-4">{t("admin.no_details")}</p>
      )}
    </SimpleDrawer>
  );
}

// ── Shared Components ──────────────────────────────────────────────

function InsightCard({ icon, label, value, color }) {
  return (
    <div className={`${color} rounded-xl p-4 shadow-sm`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl">{icon}</span>
        <div className="flex-1">
          <p className="text-xs font-medium opacity-75 mb-0.5">{label}</p>
          <p className="text-xl font-bold">{value}</p>
        </div>
      </div>
    </div>
  );
}

// ── Suggestions Tab ────────────────────────────────────────────────

function SuggestionsTab() {
  const { t } = useTranslation();
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    suggestionAPI.list()
      .then(r => setSuggestions(r.data.suggestions))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
          <Lightbulb size={20} className="text-white" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-gray-900">{t("admin.suggestions")}</h2>
          <p className="text-sm text-gray-500">{suggestions.length} {t("admin.suggestions_total")}</p>
        </div>
      </div>

      {suggestions.length === 0 ? (
        <div className="ds-card p-12 text-center text-gray-400">
          <Lightbulb size={40} className="mx-auto mb-3 opacity-30" />
          <p className="text-sm">{t("dashboard.no_suggestions")}</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {suggestions.map(s => (
            <div key={s.id} className="ds-card p-5 flex flex-col gap-2">
              <div className="flex items-start justify-between gap-2">
                <p className="font-semibold text-gray-900 text-sm leading-snug">{s.title}</p>
                <span className="text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full whitespace-nowrap">#{s.id}</span>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed flex-1">{s.description}</p>
              <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-xs text-gray-400">
                <span>{s.citizen_name}</span>
                <span>{new Date(s.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

