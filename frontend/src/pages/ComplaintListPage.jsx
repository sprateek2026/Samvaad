import { useState, useEffect } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { complaintAPI, dashboardAPI, adminAPI } from "../api";
import StatusBadge from "../components/ui/StatusBadge";
import PageHeader from "../components/ui/PageHeader";
import { ArrowLeft, FilePlus2, FileText, ArrowRight } from "lucide-react";

const TABS = [
  { key: "total",    labelKey: "complaint.tab_all" },
  { key: "pending",  labelKey: "complaint.tab_pending" },
  { key: "resolved", labelKey: "complaint.tab_resolved" },
];

function SkeletonRow() {
  return (
    <tr className="border-b border-gray-50 animate-pulse">
      {[1,2,3,4,5,6].map(i => (
        <td key={i} className="py-4 pr-4">
          <div className="h-4 bg-gray-100 rounded w-3/4" />
        </td>
      ))}
    </tr>
  );
}

export default function ComplaintListPage({ user }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const group = searchParams.get("status_group") || "total";
  const [complaints, setComplaints] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => { if (user) fetchData(1); }, [user, group]);

  async function fetchData(p = page) {
    setLoading(true);
    try {
      const params = group !== "total" ? { status_group: group } : {};
      let res;
      if (user.role === "corporator")     res = await dashboardAPI.corporatorComplaints(params);
      else if (user.role === "admin")     res = await adminAPI.complaints({ ...params, page: p });
      else                                res = await complaintAPI.list(params);
      setComplaints(res.data.complaints || []);
      if (res.data.total != null) { setTotal(res.data.total); setPages(res.data.pages || 1); setPage(p); }
    } catch (err) { console.error("[ComplaintList]", err?.response?.data || err?.message || err); setComplaints([]); }
    setLoading(false);
  }

  function setGroup(g) { setPage(1); setSearchParams(g === "total" ? {} : { status_group: g }); }

  const backPath = user?.role === "corporator" ? "/corporator" : user?.role === "admin" ? "/admin" : "/";
  const isAdmin = user?.role === "admin";

  return (
    <div className="page-content">
      <div className="flex items-center gap-3 mb-1">
        <button onClick={() => navigate(backPath)}
          className="w-9 h-9 flex items-center justify-center rounded-xl border border-gray-200
                     text-gray-500 hover:text-gray-800 hover:border-gray-300 hover:bg-white transition-all">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <PageHeader
          title={t("complaint.list_title")}
          subtitle={t("complaint.list_subtitle", {
            count: isAdmin ? total : complaints.length,
            group: t(TABS.find(tb => tb.key === group)?.labelKey || "complaint.tab_all"),
          })}
          action={user?.role === "citizen" ? (
            <Link to="/raise" className="btn-saffron">
              <FilePlus2 className="w-4 h-4" /> {t("complaint.raise_new")}
            </Link>
          ) : null}
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit mb-5">
        {TABS.map(tab => (
          <button key={tab.key} onClick={() => setGroup(tab.key)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-150
              ${group === tab.key
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"}`}>
            {t(tab.labelKey)}
          </button>
        ))}
      </div>

      {/* Table card */}
      <div className="ds-card overflow-hidden">
        {loading ? (
          <table className="w-full text-sm">
            <tbody>{[1,2,3].map(i => <SkeletonRow key={i} />)}</tbody>
          </table>
        ) : complaints.length === 0 ? (
          <div className="flex flex-col items-center py-16 gap-3">
            <div className="w-14 h-14 rounded-2xl bg-gray-100 flex items-center justify-center">
              <FileText className="w-6 h-6 text-gray-400" />
            </div>
            <p className="text-sm font-medium text-gray-600">{t("dashboard.no_complaints")}</p>
            {user?.role === "citizen" && (
              <Link to="/raise" className="btn-saffron text-sm">{t("dashboard.raise_now")}</Link>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50/50">
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-5 py-3 whitespace-nowrap">{t("dashboard.id")}</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3">{t("dashboard.title")}</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3 whitespace-nowrap">{t("complaint.status")}</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3 hidden sm:table-cell">{t("dashboard.citizen")}</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3 hidden md:table-cell whitespace-nowrap">{t("area.ward")}</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3 whitespace-nowrap">{t("dashboard.age")}</th>
                  <th className="w-8" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {complaints.map((c) => {
                  const ageDays = Math.floor((Date.now() - new Date(c.created_at)) / 86400000);
                  const ageColor = ageDays > 14 ? "text-red-600 font-semibold" : ageDays > 7 ? "text-amber-600 font-medium" : "text-gray-500";
                  return (
                    <tr key={c.id}
                      onClick={() => navigate(`/complaint/${c.complaint_id}`)}
                      className="hover:bg-[#f8faff] cursor-pointer group transition-colors">
                      <td className="px-5 py-3.5 font-mono text-xs text-gray-500 whitespace-nowrap">
                        {c.complaint_id}
                      </td>
                      <td className="px-4 py-3.5 max-w-[200px] lg:max-w-xs">
                        <span className="text-gray-900 font-medium truncate block group-hover:text-primary-700 transition-colors">
                          {c.title}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 whitespace-nowrap">
                        <StatusBadge status={c.status} size="sm" />
                      </td>
                      <td className="px-4 py-3.5 text-gray-600 whitespace-nowrap hidden sm:table-cell text-xs">
                        {c.citizen_name || "—"}
                      </td>
                      <td className="px-4 py-3.5 text-gray-500 whitespace-nowrap hidden md:table-cell text-xs">
                        {c.ward_number ? `#${c.ward_number}` : "—"}
                        {c.ward_name ? ` ${c.ward_name}` : ""}
                      </td>
                      <td className={`px-4 py-3.5 whitespace-nowrap text-xs ${ageColor}`}>
                        {ageDays === 0 ? t("common.today") : t("common.day_short", { count: ageDays })}
                      </td>
                      <td className="pr-4 py-3.5">
                        <ArrowRight className="w-3.5 h-3.5 text-gray-300 group-hover:text-primary-500 transition-colors" />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination — admin only */}
      {isAdmin && pages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-xs text-gray-500">
            Page {page} of {pages} · {total} complaints
          </p>
          <div className="flex gap-2">
            <button onClick={() => fetchData(page - 1)} disabled={page <= 1}
              className="px-3 py-1.5 text-xs rounded-lg border border-gray-200 text-gray-600
                         hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">
              ← Prev
            </button>
            <button onClick={() => fetchData(page + 1)} disabled={page >= pages}
              className="px-3 py-1.5 text-xs rounded-lg border border-gray-200 text-gray-600
                         hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed">
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
