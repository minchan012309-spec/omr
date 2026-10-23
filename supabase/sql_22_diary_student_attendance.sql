-- =====================================================================
-- 22. 알림장(학생·학부모 공지 통합) + 학생용 출결 달력
-- Supabase SQL Editor 에서 통째로 실행. 다시 실행해도 안전해요. (sql_20, sql_21 다음)
-- =====================================================================

-- 22-1) 학부모 알림 목록: 예전 「학부모 공지(notices, audience=parent/all)」와 안내문(parent_notices)을 함께 보여줘요.
--       (sql_20 이 같은 이름의 함수를 덮어써서 예전 공지가 안 보이던 것을 바로잡아요)
create or replace function pa_notices(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare a parent_accounts%rowtype;
begin
  a := _pa_auth(p_login, p_pw);
  if a.id is null then return null; end if;
  return (
    select coalesce(json_agg(json_build_object('id', x.id, 'title', x.title, 'body', x.body, 't', x.t) order by x.t desc), '[]'::json)
    from (
      select (-1 * p.id) as id, p.title, p.body, (extract(epoch from p.created_at) * 1000)::bigint as t
        from parent_notices p where p.user_id = a.user_id and (p.student_id is null or p.student_id = a.student_id)
      union all
      select n.id, n.title, n.body, n.t
        from notices n where n.user_id = a.user_id and (n.student_id is null or n.student_id = a.student_id)
         and coalesce(n.audience, 'student') in ('parent', 'all')
      order by t desc limit 60
    ) x);
end $$;
grant execute on function pa_notices(text, text) to anon, authenticated;

-- 22-2) 학생 앱의 출결 달력 (날짜와 상태만, 시각·납부 정보는 주지 않아요)
create or replace function st_attendance(p_login text, p_pw text, p_from date, p_to date) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return (select coalesce(json_agg(json_build_object('day', x.day, 'status', x.status) order by x.day), '[]'::json)
          from attendance x where x.student_id = s.id and x.day between p_from and p_to);
end $$;
grant execute on function st_attendance(text, text, date, date) to anon, authenticated;
