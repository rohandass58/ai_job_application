// frontend/js/services/authService.js

import { getCurrentUser, login, logout, register } from "../core/auth.js";
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

  logout() {
    store.set("user", null);
    logout();
  },

  currentUser() {
    return store.get("user") || getCurrentUser();
  },
};