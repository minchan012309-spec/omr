-- 24. 운영 업무·상담 예약·휴강/대체수업·역할별 권한·중복 청구 방지
-- sql_23_admin.sql 이후 실행. 데이터 삭제 없음. 기존 공동 강사는 teacher 역할로 유지.
-- 먼저 복제한 테스트 DB에서 검증하고 백업 후 운영에 적용하세요.
begin;
alter table public.academy_members add column if not exists role text not null default 'teacher' check (role in ('teacher','staff'));
create or replace function public.ops_role() returns text
language sql stable security definer set search_path=public as $$
 select case when auth.uid() is null then null else coalesce((select role from academy_members where member_id=auth.uid()),'owner') end
$$;
create or replace function public.ops_can(p_cap text) returns boolean
language sql stable security definer set search_path=public as $$
 select coalesce(case when ops_role()='owner' then true when p_cap='operations' then ops_role() in ('teacher','staff') when p_cap='billing' then ops_role()='staff' when p_cap='learning' then ops_role()='teacher' else false end,false)
$$;
create or replace function public.ops_access() returns json
language sql stable security definer set search_path=public as $$
 select json_build_object('role',ops_role(),'operations',ops_can('operations'),'billing',ops_can('billing'),'learning',ops_can('learning'),'manage',ops_can('manage'))
$$;
create or replace function public.ops_staff() returns json
language plpgsql stable security definer set search_path=public as $$
begin
 if not ops_can('manage') then raise exception 'forbidden' using errcode='42501'; end if;
 return (select coalesce(json_agg(json_build_object('member_id',member_id,'label',label,'role',role)),'[]'::json) from academy_members where owner_id=auth.uid());
end $$;
create or replace function public.ops_set_role(p_member uuid,p_role text) returns void
language plpgsql security definer set search_path=public as $$
begin
 if not ops_can('manage') or p_role not in ('teacher','staff') then raise exception 'forbidden' using errcode='42501'; end if;
 update academy_members set role=p_role where owner_id=auth.uid() and member_id=p_member;
 if not found then raise exception 'member not found'; end if;
end $$;

-- Restrictive gates intersect existing permissive tenant policies instead of replacing them.
-- SECURITY DEFINER student/parent RPCs keep their existing child authentication checks.
do $$ declare r record; cap text; begin
 for r in select tablename from pg_tables where schemaname='public' and tablename in
 ('students','classes','class_members','counsels','makeups','attendance','parent_notices','parent_accounts','fees','attempts','worksheets','assignments','wrong_notes') loop
 cap:=case when r.tablename='parent_accounts' then 'manage' when r.tablename='fees' then 'billing' when r.tablename in ('attempts','worksheets','assignments','wrong_notes') then 'learning' else 'operations' end;
 execute format('drop policy if exists ops_role_gate on public.%I',r.tablename);
 execute format('create policy ops_role_gate on public.%I as restrictive for all to authenticated using (public.ops_can(%L)) with check (public.ops_can(%L))',r.tablename,cap,cap);
 end loop;
end $$;

create table if not exists public.ops_tasks (
 id bigint generated always as identity primary key,
 user_id uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
 title text not null check (length(trim(title)) between 1 and 160),
 student_id uuid references public.students(id) on delete set null,
 assignee text not null default '' check (length(assignee)<=80),
 due_on date not null,
 repeat_kind text not null default 'none' check (repeat_kind in ('none','daily','weekly','monthly')),
 anchor_day smallint check (anchor_day between 1 and 31),
 completed_at timestamptz,
 previous_id bigint unique references public.ops_tasks(id) on delete set null,
 created_at timestamptz not null default now()
);
create index if not exists ops_tasks_due on public.ops_tasks(user_id,due_on) where completed_at is null;
create table if not exists public.counsel_appointments (
 id bigint generated always as identity primary key,
 user_id uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
 student_id uuid not null references public.students(id) on delete cascade,
 starts_at timestamptz not null,
 ends_at timestamptz not null,
 assignee text not null check (length(trim(assignee)) between 1 and 80),
 kind text not null default '학부모' check (kind in ('학생','학부모','입학','진로','기타')),
 status text not null default '예정' check (status in ('예정','완료','취소')),
 memo text not null default '' check (length(memo)<=3000),
 created_at timestamptz not null default now(),
 check (ends_at>starts_at)
);
create index if not exists counsel_appointments_time on public.counsel_appointments(user_id,starts_at);
create table if not exists public.lesson_changes (
 id bigint generated always as identity primary key,
 user_id uuid not null default public.acad_owner() references auth.users(id) on delete cascade,
 class_id bigint not null references public.classes(id) on delete cascade,
 on_date date not null,
 kind text not null check (kind in ('휴강','대체')),
 starts_at timestamptz,
 ends_at timestamptz,
 room text check (length(room)<=80),
 teacher text check (length(teacher)<=80),
 reason text not null default '' check (length(reason)<=500),
 unique(class_id,on_date),
 check ((kind='휴강' and starts_at is null and ends_at is null) or (kind='대체' and starts_at is not null and ends_at is not null and ends_at>starts_at))
);
create index if not exists lesson_changes_owner_day on public.lesson_changes(user_id,on_date);
create table if not exists public.ops_audit (
 id bigint generated always as identity primary key,
 user_id uuid not null,
 actor_id uuid,
 table_name text not null,
 row_id text not null,
 action text not null,
 created_at timestamptz not null default now()
);
alter table public.ops_audit enable row level security;
drop policy if exists ops_audit_read on public.ops_audit;
create policy ops_audit_read on public.ops_audit for select to authenticated using (user_id=public.acad_owner() and public.ops_can('manage'));

