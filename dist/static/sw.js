const CACHE_NAME = 'fantamaestro-cache-v2';
const ASSETS = [
  '/',
  '/static/css/modern_app.css',
  '/static/js/api_client.js',
  '/static/js/app.js',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Richieste di navigazione HTML: Network-first per avere sempre i dati e la grafica più recenti
  if (event.request.mode === 'navigate' || (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html'))) {
    event.respondWith(
      fetch(event.request).then((response) => {
        return response;
      }).catch(() => {
        return caches.match(event.request) || caches.match('/');
      })
    );
    return;
  }

  // Se la richiesta è per una route API, prova la rete prima della cache
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return caches.match(event.request);
      })
    );
    return;
  }

  // Risorse statiche: Cache-first con fallback su rete
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return cachedResponse || fetch(event.request);
    })
  );
});
