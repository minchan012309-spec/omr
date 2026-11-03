import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import zlib from 'node:zlib';
import { promisify } from 'node:util';
import { saveSnapshot } from '../pi/question-bank/backup-api/server.mjs';

const gunzip = promisify(zlib.gunzip);
async function withRoot(fn) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'solvi-backup-'));
  try { await fn(root); }
  finally { await fs.rm(root, { recursive: true, force: true }); }
}

test('선생님 백업은 사용자별 gzip 파일로 저장한다', async () => withRoot(async root => {
  const payload = { omr_hist_v1: '[1]' };
  const r = await saveSnapshot(root, 'teacher-1', payload);
  assert.equal(r.skipped, false);
  const files = (await fs.readdir(path.join(root, 'teachers', 'teacher-1'))).filter(name => name.endsWith('.json.gz'));
  assert.equal(files.length, 1);
  const saved = await gunzip(await fs.readFile(path.join(root, 'teachers', 'teacher-1', files[0])));
  assert.deepEqual(JSON.parse(saved), payload);
}));

test('사용자 제어 경로를 거부한다', async () => withRoot(async root => {
  await assert.rejects(() => saveSnapshot(root, '../../x', {}), /invalid-payload/);
}));