-- Cross-academy references cannot be smuggled into rows even when their owner_id is valid.
create or replace function public.ops_tenant_check() returns trigger
language plpgsql security definer set search_path=public as $$
declare j jsonb:=to_jsonb(new); oid uuid; begin
 oid:=(j->>'user_id')::uuid;
 if j->>'student_id' is not null and not exists(select 1 from students where id=(j->>'student_id')::uuid and user_id=oid) then raise exception 'student outside academy' using errcode='23514'; end if;
 if j->>'class_id' is not null and not exists(select 1 from classes where id=(j->>'class_id')::bigint and user_id=oid) then raise exception 'class outside academy' using errcode='23514'; end if;
 if j->>'previous_id' is not null and not exists(select 1 from ops_tasks where id=(j->>'previous_id')::bigint and user_id=oid) then raise exception 'task outside academy' using errcode='23514'; end if;
 return new;
end $$;
create or replace function public.ops_record_change() returns trigger
language plpgsql security definer set search_path=public as $$
declare j jsonb; begin
 if tg_op='DELETE' then j:=to_jsonb(old); else j:=to_jsonb(new); end if;
 insert into ops_audit(user_id,actor_id,table_name,row_id,action) values ((j->>'user_id')::uuid,auth.uid(),tg_table_name,j->>'id',tg_op);
 if tg_op='DELETE' then return old; else return new; end if;
end $$;
do $$ declare t text; begin
 foreach t in array array['ops_tasks','counsel_appointments','lesson_changes'] loop
 execute format('alter table public.%I enable row level security',t);
 execute format('drop policy if exists ops_tenant on public.%I',t);
 execute format('create policy ops_tenant on public.%I for all to authenticated using (user_id=public.acad_owner() and public.ops_can(''operations'')) with check (user_id=public.acad_owner() and public.ops_can(''operations''))',t);
 execute format('grant select,insert,update,delete on public.%I to authenticated',t);
 end loop;
 foreach t in array array['ops_tasks','counsel_appointments','lesson_changes','class_members','counsels','makeups','attendance','fees','parent_accounts','attempts','worksheets','assignments'] loop
 execute format('drop trigger if exists ops_tenant_guard on public.%I',t);
 execute format('create trigger ops_tenant_guard before insert or update on public.%I for each row execute function public.ops_tenant_check()',t);
 end loop;
 foreach t in array array['ops_tasks','counsel_appointments','lesson_changes','fees','counsels'] loop
 execute format('drop trigger if exists ops_change_log on public.%I',t);
 execute format('create trigger ops_change_log after insert or update or delete on public.%I for each row execute function public.ops_record_change()',t);
 end loop;
end $$;
grant select on public.ops_audit to authenticated;
grant usage,select on all sequences in schema public to authenticated;

-- Serialize conflicting appointments per academy; adjacent appointments are allowed.
create or replace function public.ops_appointment_check() returns trigger
language plpgsql security definer set search_path=public as $$
begin
 perform pg_advisory_xact_lock(hashtextextended(new.user_id::text||':appointments',0));
 if new.status='예정' and exists(select 1 from counsel_appointments x where x.user_id=new.user_id and x.id<>new.id and x.status='예정' and (x.assignee=new.assignee or x.student_id=new.student_id) and x.starts_at<new.ends_at and new.starts_at<x.ends_at) then raise exception '상담 일정이 겹쳐요' using errcode='23514'; end if;
 return new;
