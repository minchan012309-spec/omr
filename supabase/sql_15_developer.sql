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
           exists (select 1 from developers d where d.user_id = u.id) as dev
    from auth.users u limit 500) x);
end $$;
grant execute on function dev_users() to authenticated;

-- 15-6) 개발자 등록 ▶ 아래 이메일을 바꾸고 실행
insert into developers (user_id, email)
select id, email from auth.users where email = '여기에_개발자_이메일@example.com'
on conflict (user_id) do nothing;
