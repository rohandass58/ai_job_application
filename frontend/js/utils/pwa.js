// frontend/js/utils/pwa.js

let deferredPrompt = null;

/**
 * Initialize PWA install prompt handling
 * Call this early in your app (e.g., in main.js before startRouter)
 */
export function initPWA() {
  // Listen for the beforeinstallprompt event
  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    // Show your custom install UI (e.g., a button)
    showInstallButton();
  });

  // Listen for app installed event
  window.addEventListener('appinstalled', () => {
    console.log('[PWA] App was installed');
    hideInstallButton();
    deferredPrompt = null;
  });
}

/**
 * Show the custom install button
 * Creates a floating install button if it doesn't exist
 */
function showInstallButton() {
  // Don't show if already installed (standalone mode)
  if (window.matchMedia('(display-mode: standalone)').matches) {
    return;
  }

  // Don't create duplicate buttons
  if (document.getElementById('pwa-install-btn')) {
    return;
  }

  const btn = document.createElement('button');
  btn.id = 'pwa-install-btn';
  btn.innerHTML = '⬇️ Install App';
  btn.style.cssText = `
    position: fixed;
    bottom: 90px;
    right: 20px;
    z-index: 10000;
    padding: 12px 18px;
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 28px;
    font-size: 14px;
    font-weight: 600;
    box-shadow: 0 4px 16px rgba(79, 70, 229, 0.4);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    animation: slideUp 0.3s ease;
  `;

  // Add keyframes for animation
  if (!document.getElementById('pwa-install-styles')) {
    const style = document.createElement('style');
    style.id = 'pwa-install-styles';
    style.textContent = `
      @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      #pwa-install-btn:hover {
        background: #4338ca;
        transform: scale(1.02);
      }
    `;
    document.head.appendChild(style);
  }

  btn.addEventListener('click', async () => {
    if (!deferredPrompt) return;
    
    // Show the native install prompt
    deferredPrompt.prompt();
    
    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.userChoice;
    console.log('[PWA] User response to install prompt:', outcome);
    
    if (outcome === 'accepted') {
      console.log('[PWA] User accepted the install prompt');
    } else {
      console.log('[PWA] User dismissed the install prompt');
    }
    
    // Clear the deferredPrompt as it can only be used once
    deferredPrompt = null;
    hideInstallButton();
  });

  document.body.appendChild(btn);
}

/**
 * Hide the custom install button
 */
function hideInstallButton() {
  const btn = document.getElementById('pwa-install-btn');
  if (btn) {
    btn.style.animation = 'slideUp 0.3s ease reverse';
    setTimeout(() => btn.remove(), 300);
  }
}

/**
 * Check if app is already installed
 */
export function isAppInstalled() {
  return window.matchMedia('(display-mode: standalone)').matches;
}