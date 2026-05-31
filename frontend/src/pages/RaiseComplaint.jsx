import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { complaintAPI, suggestionAPI, categoryAPI } from "../api";
import {
  Shield, Lightbulb, Tag, ListTree, FileEdit, CheckCircle2,
  Camera, MapPin, Mic, MicOff, Copy, Check, ChevronLeft,
  Search, Loader2, Clock, Plus,
} from "lucide-react";

const ICONS = ["🚰","🗑️","🛣️","💡","🧹","🌳","🏥","📚","🚦","🔒","🌿","🏗️","🤝","💻","🆘","👥","⚖️","🏙️"];

const CATEGORY_GRADIENTS = [
  "from-blue-500 to-blue-600","from-gray-600 to-gray-700","from-amber-500 to-amber-600",
  "from-yellow-500 to-yellow-600","from-green-500 to-green-600","from-emerald-500 to-emerald-600",
  "from-red-500 to-red-600","from-orange-500 to-orange-600","from-rose-500 to-rose-600",
  "from-purple-500 to-purple-600","from-teal-500 to-teal-600","from-cyan-500 to-cyan-600",
  "from-indigo-500 to-indigo-600","from-violet-500 to-violet-600","from-pink-500 to-pink-600",
  "from-sky-500 to-sky-600","from-lime-500 to-lime-600","from-fuchsia-500 to-fuchsia-600",
];

const STEP_ICONS = [Tag, ListTree, FileEdit, CheckCircle2];
const STEP_KEYS = ["complaint.step_category","complaint.step_sub_issue","complaint.step_details","complaint.step_done"];

const SLA_DAYS = { water: 3, road: 7, electric: 2, waste: 5, garbage: 5, health: 3, sanit: 5, tree: 10, park: 10, education: 14, light: 2, drain: 4 };

