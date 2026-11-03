const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');

test('문제은행은 GitHub Pages 안의 정적 파일에서 직접 읽는다', () => {
  const html = fs.readFileSync('index.html', 'utf8');
  assert.match(html, /<script src="bank\/data\.js\?v=\d+"><\/script>/);
  assert.doesNotMatch(html, /bank-origin\.js/);
  assert.doesNotMatch(html, /bank\.solvi\.win/);
});

test('문제은행 요청과 백업은 라즈베리파이 전용 API에 의존하지 않는다', () => {
  const html = fs.readFileSync('index.html', 'utf8');
  assert.doesNotMatch(html, /bankUrl\(/);
  assert.doesNotMatch(html, /autoBackupNow/);
  assert.doesNotMatch(html, /\/api\/backups/);
});
