const CACHE_NAME = 'my-pwa-cache-v3'; // Altere a versão do cache.
const urlsToCache = [
    '/',
    '/index.html',
    '/script.js',
    '/login.html',
    '/cadastro.html',
    '/historico.html',
    '/admin_dashboard.html',
    '/esqueci-senha.html',
    '/esqueci-senha.js',
    '/redefinir-senha.html',
    '/redefinir-senha.js',
    '/images/icon-192x192.png',
    '/images/icon-512x512.png',
    '/images/logo.png',
    'https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css',
    'https://cdn.jsdelivr.net/npm/chart.js',
    'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Open+Sans:wght@400;600&display=swap'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        console.log('Service Worker: Deletando cache antigo', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                
                return fetch(event.request);
            })
    );
});