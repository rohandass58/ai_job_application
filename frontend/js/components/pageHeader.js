// frontend/js/components/pageHeader.js

import { esc } from "../utils/dom.js";

export function pageHeader({ title, subtitle = "", backTo = null }) {
  return `
    <header class="page-header">
      ${backTo ? `<a href="#${backTo}" class="back-link">← Back</a>` : ""}
      <h2>${esc(title)}</h2>
      ${subtitle ? `<p class="muted">${esc(subtitle)}</p>` : ""}
    </header>
  `;
}