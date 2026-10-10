/* Solvi 서비스 워커: 앱 껍데기와 한 번 불러온 데이터를 저장해 두어 오프라인에서도 열리게 합니다. */
const VER = 'solvi-v2';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(VER).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VER).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET') return;
  const u = new URL(r.url);
  if (u.origin !== location.origin) return; // Supabase·외부 CDN은 건드리지 않음
  if (r.mode === 'navigate') { // 페이지는 네트워크 우선(새 버전을 바로 받음), 실패하면 저장본
    e.respondWith(fetch(r).then(res => { if (res && res.ok) caches.open(VER).then(c => c.put('index.html', res.clone())); return res; })
      .catch(() => caches.match('index.html').then(h => h || caches.match('./'))));
    return;
  }
  // 그 밖의 정적 파일(데이터·이미지·글꼴)은 저장본을 먼저 보여주고 뒤에서 갱신
  e.respondWith(caches.open(VER).then(async c => {
    const hit = await c.match(r);
    const net = fetch(r).then(res => { if (res && res.ok) c.put(r, res.clone()); return res; }).catch(() => hit);
    return hit || net;
  }));
});
