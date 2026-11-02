const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');

test('자동 백업은 인증된 선생님 토큰만 보내고 수동 백업은 유지한다', () => {
  const html = fs.readFileSync('index.html', 'utf8');
  assert.match(html, /async function autoBackupNow/);
  assert.match(html, /Authorization:'Bearer '\+sess\.access_token/);
  assert.match(html, /setInterval\([^)]*autoBackupNow[^)]*15\*60\*1000/);
  assert.match(html, /function backupAll\(/);
  assert.match(html, /k!==LSS/);
});
