
// Service Worker for JobApply AI PWA
const CACHE_NAME = "jobapply";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
  "/favicon.ico",
  "/favicon-16.png",
  "/favicon-32.png",
  "/css/main.css",
  "/js/main.js",
  "/js/core/router.js",
  "/js/core/api.js",
  "/js/core/auth.js",
  "/js/core/store.js",
  "/js/core/toast.js",
  "/js/utils/dom.js",
  "/js/utils/pwa.js",
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

// Fetch - network first for everything, fallback to cache (works offline)
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== "GET") return;

  // Network-first with no-cache, fallback to cache
  event.respondWith(
    fetch(request, { cache: "no-cache" })
      .then(response => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => caches.match(request))
  );
});
