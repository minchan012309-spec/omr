-- Supabase 대시보드 > SQL Editor 에 통째로 붙여넣고 Run.
-- 이미 이전 버전을 실행했어도 다시 실행해도 됩니다(기존 데이터는 그대로).
-- 이 파일 하나에 1) 학생 ~ 24) 학원 운영·권한·업무·예약·휴강/대체까지 모든 표 · 함수 · 권한이 순서대로 들어 있어요.
-- supabase/sql_13 ~ sql_24 파일은 예전에 일부만 실행하던 분을 위한 조각이고, 내용은 모두 이 파일에 포함돼 있어요.

-- 1) 학생
create table if not exists students (
  id      uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  name    text not null,
  grade   text,
  memo    text,
  t       bigint not null default (extract(epoch from now()) * 1000)::bigint
);
alter table students enable row level security;
drop policy if exists "stu select" on students;
drop policy if exists "stu insert" on students;
drop policy if exists "stu update" on students;
drop policy if exists "stu delete" on students;
create policy "stu select" on students for select using (auth.uid() = user_id);
create policy "stu insert" on students for insert with check (auth.uid() = user_id);
create policy "stu update" on students for update using (auth.uid() = user_id);
create policy "stu delete" on students for delete using (auth.uid() = user_id);

-- 2) 채점 기록
create table if not exists attempts (
  id      bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  t       bigint not null,
  "set"   text,
  sub     text,
  items   jsonb not null
);
alter table attempts add column if not exists student_id uuid references students(id) on delete set null;
alter table attempts enable row level security;
drop policy if exists "own select" on attempts;
drop policy if exists "own insert" on attempts;
drop policy if exists "own delete" on attempts;
create policy "own select" on attempts for select using (auth.uid() = user_id);
create policy "own insert" on attempts for insert with check (auth.uid() = user_id);
create policy "own delete" on attempts for delete using (auth.uid() = user_id);

-- 3) 학습지
create table if not exists worksheets (
  id      bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  wid     text not null,
  t       bigint not null,
  title   text,
  meta    jsonb not null,
  unique (user_id, wid)
);
alter table worksheets add column if not exists student_id uuid references students(id) on delete set null;
create unique index if not exists worksheets_wid_key on worksheets (wid);
alter table worksheets enable row level security;
drop policy if exists "ws select" on worksheets;
drop policy if exists "ws insert" on worksheets;
drop policy if exists "ws update" on worksheets;
drop policy if exists "ws delete" on worksheets;
create policy "ws select" on worksheets for select using (auth.uid() = user_id);
create policy "ws insert" on worksheets for insert with check (auth.uid() = user_id);
create policy "ws update" on worksheets for update using (auth.uid() = user_id);
create policy "ws delete" on worksheets for delete using (auth.uid() = user_id);

-- 4) 학생(비로그인)이 학습지 번호로 문제를 받고 답을 제출하는 함수
--    번호를 아는 사람만 해당 학습지의 문항 목록을 보고, 그 학습지에 한해 결과를 올릴 수 있습니다.
create or replace function ws_get(p_wid text) returns json
language sql security definer set search_path = public as $$
  select json_build_object('title', w.title, 'meta', w.meta, 'student', s.name,
    'submitted', (w.student_id is not null and exists (select 1 from attempts a where a.student_id = w.student_id and a."set" = 'ws' and a.sub = w.wid and a.t > coalesce((w.meta->>'resetAt')::bigint, 0))))
  from worksheets w left join students s on s.id = w.student_id
  where w.wid = upper(p_wid) limit 1
$$;
create or replace function ws_submit(p_wid text, p_t bigint, p_items jsonb) returns void
language plpgsql security definer set search_path = public as $$
declare w worksheets%rowtype;
begin
  select * into w from worksheets where wid = upper(p_wid) limit 1;
  if not found then raise exception 'worksheet not found'; end if;
  if w.student_id is not null and exists (select 1 from attempts a where a.student_id = w.student_id and a."set" = 'ws' and a.sub = w.wid and a.t > coalesce((w.meta->>'resetAt')::bigint, 0)) then
    raise exception 'already submitted';
  end if;
  insert into attempts (user_id, student_id, t, "set", sub, items)
  values (w.user_id, w.student_id, p_t, 'ws', w.wid, p_items);
end $$;
grant execute on function ws_get(text) to anon, authenticated;
grant execute on function ws_submit(text, bigint, jsonb) to anon, authenticated;

-- 5) 학생 로그인 계정 (선생님이 아이디/비밀번호를 발급)
create extension if not exists pgcrypto with schema extensions;
alter table students add column if not exists login text;
alter table students add column if not exists pw_hash text;
create unique index if not exists students_login_key on students (lower(login)) where login is not null;

-- 6) 과제 배정
create table if not exists assignments (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  wid        text not null,
  title      text,
  due        text,
  note       text,
  t          bigint not null default (extract(epoch from now()) * 1000)::bigint
);
alter table assignments enable row level security;
drop policy if exists "as select" on assignments;
drop policy if exists "as insert" on assignments;
drop policy if exists "as update" on assignments;
drop policy if exists "as delete" on assignments;
create policy "as select" on assignments for select using (auth.uid() = user_id);
create policy "as insert" on assignments for insert with check (auth.uid() = user_id);
create policy "as update" on assignments for update using (auth.uid() = user_id);
create policy "as delete" on assignments for delete using (auth.uid() = user_id);

-- 7) 계정 발급·해제 (선생님만)
create or replace function issue_login(p_student uuid, p_login text, p_pw text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not exists (select 1 from students where id = p_student and user_id = auth.uid()) then
    raise exception 'not allowed';
  end if;
  if length(coalesce(p_pw,'')) < 4 then raise exception 'password too short'; end if;
  if length(coalesce(p_login,'')) < 3 then raise exception 'login too short'; end if;
  update students set login = lower(trim(p_login)), pw_hash = crypt(p_pw, gen_salt('bf')) where id = p_student;
end $$;
create or replace function revoke_login(p_student uuid) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  update students set login = null, pw_hash = null where id = p_student and user_id = auth.uid();
end $$;
grant execute on function issue_login(uuid, text, text) to authenticated;
grant execute on function revoke_login(uuid) to authenticated;

-- 8) 학생이 아이디/비밀번호로 쓰는 함수 (로그인 없이 호출, 비밀번호가 맞아야 동작)
create or replace function _st_auth(p_login text, p_pw text) returns students
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  select * into s from students where login = lower(trim(p_login)) and pw_hash is not null and pw_hash = crypt(p_pw, pw_hash) limit 1;
  if not found then return null; end if;
  return s;