export default function RaiseComplaint({ user }) {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const fileRef = useRef();

  const [mode, setMode] = useState(null);
  const [categories, setCategories] = useState([]);
  const [subCategories, setSubCategories] = useState([]);
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ title: "", description: "", category_id: null, sub_category_id: null, images: [] });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [location, setLocation] = useState(null);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [copied, setCopied] = useState(false);

  function localizedName(item) {
    if (!item) return "";
    if (i18n.language === "mr") return item.name_mr || item.name;
    if (i18n.language === "hi") return item.name_hi || item.name;
    return item.name;
  }

  useEffect(() => {
    if (!user) { navigate("/login"); return; }
    categoryAPI.list().then(r => setCategories(r.data.categories)).catch(() => {});
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        pos => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => {},
        { timeout: 5000 }
      );
    }
  }, [user, navigate]);

  const filteredCategories = categories.filter(c =>
    localizedName(c).toLowerCase().includes(searchQuery.toLowerCase())
  );

  function handleCategorySelect(id) {
    setForm({ ...form, category_id: id, sub_category_id: null, title: "", description: "" });
    categoryAPI.subCategories(id).then(r => {
      setSubCategories(r.data.sub_categories);
      setStep(2);
    }).catch(() => setStep(2));
  }

  function handleSubCategorySelect(sub) {
    setForm(prev => ({ ...prev, sub_category_id: sub.id, title: sub.name, description: sub.name }));
    setStep(3);
  }

  function handleOtherSelect() {
    setForm(prev => ({ ...prev, sub_category_id: null, title: "", description: "" }));
    setStep(3);
  }

  function handleImages(files) {
    const arr = Array.from(files);
    const sliced = arr.slice(0, 5);
    setForm(prev => ({ ...prev, images: sliced }));
    setImagePreviews(sliced.map(f => URL.createObjectURL(f)));
  }

  function removeImage(i) {
    URL.revokeObjectURL(imagePreviews[i]);
    setForm(prev => ({ ...prev, images: prev.images.filter((_, idx) => idx !== i) }));
    setImagePreviews(prev => prev.filter((_, idx) => idx !== i));
  }

  function detectLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        pos => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => {},
        { timeout: 5000 }
      );
    }
  }

  async function handleSubmitComplaint(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("title", form.title);
      fd.append("description", form.description);
      if (form.category_id) fd.append("category_id", form.category_id);
      if (form.sub_category_id) fd.append("sub_category_id", form.sub_category_id);
      if (location) {
        fd.append("latitude", location.lat);
        fd.append("longitude", location.lng);
      }
      for (const img of form.images) fd.append("images", img);
      const res = await complaintAPI.create(fd);
      setResult(res.data);
      setStep(4);
    } catch (err) {
      alert(t("common.error") + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  }

  async function handleSubmitSuggestion(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await suggestionAPI.create({ title: form.title, description: form.description });
      setResult({ suggestion_id: res.data.suggestion_id, type: "suggestion" });
      setStep(4);
    } catch (err) {
      alert(t("common.error") + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  }

  function resetForm() {
    setMode(null);
    setStep(1);
    setForm({ title: "", description: "", category_id: null, sub_category_id: null, images: [] });
    setResult(null);
    setSubCategories([]);
    setSearchQuery("");
    setImagePreviews([]);
  }

  function handleVoiceInput() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    const recognition = new SR();
    recognition.lang = i18n.language === "mr" ? "mr-IN" : i18n.language === "hi" ? "hi-IN" : "en-IN";
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = e => {
      const transcript = e.results[0][0].transcript;
      setForm(prev => {
        const joined = prev.description ? prev.description + " " + transcript : transcript;
        return { ...prev, description: joined.slice(0, 500) };
      });
    };
    recognition.start();
  }

  function handleCopyId(id) {
    navigator.clipboard.writeText(id).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => {});
  }

  function getSLADays() {
    const cat = categories.find(c => c.id === form.category_id);
    if (!cat) return 10;
    const name = (cat.name || "").toLowerCase();
    for (const [key, days] of Object.entries(SLA_DAYS)) {
      if (name.includes(key)) return days;
    }
    return 10;
  }

  if (!user) return null;

  // ── Mode selection ──────────────────────────────────────────────────────────
  if (!mode) {
    return (
      <div className="min-h-[200px] flex items-center justify-center py-10 px-4">
        <div className="max-w-lg w-full">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{t("app_name")}</h2>
            <p className="text-gray-500">{t("complaint.how_can_we_help")}</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <button onClick={() => setMode("complaint")}
              className="group relative overflow-hidden rounded-2xl bg-white border-2 border-indigo-100 hover:border-indigo-400 p-6 text-left transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mb-4 shadow-md shadow-indigo-200">
                  <Shield size={28} className="text-white" />
                </div>
                <p className="text-base font-semibold text-gray-900 mb-1">{t("complaint.raise")}</p>
                <p className="text-sm text-gray-500">{t("complaint.report_issue")}</p>
              </div>
            </button>
            <button onClick={() => setMode("suggestion")}
              className="group relative overflow-hidden rounded-2xl bg-white border-2 border-amber-100 hover:border-amber-400 p-6 text-left transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
              <div className="absolute inset-0 bg-gradient-to-br from-amber-50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mb-4 shadow-md shadow-amber-200">
                  <Lightbulb size={28} className="text-white" />
                </div>
                <p className="text-base font-semibold text-gray-900 mb-1">{t("complaint.submit_suggestion_title")}</p>
                <p className="text-sm text-gray-500">{t("complaint.suggestion_desc")}</p>
              </div>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Suggestion form ─────────────────────────────────────────────────────────
  if (mode === "suggestion") {
    return (
      <div className="max-w-2xl mx-auto py-8 px-4">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 animate-fade-in-up">
          <div className="flex items-center gap-4 mb-6">
            <button onClick={resetForm}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition">
              <ChevronLeft size={16} />
              {t("auth.back")}
            </button>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center flex-shrink-0">
              <Lightbulb size={22} className="text-white" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">{t("complaint.submit_suggestion_title")}</h2>
          </div>
          <form onSubmit={handleSubmitSuggestion} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">{t("complaint.title")}</label>
              <input type="text" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
                required placeholder={t("complaint.suggestion_title_placeholder")}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">{t("complaint.description")}</label>
              <textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                required rows="5" placeholder={t("complaint.write_description")}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition resize-none" />
            </div>
            <div className="flex justify-end pt-2">
              <button type="submit" disabled={loading}
                className="px-6 py-2.5 bg-gradient-to-r from-amber-500 to-orange-600 text-white font-semibold rounded-xl hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2 disabled:opacity-60">
                {loading && <Loader2 size={16} className="animate-spin" />}
                {loading ? t("complaint.submitting") : t("complaint.submit_suggestion")}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // ── Complaint wizard ────────────────────────────────────────────────────────
  return (
    <div className="max-w-2xl mx-auto py-8 px-4">

      {/* Step Progress */}
      <div className="flex items-center justify-center mb-10">
        {STEP_KEYS.map((key, i) => {
          const stepNum = i + 1;
          const isActive = stepNum === step;
          const isDone = stepNum < step;
          const StepIcon = STEP_ICONS[i];
          return (
            <div key={key} className="flex items-center">
              <div className="flex flex-col items-center">
                <div className={`w-9 h-9 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isDone ? "bg-emerald-500 text-white shadow-md shadow-emerald-200" :
                  isActive ? "bg-primary-600 text-white shadow-md shadow-indigo-200 ring-2 ring-offset-2 ring-primary-500" :
                  "bg-gray-100 text-gray-400"
                }`}>
                  {isDone ? <CheckCircle2 size={16} /> : <StepIcon size={16} />}
                </div>
                <span className={`text-xs mt-1.5 font-medium transition-colors duration-200 ${
                  isActive ? "text-primary-600" : isDone ? "text-emerald-600" : "text-gray-400"
                }`}>
                  {t(key)}
                </span>
              </div>
              {i < STEP_KEYS.length - 1 && (
                <div className={`w-16 md:w-24 h-0.5 mx-3 rounded transition-colors duration-300 ${
                  isDone ? "bg-emerald-400" : "bg-gray-200"
                }`} />
              )}
            </div>
          );
        })}
      </div>

      {/* Step 1: Category Selection */}
      {step === 1 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 animate-fade-in-up">
          <div className="relative mb-4">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
              placeholder={t("complaint.search_category")}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition bg-gray-50" />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {filteredCategories.map((cat, i) => (
              <button key={cat.id} onClick={() => handleCategorySelect(cat.id)}
                className="group flex flex-col items-center gap-2 p-3.5 bg-white border border-gray-100 rounded-xl hover:border-indigo-300 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 text-center">
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${CATEGORY_GRADIENTS[i % CATEGORY_GRADIENTS.length]} flex items-center justify-center flex-shrink-0 shadow-sm`}>
                  <span className="text-base">{ICONS[i] || "📌"}</span>
                </div>
                <p className="font-medium text-gray-900 text-xs group-hover:text-indigo-700 transition-colors leading-tight">{localizedName(cat)}</p>
              </button>
            ))}
            <button onClick={() => handleCategorySelect(0)}
              className="group flex flex-col items-center gap-2 p-3.5 bg-white border-2 border-dashed border-gray-200 rounded-xl hover:border-indigo-400 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 text-center">
              <div className="w-10 h-10 rounded-lg bg-gray-50 flex items-center justify-center flex-shrink-0">
                <Plus size={20} className="text-gray-400" />
              </div>
              <p className="font-medium text-gray-600 text-xs">{t("complaint.other")}</p>
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Sub-Category */}
      {step === 2 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 animate-fade-in-up">
          <div className="flex items-center gap-3 mb-5">
            <button onClick={() => setStep(1)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition">
              <ChevronLeft size={16} />
              {t("auth.back")}
            </button>
            <h2 className="text-lg font-bold text-gray-900">{t("complaint.select_sub_issue")}</h2>
          </div>
          <div className="space-y-1.5">
            {subCategories.map((sub, i) => (
              <button key={sub.id} onClick={() => handleSubCategorySelect(sub)}
                className={`w-full text-left p-3.5 rounded-xl border transition-all duration-200 group hover:border-indigo-300 hover:shadow-sm animate-fade-in-up stagger-${Math.min(i + 1, 6)} ${
                  form.sub_category_id === sub.id
                    ? "border-indigo-400 bg-indigo-50 border-l-4 border-l-indigo-500"
                    : "border-gray-100 hover:bg-gray-50 border-l-4 border-l-transparent"
                }`}>
                <p className="font-medium text-gray-800 text-sm group-hover:text-indigo-700 transition-colors">{localizedName(sub)}</p>
              </button>
            ))}
            <button onClick={handleOtherSelect}
              className="w-full text-left p-3.5 rounded-xl border-2 border-dashed border-gray-200 hover:border-indigo-400 hover:bg-gray-50 transition-all duration-200 mt-3 group">
              <p className="font-medium text-gray-500 text-sm group-hover:text-indigo-600 transition-colors">{t("complaint.other_write")}</p>
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Details Form */}
      {step === 3 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 animate-fade-in-up">
          <div className="flex items-center gap-3 mb-4">
            <button onClick={() => setStep(2)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition">
              <ChevronLeft size={16} />
              {t("auth.back")}
            </button>
            <h2 className="text-lg font-bold text-gray-900">{t("complaint.describe_issue")}</h2>
          </div>

          {/* Summary chips */}
          <div className="flex flex-wrap gap-2 mb-5">
            {categories.find(c => c.id === form.category_id) && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-700 border border-amber-200 rounded-full text-xs font-semibold">
                <Tag size={11} />
                {localizedName(categories.find(c => c.id === form.category_id))}
              </span>
            )}
            {form.sub_category_id && subCategories.find(s => s.id === form.sub_category_id) && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-full text-xs font-semibold">
                <ListTree size={11} />
                {localizedName(subCategories.find(s => s.id === form.sub_category_id))}
              </span>
            )}
          </div>

          <form onSubmit={handleSubmitComplaint} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">{t("complaint.title")}</label>
              <input type="text" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
                required placeholder={t("complaint.title_placeholder")}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition" />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-sm font-medium text-gray-700">{t("complaint.description")}</label>
                <span className={`text-xs font-medium ${form.description.length > 450 ? "text-amber-500" : "text-gray-400"}`}>
                  {form.description.length}/500
                </span>
              </div>
              <div className="relative">
                <textarea value={form.description} onChange={e => {
                  if (e.target.value.length <= 500) setForm({ ...form, description: e.target.value });
                }} required rows="4" placeholder={t("complaint.write_description")} maxLength={500}
                  className="w-full px-4 py-2.5 pr-11 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition resize-none" />
                {!!(window.SpeechRecognition || window.webkitSpeechRecognition) && (
                  <button type="button" onClick={handleVoiceInput}
                    className={`absolute bottom-2.5 right-2.5 w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                      isListening ? "bg-red-500 text-white animate-pulse" : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                    }`}>
                    {isListening ? <MicOff size={15} /> : <Mic size={15} />}
                  </button>
                )}
              </div>
              <div className="mt-1.5 h-1 bg-gray-100 rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-200 ${form.description.length > 450 ? "bg-amber-400" : "bg-primary-500"}`}
                  style={{ width: `${(form.description.length / 500) * 100}%` }} />
              </div>
            </div>

            {/* Photo upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                {t("complaint.photos")}
                <span className="text-xs text-gray-400 ml-2">({t("complaint.photos_max", { count: 5 })})</span>
              </label>
              <div onClick={() => fileRef.current?.click()}
                className="relative border-2 border-dashed border-gray-200 rounded-xl p-6 text-center cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/30 transition-all duration-200 group">
                <input ref={fileRef} type="file" multiple accept="image/*" className="hidden"
                  onChange={e => handleImages(e.target.files)} />
                {imagePreviews.length > 0 ? (
                  <div className="flex flex-wrap gap-2 justify-center">
                    {imagePreviews.map((url, i) => (
                      <div key={i} className="relative w-20 h-20 rounded-lg overflow-hidden border border-gray-200 group/img">
                        <img src={url} alt="" className="w-full h-full object-cover" />
                        <button type="button" onClick={e => { e.stopPropagation(); removeImage(i); }}
                          className="absolute top-0.5 right-0.5 w-5 h-5 bg-black/50 text-white rounded-full flex items-center justify-center text-xs opacity-0 group-hover/img:opacity-100 transition">
                          ×
                        </button>
                      </div>
                    ))}
                    {imagePreviews.length < 5 && (
                      <div className="w-20 h-20 rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center hover:border-indigo-400 transition">
                        <Camera size={24} className="text-gray-400" />
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-1.5">
                    <Camera size={32} className="text-gray-300" />
                    <p className="text-sm text-gray-500">{t("complaint.drag_drop_photos")}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Location card */}
            <div className="ds-card p-3.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
                    location ? "bg-green-100 text-green-600" : "bg-gray-100 text-gray-400"
                  }`}>
                    <MapPin size={18} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      {location ? t("complaint.location_detected") : t("complaint.location_missing")}
                    </p>
                    {location ? (
                      <p className="text-xs text-gray-400">{location.lat.toFixed(4)}, {location.lng.toFixed(4)}</p>
                    ) : (
                      <p className="text-xs text-gray-400">{t("complaint.gps_attached")}</p>
                    )}
                  </div>
                  {location && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">{t("complaint.gps_found")}</span>
                  )}
                </div>
                <button type="button" onClick={detectLocation}
                  className="text-xs px-3 py-1.5 bg-white border border-gray-200 rounded-lg hover:border-indigo-400 hover:text-indigo-600 transition flex items-center gap-1.5 flex-shrink-0">
                  <MapPin size={12} />
                  {t("complaint.locate_again")}
                </button>
              </div>
            </div>

            {/* SLA preview */}
            <div className="flex items-center gap-2 text-xs text-gray-500 px-1">
              <Clock size={13} className="text-amber-500 flex-shrink-0" />
              <span>{t("complaint.expected_within", { days: getSLADays() })}</span>
            </div>

            <div className="flex justify-end pt-2">
              <button type="submit" disabled={loading}
                className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-700 text-white font-semibold rounded-xl hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 flex items-center gap-2 disabled:opacity-60">
                {loading && <Loader2 size={16} className="animate-spin" />}
                {loading ? t("complaint.submitting") : t("complaint.submit")}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Step 4: Success */}
      {step === 4 && result && (
        <div className="animate-scale-in text-center">
          <div className="mb-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center mx-auto shadow-lg shadow-green-200">
              <CheckCircle2 size={40} className="text-white" />
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 max-w-md mx-auto mb-6">
            {result.type === "suggestion" ? (
              <>
                <h2 className="text-2xl font-bold text-gray-900 mb-1">{t("complaint.suggestion_submitted")}</h2>
                <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-amber-50 text-amber-700 rounded-full text-sm font-medium mt-3 mb-2">
                  💡 #{result.suggestion_id}
                </div>
                <p className="text-sm text-gray-500 mt-3">{t("complaint.thank_you")}</p>
              </>
            ) : (
              <>
                <div className="flex items-center justify-center gap-2 mb-1">
                  <span className="text-3xl">🎉</span>
                  <h2 className="text-2xl font-bold text-gray-900">{t("complaint.complaint_submitted")}</h2>
                </div>

                {/* Click-to-copy complaint ID */}
                <button onClick={() => handleCopyId(result.complaint_id)}
                  className="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-50 text-indigo-700 rounded-full text-sm font-mono font-semibold mt-3 mb-4 hover:bg-indigo-100 transition cursor-pointer">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                  {result.complaint_id}
                  {copied ? <Check size={14} className="text-green-600" /> : <Copy size={14} />}
                </button>

                {/* AI classification card */}
                {result.ai_classification && (
                  <div className="ds-card p-4 mb-4 text-left">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">{t("complaint.ai_classification")}</p>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm font-semibold text-purple-700">{result.ai_classification.category}</span>
                      <span className="text-sm font-bold text-gray-700">{Math.round(result.ai_classification.confidence * 100)}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full transition-all duration-700"
                        style={{ width: `${Math.round(result.ai_classification.confidence * 100)}%` }} />
                    </div>
                    <p className="text-xs text-gray-400 mt-1.5">{t("complaint.confidence_score")}</p>
                  </div>
                )}

                <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                  <Clock size={15} className="text-gray-400" />
                  {t("complaint.sla_deadline")}: <strong className="ml-0.5">{new Date(result.sla_deadline).toLocaleDateString()}</strong>
                </div>
              </>
            )}
          </div>

          <div className="flex flex-col sm:flex-row justify-center gap-3">
            <button onClick={() => navigate("/")}
              className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-700 text-white font-semibold rounded-xl hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200">
              {t("complaint.go_to_dashboard")}
            </button>
            <button onClick={resetForm}
              className="px-6 py-2.5 border border-gray-200 text-gray-700 font-medium rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all duration-200">
              {t("complaint.submit_another")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
