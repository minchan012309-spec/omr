-- 신규 브라우저 조판 PDF의 불변 쪽 명세. 개인 정보·PDF·폰트·LaTeX 원문은 저장하지 않는다.
create table if not exists public.latex_manifests (
 id uuid primary key,
 manifest jsonb not null,
 digest text not null check (digest ~ '^[0-9a-f]{64}$'),
 created_at timestamptz not null default now()
);
alter table public.latex_manifests enable row level security;
revoke all on public.latex_manifests from anon, authenticated;
create index if not exists latex_manifests_created_at on public.latex_manifests(created_at);

create or replace function public.latex_manifest_create(p_id uuid,p_manifest jsonb,p_digest text)
returns boolean language plpgsql security definer set search_path=pg_catalog as $$
declare p jsonb; c jsonb; clean jsonb := '[]'; cs jsonb; nums jsonb; num text;
begin
 if p_manifest->>'printEngine' is distinct from 'xelatex-v1' or p_manifest->>'templateVersion' is distinct from 'haewon-2026-v1'
  or coalesce(p_manifest->>'subject','') not in ('me','cm','ph','hl','aim')
  or jsonb_typeof(p_manifest->'pages') is distinct from 'array'
  or pg_column_size(p_manifest)>524288 then raise exception 'invalid manifest'; end if;
 if jsonb_array_length(p_manifest->'pages') not between 1 and 500 then raise exception 'page limit'; end if;
 if p_manifest->>'material'='worksheet' and coalesce(p_manifest->>'worksheetId','') !~ '^[0-9]{8}$' then raise exception 'invalid worksheet'; end if;
 for p in select value from jsonb_array_elements(p_manifest->'pages') loop
  if coalesce(p->>'kind','') not in ('questions','answers','quick','concept','cover','back','blank','contents','notes')
   or jsonb_typeof(p->'codes') is distinct from 'array' then raise exception 'invalid page'; end if;
  if jsonb_array_length(p->'codes')>300 then raise exception 'code limit'; end if;
  cs := '[]';
  for c in select value from jsonb_array_elements(p->'codes') loop
   if jsonb_typeof(c)<>'string' or (c #>> '{}') !~ '^[A-Za-z0-9_.~\-]{1,150}$' then raise exception 'invalid code'; end if;
   cs := cs || jsonb_build_array(c);
  end loop;
  nums := '{}';for c in select value from jsonb_array_elements(cs) loop num := p->'nums'->>(c #>> '{}');if num is not null and num ~ '^[0-9]{1,6}$' then nums := nums || jsonb_build_object(c #>> '{}',num::integer);end if;end loop;
  clean := clean || jsonb_build_array(jsonb_build_object('kind',p->>'kind','codes',cs,'nums',nums));
 end loop;
 perform pg_advisory_xact_lock(2720261119);
 if (select count(*) from public.latex_manifests where created_at>now()-interval '1 hour')>=1000 then raise exception 'hourly limit'; end if;
 insert into public.latex_manifests(id,manifest,digest) values(p_id,jsonb_build_object('printEngine','xelatex-v1','templateVersion','haewon-2026-v1','subject',p_manifest->>'subject','bookId',case when p_manifest->>'bookId' ~ '^[A-Za-z0-9_.~\-]{1,2000}$' then p_manifest->>'bookId' else null end,'material',case when p_manifest->>'material'='worksheet' then 'worksheet' else 'book' end,'worksheetId',case when p_manifest->>'material'='worksheet' then p_manifest->>'worksheetId' else null end,'pages',clean),p_digest);
 return true;
end $$;
create or replace function public.latex_manifest_read(p_id uuid)
returns jsonb language sql stable security definer set search_path=pg_catalog as $$
 select manifest from public.latex_manifests where id=p_id
$$;
revoke all on function public.latex_manifest_create(uuid,jsonb,text) from public;
revoke all on function public.latex_manifest_read(uuid) from public;
grant execute on function public.latex_manifest_create(uuid,jsonb,text) to anon,authenticated;
grant execute on function public.latex_manifest_read(uuid) to anon,authenticated;
