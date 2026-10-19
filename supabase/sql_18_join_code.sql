-- 18) 가입 코드 다시 만들기 (임의 입력 불가 · 서버가 무작위로 새로 만듦)
-- 선생님 화면: 학원 설정 → 가입 → 「코드 다시 만들기」. 이전 코드는 바로 못 쓰게 됩니다.
create or replace function join_code_regen() returns json
language plpgsql security definer set search_path = public, extensions as $$
declare c text; n int := 0; r teacher_join%rowtype;
begin
  if auth.uid() is null then raise exception 'not allowed'; end if;
  perform join_info();
  loop
    c := upper(substr(translate(encode(gen_random_bytes(9), 'base64'), '+/=lIO01', 'XYZABCDE'), 1, 6));
    exit when not exists (select 1 from teacher_join where code = c);
    n := n + 1;
    if n > 20 then raise exception 'try again'; end if;
  end loop;
  update teacher_join set code = c where user_id = auth.uid() returning * into r;
  return json_build_object('code', r.code, 'open', r.open);
end $$;
grant execute on function join_code_regen() to authenticated;
