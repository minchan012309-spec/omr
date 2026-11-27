// 사용: node docs/research/experiments/schema.cjs <출력 json> (저장소 어디서 실행해도 됨)
const fs=require('fs');const path=require('path');process.chdir(path.resolve(__dirname,'../../..'));
const { PGlite, pgcrypto } = require(path.resolve(__dirname,'../../../tests/runtime.cjs'));
(async()=>{
 const db=new PGlite({extensions:{pgcrypto}});
 await db.exec(`create role anon;create role authenticated;create role service_role;create schema auth;create schema extensions;create table auth.users(id uuid primary key,email text);create function auth.uid() returns uuid language sql stable as $$select nullif(current_setting('test.uid',true),'')::uuid$$;grant usage on schema auth,extensions to anon,authenticated;grant execute on function auth.uid() to anon,authenticated;`);
 await db.exec(fs.readFileSync('setup.sql','utf8'));
 for(const f of ['sql_24_operations.sql','sql_25_trash.sql','sql_27_latex_manifests.sql','sql_28_wrong_answer.sql','sql_29_account_self.sql']){try{await db.exec(fs.readFileSync('supabase/'+f,'utf8'));console.error('ok',f)}catch(e){console.error('ERR',f,e.message)}}
 const cols=(await db.query(`select c.table_name t,c.column_name n,c.data_type d,c.is_nullable nl,c.column_default df,c.ordinal_position p from information_schema.columns c join information_schema.tables t using(table_schema,table_name) where c.table_schema='public' and t.table_type='BASE TABLE' order by 1,6`)).rows;
 const pks=(await db.query(`select tc.table_name t,kcu.column_name n from information_schema.table_constraints tc join information_schema.key_column_usage kcu on tc.constraint_name=kcu.constraint_name and tc.table_schema=kcu.table_schema where tc.constraint_type='PRIMARY KEY' and tc.table_schema='public'`)).rows;
 const fks=(await db.query(`select conrelid::regclass::text t, a.attname n, confrelid::regclass::text rt, af.attname rn, confdeltype del from pg_constraint c join lateral unnest(c.conkey) with ordinality k(attnum,o) on true join lateral unnest(c.confkey) with ordinality fk(attnum,o) on fk.o=k.o join pg_attribute a on a.attrelid=c.conrelid and a.attnum=k.attnum join pg_attribute af on af.attrelid=c.confrelid and af.attnum=fk.attnum where c.contype='f' and connamespace='public'::regnamespace`)).rows;
 const uq=(await db.query(`select conrelid::regclass::text t, pg_get_constraintdef(oid) d, contype from pg_constraint where connamespace='public'::regnamespace and contype in ('u','c')`)).rows;
 const fn=(await db.query(`select count(*) from pg_proc where pronamespace='public'::regnamespace`)).rows;
 const pol=(await db.query(`select tablename t,count(*) c from pg_policies where schemaname='public' group by 1`)).rows;
 const rls=(await db.query(`select relname t, relrowsecurity r from pg_class where relnamespace='public'::regnamespace and relkind='r'`)).rows;
 const idx=(await db.query(`select tablename t, indexname i, indexdef d from pg_indexes where schemaname='public'`)).rows;
 const fnl=(await db.query(`select proname from pg_proc where pronamespace='public'::regnamespace order by 1`)).rows.map(r=>r.proname);
 fs.writeFileSync(process.argv[2]||'schema.json',JSON.stringify({cols,pks,fks,uq,fn,pol,rls,idx,fnl},null,1));
 console.log(new Set(cols.map(c=>c.t)).size,'tables',fks.length,'fks',fn[0].count,'fns');
})().catch(e=>{console.error(e);process.exit(1)});
