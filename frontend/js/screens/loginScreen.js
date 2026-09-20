// frontend/js/screens/loginScreen.js

import { navigate } from "../core/router.js";
import { showToast } from "../core/toast.js";
import { authService } from "../services/authService.js";
import { $, mount, setLoading } from "../utils/dom.js";

export function loginScreen() {
  mount(`
    <div class="auth-wrap">
      <h1 class="auth-title">JobApply AI</h1>
      <p class="auth-sub">Apply smarter with AI</p>

      <form class="card" id="loginForm" novalidate>
        <div class="form-group">
          <label for="username">Username</label>
          <input type="text" id="username" name="username"
                 autocomplete="username" placeholder="Enter username" required />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" name="password"
                 autocomplete="current-password" placeholder="Enter password" required />
        </div>

        <button type="submit" class="btn btn-primary" id="loginBtn">Login</button>

        <p class="auth-switch">
          Don't have an account? <a href="#/register">Register</a>
        </p>
      </form>
    </div>
  `);

  $("#loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = $("#username").value.trim();
    const password = $("#password").value;

    if (!username || !password) {
      showToast("Enter username and password", "error");
      return;
    }

    const restore = setLoading($("#loginBtn"), "Logging in...");
    try {
      await authService.login(username, password);
      showToast("Welcome back!", "success");
      navigate("/home");
    } catch (err) {
      showToast(err.message || "Login failed", "error");
      restore();
    }
  });
}