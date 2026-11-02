const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');

test('운영 도메인에서 문제은행 주소는 Pi로 향하고 개발 주소는 상대 경로를 쓴다', () => {
  const src = fs.readFileSync('bank-origin.js', 'utf8');
  assert.match(src, /bank\.solvi\.win/);
  assert.match(src, /location\.hostname===['"]solvi\.win['"]/);
  assert.match(src, /window\.bankUrl/);
});

test('초기 문제 데이터는 앱 본문보다 먼저 origin helper를 거쳐 불러온다', () => {
  const html = fs.readFileSync('index.html', 'utf8');
  const helper = html.indexOf('src="bank-origin.js');
  const core = html.indexOf('src="lib/academy-core.js');
  assert.ok(helper >= 0 && helper < core, 'bank-origin helper must load before application scripts');
  assert.doesNotMatch(html, /<script src="bank\/data\.js/);
});

test('문제은행 fetch는 bankUrl을 통해 외부 원점을 사용한다', () => {
  const html = fs.readFileSync('index.html', 'utf8');
  for (const path of ['index.json', 'data.json', 'concept.json']) {
    assert.match(html, new RegExp(`bankUrl\\([^)]*['"]${path}`));
  }
});
