// frontend/js/components/loader.js

import { esc } from "../utils/dom.js";

export function pageLoader(text = "Loading...") {
  return `
    <div class="page-loader">
      <div class="spinner spinner-dark"></div>
      <p class="muted">${esc(text)}</p>
    </div>
  `;
}

export function emptyState({ icon = "📭", title, text = "", actionHtml = "" }) {
  return `
    <div class="empty-state">
      <div class="empty-icon">${icon}</div>
      <h3>${esc(title)}</h3>
      ${text ? `<p class="muted">${esc(text)}</p>` : ""}
      ${actionHtml}
    </div>
  `;
}