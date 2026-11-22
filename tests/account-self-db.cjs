/* 계정 스스로 바꾸기(sql_29): 격리된 PostgreSQL(PGlite)에서 setup.sql + sql_29.
   선생님이 발급한 학생 · 학부모 계정은 must_reset, 지금 비밀번호로만 아이디 · 비밀번호 변경, 토큰 · 틀린 비밀번호 · 중복 아이디 거부. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');const {PGlite,pgcrypto}=require('./runtime.cjs');
(async()=>{const db=new PGlite({extensions:{pgcrypto}});const q=async(s,p)=>(await db.query(s,p)).rows;
await db.exec(`create role anon;create role authenticated;create role service_role;create schema auth;create schema extensions;create table auth.users(id uuid primary key,email text);create function auth.uid() returns uuid language sql stable as $$select nullif(current_setting('test.uid',true),'')::uuid$$;grant usage on schema auth,extensions to anon,authenticated;grant execute on function auth.uid() to anon,authenticated;`);
process.chdir(path.join(__dirname,'..'));await db.exec(fs.readFileSync('setup.sql','utf8'));const sql=fs.readFileSync('supabase/sql_29_account_self.sql','utf8');await db.exec(sql);await db.exec(sql);
const T='00000000-0000-0000-0000-0000000000a1';await db.exec(`insert into auth.users values('${T}','t@x.invalid')`);
const S1=(await q(`insert into students(user_id,name) values('${T}','가학생') returning id`))[0].id,S2=(await q(`insert into students(user_id,name) values('${T}','나학생') returning id`))[0].id;
const as=async(u,f)=>{await db.exec('reset role');await db.query("select set_config('test.uid',$1,false)",[u||'']);await db.exec(u?'set role authenticated':'set role anon');try{return await f()}finally{await db.exec('reset role')}};
const one=async(s,p)=>Object.values((await q(s,p))[0])[0];
// 선생님 발급 → 첫 로그인에서 새로 정해야 함
await as(T,()=>q(`select issue_login('${S1}','ga01','1234')`));await as(T,()=>q(`select issue_login('${S2}','na01','1234')`));
let j=await as(null,()=>one("select st_login('ga01','1234')"));assert.equal(j.must_reset,true,'teacher-issued student account must reset');
// 바꾸기: 틀린 비밀번호 · 토큰 · 형식 · 짧은 비밀번호 · 중복
const ch=(a,b,c,d)=>as(null,()=>one('select st_change_credentials($1,$2,$3,$4)',[a,b,c,d]));
assert.equal(await ch('ga01','9999','gahak','abcdef'),'auth');
await db.exec(`insert into st_tokens(token_hash,student_id) values(encode(extensions.digest('tk','sha256'),'hex'),'${S1}')`);
assert.equal(await ch('ga01','tok:tk','gahak','abcdef'),'auth','auto-login token cannot change the password');
assert.equal(await ch('ga01','1234','가학생','abcdef'),'login');assert.equal(await ch('ga01','1234','gahak','12'),'pw');assert.equal(await ch('ga01','1234','NA01','abcdef'),'taken');
assert.equal(await ch('ga01','1234','gahak','abcdef'),'ok');
assert.equal(await as(null,()=>one("select st_login('ga01','1234')")),null,'old credentials stop working');
j=await as(null,()=>one("select st_login('gahak','abcdef')"));assert.equal(j.must_reset,false,'reset done');
assert.equal(+(await one(`select count(*) from st_tokens where student_id='${S1}'`)),0,'old auto-login tokens revoked');
assert.equal(await ch('gahak','abcdef','gahak','newpass1'),'ok','password only (same id)');
// 학부모
await as(T,()=>q(`select parent_issue('${S2}','mom01','1234','어머니')`));
j=await as(null,()=>one("select pa_login('mom01','1234')"));assert.equal(j.must_reset,true,'teacher-issued parent account must reset');
const pc=(a,b,c,d)=>as(null,()=>one('select pa_change_credentials($1,$2,$3,$4)',[a,b,c,d]));
assert.equal(await pc('mom01','0000','mom02','qwerty'),'auth');assert.equal(await pc('mom01','1234','mom02','qwerty'),'ok');
j=await as(null,()=>one("select pa_login('mom02','qwerty')"));assert.equal(j.must_reset,false);
// 다시 발급하면 다시 새로 정해야 함
await as(T,()=>q(`select issue_login('${S1}','gahak','5678')`));j=await as(null,()=>one("select st_login('gahak','5678')"));assert.equal(j.must_reset,true,'re-issue asks again');
console.log('PASS 계정 스스로 바꾸기: 발급 계정 첫 로그인 재설정, 지금 비밀번호로만 변경(토큰 · 틀린 비밀번호 거부), 형식 · 길이 · 중복 검사, 이전 토큰 무효');
await db.close()})().catch(e=>{console.error(e);process.exit(1)});
