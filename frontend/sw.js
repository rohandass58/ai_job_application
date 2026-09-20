
// Service Worker for JobApply AI PWA
const CACHE_NAME = "jobapply-v1";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
  "/favicon.svg",
  "/css/main.css",
  "/js/main.js",
  "/js/core/router.js",
  "/js/core/api.js",
  "/js/core/auth.js",
  "/js/core/store.js",
  "/js/core/toast.js",
  "/js/utils/dom.js",
  "/js/components/bottomNav.js",
  "/js/components/pageHeader.js",
  "/js/components/loader.js",
  "/js/components/statusBadge.js",
  "/js/components/modal.js",
  "/js/services/authService.js",
  "/js/services/resumeService.js",
  "/js/services/jobService.js",
  "/js/services/applicationService.js",
  "/js/screens/homeScreen.js",
  "/js/screens/loginScreen.js",
  "/js/screens/registerScreen.js",
  "/js/screens/resumesScreen.js",
  "/js/screens/uploadScreen.js",
  "/js/screens/reviewScreen.js",
  "/js/screens/applicationsScreen.js",
  "/js/screens/profileScreen.js",
  "/js/screens/emailSettingsScreen.js"
];

// Install - cache static assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[SW] Caching static assets");
      return cache.addAll(STATIC_ASSETS.map(url => new Request(url, { cache: "reload" })));
    }).catch(err => console.error("[SW] Cache install failed:", err))
  );
  self.skipWaiting();
});

// Activate - clean old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch - network first for API, cache first for static
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== "GET") return;

  // API requests - network first, fallback to cache
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Static assets - cache first, fallback to network
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
        }
        return response;
      });
    })
  );
});

// Background sync for offline form submissions (future enhancement)
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-applications") {
    event.waitUntil(syncApplications());
  }
});

async function syncApplications() {
  // Future: sync pending applications when online
  console.log("[SW] Background sync triggered");
}
