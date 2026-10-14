// Supabase Edge Function: 패스키 등록·로그인
// 배포: supabase functions deploy passkey
// 비밀값(선택): supabase secrets set SITE_URL=https://ssolvi.kro.kr  (패스키를 쓰는 사이트 주소, 경로 제외)
// 설정하지 않으면 기본값 https://ssolvi.kro.kr 을 씁니다. 도메인을 바꾸면 SITE_URL 비밀값을 바꾸세요.
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.45.4';
import * as swa from 'https://esm.sh/@simplewebauthn/server@10.0.1';
import { makeHandler } from './handler.js';

const DEFAULT_SITE = 'https://ssolvi.kro.kr';
const SITE = (Deno.env.get('SITE_URL') || DEFAULT_SITE).replace(/\/+$/, '');
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
    out['SITE_URL'] = SITE + (Deno.env.get('SITE_URL') ? '' : ' (기본값 사용 중)');
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
