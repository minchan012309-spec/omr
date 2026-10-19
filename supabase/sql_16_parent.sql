-- =====================================================================
-- 16. 학부모 계정 (읽기 전용)
--   선생님이 학생마다 학부모 아이디/비밀번호를 발급하면, 학부모는 로그인해서 자녀의 학습 현황만 볼 수 있습니다.
--   (문제를 풀거나 제출하는 기능은 없고, 다른 학생의 정보는 볼 수 없습니다)
-- 이미 실행했어도 다시 실행해도 됩니다.
-- =====================================================================
create extension if not exists pgcrypto with schema extensions;

create table if not exists parent_accounts (
  id         bigint generated always as identity primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  login      text not null,
  pw_hash    text not null,
  label      text not null default '학부모',
  created_at timestamptz not null default now(),
  last_login timestamptz
);
create unique index if not exists parent_accounts_login_key on parent_accounts (lower(login));
create index if not exists parent_accounts_student on parent_accounts (student_id);
create table if not exists pa_tokens (
  token_hash text primary key,
  parent_id  bigint not null references parent_accounts(id) on delete cascade,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default now() + interval '90 days'
);
-- 정책을 만들지 않으면 일반 사용자는 표를 직접 읽거나 쓸 수 없고, 아래 함수로만 접근합니다.
alter table parent_accounts enable row level security;
alter table pa_tokens enable row level security;

-- 선생님: 발급(같은 아이디로 다시 발급하면 비밀번호 변경) · 해제 · 목록
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
    update parent_accounts set pw_hash = crypt(p_pw, gen_salt('bf')), label = lb where id = a.id;
    delete from pa_tokens where parent_id = a.id;
  else
    if (select count(*) from parent_accounts where student_id = p_student) >= 5 then raise exception 'too many accounts'; end if;
    insert into parent_accounts (user_id, student_id, login, pw_hash, label) values (auth.uid(), p_student, l, crypt(p_pw, gen_salt('bf')), lb);
  end if;
end $$;
create or replace function parent_revoke(p_id bigint) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  delete from parent_accounts where id = p_id and user_id = auth.uid();
end $$;
create or replace function parent_list() returns json
language plpgsql security definer set search_path = public, extensions as $$
begin
  return (select coalesce(json_agg(json_build_object('id', id, 'student_id', student_id, 'login', login, 'label', label, 'last_login', last_login) order by id), '[]'::json)
          from parent_accounts where user_id = auth.uid());
end $$;
grant execute on function parent_issue(uuid, text, text, text) to authenticated;
grant execute on function parent_revoke(bigint) to authenticated;
grant execute on function parent_list() to authenticated;

-- 학부모(비로그인): 비밀번호 또는 자동 로그인 토큰(「tok:<토큰>」)으로 확인
create or replace function _pa_auth(p_login text, p_pw text) returns parent_accounts
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype;
begin
  if p_pw like 'tok:%' then
    select pa.* into a from parent_accounts pa join pa_tokens t on t.parent_id = pa.id
      where lower(pa.login) = lower(trim(p_login)) and t.token_hash = encode(digest(substr(p_pw, 5), 'sha256'), 'hex') and t.expires_at > now() limit 1;
  else
    select * into a from parent_accounts where lower(login) = lower(trim(p_login)) and pw_hash = crypt(p_pw, pw_hash) limit 1;
  end if;
  if not found then return null; end if;
  return a;
end $$;
revoke all on function _pa_auth(text, text) from public, anon, authenticated;

create or replace function pa_login(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; s students%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  select * into s from students where id = a.student_id;
  update parent_accounts set last_login = now() where id = a.id;
  return json_build_object('id', a.id, 'label', a.label, 'student', json_build_object('id', s.id, 'name', s.name, 'grade', s.grade));
end $$;
create or replace function pa_data(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; s students%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  select * into s from students where id = a.student_id;
  return json_build_object(
    'label', a.label,
    'student', json_build_object('id', s.id, 'name', s.name, 'grade', s.grade),
    'attempts', (select coalesce(json_agg(json_build_object('t', x.t, 'set', x."set", 'sub', x.sub, 'items', x.items, 'rng', x.rng) order by x.t), '[]'::json)
                 from (select * from attempts where student_id = s.id order by t desc limit 400) x),
    'assignments', (select coalesce(json_agg(json_build_object('wid', y.wid, 'title', y.title, 'due', y.due, 'note', y.note, 't', y.t) order by y.t desc), '[]'::json)
                    from assignments y where y.student_id = s.id));
end $$;
create or replace function pa_issue_token(p_login text, p_pw text) returns text
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype; tok text;
begin
  if p_pw like 'tok:%' then return null; end if;
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  tok := encode(gen_random_bytes(32), 'hex');
  insert into pa_tokens (token_hash, parent_id) values (encode(digest(tok, 'sha256'), 'hex'), a.id);
  delete from pa_tokens where parent_id = a.id and expires_at < now();
  return tok;
end $$;
create or replace function pa_logout(p_login text, p_token text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  delete from pa_tokens where token_hash = encode(digest(p_token, 'sha256'), 'hex')
    and parent_id in (select id from parent_accounts where lower(login) = lower(trim(p_login)));
end $$;
grant execute on function pa_login(text, text) to anon, authenticated;
grant execute on function pa_data(text, text) to anon, authenticated;
grant execute on function pa_issue_token(text, text) to anon, authenticated;
grant execute on function pa_logout(text, text) to anon, authenticated;
