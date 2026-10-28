/* Solvi 서비스 워커: 앱 껍데기와 한 번 불러온 데이터를 저장해 두어 오프라인에서도 열리게 합니다. */
const VER = 'solvi-v154';
const SHELL = ['./', 'index.html', 'books.js', 'lazy/omr-report.js', 'lazy/tset.js', 'lazy/acad.js', 'lazy/admin.js', 'lib/academy-core.js?v=1', 'lib/korean-editor.js?v=1', 'fonts/SolviSymbols.woff2', 'bank/data.js?v=1', 'manifest.webmanifest?v=2', 'icons/icon-192.png?v=2', 'icons/icon-512.png?v=2', 'fonts/KoPubDotum-Medium.subset.woff2', 'fonts/KoPubDotum-Bold.subset.woff2', 'intro.html', 'intro.css?v=5', 'intro.js?v=5', 'intro/display.webp'];
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
  if (/^\/((google|naver)[0-9a-z]+\.html|robots\.txt|sitemap\.xml)$/.test(u.pathname)) return; // 검색엔진 확인·안내 파일은 서비스 워커가 가로채지 않음
  if (r.mode === 'navigate') { // 페이지는 네트워크 우선(새 버전을 바로 받음), 실패하면 저장본
    e.respondWith(fetch(r).then(res => { if (res && res.ok && (u.pathname === '/' || /\/index\.html$/.test(u.pathname))) caches.open(VER).then(c => c.put('index.html', res.clone())); return res; })
      .catch(() => caches.match('index.html').then(h => h || caches.match('./'))));
    return;
  }
  if (/\.(js|css)$/.test(u.pathname)) { // 코드(JS·CSS)는 네트워크 우선: HTML 과 버전이 어긋나 화면이 깨지지 않게(예전 저장본이 새 HTML 에 붙던 문제), 오프라인이면 저장본
    e.respondWith(caches.open(VER).then(c => fetch(r).then(res => { if (res && res.ok) c.put(r, res.clone()); return res; }).catch(() => c.match(r).then(h => h || c.match(r, { ignoreSearch: true })))));
    return;
  }
  // 그 밖의 정적 파일(데이터·이미지·글꼴)은 저장본을 먼저 보여주고 뒤에서 갱신
  e.respondWith(caches.open(VER).then(async c => {
    const hit = await c.match(r);
    const net = fetch(r).then(res => { if (res && res.ok) c.put(r, res.clone()); return res; }).catch(() => hit);
    return hit || net;
  }));
});
