// frontend/js/main.js

import { register, setNotFound, startRouter } from "./core/router.js";
import { applicationsScreen } from "./screens/applicationsScreen.js";
import { homeScreen } from "./screens/homeScreen.js";
import { loginScreen } from "./screens/loginScreen.js";
import { profileScreen } from "./screens/profileScreen.js";
import { registerScreen } from "./screens/registerScreen.js";
import { resumesScreen } from "./screens/resumesScreen.js";
import { reviewScreen } from "./screens/reviewScreen.js";
import { uploadScreen } from "./screens/uploadScreen.js";
import { emailSettingsScreen } from "./screens/emailSettingsScreen.js";
import { mount } from "./utils/dom.js";


// Register Service Worker for PWA
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js")
      .then(reg => console.log("[PWA] Service Worker registered:", reg.scope))
      .catch(err => console.error("[PWA] Service Worker registration failed:", err));
  });
}

register("/login", loginScreen);
register("/register", registerScreen);
register("/home", homeScreen, { auth: true });
register("/resumes", resumesScreen, { auth: true });
register("/upload", uploadScreen, { auth: true });
register("/applications/:id", reviewScreen, { auth: true });
register("/applications", applicationsScreen, { auth: true });
register("/profile", profileScreen, { auth: true });
register("/email-settings", emailSettingsScreen, { auth: true });
setNotFound(() =>
  mount(`<div style="padding:20px"><div class="card">Page not found</div></div>`)
);

if (!window.location.hash) {
  window.location.hash = "/login";
}

startRouter();