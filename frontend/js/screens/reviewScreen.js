// frontend/js/screens/reviewScreen.js

import { bottomNav } from "../components/bottomNav.js";
import { emptyState, pageLoader } from "../components/loader.js";
import { pageHeader } from "../components/pageHeader.js";
import { statusBadge } from "../components/statusBadge.js";
import { showConfirmModal } from "../components/modal.js";
import { showToast } from "../core/toast.js";
import { applicationService } from "../services/applicationService.js";
import { $, esc, formatDate, mount, setLoading } from "../utils/dom.js";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function shell(inner) {
  return `<div class="page">${inner}</div>${bottomNav("/applications")}`;
}

function readForm() {
  return {
    to_email: $("#toEmail").value.trim(),
    subject: $("#subject").value.trim(),
    body: $("#body").value.trim(),
  };
}

function validate({ to_email, subject, body }) {
  if (!to_email) return "Enter the recipient email";
  if (!EMAIL_RE.test(to_email)) return "Recipient email is not valid";
  if (!subject) return "Subject cannot be empty";
  if (!body) return "Email body cannot be empty";
  return null;
}

function renderSent(app) {
  mount(
    shell(`
      ${pageHeader({ title: "Application sent", backTo: "/applications" })}
      <div class="card">
        <div class="detail-row"><span class="muted">Status</span>${statusBadge(app.status)}</div>
        <div class="detail-row"><span class="muted">To</span><strong>${esc(app.to_email)}</strong></div>
        <div class="detail-row"><span class="muted">Sent on</span><strong>${formatDate(app.sent_at)}</strong></div>
      </div>
      <div class="card">
        <div class="list-title" style="margin-bottom:8px">${esc(app.subject)}</div>
        <div class="email-preview">${esc(app.body)}</div>
      </div>
    `)
  );
}

function renderEditor(app) {
  const job = app.job_post || {};
  const failed = app.status === "failed";

  mount(
    shell(`
      ${pageHeader({
        title: "Review email",
        subtitle: `${job.role || "Role"} at ${job.company || "Company"}`,
        backTo: "/applications",
      })}

      ${
        failed
          ? `<div class="card notice"><strong>Last attempt failed</strong>
             <p class="muted" style="margin-top:6px">${esc(app.error_message) || "Unknown error"}</p></div>`
          : ""
      }

      <form class="card" id="reviewForm" novalidate>
        <div class="attach-row">
          ${
            app.resume
              ? `<span class="badge badge-info">📎 ${esc(app.resume.title)}.pdf attached</span>`
              : `<span class="badge badge-muted">No resume attached</span>`
          }
        </div>

        <div class="form-group">
          <label for="toEmail">To</label>
          <input type="email" id="toEmail" value="${esc(app.to_email)}" placeholder="hr@company.com" />
        </div>

        <div class="form-group">
          <label for="subject">Subject</label>
          <input type="text" id="subject" value="${esc(app.subject)}" maxlength="300" />
        </div>

        <div class="form-group">
          <label for="body">Message</label>
          <textarea id="body" rows="12">${esc(app.body)}</textarea>
        </div>

        <button type="button" class="btn btn-outline btn-block" id="saveBtn">Save draft</button>
        <button type="submit" class="btn btn-primary btn-block" id="sendBtn" style="margin-top:10px">
          ${failed ? "Retry send" : "Send email"}
        </button>
      </form>
    `)
  );

  $("#saveBtn").onclick = async () => {
    const data = readForm();
    if (!data.subject || !data.body) {
      showToast("Subject and message cannot be empty", "error");
      return;
    }
    const restore = setLoading($("#saveBtn"), "Saving...");
    try {
      await applicationService.update(app.id, data);
      showToast("Draft saved", "success");
    } catch (err) {
      showToast(err.message || "Could not save", "error");
    } finally {
      restore();
    }
  };

  $("#reviewForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = readForm();
    const problem = validate(data);
    if (problem) {
      showToast(problem, "error");
      return;
    }

    const confirmed = await showConfirmModal({
      title: "Send email?",
      message: `Send this email to ${data.to_email}? This cannot be undone.`,
      confirmText: "Send",
      cancelText: "Cancel",
      type: "warning"
    });
    if (!confirmed) return;

    const restore = setLoading($("#sendBtn"), "Sending...");
    try {
      await applicationService.update(app.id, data); // save latest edits first
      const sent = await applicationService.send(app.id);
      showToast("Email sent!", "success");
      renderSent(sent);
    } catch (err) {
      showToast(err.message || "Could not send email", "error");
      restore();
    }
  });
}

export async function reviewScreen({ id }) {
  mount(shell(pageLoader("Loading application...")));

  try {
    const app = await applicationService.get(id);
    if (app.status === "sent") renderSent(app);
    else renderEditor(app);
  } catch (err) {
    mount(
      shell(
        emptyState({
          icon: "⚠️",
          title: err.status === 404 ? "Application not found" : "Could not load application",
          text: err.message,
          actionHtml: `<a href="#/applications" class="btn btn-primary btn-sm">Back to applications</a>`,
        })
      )
    );
  }
}