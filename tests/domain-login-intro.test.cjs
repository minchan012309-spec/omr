/* 운영 도메인 전환과 첫 진입 흐름이 이전 주소·단순 알림으로 되돌아가지 않게 지키는 정적 계약. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { test } = require('node:test');

const read = f => fs.readFileSync(f, 'utf8');
const app = read('index.html');
const intro = read('intro.html');
const introCss = read('intro.css');
const passkey = read('supabase/functions/passkey/index.ts');

test('쌍둥이 문제를 담으면 하단에서 바로 학습지 만들기를 제안한다', () => {
  assert.match(app, /function basketBar\(notice(?:='')?\)/, 'basket bar accepts a context notice');
  assert.match(app, /쌍둥이 문제 3개를 담았어요\. 바로 학습지로 만들까요\?/, 'twin add supplies a clear next action');
  assert.match(app, /class="bk-note"/, 'basket bar renders the twin-specific message');
  assert.doesNotMatch(app, /alert\('쌍둥이 문제 3개를 담았습니다\.'/, 'a blocking alert cannot hide the next action');
});

test('공개 운영 주소와 패스키 기본 RP는 solvi.win이다', () => {
  assert.match(app, /pub:'https:\/\/solvi\.win\/'/);
  assert.match(passkey, /const DEFAULT_SITE = 'https:\/\/solvi\.win';/);
  for (const file of ['index.html', 'intro.html', 'policy.html', 'robots.txt', 'sitemap.xml']) {
    assert.doesNotMatch(read(file), /solvi\.p-e\.kr/, file + ' has no old public URL');
  }
  assert.match(app, /이전 주소에서 만든 패스키는 새 주소에서 다시 등록해야 해요/, 'origin mismatch has a useful recovery message');
});

test('인트로 첫 화면은 유형 지도이고, 바로 아래에는 수업의 문제를 말하는 문장이 있다', () => {
  assert.match(intro, /<figure class="tmap" id="tmap">/);
  assert.match(intro, /<section class="why" id="why"/);
  assert.match(intro, /학생마다 틀리는 곳은 다릅니다/);
  assert.doesNotMatch(intro, /id="systemMap"/, 'the operation map is not the hero focal point');
  assert.match(introCss, /\.tmap\{/, 'type-map visual system remains styled');
});

test('로그인 화면은 역할 선택과 폼에 서로 다른 여백 리듬을 둔다', () => {
  const css = read('styles/screens.css');
  assert.match(css, /\.entry-card\{[^}]*padding:clamp\(24px,4vw,40px\)/);
  assert.match(css, /\.entry-card #stbody\{display:grid;gap:18px/);
  assert.match(css, /\.entry-card\{padding:20px 18px/, 'mobile card has compact horizontal padding');
});
