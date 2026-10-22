-- =====================================================================
-- 21. 한 학원을 여러 선생님 계정이 함께 쓰기 (대표 선생님 + 공동 선생님)
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
create table if not exists academy_invites (
  code       text primary key,
  owner_id   uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default now() + interval '7 days'
);
-- 정책을 만들지 않으면 일반 사용자는 직접 읽거나 쓸 수 없고, 아래 함수로만 접근해요.
alter table academy_members enable row level security;
alter table academy_invites enable row level security;

-- 데이터 주인: 공동 선생님이면 대표 선생님, 아니면 본인
create or replace function acad_owner() returns uuid
language sql stable security definer set search_path = public as $$
  select coalesce((select owner_id from academy_members where member_id = auth.uid()), auth.uid())
$$;
grant execute on function acad_owner() to anon, authenticated;

-- 대표 선생님: 초대 코드 만들기 (7일 동안 한 번만 쓸 수 있어요)
create or replace function acad_invite() returns text
language plpgsql security definer set search_path = public, extensions as $$
declare c text; n int := 0; al text := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
begin
  if auth.uid() is null or exists (select 1 from academy_members where member_id = auth.uid()) then raise exception 'not allowed'; end if;
  delete from academy_invites where expires_at < now();
  if (select count(*) from academy_invites where owner_id = auth.uid()) >= 10 then raise exception 'too many invites'; end if;
  loop
    c := '';
    for i in 1..8 loop c := c || substr(al, 1 + floor(random() * length(al))::int, 1); end loop;
    begin
      insert into academy_invites (code, owner_id) values (c, auth.uid());
      return c;
    exception when unique_violation then
      n := n + 1; if n > 20 then raise exception 'try again'; end if;
    end;
  end loop;
end $$;

-- 공동 선생님: 코드로 합류 (이미 학생 데이터를 가진 계정은 합류할 수 없어요 — 데이터가 가려지는 걸 막기 위해)
create or replace function acad_join(p_code text, p_label text default null) returns boolean
language plpgsql security definer set search_path = public, extensions as $$
declare iv academy_invites%rowtype;
begin
  if auth.uid() is null then raise exception 'not allowed'; end if;
  select * into iv from academy_invites where code = upper(trim(p_code)) and expires_at > now();
  if not found then return false; end if;
  if iv.owner_id = auth.uid() then raise exception 'self'; end if;
  if exists (select 1 from academy_members where member_id = auth.uid() or owner_id = auth.uid()) then raise exception 'already'; end if;
  if exists (select 1 from students where user_id = auth.uid()) then raise exception 'has data'; end if;
  insert into academy_members (member_id, owner_id, label) values (auth.uid(), iv.owner_id, nullif(trim(coalesce(p_label, '')), ''));
  delete from academy_invites where code = iv.code;
  return true;
end $$;

create or replace function acad_info() returns json
language plpgsql security definer set search_path = public, extensions as $$
declare m academy_members%rowtype;
begin
  if auth.uid() is null then return null; end if;
  select * into m from academy_members where member_id = auth.uid();
  if found then
    return json_build_object('role', 'member', 'owner', (select email from auth.users where id = m.owner_id));
  end if;
  return json_build_object('role', 'owner',
    'members', (select coalesce(json_agg(json_build_object('id', a.member_id, 'label', a.label, 'email', u.email, 't', a.created_at) order by a.created_at), '[]'::json)
                from academy_members a join auth.users u on u.id = a.member_id where a.owner_id = auth.uid()),
    'invites', (select coalesce(json_agg(json_build_object('code', i.code, 'exp', i.expires_at) order by i.created_at desc), '[]'::json)
                from academy_invites i where i.owner_id = auth.uid() and i.expires_at > now()));
end $$;

create or replace function acad_member_remove(p_member uuid) returns void
language plpgsql security definer set search_path = public as $$
begin
  delete from academy_members where member_id = p_member and owner_id = auth.uid();
end $$;
create or replace function acad_invite_revoke(p_code text) returns void
language plpgsql security definer set search_path = public as $$
begin
  delete from academy_invites where code = p_code and owner_id = auth.uid();
end $$;
create or replace function acad_leave() returns void
language plpgsql security definer set search_path = public as $$
begin
  delete from academy_members where member_id = auth.uid();
end $$;
grant execute on function acad_invite() to authenticated;
grant execute on function acad_join(text, text) to authenticated;
grant execute on function acad_info() to authenticated;
grant execute on function acad_member_remove(uuid) to authenticated;
grant execute on function acad_invite_revoke(text) to authenticated;
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
