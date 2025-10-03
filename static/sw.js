/**
 * Service Worker for Elite FnO Trading Platform
 * Provides offline capabilities and performance improvements
 */

const CACHE_NAME = 'elite-fno-v1.0.0';
const urlsToCache = [
    '/',
    '/static/css/variables.css',
    '/static/css/base.css',
    '/static/css/components.css',
    '/static/css/animations.css',
    '/static/js/main.js',
    '/static/js/premium_landing.js',
    // Add other static assets as needed
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});