/* Isolated real PostgreSQL regression. npm install --prefix /tmp/solvi-db-tests @electric-sql/pglite */
const fs = require("node:fs"),
  assert = require("node:assert/strict");
const { PGlite } = require("./runtime.cjs");
const O = "00000000-0000-0000-0000-000000000001",
  T = "00000000-0000-0000-0000-000000000002",
  S = "00000000-0000-0000-0000-000000000003",
  X = "00000000-0000-0000-0000-000000000004",
  A = "10000000-0000-0000-0000-000000000001",
  B = "10000000-0000-0000-0000-000000000002";
(async () => {
  const db = new PGlite();
  let count = 0;
  const check = async (name, f) => {
    await f();
    count++;
    console.log("PASS", name);
  };
  const q = async (s) => (await db.query(s)).rows;
  const as = async (id) => {
    await db.exec("reset role");
    await db.query("select set_config('test.uid',$1,false)", [id || ""]);
    await db.exec("set role authenticated");
  };
  try {
    await db.exec(`create role anon;create role authenticated;create role service_role;create schema auth;create table auth.users(id uuid primary key);create function auth.uid() returns uuid language sql stable as $$select nullif(current_setting('test.uid',true),'')::uuid$$;grant usage on schema auth to authenticated,anon;grant execute on function auth.uid() to authenticated,anon;
create table academy_members(member_id uuid primary key references auth.users,owner_id uuid references auth.users,label text);alter table academy_members enable row level security;
create function acad_owner() returns uuid language sql stable security definer as $$select coalesce((select owner_id from academy_members where member_id=auth.uid()),auth.uid())$$;
create table students(id uuid primary key default gen_random_uuid(),user_id uuid not null default acad_owner() references auth.users,name text,grade text,phone text,memo text,t bigint,login text,pw_hash text);
create table fees(id bigint generated always as identity primary key,user_id uuid not null default acad_owner(),student_id uuid references students,kind text default 'tuition',title text,amount integer,paid_amount integer default 0,paid_at timestamptz,due date,created_at timestamptz default now());
create table attendance(id bigint generated always as identity primary key,user_id uuid not null default acad_owner(),student_id uuid references students,day date,status text check(status in ('in','late','absent','excused')),t_in timestamptz,t_out timestamptz);
create table parent_accounts(id uuid default gen_random_uuid(),user_id uuid default acad_owner(),student_id uuid references students);
create table attempts(id bigint generated always as identity primary key,user_id uuid default acad_owner(),student_id uuid references students,t bigint,items jsonb);
create table worksheets(id bigint generated always as identity primary key,user_id uuid default acad_owner(),student_id uuid references students);
create table assignments(id bigint generated always as identity primary key,user_id uuid default acad_owner(),student_id uuid references students);
create table teacher_settings(user_id uuid primary key default acad_owner(),data jsonb default '{}'::jsonb);
create table signup_requests(id bigint generated always as identity primary key,user_id uuid default acad_owner(),pw_hash text,login text);
create table wrong_notes(id bigint generated always as identity primary key,user_id uuid default acad_owner());
create table parent_notices(id bigint generated always as identity primary key,user_id uuid default acad_owner(),student_id uuid references students);
`);
    await db.exec(
      `create function issue_login(p_student uuid,p_login text,p_pw text) returns void language plpgsql security definer as $$begin update students set login=p_login,pw_hash=p_pw where id=p_student and user_id=acad_owner(); end$$;create function parent_issue(p_student uuid,p_login text,p_pw text,p_label text default '학부모') returns void language plpgsql security definer as $$begin insert into parent_accounts(user_id,student_id) values(acad_owner(),p_student); end$$;`,
    );
    await db.exec(
      fs
        .readFileSync("supabase/sql_23_admin.sql", "utf8")
        .replace(
          "create extension if not exists pgcrypto with schema extensions;",
          "",
        ),
    );
    for (const t of [
      "students",
      "fees",
      "attendance",
      "attempts",
      "worksheets",
      "assignments",
      "wrong_notes",
      "parent_accounts",
      "parent_notices",
      "signup_requests",
      "teacher_settings",
    ])
      await db.exec(
        `alter table ${t} enable row level security;create policy fixture_tenant on ${t} for all using(user_id=acad_owner()) with check(user_id=acad_owner())`,
      );
    await db.exec(
      "grant select,insert,update,delete on all tables in schema public to authenticated;grant usage,select on all sequences in schema public to authenticated",
    );
    await check("migration applies and is repeatable", async () => {
      await db.exec(fs.readFileSync("supabase/sql_24_operations.sql", "utf8"));
      await db.exec(fs.readFileSync("supabase/sql_24_operations.sql", "utf8"));
    });
    await db.exec(
      `insert into auth.users values('${O}'),('${T}'),('${S}'),('${X}');insert into academy_members(member_id,owner_id,label,role) values('${T}','${O}','강사','teacher'),('${S}','${O}','행정','staff');insert into students(id,user_id,name,status) values('${A}','${O}','검증학생','재원'),('${B}','${X}','다른학원','재원');insert into classes(user_id,name,tuition,sched,room,teacher) values('${O}','A반',100000,'[{"d":1,"s":"18:00","e":"20:00"}]','101','김');insert into class_members(class_id,student_id,user_id) values(1,'${A}','${O}');insert into attempts(user_id,student_id,t,items) values('${O}','${A}',1,'[{"c":"a","r":1}]');`,
    );
    await check(
      "owner can create monthly bill, repeated call creates no duplicate",
      async () => {
        await as(O);
        assert.equal(
          (
            await q("select ops_monthly_bill('2026-10-01','2026-10-10') as x")
          )[0].x.created,
          1,
        );
        assert.equal(
          (
            await q("select ops_monthly_bill('2026-10-01','2026-10-10') as x")
          )[0].x.created,
          0,
        );
        assert.equal((await q("select count(*)::int as n from fees"))[0].n, 1);
      },
    );
    await check(
      "renaming a class still cannot duplicate billing key",
      async () => {
        await db.exec("update classes set name='바뀐반' where id=1");
        assert.equal(
          (
            await q("select ops_monthly_bill('2026-10-01','2026-10-10') as x")
          )[0].x.created,
          0,
        );
      },
    );
    await check(
      "teacher cannot read fees or bill; can read learning",
      async () => {
        await as(T);
        assert.equal((await q("select count(*)::int n from fees"))[0].n, 0);
        assert.equal((await q("select count(*)::int n from attempts"))[0].n, 1);
        await assert.rejects(
          () => q("select ops_monthly_bill('2026-11-01','2026-11-10')"),
          /forbidden/,
        );
      },
    );
    await check(
      "staff can read fees but cannot read learning or change roles",
      async () => {
        await as(S);
        assert.equal((await q("select count(*)::int n from fees"))[0].n, 1);
        assert.equal((await q("select count(*)::int n from attempts"))[0].n, 0);
        await assert.rejects(
          () => q(`select ops_set_role('${T}','staff')`),
          /forbidden/,
        );
      },
    );
    await check(
      "cross-academy student references are rejected at database boundary",
      async () => {
        await as(O);
        await assert.rejects(
          () =>
            q(
              `insert into ops_tasks(title,student_id,due_on) values('테스트','${B}','2026-10-01')`,
            ),
          /outside academy/,
        );
        await assert.rejects(
          () =>
            q(
              `insert into class_members(class_id,student_id) values(1,'${B}')`,
            ),
          /outside academy/,
        );
      },
    );
    await check(
      "monthly recurring task completion is atomic and idempotent",
      async () => {
        await q(
          "insert into ops_tasks(title,due_on,repeat_kind) values('월말 정리','2026-01-31','monthly')",
        );
        const id = (
          await q("select id from ops_tasks where title='월말 정리'")
        )[0].id;
        const first = (await q(`select ops_complete_task(${id}) x`))[0].x;
        const second = (await q(`select ops_complete_task(${id}) x`))[0].x;
        assert.equal(first.next_id, second.next_id);
        const due = (
          await q(
            `select due_on::text d from ops_tasks where id=${first.next_id}`,
          )
        )[0].d;
        assert.equal(due, "2026-02-28");
        const next = (
          await q(`select ops_complete_task(${first.next_id}) x`)
        )[0].x;
        assert.equal(
          (
            await q(
              `select due_on::text d from ops_tasks where id=${next.next_id}`,
            )
          )[0].d,
          "2026-03-31",
        );
      },
    );
    await check(
      "appointment conflicts are blocked and adjacent bookings allowed",
      async () => {
        await q(
          `insert into counsel_appointments(student_id,starts_at,ends_at,assignee) values('${A}','2026-10-29 18:00+09','2026-10-29 19:00+09','김')`,
        );
        await assert.rejects(
          () =>
            q(
              `insert into counsel_appointments(student_id,starts_at,ends_at,assignee) values('${A}','2026-10-29 18:30+09','2026-10-29 19:30+09','이')`,
            ),
          /겹쳐/,
        );
        await q(
          `insert into counsel_appointments(student_id,starts_at,ends_at,assignee) values('${A}','2026-10-29 19:00+09','2026-10-29 20:00+09','김')`,
        );
      },
    );
    await check(
      "early departure is stored and student schedule helper contains only enrolled changes",
      async () => {
        await q(
          `insert into attendance(student_id,day,status) values('${A}','2026-10-29','early')`,
        );
        await q(
          "insert into lesson_changes(class_id,on_date,kind,reason) values(1,current_date,'휴강','검증')",
        );
        await db.exec("reset role");
        const x = (await q(`select _sched_of('${O}','${A}',true) x`))[0].x;
        assert.equal(x.lesson_changes.length, 1);
        assert.equal(
          (await q(`select _sched_of('${X}','${B}',true) x`))[0].x
            .lesson_changes.length,
          0,
        );
      },
    );
    await check("anonymous cannot execute operation helpers", async () => {
      await db.exec("set role anon");
      await assert.rejects(() => q("select ops_staff()"), /permission denied/);
      await db.exec("reset role");
    });
    await check(
      "audit logs record actor and row metadata without counsel body",
      async () => {
        await as(O);
        const logs = await q("select * from ops_audit");
        assert.ok(logs.length > 0);
        assert.ok(logs.every((x) => !("body" in x)));
        await as(T);
        assert.equal(
          (await q("select count(*)::int n from ops_audit"))[0].n,
          0,
        );
      },
    );
    await check(
      "credential RPCs and direct writes cannot bypass staff/teacher capabilities",
      async () => {
        await as(S);
        await assert.rejects(
          () => q(`select issue_login('${A}','known','pass')`),
          /forbidden/,
        );
        await assert.rejects(
          () =>
            q(
              `update students set login='known',pw_hash='known' where id='${A}'`,
            ),
          /credential provisioning/,
        );
        await assert.rejects(
          () => q("select pw_hash from students"),
          /permission denied/,
        );
        await assert.rejects(
          () => q("select pw_hash from signup_requests"),
          /permission denied/,
        );
        await as(T);
        await assert.rejects(
          () => q(`select parent_issue('${A}','known','pass')`),
          /forbidden/,
        );
        await q(`select issue_login('${A}','teacher-issued','test-password')`);
        await as(O);
        await q(`select parent_issue('${A}','owner-issued','test-password')`);
      },
    );
    await check("replacement lesson must have an end time", async () => {
      await as(O);
      await assert.rejects(
        () =>
          q(
            "insert into lesson_changes(class_id,on_date,kind,starts_at) values(1,'2027-01-01','대체','2027-01-01 18:00+09')",
          ),
        /check constraint/,
      );
    });
    await check(
      "same-name classes each receive their own keyed invoice",
      async () => {
        await as(O);
        await q("update classes set name='같은이름' where id=1");
        assert.equal(
          (await q("select ops_monthly_bill('2026-12-01','2026-12-10') x"))[0].x
            .created,
          1,
        );
        await q("insert into classes(name,tuition) values('같은이름',200000)");
        await q(
          `insert into class_members(class_id,student_id) values(2,'${A}')`,
        );
        assert.equal(
          (await q("select ops_monthly_bill('2026-12-01','2026-12-10') x"))[0].x
            .created,
          1,
        );
      },
    );
    await check(
      "teachers cannot change guardian-facing billing settings but teaching preferences remain writable",
      async () => {
        await as(O);
        await q(
          `insert into teacher_settings(user_id,data) values('${O}','{"pay":{"bank":"검증계좌"},"perms":{"academy":"검증"}}')`,
        );
        await as(T);
        await assert.rejects(
          () =>
            q(
              `update teacher_settings set data=jsonb_set(data,'{pay,bank}','"변경"')`,
            ),
          /billing settings require permission/,
        );
        await q(
          `update teacher_settings set data=jsonb_set(data,'{books}','[]')`,
        );
        await as(S);
        await q(
          `update teacher_settings set data=jsonb_set(data,'{pay,bank}','"행정변경"')`,
        );
        await assert.rejects(
          () =>
            q(
              `update teacher_settings set data=jsonb_set(data,'{perms,academy}','"변경"')`,
            ),
          /owner permission/,
        );
      },
    );
    await check(
      "date-aware lesson guards reject overlapping replacements and honor cancellations",
      async () => {
        await as(O);
        await q(
          `insert into lesson_changes(class_id,on_date,kind,starts_at,ends_at,room) values(1,'2026-12-07','대체','2026-12-06 18:00+09','2026-12-06 20:00+09','101')`,
        );
        await assert.rejects(
          () =>
            q(
              `insert into lesson_changes(class_id,on_date,kind,starts_at,ends_at,room) values(2,'2026-12-08','대체','2026-12-06 19:00+09','2026-12-06 21:00+09','101')`,
            ),
          /겹쳐/,
        );
        await q(
          `insert into lesson_changes(class_id,on_date,kind) values(1,'2026-12-14','휴강')`,
        );
        await q(
          `insert into lesson_changes(class_id,on_date,kind,starts_at,ends_at,room) values(2,'2026-12-15','대체','2026-12-14 18:00+09','2026-12-14 20:00+09','101')`,
        );
      },
    );
    await check(
      "cancellation identity cannot move or delete and restore a conflicting regular lesson",
      async () => {
        await as(O);
        await assert.rejects(
          () =>
            q(
              "update lesson_changes set on_date='2026-12-15' where class_id=1 and on_date='2026-12-14'",
            ),
          /원래 날짜/,
        );
        await assert.rejects(
          () =>
            q(
              "delete from lesson_changes where class_id=1 and on_date='2026-12-14'",
            ),
          /삭제할 수 없/,
        );
        await q("delete from classes where id=2"); // cascade is safe: that class's regular lessons disappear too
      },
    );
    console.log(`${count} PostgreSQL checks passed`);
  } finally {
    await db.close();
  }
})().catch((e) => {
  console.error(e.message, e.detail || "", e.where || "");
  process.exit(1);
});
