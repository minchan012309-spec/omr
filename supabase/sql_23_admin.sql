-- =====================================================================
-- 23. 학원 행정: 원생 정보 · 반 · 시간표 · 상담 일지 · 보강
-- Supabase 대시보드 > SQL Editor 에 통째로 붙여넣고 Run. 이미 실행했어도 다시 실행해도 됩니다.
-- 반드시 sql_21_shared_academy.sql 까지 모두 실행한 뒤에 실행하세요(공동 선생님이 같은 데이터를 보도록 acad_owner() 를 씀).
-- 실행하기 전에는 앱의 「학원 운영」 화면이 이 파일을 실행하라는 안내만 보여 주고, 다른 기능은 그대로 동작해요.
-- =====================================================================
create extension if not exists pgcrypto with schema extensions;

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
