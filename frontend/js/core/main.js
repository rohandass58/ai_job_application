// frontend/js/main.js

import { isLoggedIn } from "./core/auth.js";
import { showToast } from "./core/toast.js";

// Temporary simple screens (we will improve them next)
function renderLogin() {
  document.getElementById("app").innerHTML = `
    <div style="padding: 40px 20px;">
      <h1 style="text-align:center; margin-bottom: 8px;">JobApply AI</h1>
      <p style="text-align:center; color:#64748b; margin-bottom: 32px;">Apply smarter with AI</p>

      <div class="card">
        <div class="form-group">
          <label>Username</label>
          <input type="text" id="username" placeholder="Enter username" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" id="password" placeholder="Enter password" />
        </div>
        <button class="btn btn-primary" id="loginBtn">Login</button>
        <p style="text-align:center; margin-top: 16px; font-size: 14px;">
          Don't have an account? <a href="#" id="goRegister">Register</a>
        </p>
      </div>
    </div>
  `;

  document.getElementById("loginBtn").onclick = async () => {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    try {
      const { login } = await import("./core/auth.js");
      await login(username, password);
      showToast("Login successful!", "success");
      renderApp();
    } catch (err) {
      showToast(err.message || "Login failed", "error");
    }
  };

  document.getElementById("goRegister").onclick = (e) => {
    e.preventDefault();
    renderRegister();
  };
}

function renderRegister() {
  document.getElementById("app").innerHTML = `
    <div style="padding: 40px 20px;">
      <h1 style="text-align:center; margin-bottom: 24px;">Create Account</h1>
      <div class="card">
        <div class="form-group">
          <label>Username</label>
          <input type="text" id="reg-username" />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input type="email" id="reg-email" />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" id="reg-password" />
        </div>
        <div class="form-group">
          <label>Confirm Password</label>
          <input type="password" id="reg-password2" />
        </div>
        <button class="btn btn-primary" id="registerBtn">Register</button>
        <p style="text-align:center; margin-top: 16px; font-size: 14px;">
          Already have an account? <a href="#" id="goLogin">Login</a>
        </p>
      </div>
    </div>
  `;

  document.getElementById("registerBtn").onclick = async () => {
    const payload = {
      username: document.getElementById("reg-username").value.trim(),
      email: document.getElementById("reg-email").value.trim(),
      password: document.getElementById("reg-password").value,
      password2: document.getElementById("reg-password2").value,
    };

    try {
      const { register } = await import("./core/auth.js");
      await register(payload);
      showToast("Registered successfully! Please login.", "success");
      renderLogin();
    } catch (err) {
      showToast(err.message || "Registration failed", "error");
    }
  };

  document.getElementById("goLogin").onclick = (e) => {
    e.preventDefault();
    renderLogin();
  };
}

function renderApp() {
  document.getElementById("app").innerHTML = `
    <div style="padding: 20px;">
      <h2>Welcome 👋</h2>
      <p style="color:#64748b; margin: 8px 0 24px;">You are logged in. Next we will build the real screens.</p>

      <div class="card">
        <p>Coming next:</p>
        <ul style="margin-top: 12px; padding-left: 20px; color:#64748b;">
          <li>Upload Job Screenshot</li>
          <li>Review & Edit Email</li>
          <li>Application History</li>
        </ul>
      </div>
    </div>

    <nav class="bottom-nav">
      <button class="nav-item active">Home</button>
      <button class="nav-item">Applications</button>
      <button class="nav-item">Profile</button>
    </nav>
  `;
}

// Boot
if (isLoggedIn()) {
  renderApp();
} else {
  renderLogin();
}