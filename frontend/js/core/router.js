// frontend/js/core/router.js

import { isLoggedIn } from "./auth.js";

const routes = new Map();
let notFoundHandler = null;

/**
 * routes are registered as:
 *   register("/home", handler, { auth: true })
 *   register("/jobs/:id", handler, { auth: true })
 */
export function register(path, handler, options = {}) {
  const keys = [];
  const pattern = path.replace(/:([^/]+)/g, (_, key) => {
    keys.push(key);
    return "([^/]+)";
  });

  routes.set(path, {
    regex: new RegExp(`^${pattern}$`),
    keys,
    handler,
    auth: options.auth ?? false,
  });
}

export function setNotFound(handler) {
  notFoundHandler = handler;
}

export function navigate(path) {
  if (window.location.hash === `#${path}`) {
    resolve(); // same route -> force re-render
  } else {
    window.location.hash = path;
  }
}

function currentPath() {
  return window.location.hash.replace(/^#/, "") || "/";
}

export function resolve() {
  const path = currentPath();

  for (const route of routes.values()) {
    const match = path.match(route.regex);
    if (!match) continue;

    // Auth guard
    if (route.auth && !isLoggedIn()) {
      navigate("/login");
      return;
    }

    // Logged-in user should not see login/register again
    if (!route.auth && isLoggedIn() && (path === "/login" || path === "/register")) {
      navigate("/home");
      return;
    }

    const params = {};
    route.keys.forEach((key, i) => {
      params[key] = decodeURIComponent(match[i + 1]);
    });

    route.handler(params);
    return;
  }

  if (notFoundHandler) notFoundHandler();
}

export function startRouter() {
  window.addEventListener("hashchange", resolve);
  resolve();
}