// frontend/js/screens/emailSettingsScreen.js
import { showToast } from "../core/toast.js";

import { bottomNav } from "../components/bottomNav.js";
import { pageHeader } from "../components/pageHeader.js";
import { authService } from "../services/authService.js";
import { api } from "../core/api.js";
import { $, esc, mount } from "../utils/dom.js";

export async function emailSettingsScreen() {
  const user = authService.currentUser() || {};
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");

  // Load current credential
  let credential = null;
  try {
    const res = await api.get("/accounts/email-credential/");
    credential = res.data;
  } catch (e) {
    // No credential or error
  }

  mount(`
    <div class="page">
      ${pageHeader({ title: "Email Settings", back: "/profile" })}

      <div class="card">
        <div class="card-title">Gmail App Password</div>
        <p class="muted small" style="margin-bottom: 16px;">
          Connect your Gmail account to send application emails from your own address.
          <br>You'll need a <strong>Gmail App Password</strong> (16 characters).
          <br><a href="https://support.google.com/accounts/answer/185833" target="_blank" class="link">How to create one?</a>
        </p>

        <div id="credentialForm">
          <div class="form-group">
            <label class="form-label">Gmail Address</label>
            <input type="email" class="form-input" id="emailInput" value="${esc(credential?.email || "")}" placeholder="your@gmail.com" ${credential ? "readonly" : ""}>
          </div>

          <div class="form-group" id="passwordGroup" style="${credential ? "display:none" : ""}">
            <label class="form-label">App Password</label>
            <input type="password" class="form-input" id="passwordInput" placeholder="16-character app password" autocomplete="new-password">
            <p class="muted small">This is stored encrypted and never shared.</p>
          </div>

          <div class="form-group" id="passwordGroupEdit" style="${credential ? "" : "display:none"}">
            <label class="form-label">New App Password (optional)</label>
            <input type="password" class="form-input" id="passwordInputEdit" placeholder="Leave blank to keep current" autocomplete="new-password">
          </div>

          <div id="credentialActions">
            ${credential 
              ? `<button class="btn btn-primary" id="updateBtn">Update</button>
                 <button class="btn btn-outline" id="deleteBtn" style="margin-left: 8px;">Disconnect</button>
                 <button class="btn btn-secondary" id="testBtn" style="margin-left: 8px;">Send Test Email</button>`
              : `<button class="btn btn-primary" id="saveBtn">Connect Gmail</button>`
            }
          </div>
        </div>

        ${credential ? `
        <div id="credentialStatus" class="card" style="margin-top: 16px; background: #e8f5e9;">
          <div class="detail-row">
            <span class="muted">Status</span>
            <strong style="color: #2e7d32;">${credential.is_verified ? "✅ Verified & Connected" : "⚠️ Not Verified"}</strong>
          </div>
          <div class="detail-row">
            <span class="muted">SMTP</span>
            <strong>${esc(credential.smtp_host)}:${credential.smtp_port}</strong>
          </div>
        </div>
        ` : ""}
      </div>

      <div class="card" style="margin-top: 16px;">
        <div class="card-title">How it works</div>
        <ul class="small muted" style="line-height: 1.8; padding-left: 20px;">
          <li>Your emails are sent via Gmail SMTP using your App Password</li>
          <li>HR replies go directly to your Gmail inbox</li>
          <li>Your resume PDF is automatically attached</li>
          <li>Password is encrypted at rest (AES-256 via Fernet)</li>
          <li>If not configured, platform fallback (Brevo) is used</li>
        </ul>
      </div>
    </div>
    ${bottomNav("/profile")}
  `);

  // Event handlers
  if (credential) {
    $("#updateBtn").onclick = () => handleUpdate();
    $("#deleteBtn").onclick = () => handleDelete();
    $("#testBtn").onclick = () => handleTest();
  } else {
    $("#saveBtn").onclick = () => handleSave();
  }
}

async function handleSave() {
  const email = $("#emailInput").value.trim();
  const password = $("#passwordInput").value.trim();

  if (!email || !password) {
    showToast("Please fill in both fields", "error");
    return;
  }

  if (!email.endsWith("@gmail.com")) {
    showToast("Please use a Gmail address", "error");
    return;
  }

  if (password.length !== 16) {
    showToast("App Password must be 16 characters", "error");
    return;
  }

  const btn = $("#saveBtn");
  btn.disabled = true;
  btn.textContent = "Connecting...";

  try {
    await api.post("/accounts/email-credential/", { email, password, smtp_host: "smtp.gmail.com", smtp_port: 587 });
    showToast("Gmail connected successfully!");
    // Reload screen
    window.location.hash = "/email-settings";
  } catch (e) {
    showToast(e.message || "Failed to connect Gmail", "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Connect Gmail";
  }
}

async function handleUpdate() {
  const password = $("#passwordInputEdit").value.trim();

  if (!password) {
    showToast("No changes to update", "error");
    return;
  }

  if (password.length !== 16) {
    showToast("App Password must be 16 characters", "error");
    return;
  }

  const btn = $("#updateBtn");
  btn.disabled = true;
  btn.textContent = "Updating...";

  try {
    await api.patch("/accounts/email-credential/", { password });
    showToast("Updated successfully!");
    window.location.hash = "/email-settings";
  } catch (e) {
    showToast(e.message || "Failed to update", "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Update";
  }
}

async function handleDelete() {
  if (!confirm("Disconnect Gmail? You'll need to set it up again to send from your address.")) return;

  const btn = $("#deleteBtn");
  btn.disabled = true;
  btn.textContent = "Disconnecting...";

  try {
    await api.delete("/accounts/email-credential/");
    showToast("Disconnected");
    window.location.hash = "/email-settings";
  } catch (e) {
    showToast(e.message || "Failed to disconnect", "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Disconnect";
  }
}

async function handleTest() {
  const testEmail = prompt("Enter email address to send test to:", authService.currentUser()?.email || "");
  if (!testEmail) return;

  const btn = $("#testBtn");
  btn.disabled = true;
  btn.textContent = "Sending...";

  try {
    await api.post("/accounts/email-credential/test/", { test_email: testEmail });
    showToast("Test email sent! Check your inbox.");
  } catch (e) {
    showToast(e.message || "Failed to send test email", "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Send Test Email";
  }
}
