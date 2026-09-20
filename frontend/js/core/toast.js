// frontend/js/core/toast.js

export function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message; // textContent (not innerHTML) -> XSS safe

  container.appendChild(toast);

  const duration = type === "error" ? 4500 : 3000;
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}