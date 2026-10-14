// frontend/js/services/authService.js

import { getCurrentUser, login, logout, register, registerInit, verifyOTP, resendOTP } from "../core/auth.js";
import { store } from "../core/store.js";

export const authService = {
  async login(username, password) {
    const user = await login(username, password);
    store.set("user", user);
    return user;
  },

  async register(payload) {
    return register(payload);
  },

  // New OTP-based registration flow
  async registerInit(payload) {
    return registerInit(payload);
  },

  async verifyOTP(email, otpCode) {
    const data = await verifyOTP(email, otpCode);
    // Store tokens and user data for auto-login
    store.set("user", data.user);
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    return data;
  },

  async resendOTP(email) {
    return resendOTP(email);
  },

  logout() {
    store.set("user", null);
    logout();
  },

  currentUser() {
    return store.get("user") || getCurrentUser();
  },
};