end $$;
drop trigger if exists ops_appointment_guard on public.counsel_appointments;
create trigger ops_appointment_guard before insert or update on public.counsel_appointments for each row execute function public.ops_appointment_check();

create or replace function public.ops_complete_task(p_id bigint) returns json
language plpgsql security definer set search_path=public as $$
declare x ops_tasks%rowtype; nd date; nid bigint; anchor int; begin
 if not ops_can('operations') then raise exception 'forbidden' using errcode='42501'; end if;
 select * into x from ops_tasks where id=p_id and user_id=acad_owner() for update;
 if not found then raise exception 'task not found'; end if;
 if x.completed_at is not null then return json_build_object('completed',x.id,'next_id',(select id from ops_tasks where previous_id=x.id)); end if;
 anchor:=coalesce(x.anchor_day,extract(day from x.due_on)::int);
 nd:=case x.repeat_kind when 'daily' then x.due_on+1 when 'weekly' then x.due_on+7 when 'monthly' then (date_trunc('month',x.due_on)+interval '1 month')::date+least(anchor,extract(day from date_trunc('month',x.due_on)+interval '2 months - 1 day')::int)-1 else null end;
 update ops_tasks set completed_at=now() where id=x.id;
 if nd is not null then insert into ops_tasks(user_id,title,student_id,assignee,due_on,repeat_kind,anchor_day,previous_id) values(x.user_id,x.title,x.student_id,x.assignee,nd,x.repeat_kind,anchor,x.id) returning id into nid; end if;
 return json_build_object('completed',x.id,'next_id',nid);
end $$;

alter table public.fees add column if not exists billing_key text;
create unique index if not exists fees_billing_key on public.fees(user_id,billing_key) where billing_key is not null;
create or replace function public.ops_monthly_bill(p_month date,p_due date) returns json
language plpgsql security definer set search_path=public as $$
declare oid uuid:=acad_owner(); n integer; begin
 if not ops_can('billing') then raise exception 'forbidden' using errcode='42501'; end if;
 if p_month is null or p_month<>date_trunc('month',p_month)::date or p_due is null then raise exception '청구 월과 납부 기한을 확인해 주세요'; end if;
 perform pg_advisory_xact_lock(hashtextextended(oid::text||':billing:'||p_month::text,0));
 insert into fees(user_id,student_id,kind,title,amount,due,billing_key)
 select oid,s.id,'tuition',extract(year from p_month)::int||'년 '||extract(month from p_month)::int||'월 '||c.name||' 수강료',c.tuition,p_due,to_char(p_month,'YYYY-MM')||':'||c.id||':'||s.id
 from classes c join class_members m on m.class_id=c.id and m.user_id=oid join students s on s.id=m.student_id and s.user_id=oid
 where c.user_id=oid and c.active and c.tuition>0 and s.status='재원'
 and not exists(select 1 from fees f where f.user_id=oid and f.student_id=s.id and f.billing_key is null and f.title=extract(year from p_month)::int||'년 '||extract(month from p_month)::int||'월 '||c.name||' 수강료')
 on conflict (user_id,billing_key) where billing_key is not null do nothing;
 get diagnostics n=row_count;
 return json_build_object('created',n);
end $$;

-- Child credentials imply access to child/guardian RPCs, so provisioning is capability protected too.
-- Do not expose password hashes through REST; preserve nonsecret fields used by old clients.
do $$ declare r record; d text; capability text; cols text; t text; begin
 for r in select p.oid,p.proname from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.proname in ('issue_login','revoke_login','parent_issue','parent_revoke','approve_signup') loop
 capability:=case when r.proname in ('issue_login','revoke_login') then 'learning' else 'manage' end;
 d:=pg_get_functiondef(r.oid);
 if d not like '%-- ops credential gate%' then
 d:=regexp_replace(d,'\y[Bb][Ee][Gg][Ii][Nn]\y','begin'||chr(10)||' -- ops credential gate'||chr(10)||format(' if not public.ops_can(%L) then raise exception ''forbidden'' using errcode=''42501''; end if;',capability));
 execute d;
 end if;
 end loop;
 foreach t in array array['students','signup_requests'] loop
 if to_regclass('public.'||t) is null then continue; end if;
 select string_agg(quote_ident(column_name),',') into cols from information_schema.columns where table_schema='public' and table_name=t and column_name not in ('pw_hash','password','password_hash');
 execute format('revoke select on public.%I from public,anon,authenticated',t);
 execute format('revoke select (pw_hash) on public.%I from public,anon,authenticated',t);
 execute format('grant select (%s) on public.%I to authenticated',cols,t);
 end loop;
