// frontend/js/core/auth.js

import { api, clearSession } from "./api.js";

export function isLoggedIn() {
  return !!localStorage.getItem("access_token");
}

export function getCurrentUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

export async function login(username, password) {
  const data = await api.post("/auth/login/", { username, password }, { skipAuthRefresh: true });

  localStorage.setItem("access_token", data.access);
  localStorage.setItem("refresh_token", data.refresh);
  localStorage.setItem("user", JSON.stringify(data.user));

  return data.user;
}

export async function register(payload) {
  return api.post("/auth/register/", payload, { skipAuthRefresh: true });
}

// New OTP-based registration flow
export async function registerInit(payload) {
  return api.post("/auth/register/init/", payload, { skipAuthRefresh: true });
}

export async function verifyOTP(email, otpCode) {
  return api.post("/auth/register/verify/", { email, otp_code: otpCode }, { skipAuthRefresh: true });
}

export async function resendOTP(email) {
  return api.post("/auth/register/resend/", { email }, { skipAuthRefresh: true });
}

export function logout() {
  clearSession();
  window.location.hash = "/login";
}