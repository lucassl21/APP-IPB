const CACHE_NAME = 'my-pwa-cache-v1';
const urlsToCache = [
    '/',
    '/home.html',
    '/index.html',
    '/script.js',
    '/images/icon-192x192.png',
    '/images/icon-512x512.png',
    'https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
    );
});