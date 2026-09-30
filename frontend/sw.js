const CACHE_NAME = 'medsave-v2';
const ASSETS = [
    './',
    './index.html',
    './style.css',
    './main.js',
    './icon.png'
];

// Install Event - cache assets
self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
    );
});

// Activate Event - delete old caches (e.g. medsave-v1)
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        console.log('SW: Deleting old cache:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch Event - Network First for JS / API, Cache Fallback for offline
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Network-first strategy for JS scripts and API requests
    if (url.pathname.endsWith('.js') || url.pathname.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200 && !url.pathname.includes('/api/')) {
                        const responseClone = networkResponse.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
                    }
                    return networkResponse;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Default Cache-First strategy for static assets
    event.respondWith(
        caches.match(event.request).then((response) => response || fetch(event.request))
    );
});
