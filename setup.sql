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
