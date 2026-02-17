var CACHE='eventspot-v3';
var ASSETS=['/','index.html','manifest.json','icon-192.png','icon-512.png'];
self.addEventListener('install',function(e){e.waitUntil(caches.open(CACHE).then(function(c){return c.addAll(ASSETS)}));self.skipWaiting()});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(k){return Promise.all(k.filter(function(x){return x!==CACHE}).map(function(x){return caches.delete(x)}))}));self.clients.claim()});
self.addEventListener('fetch',function(e){if(e.request.url.indexOf('firestore')>=0||e.request.url.indexOf('googleapis')>=0){e.respondWith(fetch(e.request).catch(function(){return caches.match(e.request)}))}else{e.respondWith(caches.match(e.request).then(function(r){return r||fetch(e.request)}))}});