end $$;
create or replace function st_login(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return json_build_object('id', s.id, 'name', s.name, 'grade', s.grade);
end $$;
create or replace function st_data(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return json_build_object(
    'student', json_build_object('id', s.id, 'name', s.name, 'grade', s.grade),
    'attempts', (select coalesce(json_agg(json_build_object('t', a.t, 'set', a."set", 'sub', a.sub, 'items', a.items) order by a.t), '[]'::json)
                 from (select * from attempts where student_id = s.id order by t desc limit 400) a),
    'assignments', (select coalesce(json_agg(json_build_object('wid', x.wid, 'title', x.title, 'due', x.due, 'note', x.note, 't', x.t) order by x.t desc), '[]'::json)
                    from assignments x where x.student_id = s.id));
end $$;
create or replace function st_submit(p_login text, p_pw text, p_t bigint, p_set text, p_sub text, p_items jsonb) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then raise exception 'login failed'; end if;
  insert into attempts (user_id, student_id, t, "set", sub, items) values (s.user_id, s.id, p_t, p_set, p_sub, p_items);
end $$;
revoke all on function _st_auth(text, text) from public, anon, authenticated;
grant execute on function st_login(text, text) to anon, authenticated;
grant execute on function st_data(text, text) to anon, authenticated;
grant execute on function st_submit(text, text, bigint, text, text, jsonb) to anon, authenticated;

-- 9) 채점 결과 고정: 한 번 제출한 채점은 선생님이 초기화하기 전까지 다시 제출할 수 없습니다 (서버에서도 막습니다)
alter table attempts add column if not exists rng text;
drop function if exists st_submit(text, text, bigint, text, text, jsonb);
create or replace function st_submit(p_login text, p_pw text, p_t bigint, p_set text, p_sub text, p_items jsonb, p_rng text default null) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype; ra bigint := 0;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then raise exception 'login failed'; end if;
  if p_set = 'ws' then
    select coalesce((meta->>'resetAt')::bigint, 0) into ra from worksheets where wid = upper(p_sub) limit 1;
  end if;
  if exists (select 1 from attempts a where a.student_id = s.id and a."set" = p_set and a.sub = p_sub
             and a.t > ra and coalesce(a.rng, '') = coalesce(p_rng, '')) then
    raise exception 'already submitted';
  end if;
  insert into attempts (user_id, student_id, t, "set", sub, items, rng) values (s.user_id, s.id, p_t, p_set, p_sub, p_items, p_rng);
end $$;
grant execute on function st_submit(text, text, bigint, text, text, jsonb, text) to anon, authenticated;
create or replace function st_data(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return json_build_object(
    'student', json_build_object('id', s.id, 'name', s.name, 'grade', s.grade),
    'attempts', (select coalesce(json_agg(json_build_object('t', a.t, 'set', a."set", 'sub', a.sub, 'items', a.items, 'rng', a.rng) order by a.t), '[]'::json)
                 from (select * from attempts where student_id = s.id order by t desc limit 400) a),
    'assignments', (select coalesce(json_agg(json_build_object('wid', x.wid, 'title', x.title, 'due', x.due, 'note', x.note, 't', x.t) order by x.t desc), '[]'::json)
                    from assignments x where x.student_id = s.id));
end $$;

-- 10) 패스키 로그인 · 자동 로그인 토큰 (Edge Function `passkey`가 사용합니다)
create table if not exists passkeys (
  id            bigint generated always as identity primary key,
  user_id       uuid references auth.users(id) on delete cascade,
  student_id    uuid references students(id) on delete cascade,
  credential_id text not null unique,
  public_key    text not null,
  counter       bigint not null default 0,
  transports    text[],
  label         text,
  created_at    timestamptz not null default now(),
  last_used     timestamptz,
  check ((user_id is null) <> (student_id is null))
);
create table if not exists passkey_challenges (
  id         uuid primary key default gen_random_uuid(),
  challenge  text not null,
  purpose    text not null,
  subject    text not null default '',
  created_at timestamptz not null default now()
);
create table if not exists st_tokens (
  token_hash text primary key,
  student_id uuid not null references students(id) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default now() + interval '90 days'
);
-- 정책을 만들지 않으면 일반 사용자는 접근할 수 없고, 서비스 키(Edge Function)만 읽고 쓸 수 있습니다.
alter table passkeys enable row level security;
alter table passkey_challenges enable row level security;
alter table st_tokens enable row level security;

-- 학생 인증: 비밀번호 대신 「tok:<토큰>」을 넘기면 자동 로그인 토큰으로 확인합니다.
create or replace function _st_auth(p_login text, p_pw text) returns students
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  if p_pw like 'tok:%' then
    select st.* into s from students st join st_tokens t on t.student_id = st.id
      where st.login = lower(trim(p_login)) and st.pw_hash is not null
        and t.token_hash = encode(digest(substr(p_pw, 5), 'sha256'), 'hex') and t.expires_at > now() limit 1;
  else
    select * into s from students where login = lower(trim(p_login)) and pw_hash is not null and pw_hash = crypt(p_pw, pw_hash) limit 1;
  end if;
  if not found then return null; end if;
  return s;
end $$;
revoke all on function _st_auth(text, text) from public, anon, authenticated;

create or replace function _st_auth_row(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return json_build_object('id', s.id, 'name', s.name, 'login', s.login);
end $$;
revoke all on function _st_auth_row(text, text) from public, anon, authenticated;
grant execute on function _st_auth_row(text, text) to service_role;

-- 비밀번호로 로그인한 학생에게 자동 로그인 토큰을 발급 (비밀번호를 기기에 저장하지 않기 위해)
create or replace function st_issue_token(p_login text, p_pw text) returns text
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype; tok text;
begin
  if p_pw like 'tok:%' then return null; end if;
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  tok := encode(gen_random_bytes(32), 'hex');
  insert into st_tokens (token_hash, student_id) values (encode(digest(tok, 'sha256'), 'hex'), s.id);
  delete from st_tokens where student_id = s.id and expires_at < now();
  return tok;
end $$;
create or replace function st_logout(p_login text, p_token text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  delete from st_tokens where token_hash = encode(digest(p_token, 'sha256'), 'hex')
    and student_id in (select id from students where login = lower(trim(p_login)));
end $$;
grant execute on function st_issue_token(text, text) to anon, authenticated;
grant execute on function st_logout(text, text) to anon, authenticated;

-- 비밀번호를 다시 발급하거나 계정을 해제하면 기존 자동 로그인과 패스키도 함께 무효화합니다.
create or replace function issue_login(p_student uuid, p_login text, p_pw text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not exists (select 1 from students where id = p_student and user_id = auth.uid()) then
    raise exception 'not allowed';
  end if;
  if length(coalesce(p_pw,'')) < 4 then raise exception 'password too short'; end if;
  if length(coalesce(p_login,'')) < 3 then raise exception 'login too short'; end if;
  update students set login = lower(trim(p_login)), pw_hash = crypt(p_pw, gen_salt('bf')) where id = p_student;
  delete from st_tokens where student_id = p_student;
end $$;
create or replace function revoke_login(p_student uuid) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  update students set login = null, pw_hash = null where id = p_student and user_id = auth.uid();
  delete from st_tokens where student_id = p_student and exists (select 1 from students where id = p_student and user_id = auth.uid());
  delete from passkeys where student_id = p_student and exists (select 1 from students where id = p_student and user_id = auth.uid());
end $$;

-- 11) 알림: 선생님이 학생에게 공지를 보냅니다 (student_id가 비어 있으면 모든 학생)
create table if not exists notices (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  student_id uuid references students(id) on delete cascade,
  title      text not null,
  body       text not null default '',
  t          bigint not null default (extract(epoch from now()) * 1000)::bigint
);
alter table notices enable row level security;
drop policy if exists "nt select" on notices;
drop policy if exists "nt insert" on notices;
drop policy if exists "nt update" on notices;
drop policy if exists "nt delete" on notices;
create policy "nt select" on notices for select using (auth.uid() = user_id);
create policy "nt insert" on notices for insert with check (auth.uid() = user_id);
create policy "nt update" on notices for update using (auth.uid() = user_id);
create policy "nt delete" on notices for delete using (auth.uid() = user_id);

-- 학생(비로그인)이 아이디/비밀번호(또는 자동 로그인 토큰)로 자기 알림을 읽는 함수
create or replace function st_notices(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return (select coalesce(json_agg(json_build_object('id', n.id, 'title', n.title, 'body', n.body, 't', n.t) order by n.t desc), '[]'::json)
          from (select * from notices where user_id = s.user_id and (student_id is null or student_id = s.id) order by t desc limit 50) n);
end $$;
grant execute on function st_notices(text, text) to anon, authenticated;

-- =====================================================================
-- 12. 교사 설정 (학생 권한)
-- =====================================================================
create table if not exists teacher_settings (
  user_id    uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  data       jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table teacher_settings enable row level security;
drop policy if exists "ts select" on teacher_settings;
drop policy if exists "ts insert" on teacher_settings;
drop policy if exists "ts update" on teacher_settings;
create policy "ts select" on teacher_settings for select using (auth.uid() = user_id);
create policy "ts insert" on teacher_settings for insert with check (auth.uid() = user_id);
create policy "ts update" on teacher_settings for update using (auth.uid() = user_id);

create or replace function st_perms(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return coalesce((select ((data->'perms') - 'logo' - 'logoDark')
      || case when coalesce(data->'perms'->>'logo', '') <> '' or coalesce(data->'perms'->>'logoDark', '') <> ''
              then jsonb_build_object('logov', coalesce(nullif(data->'perms'->>'logov', ''), left(md5(coalesce(data->'perms'->>'logo', '') || coalesce(data->'perms'->>'logoDark', '')), 8)))
              else '{}'::jsonb end
      from teacher_settings where user_id = s.user_id), '{}'::jsonb)::json;
end $$;
grant execute on function st_perms(text, text) to anon, authenticated;

-- 학원 로고(이미지)는 권한 응답과 분리: 버전(logov)이 바뀔 때만 학생이 받아 감
create or replace function st_academy(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype; p jsonb;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  select data->'perms' into p from teacher_settings where user_id = s.user_id;
  return json_build_object('logo', coalesce(p->>'logo', ''), 'logoDark', coalesce(p->>'logoDark', ''), 'v', coalesce(nullif(p->>'logov', ''), left(md5(coalesce(p->>'logo', '') || coalesce(p->>'logoDark', '')), 8)));
end $$;
grant execute on function st_academy(text, text) to anon, authenticated;

-- =====================================================================
-- 13. 버그 신고
-- =====================================================================
create table if not exists bug_reports (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default auth.uid() references auth.users(id) on delete cascade,
  student_id uuid references students(id) on delete set null,
  who        text not null default '',
  msg        text not null,
  info       jsonb not null default '{}'::jsonb,
  t          bigint not null default (extract(epoch from now()) * 1000)::bigint
);
alter table bug_reports enable row level security;
drop policy if exists "bug select" on bug_reports;
drop policy if exists "bug insert" on bug_reports;
drop policy if exists "bug delete" on bug_reports;
create policy "bug select" on bug_reports for select using (auth.uid() = user_id);
create policy "bug insert" on bug_reports for insert with check (auth.uid() = user_id);
create policy "bug delete" on bug_reports for delete using (auth.uid() = user_id);

create or replace function st_bug(p_login text, p_pw text, p_msg text, p_info jsonb) returns boolean
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return false; end if;
  if coalesce(trim(p_msg), '') = '' then return false; end if;
  insert into bug_reports(user_id, student_id, who, msg, info)
  values (s.user_id, s.id, s.name, left(p_msg, 2000), coalesce(p_info, '{}'::jsonb));
  return true;
end $$;
grant execute on function st_bug(text, text, text, jsonb) to anon, authenticated;

-- =====================================================================
-- 14. 학생 가입 신청 · 선생님 승인
-- =====================================================================
create table if not exists teacher_join (
  user_id uuid primary key default auth.uid() references auth.users(id) on delete cascade,
  code    text not null unique,
  open    boolean not null default true
);
alter table teacher_join enable row level security;
drop policy if exists "tj select" on teacher_join;
drop policy if exists "tj update" on teacher_join;
create policy "tj select" on teacher_join for select using (auth.uid() = user_id);
create policy "tj update" on teacher_join for update using (auth.uid() = user_id);

create table if not exists signup_requests (
  id         bigint generated always as identity primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  name       text not null,
  grade      text,
  login      text not null,
  pw_hash    text not null,
  status     text not null default 'pending',
  student_id uuid references students(id) on delete set null,
  t          bigint not null default (extract(epoch from now()) * 1000)::bigint
);
create unique index if not exists signup_pending_login on signup_requests (lower(login)) where status = 'pending';
alter table signup_requests enable row level security;
drop policy if exists "sr select" on signup_requests;
drop policy if exists "sr delete" on signup_requests;
create policy "sr select" on signup_requests for select using (auth.uid() = user_id);
create policy "sr delete" on signup_requests for delete using (auth.uid() = user_id);

-- 선생님: 가입 코드(없으면 만들어 돌려줌), 가입 받기 켜기/끄기
create or replace function join_info() returns json
language plpgsql security definer set search_path = public, extensions as $$
declare r teacher_join%rowtype;
begin
  if auth.uid() is null then raise exception 'not allowed'; end if;
  select * into r from teacher_join where user_id = auth.uid();
  if r.user_id is null then
    insert into teacher_join(user_id, code) values (auth.uid(), upper(substr(translate(encode(gen_random_bytes(9), 'base64'), '+/=lIO01', 'XYZABCDE'), 1, 6)))
    returning * into r;
  end if;
  return json_build_object('code', r.code, 'open', r.open);
end $$;
create or replace function join_open_set(p_open boolean) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  if auth.uid() is null then raise exception 'not allowed'; end if;
  update teacher_join set open = p_open where user_id = auth.uid();
end $$;
grant execute on function join_info() to authenticated;
grant execute on function join_open_set(boolean) to authenticated;

-- 학생(비로그인): 가입 신청
create or replace function st_signup(p_code text, p_name text, p_grade text, p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare t teacher_join%rowtype; lg text := lower(trim(coalesce(p_login, '')));
begin
  select * into t from teacher_join where code = upper(trim(coalesce(p_code, '')));
  if t.user_id is null then return json_build_object('ok', false, 'err', 'bad_code'); end if;
  if not t.open then return json_build_object('ok', false, 'err', 'closed'); end if;
  if lg !~ '^[a-z0-9_]{3,20}$' or length(trim(coalesce(p_name, ''))) not between 1 and 20 or length(coalesce(p_pw, '')) < 4 then
    return json_build_object('ok', false, 'err', 'invalid');
  end if;
  if exists (select 1 from students where lower(login) = lg) or exists (select 1 from signup_requests where lower(login) = lg and status = 'pending') then
    return json_build_object('ok', false, 'err', 'login_taken');
  end if;
  if (select count(*) from signup_requests where user_id = t.user_id and status = 'pending') >= 300 then
    return json_build_object('ok', false, 'err', 'closed');
  end if;
  insert into signup_requests(user_id, name, grade, login, pw_hash)
  values (t.user_id, left(trim(p_name), 20), left(trim(coalesce(p_grade, '')), 20), lg, crypt(p_pw, gen_salt('bf')));
  return json_build_object('ok', true);
end $$;

-- 학생(비로그인): 내 신청 상태 확인 (pending / approved / rejected / none)
create or replace function st_signup_check(p_login text, p_pw text) returns text
language plpgsql security definer set search_path = public, extensions as $$
declare r signup_requests%rowtype; lg text := lower(trim(coalesce(p_login, '')));
begin
  select * into r from signup_requests where lower(login) = lg order by id desc limit 1;
  if r.id is null or r.pw_hash <> crypt(coalesce(p_pw, ''), r.pw_hash) then return 'none'; end if;
  return r.status;
end $$;
grant execute on function st_signup(text, text, text, text, text) to anon, authenticated;
grant execute on function st_signup_check(text, text) to anon, authenticated;

-- 선생님: 승인(학생 + 로그인 계정 생성, 학생에게 알림) / 거절
create or replace function approve_signup(p_id bigint) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare r signup_requests%rowtype; sid uuid;
begin
  select * into r from signup_requests where id = p_id and user_id = auth.uid() and status = 'pending';
  if r.id is null then raise exception 'not allowed'; end if;
  if exists (select 1 from students where lower(login) = lower(r.login)) then raise exception 'login_taken'; end if;
  insert into students(user_id, name, grade, login, pw_hash) values (r.user_id, r.name, nullif(r.grade, ''), lower(r.login), r.pw_hash) returning id into sid;
  update signup_requests set status = 'approved', student_id = sid where id = r.id;
  insert into notices(user_id, student_id, title, body) values (r.user_id, sid, '가입이 승인됐어요', r.name || '님, 이제 로그인해서 학습을 시작할 수 있어요!');
end $$;
create or replace function reject_signup(p_id bigint) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  update signup_requests set status = 'rejected' where id = p_id and user_id = auth.uid() and status = 'pending';
end $$;
grant execute on function approve_signup(bigint) to authenticated;
grant execute on function reject_signup(bigint) to authenticated;

-- =====================================================================
-- 15. 개발자 계정 · 사이트 공지 · 사이트 설정  (supabase/sql_15_developer.sql 과 같은 내용)
-- =====================================================================
-- 15-1) 개발자 명단 (앱에서는 직접 읽거나 쓸 수 없고, 아래 함수로만 확인합니다)
create table if not exists developers (
  user_id  uuid primary key references auth.users(id) on delete cascade,
  email    text,
  added_at timestamptz not null default now()
);
alter table developers enable row level security;

create or replace function is_dev() returns boolean
language sql security definer stable set search_path = public as $$
  select exists (select 1 from developers where user_id = auth.uid())
$$;
grant execute on function is_dev() to anon, authenticated;

-- 15-2) 사이트 공지: 모든 사용자(학생 포함)에게 보이는 공지. 개발자만 쓰고 지움.
create table if not exists site_notices (
  id     bigint generated always as identity primary key,
  title  text not null,
  body   text not null default '',
  tag    text not null default '공지',
  pinned boolean not null default false,
  active boolean not null default true,
  t      bigint not null default (extract(epoch from now()) * 1000)::bigint
);
alter table site_notices enable row level security;
drop policy if exists "sn select" on site_notices;
drop policy if exists "sn insert" on site_notices;
drop policy if exists "sn update" on site_notices;
drop policy if exists "sn delete" on site_notices;
create policy "sn select" on site_notices for select using (active or is_dev());
create policy "sn insert" on site_notices for insert with check (is_dev());
create policy "sn update" on site_notices for update using (is_dev());
create policy "sn delete" on site_notices for delete using (is_dev());
grant select on site_notices to anon, authenticated;
grant insert, update, delete on site_notices to authenticated;

-- 15-3) 사이트 설정(상단 안내 배너, 잠글 과목 등). 누구나 읽고 개발자만 바꿈.
create table if not exists site_config (
  key        text primary key,
  value      jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table site_config enable row level security;
drop policy if exists "sc select" on site_config;
drop policy if exists "sc insert" on site_config;
drop policy if exists "sc update" on site_config;
create policy "sc select" on site_config for select using (true);
create policy "sc insert" on site_config for insert with check (is_dev());
create policy "sc update" on site_config for update using (is_dev());
grant select on site_config to anon, authenticated;
grant insert, update on site_config to authenticated;

-- 15-4) 개발자는 모든 버그 신고를 보고 지울 수 있음
drop policy if exists "bug select dev" on bug_reports;
drop policy if exists "bug delete dev" on bug_reports;
create policy "bug select dev" on bug_reports for select using (is_dev());
create policy "bug delete dev" on bug_reports for delete using (is_dev());

-- 15-5) 사용 현황 · 선생님 계정 목록 (개발자만)
create or replace function dev_stats() returns json
language plpgsql security definer set search_path = public, auth as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  return json_build_object(
    'teachers',   (select count(*) from auth.users),
    'students',   (select count(*) from students),
    'attempts',   (select count(*) from attempts),
    'worksheets', (select count(*) from worksheets),
    'bugs',       (select count(*) from bug_reports),
    'pending',    (select count(*) from signup_requests where status = 'pending')
  );
end $$;
grant execute on function dev_stats() to authenticated;

create or replace function dev_users() returns json
language plpgsql security definer set search_path = public, auth as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  return (select coalesce(json_agg(x order by x.created_at desc), '[]'::json) from (
    select u.id, u.email, u.created_at, u.last_sign_in_at,
           (select count(*) from students s where s.user_id = u.id) as students,
           exists (select 1 from developers d where d.user_id = u.id) as dev,
           (u.banned_until is not null and u.banned_until > now()) as banned
    from auth.users u limit 500) x);
end $$;
grant execute on function dev_users() to authenticated;

-- 15-5b) 문항 관리: 문제·해설·정답·난이도를 고치거나 숨기는 덮어쓰기(원본 파일은 그대로, 앱이 불러올 때 적용)
create table if not exists q_overrides (
  code       text primary key,
  patch      jsonb not null default '{}'::jsonb,
  hidden     boolean not null default false,
  note       text not null default '',
  by_email   text,
  updated_at timestamptz not null default now()
);
alter table q_overrides enable row level security;
drop policy if exists "qo select" on q_overrides;
drop policy if exists "qo insert" on q_overrides;
drop policy if exists "qo update" on q_overrides;
drop policy if exists "qo delete" on q_overrides;
create policy "qo select" on q_overrides for select using (true);
create policy "qo insert" on q_overrides for insert with check (is_dev());
create policy "qo update" on q_overrides for update using (is_dev());
create policy "qo delete" on q_overrides for delete using (is_dev());
grant select on q_overrides to anon, authenticated;
grant insert, update, delete on q_overrides to authenticated;

-- 15-5c) 개발자 활동 기록
create table if not exists dev_log (
  id    bigint generated always as identity primary key,
  who   text,
  act   text not null,
  info  text not null default '',
  t     bigint not null default (extract(epoch from now()) * 1000)::bigint
);
alter table dev_log enable row level security;
drop policy if exists "dl select" on dev_log;
drop policy if exists "dl insert" on dev_log;
create policy "dl select" on dev_log for select using (is_dev());
create policy "dl insert" on dev_log for insert with check (is_dev());
grant select, insert on dev_log to authenticated;

-- 15-5d) 문항 통계: 모든 채점 기록에서 문항별 푼 횟수·정답률 (개발자만)
create or replace function dev_qstats(p_min int default 5) returns json
language plpgsql security definer set search_path = public as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  return (select coalesce(json_agg(x), '[]'::json) from (
    select c as code, count(*) as n, sum(r)::int as right
    from (select (e->>'c') as c, coalesce((e->>'r')::int, 0) as r
          from attempts a, jsonb_array_elements(case when jsonb_typeof(a.items) = 'array' then a.items else '[]'::jsonb end) e) z
    where c is not null group by c having count(*) >= p_min
    order by (sum(r)::float / count(*)) asc, count(*) desc limit 300) x);
end $$;
grant execute on function dev_qstats(int) to authenticated;

-- 15-5e) 개발자 지정·해제, 계정 정지·해제 (개발자만)
create or replace function dev_add(p_email text) returns boolean
language plpgsql security definer set search_path = public, auth as $$
declare u uuid;
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  select id into u from auth.users where lower(email) = lower(p_email);
  if u is null then return false; end if;
  insert into developers(user_id, email) values (u, p_email) on conflict (user_id) do nothing;
  return true;
