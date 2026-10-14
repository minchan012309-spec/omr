// 대시보드에서 한 파일로 붙여 넣어 배포하는 버전입니다 (handler.js + index.ts를 합친 것).
// 수정할 때는 handler.js와 index.ts를 고친 뒤 이 파일을 다시 만들어 주세요.
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.45.4';
import * as swa from 'https://esm.sh/@simplewebauthn/server@10.0.1';

// Solvi 패스키(WebAuthn) 처리기. Supabase Edge Function(index.ts)과 로컬 테스트에서 같이 씁니다.
// 외부 의존성은 모두 인자로 받습니다: swa(@simplewebauthn/server), db(저장소), cfg.
const enc = new TextEncoder();
const b64uToBytes = (s) => {
  s = String(s).replace(/-/g, '+').replace(/_/g, '/');
  while (s.length % 4) s += '=';
  const bin = atob(s); const u = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return u;
};
const bytesToB64u = (u) => {
  let s = ''; for (const b of u) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
};
const fail = (status, error) => ({ status, json: { error } });
const CHALLENGE_TTL_MS = 5 * 60 * 1000;

function makeHandler({ swa, db, cfg }) {
  // cfg: { rpID, rpName, origins: [..] }
  const subjectOf = async (body, user) => {
    if (body.who === 'teacher') {
      if (!user) return null;
      return { kind: 'teacher', id: user.id, name: user.email || '선생님', label: user.email || '선생님' };
    }
    if (body.who === 'student') {
      const s = await db.studentByAuth(String(body.login || ''), String(body.secret || ''));
      if (!s) return null;
      return { kind: 'student', id: s.id, name: s.login, label: s.name || s.login };
    }
    return null;
  };
  const ownerCol = (sub) => (sub.kind === 'teacher' ? { user_id: sub.id } : { student_id: sub.id });

  async function handle(body, user) {
    const action = body && body.action;
    if (action === 'ping') {
      const info = await db.ping();
      return { status: 200, json: { ok: true, rpID: cfg.rpID, origins: cfg.origins, ...info } };
    }
    if (action === 'reg-options') {
      const sub = await subjectOf(body, user);
      if (!sub) return fail(401, 'unauthorized');
      const existing = await db.listPasskeys(ownerCol(sub));
      const options = await swa.generateRegistrationOptions({
        rpName: cfg.rpName, rpID: cfg.rpID,
        userID: enc.encode(sub.kind + ':' + sub.id), userName: sub.name, userDisplayName: sub.label,
        attestationType: 'none',
        authenticatorSelection: { residentKey: 'required', userVerification: 'preferred' },
        excludeCredentials: existing.map((p) => ({ id: p.credential_id, transports: p.transports || undefined })),
      });
      const cid = await db.saveChallenge({ challenge: options.challenge, purpose: 'reg', subject: sub.kind + ':' + sub.id });
      return { status: 200, json: { options, cid } };
    }
    if (action === 'reg-verify') {
      const sub = await subjectOf(body, user);
      if (!sub) return fail(401, 'unauthorized');
      const ch = await db.takeChallenge(body.cid);
      if (!ch || ch.purpose !== 'reg' || ch.subject !== sub.kind + ':' + sub.id || Date.now() - ch.t > CHALLENGE_TTL_MS) return fail(400, 'challenge expired');
      let v;
      try {
        v = await swa.verifyRegistrationResponse({ response: body.credential, expectedChallenge: ch.challenge, expectedOrigin: cfg.origins, expectedRPID: cfg.rpID, requireUserVerification: false });
      } catch (e) { return fail(400, 'verify failed: ' + e.message); }
      if (!v.verified || !v.registrationInfo) return fail(400, 'not verified');
      const r = v.registrationInfo;
      await db.insertPasskey({ ...ownerCol(sub), credential_id: r.credentialID, public_key: bytesToB64u(r.credentialPublicKey), counter: r.counter, transports: (body.credential.response && body.credential.response.transports) || null, label: String(body.label || '').slice(0, 40) || null });
      return { status: 200, json: { ok: true } };
    }
    if (action === 'login-options') {
      const options = await swa.generateAuthenticationOptions({ rpID: cfg.rpID, userVerification: 'preferred' });
      const cid = await db.saveChallenge({ challenge: options.challenge, purpose: 'auth', subject: '' });
      return { status: 200, json: { options, cid } };
    }
    if (action === 'login-verify') {
      const ch = await db.takeChallenge(body.cid);
      if (!ch || ch.purpose !== 'auth' || Date.now() - ch.t > CHALLENGE_TTL_MS) return fail(400, 'challenge expired');
      const cred = body.credential || {};
      const pk = await db.getPasskeyByCred(cred.id);
      if (!pk) return fail(401, 'unknown credential');
      let v;
      try {
        v = await swa.verifyAuthenticationResponse({
          response: cred, expectedChallenge: ch.challenge, expectedOrigin: cfg.origins, expectedRPID: cfg.rpID, requireUserVerification: false,
          authenticator: { credentialID: b64uToBytes(pk.credential_id), credentialPublicKey: b64uToBytes(pk.public_key), counter: Number(pk.counter) || 0, transports: pk.transports || undefined },
        });
      } catch (e) { return fail(401, 'verify failed: ' + e.message); }
      if (!v.verified) return fail(401, 'not verified');
      await db.updateCounter(pk.id, v.authenticationInfo.newCounter);
      if (pk.user_id) {
        const link = await db.teacherLink(pk.user_id);
        if (!link) return fail(500, 'could not create session');
        return { status: 200, json: { kind: 'teacher', token_hash: link.token_hash, email: link.email } };
      }
      const st = await db.getStudent(pk.student_id);
      if (!st || !st.login) return fail(401, 'student login disabled');
      const token = await db.issueStudentToken(st.id);
      return { status: 200, json: { kind: 'student', login: st.login, token, name: st.name } };
    }
    if (action === 'list') {
      const sub = await subjectOf(body, user);
      if (!sub) return fail(401, 'unauthorized');
      const rows = await db.listPasskeys(ownerCol(sub));
      return { status: 200, json: { items: rows.map((p) => ({ id: p.id, label: p.label, created_at: p.created_at })) } };
    }
    if (action === 'remove') {
      const sub = await subjectOf(body, user);
      if (!sub) return fail(401, 'unauthorized');
      await db.deletePasskey(body.id, ownerCol(sub));
      return { status: 200, json: { ok: true } };
    }
    return fail(400, 'unknown action');
  }
  return { handle };
}

