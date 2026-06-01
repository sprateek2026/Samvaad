import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});

// Backend serves uploaded files (photos, complaint images) from its root,
// NOT under /api — strip the /api suffix to build absolute asset URLs.
const FILE_BASE_URL = API_URL.replace(/\/api\/?$/, "");

export function assetUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  return `${FILE_BASE_URL}/${path.replace(/^\//, "")}`;
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (axios.isCancel(error)) return Promise.reject(error);
    if (error.code === "ECONNABORTED") {
      console.warn("[API] Request timed out:", error.config?.url);
    } else if (!error.response) {
      console.warn("[API] Network error — backend may be starting up:", error.config?.url);
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post("/auth/register", data),
  profile: (signal) => api.get("/auth/profile", { signal }),
  updateProfile: (data) => api.patch("/auth/profile", data),
};

export const categoryAPI = {
  list: () => api.get("/categories"),
  subCategories: (id) => api.get(`/categories/${id}/sub`),
};

export const suggestionAPI = {
  create: (data) => api.post("/suggestions", data),
  list: (params) => api.get("/suggestions", { params }),
};

export const complaintAPI = {
  create: (formData) => api.post("/complaints", formData, { headers: { "Content-Type": "multipart/form-data" } }),
  list: (params) => api.get("/complaints", { params }),
  get: (id) => api.get(`/complaints/${id}`),
  updateStatus: (id, data) => api.patch(`/complaints/${id}/status`, data),
  rate: (id, rating) => api.post(`/complaints/${id}/rate`, { rating }),
};

export const dashboardAPI = {
  citizenStats: () => api.get("/dashboard/citizen/stats"),
  corporatorStats: () => api.get("/dashboard/corporator/stats"),
  corporatorComplaints: (params) => api.get("/dashboard/corporator/complaints", { params }),
  notifications: () => api.get("/dashboard/notifications"),
};

export const gisAPI = {
  locate: (data) => api.post("/gis/locate", data),
  pincodeLookup: (data) => api.post("/gis/pincode-lookup", data),
  localities: (pinCode) => api.get(`/gis/localities?pin_code=${pinCode}`),
  autocomplete: (q) => api.get("/gis/autocomplete", { params: { q } }),
  reverseGeocode: (params) => api.get("/gis/reverse-geocode", { params }),
  wards: () => api.get("/gis/wards"),
};

export const adminAPI = {
  createUser: (data) => api.post("/admin/users", data),
  complaints: (params) => api.get("/admin/complaints", { params }),
  analytics: () => api.get("/admin/analytics/overview"),
  dashboard: (params) => api.get("/admin/dashboard", { params, timeout: 30000 }),
  listReps: (params) => api.get("/admin/representatives", { params }),
  createRep: (formData) => api.post("/admin/representatives", formData, { headers: { "Content-Type": "multipart/form-data" } }),
  updateRep: (id, formData) => api.put(`/admin/representatives/${id}`, formData, { headers: { "Content-Type": "multipart/form-data" } }),
  deleteRep: (id) => api.delete(`/admin/representatives/${id}`),
  repKyc: (id) => api.get(`/admin/representatives/${id}/kyc`),
};

export default api;
