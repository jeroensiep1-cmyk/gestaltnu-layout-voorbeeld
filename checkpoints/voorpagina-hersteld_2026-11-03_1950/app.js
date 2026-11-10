const knop = document.querySelector(".menu-knop");
const menu = document.querySelector("#menu");

if (knop && menu) {
  knop.addEventListener("click", () => {
    const open = knop.getAttribute("aria-expanded") === "true";
    knop.setAttribute("aria-expanded", String(!open));
    menu.classList.toggle("open", !open);
  });
}

const script = document.querySelector("script[src$='app.js']");
if (script && "serviceWorker" in navigator) {
  const swUrl = new URL("sw.js", script.src);
  navigator.serviceWorker.register(swUrl).catch(() => {});
}
