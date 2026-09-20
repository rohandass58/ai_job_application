// frontend/js/components/statusBadge.js

const STATUS_MAP = {
  draft: { label: "Draft", cls: "badge-muted" },
  ready: { label: "Ready", cls: "badge-info" },
  sent: { label: "Sent", cls: "badge-success" },
  failed: { label: "Failed", cls: "badge-danger" },
};

export function statusBadge(status) {
  const s = STATUS_MAP[status] || { label: status, cls: "badge-muted" };
  return `<span class="badge ${s.cls}">${s.label}</span>`;
}