end $$;
create or replace function public.ops_credential_check() returns trigger
language plpgsql security definer set search_path=public as $$
begin
 if auth.uid() is not null and not ops_can('learning') then
 if tg_op='INSERT' then
 if new.login is not null or new.pw_hash is not null then raise exception 'credential provisioning requires learning permission' using errcode='42501'; end if;
 elsif new.login is distinct from old.login or new.pw_hash is distinct from old.pw_hash then raise exception 'credential provisioning requires learning permission' using errcode='42501';
 end if;
 end if;
 return new;
end $$;
drop trigger if exists ops_credential_guard on public.students;
create trigger ops_credential_guard before insert or update on public.students for each row execute function public.ops_credential_check();
revoke all on function public.ops_credential_check() from public,anon,authenticated;

-- Add early departure without rewriting any existing attendance rows.
alter table public.attendance drop constraint if exists attendance_status_check;
alter table public.attendance add constraint attendance_status_check check (status in ('in','late','absent','excused','early'));

-- Existing student/parent schedule RPCs call this helper, so exceptions share their child authentication.
create or replace function public._sched_of(p_owner uuid,p_student uuid,p_counsel boolean) returns json
language sql stable security definer set search_path=public as $$
 select json_build_object(
 'classes',(select coalesce(json_agg(json_build_object('id',c.id,'name',c.name,'subject',c.subject,'teacher',c.teacher,'room',c.room,'sched',c.sched,'color',c.color) order by c.name),'[]'::json) from classes c join class_members m on m.class_id=c.id where c.user_id=p_owner and m.student_id=p_student and c.active),
 'makeups',(select coalesce(json_agg(json_build_object('missed_on',k.missed_on,'plan_at',k.plan_at,'status',k.status,'reason',k.reason,'class',(select name from classes where id=k.class_id)) order by k.missed_on desc),'[]'::json) from makeups k where k.user_id=p_owner and k.student_id=p_student),
 'counsels',case when p_counsel then (select coalesce(json_agg(json_build_object('day',c.day,'kind',c.kind,'body',c.body,'next_on',c.next_on,'next_todo',c.next_todo) order by c.day desc),'[]'::json) from counsels c where c.user_id=p_owner and c.student_id=p_student and c.share) else '[]'::json end,
 'lesson_changes',(select coalesce(json_agg(json_build_object('class_id',l.class_id,'on_date',l.on_date,'kind',l.kind,'starts_at',l.starts_at,'ends_at',l.ends_at,'room',l.room,'teacher',l.teacher,'reason',l.reason,'class',c.name) order by l.on_date),'[]'::json) from lesson_changes l join classes c on c.id=l.class_id and c.active where l.user_id=p_owner and l.on_date>=(now() at time zone 'Asia/Seoul')::date-30 and exists(select 1 from class_members m where m.class_id=l.class_id and m.student_id=p_student))
 )
$$;
revoke all on function public._sched_of(uuid,uuid,boolean) from public,anon,authenticated;

-- Preserve teaching preferences while enforcing payment/academy-settings ownership at the DB boundary.
create or replace function public.ops_settings_check() returns trigger
language plpgsql security definer set search_path=public as $$
declare previous jsonb; begin
 if auth.uid() is null then return new; end if;
 select data into previous from teacher_settings where user_id=new.user_id;
 if not ops_can('billing') and new.data->'pay' is distinct from previous->'pay' then raise exception 'billing settings require permission' using errcode='42501'; end if;
 if not ops_can('manage') and new.data->'perms' is distinct from previous->'perms' then raise exception 'academy settings require owner permission' using errcode='42501'; end if;
 return new;
end $$;
drop trigger if exists ops_settings_guard on public.teacher_settings;
create trigger ops_settings_guard before insert or update on public.teacher_settings for each row execute function public.ops_settings_check();
revoke all on function public.ops_settings_check() from public,anon,authenticated;

