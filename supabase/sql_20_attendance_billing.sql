-- =====================================================================
-- 20. 출결 · 학부모 안내문 · 수납 관리 (토스페이먼츠 연동 준비 포함)
-- Supabase 대시보드 > SQL Editor 에 통째로 붙여넣고 Run. 이미 실행했어도 다시 실행해도 됩니다.
-- (sql_16_parent.sql 이 먼저 실행되어 있어야 해요)
-- =====================================================================
create extension if not exists pgcrypto with schema extensions;

-- 20-1) 학생 연락처·출결 번호 (출결 번호 기본값은 앱이 전화번호 일부로 채워 줘요)
alter table students add column if not exists phone text;
alter table students add column if not exists att_pin text;

-- 20-2) 출결 기록 (하루에 학생당 1줄)
create table if not exists attendance (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  day        date not null,
  status     text not null default 'in' check (status in ('in','late','absent','excused')),
  t_in       timestamptz,
  t_out      timestamptz,
  memo       text,
  unique (student_id, day)
);
create index if not exists attendance_user_day on attendance (user_id, day);
alter table attendance enable row level security;
drop policy if exists "att all" on attendance;
create policy "att all" on attendance for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- 20-3) 출결 단말(태블릿)에서 번호를 입력하면 등원 → 같은 날 다시 입력하면 하원으로 기록 (선생님 계정으로 로그인한 단말에서 호출)
create or replace function att_checkin(p_pin text, p_student uuid default null) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare c int; s students%rowtype; a attendance%rowtype; d date := (now() at time zone 'Asia/Seoul')::date; kind text;
begin
  if auth.uid() is null then raise exception 'not allowed'; end if;
  if length(coalesce(trim(p_pin), '')) < 3 then return json_build_object('ok', false, 'err', 'pin'); end if;
  select count(*) into c from students where user_id = auth.uid() and att_pin = trim(p_pin) and (p_student is null or id = p_student);
  if c = 0 then return json_build_object('ok', false, 'err', 'pin'); end if;
  if c > 1 then
    return json_build_object('ok', false, 'err', 'choose', 'choose',
      (select json_agg(json_build_object('id', id, 'name', name, 'grade', grade)) from students where user_id = auth.uid() and att_pin = trim(p_pin)));
  end if;
  select * into s from students where user_id = auth.uid() and att_pin = trim(p_pin) and (p_student is null or id = p_student);
  select * into a from attendance where student_id = s.id and day = d;
  if not found or a.t_in is null then
    insert into attendance (user_id, student_id, day, status, t_in) values (auth.uid(), s.id, d, 'in', now())
      on conflict (student_id, day) do update set t_in = now(), status = case when attendance.status in ('absent','excused') then 'in' else attendance.status end;
    kind := 'in';
  elsif a.t_out is null and now() - a.t_in > interval '10 minutes' then
    update attendance set t_out = now() where id = a.id;
    kind := 'out';
  else
    kind := 'dup';
  end if;
  return json_build_object('ok', true, 'kind', kind, 'name', s.name, 'grade', s.grade, 't', now());
end $$;
grant execute on function att_checkin(text, uuid) to authenticated;

-- 20-4) 학부모 안내문 (student_id 가 비어 있으면 모든 학부모에게)
create table if not exists parent_notices (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  student_id uuid references students(id) on delete cascade,
  title      text not null,
  body       text not null default '',
  created_at timestamptz not null default now()
);
create index if not exists parent_notices_user on parent_notices (user_id, created_at desc);
alter table parent_notices enable row level security;
drop policy if exists "pn all" on parent_notices;
create policy "pn all" on parent_notices for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- 20-5) 수납(학원비·교재비 등)
create table if not exists fees (
  id          bigint generated always as identity primary key,
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  student_id  uuid not null references students(id) on delete cascade,
  kind        text not null default 'tuition',          -- tuition(학원비) · book(교재비) · etc
  title       text not null,
  amount      integer not null check (amount >= 0),
  due         date,
  paid_amount integer not null default 0,
  paid_at     timestamptz,
  method      text,                                      -- 현금 · 계좌이체 · 카드 · 토스 · 데모
  pay_key     text,                                      -- 토스 paymentKey
  memo        text,
  created_at  timestamptz not null default now()
);
create index if not exists fees_user on fees (user_id, due);
create index if not exists fees_student on fees (student_id);
alter table fees enable row level security;
drop policy if exists "fees all" on fees;
create policy "fees all" on fees for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- 20-6) 학부모 화면용 조회 (읽기 전용)
create or replace function pa_attendance(p_login text, p_pw text, p_from date, p_to date) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  return (select coalesce(json_agg(json_build_object('day', x.day, 'status', x.status, 't_in', x.t_in, 't_out', x.t_out, 'memo', x.memo) order by x.day), '[]'::json)
          from attendance x where x.student_id = a.student_id and x.day between p_from and p_to);