end $$;
create or replace function dev_remove(p_uid uuid) returns boolean
language plpgsql security definer set search_path = public, auth as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  if p_uid = auth.uid() then return false; end if;
  delete from developers where user_id = p_uid;
  return true;
end $$;
create or replace function dev_ban(p_uid uuid, p_ban boolean) returns boolean
language plpgsql security definer set search_path = public, auth as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  if p_uid = auth.uid() then return false; end if;
  update auth.users set banned_until = case when p_ban then now() + interval '100 years' else null end where id = p_uid;
  return true;
end $$;
grant execute on function dev_add(text), dev_remove(uuid), dev_ban(uuid, boolean) to authenticated;

-- 15-5f) 사이트 공지 확장: 게시 기간, 처음 접속 시 팝업
alter table site_notices add column if not exists start_at bigint;
alter table site_notices add column if not exists end_at   bigint;
alter table site_notices add column if not exists popup    boolean not null default false;

-- 15-5g) 사용 현황: 일별 채점, 학생·채점 목록, 가입 대기, 정리 (개발자만)
create or replace function dev_daily(p_days int default 30) returns json
language plpgsql security definer set search_path = public as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  return (select coalesce(json_agg(x order by x.d), '[]'::json) from (
    select to_char(to_timestamp(a.t / 1000.0) at time zone 'Asia/Seoul', 'YYYY-MM-DD') as d,
           count(*) as n,
           coalesce(sum(jsonb_array_length(case when jsonb_typeof(a.items) = 'array' then a.items else '[]'::jsonb end)), 0) as q,
           count(distinct coalesce(a.student_id::text, a.user_id::text)) as u
    from attempts a
    where a.t >= (extract(epoch from now() - make_interval(days => greatest(p_days, 1))) * 1000)::bigint
    group by 1) x);
end $$;

create or replace function dev_students(p_limit int default 300) returns json
language plpgsql security definer set search_path = public, auth as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  return (select coalesce(json_agg(x), '[]'::json) from (
    select s.id, s.name, s.grade, (s.login is not null) as has_login, u.email as teacher,
           (select count(*) from attempts a where a.student_id = s.id) as attempts,
           (select max(a.t) from attempts a where a.student_id = s.id) as last_t
    from students s left join auth.users u on u.id = s.user_id
    order by s.t desc limit greatest(p_limit, 1)) x);
end $$;

create or replace function dev_attempts(p_limit int default 100) returns json
language plpgsql security definer set search_path = public, auth as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  return (select coalesce(json_agg(x), '[]'::json) from (
    select a.t, a."set", a.sub, s.name as student, u.email as teacher,
           jsonb_array_length(case when jsonb_typeof(a.items) = 'array' then a.items else '[]'::jsonb end) as n,
           (select count(*) from jsonb_array_elements(case when jsonb_typeof(a.items) = 'array' then a.items else '[]'::jsonb end) e where (e->>'r') = '1') as right
    from attempts a left join students s on s.id = a.student_id left join auth.users u on u.id = a.user_id
    order by a.t desc limit greatest(p_limit, 1)) x);
end $$;

create or replace function dev_signups() returns json
language plpgsql security definer set search_path = public, auth as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  return (select coalesce(json_agg(x), '[]'::json) from (
    select r.id, r.name, r.grade, r.login, r.status, r.t, u.email as teacher
    from signup_requests r left join auth.users u on u.id = r.user_id order by r.t desc limit 200) x);
