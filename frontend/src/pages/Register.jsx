import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { authAPI, gisAPI } from "../api";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { MAP_STYLE } from "../mapStyle";

export default function Register({ onLogin }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const token = localStorage.getItem("auth_token") || "";
  const [form, setForm] = useState({ full_name: "", pin_code: "", address: "", latitude: null, longitude: null, ward_id: null });
  const mobile = token.replace("dev-user-", "");
  const [areaInfo, setAreaInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [wardsByPin, setWardsByPin] = useState([]);
  const [selectedWardByPin, setSelectedWardByPin] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debounceTimer = useRef(null);
  const mapContainer = useRef(null);
  const map = useRef(null);
  const marker = useRef(null);

  useEffect(() => {
    if (form.pin_code.length === 6) {
      gisAPI.pincodeLookup({ pin_code: form.pin_code }).then(res => {
        setWardsByPin(res.data.wards || []);
        setSelectedWardByPin("");
      }).catch(() => setWardsByPin([]));
    } else {
      setWardsByPin([]);
      setSelectedWardByPin("");
    }
  }, [form.pin_code]);

  useEffect(() => {
    if (map.current || !mapContainer.current) return;
    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: MAP_STYLE,
      center: [73.8567, 18.5204],
      zoom: 11
    });
    map.current.addControl(new maplibregl.NavigationControl(), "top-left");
    map.current.on("click", handleMapClick);
    return () => {
      if (map.current) {
        map.current.off("click", handleMapClick);
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  function placeMarker(lng, lat) {
    if (marker.current) marker.current.remove();
    marker.current = new maplibregl.Marker({ color: "#ef4444", draggable: true })
      .setLngLat([lng, lat])
      .addTo(map.current);
    marker.current.on("dragend", handleMarkerDragEnd);
  }

  async function handleMarkerDragEnd() {
    if (!marker.current) return;
    const { lng, lat } = marker.current.getLngLat();
    setForm(f => ({ ...f, latitude: lat, longitude: lng }));
    try {
      const res = await gisAPI.locate({ latitude: lat, longitude: lng });
      setAreaInfo(res.data);
      setForm(f => ({ ...f, ward_id: res.data.id }));
    } catch { setAreaInfo(null); }
    try {
      const geo = await gisAPI.reverseGeocode({ lat, lng });
      if (geo.data?.display_name) setForm(f => ({ ...f, address: geo.data.display_name }));
      if (geo.data?.address?.postcode) setForm(f => ({ ...f, pin_code: geo.data.address.postcode }));
    } catch {}
  }

  async function handleMapClick(e) {
    const { lng, lat } = e.lngLat;
    setForm(f => ({ ...f, latitude: lat, longitude: lng }));
    placeMarker(lng, lat);
    try {
      const res = await gisAPI.locate({ latitude: lat, longitude: lng });
      setAreaInfo(res.data);
      setForm(f => ({ ...f, ward_id: res.data.id }));
    } catch { setAreaInfo(null); }
    try {
      const geo = await gisAPI.reverseGeocode({ lat, lng });
      if (geo.data?.display_name) setForm(f => ({ ...f, address: geo.data.display_name }));
      if (geo.data?.address?.postcode) setForm(f => ({ ...f, pin_code: geo.data.address.postcode }));
    } catch {}
  }

  function handleWardByPinChange(wardId) {
    if (!wardId) {
      setSelectedWardByPin("");
      setForm(f => ({ ...f, ward_id: null }));
      setAreaInfo(null);
      return;
    }
    const ward = wardsByPin.find(w => String(w.id) === wardId);
    if (ward) {
      setSelectedWardByPin(wardId);
      setForm(f => ({ ...f, ward_id: ward.id, latitude: null, longitude: null }));
      setAreaInfo({ id: ward.id, ward_number: ward.ward_number, ward_name: ward.ward_name });
    }
  }

  function handleAddressInput(value) {
    setForm(f => ({ ...f, address: value }));
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    if (value.length < 3) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    debounceTimer.current = setTimeout(async () => {
      try {
        const res = await gisAPI.autocomplete(value);
        setSuggestions(res.data.suggestions || []);
        setShowSuggestions(true);
      } catch {
        setSuggestions([]);
      }
    }, 300);
  }

  function selectSuggestion(s) {
    setForm(f => ({ ...f, address: s.full, latitude: s.lat, longitude: s.lng, ward_id: null }));
    setShowSuggestions(false);
    setSelectedLocality("");
    gisAPI.locate({ latitude: s.lat, longitude: s.lng }).then(res => {
      setAreaInfo(res.data);
      setForm(f => ({ ...f, ward_id: res.data.id }));
      placeMarker(s.lng, s.lat);
      if (map.current) map.current.flyTo({ center: [s.lng, s.lat], zoom: 14 });
    }).catch(() => setAreaInfo(null));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (localities.length > 0 && !form.ward_id && !form.latitude) {
      alert("Select a locality or click on the map to set your location");
      return;
    }
    setLoading(true);
    try {
      const res = await authAPI.register({ ...form, firebase_uid: token, mobile });
      setAreaInfo(res.data.ward);
      const profile = await authAPI.profile();
      onLogin({ ...profile.data, token });
      navigate("/");
    } catch (err) {
      alert(t("auth.registration_error") + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  }

  async function detectLocation() {
    if (!navigator.geolocation) return alert(t("auth.gps_not_available"));
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const { latitude, longitude } = pos.coords;
      placeMarker(longitude, latitude);
      setForm(f => ({ ...f, latitude, longitude }));
      try {
        const res = await gisAPI.locate({ latitude, longitude });
        setAreaInfo(res.data);
        setForm(f => ({ ...f, ward_id: res.data.id }));
      } catch { alert(t("auth.location_error")); }
      try {
        const geo = await gisAPI.reverseGeocode({ lat: latitude, lng: longitude });
        if (geo.data?.display_name) setForm(f => ({ ...f, address: geo.data.display_name }));
        if (geo.data?.address?.postcode) setForm(f => ({ ...f, pin_code: geo.data.address.postcode }));
      } catch {}
      if (map.current) map.current.flyTo({ center: [longitude, latitude], zoom: 14 });
    }, () => alert(t("auth.location_error")));
  }

  if (!token) {
    return (
      <div className="ds-card max-w-md mx-auto mt-16 p-8">
        <h2 className="text-2xl font-bold text-center text-indigo-700 mb-6">{t("auth.register")}</h2>
        <p className="text-center text-gray-500">{t("auth.please_login_first")}</p>
        <button onClick={() => navigate("/login")} className="w-full mt-4 bg-primary-600 text-white py-2 rounded-xl hover:bg-primary-700 transition-colors">{t("auth.login")}</button>
      </div>
    );
  }

  return (
    <div className="ds-card max-w-lg mx-auto mt-8 p-8">
      <h2 className="text-2xl font-bold text-indigo-700 mb-6">{t("auth.register")}</h2>
      <form onSubmit={handleSubmit}>
        <p className="text-sm text-gray-500 mb-4">{t("auth.mobile")}: <strong>{mobile}</strong></p>
        <label className="block text-sm font-medium text-gray-700 mb-1">{t("auth.full_name")}</label>
        <input type="text" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required className="w-full px-4 py-2 border border-gray-300 rounded-xl mb-4 focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition" />

        <label className="block text-sm font-medium text-gray-700 mb-1">{t("auth.pin_code")}</label>
        <input type="text" value={form.pin_code} onChange={(e) => setForm({ ...form, pin_code: e.target.value })} placeholder="411038" maxLength={6} className="w-full px-4 py-2 border border-gray-300 rounded-xl mb-1 focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition" />
        <p className="text-[11px] text-amber-600 mb-3">GPS may auto-fill this — verify it matches your actual PIN code.</p>

        {wardsByPin.length > 0 && (
          <>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select Your Ward</label>
            <select value={selectedWardByPin} onChange={(e) => handleWardByPinChange(e.target.value)} className="w-full px-4 py-2 border border-gray-300 rounded-xl mb-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition">
              <option value="">— Choose your ward —</option>
              {wardsByPin.map(w => (
                <option key={w.id} value={w.id}>Ward {w.ward_number} — {w.ward_name}</option>
              ))}
            </select>
          </>
        )}
        {form.pin_code.length === 6 && wardsByPin.length === 0 && (
          <p className="text-xs text-amber-600 mb-4">No wards found for this PIN code. Use the map below to set your location.</p>
        )}

        <label className="block text-sm font-medium text-gray-700 mb-1">{t("auth.address")}</label>
        <div className="relative mb-4">
          <input type="text" value={form.address}
            onChange={(e) => handleAddressInput(e.target.value)}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder={t("auth.address_hint")}
            className="w-full px-4 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 transition" />
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg mt-1 shadow-lg max-h-48 overflow-y-auto">
              {suggestions.map((s, i) => (
                <div key={i} onMouseDown={() => selectSuggestion(s)}
                  className="px-4 py-2 text-sm hover:bg-indigo-50 cursor-pointer border-b border-gray-100 last:border-b-0">
                  <p className="font-medium">{s.name}</p>
                  <p className="text-xs text-gray-500">{s.address}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div ref={mapContainer} className="w-full h-56 rounded-xl overflow-hidden border border-gray-200 mb-4" />

        <button type="button" onClick={detectLocation} className="w-full mb-4 bg-emerald-600 text-white py-2 rounded-xl hover:bg-emerald-700 transition-colors text-sm">{t("auth.detect_location")}</button>
        <button type="submit" disabled={loading} className="w-full bg-primary-600 text-white py-2 rounded-xl hover:bg-primary-700 transition-colors font-medium disabled:opacity-60">{loading ? t("auth.saving") : t("area.confirm")}</button>
      </form>

      {areaInfo && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-xl">
          <h3 className="font-semibold text-green-800">{t("area.your_area")}</h3>
          <p className="text-sm mt-1"><strong>{t("area.ward")}:</strong> {areaInfo.ward_name} (#{areaInfo.ward_number})</p>
          {areaInfo.corporators?.map((c, i) => c.name ? (
            <p key={i} className="text-sm"><strong>{t("area.corporator")} {c.label}:</strong> {c.name}{c.party ? ` (${c.party})` : ""}</p>
          ) : null)}
          {areaInfo.mla && <p className="text-sm"><strong>{t("area.mla")}:</strong> {areaInfo.mla.name} ({areaInfo.mla.constituency})</p>}
          {areaInfo.mp && <p className="text-sm"><strong>{t("area.mp")}:</strong> {areaInfo.mp.name} ({areaInfo.mp.constituency})</p>}
        </div>
      )}
    </div>
  );
}
