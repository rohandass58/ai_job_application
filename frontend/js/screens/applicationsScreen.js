// frontend/js/screens/applicationsScreen.js

import { bottomNav } from "../components/bottomNav.js";
import { emptyState, pageLoader } from "../components/loader.js";
import { pageHeader } from "../components/pageHeader.js";
import { statusBadge } from "../components/statusBadge.js";
import { showToast } from "../core/toast.js";
import { applicationService } from "../services/applicationService.js";
import { $, $$, esc, mount, timeAgo } from "../utils/dom.js";

const FILTERS = [
  { key: "all", label: "All", match: () => true },
  { key: "draft", label: "Drafts", match: (a) => a.status === "draft" || a.status === "ready" },
  { key: "sent", label: "Sent", match: (a) => a.status === "sent" },
  { key: "failed", label: "Failed", match: (a) => a.status === "failed" },
];

function shell(inner) {
  return `<div class="page">${inner}</div>${bottomNav("/applications")}`;
}

function itemHtml(app) {
  const company = app.job_post?.company || "Unknown company";
  const role = app.job_post?.role || "Role not detected";

  return `
    <a href="#/applications/${app.id}" class="list-item">
      <div class="list-main">
        <div class="list-title">${esc(role)}</div>
        <div class="muted">${esc(company)} · ${timeAgo(app.created_at)}</div>
        ${app.to_email ? `<div class="muted">To: ${esc(app.to_email)}</div>` : ""}
      </div>
      ${statusBadge(app.status)}
    </a>`;
}

function renderList(apps, filterKey) {
  const filter = FILTERS.find((f) => f.key === filterKey) || FILTERS[0];
  const filtered = apps.filter(filter.match);
  const box = $("#appList");

  box.innerHTML = filtered.length
    ? `<div class="card list-card">${filtered.map(itemHtml).join("")}</div>`
    : emptyState({
        icon: "📭",
        title: filterKey === "all" ? "No applications yet" : "Nothing here",
        text: filterKey === "all" ? "Start by uploading a job screenshot." : "No applications match this filter.",
        actionHtml:
          filterKey === "all" ? `<a href="#/upload" class="btn btn-primary btn-sm">New Application</a>` : "",
      });
}

export async function applicationsScreen() {
  mount(shell(pageLoader("Loading applications...")));

  try {
    const apps = await applicationService.list();

    mount(
      shell(`
        ${pageHeader({ title: "Applications", subtitle: `${apps.length} total` })}

        <div class="tabs" id="filterTabs">
          ${FILTERS.map(
            (f, i) => `<button class="tab ${i === 0 ? "active" : ""}" data-filter="${f.key}">${f.label}</button>`
          ).join("")}
        </div>

        <div id="appList"></div>
      `)
    );

    renderList(apps, "all");

    $("#filterTabs").addEventListener("click", (e) => {
      const btn = e.target.closest(".tab");
      if (!btn) return;
      $$(".tab").forEach((t) => t.classList.remove("active"));
      btn.classList.add("active");
      renderList(apps, btn.dataset.filter);
    });
  } catch (err) {
    showToast(err.message || "Failed to load applications", "error");
    mount(
      shell(
        emptyState({
          icon: "⚠️",
          title: "Could not load applications",
          text: err.message,
          actionHtml: `<button class="btn btn-primary btn-sm" onclick="location.reload()">Retry</button>`,
        })
      )
    );
  }
}