end $$;

create or replace function dev_cleanup() returns json
language plpgsql security definer set search_path = public as $$
declare a int; b int; c int;
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  delete from passkey_challenges where created_at < now() - interval '1 hour'; get diagnostics a = row_count;
  delete from st_tokens where expires_at < now(); get diagnostics b = row_count;
  delete from dev_log where t < (extract(epoch from now() - interval '180 days') * 1000)::bigint; get diagnostics c = row_count;
  return json_build_object('challenges', a, 'tokens', b, 'logs', c);
end $$;
grant execute on function dev_daily(int), dev_students(int), dev_attempts(int), dev_signups(), dev_cleanup() to authenticated;

-- 15-6) 개발자 등록 ▶ 아래 이메일을 바꾸고 실행
insert into developers (user_id, email)
select id, email from auth.users where email = '여기에_개발자_이메일@example.com'
on conflict (user_id) do nothing;

-- =====================================================================
-- 16. 학부모 계정 (읽기 전용)
--   선생님이 학생마다 학부모 아이디/비밀번호를 발급하면, 학부모는 로그인해서 자녀의 학습 현황만 볼 수 있습니다.
--   (문제를 풀거나 제출하는 기능은 없고, 다른 학생의 정보는 볼 수 없습니다)
-- 이미 실행했어도 다시 실행해도 됩니다.
-- =====================================================================
create extension if not exists pgcrypto with schema extensions;

create table if not exists parent_accounts (
  id         bigint generated always as identity primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  login      text not null,
  pw_hash    text not null,
  label      text not null default '학부모',
  created_at timestamptz not null default now(),
  last_login timestamptz
);
create unique index if not exists parent_accounts_login_key on parent_accounts (lower(login));
create index if not exists parent_accounts_student on parent_accounts (student_id);
create table if not exists pa_tokens (
  token_hash text primary key,
  parent_id  bigint not null references parent_accounts(id) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default now() + interval '90 days'
);
-- 정책을 만들지 않으면 일반 사용자는 표를 직접 읽거나 쓸 수 없고, 아래 함수로만 접근합니다.
alter table parent_accounts enable row level security;
alter table pa_tokens enable row level security;

-- 선생님: 발급(같은 아이디로 다시 발급하면 비밀번호 변경) · 해제 · 목록
create or replace function parent_issue(p_student uuid, p_login text, p_pw text, p_label text default '학부모') returns void
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; l text := lower(trim(coalesce(p_login, ''))); lb text := coalesce(nullif(trim(p_label), ''), '학부모');
begin
  if auth.uid() is null or not exists (select 1 from students where id = p_student and user_id = auth.uid()) then
    raise exception 'not allowed';
  end if;
  if length(coalesce(p_pw, '')) < 4 then raise exception 'password too short'; end if;
  if length(l) < 3 then raise exception 'login too short'; end if;
  select * into a from parent_accounts where lower(login) = l;
  if found then
    if a.user_id <> auth.uid() or a.student_id <> p_student then raise exception 'login taken'; end if;
    update parent_accounts set pw_hash = crypt(p_pw, gen_salt('bf')), label = lb where id = a.id;
    delete from pa_tokens where parent_id = a.id;
  else
    if (select count(*) from parent_accounts where student_id = p_student) >= 5 then raise exception 'too many accounts'; end if;
    insert into parent_accounts (user_id, student_id, login, pw_hash, label) values (auth.uid(), p_student, l, crypt(p_pw, gen_salt('bf')), lb);
  end if;
end $$;
create or replace function parent_revoke(p_id bigint) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  delete from parent_accounts where id = p_id and user_id = auth.uid();
end $$;
create or replace function parent_list() returns json
language plpgsql security definer set search_path = public, extensions as $$
begin
  return (select coalesce(json_agg(json_build_object('id', id, 'student_id', student_id, 'login', login, 'label', label, 'last_login', last_login) order by id), '[]'::json)
          from parent_accounts where user_id = auth.uid());
end $$;
grant execute on function parent_issue(uuid, text, text, text) to authenticated;
grant execute on function parent_revoke(bigint) to authenticated;
grant execute on function parent_list() to authenticated;

-- 학부모(비로그인): 비밀번호 또는 자동 로그인 토큰(「tok:<토큰>」)으로 확인
create or replace function _pa_auth(p_login text, p_pw text) returns parent_accounts
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype;
begin
  if p_pw like 'tok:%' then
    select pa.* into a from parent_accounts pa join pa_tokens t on t.parent_id = pa.id
      where lower(pa.login) = lower(trim(p_login)) and t.token_hash = encode(digest(substr(p_pw, 5), 'sha256'), 'hex') and t.expires_at > now() limit 1;
  else
    select * into a from parent_accounts where lower(login) = lower(trim(p_login)) and pw_hash = crypt(p_pw, pw_hash) limit 1;
  end if;
  if not found then return null; end if;
  return a;
end $$;
revoke all on function _pa_auth(text, text) from public, anon, authenticated;

