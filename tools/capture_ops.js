// 소개 페이지 「학원 운영」 장면용 실제 앱 캡처: 운영 업무 · 보강 · 출결(하루) · 월 청구 · 알림장.
//   node tools/capture_ops.js <png 폴더>   (python3 server.py 가 8765에서 실행 중이어야 함) → python3 tools/intro_webp.py <png 폴더>
// tools/capture_cine.js 와 같은 지어낸 학원(이름은 모두 「○○ 학생」, 연락처 010-0000-00xx)과 지어낸 기록. 실제 학생 · 서버 데이터 없음.
const {chromium,browserOptions}=require('../tests/runtime.cjs');const fs=require('fs');const path=require('path');
const OUT=process.argv[2]||'intro_png';fs.mkdirSync(OUT,{recursive:true});
const BASE=process.env.BASE||'http://localhost:8765/';
const ACADEMY=fs.readFileSync(path.join(__dirname,'capture_cine.js'),'utf8').match(/const ACADEMY=`([\s\S]*?)`;/)[1];
const NAMES=['솔비','하늘','바다','별빛','가람','나래','다온','라온','마루','보람','새봄','아라','온새','지음','한결','해솔','그린','누리'];
const day=n=>new Date(Date.now()+n*864e5+9*36e5).toISOString().slice(0,10),mon=day(0).slice(0,7);
const STU=NAMES.map((n,i)=>({id:'s'+(i+1),name:n+' 학생',grade:['고1','고2','고3'][i%3],phone:'010-0000-00'+String(10+i),att_pin:String(1010+i)}));
const ATT=STU.slice(0,13).map((s,i)=>({student_id:s.id,day:day(0),status:i%6===5?'late':i===11?'abs':'in',t_in:new Date(Date.now()-(80-i*4)*6e4).toISOString(),t_out:i<4?new Date(Date.now()-10*6e4).toISOString():null}));
const AMT=[320000,300000,360000,280000];
const FEES=STU.slice(0,14).map((s,i)=>({id:i+1,student_id:s.id,title:mon.slice(5)+'월 수강료',amount:AMT[i%4],paid_amount:i%5===4?0:i===7?150000:AMT[i%4],due:i%5===4&&i<10?day(-3):mon+'-25',method:i%5===4?null:['계좌 이체','카드','현금'][i%3],created_at:mon+'-01T09:00:00+09:00'}));
const NOTES=[{id:1,title:day(0).slice(5).replace('-','월 ')+'일 알림장',body:'오늘 진도: 유형서 p.42~47 · 반응 속도식과 반응 차수\n숙제: 유형서 p.48~50, 오답 유사 학습지\n전달: 다음 주 화요일 단원 평가가 있어요.',t:Date.now()-3*36e5,student_id:null,audience:'both'},
 {id:2,title:day(-2).slice(5).replace('-','월 ')+'일 알림장',body:'오늘 진도: 헤스 법칙과 열화학 반응식의 조합\n숙제: 기본 문제 1~12',t:Date.now()-50*36e5,student_id:null,audience:'both'}];
