// Service worker minimal de Lenyay : il rend l'application installable.
// Pas de cache applicatif : le chat est vivant par nature, servir du périmé
// serait pire que d'échouer franchement. Seul le réseau fait foi.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (e) => {
  e.respondWith(fetch(e.request).catch(() =>
    new Response("Hors ligne — Lenyay a besoin du réseau. / Offline — Lenyay needs the network.",
      { status: 503, headers: { "Content-Type": "text/plain; charset=utf-8" } })
  ));
});
