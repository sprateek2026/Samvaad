import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import i18n from "./i18n";
import { authAPI } from "./api";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CitizenDashboard from "./pages/CitizenDashboard";
import RaiseComplaint from "./pages/RaiseComplaint";
import CorporatorDashboard from "./pages/CorporatorDashboard";
import ComplaintDetail from "./pages/ComplaintDetail";
import ComplaintListPage from "./pages/ComplaintListPage";
import AdminPage from "./pages/Admin";
import "./index.css";

function readCachedUser() {
  try {
    const token = localStorage.getItem("auth_token");
    if (!token) return null;
    const raw = localStorage.getItem("auth_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export default function App() {
  // Restore user instantly from localStorage — no API wait, no flash
  const [user, setUser] = useState(readCachedUser);
  // authReady gates the spinner only for the case where a token exists
  // but there is no cached user yet (very first login on a new device/browser)
  const [authReady, setAuthReady] = useState(!!readCachedUser() || !localStorage.getItem("auth_token"));

  useEffect(() => {
    const controller = new AbortController();
    // Safety net: if the profile API never responds, unblock the UI after 6 s
    // rather than leaving the spinner up indefinitely (e.g. backend cold start).
    const safetyTimer = setTimeout(() => {
      if (!controller.signal.aborted) setAuthReady(true);
    }, 6000);

    const token = localStorage.getItem("auth_token");
    if (!token) {
      localStorage.removeItem("auth_user");
      setUser(null);
      setAuthReady(true);
      clearTimeout(safetyTimer);
      return () => controller.abort();
    }

    authAPI.profile(controller.signal)
      .then(res => {
        if (controller.signal.aborted) return;
        const userData = { ...res.data, token };
        localStorage.setItem("auth_user", JSON.stringify(userData));
        setUser(userData);
      })
      .catch(() => {
        // Any failure (network error, timeout, 4xx/5xx): keep the cached session.
        // Explicit logout via handleLogout() is the only path to clearing state.
      })
      .finally(() => {
        clearTimeout(safetyTimer);
        if (!controller.signal.aborted) setAuthReady(true);
      });

    return () => {
      controller.abort();
      clearTimeout(safetyTimer);
    };
  }, []);

  function saveUser(userData) {
    localStorage.setItem("auth_user", JSON.stringify(userData));
    setUser(userData);
  }

  function handleLogin(data) {
    if (typeof data === "string") {
      // Legacy path: token string passed directly (not used by current Login.jsx)
      localStorage.setItem("auth_token", data);
      authAPI.profile()
        .then(res => saveUser({ ...res.data, token: data }))
        .catch(() => {});
    } else {
      // Normal path: full user object from Login.jsx / Register.jsx
      const token = data.token || localStorage.getItem("auth_token");
      saveUser({ ...data, token });
    }
  }

  function handleLogout() {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
    setUser(null);
  }

  // Spinner only when we have a token but haven't resolved yet (no cache)
  if (!authReady) {
    return (
      <I18nextProvider i18n={i18n}>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-700" />
        </div>
      </I18nextProvider>
    );
  }

  return (
    <I18nextProvider i18n={i18n}>
      <Router>
        <Layout user={user} onLogout={handleLogout}>
          <Routes>
            <Route path="/" element={
              user ? (
                user.role === "corporator" ? <CorporatorDashboard user={user} /> :
                user.role === "admin"      ? <AdminPage user={user} /> :
                                             <CitizenDashboard user={user} onUserUpdate={saveUser} />
              ) : <Login onLogin={handleLogin} />
            } />
            <Route path="/login"       element={<Login onLogin={handleLogin} />} />
            <Route path="/register"    element={<Register onLogin={handleLogin} />} />
            <Route path="/raise"       element={user ? <RaiseComplaint user={user} /> : <Navigate to="/login" replace />} />
            <Route path="/complaint/:id" element={user ? <ComplaintDetail user={user} /> : <Navigate to="/login" replace />} />
            <Route path="/complaints"  element={user ? <ComplaintListPage user={user} /> : <Navigate to="/login" replace />} />
            <Route path="/corporator"  element={
              user?.role === "corporator" ? <CorporatorDashboard user={user} /> :
              user ? <Navigate to="/" replace /> :
              <Navigate to="/login" replace />
            } />
            <Route path="/admin"       element={
              user?.role === "admin" ? <AdminPage user={user} /> :
              user ? <Navigate to="/" replace /> :
              <Navigate to="/login" replace />
            } />
          </Routes>
        </Layout>
      </Router>
    </I18nextProvider>
  );
}
