var C = 'es-v5';
self.addEventListener('install', function(e) { self.skipWaiting(); });
self.addEventListener('activate', function(e) {
  e.waitUntil(caches.keys().then(function(ks) {
    return Promise.all(ks.filter(function(k){return k!==C}).map(function(k){return caches.delete(k)}));
  }));
  self.clients.claim();
});
self.addEventListener('fetch', function(e) {
  e.respondWith(fetch(e.request).catch(function() { return caches.match(e.request); }));
});
