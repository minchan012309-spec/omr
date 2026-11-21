/* 오답 학생 답 고치기(sql_28): 격리된 PostgreSQL(PGlite)에서 setup.sql + sql_28. 오답 문항의 a만 바뀌고 r은 그대로, 정답 문항·남의 기록은 못 바꿈. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');const {PGlite,pgcrypto}=require('./runtime.cjs');
(async()=>{const db=new PGlite({extensions:{pgcrypto}});const q=async s=>(await db.query(s)).rows;
await db.exec(`create role anon;create role authenticated;create role service_role;create schema auth;create schema extensions;create table auth.users(id uuid primary key,email text);create function auth.uid() returns uuid language sql stable as $$select nullif(current_setting('test.uid',true),'')::uuid$$;grant usage on schema auth,extensions to anon,authenticated;grant execute on function auth.uid() to anon,authenticated;`);
process.chdir(path.join(__dirname,'..'));await db.exec(fs.readFileSync('setup.sql','utf8'));await db.exec(fs.readFileSync('supabase/sql_28_wrong_answer.sql','utf8'));await db.exec(fs.readFileSync('supabase/sql_28_wrong_answer.sql','utf8'));
const A='00000000-0000-0000-0000-0000000000a1',B='00000000-0000-0000-0000-0000000000b2';
await db.exec(`insert into auth.users values('${A}','a@x.invalid'),('${B}','b@x.invalid')`);
await db.exec(`insert into attempts(user_id,t,"set",sub,items) values('${A}',100,'ws','12345678','[{"c":"Q1","a":"2","r":1},{"c":"Q2","a":"","r":0}]')`);
const as=async(u,f)=>{await db.exec('reset role');await db.query("select set_config('test.uid',$1,false)",[u]);await db.exec('set role authenticated');try{return await f()}finally{await db.exec('reset role')}};
await as(A,()=>q("select attempt_wrong_answer(100,'Q2','4')"));
let it=(await q("select items from attempts where t=100"))[0].items;assert.deepEqual(it[1],{c:'Q2',a:'4',r:0});assert.deepEqual(it[0],{c:'Q1',a:'2',r:1});
let e=0;try{await as(A,()=>q("select attempt_wrong_answer(100,'Q1','3')"))}catch(x){e++}assert.equal(e,1,'정답 문항은 못 바꿈');
try{await as(B,()=>q("select attempt_wrong_answer(100,'Q2','1')"))}catch(x){e++}assert.equal(e,2,'다른 계정 기록은 못 바꿈');
try{await db.exec('set role anon');await q("select attempt_wrong_answer(100,'Q2','1')")}catch(x){e++}finally{await db.exec('reset role')}assert.equal(e,3,'로그인 안 하면 못 씀');
it=(await q("select items from attempts where t=100"))[0].items;assert.equal(it[1].a,'4');assert.equal(it[1].r,0);
console.log('PASS 오답 학생 답 고치기: 오답 문항의 답만, r 그대로, 남의 기록·정답 문항 불가');
})().catch(e=>{console.error(e);process.exitCode=1});