const SESS={access_token:'x',refresh_token:'r',user:{id:'demo',email:'demo@solvi.kr'}};
(async()=>{const b=await chromium.launch(browserOptions());
 const ctx=await b.newContext({viewport:{width:1760,height:990},deviceScaleFactor:2,serviceWorkers:'block'});
 await ctx.addInitScript(S=>{try{localStorage.setItem('omr_sess_v1',JSON.stringify(S));localStorage.setItem('omr_theme','light');localStorage.setItem('omr_reload_seen',String(Date.now()));localStorage.setItem('omr_snpop','9');localStorage.setItem('omr_tour_done','1')}catch(e){}},SESS);
 await ctx.route(/supabase\.co/,r=>{const u=new URL(r.request().url()),p=u.pathname;
  if(p.endsWith('/auth/v1/token'))return r.fulfill({json:SESS});
  if(/\/rpc\/ops_access$/.test(p))return r.fulfill({json:{role:'owner',operations:true,billing:true,learning:true,manage:true}});
  if(p.endsWith('/rest/v1/students'))return r.fulfill({json:STU});
  if(p.endsWith('/rest/v1/attendance'))return r.fulfill({json:ATT});
  if(p.endsWith('/rest/v1/fees'))return r.fulfill({json:FEES});
  if(p.endsWith('/rest/v1/notices'))return r.fulfill({json:NOTES});
  return r.fulfill({json:[]})});
 const pg=await ctx.newPage();pg.on('dialog',d=>d.accept());pg.on('pageerror',e=>console.log('ERR',String(e)));
 await pg.goto(BASE+'index.html?app=1');await pg.waitForTimeout(2500);
 const quiet="document.documentElement.classList.remove('entry-mode','noauth');document.querySelectorAll('#toast,.tour,#tour,#instb,#bellN,#sitebanner').forEach(e=>e.remove());scrollTo(0,0)";
 const shot=async n=>{await pg.waitForTimeout(700);await pg.evaluate(quiet);await pg.screenshot({path:OUT+'/'+n+'.png'});console.log(n)};
 await pg.evaluate("setSubject('me')");await pg.waitForTimeout(1200);
 await pg.evaluate("lazyLoad('admin')");await pg.waitForTimeout(800);
 const ops=`(()=>{const d=n=>adDay(new Date(Date.now()+n*864e5));AD.opsReady=true;
  AD.tasks=[{id:1,title:'11월 수강료 청구서 보내기',due_on:d(1),assignee:'행정 정음',repeat_kind:'monthly',student_id:null},{id:2,title:'고2 화학 A 단원 평가 채점',due_on:d(2),assignee:'김솔 선생님',repeat_kind:'none',student_id:null},{id:3,title:'신규 상담 학생 체험 수업 안내',due_on:d(2),assignee:'원장',repeat_kind:'none',student_id:'s17'},{id:4,title:'출결 단말 번호 확인',due_on:d(3),assignee:'행정 정음',repeat_kind:'weekly',student_id:null}];
  AD.appointments=[{id:1,student_id:'s3',starts_at:d(1)+'T19:00:00+09:00',ends_at:d(1)+'T19:30:00+09:00',assignee:'김솔 선생님',kind:'학부모',status:'예정',memo:'반응 속도 단원 보강 일정'},{id:2,student_id:'s7',starts_at:d(3)+'T17:00:00+09:00',ends_at:d(3)+'T17:40:00+09:00',assignee:'원장',kind:'진로',status:'예정',memo:'심화반 이동'}];
  AD.changes=[{id:1,class_id:1,on_date:d(4),kind:'휴강',reason:'학교 시험 기간'},{id:2,class_id:3,on_date:d(5),kind:'대체',starts_at:d(5)+'T14:00:00+09:00',ends_at:d(5)+'T15:50:00+09:00',teacher:'박결 선생님',room:'303',reason:'휴강 대체'}]})()`;
 await pg.evaluate(ACADEMY);await pg.evaluate(ops);
 for(const [sec,name] of [['ops','xdr-ops'],['mku','xdr-mku']]){await pg.evaluate(quiet+";tab='admin';AD.sec='"+sec+"';render()");await pg.waitForTimeout(900);await pg.evaluate(ACADEMY);await pg.evaluate(ops);await pg.evaluate("AD.sec='"+sec+"';adminView()");await shot(name)}
 await pg.evaluate("lazyLoad('acad')");await pg.waitForTimeout(800);
 await pg.evaluate("AC.sec='day';AC.ld=0;tab='att';render()");await pg.waitForTimeout(1500);await shot('xdr-att');
 await pg.evaluate("AC.sec='bill';AC.ld=0;tab='fee';render()");await pg.waitForTimeout(1200);await pg.evaluate(ACADEMY);await pg.evaluate(ops);await pg.evaluate("AD.ld=1;attView()");await pg.waitForTimeout(1200);await shot('xdr-bill');
 await pg.evaluate("AC.ld=0;tab='diary';render()");await pg.waitForTimeout(1500);
 /* 알림장 쓰기 칸에 예시 내용을 채워서 찍는다(보내지는 않음) */
 await pg.evaluate(()=>{const set=(ph,v)=>{const e=[...document.querySelectorAll('#main input,#main textarea')].find(x=>(x.placeholder||'').includes(ph));if(e){e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))}};
  set('p.12','유형서 p.42~47 · 반응 속도식과 반응 차수');set('p.16','유형서 p.48~50 풀어 오기, 틀린 문제는 오답 유사 학습지로');set('쪽지시험','다음 주 화요일 반응 속도 단원 평가가 있어요');set('알림장','')});
 await shot('xdr-diary');
 await b.close()})();