create or replace function pa_login(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; s students%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  select * into s from students where id = a.student_id;
  update parent_accounts set last_login = now() where id = a.id;
  return json_build_object('id', a.id, 'label', a.label, 'student', json_build_object('id', s.id, 'name', s.name, 'grade', s.grade));
end $$;
create or replace function pa_data(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; s students%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  select * into s from students where id = a.student_id;
  return json_build_object(
    'label', a.label,
    'student', json_build_object('id', s.id, 'name', s.name, 'grade', s.grade),
    'attempts', (select coalesce(json_agg(json_build_object('t', x.t, 'set', x."set", 'sub', x.sub, 'items', x.items, 'rng', x.rng) order by x.t), '[]'::json)
                 from (select * from attempts where student_id = s.id order by t desc limit 400) x),
    'assignments', (select coalesce(json_agg(json_build_object('wid', y.wid, 'title', y.title, 'due', y.due, 'note', y.note, 't', y.t) order by y.t desc), '[]'::json)
                    from assignments y where y.student_id = s.id));
end $$;
create or replace function pa_issue_token(p_login text, p_pw text) returns text
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; tok text;
begin
  if p_pw like 'tok:%' then return null; end if;
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  tok := encode(gen_random_bytes(32), 'hex');
  insert into pa_tokens (token_hash, parent_id) values (encode(digest(tok, 'sha256'), 'hex'), a.id);
  delete from pa_tokens where parent_id = a.id and expires_at < now();
  return tok;
end $$;
create or replace function pa_logout(p_login text, p_token text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  delete from pa_tokens where token_hash = encode(digest(p_token, 'sha256'), 'hex')
    and parent_id in (select id from parent_accounts where lower(login) = lower(trim(p_login)));
end $$;
grant execute on function pa_login(text, text) to anon, authenticated;
grant execute on function pa_data(text, text) to anon, authenticated;
grant execute on function pa_issue_token(text, text) to anon, authenticated;
grant execute on function pa_logout(text, text) to anon, authenticated;

-- =====================================================================
-- 17. 서버에 저장되는 설정(D-day 등) · 시험 일정 · 오답 메모 · 문항 신고 처리 · 학부모 알림
-- 이미 실행했어도 다시 실행해도 됩니다. (sql_16_parent.sql 다음에 실행)
-- =====================================================================
create extension if not exists pgcrypto with schema extensions;

-- 17-1) 학생 개인 설정(D-day·목표·오늘의 문제 범위 등)을 서버에 저장 → 기기를 바꿔도 그대로
alter table students add column if not exists prefs jsonb not null default '{}'::jsonb;

-- 선생님이 정한 시험 일정은 teacher_settings.data.exams 에 저장되고, 학생·학부모는 아래 함수로 읽습니다.
create or replace function st_prefs_get(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return json_build_object('prefs', coalesce(s.prefs, '{}'::jsonb),
    'exams', coalesce((select data->'exams' from teacher_settings where user_id = s.user_id), '[]'::jsonb),
    'grade', s.grade);
end $$;
create or replace function st_prefs_set(p_login text, p_pw text, p_prefs jsonb) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then raise exception 'login failed'; end if;
  if jsonb_typeof(p_prefs) <> 'object' or length(p_prefs::text) > 20000 then raise exception 'bad prefs'; end if;
  update students set prefs = coalesce(prefs, '{}'::jsonb) || p_prefs where id = s.id;
end $$;
create or replace function pa_prefs_get(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; s students%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  select * into s from students where id = a.student_id;
  return json_build_object('prefs', coalesce(s.prefs, '{}'::jsonb),
    'exams', coalesce((select data->'exams' from teacher_settings where user_id = s.user_id), '[]'::jsonb),
    'grade', s.grade);
end $$;
grant execute on function st_prefs_get(text, text) to anon, authenticated;
grant execute on function st_prefs_set(text, text, jsonb) to anon, authenticated;
grant execute on function pa_prefs_get(text, text) to anon, authenticated;

-- 17-2) 공지 받는 사람(학생/학부모/모두)
alter table notices add column if not exists audience text not null default 'student';
create or replace function st_notices(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return (select coalesce(json_agg(json_build_object('id', n.id, 'title', n.title, 'body', n.body, 't', n.t) order by n.t desc), '[]'::json)
          from (select * from notices where user_id = s.user_id and (student_id is null or student_id = s.id)
                  and coalesce(audience, 'student') in ('student', 'all') order by t desc limit 50) n);
end $$;
create or replace function pa_notices(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  return (select coalesce(json_agg(json_build_object('id', n.id, 'title', n.title, 'body', n.body, 't', n.t) order by n.t desc), '[]'::json)
          from (select * from notices where user_id = a.user_id and (student_id is null or student_id = a.student_id)
                  and coalesce(audience, 'student') in ('parent', 'all') order by t desc limit 50) n);
end $$;
grant execute on function st_notices(text, text) to anon, authenticated;
grant execute on function pa_notices(text, text) to anon, authenticated;

-- 17-3) 오답 메모(글 + 작은 사진)
create table if not exists wrong_notes (
  student_id uuid not null references students(id) on delete cascade,
  code       text not null,
  memo       text not null default '',
  photo      text,
  t          bigint not null default (extract(epoch from now()) * 1000)::bigint,
  primary key (student_id, code)
);
alter table wrong_notes enable row level security;
drop policy if exists "wn select" on wrong_notes;
create policy "wn select" on wrong_notes for select using (exists (select 1 from students s where s.id = student_id and s.user_id = auth.uid()));
create or replace function st_notes(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return (select coalesce(json_agg(json_build_object('c', code, 'm', memo, 'p', photo, 't', t) order by t desc), '[]'::json) from wrong_notes where student_id = s.id);
end $$;
create or replace function st_note_set(p_login text, p_pw text, p_code text, p_memo text, p_photo text) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then raise exception 'login failed'; end if;
  if length(coalesce(p_memo, '')) > 1500 or length(coalesce(p_photo, '')) > 200000 then raise exception 'too large'; end if;
  -- 사진은 이미지 data URL 형식만 허용 (화면에 그대로 넣기 때문에 다른 문자열은 막습니다)
  if coalesce(p_photo, '') <> '' and p_photo !~ '^data:image/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$' then raise exception 'bad photo'; end if;
  if not exists (select 1 from wrong_notes where student_id = s.id and code = p_code)
     and (select count(*) from wrong_notes where student_id = s.id) >= 300 then raise exception 'too many'; end if;
  insert into wrong_notes (student_id, code, memo, photo, t) values (s.id, p_code, coalesce(p_memo, ''), nullif(p_photo, ''), (extract(epoch from now()) * 1000)::bigint)
  on conflict (student_id, code) do update set memo = excluded.memo, photo = excluded.photo, t = excluded.t;
end $$;
create or replace function st_note_del(p_login text, p_pw text, p_code text) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then raise exception 'login failed'; end if;
  delete from wrong_notes where student_id = s.id and code = p_code;
end $$;
grant execute on function st_notes(text, text) to anon, authenticated;
grant execute on function st_note_set(text, text, text, text, text) to anon, authenticated;
grant execute on function st_note_del(text, text, text) to anon, authenticated;

-- 17-4) 문항 신고: 학생·선생님이 신고 → 개발자가 모아서 고치고 「처리됨」으로 바꾸면 신고한 학생에게 알림
create table if not exists q_reports (
  id          bigint generated always as identity primary key,
  user_id     uuid not null references auth.users(id) on delete cascade,
  student_id  uuid references students(id) on delete set null,
  who         text not null default '',
  code        text not null,
  reason      text not null default '',
  memo        text not null default '',
  status      text not null default 'open',
  resolution  text not null default '',
  t           bigint not null default (extract(epoch from now()) * 1000)::bigint,
  resolved_at bigint
);
alter table q_reports drop constraint if exists q_reports_fmt;
alter table q_reports add constraint q_reports_fmt check (code ~ '^[A-Za-z0-9_.:-]{3,40}$' and length(reason) <= 60 and length(memo) <= 800 and length(who) <= 120) not valid;
create index if not exists q_reports_code on q_reports (code);
alter table q_reports enable row level security;
drop policy if exists "qr select" on q_reports;
drop policy if exists "qr insert" on q_reports;
drop policy if exists "qr delete" on q_reports;
create policy "qr select" on q_reports for select using (auth.uid() = user_id);
create policy "qr insert" on q_reports for insert with check (auth.uid() = user_id);
create policy "qr delete" on q_reports for delete using (auth.uid() = user_id);
create or replace function st_qreport(p_login text, p_pw text, p_code text, p_reason text, p_memo text) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then raise exception 'login failed'; end if;
  if coalesce(p_code, '') !~ '^[A-Za-z0-9_.:-]{3,40}$' then raise exception 'bad code'; end if;
  if exists (select 1 from q_reports where student_id = s.id and code = p_code and status = 'open') then return; end if;
  insert into q_reports (user_id, student_id, who, code, reason, memo) values (s.user_id, s.id, s.name, p_code, left(coalesce(p_reason, ''), 60), left(coalesce(p_memo, ''), 800));
end $$;
create or replace function st_qreports(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return (select coalesce(json_agg(json_build_object('code', code, 'reason', reason, 'status', status, 'resolution', resolution, 't', t) order by t desc), '[]'::json)
          from (select * from q_reports where student_id = s.id order by t desc limit 100) x);
end $$;
grant execute on function st_qreport(text, text, text, text, text) to anon, authenticated;
grant execute on function st_qreports(text, text) to anon, authenticated;

create or replace function dev_qreports() returns json
language plpgsql security definer set search_path = public as $$
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  return (select coalesce(json_agg(x order by x.open desc, x.last desc), '[]'::json) from (
    select code, count(*) filter (where status = 'open') as open, count(*) as total, max(t) as last,
           json_agg(json_build_object('id', id, 'who', who, 'reason', reason, 'memo', memo, 'status', status, 't', t) order by t desc) as items
    from q_reports group by code) x);
end $$;
create or replace function dev_qreport_resolve(p_code text, p_status text, p_note text) returns int
language plpgsql security definer set search_path = public as $$
declare n int := 0; r record;
begin
  if not is_dev() then raise exception 'not allowed'; end if;
  if p_status not in ('fixed', 'rejected') then raise exception 'bad status'; end if;
  for r in select * from q_reports where code = p_code and status = 'open' loop
    update q_reports set status = p_status, resolution = left(coalesce(p_note, ''), 300), resolved_at = (extract(epoch from now()) * 1000)::bigint where id = r.id;
    if r.student_id is not null then
      insert into notices (user_id, student_id, title, body, audience)
      values (r.user_id, r.student_id, case when p_status = 'fixed' then '신고하신 문항을 고쳤어요' else '신고하신 문항을 확인했어요' end,
              p_code || ' 문항 신고를 확인했어요.' || case when coalesce(p_note, '') <> '' then ' ' || left(p_note, 200) else '' end || ' 알려 줘서 고마워요!', 'student');
    end if;
    n := n + 1;
  end loop;
  return n;
end $$;
grant execute on function dev_qreports() to authenticated;
grant execute on function dev_qreport_resolve(text, text, text) to authenticated;

-- 선생님 화면: 학원 설정 → 가입 → 「코드 다시 만들기」. 이전 코드는 바로 못 쓰게 됩니다.
create or replace function join_code_regen() returns json
language plpgsql security definer set search_path = public, extensions as $$
declare c text; n int := 0; r teacher_join%rowtype;
begin
  if auth.uid() is null then raise exception 'not allowed'; end if;
  perform join_info();
  loop
    c := upper(substr(translate(encode(gen_random_bytes(9), 'base64'), '+/=lIO01', 'XYZABCDE'), 1, 6));
    exit when not exists (select 1 from teacher_join where code = c);
    n := n + 1;
    if n > 20 then raise exception 'try again'; end if;
  end loop;
  update teacher_join set code = c where user_id = auth.uid() returning * into r;
  return json_build_object('code', r.code, 'open', r.open);
end $$;
grant execute on function join_code_regen() to authenticated;

-- ===== sql_20_attendance_billing.sql =====
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

-- ===== sql_21_shared_academy.sql =====
-- =====================================================================
-- 21. 한 학원을 여러 선생님 계정이 함께 쓰기 (원장 + 선생님)
-- Supabase 대시보드 > SQL Editor 에 통째로 붙여넣고 Run. 이미 실행했어도 다시 실행해도 됩니다.
-- 반드시 sql_20_attendance_billing.sql 까지 모두 실행한 뒤에 실행하세요.
--
-- 방식: 공동 선생님이 로그인하면 서버가 "이 사람의 데이터 주인 = 대표 선생님"으로 취급해요.
--       그래서 학생·채점·학습지·출결·수납·설정이 대표 선생님과 똑같이 보이고 같이 바뀝니다.
--       (대표 선생님 본인의 동작은 전혀 달라지지 않아요.)
-- =====================================================================
create extension if not exists pgcrypto with schema extensions;

create table if not exists academy_members (
  member_id  uuid primary key references auth.users(id) on delete cascade,
  owner_id   uuid not null references auth.users(id) on delete cascade,
  label      text,
  created_at timestamptz not null default now()
);
create index if not exists academy_members_owner on academy_members (owner_id);
-- 선생님 가입 신청 (원장이 수락하면 선생님이 돼요)
create table if not exists academy_requests (
  id         bigint generated always as identity primary key,
  member_id  uuid not null unique references auth.users(id) on delete cascade,
  owner_id   uuid not null references auth.users(id) on delete cascade,
  label      text,
  created_at timestamptz not null default now()
);
create index if not exists academy_requests_owner on academy_requests (owner_id);
drop function if exists acad_invite();
drop function if exists acad_invite_revoke(text);
drop function if exists acad_join(text, text);
drop table if exists academy_invites;
-- 정책을 만들지 않으면 일반 사용자는 직접 읽거나 쓸 수 없고, 아래 함수로만 접근해요.
alter table academy_members enable row level security;
alter table academy_requests enable row level security;

-- 데이터 주인: 선생님이면 원장, 아니면 본인
create or replace function acad_owner() returns uuid
language sql stable security definer set search_path = public as $$
  select coalesce((select owner_id from academy_members where member_id = auth.uid()), auth.uid())
$$;
grant execute on function acad_owner() to anon, authenticated;

-- 선생님 계정으로 가입한 사람: 학원 코드(「학생 가입」에서 쓰는 코드와 같아요)를 입력해 가입 신청
create or replace function acad_request(p_code text, p_label text default null) returns boolean
language plpgsql security definer set search_path = public, extensions as $$
declare o uuid;
begin
  if auth.uid() is null then raise exception 'not allowed'; end if;
  select user_id into o from teacher_join where code = upper(trim(p_code));
  if o is null then return false; end if;
  if o = auth.uid() then raise exception 'self'; end if;
  if exists (select 1 from academy_members where member_id = auth.uid() or owner_id = auth.uid()) then raise exception 'already'; end if;
  if exists (select 1 from students where user_id = auth.uid()) then raise exception 'has data'; end if;
  insert into academy_requests (member_id, owner_id, label) values (auth.uid(), o, nullif(trim(coalesce(p_label, '')), ''))
    on conflict (member_id) do update set owner_id = excluded.owner_id, label = excluded.label, created_at = now();
  return true;
end $$;
create or replace function acad_request_cancel() returns void
language plpgsql security definer set search_path = public as $$
begin delete from academy_requests where member_id = auth.uid(); end $$;

create or replace function acad_info() returns json
language plpgsql security definer set search_path = public, extensions as $$
declare m academy_members%rowtype; rq academy_requests%rowtype;
begin
  if auth.uid() is null then return null; end if;
  select * into m from academy_members where member_id = auth.uid();
  if found then
    return json_build_object('role', 'member', 'owner', (select email from auth.users where id = m.owner_id));
  end if;
  select * into rq from academy_requests where member_id = auth.uid();
  return json_build_object('role', 'owner',
    'pending', case when rq.id is null then null else (select email from auth.users where id = rq.owner_id) end,
    'members', (select coalesce(json_agg(json_build_object('id', a.member_id, 'label', a.label, 'email', u.email, 't', a.created_at) order by a.created_at), '[]'::json)
                from academy_members a join auth.users u on u.id = a.member_id where a.owner_id = auth.uid()),
    'requests', (select coalesce(json_agg(json_build_object('id', r.id, 'label', r.label, 'email', u.email, 't', r.created_at) order by r.created_at), '[]'::json)
                from academy_requests r join auth.users u on u.id = r.member_id where r.owner_id = auth.uid()),
    'code', (select code from teacher_join where user_id = auth.uid()));
end $$;

-- 원장: 신청 수락 · 거절
create or replace function acad_approve(p_id bigint) returns boolean
language plpgsql security definer set search_path = public as $$
declare r academy_requests%rowtype;
begin
  select * into r from academy_requests where id = p_id and owner_id = auth.uid();
  if not found then return false; end if;
  if exists (select 1 from academy_members where member_id = auth.uid()) then raise exception 'not allowed'; end if;
  if exists (select 1 from students where user_id = r.member_id) then raise exception 'has data'; end if;
  insert into academy_members (member_id, owner_id, label) values (r.member_id, r.owner_id, r.label) on conflict (member_id) do nothing;
  delete from academy_requests where id = r.id;
  return true;
end $$;
create or replace function acad_reject(p_id bigint) returns void
language plpgsql security definer set search_path = public as $$
begin delete from academy_requests where id = p_id and owner_id = auth.uid(); end $$;

-- 원장: 앱에서 방금 만든 선생님 계정(이메일)을 바로 우리 학원 선생님으로 연결
create or replace function acad_add_member(p_email text, p_label text default null) returns boolean
language plpgsql security definer set search_path = public, extensions as $$
declare u uuid;
begin
  if auth.uid() is null or exists (select 1 from academy_members where member_id = auth.uid()) then raise exception 'not allowed'; end if;
  select id into u from auth.users where lower(email) = lower(trim(p_email));
  if u is null then return false; end if;
  if u = auth.uid() then raise exception 'self'; end if;
  if exists (select 1 from academy_members where member_id = u) or exists (select 1 from academy_members where owner_id = u) then raise exception 'already'; end if;
  if exists (select 1 from students where user_id = u) then raise exception 'has data'; end if;
  insert into academy_members (member_id, owner_id, label) values (u, auth.uid(), nullif(trim(coalesce(p_label, '')), ''));
  delete from academy_requests where member_id = u;
  return true;
end $$;
create or replace function acad_member_remove(p_member uuid) returns void
language plpgsql security definer set search_path = public as $$
begin delete from academy_members where member_id = p_member and owner_id = auth.uid(); end $$;
create or replace function acad_leave() returns void
language plpgsql security definer set search_path = public as $$
begin delete from academy_members where member_id = auth.uid(); end $$;
grant execute on function acad_request(text, text) to authenticated;
grant execute on function acad_request_cancel() to authenticated;
grant execute on function acad_info() to authenticated;
grant execute on function acad_approve(bigint) to authenticated;
grant execute on function acad_reject(bigint) to authenticated;
grant execute on function acad_add_member(text, text) to authenticated;
grant execute on function acad_member_remove(uuid) to authenticated;
grant execute on function acad_leave() to authenticated;

-- ---------------------------------------------------------------------
-- 기존 규칙(auth.uid() = user_id)을 "데이터 주인 = acad_owner()"로 바꿔요.
-- 대표 선생님에게는 결과가 똑같고, 공동 선생님에게는 대표 선생님의 데이터가 열려요.
-- 개발자·버그 신고 관련 표/함수는 건드리지 않아요.
-- ---------------------------------------------------------------------
do $$
declare
  r record; q text; w text; d text;
  tbls text[] := array['students','attempts','worksheets','assignments','notices','teacher_settings','teacher_join','signup_requests','wrong_notes','q_reports','parent_accounts','attendance','parent_notices','fees'];
  fns  text[] := array['approve_signup','att_checkin','issue_login','revoke_login','join_code_regen','join_info','join_open_set','parent_issue','parent_list','parent_revoke','reject_signup'];
begin
  -- 1) 정책
  for r in select * from pg_policies where schemaname = 'public' and tablename = any(tbls) loop
    q := r.qual; w := r.with_check;
    if coalesce(q, '') like '%auth.uid()%' or coalesce(w, '') like '%auth.uid()%' then
      execute format('alter policy %I on public.%I %s %s', r.policyname, r.tablename,
        case when coalesce(q, '') like '%auth.uid()%' then 'using (' || replace(q, 'auth.uid()', 'public.acad_owner()') || ')'
             when q is not null then 'using (' || q || ')' else '' end,
        case when coalesce(w, '') like '%auth.uid()%' then 'with check (' || replace(w, 'auth.uid()', 'public.acad_owner()') || ')'
             when w is not null then 'with check (' || w || ')' else '' end);
    end if;
  end loop;
  -- 2) 새 줄을 만들 때 user_id 기본값
  for r in select table_name, column_name from information_schema.columns
           where table_schema = 'public' and table_name = any(tbls) and column_default like '%auth.uid()%' loop
    execute format('alter table public.%I alter column %I set default public.acad_owner()', r.table_name, r.column_name);
  end loop;
  -- 3) 함수 안의 auth.uid()
  for r in select p.oid from pg_proc p join pg_namespace n on n.oid = p.pronamespace
           where n.nspname = 'public' and p.proname = any(fns) loop
    d := pg_get_functiondef(r.oid);
    if d like '%auth.uid()%' then execute replace(d, 'auth.uid()', 'public.acad_owner()'); end if;
  end loop;
end $$;

-- ===== sql_22_diary_student_attendance.sql =====
-- =====================================================================
-- 22. 알림장(학생·학부모 공지 통합) + 학생용 출결 달력
-- Supabase SQL Editor 에서 통째로 실행. 다시 실행해도 안전해요. (sql_20, sql_21 다음)
-- =====================================================================

-- 22-1) 학부모 알림 목록: 예전 「학부모 공지(notices, audience=parent/all)」와 안내문(parent_notices)을 함께 보여줘요.
--       (sql_20 이 같은 이름의 함수를 덮어써서 예전 공지가 안 보이던 것을 바로잡아요)
create or replace function pa_notices(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  return (
    select coalesce(json_agg(json_build_object('id', x.id, 'title', x.title, 'body', x.body, 't', x.t) order by x.t desc), '[]'::json)
    from (
      select (-1 * p.id) as id, p.title, p.body, (extract(epoch from p.created_at) * 1000)::bigint as t
        from parent_notices p where p.user_id = a.user_id and (p.student_id is null or p.student_id = a.student_id)
      union all
      select n.id, n.title, n.body, n.t
        from notices n where n.user_id = a.user_id and (n.student_id is null or n.student_id = a.student_id)
         and coalesce(n.audience, 'student') in ('parent', 'all')
      order by t desc limit 60
    ) x);
end $$;
grant execute on function pa_notices(text, text) to anon, authenticated;

-- 22-2) 학생 앱의 출결 달력 (날짜와 상태만, 시각·납부 정보는 주지 않아요)
create or replace function st_attendance(p_login text, p_pw text, p_from date, p_to date) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return (select coalesce(json_agg(json_build_object('day', x.day, 'status', x.status) order by x.day), '[]'::json)
          from attendance x where x.student_id = s.id and x.day between p_from and p_to);
end $$;
grant execute on function st_attendance(text, text, date, date) to anon, authenticated;

-- =====================================================================
-- 23) 학원 행정: 원생 정보 · 반 · 시간표 · 상담 일지 · 보강 (supabase/sql_23_admin.sql 과 같음)
-- =====================================================================
-- 23-1) 원생 정보: 학교 · 상태(재원·휴원·퇴원·상담) · 입원일 · 퇴원일 · 보호자
alter table students add column if not exists school text;
alter table students add column if not exists status text not null default '재원';
alter table students add column if not exists joined_on date;
alter table students add column if not exists left_on date;
alter table students add column if not exists guardian text;
alter table students add column if not exists guardian_phone text;
do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'students_status_chk') then
    alter table students add constraint students_status_chk check (status in ('재원', '휴원', '퇴원', '상담'));
  end if;
