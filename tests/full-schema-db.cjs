/* Fresh schema + actual credential functions in isolated PostgreSQL, never a Supabase connection. */
const fs = require("node:fs"),
  assert = require("node:assert/strict");
const { PGlite, pgcrypto } = require("./runtime.cjs");
(async () => {
  const db = new PGlite({ extensions: { pgcrypto } });
  const O = "00000000-0000-0000-0000-000000000001",
    T = "00000000-0000-0000-0000-000000000002",
    S = "00000000-0000-0000-0000-000000000003";
  const q = async (s) => (await db.query(s)).rows;
  const as = async (id) => {
    await db.exec("reset role");
    await db.query("select set_config('test.uid',$1,false)", [id]);
    await db.exec("set role authenticated");
  };
  try {
    await db.exec(
      `create role anon;create role authenticated;create role service_role;create schema auth;create schema extensions;create table auth.users(id uuid primary key,email text);create function auth.uid() returns uuid language sql stable as $$select nullif(current_setting('test.uid',true),'')::uuid$$;grant usage on schema auth,extensions to anon,authenticated;grant execute on function auth.uid() to anon,authenticated;`,
    );
    await db.exec(fs.readFileSync("setup.sql", "utf8"));
    await db.exec(
      "grant select,insert,update,delete on all tables in schema public to authenticated;grant usage,select on all sequences in schema public to authenticated",
    );
    await db.exec(fs.readFileSync("supabase/sql_24_operations.sql", "utf8"));
    console.log("PASS complete setup.sql + migration");
    await db.exec(
      `insert into auth.users values('${O}','owner@fixture.invalid'),('${T}','teacher@fixture.invalid'),('${S}','staff@fixture.invalid');insert into academy_members(member_id,owner_id,label,role) values('${T}','${O}','강사','teacher'),('${S}','${O}','행정','staff')`,
    );
    await as(O);
    const sid = (
      await q("insert into students(name) values('검증학생') returning id")
    )[0].id;
    await q(`select issue_login('${sid}','fixture-student','testpass123')`);
    assert.ok(
      (await q("select st_data('fixture-student','testpass123') x"))[0].x,
    );
    await q(
      `select parent_issue('${sid}','fixture-parent','testpass123','보호자')`,
    );
    assert.ok(
      (await q("select pa_fees('fixture-parent','testpass123') x"))[0].x,
    );
    console.log(
      "PASS original student/parent credential issuance and authenticated RPC compatibility",
    );
    await as(S);
    await assert.rejects(
      () => q(`select issue_login('${sid}','taken','testpass123')`),
      /forbidden/,
    );
    await assert.rejects(
      () =>
        q(
          `update students set login='taken',pw_hash='known' where id='${sid}'`,
        ),
      /credential provisioning/,
    );
    await assert.rejects(
      () => q("select pw_hash from students"),
      /permission denied/,
    );
    await as(T);
    await assert.rejects(
      () => q(`select parent_issue('${sid}','taken','testpass123')`),
      /forbidden/,
    );
    console.log("PASS real legacy credential bypass paths blocked");
    await db.exec("reset role");
    const defs = (
      await q(
        "select pg_get_functiondef(oid) d from pg_proc where proname='issue_login'",
      )
    )[0].d;
    assert.ok(defs.includes("-- ops credential gate"));
    await db.exec(fs.readFileSync("supabase/sql_24_operations.sql", "utf8"));
    console.log("PASS full-schema migration repeat");
  } finally {
    await db.close();
  }
})().catch((e) => {
  console.error(e.message, e.detail || "", e.where || "");
  process.exit(1);
});
