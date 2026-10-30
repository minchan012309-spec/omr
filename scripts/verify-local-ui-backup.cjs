/* 로컬 전용 검증: git 에서 제외된 backups/ui-rebuild-2026-10-29 백업이 온전한지 확인한다.
   깨끗한 clone · CI 에는 backups/ 가 없으므로 npm test 에 넣지 않는다. 실행: node --test scripts/verify-local-ui-backup.cjs */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const ROOT = path.resolve(__dirname, '..');
const BACKUP = path.join(ROOT, 'backups', 'ui-rebuild-2026-10-29');
const REQUIRED = [
  'index.html',
  'intro.html',
  'intro.css',
  'intro.js',
  'sw.js',
  'tests/intro-regression.cjs',
  'tests/runtime.cjs',
];

const sha256 = (file) =>
  crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

test('UI rebuild backup is complete and byte-verifiable', () => {
  assert.ok(fs.existsSync(BACKUP), 'backup directory must exist');
  const manifestPath = path.join(BACKUP, 'MANIFEST.txt');
  assert.ok(fs.existsSync(manifestPath), 'backup manifest must exist');
  const manifest = fs.readFileSync(manifestPath, 'utf8');
  assert.match(manifest, /^commit: [0-9a-f]{40}$/m);
  assert.match(manifest, /^branch: \S+$/m);
  assert.match(manifest, /^status:/m);

  for (const relative of REQUIRED) {
    const copy = path.join(BACKUP, relative);
    assert.ok(fs.existsSync(copy), `missing backup file: ${relative}`);
    assert.match(
      manifest,
      new RegExp(`^${sha256(copy)}  ${relative.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`, 'm'),
      `manifest checksum mismatch: ${relative}`,
    );
  }
});

test('backup output is excluded from product commits', () => {
  const ignore = fs.readFileSync(path.join(ROOT, '.gitignore'), 'utf8');
  assert.match(ignore, /^backups\/$/m);
});
