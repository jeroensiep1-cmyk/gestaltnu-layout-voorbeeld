const script = document.querySelector("script[src$='app.js']");
if (script && "serviceWorker" in navigator) {
  const swUrl = new URL("sw.js", script.src);
  navigator.serviceWorker.register(swUrl).catch(() => {});
}
