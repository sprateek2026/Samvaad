import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { complaintAPI, assetUrl } from "../api";
import ComplaintTimeline from "../components/ComplaintTimeline";
import StatusBadge from "../components/ui/StatusBadge";
import SimpleDrawer from "../components/SimpleDrawer";
import {
  ArrowLeft, Tag, AlertCircle, Calendar, Clock, MapPin,
  Bot, Star, CheckCircle2, ZoomIn,
} from "lucide-react";

const PRIORITY_COLOR = { low: "text-gray-500", medium: "text-amber-600", high: "text-red-600", urgent: "text-red-700" };
const STATUS_UPDATE_COLORS = {
  under_review: "bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100",
  in_progress:  "bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100",
  resolved:     "bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100",
};

export default function ComplaintDetail({ user }) {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const [complaint, setComplaint] = useState(null);
  const [remarks, setRemarks] = useState("");
  const [lightbox, setLightbox] = useState(null);
  const [rating, setRating] = useState(0);
  const [ratingHover, setRatingHover] = useState(0);

  useEffect(() => { if (id) fetchComplaint(); }, [id]);

  async function fetchComplaint() {
    try {
      const res = await complaintAPI.get(id);
      setComplaint(res.data);
      setRating(res.data.citizen_rating || 0);
      setRemarks("");
    } catch {}
  }

  async function handleStatusUpdate(newStatus) {
    try { await complaintAPI.updateStatus(id, { status: newStatus, remarks }); fetchComplaint(); } catch {}
  }

  async function handleRate(r) {
    try { await complaintAPI.rate(id, r); setRating(r); } catch {}
  }

  const isPastDue = complaint?.sla_deadline && new Date(complaint.sla_deadline) < new Date() && complaint.status !== "resolved";

  if (!complaint) {
    return (
      <div className="page-content max-w-3xl mx-auto">
        <div className="space-y-4 animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3" />
          <div className="ds-card p-6 space-y-4">
            <div className="h-6 bg-gray-200 rounded w-2/3" />
            <div className="grid grid-cols-4 gap-3">
              {[1,2,3,4].map(i => <div key={i} className="h-16 bg-gray-100 rounded-xl" />)}
            </div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-100 rounded" />
              <div className="h-4 bg-gray-100 rounded w-4/5" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-content max-w-3xl mx-auto">
      {/* Back button + header */}
      <div className="flex items-center gap-3 mb-5">
        <button onClick={() => navigate(-1)}
          className="w-9 h-9 flex items-center justify-center rounded-xl border border-gray-200
                     text-gray-500 hover:text-gray-800 hover:border-gray-300 hover:bg-white transition-all">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-lg font-bold text-gray-900 leading-tight truncate">{complaint.title}</h1>
            <StatusBadge status={complaint.status} />
          </div>
          <p className="text-xs text-gray-400 font-mono mt-0.5">#{complaint.complaint_id}</p>
        </div>
      </div>

      {/* Metadata grid */}
      <div className="ds-card p-5 mb-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { icon: Tag,          label: t("complaint.category_label"),  value: complaint.category_name },
            { icon: AlertCircle,  label: t("complaint.priority_label"),   value: complaint.priority,
              valueClass: PRIORITY_COLOR[complaint.priority] || "text-gray-800", capitalize: true },
            { icon: Calendar,     label: t("complaint.submitted_label"),  value: new Date(complaint.created_at).toLocaleDateString("en-IN") },
            { icon: Clock,        label: t("complaint.sla_label"),
              value: new Date(complaint.sla_deadline).toLocaleDateString("en-IN"),
              valueClass: isPastDue ? "text-red-600 font-semibold" : "" },
          ].map(({ icon: Icon, label, value, valueClass = "", capitalize }) => (
            <div key={label} className="flex items-start gap-2.5 p-3 rounded-xl bg-gray-50">
              <div className="w-7 h-7 rounded-lg bg-white border border-gray-100 flex items-center justify-center flex-shrink-0">
                <Icon className="w-3.5 h-3.5 text-gray-500" />
              </div>
              <div className="min-w-0">
                <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wide mb-0.5">{label}</p>
                <p className={`text-sm font-semibold text-gray-800 truncate ${valueClass} ${capitalize ? "capitalize" : ""}`}>{value || "—"}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className="ds-card p-5 mb-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Progress</h3>
        <ComplaintTimeline
          status={complaint.status}
          statusLog={complaint.status_log || []}
          createdAt={complaint.created_at}
        />
      </div>

      {/* Description */}
      <div className="ds-card p-5 mb-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Description</h3>
        <p className="text-sm text-gray-700 leading-relaxed">{complaint.description}</p>
        {complaint.location_lat && (
          <div className="flex items-center gap-1.5 mt-3 text-xs text-gray-500">
            <MapPin className="w-3.5 h-3.5 text-primary-500" />
            {complaint.location_address || `${complaint.location_lat.toFixed(5)}, ${complaint.location_lng.toFixed(5)}`}
          </div>
        )}
      </div>

      {/* AI Classification */}
      {complaint.ai_category && (
        <div className="ds-card p-5 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-7 h-7 rounded-lg bg-primary-50 flex items-center justify-center">
              <Bot className="w-3.5 h-3.5 text-primary-600" />
            </div>
            <h3 className="text-sm font-semibold text-gray-700">{t("complaint.ai_classification")}</h3>
          </div>
          <p className="text-sm text-gray-700 mb-2">
            Classified as <span className="font-semibold text-primary-700">{complaint.ai_category}</span>
            {" "}via <span className="text-gray-500">{complaint.ai_method}</span>
          </p>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-primary-500 rounded-full transition-all duration-500"
                   style={{ width: `${Math.round((complaint.ai_confidence || 0) * 100)}%` }} />
            </div>
            <span className="text-xs font-semibold text-primary-700 w-10 text-right">
              {Math.round((complaint.ai_confidence || 0) * 100)}%
            </span>
          </div>
        </div>
      )}

      {/* Images */}
      {complaint.images?.length > 0 && (
        <div className="ds-card p-5 mb-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Photos ({complaint.images.length})</h3>
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-thin">
            {complaint.images.map((img) => (
              <button key={img.id} onClick={() => setLightbox(img)}
                className="relative flex-shrink-0 group">
                <img src={assetUrl(img.file_path)} alt=""
                  className="h-24 w-24 object-cover rounded-xl border border-gray-100 group-hover:opacity-90 transition-opacity" />
                <div className="absolute inset-0 rounded-xl flex items-center justify-center
                                bg-black/0 group-hover:bg-black/20 transition-colors">
                  <ZoomIn className="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Corporator: Status update */}
      {(user?.role === "corporator" || user?.role === "admin") && (
        <div className="ds-card p-5 mb-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">{t("complaint.update_status")}</h3>
          <textarea value={remarks} onChange={e => setRemarks(e.target.value)}
            placeholder="Add remarks or notes..."
            className="ds-input mb-3 resize-none" rows={2} />
          <div className="flex flex-wrap gap-2">
            {["under_review","in_progress","resolved"].map(s => (
              <button key={s} onClick={() => handleStatusUpdate(s)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-xl border transition-colors capitalize ${STATUS_UPDATE_COLORS[s]}`}>
                Mark as {s.replace(/_/g," ")}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Citizen: Rating */}
      {complaint.status === "resolved" && user?.role === "citizen" && (
        <div className="ds-card p-5 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <h3 className="text-sm font-semibold text-gray-700">{t("complaint.rate_resolution")}</h3>
          </div>
          <div className="flex gap-1">
            {[1,2,3,4,5].map(n => (
              <button key={n}
                onClick={() => handleRate(n)}
                onMouseEnter={() => setRatingHover(n)}
                onMouseLeave={() => setRatingHover(0)}
                className="p-1 transition-transform hover:scale-110">
                <Star className={`w-7 h-7 transition-colors ${
                  n <= (ratingHover || rating)
                    ? "fill-gold-400 text-gold-400"
                    : "text-gray-300"
                }`} />
              </button>
            ))}
          </div>
          {rating > 0 && <p className="text-xs text-gray-500 mt-2">You rated this {rating}/5</p>}
        </div>
      )}

      {/* Image lightbox */}
      <SimpleDrawer isOpen={!!lightbox} onClose={() => setLightbox(null)} title="Photo">
        {lightbox && (
          <img src={assetUrl(lightbox.file_path)} alt=""
            className="w-full rounded-xl" />
        )}
      </SimpleDrawer>
    </div>
  );
}
