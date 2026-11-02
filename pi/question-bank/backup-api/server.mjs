import http from 'node:http';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import zlib from 'node:zlib';
import { promisify } from 'node:util';

const gzip = promisify(zlib.gzip);
const MAX_BODY = 8 * 1024 * 1024;
const safeId = id => /^[a-zA-Z0-9-]{1,128}$/.test(id) ? id : null;
const send = (res, status, body, origin) => {
  const json = JSON.stringify(body);
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'content-length': Buffer.byteLength(json), ...(origin ? { 'access-control-allow-origin': origin, vary: 'Origin' } : {}) });
  res.end(json);
};
const readBody = req => new Promise((resolve, reject) => {
  let size = 0, chunks = [];
  req.on('data', part => { size += part.length; if (size > MAX_BODY) { reject(new Error('too-large')); req.destroy(); } else chunks.push(part); });
  req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
  req.on('error', reject);
});

async function defaultVerify(token) {
  const base = String(process.env.SUPABASE_URL || '').replace(/\/$/, '');
  const key = process.env.SUPABASE_ANON_KEY;
  if (!base || !key || !token) return null;
  const headers = { apikey: key, authorization: 'Bearer ' + token };
  const userRes = await fetch(base + '/auth/v1/user', { headers });
  if (!userRes.ok) return null;
  const user = await userRes.json();
  if (!safeId(user.id)) return null;
  const roleRes = await fetch(base + '/rest/v1/teacher_settings?select=user_id&user_id=eq.' + encodeURIComponent(user.id), { headers });
  if (!roleRes.ok) return null;
  const rows = await roleRes.json();
  return rows.some(row => row.user_id === user.id) ? { id: user.id, teacher: true } : null;
}

async function prune(dir) {
  const files = (await fs.readdir(dir, { withFileTypes: true })).filter(f => f.isFile() && /^\d{4}-\d\d-\d\dT[\d.-]+Z\.json\.gz$/.test(f.name));
  const now = Date.now();
  const records = [];
  for (const file of files) { const stat = await fs.stat(path.join(dir, file.name)); records.push({ name: file.name, time: stat.mtimeMs, size: stat.size }); }
  records.sort((a, b) => b.time - a.time);
  const keepDays = new Set(), remove = [];
  for (const f of records) {
    const age = now - f.time, day = new Date(f.time).toISOString().slice(0, 10);
    if (age > 30 * 864e5 || (age > 864e5 && keepDays.has(day))) remove.push(f);
    else keepDays.add(day);
  }
  let total = records.filter(f => !remove.includes(f)).reduce((n, f) => n + f.size, 0);
  for (const f of [...records].reverse()) if (total > 256 * 1024 * 1024 && !remove.includes(f)) { remove.push(f); total -= f.size; }
  await Promise.all(remove.map(f => fs.rm(path.join(dir, f.name), { force: true })));
}

export async function saveSnapshot(backupRoot, userId, payload, expectedDigest = '') {
  if (!safeId(userId) || !payload || typeof payload !== 'object' || Array.isArray(payload)) throw new Error('invalid-payload');
  const raw = JSON.stringify(payload), digest = crypto.createHash('sha256').update(raw).digest('hex');
  if (expectedDigest && expectedDigest !== digest) throw new Error('digest-mismatch');
  const dir = path.join(backupRoot, 'teachers', userId);
  await fs.mkdir(dir, { recursive: true, mode: 0o700 });
  const marker = path.join(dir, '.last-digest');
  try { if ((await fs.readFile(marker, 'utf8')) === digest) return { savedAt: null, skipped: true }; } catch {}
  const stamp = new Date().toISOString().replace(/:/g, '-');
  const dest = path.join(dir, stamp + '.json.gz');
  await fs.writeFile(dest + '.tmp', await gzip(raw), { mode: 0o600 });
  await fs.rename(dest + '.tmp', dest);
  await fs.writeFile(marker, digest, { mode: 0o600 });
  await prune(dir);
  return { savedAt: new Date().toISOString(), skipped: false };
}

export function createBackupServer(options = {}) {
  const backupRoot = options.backupRoot || process.env.BACKUP_ROOT || '/backups';
  const allowedOrigins = options.allowedOrigins || String(process.env.ALLOWED_ORIGINS || 'https://solvi.win').split(',').map(x => x.trim());
  const verifyToken = options.verifyToken || defaultVerify;
  return http.createServer(async (req, res) => {
    const origin = allowedOrigins.includes(req.headers.origin) ? req.headers.origin : '';
    if (req.method === 'OPTIONS') { res.writeHead(origin ? 204 : 403, origin ? { 'access-control-allow-origin': origin, 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'Authorization, Content-Type', vary: 'Origin' } : {}); return res.end(); }
    if (req.method !== 'POST' || req.url !== '/api/backups') return send(res, 404, { error: 'not-found' }, origin);
    const token = String(req.headers.authorization || '').replace(/^Bearer\s+/i, '');
    let account;
    try { account = await verifyToken(token); } catch { account = null; }
    if (!account || !account.teacher || !safeId(account.id)) { req.resume(); return send(res, 401, { error: 'unauthorized' }, origin); }
    let data;
    try { data = JSON.parse(await readBody(req)); } catch (error) { return send(res, error.message === 'too-large' ? 413 : 400, { error: 'invalid-body' }, origin); }
    try { const saved = await saveSnapshot(backupRoot, account.id, data.payload, data.digest); return send(res, saved.skipped ? 200 : 201, saved, origin); }
    catch (error) { return send(res, 400, { error: error.message === 'digest-mismatch' ? 'digest-mismatch' : 'invalid-payload' }, origin); }
  });
}

if (import.meta.url === `file://${process.argv[1]}`) createBackupServer().listen(Number(process.env.PORT || 3000), '0.0.0.0');
