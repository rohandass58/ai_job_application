// frontend/js/screens/registerScreen.js

import { navigate } from "../core/router.js";
import { showToast } from "../core/toast.js";
import { authService } from "../services/authService.js";
import { $, $$, esc, mount, setLoading } from "../utils/dom.js";

const REG_FIELDS = ["username", "email", "password", "password2", "first_name", "last_name"];
const OTP_FIELDS = ["otp_code"];

let registrationData = null; // Store registration data between steps

function showFieldErrors(errors, fields = REG_FIELDS) {
  $$(".field-error").forEach((el) => el.remove());
  if (!errors || typeof errors !== "object") return;

  fields.forEach((field) => {
    const messages = errors[field];
    if (!messages) return;

    const input = $(`#reg-${field}`);
    const text = Array.isArray(messages) ? messages.join(" ") : String(messages);
    input.insertAdjacentHTML("afterend", `<div class="field-error">${esc(text)}</div>`);
  });
}

function renderRegistrationForm() {
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
          <label for="reg-first_name">First Name (optional)</label>
          <input type="text" id="reg-first_name" autocomplete="given-name" />
        </div>

        <div class="form-group">
          <label for="reg-last_name">Last Name (optional)</label>
          <input type="text" id="reg-last_name" autocomplete="family-name" />
        </div>

        <div class="form-group">
          <label for="reg-password">Password</label>
          <input type="password" id="reg-password" autocomplete="new-password" required />
        </div>

        <div class="form-group">
          <label for="reg-password2">Confirm Password</label>
          <input type="password" id="reg-password2" autocomplete="new-password" required />
        </div>

        <button type="submit" class="btn btn-primary" id="registerBtn">Send Verification Code</button>

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
      email: $("#reg-email").value.trim().toLowerCase(),
      first_name: $("#reg-first_name").value.trim(),
      last_name: $("#reg-last_name").value.trim(),
      password: $("#reg-password").value,
      password2: $("#reg-password2").value,
    };

    if (payload.password !== payload.password2) {
      showFieldErrors({ password2: "Passwords do not match" });
      return;
    }

    const restore = setLoading($("#registerBtn"), "Sending code...");
    try {
      await authService.registerInit(payload);
      registrationData = payload;
      showToast("Verification code sent to your email!", "success");
      renderOTPForm(payload.email);
    } catch (err) {
      showFieldErrors(err.errors);
      showToast(err.message || "Registration failed", "error");
      restore();
    }
  });
}

function renderOTPForm(email) {
  mount(`
    <div class="auth-wrap">
      <h1 class="auth-title">Verify Email</h1>
      <p class="auth-sub">We sent a 6-digit code to <strong>${esc(email)}</strong></p>

      <form class="card" id="otpForm" novalidate>
        <div class="form-group">
          <label for="reg-otp_code">Verification Code</label>
          <input 
            type="text" 
            id="reg-otp_code" 
            inputmode="numeric" 
            maxlength="6" 
            pattern="[0-9]{6}" 
            autocomplete="one-time-code" 
            required 
            style="letter-spacing: 0.5em; text-align: center; font-size: 1.25rem;"
            placeholder="000000"
          />
        </div>

        <button type="submit" class="btn btn-primary" id="verifyBtn">Verify & Create Account</button>

        <p class="auth-switch" style="margin-top: 16px;">
          <button type="button" class="btn btn-link" id="resendBtn">Didn't receive it? Resend code</button>
        </p>
        <p class="auth-switch">
          <a href="#/register">← Back to registration</a>
        </p>
      </form>
    </div>
  `);

  const otpInput = $("#reg-otp_code");
  otpInput.focus();

  otpInput.addEventListener("input", (e) => {
    e.target.value = e.target.value.replace(/[^0-9]/g, "");
  });

  $("#otpForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    showFieldErrors(null, OTP_FIELDS);

    const otpCode = otpInput.value.trim();
    if (otpCode.length !== 6) {
      showFieldErrors({ otp_code: "Please enter the 6-digit code" }, OTP_FIELDS);
      return;
    }

    const restore = setLoading($("#verifyBtn"), "Verifying...");
    try {
      await authService.verifyOTP(email, otpCode);
      showToast("Account created successfully!", "success");
      navigate("/home");
    } catch (err) {
      showFieldErrors(err.errors, OTP_FIELDS);
      showToast(err.message || "Verification failed", "error");
      restore();
    }
  });

  $("#resendBtn").addEventListener("click", async () => {
    const btn = $("#resendBtn");
    btn.disabled = true;
    btn.textContent = "Sending...";

    try {
      await authService.resendOTP(email);
      showToast("New code sent!", "success");
    } catch (err) {
      showToast(err.message || "Failed to resend code", "error");
    } finally {
      btn.disabled = false;
      btn.textContent = "Didn't receive it? Resend code";
    }
  });
}

export function registerScreen() {
  renderRegistrationForm();
}
