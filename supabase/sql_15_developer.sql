-- Supabase 대시보드 > SQL Editor 에 통째로 붙여넣고 Run 하세요. (15번 개발자 계정 · 사이트 공지 · 사이트 설정)
-- 여러 번 실행해도 안전합니다. 맨 아래 「개발자 등록」의 이메일을 본인 계정 이메일로 바꿔 한 번 더 실행하세요.
-- (그 이메일로 앱에서 먼저 선생님 회원가입을 해 두어야 합니다. 개발자는 별도 로그인 화면이 아니라 같은 로그인으로 들어오고, 등록된 계정에만 「개발자」 탭이 보입니다.)

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
