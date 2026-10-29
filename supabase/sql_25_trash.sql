-- Run once in the Supabase SQL editor. pg_cron must be enabled for the daily purge.
create extension if not exists pg_cron with schema extensions;

create or replace function public.ws_get(p_wid text) returns json
language sql security definer set search_path = public as $$
  select json_build_object('title', w.title, 'meta', w.meta, 'student', s.name,
    'submitted', (w.student_id is not null and exists (select 1 from attempts a where a.student_id = w.student_id and a."set" = 'ws' and a.sub = w.wid and a.t > coalesce((w.meta->>'resetAt')::bigint, 0))))
  from worksheets w left join students s on s.id = w.student_id
  where w.wid = upper(p_wid) and coalesce((w.meta->>'deletedAt')::bigint, 0) = 0 limit 1
$$;

create or replace function public.ws_submit(p_wid text, p_t bigint, p_items jsonb) returns void
language plpgsql security definer set search_path = public as $$
declare w worksheets%rowtype;
begin
  select * into w from worksheets where wid = upper(p_wid) and coalesce((meta->>'deletedAt')::bigint, 0) = 0 limit 1;
  if not found then raise exception 'worksheet not found'; end if;
  if w.student_id is not null and exists (select 1 from attempts a where a.student_id = w.student_id and a."set" = 'ws' and a.sub = w.wid and a.t > coalesce((w.meta->>'resetAt')::bigint, 0)) then
    raise exception 'already submitted';
  end if;
  insert into attempts (user_id, student_id, t, "set", sub, items)
  values (w.user_id, w.student_id, p_t, 'ws', w.wid, p_items);
end $$;

create or replace function public.book_access(p_book text, p_owner text default null) returns boolean
language sql security definer set search_path = public as $$
  select exists (
    select 1 from teacher_settings t, jsonb_array_elements(coalesce(t.data->'books', '[]'::jsonb)) b
    where b->>'id' = p_book and coalesce((b->>'deletedAt')::bigint, 0) = 0
      and (p_owner is null or t.user_id::text = p_owner)
      and not coalesce(t.data->'booksDel', '[]'::jsonb) ? p_book
      and (p_owner is not null or not exists (
        select 1 from teacher_settings x
        where coalesce(x.data->'booksDel', '[]'::jsonb) ? p_book
          or exists (select 1 from jsonb_array_elements(coalesce(x.data->'books', '[]'::jsonb)) z
            where z->>'id' = p_book and coalesce((z->>'deletedAt')::bigint, 0) > 0)
      ))
  )
$$;
revoke all on function public.book_access(text, text) from public;
grant execute on function public.book_access(text, text) to anon, authenticated;

create or replace function public.trash_purge() returns void
language plpgsql security definer set search_path = public as $$
declare t record; remaining jsonb; expired jsonb;
begin
  delete from worksheets
  where coalesce((meta->>'deletedAt')::bigint, 0) > 0
    and (meta->>'deletedAt')::bigint < (extract(epoch from now() - interval '30 days') * 1000)::bigint;

  for t in select user_id, data from teacher_settings loop
    select coalesce(jsonb_agg(b), '[]'::jsonb) into remaining
    from jsonb_array_elements(coalesce(t.data->'books', '[]'::jsonb)) b
    where coalesce((b->>'deletedAt')::bigint, 0) = 0
      or (b->>'deletedAt')::bigint >= (extract(epoch from now() - interval '30 days') * 1000)::bigint;
    select coalesce(jsonb_agg(b->>'id'), '[]'::jsonb) into expired
    from jsonb_array_elements(coalesce(t.data->'books', '[]'::jsonb)) b
    where coalesce((b->>'deletedAt')::bigint, 0) > 0
      and (b->>'deletedAt')::bigint < (extract(epoch from now() - interval '30 days') * 1000)::bigint;
    if jsonb_array_length(expired) > 0 then
      update teacher_settings set data = jsonb_set(
        jsonb_set(t.data, '{books}', remaining), '{booksDel}',
        coalesce(t.data->'booksDel', '[]'::jsonb) || expired
      ), updated_at = now() where user_id = t.user_id;
    end if;
  end loop;
end $$;
revoke all on function public.trash_purge() from public, anon, authenticated;

select cron.schedule('omr-trash-purge-daily', '17 3 * * *', 'select public.trash_purge()');
