// frontend/js/core/api.js

// Replace with your real Railway domain (Settings -> Networking). Keep https:// and /api, no trailing slash.
const PROD_API = "https://xxxx.up.railway.app/api";

const API_BASE = ["localhost", "127.0.0.1"].includes(window.location.hostname)
  ? "http://localhost:8000/api"
  : PROD_API;

const TOKEN_KEYS = {
  access: "access_token",
  refresh: "refresh_token",
  user: "user",
};

export function clearSession() {
  Object.values(TOKEN_KEYS).forEach((k) => localStorage.removeItem(k));
}

// ---- Token refresh (single-flight) ----
let refreshPromise = null;

async function refreshAccessToken() {
  // If a refresh is already running, reuse it (avoids parallel refresh calls,
  // which would break with ROTATE_REFRESH_TOKENS + blacklist)
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const refresh = localStorage.getItem(TOKEN_KEYS.refresh);
    if (!refresh) throw new Error("No refresh token");

    const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });

    const json = await res.json().catch(() => null);
    if (!res.ok || !json?.success) throw new Error("Refresh failed");

    localStorage.setItem(TOKEN_KEYS.access, json.data.access);
    // ROTATE_REFRESH_TOKENS=True -> server sends a new refresh token too
    if (json.data.refresh) {
      localStorage.setItem(TOKEN_KEYS.refresh, json.data.refresh);
    }
    return json.data.access;
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

// ---- Core request ----
async function rawRequest(endpoint, options, token) {
  const isForm = options.body instanceof FormData;

  const headers = {
    ...(isForm ? {} : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const config = { ...options, headers };
  if (options.body && !isForm) {
    config.body = JSON.stringify(options.body);
  }

  return fetch(`${API_BASE}${endpoint}`, config);
}

function makeError(message, status, errors = null) {
  const error = new Error(message);
  error.status = status;
  error.errors = errors;
  return error;
}

export async function apiRequest(endpoint, options = {}) {
  let token = localStorage.getItem(TOKEN_KEYS.access);
  let response;

  try {
    response = await rawRequest(endpoint, options, token);

    // Access token expired -> refresh once and retry
    if (response.status === 401 && !options.skipAuthRefresh) {
      try {
        token = await refreshAccessToken();
        response = await rawRequest(endpoint, options, token);
      } catch {
        clearSession();
        window.location.hash = "/login";
        throw makeError("Session expired. Please login again.", 401);
      }
    }
  } catch (err) {
    if (err.status) throw err; // already a formatted error
    throw makeError("Cannot reach server. Check your connection.", 0);
  }

  const json = await response.json().catch(() => null);

  if (!json) {
    throw makeError("Unexpected server response", response.status);
  }

  if (!response.ok || json.success === false) {
    throw makeError(json.message || "Something went wrong", response.status, json.errors);
  }

  return json; // { success, message, data, errors }
}

// Convenience helpers -> return json.data directly
export const api = {
  request: (method, url, body, opts) =>
    apiRequest(url, { ...opts, method, ...(body ? { body } : {}) }).then((r) => r.data),
  get: (url, opts) => apiRequest(url, { ...opts, method: "GET" }).then((r) => r.data),
  post: (url, body, opts) => apiRequest(url, { ...opts, method: "POST", body }).then((r) => r.data),
  patch: (url, body, opts) => apiRequest(url, { ...opts, method: "PATCH", body }).then((r) => r.data),
  upload: (url, formData, opts) => apiRequest(url, { ...opts, method: "POST", body: formData }).then((r) => r.data),
};