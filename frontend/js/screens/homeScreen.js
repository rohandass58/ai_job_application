// frontend/js/screens/homeScreen.js

import { bottomNav } from "../components/bottomNav.js";
import { emptyState, pageLoader } from "../components/loader.js";
import { statusBadge } from "../components/statusBadge.js";
import { showToast } from "../core/toast.js";
import { applicationService } from "../services/applicationService.js";
import { authService } from "../services/authService.js";
import { resumeService } from "../services/resumeService.js";
import { api } from "../core/api.js";
import { esc, mount, timeAgo } from "../utils/dom.js";

function shell(inner) {
  return `<div class="page">${inner}</div>${bottomNav("/home")}`;
}

function statCard(value, label) {
  return `
    <div class="stat-card">
      <div class="stat-value">${value}</div>
      <div class="stat-label">${label}</div>
    </div>`;
}

function recentItem(app) {
  const company = app.job_post?.company || "Unknown company";
  const role = app.job_post?.role || "Role not detected";

  return `
    <a href="#/applications/${app.id}" class="list-item">
      <div class="list-main">
        <div class="list-title">${esc(role)}</div>
        <div class="muted">${esc(company)} · ${timeAgo(app.created_at)}</div>
      </div>
      ${statusBadge(app.status)}
    </a>`;
}

function emailCredentialBanner(credential) {
  if (credential?.is_verified) return "";
  
  const hasCredential = credential !== null;
  const message = hasCredential
    ? "Your Gmail App Password is not verified yet."
    : "Connect your Gmail to send application emails from your own address.";
  
  const actionText = hasCredential ? "Verify now" : "Connect Gmail";
  
  return `
    <div class="card banner banner-warning" style="margin-bottom: 16px;">
      <div class="banner-icon">📧</div>
      <div class="banner-content">
        <strong>Email not set up</strong>
        <p class="muted" style="margin: 4px 0 0;">${message}</p>
      </div>
      <a href="#/email-settings" class="btn btn-sm btn-primary">${actionText}</a>
    </div>`;
}

export async function homeScreen() {
  mount(shell(pageLoader("Loading your dashboard...")));

  const user = authService.currentUser();
  const name = user?.first_name || user?.username || "there";

  try {
    const [resumes, applications] = await Promise.all([
      resumeService.list(),
      applicationService.list(),
    ]);

    // Check email credential
    let credential = null;
    try {
      const res = await api.get("/accounts/email-credential/");
      credential = res.data;
    } catch (e) {
      // No credential or error
    }

    const sent = applications.filter((a) => a.status === "sent").length;
    const drafts = applications.filter((a) => a.status === "draft" || a.status === "ready").length;
    const recent = applications.slice(0, 5);
    const hasResume = resumes.length > 0;

    const cta = hasResume
      ? `<a href="#/upload" class="btn btn-primary btn-block">📸 New Application</a>`
      : `
        <div class="card notice">
          <strong>Upload your resume first</strong>
          <p class="muted" style="margin:6px 0 14px">
            The AI uses your resume to write a personalised email.
          </p>
          <a href="#/resumes" class="btn btn-primary btn-block">Upload Resume</a>
        </div>`;

    mount(
      shell(`
        <header class="page-header">
          <h2>Hi, ${esc(name)} 👋</h2>
          <p class="muted">Ready to apply smarter?</p>
        </header>

        ${emailCredentialBanner(credential)}

        <div class="stat-row">
          ${statCard(applications.length, "Total")}
          ${statCard(sent, "Sent")}
          ${statCard(drafts, "Drafts")}
        </div>

        ${cta}

        <div class="section-head">
          <h3>Recent applications</h3>
          ${applications.length > 5 ? `<a href="#/applications" class="link">View all</a>` : ""}
        </div>

        ${
          recent.length
            ? `<div class="card list-card">${recent.map(recentItem).join("")}</div>`
            : emptyState({
                icon: "📨",
                title: "No applications yet",
                text: "Upload a job screenshot and we will draft the email for you.",
              })
        }
      `)
    );
  } catch (err) {
    showToast(err.message || "Failed to load dashboard", "error");
    mount(
      shell(
        emptyState({
          icon: "⚠️",
          title: "Could not load dashboard",
          text: err.message,
          actionHtml: `<button class="btn btn-primary btn-sm" onclick="location.reload()">Retry</button>`,
        })
      )
    );
  }
}
