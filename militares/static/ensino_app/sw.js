const CACHE_NAME = 'ensino-app-v2';
const URLS_TO_CACHE = [
  '/',
  '/militares/ensino/login/',
  '/militares/ensino/pwa/',
  '/militares/ensino/revisoes/meus/',
  '/militares/ensino/revisoes/instrutor/',
  '/static/logo_cbmepi.png',
  '/static/ensino_app/offline.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(URLS_TO_CACHE))
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);
  const isAPIGet = req.method === 'GET' && url.pathname.startsWith('/militares/api/ensino/');
  const isNavigate = req.mode === 'navigate';
  if (isAPIGet) {
    event.respondWith(
      fetch(req).then(resp => {
        const respClone = resp.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(req, respClone)).catch(()=>{});
        return resp;
      }).catch(() => caches.match(req))
    );
    return;
  }
  if (isNavigate) {
    event.respondWith(
      fetch(req).catch(() => caches.match('/static/ensino_app/offline.html'))
    );
    return;
  }
  event.respondWith(
    caches.match(req).then(response => response || fetch(req))
  );
});

self.addEventListener('push', event => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch(e) {}
  const title = data.title || 'Novo evento';
  const body = data.body || 'Você tem uma atualização';
  const options = { body, icon: '/static/logo_cbmepi.png', data: data.url ? { url: data.url } : {} };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/militares/ensino/pwa/';
  event.waitUntil(clients.openWindow(url));
});
