// frontend/js/screens/profileScreen.js

import { bottomNav } from "../components/bottomNav.js";
import { pageHeader } from "../components/pageHeader.js";
import { authService } from "../services/authService.js";
import { $, esc, mount } from "../utils/dom.js";

export function profileScreen() {
  const user = authService.currentUser() || {};
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");

  mount(`
    <div class="page">
      ${pageHeader({ title: "Profile" })}

      <div class="card">
        <div class="detail-row"><span class="muted">Name</span><strong>${esc(fullName) || "Not set"}</strong></div>
        <div class="detail-row"><span class="muted">Username</span><strong>${esc(user.username)}</strong></div>
        <div class="detail-row"><span class="muted">Email</span><strong>${esc(user.email) || "Not set"}</strong></div>
      </div>

      <div class="card list-card">
        <a href="#/resumes" class="list-item">
          <div class="list-main"><div class="list-title">📄 My Resumes</div></div>
          <span class="muted">›</span>
        </a>
        <a href="#/email-settings" class="list-item">
          <div class="list-main"><div class="list-title">📧 Email Settings</div></div>
          <span class="muted">›</span>
        </a>
      </div>

      <button class="btn btn-outline btn-block" id="logoutBtn">Log out</button>
    </div>
    ${bottomNav("/profile")}
  `);

  $("#logoutBtn").onclick = () => {
    if (confirm("Log out of your account?")) authService.logout();
  };
}