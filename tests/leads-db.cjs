/* site_leads(무료 체험 신청 · 문의) 권한: 격리된 PostgreSQL(PGlite)에서 setup.sql + sql_26 을 적용해 확인. 실제 Supabase에는 연결하지 않는다. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');const {PGlite,pgcrypto}=require('./runtime.cjs');
(async()=>{const db=new PGlite({extensions:{pgcrypto}});const q=async s=>(await db.query(s)).rows;
await db.exec(`create role anon;create role authenticated;create role service_role;create schema auth;create schema extensions;create table auth.users(id uuid primary key,email text);create function auth.uid() returns uuid language sql stable as $$select nullif(current_setting('test.uid',true),'')::uuid$$;grant usage on schema auth,extensions to anon,authenticated;grant execute on function auth.uid() to anon,authenticated;`);
process.chdir(path.join(__dirname,'..'));await db.exec(fs.readFileSync('setup.sql','utf8'));await db.exec(fs.readFileSync('supabase/sql_26_site_leads.sql','utf8'));await db.exec(fs.readFileSync('supabase/sql_26_site_leads.sql','utf8'));
await db.exec("set role anon");
await q("insert into site_leads(kind,name,phone) values('trial','홍길동','010-0000-0000')");
let blocked=0;try{await q("insert into site_leads(kind,name) values('contact','연락처없음')")}catch(e){blocked++}
try{await q("insert into site_leads(kind,name,phone,status) values('trial','a','1','done')")}catch(e){blocked++}
assert.equal(blocked,2);
let ro=1;try{ro=(await q("select count(*)::int n from site_leads"))[0].n}catch(e){ro=0}assert.equal(ro,0,'anon cannot read');
await db.exec("reset role");const U2='00000000-0000-0000-0000-0000000000aa';await db.exec(`insert into auth.users values('${U2}','t@x.invalid')`);await db.query("select set_config('test.uid',$1,false)",[U2]);await db.exec("set role authenticated");assert.equal((await q("select count(*)::int n from site_leads"))[0].n,0,'other teachers cannot read');
await db.exec("reset role");const D='00000000-0000-0000-0000-0000000000dd';await db.exec(`insert into auth.users values('${D}','dev@x.invalid')`);
await q(`insert into developers(user_id) values('${D}')`).catch(async e=>{const cols=(await q("select column_name from information_schema.columns where table_name='developers'")).map(r=>r.column_name);throw new Error('developers cols '+cols)});
await db.query("select set_config('test.uid',$1,false)",[D]);await db.exec("set role authenticated");
assert.equal((await q("select count(*)::int n from site_leads"))[0].n,1,'dev reads');
await q("update site_leads set status='done'");assert.equal((await q("select status from site_leads"))[0].status,'done');
console.log('PASS site_leads: anon insert only, contact required, dev read/update, repeatable');})().catch(e=>{console.error(e);process.exit(1)});
