-- 계정 스스로 바꾸기: 학생 · 학부모가 설정에서 아이디 · 비밀번호를 바꾸고,
-- 선생님이 발급한 계정은 처음 로그인할 때 아이디 · 비밀번호를 새로 정하게 한다.
-- Supabase SQL 편집기에서 한 번 실행(여러 번 실행해도 안전).
-- 선생님 계정의 비밀번호는 Supabase 인증(/auth/v1/user)으로 바꾸므로 여기에는 없다.

alter table students add column if not exists must_reset boolean not null default false;
alter table parent_accounts add column if not exists must_reset boolean not null default false;

-- 선생님이 발급(또는 다시 발급)한 계정은 다음 로그인에서 새로 정해야 한다.
-- 이미 쓰고 있는 계정은 그대로(must_reset 기본값 false): 이 스크립트를 실행한 뒤 발급한 계정부터 적용.
create or replace function issue_login(p_student uuid, p_login text, p_pw text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not exists (select 1 from students where id = p_student and user_id = auth.uid()) then
    raise exception 'not allowed';
  end if;
  if length(coalesce(p_pw,'')) < 4 then raise exception 'password too short'; end if;
  if length(coalesce(p_login,'')) < 3 then raise exception 'login too short'; end if;
  update students set login = lower(trim(p_login)), pw_hash = crypt(p_pw, gen_salt('bf')), must_reset = true where id = p_student;
  delete from st_tokens where student_id = p_student;
end $$;

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
    update parent_accounts set pw_hash = crypt(p_pw, gen_salt('bf')), label = lb, must_reset = true where id = a.id;
    delete from pa_tokens where parent_id = a.id;
  else
    if (select count(*) from parent_accounts where student_id = p_student) >= 5 then raise exception 'too many accounts'; end if;
    insert into parent_accounts (user_id, student_id, login, pw_hash, label, must_reset) values (auth.uid(), p_student, l, crypt(p_pw, gen_salt('bf')), lb, true);
  end if;
end $$;

-- 로그인 응답에 「새로 정해야 함」을 함께 돌려준다.
create or replace function st_login(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return json_build_object('id', s.id, 'name', s.name, 'grade', s.grade, 'must_reset', coalesce(s.must_reset, false));
end $$;

create or replace function pa_login(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; s students%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  select * into s from students where id = a.student_id;
  update parent_accounts set last_login = now() where id = a.id;
  return json_build_object('id', a.id, 'label', a.label, 'must_reset', coalesce(a.must_reset, false), 'student', json_build_object('id', s.id, 'name', s.name, 'grade', s.grade));
end $$;

-- 학생: 지금 비밀번호(자동 로그인 토큰은 안 됨)로 확인한 뒤 아이디 · 비밀번호를 바꾼다.
-- 결과: 'ok' | 'auth'(지금 비밀번호 틀림) | 'login'(아이디 형식) | 'pw'(비밀번호 6자 미만) | 'taken'(이미 쓰는 아이디)
create or replace function st_change_credentials(p_login text, p_pw text, p_new_login text, p_new_pw text) returns text
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype; nl text := lower(trim(coalesce(p_new_login, '')));
begin
  if coalesce(p_pw, '') like 'tok:%' then return 'auth'; end if;
  s := _st_auth(p_login, p_pw);
  if s.id is null then return 'auth'; end if;
  if nl !~ '^[a-z0-9_]{3,20}$' then return 'login'; end if;
  if length(coalesce(p_new_pw, '')) < 6 then return 'pw'; end if;
  if nl <> lower(s.login) and (exists (select 1 from students where lower(login) = nl and id <> s.id)
      or exists (select 1 from signup_requests where lower(login) = nl and status = 'pending')) then
    return 'taken';
  end if;
  update students set login = nl, pw_hash = crypt(p_new_pw, gen_salt('bf')), must_reset = false where id = s.id;
  delete from st_tokens where student_id = s.id;
  return 'ok';
end $$;

create or replace function pa_change_credentials(p_login text, p_pw text, p_new_login text, p_new_pw text) returns text
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; nl text := lower(trim(coalesce(p_new_login, '')));
begin
  if coalesce(p_pw, '') like 'tok:%' then return 'auth'; end if;
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return 'auth'; end if;
  if nl !~ '^[a-z0-9_]{3,20}$' then return 'login'; end if;
  if length(coalesce(p_new_pw, '')) < 6 then return 'pw'; end if;
  if nl <> lower(a.login) and exists (select 1 from parent_accounts where lower(login) = nl and id <> a.id) then return 'taken'; end if;
  update parent_accounts set login = nl, pw_hash = crypt(p_new_pw, gen_salt('bf')), must_reset = false where id = a.id;
  delete from pa_tokens where parent_id = a.id;
  return 'ok';
end $$;

revoke all on function st_change_credentials(text, text, text, text) from public;
revoke all on function pa_change_credentials(text, text, text, text) from public;
grant execute on function st_change_credentials(text, text, text, text) to anon, authenticated;
grant execute on function pa_change_credentials(text, text, text, text) to anon, authenticated;
grant execute on function st_login(text, text) to anon, authenticated;
grant execute on function pa_login(text, text) to anon, authenticated;
grant execute on function issue_login(uuid, text, text) to authenticated;
grant execute on function parent_issue(uuid, text, text, text) to authenticated;
