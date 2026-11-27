// 실험 2·3: node docs/research/experiments/bench.cjs <결과 json>  — 시뮬레이션 풀이 기록(고정 시드)으로 SQL 진단 정확도·시간 측정
const fs=require('fs');const path=require('path');process.chdir(path.resolve(__dirname,'../../..'));
const {PGlite,pgcrypto}=require(path.resolve(__dirname,'../../../tests/runtime.cjs'));
let seed=20261125;const rnd=()=>{seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff};
(async()=>{
 const db=new PGlite({extensions:{pgcrypto}});
 await db.exec(`create role anon;create role authenticated;create role service_role;create schema auth;create schema extensions;create table auth.users(id uuid primary key,email text);create function auth.uid() returns uuid language sql stable as $$select nullif(current_setting('test.uid',true),'')::uuid$$;`);
 await db.exec(fs.readFileSync('setup.sql','utf8'));
 // 1) 실제 문제은행 메타데이터 적재
 const Q=[];for(const [d,subj] of [['bank','물질과 에너지'],['cm','세포와 물질대사'],['ph','역학과 에너지'],['hl','화법과 언어'],['aim','인공지능 수학']]){const idx=JSON.parse(fs.readFileSync(d+'/index.json'));for(const tag of Object.keys(idx)){if(!idx[tag]||typeof idx[tag]!=='object'||!idx[tag].n)continue;let a;try{a=JSON.parse(fs.readFileSync(`${d}/${tag}.json`))}catch(e){continue}if(!Array.isArray(a))continue;a.forEach(q=>Q.push([q.code,subj,q.sub||'',q.type||tag,q.lv||'중']))}}
 await db.exec(`create table q_meta(code text primary key, subject text not null, sub text, type text not null, lv text not null)`);
 for(let i=0;i<Q.length;i+=2000){const ch=Q.slice(i,i+2000);await db.query('insert into q_meta select * from unnest($1::text[],$2::text[],$3::text[],$4::text[],$5::text[]) on conflict do nothing',[0,1,2,3,4].map(k=>ch.map(r=>r[k])))}
 const nq=(await db.query('select count(*)::int n, count(distinct type)::int t from q_meta')).rows[0];
 // 2) 합성 풀이 기록: 세포와 물질대사 문항으로 학생 200명 × 학습지 30회 × 20문항
 const cm=(await db.query(`select code,type,lv from q_meta where subject='세포와 물질대사'`)).rows;
 const types=[...new Set(cm.map(q=>q.type))];
 await db.exec(`insert into auth.users values('00000000-0000-0000-0000-0000000000aa','t@x.invalid')`);
 const U='00000000-0000-0000-0000-0000000000aa';
 const st=(await db.query(`insert into students(user_id,name) select '${U}', '학생'||g from generate_series(1,200) g returning id`)).rows.map(r=>r.id);
 const WEAK={};const base={'하':.85,'중':.7,'상':.5,'최':.3};const rows=[];const hist={};
 for(const s of st){const weak=new Set([...types].sort(()=>rnd()-.5).slice(0,4));hist[s]=[];WEAK[s]=weak;
  for(let k=0;k<30;k++){const items=[];for(let j=0;j<20;j++){const q=cm[Math.floor(rnd()*cm.length)];let p=base[q.lv]||.7;if(weak.has(q.type))p-=.3;items.push({c:q.code,r:rnd()<p?1:0,a:String(1+Math.floor(rnd()*5))})}
   const t=1700000000000+k*86400000;rows.push([s,t,JSON.stringify(items)]);hist[s].push({t,items})}}
 for(let i=0;i<rows.length;i+=500){const ch=rows.slice(i,i+500);await db.query(`insert into attempts(user_id,student_id,t,"set",sub,items) select '${U}',s,t,'ws','W',i::jsonb from unnest($1::uuid[],$2::bigint[],$3::text[]) as x(s,t,i)`,[ch.map(r=>r[0]),ch.map(r=>r[1]),ch.map(r=>r[2])])}
 const N=(await db.query(`select count(*)::int a,(select count(*) from attempts, jsonb_array_elements(items))::int i from attempts`)).rows[0];
 const time=async(label,sql,rep=5)=>{let best=1e9,res;for(let i=0;i<rep;i++){const t0=performance.now();res=await db.query(sql);best=Math.min(best,performance.now()-t0)}return {label,ms:+best.toFixed(1),rows:res.rows.length,res:res.rows}};
 const R={};
 // Q1 유형별 정답률(학생별)
 const Q1=`select a.student_id, m.type, count(*) n, sum(x.r) r, round(avg(x.r)::numeric,4) p
  from attempts a cross join lateral jsonb_to_recordset(a.items) as x(c text, r int, a text) join q_meta m on m.code=x.c
  group by a.student_id, m.type`;
 R.q1=await time('유형별 정답률 (JSONB 펼치기 + JOIN + GROUP BY)',Q1);
 // Q2 최근 6회 정답률 (윈도 함수)
 const Q2=`with e as (select a.student_id, m.type, x.r, a.t, x.ord from attempts a cross join lateral rows from (jsonb_to_recordset(a.items) as (c text,r int,a text)) with ordinality as x(c,r,a,ord) join q_meta m on m.code=x.c),
  k as (select *, row_number() over (partition by student_id,type order by t desc, ord desc) rn from e)
  select student_id,type, round(avg(r)::numeric,4) rp from k where rn<=6 group by student_id,type`;
 R.q2=await time('최근 6회 정답률 (윈도 함수 row_number)',Q2);
 // Q3 학생별 취약 유형 TOP3 (rank)
 const Q3=`with s as (${Q1}) select * from (select s.*, rank() over (partition by student_id order by p asc, n desc) rk from s where n>=5) z where rk<=3`;
 R.q3=await time('학생별 취약 유형 TOP3 (rank + 서브쿼리)',Q3);
 // Q4 반복 오답
 const Q4=`select a.student_id, x.c, count(*) wrong from attempts a cross join lateral jsonb_to_recordset(a.items) as x(c text,r int) where x.r=0 group by a.student_id,x.c having count(*)>=2`;
 R.q4=await time('반복 오답 문항 (HAVING)',Q4);
 // Q5 CTT 난이도 보정
 const Q5=`select m.code,m.lv, count(*) n, round(avg(x.r)::numeric,3) p, case when avg(x.r)>=.8 then '하' when avg(x.r)>=.6 then '중' when avg(x.r)>=.35 then '상' else '최' end lv_measured
  from attempts a cross join lateral jsonb_to_recordset(a.items) as x(c text,r int) join q_meta m on m.code=x.c group by m.code,m.lv having count(*)>=10`;
 R.q5=await time('실측 정답률로 난이도 보정 (고전 검사 이론)',Q5);
 // 정규화 비교: attempt_items 표(1NF)
 await db.exec(`create table attempt_items(attempt_id bigint references attempts(id) on delete cascade, ord int, code text not null, r smallint not null, ans text, primary key(attempt_id,ord));
  insert into attempt_items select a.id, x.ord, x.c, x.r, x.a from attempts a cross join lateral rows from (jsonb_to_recordset(a.items) as (c text,r int,a text)) with ordinality as x(c,r,a,ord);
  create index on attempt_items(code); create index on attempts(student_id); analyze;`);
 const Q1n=`select a.student_id, m.type, count(*) n, sum(i.r) r, round(avg(i.r)::numeric,4) p from attempts a join attempt_items i on i.attempt_id=a.id join q_meta m on m.code=i.code group by a.student_id,m.type`;
 R.q1n=await time('유형별 정답률 — 정규화 표(attempt_items) 사용',Q1n);
 const one=st[0];
 R.one_json=await time('학생 1명 유형별 정답률 — JSONB',`select m.type,count(*),avg(x.r) from attempts a cross join lateral jsonb_to_recordset(a.items) as x(c text,r int) join q_meta m on m.code=x.c where a.student_id='${one}' group by m.type`,20);
 R.one_norm=await time('학생 1명 유형별 정답률 — 정규화 표',`select m.type,count(*),avg(i.r) from attempts a join attempt_items i on i.attempt_id=a.id join q_meta m on m.code=i.code where a.student_id='${one}' group by m.type`,20);
 const size=(await db.query(`select pg_total_relation_size('attempts')::bigint a, pg_total_relation_size('attempt_items')::bigint i`)).rows[0];
 // 앱(JS statsFrom)과 SQL 결과 대조
 const meta=Object.fromEntries(cm.map(q=>[q.code,q]));let mism=0,cmp=0;
 const sqlMap=new Map(R.q1.res.map(r=>[r.student_id+'|'+r.type,r]));
 const sqlRp=new Map(R.q2.res.map(r=>[r.student_id+'|'+r.type,+r.rp]));
 for(const s of st){const m={};hist[s].forEach(h=>h.items.forEach(x=>{const q=meta[x.c];const o=m[q.type]=m[q.type]||{n:0,r:0,rec:[]};o.n++;o.r+=x.r;o.rec.push(x.r)}));
  for(const [ty,o] of Object.entries(m)){cmp++;const q=sqlMap.get(s+'|'+ty);const rp=o.rec.slice(-6).reduce((a,b)=>a+b,0)/Math.min(6,o.rec.length);
   if(!q||+q.n!==o.n||+q.r!==o.r||Math.abs(sqlRp.get(s+'|'+ty)-rp)>1e-3)mism++}}
 // 취약 유형 진단 정확도: 실제로 심은 약점 4개 중 TOP3에 든 비율
 let hit=0,tot=0;R.q3.res.forEach(r=>{if(r.rk<=3){tot++;if(WEAK[r.student_id].has(r.type))hit++}});
 const out={precision:{hit,tot},questions:nq,attempts:N.a,items:N.i,students:st.length,timings:Object.fromEntries(Object.entries(R).map(([k,v])=>[k,{label:v.label,ms:v.ms,rows:v.rows}])),size,compare:{pairs:cmp,mismatch:mism},
  q5_changed:R.q5.res.filter(r=>r.lv!==r.lv_measured).length, q5_total:R.q5.res.length, sample_top3:R.q3.res.slice(0,6)};
 fs.writeFileSync(process.argv[2],JSON.stringify(out,null,1));console.log(JSON.stringify(out,null,1).slice(0,2500));
})().catch(e=>{console.error(e);process.exit(1)});
