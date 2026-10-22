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
