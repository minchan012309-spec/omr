// Supabase Edge Function: 토스페이먼츠 결제 승인
// 배포: supabase functions deploy toss-confirm --no-verify-jwt
// 비밀값: supabase secrets set TOSS_SECRET_KEY=test_sk_...   (토스 개발자센터의 시크릿 키. 절대 화면 코드에 넣지 마세요)
// 흐름: 학부모가 토스 결제창에서 결제 → 앱으로 돌아오면 paymentKey·orderId·amount 와 함께 이 함수를 호출
//       → 금액을 DB 의 청구 금액과 대조 → 토스 승인 API 호출 → 성공하면 수납 완료로 기록
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.45.4';

const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, apikey, content-type', 'Content-Type': 'application/json' };
const sb = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, { auth: { persistSession: false } });
const json = (o: unknown, s = 200) => new Response(JSON.stringify(o), { status: s, headers: cors });

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  try {
    const { login, pw, feeId, paymentKey, orderId, amount } = await req.json();
    const secret = Deno.env.get('TOSS_SECRET_KEY');
    if (!secret) return json({ ok: false, err: 'TOSS_SECRET_KEY 가 설정되지 않았어요' }, 500);
    const who = await sb.rpc('_pa_auth_row', { p_login: login, p_pw: pw });
    if (!who.data) return json({ ok: false, err: '로그인 정보를 확인할 수 없어요' }, 401);
    const due = await sb.rpc('fee_amount', { p_fee: feeId, p_student: who.data.student_id });
    if (due.data == null || Number(due.data) !== Number(amount)) return json({ ok: false, err: '결제 금액이 청구 금액과 달라요' }, 400);
    const r = await fetch('https://api.tosspayments.com/v1/payments/confirm', {
      method: 'POST',
      headers: { Authorization: 'Basic ' + btoa(secret + ':'), 'Content-Type': 'application/json' },
      body: JSON.stringify({ paymentKey, orderId, amount: Number(amount) }),
    });
    const j = await r.json();
    if (!r.ok) return json({ ok: false, err: j.message || '토스 승인에 실패했어요', code: j.code }, 400);
    await sb.rpc('fee_mark_paid', { p_fee: feeId, p_student: who.data.student_id, p_key: paymentKey, p_method: '토스(' + (j.method || '') + ')' });
    return json({ ok: true });
  } catch (e) {
    return json({ ok: false, err: String((e as Error).message || e) }, 500);
  }
});
