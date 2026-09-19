// frontend/js/core/auth.js

import { apiRequest } from "./api.js";
import { showToast } from "./toast.js";

export function isLoggedIn() {
  return !!localStorage.getItem("access_token");
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
  window.location.reload();
}

export async function login(username, password) {
  const data = await apiRequest("/auth/login/", {
    method: "POST",
    body: { username, password },
  });

  localStorage.setItem("access_token", data.access);
  localStorage.setItem("refresh_token", data.refresh);
  if (data.user) {
    localStorage.setItem("user", JSON.stringify(data.user));
  }

  return data;
}

export async function register(formData) {
  return apiRequest("/auth/register/", {
    method: "POST",
    body: formData,
  });
}

export function getCurrentUser() {
  const user = localStorage.getItem("user");
  return user ? JSON.parse(user) : null;
}