end $$;
create or replace function pa_notices(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  return (select coalesce(json_agg(json_build_object('id', n.id, 'title', n.title, 'body', n.body, 't', n.created_at) order by n.created_at desc), '[]'::json)
          from (select * from parent_notices where user_id = a.user_id and (student_id is null or student_id = a.student_id) order by created_at desc limit 60) n);
end $$;
create or replace function pa_fees(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; pay jsonb;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  select coalesce(data->'pay', '{}'::jsonb) into pay from teacher_settings where user_id = a.user_id;
  return json_build_object(
    'pay', json_build_object('demo', coalesce((pay->>'demo')::boolean, false), 'clientKey', coalesce(pay->>'clientKey', ''), 'bank', coalesce(pay->>'bank', '')),
    'fees', (select coalesce(json_agg(json_build_object('id', f.id, 'kind', f.kind, 'title', f.title, 'amount', f.amount, 'due', f.due, 'paid_amount', f.paid_amount, 'paid_at', f.paid_at, 'method', f.method) order by f.due desc nulls last, f.id desc), '[]'::json)
             from fees f where f.student_id = a.student_id));
end $$;
-- 데모 결제: 선생님이 「데모 결제 허용」을 켠 경우에만 동작해요 (실제 돈은 오가지 않아요)
create or replace function pa_fee_demo_pay(p_login text, p_pw text, p_fee bigint) returns boolean
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; ok boolean;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return false; end if;
  select coalesce((data->'pay'->>'demo')::boolean, false) into ok from teacher_settings where user_id = a.user_id;
  if not coalesce(ok, false) then return false; end if;
  update fees set paid_amount = amount, paid_at = now(), method = '데모 결제' where id = p_fee and student_id = a.student_id and paid_amount < amount;
  return found;
end $$;
-- 토스 결제 승인 확인 후 Edge Function(toss-confirm)이 서비스 키로만 호출해요
create or replace function _pa_auth_row(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  return json_build_object('id', a.id, 'student_id', a.student_id, 'user_id', a.user_id);
end $$;
revoke all on function _pa_auth_row(text, text) from public, anon, authenticated;
grant execute on function _pa_auth_row(text, text) to service_role;
create or replace function fee_mark_paid(p_fee bigint, p_student uuid, p_key text, p_method text) returns boolean
language plpgsql security definer set search_path = public, extensions as $$
begin
  update fees set paid_amount = amount, paid_at = now(), method = coalesce(p_method, '토스'), pay_key = p_key where id = p_fee and student_id = p_student and paid_amount < amount;
  return found;
end $$;
revoke all on function fee_mark_paid(bigint, uuid, text, text) from public, anon, authenticated;
grant execute on function fee_mark_paid(bigint, uuid, text, text) to service_role;
create or replace function fee_amount(p_fee bigint, p_student uuid) returns integer
language sql security definer set search_path = public as $$ select amount from fees where id = p_fee and student_id = p_student $$;
revoke all on function fee_amount(bigint, uuid) from public, anon, authenticated;
grant execute on function fee_amount(bigint, uuid) to service_role;

grant execute on function pa_attendance(text, text, date, date) to anon, authenticated;
grant execute on function pa_notices(text, text) to anon, authenticated;
grant execute on function pa_fees(text, text) to anon, authenticated;
grant execute on function pa_fee_demo_pay(text, text, bigint) to anon, authenticated;