end $$;

-- 23-2) 반: 이름 · 과목 · 담당 · 강의실 · 요일·시간(sched) · 월 수강료
--   sched 예: [{"d":1,"s":"18:00","e":"20:00"},{"d":3,"s":"18:00","e":"20:00"}]  (d: 1 월요일 … 7 일요일)
create table if not exists classes (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
  name       text not null,
  subject    text,
  teacher    text,
  room       text,
  sched      jsonb not null default '[]'::jsonb,
  tuition    integer check (tuition is null or tuition >= 0),
  color      text,
  memo       text,
  active     boolean not null default true,
  created_at timestamptz not null default now()
);
create index if not exists classes_user on classes (user_id);
alter table classes enable row level security;
drop policy if exists "cls all" on classes;
create policy "cls all" on classes for all using (user_id = public.acad_owner()) with check (user_id = public.acad_owner());

-- 23-3) 반 구성원(학생 한 명이 여러 반에 들 수 있음)
create table if not exists class_members (
  class_id   bigint not null references classes(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  user_id    uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
  since      date not null default current_date,
  primary key (class_id, student_id)
);
create index if not exists class_members_student on class_members (student_id);
create index if not exists class_members_user on class_members (user_id);
alter table class_members enable row level security;
drop policy if exists "clm all" on class_members;
create policy "clm all" on class_members for all using (user_id = public.acad_owner()) with check (user_id = public.acad_owner());

-- 23-4) 상담 일지: 누구와(학생·학부모) · 무엇을 · 다음에 할 일 · 학부모에게 공유
create table if not exists counsels (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  day        date not null default current_date,
  kind       text not null default '학생' check (kind in ('학생', '학부모', '입학', '진로', '기타')),
  body       text not null,
  next_on    date,
  next_todo  text,
  done       boolean not null default false,
  share      boolean not null default false,
  by_name    text,
  created_at timestamptz not null default now()
);
create index if not exists counsels_user_day on counsels (user_id, day desc);
create index if not exists counsels_student on counsels (student_id);
alter table counsels enable row level security;
drop policy if exists "cns all" on counsels;
create policy "cns all" on counsels for all using (user_id = public.acad_owner()) with check (user_id = public.acad_owner());

-- 23-5) 보강: 빠진 날 · 사유 · 보강 일시 · 상태
create table if not exists makeups (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  class_id   bigint references classes(id) on delete set null,
  missed_on  date not null,
  reason     text,
  plan_at    timestamptz,
  status     text not null default '예정' check (status in ('예정', '완료', '취소')),
  memo       text,
  created_at timestamptz not null default now()
);
create index if not exists makeups_user on makeups (user_id, status);
create index if not exists makeups_student on makeups (student_id);
alter table makeups enable row level security;
drop policy if exists "mku all" on makeups;
create policy "mku all" on makeups for all using (user_id = public.acad_owner()) with check (user_id = public.acad_owner());

-- 23-6) 학생 · 학부모: 내 반 시간표 · 보강 일정 · (학부모) 공유된 상담 기록
create or replace function _sched_of(p_owner uuid, p_student uuid, p_counsel boolean) returns json
language sql stable security definer set search_path = public as $$
  select json_build_object(
    'classes', (select coalesce(json_agg(json_build_object('id', c.id, 'name', c.name, 'subject', c.subject, 'teacher', c.teacher, 'room', c.room, 'sched', c.sched, 'color', c.color) order by c.name), '[]'::json)
                from classes c join class_members m on m.class_id = c.id
                where c.user_id = p_owner and m.student_id = p_student and c.active),
    'makeups', (select coalesce(json_agg(json_build_object('missed_on', k.missed_on, 'plan_at', k.plan_at, 'status', k.status, 'reason', k.reason,
                  'class', (select name from classes where id = k.class_id)) order by k.missed_on desc), '[]'::json)
                from (select * from makeups where user_id = p_owner and student_id = p_student order by missed_on desc limit 30) k),
    'counsels', case when p_counsel then
                (select coalesce(json_agg(json_build_object('day', n.day, 'kind', n.kind, 'body', n.body, 'next_on', n.next_on, 'next_todo', n.next_todo) order by n.day desc), '[]'::json)
                 from (select * from counsels where user_id = p_owner and student_id = p_student and share order by day desc limit 30) n)
                else '[]'::json end)
