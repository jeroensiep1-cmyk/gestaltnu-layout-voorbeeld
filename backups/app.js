const knop = document.querySelector(".menu-knop");
const menu = document.querySelector("#menu");

if (knop && menu) {
  knop.addEventListener("click", () => {
    const open = knop.getAttribute("aria-expanded") === "true";
    knop.setAttribute("aria-expanded", String(!open));
    menu.classList.toggle("open", !open);
  });
}

/* Preview: geen service worker — oude /sw.js-cache maakte de hero wit (404 op PNG). */
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.getRegistrations().then((regs) => {
    regs.forEach((r) => r.unregister());
  });
  if (navigator.serviceWorker.controller) {
    // forceer loskoppelen bij volgende load
  }
  if (window.caches) {
    caches.keys().then((keys) => keys.forEach((k) => caches.delete(k)));
  }
}