-- Date-aware replacement conflicts, including other replacements and excluding cancelled regular lessons.
create or replace function public.ops_lesson_check() returns trigger
language plpgsql security definer set search_path=public as $$
declare target date; rm text; tr text; begin
 if new.kind='휴강' or new.starts_at is null or new.ends_at is null then return new; end if;
 perform pg_advisory_xact_lock(hashtextextended(new.user_id::text||':lessons',0));
 target:=(new.starts_at at time zone 'Asia/Seoul')::date;
 if (new.ends_at at time zone 'Asia/Seoul')::date<>target then raise exception '대체수업은 같은 날에 시작하고 끝나야 해요' using errcode='23514'; end if;
 select coalesce(nullif(trim(new.room),''),nullif(trim(c.room),'')),coalesce(nullif(trim(new.teacher),''),nullif(trim(c.teacher),'')) into rm,tr from classes c where c.id=new.class_id;
 if exists(
 select 1 from lesson_changes l join classes c on c.id=l.class_id
 where l.user_id=new.user_id and l.id<>new.id and l.kind='대체' and c.active
 and l.starts_at<new.ends_at and new.starts_at<l.ends_at
 and ((rm is not null and rm=coalesce(nullif(trim(l.room),''),nullif(trim(c.room),''))) or (tr is not null and tr=coalesce(nullif(trim(l.teacher),''),nullif(trim(c.teacher),''))))
 ) or exists(
 select 1 from classes c cross join lateral jsonb_array_elements(c.sched) t
 where c.user_id=new.user_id and c.active
 and not(c.id=new.class_id and new.on_date=target)
 and t->>'d'=extract(isodow from target)::int::text
 and t->>'s' ~ '^([01][0-9]|2[0-3]):[0-5][0-9]$' and t->>'e' ~ '^([01][0-9]|2[0-3]):[0-5][0-9]$'
 and not exists(select 1 from lesson_changes l where l.class_id=c.id and l.on_date=target and l.id<>new.id)
 and ((rm is not null and rm=nullif(trim(c.room),'')) or (tr is not null and tr=nullif(trim(c.teacher),'')))
 and ((target+(t->>'s')::time) at time zone 'Asia/Seoul')<new.ends_at
 and new.starts_at<((target+(t->>'e')::time) at time zone 'Asia/Seoul')
 ) then raise exception '강사 또는 강의실의 수업 시간이 겹쳐요' using errcode='23514'; end if;
 return new;
end $$;
drop trigger if exists ops_lesson_guard on public.lesson_changes;
create trigger ops_lesson_guard before insert or update on public.lesson_changes for each row execute function public.ops_lesson_check();
revoke all on function public.ops_lesson_check() from public,anon,authenticated;

-- Keep the date/class identity of an exception. Moving/deleting it would silently restore
-- a regular lesson on an already-booked date. Restore via a replacement at the original time.
create or replace function public.ops_lesson_identity_check() returns trigger
language plpgsql security definer set search_path=public as $$
begin
 if tg_op='DELETE' then
 if pg_trigger_depth()>1 then return old; end if; -- parent class/account cascade also removes the regular lesson
 raise exception '수업 변경 이력은 삭제할 수 없어요. 원래 시간의 대체수업으로 복원해 주세요' using errcode='23514';
 end if;
 if new.class_id is distinct from old.class_id or new.on_date is distinct from old.on_date then raise exception '수업 변경의 반과 원래 날짜는 바꿀 수 없어요. 원래 시간의 대체수업으로 먼저 복원해 주세요' using errcode='23514'; end if;
 return new;
end $$;
drop trigger if exists ops_lesson_identity_guard on public.lesson_changes;
create trigger ops_lesson_identity_guard before update or delete on public.lesson_changes for each row execute function public.ops_lesson_identity_check();
revoke all on function public.ops_lesson_identity_check() from public,anon,authenticated;

-- Public helpers are not anonymous APIs. Default PostgreSQL PUBLIC execute is revoked explicitly.
revoke all on function public.ops_role(), public.ops_can(text), public.ops_access(), public.ops_staff(), public.ops_set_role(uuid,text), public.ops_complete_task(bigint), public.ops_monthly_bill(date,date), public.ops_tenant_check(), public.ops_record_change(), public.ops_appointment_check() from public,anon;
grant execute on function public.ops_role(), public.ops_can(text), public.ops_access(), public.ops_staff(), public.ops_set_role(uuid,text), public.ops_complete_task(bigint), public.ops_monthly_bill(date,date) to authenticated;
notify pgrst, 'reload schema';
commit;
