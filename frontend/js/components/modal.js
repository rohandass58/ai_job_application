// frontend/js/components/modal.js

import { $, esc, mount } from "../utils/dom.js";

let modalOverlay = null;
let modalResolve = null;

/**
 * Show a confirmation modal
 * @param {Object} options
 * @param {string} options.title - Modal title
 * @param {string} options.message - Main message
 * @param {string} options.confirmText - Confirm button text (default: "Confirm")
 * @param {string} options.cancelText - Cancel button text (default: "Cancel")
 * @param {string} options.type - "danger" | "warning" | "info" (default: "warning")
 * @returns {Promise<boolean>} - true if confirmed, false if cancelled
 */
export function showConfirmModal({
  title = "Confirm",
  message = "Are you sure?",
  confirmText = "Confirm",
  cancelText = "Cancel",
  type = "warning"
} = {}) {
  return new Promise((resolve) => {
    modalResolve = resolve;

    if (modalOverlay) modalOverlay.remove();

    const typeStyles = {
      danger: "border-danger bg-danger-light",
      warning: "border-warning bg-warning-light",
      info: "border-info bg-info-light"
    };

    const icons = {
      danger: "⚠️",
      warning: "⚠️",
      info: "ℹ️"
    };

    modalOverlay = document.createElement("div");
    modalOverlay.className = "modal-overlay";
    modalOverlay.innerHTML = `
      <div class="modal ${typeStyles[type] || typeStyles.warning}" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal-header">
          <span class="modal-icon" aria-hidden="true">${icons[type] || icons.warning}</span>
          <h3 id="modal-title">${esc(title)}</h3>
        </div>
        <div class="modal-body">
          <p>${esc(message)}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline modal-cancel">${esc(cancelText)}</button>
          <button type="button" class="btn btn-${type === "danger" ? "danger" : "primary"} modal-confirm">${esc(confirmText)}</button>
        </div>
      </div>
    `;

    document.body.appendChild(modalOverlay);

    requestAnimationFrame(() => {
      modalOverlay.classList.add("show");
    });

    const confirmBtn = modalOverlay.querySelector(".modal-confirm");
    const cancelBtn = modalOverlay.querySelector(".modal-cancel");
    const modal = modalOverlay.querySelector(".modal");

    confirmBtn.focus();

    const cleanup = () => {
      modalOverlay.classList.remove("show");
      setTimeout(() => {
        if (modalOverlay && modalOverlay.parentNode) modalOverlay.remove();
        modalOverlay = null;
        modalResolve = null;
      }, 200);
    };

    confirmBtn.onclick = () => {
      cleanup();
      resolve(true);
    };

    cancelBtn.onclick = () => {
      cleanup();
      resolve(false);
    };

    modalOverlay.onclick = (e) => {
      if (e.target === modalOverlay) {
        cleanup();
        resolve(false);
      }
    };

    const handleEsc = (e) => {
      if (e.key === "Escape" && modalOverlay) {
        cleanup();
        resolve(false);
        document.removeEventListener("keydown", handleEsc);
      }
    };
    document.addEventListener("keydown", handleEsc);

    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    modal.addEventListener("keydown", (e) => {
      if (e.key === "Tab") {
        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    });
  });
}

/**
 * Show an alert modal (single button)
 */
export function showAlertModal({
  title = "Notice",
  message = "",
  confirmText = "OK",
  type = "info"
} = {}) {
  return new Promise((resolve) => {
    if (modalOverlay) modalOverlay.remove();

    const typeStyles = {
      danger: "border-danger bg-danger-light",
      warning: "border-warning bg-warning-light",
      info: "border-info bg-info-light",
      success: "border-success bg-success-light"
    };

    const icons = {
      danger: "❌",
      warning: "⚠️",
      info: "ℹ️",
      success: "✅"
    };

    modalOverlay = document.createElement("div");
    modalOverlay.className = "modal-overlay";
    modalOverlay.innerHTML = `
      <div class="modal ${typeStyles[type] || typeStyles.info}" role="alertdialog" aria-modal="true" aria-labelledby="alert-title">
        <div class="modal-header">
          <span class="modal-icon" aria-hidden="true">${icons[type] || icons.info}</span>
          <h3 id="alert-title">${esc(title)}</h3>
        </div>
        <div class="modal-body">
          <p>${esc(message)}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-${type === "danger" ? "danger" : "primary"} modal-ok">${esc(confirmText)}</button>
        </div>
      </div>
    `;

    document.body.appendChild(modalOverlay);

    requestAnimationFrame(() => {
      modalOverlay.classList.add("show");
    });

    const okBtn = modalOverlay.querySelector(".modal-ok");
    okBtn.focus();

    const cleanup = () => {
      modalOverlay.classList.remove("show");
      setTimeout(() => {
        if (modalOverlay && modalOverlay.parentNode) modalOverlay.remove();
        modalOverlay = null;
      }, 200);
      resolve(true);
    };

    okBtn.onclick = cleanup;
    modalOverlay.onclick = (e) => {
      if (e.target === modalOverlay) cleanup();
    };

    const handleEsc = (e) => {
      if (e.key === "Escape" && modalOverlay) {
        cleanup();
        document.removeEventListener("keydown", handleEsc);
      }
    };
    document.addEventListener("keydown", handleEsc);
  });
}
