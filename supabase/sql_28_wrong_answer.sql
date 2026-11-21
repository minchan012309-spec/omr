-- 선생님 채점 기록에서 「오답 문항에 학생이 쓴 답」만 나중에 고치는 함수. Supabase SQL 편집기에서 한 번 실행.
-- 정답 여부(r)는 바꾸지 않는다: r=0(오답) 문항의 a(학생 답)만 바뀐다. 오답 → 정답은 제출 초기화로만.
create or replace function public.attempt_wrong_answer(p_t bigint, p_code text, p_a text) returns void
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  if auth.uid() is null then raise exception 'not allowed'; end if;
  if length(coalesce(p_a, '')) > 60 then raise exception 'answer too long'; end if;
  update attempts a set items = (
      select jsonb_agg(case when x.e->>'c' = p_code and coalesce((x.e->>'r')::numeric, 0) = 0
                            then jsonb_set(x.e, '{a}', to_jsonb(coalesce(p_a, ''))) else x.e end order by x.ord)
      from jsonb_array_elements(a.items) with ordinality as x(e, ord))
  where a.user_id = auth.uid() and a.t = p_t
    and exists (select 1 from jsonb_array_elements(a.items) e where e->>'c' = p_code and coalesce((e->>'r')::numeric, 0) = 0);
  get diagnostics n = row_count;
  if n = 0 then raise exception 'wrong item not found'; end if;
end $$;
revoke all on function public.attempt_wrong_answer(bigint, text, text) from public, anon;
grant execute on function public.attempt_wrong_answer(bigint, text, text) to authenticated;