$$;
revoke all on function _sched_of(uuid, uuid, boolean) from public, anon, authenticated;

create or replace function st_schedule(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return _sched_of(s.user_id, s.id, false);
end $$;
grant execute on function st_schedule(text, text) to anon, authenticated;

create or replace function pa_schedule(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  return _sched_of(a.user_id, a.student_id, true);
end $$;
grant execute on function pa_schedule(text, text) to anon, authenticated;

notify pgrst, 'reload schema';


-- ===== sql_24_operations.sql =====
-- 24. 운영 업무·상담 예약·휴강/대체수업·역할별 권한·중복 청구 방지
-- sql_23_admin.sql 이후 실행. 데이터 삭제 없음. 기존 공동 강사는 teacher 역할로 유지.
-- 먼저 복제한 테스트 DB에서 검증하고 백업 후 운영에 적용하세요.
begin;
alter table public.academy_members add column if not exists role text not null default 'teacher' check (role in ('teacher','staff'));
create or replace function public.ops_role() returns text
language sql stable security definer set search_path=public as $$
 select case when auth.uid() is null then null else coalesce((select role from academy_members where member_id=auth.uid()),'owner') end
$$;
create or replace function public.ops_can(p_cap text) returns boolean
language sql stable security definer set search_path=public as $$
 select coalesce(case when ops_role()='owner' then true when p_cap='operations' then ops_role() in ('teacher','staff') when p_cap='billing' then ops_role()='staff' when p_cap='learning' then ops_role()='teacher' else false end,false)
$$;
create or replace function public.ops_access() returns json
language sql stable security definer set search_path=public as $$
 select json_build_object('role',ops_role(),'operations',ops_can('operations'),'billing',ops_can('billing'),'learning',ops_can('learning'),'manage',ops_can('manage'))
$$;
create or replace function public.ops_staff() returns json
language plpgsql stable security definer set search_path=public as $$
begin
 if not ops_can('manage') then raise exception 'forbidden' using errcode='42501'; end if;
 return (select coalesce(json_agg(json_build_object('member_id',member_id,'label',label,'role',role)),'[]'::json) from academy_members where owner_id=auth.uid());
end $$;
create or replace function public.ops_set_role(p_member uuid,p_role text) returns void
language plpgsql security definer set search_path=public as $$
begin
 if not ops_can('manage') or p_role not in ('teacher','staff') then raise exception 'forbidden' using errcode='42501'; end if;
 update academy_members set role=p_role where owner_id=auth.uid() and member_id=p_member;
 if not found then raise exception 'member not found'; end if;
end $$;

-- Restrictive gates intersect existing permissive tenant policies instead of replacing them.
-- SECURITY DEFINER student/parent RPCs keep their existing child authentication checks.
do $$ declare r record; cap text; begin
 for r in select tablename from pg_tables where schemaname='public' and tablename in
 ('students','classes','class_members','counsels','makeups','attendance','parent_notices','parent_accounts','fees','attempts','worksheets','assignments','wrong_notes') loop
 cap:=case when r.tablename='parent_accounts' then 'manage' when r.tablename='fees' then 'billing' when r.tablename in ('attempts','worksheets','assignments','wrong_notes') then 'learning' else 'operations' end;
 execute format('drop policy if exists ops_role_gate on public.%I',r.tablename);
 execute format('create policy ops_role_gate on public.%I as restrictive for all to authenticated using (public.ops_can(%L)) with check (public.ops_can(%L))',r.tablename,cap,cap);
 end loop;
end $$;

create table if not exists public.ops_tasks (
 id bigint generated always as identity primary key,
 user_id uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
 title text not null check (length(trim(title)) between 1 and 160),
 student_id uuid references public.students(id) on delete set null,
 assignee text not null default '' check (length(assignee)<=80),
 due_on date not null,
 repeat_kind text not null default 'none' check (repeat_kind in ('none','daily','weekly','monthly')),
 anchor_day smallint check (anchor_day between 1 and 31),
 completed_at timestamptz,
 previous_id bigint unique references public.ops_tasks(id) on delete set null,
 created_at timestamptz not null default now()
);
create index if not exists ops_tasks_due on public.ops_tasks(user_id,due_on) where completed_at is null;
create table if not exists public.counsel_appointments (
 id bigint generated always as identity primary key,
 user_id uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
 student_id uuid not null references public.students(id) on delete cascade,
 starts_at timestamptz not null,
 ends_at timestamptz not null,
 assignee text not null check (length(trim(assignee)) between 1 and 80),
 kind text not null default '학부모' check (kind in ('학생','학부모','입학','진로','기타')),
 status text not null default '예정' check (status in ('예정','완료','취소')),
 memo text not null default '' check (length(memo)<=3000),
 created_at timestamptz not null default now(),
 check (ends_at>starts_at)
);
create index if not exists counsel_appointments_time on public.counsel_appointments(user_id,starts_at);
create table if not exists public.lesson_changes (
 id bigint generated always as identity primary key,
 user_id uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
 class_id bigint not null references public.classes(id) on delete cascade,
 on_date date not null,
 kind text not null check (kind in ('휴강','대체')),
 starts_at timestamptz,
 ends_at timestamptz,
 room text check (length(room)<=80),
 teacher text check (length(teacher)<=80),
 reason text not null default '' check (length(reason)<=500),
 unique(class_id,on_date),
 check ((kind='휴강' and starts_at is null and ends_at is null) or (kind='대체' and starts_at is not null and ends_at is not null and ends_at>starts_at))
);
create index if not exists lesson_changes_owner_day on public.lesson_changes(user_id,on_date);
create table if not exists public.ops_audit (
 id bigint generated always as identity primary key,
 user_id uuid not null,
 actor_id uuid,
 table_name text not null,
 row_id text not null,
 action text not null,
 created_at timestamptz not null default now()
);
alter table public.ops_audit enable row level security;
drop policy if exists ops_audit_read on public.ops_audit;
create policy ops_audit_read on public.ops_audit for select to authenticated using (user_id=public.acad_owner() and public.ops_can('manage'));

-- Cross-academy references cannot be smuggled into rows even when their owner_id is valid.
create or replace function public.ops_tenant_check() returns trigger
language plpgsql security definer set search_path=public as $$
declare j jsonb:=to_jsonb(new); oid uuid; begin
 oid:=(j->>'user_id')::uuid;
 if j->>'student_id' is not null and not exists(select 1 from students where id=(j->>'student_id')::uuid and user_id=oid) then raise exception 'student outside academy' using errcode='23514'; end if;
 if j->>'class_id' is not null and not exists(select 1 from classes where id=(j->>'class_id')::bigint and user_id=oid) then raise exception 'class outside academy' using errcode='23514'; end if;
 if j->>'previous_id' is not null and not exists(select 1 from ops_tasks where id=(j->>'previous_id')::bigint and user_id=oid) then raise exception 'task outside academy' using errcode='23514'; end if;
 return new;
end $$;
create or replace function public.ops_record_change() returns trigger
language plpgsql security definer set search_path=public as $$
declare j jsonb; begin
 if tg_op='DELETE' then j:=to_jsonb(old); else j:=to_jsonb(new); end if;
 insert into ops_audit(user_id,actor_id,table_name,row_id,action) values ((j->>'user_id')::uuid,auth.uid(),tg_table_name,j->>'id',tg_op);
 if tg_op='DELETE' then return old; else return new; end if;
end $$;
do $$ declare t text; begin
 foreach t in array array['ops_tasks','counsel_appointments','lesson_changes'] loop
 execute format('alter table public.%I enable row level security',t);
 execute format('drop policy if exists ops_tenant on public.%I',t);
 execute format('create policy ops_tenant on public.%I for all to authenticated using (user_id=public.acad_owner() and public.ops_can(''operations'')) with check (user_id=public.acad_owner() and public.ops_can(''operations''))',t);
 execute format('grant select,insert,update,delete on public.%I to authenticated',t);
 end loop;
 foreach t in array array['ops_tasks','counsel_appointments','lesson_changes','class_members','counsels','makeups','attendance','fees','parent_accounts','attempts','worksheets','assignments'] loop
 execute format('drop trigger if exists ops_tenant_guard on public.%I',t);
 execute format('create trigger ops_tenant_guard before insert or update on public.%I for each row execute function public.ops_tenant_check()',t);
 end loop;
 foreach t in array array['ops_tasks','counsel_appointments','lesson_changes','fees','counsels'] loop
 execute format('drop trigger if exists ops_change_log on public.%I',t);
 execute format('create trigger ops_change_log after insert or update or delete on public.%I for each row execute function public.ops_record_change()',t);
 end loop;
end $$;
grant select on public.ops_audit to authenticated;
grant usage,select on all sequences in schema public to authenticated;

-- Serialize conflicting appointments per academy; adjacent appointments are allowed.
create or replace function public.ops_appointment_check() returns trigger
language plpgsql security definer set search_path=public as $$
begin
 perform pg_advisory_xact_lock(hashtextextended(new.user_id::text||':appointments',0));
 if new.status='예정' and exists(select 1 from counsel_appointments x where x.user_id=new.user_id and x.id<>new.id and x.status='예정' and (x.assignee=new.assignee or x.student_id=new.student_id) and x.starts_at<new.ends_at and new.starts_at<x.ends_at) then raise exception '상담 일정이 겹쳐요' using errcode='23514'; end if;
 return new;
end $$;
drop trigger if exists ops_appointment_guard on public.counsel_appointments;
create trigger ops_appointment_guard before insert or update on public.counsel_appointments for each row execute function public.ops_appointment_check();

create or replace function public.ops_complete_task(p_id bigint) returns json
language plpgsql security definer set search_path=public as $$
declare x ops_tasks%rowtype; nd date; nid bigint; anchor int; begin
 if not ops_can('operations') then raise exception 'forbidden' using errcode='42501'; end if;
 select * into x from ops_tasks where id=p_id and user_id=acad_owner() for update;
 if not found then raise exception 'task not found'; end if;
 if x.completed_at is not null then return json_build_object('completed',x.id,'next_id',(select id from ops_tasks where previous_id=x.id)); end if;
 anchor:=coalesce(x.anchor_day,extract(day from x.due_on)::int);
 nd:=case x.repeat_kind when 'daily' then x.due_on+1 when 'weekly' then x.due_on+7 when 'monthly' then (date_trunc('month',x.due_on)+interval '1 month')::date+least(anchor,extract(day from date_trunc('month',x.due_on)+interval '2 months - 1 day')::int)-1 else null end;
 update ops_tasks set completed_at=now() where id=x.id;
 if nd is not null then insert into ops_tasks(user_id,title,student_id,assignee,due_on,repeat_kind,anchor_day,previous_id) values(x.user_id,x.title,x.student_id,x.assignee,nd,x.repeat_kind,anchor,x.id) returning id into nid; end if;
 return json_build_object('completed',x.id,'next_id',nid);
end $$;

alter table public.fees add column if not exists billing_key text;
create unique index if not exists fees_billing_key on public.fees(user_id,billing_key) where billing_key is not null;
create or replace function public.ops_monthly_bill(p_month date,p_due date) returns json
language plpgsql security definer set search_path=public as $$
declare oid uuid:=acad_owner(); n integer; begin
 if not ops_can('billing') then raise exception 'forbidden' using errcode='42501'; end if;
 if p_month is null or p_month<>date_trunc('month',p_month)::date or p_due is null then raise exception '청구 월과 납부 기한을 확인해 주세요'; end if;
 perform pg_advisory_xact_lock(hashtextextended(oid::text||':billing:'||p_month::text,0));
 insert into fees(user_id,student_id,kind,title,amount,due,billing_key)
 select oid,s.id,'tuition',extract(year from p_month)::int||'년 '||extract(month from p_month)::int||'월 '||c.name||' 수강료',c.tuition,p_due,to_char(p_month,'YYYY-MM')||':'||c.id||':'||s.id
 from classes c join class_members m on m.class_id=c.id and m.user_id=oid join students s on s.id=m.student_id and s.user_id=oid
 where c.user_id=oid and c.active and c.tuition>0 and s.status='재원'
 and not exists(select 1 from fees f where f.user_id=oid and f.student_id=s.id and f.billing_key is null and f.title=extract(year from p_month)::int||'년 '||extract(month from p_month)::int||'월 '||c.name||' 수강료')
 on conflict (user_id,billing_key) where billing_key is not null do nothing;
 get diagnostics n=row_count;
 return json_build_object('created',n);
end $$;

-- Child credentials imply access to child/guardian RPCs, so provisioning is capability protected too.
-- Do not expose password hashes through REST; preserve nonsecret fields used by old clients.
do $$ declare r record; d text; capability text; cols text; t text; begin
 for r in select p.oid,p.proname from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.proname in ('issue_login','revoke_login','parent_issue','parent_revoke','approve_signup') loop
 capability:=case when r.proname in ('issue_login','revoke_login') then 'learning' else 'manage' end;
 d:=pg_get_functiondef(r.oid);
 if d not like '%-- ops credential gate%' then
 d:=regexp_replace(d,'\y[Bb][Ee][Gg][Ii][Nn]\y','begin'||chr(10)||' -- ops credential gate'||chr(10)||format(' if not public.ops_can(%L) then raise exception ''forbidden'' using errcode=''42501''; end if;',capability));
 execute d;
 end if;
 end loop;
 foreach t in array array['students','signup_requests'] loop
 if to_regclass('public.'||t) is null then continue; end if;
 select string_agg(quote_ident(column_name),',') into cols from information_schema.columns where table_schema='public' and table_name=t and column_name not in ('pw_hash','password','password_hash');
 execute format('revoke select on public.%I from public,anon,authenticated',t);
 execute format('revoke select (pw_hash) on public.%I from public,anon,authenticated',t);
 execute format('grant select (%s) on public.%I to authenticated',cols,t);
 end loop;
end $$;
create or replace function public.ops_credential_check() returns trigger
language plpgsql security definer set search_path=public as $$
begin
 if auth.uid() is not null and not ops_can('learning') then
 if tg_op='INSERT' then
 if new.login is not null or new.pw_hash is not null then raise exception 'credential provisioning requires learning permission' using errcode='42501'; end if;
 elsif new.login is distinct from old.login or new.pw_hash is distinct from old.pw_hash then raise exception 'credential provisioning requires learning permission' using errcode='42501';
 end if;
 end if;
 return new;
end $$;
drop trigger if exists ops_credential_guard on public.students;
create trigger ops_credential_guard before insert or update on public.students for each row execute function public.ops_credential_check();
revoke all on function public.ops_credential_check() from public,anon,authenticated;

-- Add early departure without rewriting any existing attendance rows.
alter table public.attendance drop constraint if exists attendance_status_check;
alter table public.attendance add constraint attendance_status_check check (status in ('in','late','absent','excused','early'));

-- Existing student/parent schedule RPCs call this helper, so exceptions share their child authentication.
create or replace function public._sched_of(p_owner uuid,p_student uuid,p_counsel boolean) returns json
language sql stable security definer set search_path=public as $$
 select json_build_object(
 'classes',(select coalesce(json_agg(json_build_object('id',c.id,'name',c.name,'subject',c.subject,'teacher',c.teacher,'room',c.room,'sched',c.sched,'color',c.color) order by c.name),'[]'::json) from classes c join class_members m on m.class_id=c.id where c.user_id=p_owner and m.student_id=p_student and c.active),
 'makeups',(select coalesce(json_agg(json_build_object('missed_on',k.missed_on,'plan_at',k.plan_at,'status',k.status,'reason',k.reason,'class',(select name from classes where id=k.class_id)) order by k.missed_on desc),'[]'::json) from makeups k where k.user_id=p_owner and k.student_id=p_student),
 'counsels',case when p_counsel then (select coalesce(json_agg(json_build_object('day',c.day,'kind',c.kind,'body',c.body,'next_on',c.next_on,'next_todo',c.next_todo) order by c.day desc),'[]'::json) from counsels c where c.user_id=p_owner and c.student_id=p_student and c.share) else '[]'::json end,
 'lesson_changes',(select coalesce(json_agg(json_build_object('class_id',l.class_id,'on_date',l.on_date,'kind',l.kind,'starts_at',l.starts_at,'ends_at',l.ends_at,'room',l.room,'teacher',l.teacher,'reason',l.reason,'class',c.name) order by l.on_date),'[]'::json) from lesson_changes l join classes c on c.id=l.class_id and c.active where l.user_id=p_owner and l.on_date>=(now() at time zone 'Asia/Seoul')::date-30 and exists(select 1 from class_members m where m.class_id=l.class_id and m.student_id=p_student))
 )
$$;
revoke all on function public._sched_of(uuid,uuid,boolean) from public,anon,authenticated;

-- Preserve teaching preferences while enforcing payment/academy-settings ownership at the DB boundary.
create or replace function public.ops_settings_check() returns trigger
language plpgsql security definer set search_path=public as $$
declare previous jsonb; begin
 if auth.uid() is null then return new; end if;
 select data into previous from teacher_settings where user_id=new.user_id;
 if not ops_can('billing') and new.data->'pay' is distinct from previous->'pay' then raise exception 'billing settings require permission' using errcode='42501'; end if;
 if not ops_can('manage') and new.data->'perms' is distinct from previous->'perms' then raise exception 'academy settings require owner permission' using errcode='42501'; end if;
 return new;
end $$;
drop trigger if exists ops_settings_guard on public.teacher_settings;
create trigger ops_settings_guard before insert or update on public.teacher_settings for each row execute function public.ops_settings_check();
revoke all on function public.ops_settings_check() from public,anon,authenticated;

-- Date-aware replacement conflicts, including other replacements and excluding cancelled regular lessons.
create or replace function public.ops_lesson_check() returns trigger
language plpgsql security definer set search_path=public as $$
declare target date; rm text; tr text; begin
 if new.kind='휴강' or new.starts_at is null or new.ends_at is null then return new; end if;
 perform pg_advisory_xact_lock(hashtextextended(new.user_id::text||':lessons',0));
 target:=(new.starts_at at time zone 'Asia/Seoul')::date;
 if (new.ends_at at time zone 'Asia/Seoul')::date<>target then raise exception '대체수업은 같은 날에 시작하고 끝나야 해요' using errcode='23514'; end if;
 select coalesce(nullif(trim(new.room),''),nullif(trim(c.room),'')),coalesce(nullif(trim(new.teacher),''),nullif(trim(c.teacher),'')) into rm,tr from classes c where c.id=new.class_id;
 if exists(
 select 1 from lesson_changes l join classes c on c.id=l.class_id
 where l.user_id=new.user_id and l.id<>new.id and l.kind='대체' and c.active
 and l.starts_at<new.ends_at and new.starts_at<l.ends_at
 and ((rm is not null and rm=coalesce(nullif(trim(l.room),''),nullif(trim(c.room),''))) or (tr is not null and tr=coalesce(nullif(trim(l.teacher),''),nullif(trim(c.teacher),''))))
 ) or exists(
 select 1 from classes c cross join lateral jsonb_array_elements(c.sched) t
 where c.user_id=new.user_id and c.active
 and not(c.id=new.class_id and new.on_date=target)
 and t->>'d'=extract(isodow from target)::int::text
 and t->>'s' ~ '^([01][0-9]|2[0-3]):[0-5][0-9]$' and t->>'e' ~ '^([01][0-9]|2[0-3]):[0-5][0-9]$'
 and not exists(select 1 from lesson_changes l where l.class_id=c.id and l.on_date=target and l.id<>new.id)
 and ((rm is not null and rm=nullif(trim(c.room),'')) or (tr is not null and tr=nullif(trim(c.teacher),'')))
 and ((target+(t->>'s')::time) at time zone 'Asia/Seoul')<new.ends_at
 and new.starts_at<((target+(t->>'e')::time) at time zone 'Asia/Seoul')
 ) then raise exception '강사 또는 강의실의 수업 시간이 겹쳐요' using errcode='23514'; end if;
 return new;
end $$;
drop trigger if exists ops_lesson_guard on public.lesson_changes;
create trigger ops_lesson_guard before insert or update on public.lesson_changes for each row execute function public.ops_lesson_check();
revoke all on function public.ops_lesson_check() from public,anon,authenticated;

-- Keep the date/class identity of an exception. Moving/deleting it would silently restore
-- a regular lesson on an already-booked date. Restore via a replacement at the original time.
create or replace function public.ops_lesson_identity_check() returns trigger
language plpgsql security definer set search_path=public as $$
begin
 if tg_op='DELETE' then
 if pg_trigger_depth()>1 then return old; end if; -- parent class/account cascade also removes the regular lesson
 raise exception '수업 변경 이력은 삭제할 수 없어요. 원래 시간의 대체수업으로 복원해 주세요' using errcode='23514';
 end if;
 if new.class_id is distinct from old.class_id or new.on_date is distinct from old.on_date then raise exception '수업 변경의 반과 원래 날짜는 바꿀 수 없어요. 원래 시간의 대체수업으로 먼저 복원해 주세요' using errcode='23514'; end if;
 return new;
end $$;
drop trigger if exists ops_lesson_identity_guard on public.lesson_changes;
create trigger ops_lesson_identity_guard before update or delete on public.lesson_changes for each row execute function public.ops_lesson_identity_check();
revoke all on function public.ops_lesson_identity_check() from public,anon,authenticated;

-- Public helpers are not anonymous APIs. Default PostgreSQL PUBLIC execute is revoked explicitly.
revoke all on function public.ops_role(), public.ops_can(text), public.ops_access(), public.ops_staff(), public.ops_set_role(uuid,text), public.ops_complete_task(bigint), public.ops_monthly_bill(date,date), public.ops_tenant_check(), public.ops_record_change(), public.ops_appointment_check() from public,anon;
grant execute on function public.ops_role(), public.ops_can(text), public.ops_access(), public.ops_staff(), public.ops_set_role(uuid,text), public.ops_complete_task(bigint), public.ops_monthly_bill(date,date) to authenticated;
notify pgrst, 'reload schema';
commit;
