-- 19) 학원 로고를 권한 응답에서 분리 (학생 앱이 1분마다 받는 응답이 로고(최대 160KB)만큼 커지는 것을 막음)
-- st_perms: perms에서 logo / logoDark 이미지는 빼고, 버전(logov)만 남깁니다.
-- st_academy: 학생이 로고 버전이 바뀌었을 때만 이미지를 받아 갑니다.
create or replace function st_perms(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  return coalesce((select (data->'perms') - 'logo' - 'logoDark' from teacher_settings where user_id = s.user_id), '{}'::jsonb)::json;
end $$;
grant execute on function st_perms(text, text) to anon, authenticated;

create or replace function st_academy(p_login text, p_pw text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s students%rowtype; p jsonb;
begin
  s := _st_auth(p_login, p_pw);
  if s.id is null then return null; end if;
  select data->'perms' into p from teacher_settings where user_id = s.user_id;
  return json_build_object('logo', coalesce(p->>'logo', ''), 'logoDark', coalesce(p->>'logoDark', ''), 'v', coalesce(p->>'logov', ''));
end $$;
grant execute on function st_academy(text, text) to anon, authenticated;
