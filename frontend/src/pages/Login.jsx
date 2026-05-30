import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Megaphone } from "lucide-react";
import { authAPI } from "../api";

function ShivajiIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="16.5" width="18" height="2.5" rx="1.25" />
      <path d="M5 16.5V12L7 8.5l2 3.5v4.5" />
      <path d="M9 16.5V10.5L12 5l3 5.5v5" />
      <path d="M15 16.5V12l2-3.5 2 3.5v4.5" />
      <circle cx="12" cy="9.5" r="1" />
    </svg>
  );
}

export default function Login({ onLogin }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [mobile, setMobile] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState("mobile");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState("");
  const [showOtp, setShowOtp] = useState(false);

  function handleSendOtp(e) {
    e.preventDefault();
    if (!selectedRole) { setError(t("auth.select_role")); return; }
    if (!/^\d{10}$/.test(mobile)) { setError(t("auth.invalid_mobile")); return; }
    setError("");
    setStep("otp");
  }

  async function handleVerifyOtp(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const token = `dev-user-${mobile}`;
    localStorage.setItem("auth_token", token);
    try {
      const res = await authAPI.profile();
      onLogin({ ...res.data, token });
      navigate(res.data.role === "corporator" ? "/corporator" : res.data.role === "admin" ? "/admin" : "/");
    } catch {
      setLoading(false);
      navigate("/register");
    }
  }

  const otpFilled = otp.length === 6;

  return (
    <div className="flex min-h-screen">

      {/* ── Left branding panel ── */}
      <div className="hidden md:flex flex-none w-[45%] relative flex-col p-10"
        style={{ background: "linear-gradient(160deg, #0d1b35 0%, #102a5c 22%, #1a4a8a 42%, #6b2206 64%, #c24a0a 80%, #e8760e 92%, #f5a31a 100%)" }}>
        <div className="absolute inset-0 bg-black/[.18]" />

        <div className="relative z-10 flex flex-col h-full">
          {/* Government badge */}
          <div className="flex items-center gap-2.5 mb-11">
            <div className="w-9 h-9 bg-saffron-500 rounded-full flex items-center justify-center flex-shrink-0">
              <ShivajiIcon size={20} />
            </div>
            <div>
              <div className="text-white/[.55] text-[0.62rem] uppercase tracking-[0.08em]">Government of</div>
              <div className="text-white text-[0.78rem] font-semibold">Maharashtra</div>
            </div>
          </div>

          {/* Samvaad title */}
          <div className="mb-5">
            <div className="inline-flex items-center gap-2.5 bg-saffron-500/10 border border-saffron-500/30 rounded-xl px-4 py-3 mb-3">
              <Megaphone className="w-7 h-7 text-white" />
              <h1 className="text-white text-[2.75rem] font-bold leading-none tracking-tight">Samvaad</h1>
            </div>
            <p className="text-white/60 text-sm tracking-[0.15em] uppercase">Smart Governance Portal</p>
          </div>

          <p className="text-white/[.65] text-sm leading-relaxed mb-auto max-w-[300px]">
            A unified digital platform connecting citizens and government for faster, transparent, and accountable governance across Maharashtra.
          </p>

          {/* Feature bullets */}
          <div className="flex flex-col gap-3.5">
            {[
              { icon: "⚡", text: "Real-time grievance tracking" },
              { icon: "🔒", text: "Secure OTP-based authentication" },
              { icon: "📋", text: "Integrated with e-governance services" },
            ].map(({ icon, text }) => (
              <div key={text} className="flex items-center gap-3">
                <div className="w-[30px] h-[30px] flex-shrink-0 bg-saffron-500/10 border border-saffron-500/30 rounded-[7px] flex items-center justify-center text-sm">
                  {icon}
                </div>
                <span className="text-white/[.78] text-sm">{text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right form panel ── */}
      <div className="flex-1 bg-white flex flex-col items-center justify-center px-8 py-12">
        <div className="animate-login-card w-full max-w-[400px]">
          <h2 className="text-[1.7rem] font-bold text-gray-900 mb-1.5">Welcome back</h2>
          <p className="text-gray-500 text-sm mb-8">Sign in to access Maharashtra&apos;s governance services</p>

          {/* Role pill toggle */}
          <div className="mb-5">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {t("auth.login_as")} <span className="text-red-500">*</span>
            </label>
            <div className={`flex rounded-xl border p-1 bg-gray-50 gap-1 transition-all ${
              !selectedRole ? "border-saffron-400 ring-2 ring-saffron-300/40" : "border-gray-200"
            }`}>
              {["citizen","corporator","admin"].map(role => {
                const locked = step === "otp";
                const isSelected = selectedRole === role;
                return (
                  <button key={role} type="button"
                    onClick={() => { if (locked) return; setSelectedRole(role); setError(""); }}
                    disabled={locked && !isSelected}
                    className={`flex-1 py-2 px-2 rounded-lg text-xs font-semibold transition-all ${
                      isSelected
                        ? "bg-saffron-500 text-white shadow-sm"
                        : locked
                          ? "text-gray-300 cursor-not-allowed"
                          : "text-gray-600 hover:bg-gray-100"
                    }`}>
                    {locked && isSelected && <span className="mr-1">🔒</span>}
                    {role.charAt(0).toUpperCase() + role.slice(1)}
                  </button>
                );
              })}
            </div>
            {!selectedRole && (
              <p className="text-xs text-saffron-600 mt-1.5 font-medium">
                ↑ Choose your role to continue
              </p>
            )}
          </div>

          {selectedRole === "admin" && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg px-3.5 py-2.5 mb-5 text-xs text-amber-800 flex items-start gap-2">
              <span>🔒</span><span>{t("auth.admin_notice")}</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 text-red-700 rounded-lg px-3.5 py-2.5 mb-5 text-sm">{error}</div>
          )}

          {step === "mobile" ? (
            <form onSubmit={handleSendOtp}>
              <div className="mb-5">
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  {t("auth.mobile")} <span className="text-red-500">*</span>
                </label>
                <div className="flex border border-gray-300 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-primary-500/30 focus-within:border-primary-500 transition">
                  <div className="flex items-center gap-1.5 px-3 bg-gray-50 border-r border-gray-300 flex-shrink-0">
                    <span className="text-base">🇮🇳</span>
                    <span className="text-sm text-gray-700 font-medium">+91</span>
                  </div>
                  <input type="tel" value={mobile}
                    onChange={e => { setMobile(e.target.value); if (error) setError(""); }}
                    placeholder={t("auth.mobile_placeholder")} maxLength={10} required
                    className="flex-1 px-3 py-2.5 text-sm border-none outline-none bg-white" />
                </div>
              </div>

              <div className="flex items-center gap-2 mb-6">
                <input type="checkbox" id="remember" className="w-3.5 h-3.5 cursor-pointer" />
                <label htmlFor="remember" className="text-xs text-gray-500 flex-1 cursor-pointer select-none">
                  {t("auth.remember_me")}
                </label>
                <a href="#" className="text-xs text-saffron-500 font-medium"
                  onClick={e => e.preventDefault()}>{t("auth.forgot_password")}</a>
              </div>

              <button type="submit" disabled={!selectedRole}
                className="w-full py-3 bg-saffron-500 hover:bg-saffron-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm rounded-lg transition-colors tracking-wide">
                {t("auth.send_otp")}
              </button>

              {selectedRole !== "admin" && (
                <p className="text-xs text-gray-500 text-center mt-5">
                  {t("auth.register_here")}{" "}
                  <a href="/register" className="text-saffron-500 font-semibold"
                    onClick={e => { e.preventDefault(); navigate("/register"); }}>
                    {t("auth.register")} →
                  </a>
                </p>
              )}
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp}>
              <div className="mb-5">
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  {t("auth.otp")} <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type={showOtp ? "text" : "password"}
                    value={otp}
                    onChange={e => { setOtp(e.target.value.replace(/\D/g, "").slice(0, 6)); if (error) setError(""); }}
                    placeholder="••••••"
                    maxLength={6}
                    required
                    autoFocus
                    className="w-full px-4 py-2.5 pr-11 border border-gray-300 rounded-lg text-sm tracking-widest focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition"
                  />
                  <button type="button" onClick={() => setShowOtp(!showOtp)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 bg-transparent border-none cursor-pointer p-0">
                    {showOtp ? (
                      <svg width="17" height="17" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" /></svg>
                    ) : (
                      <svg width="17" height="17" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    )}
                  </button>
                </div>
              </div>

              <button type="submit" disabled={loading || !otpFilled}
                className="w-full py-3 bg-saffron-500 hover:bg-saffron-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm rounded-lg transition-colors mb-3">
                {loading ? t("auth.verifying") : t("auth.sign_in")}
              </button>

              {selectedRole !== "admin" && (
                <p className="text-xs text-gray-500 text-center mb-2">
                  {t("auth.register_here")}{" "}
                  <a href="/register" className="text-saffron-500 font-semibold"
                    onClick={e => { e.preventDefault(); navigate("/register"); }}>
                    {t("auth.register")} →
                  </a>
                </p>
              )}

              <button type="button"
                onClick={() => { setStep("mobile"); setError(""); setOtp(""); }}
                className="block w-full text-xs text-saffron-500 bg-transparent border-none cursor-pointer text-center py-1">
                ← {t("auth.back")}
              </button>
            </form>
          )}

          {/* DEV MODE notice */}
          <div className="mt-6 bg-amber-50 border border-amber-200 rounded-lg px-3.5 py-2.5 text-xs text-amber-800 flex items-center gap-2">
            <span>⚠️</span><span>{t("auth.dev_mode")}</span>
          </div>
        </div>

        <p className="mt-10 text-[0.7rem] text-gray-400 text-center">
          &copy; 2026 {t("app_name")} — {t("auth.smart_governance")} | {t("footer.all_rights", "All Rights Reserved")}
        </p>
      </div>
    </div>
  );
}
