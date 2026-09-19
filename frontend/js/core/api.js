// frontend/js/core/api.js

const API_BASE = "http://localhost:8000/api";   // change later for production

async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
  };

  if (options.body && !(options.body instanceof FormData)) {
    config.body = JSON.stringify(options.body);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config);
  const data = await response.json();

  if (!response.ok || data.success === false) {
    const error = new Error(data.message || "Something went wrong");
    error.errors = data.errors;
    error.status = response.status;
    throw error;
  }

  return data;
}

export { apiRequest };