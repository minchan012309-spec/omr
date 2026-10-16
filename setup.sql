-- Supabase 대시보드 > SQL Editor 에 통째로 붙여넣고 Run.
-- 이미 이전 버전을 실행했어도 다시 실행해도 됩니다(기존 데이터는 그대로).

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
  return coalesce((select data->'perms' from teacher_settings where user_id = s.user_id), '{}'::jsonb)::json;
end $$;
grant execute on function st_perms(text, text) to anon, authenticated;

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
           exists (select 1 from developers d where d.user_id = u.id) as dev
    from auth.users u limit 500) x);
end $$;
grant execute on function dev_users() to authenticated;

-- 15-6) 개발자 등록 ▶ 아래 이메일을 바꾸고 실행
insert into developers (user_id, email)
select id, email from auth.users where email = '여기에_개발자_이메일@example.com'
on conflict (user_id) do nothing;
