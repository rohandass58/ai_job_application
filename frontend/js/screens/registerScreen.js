// frontend/js/screens/registerScreen.js

import { navigate } from "../core/router.js";
import { showToast } from "../core/toast.js";
import { authService } from "../services/authService.js";
import { $, $$, esc, mount, setLoading } from "../utils/dom.js";

const FIELDS = ["username", "email", "password", "password2"];

function showFieldErrors(errors) {
  $$(".field-error").forEach((el) => el.remove());
  if (!errors || typeof errors !== "object") return;

  FIELDS.forEach((field) => {
    const messages = errors[field];
    if (!messages) return;

    const input = $(`#reg-${field}`);
    const text = Array.isArray(messages) ? messages.join(" ") : String(messages);
    input.insertAdjacentHTML("afterend", `<div class="field-error">${esc(text)}</div>`);
  });
}

export function registerScreen() {
  mount(`
    <div class="auth-wrap">
      <h1 class="auth-title">Create Account</h1>
      <p class="auth-sub">Start applying in minutes</p>

      <form class="card" id="registerForm" novalidate>
        <div class="form-group">
          <label for="reg-username">Username</label>
          <input type="text" id="reg-username" autocomplete="username" required />
        </div>

        <div class="form-group">
          <label for="reg-email">Email</label>
          <input type="email" id="reg-email" autocomplete="email" required />
        </div>

        <div class="form-group">
          <label for="reg-password">Password</label>
          <input type="password" id="reg-password" autocomplete="new-password" required />
        </div>

        <div class="form-group">
          <label for="reg-password2">Confirm Password</label>
          <input type="password" id="reg-password2" autocomplete="new-password" required />
        </div>

        <button type="submit" class="btn btn-primary" id="registerBtn">Register</button>

        <p class="auth-switch">
          Already have an account? <a href="#/login">Login</a>
        </p>
      </form>
    </div>
  `);

  $("#registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    showFieldErrors(null);

    const payload = {
      username: $("#reg-username").value.trim(),
      email: $("#reg-email").value.trim(),
      password: $("#reg-password").value,
      password2: $("#reg-password2").value,
    };

    if (payload.password !== payload.password2) {
      showFieldErrors({ password2: "Passwords do not match" });
      return;
    }

    const restore = setLoading($("#registerBtn"), "Creating account...");
    try {
      await authService.register(payload);
      // Auto-login so user lands directly on home
      await authService.login(payload.username, payload.password);
      showToast("Account created!", "success");
      navigate("/home");
    } catch (err) {
      showFieldErrors(err.errors);
      showToast(err.message || "Registration failed", "error");
      restore();
    }
  });
}