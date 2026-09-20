// frontend/js/utils/dom.js

const ESCAPE_MAP = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

/**
 * Escape untrusted text before putting it inside innerHTML.
 * Rule: EVERY dynamic value in a template string goes through esc().
 */
export function esc(value) {
  if (value === null || value === undefined) return "";
  return String(value).replace(/[&<>"']/g, (ch) => ESCAPE_MAP[ch]);
}

/** Shorthand for document.querySelector scoped to a root. */
export function $(selector, root = document) {
  return root.querySelector(selector);
}

export function $$(selector, root = document) {
  return Array.from(root.querySelectorAll(selector));
}

/** Render html string into #app (single place that touches the DOM root). */
export function mount(html) {
  const app = document.getElementById("app");
  app.innerHTML = html;
  window.scrollTo(0, 0);
  return app;
}

/** Disable a button + show loading label; returns a restore function. */
export function setLoading(button, label = "Please wait...") {
  const original = button.innerHTML;
  button.disabled = true;
  button.innerHTML = `<span class="spinner"></span> ${esc(label)}`;
  return () => {
    button.disabled = false;
    button.innerHTML = original;
  };
}

/** "2026-05-01T10:00:00Z" -> "1 May 2026" */
export function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

/** 1536000 -> "1.5 MB" */
export function formatBytes(bytes) {
  if (!bytes) return "";
  const units = ["B", "KB", "MB"];
  let i = 0;
  let size = bytes;
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024;
    i++;
  }
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

/** "2026-09-20T10:00:00Z" -> "2 hours ago" */
export function timeAgo(iso) {
  if (!iso) return "";
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hr ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} day${days > 1 ? "s" : ""} ago`;
  return formatDate(iso);
}