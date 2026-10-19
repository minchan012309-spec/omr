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
