// frontend/js/components/bottomNav.js

const TABS = [
  { path: "/home", label: "Home", icon: "🏠" },
  { path: "/applications", label: "Applications", icon: "📨" },
  { path: "/profile", label: "Profile", icon: "👤" },
];

export function bottomNav(activePath) {
  return `
    <nav class="bottom-nav">
      ${TABS.map(
        (tab) => `
        <a href="#${tab.path}" class="nav-item ${tab.path === activePath ? "active" : ""}">
          <span class="nav-icon">${tab.icon}</span>
          <span>${tab.label}</span>
        </a>`
      ).join("")}
    </nav>
  `;
}