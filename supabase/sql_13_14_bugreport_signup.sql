-- Supabase 대시보드 > SQL Editor 에 통째로 붙여넣고 Run 하세요. (13번 버그 신고 + 14번 학생 가입·승인)
-- 여러 번 실행해도 안전합니다. setup.sql 10~12번을 이미 실행한 상태여야 합니다.

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