// Supabase Edge Function: 패스키 등록·로그인
// 배포: supabase functions deploy passkey
// 비밀값: supabase secrets set SITE_URL=https://<아이디>.github.io  (패스키를 쓰는 사이트 주소, 경로 제외)

const SITE = (Deno.env.get('SITE_URL') || '').replace(/\/+$/, '');
const sb = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, { auth: { persistSession: false } });
const cfg = { rpID: SITE ? new URL(SITE).hostname : 'localhost', rpName: 'Solvi', origins: SITE ? [SITE] : ['http://localhost:8765'] };

const sha256hex = async (s: string) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))).map((b) => b.toString(16).padStart(2, '0')).join('');
const randToken = () => { const u = crypto.getRandomValues(new Uint8Array(32)); return Array.from(u).map((b) => b.toString(16).padStart(2, '0')).join(''); };

const withTimeout = <T>(p: Promise<T>, ms: number, msg: string): Promise<T> => Promise.race([p, new Promise<T>((_, rej) => setTimeout(() => rej(new Error(msg)), ms))]);

const db = {
  async ping() {
    const out: Record<string, string> = {};
    for (const t of ['passkeys', 'passkey_challenges', 'st_tokens']) {
      try { const { error } = await withTimeout(sb.from(t).select('*', { head: true, count: 'exact' }).limit(1) as unknown as Promise<{ error: { message: string } | null }>, 8000, '시간 초과'); out[t] = error ? '오류: ' + error.message : 'ok'; }
      catch (e) { out[t] = '오류: ' + (e as Error).message; }
    }
    try { const { error } = await withTimeout(sb.rpc('_st_auth_row', { p_login: 'x', p_pw: 'x' }) as unknown as Promise<{ error: { message: string } | null }>, 8000, '시간 초과'); out['_st_auth_row'] = error ? '오류: ' + error.message : 'ok'; }
    catch (e) { out['_st_auth_row'] = '오류: ' + (e as Error).message; }
    out['SITE_URL'] = SITE || '(설정 안 됨)';
    return { checks: out };
  },
  async saveChallenge(c: { challenge: string; purpose: string; subject: string }) {
    const { data, error } = await sb.from('passkey_challenges').insert(c).select('id').single();
    if (error) throw error;
    sb.from('passkey_challenges').delete().lt('created_at', new Date(Date.now() - 3600_000).toISOString()).then(() => {});
    return data.id;
  },
  async takeChallenge(id: string) {
    if (!id) return null;
    const { data } = await sb.from('passkey_challenges').delete().eq('id', id).select('challenge,purpose,subject,created_at').maybeSingle();
    return data ? { challenge: data.challenge, purpose: data.purpose, subject: data.subject, t: new Date(data.created_at).getTime() } : null;
  },
  async listPasskeys(owner: Record<string, string>) {
    const { data } = await sb.from('passkeys').select('id,credential_id,transports,label,created_at').match(owner).order('created_at');
    return data || [];
  },
  async getPasskeyByCred(cid: string) {
    const { data } = await sb.from('passkeys').select('*').eq('credential_id', cid).maybeSingle();
    return data;
  },
  async insertPasskey(row: Record<string, unknown>) {
    const { error } = await sb.from('passkeys').insert(row);
    if (error) throw error;
  },
  async updateCounter(id: number, counter: number) { await sb.from('passkeys').update({ counter, last_used: new Date().toISOString() }).eq('id', id); },
  async deletePasskey(id: number, owner: Record<string, string>) { await sb.from('passkeys').delete().eq('id', id).match(owner); },
  async studentByAuth(login: string, secret: string) {
    const { data } = await sb.rpc('_st_auth_row', { p_login: login, p_pw: secret });
    return data && data.id ? data : null;
  },
  async getStudent(id: string) { const { data } = await sb.from('students').select('id,name,login').eq('id', id).maybeSingle(); return data; },
  async issueStudentToken(studentId: string) {
    const token = randToken();
    await sb.from('st_tokens').insert({ token_hash: await sha256hex(token), student_id: studentId });
    return token;
  },
  async teacherLink(userId: string) {
    const { data: u } = await sb.auth.admin.getUserById(userId);
    const email = u?.user?.email;
    if (!email) return null;
    const { data, error } = await sb.auth.admin.generateLink({ type: 'magiclink', email });
    if (error || !data?.properties?.hashed_token) return null;
    return { token_hash: data.properties.hashed_token, email };
  },
};

const { handle } = makeHandler({ swa, db, cfg });
const cors = { 'Access-Control-Allow-Origin': SITE || '*', 'Access-Control-Allow-Headers': 'authorization, apikey, content-type, x-client-info', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Vary': 'Origin' };

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  try {
    const body = await req.json();
    let user = null;
    const jwt = (req.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
    if (jwt) { const { data } = await withTimeout(sb.auth.getUser(jwt), 8000, '로그인 확인 시간 초과'); user = data?.user ? { id: data.user.id, email: data.user.email } : null; }
    const r = await withTimeout(handle(body, user), 20000, '서버 안에서 20초 넘게 기다렸어요 (DB 연결 확인)');
    return new Response(JSON.stringify(r.json), { status: r.status, headers: { ...cors, 'Content-Type': 'application/json' } });
  } catch (e) {
    return new Response(JSON.stringify({ error: String((e as Error).message || e) }), { status: 500, headers: { ...cors, 'Content-Type': 'application/json' } });
  }
});
