// 시네마틱 소개 페이지(intro.html)의 디바이스 화면용 실제 앱 캡처.  node tools/capture_cine.js <png 폴더>   (python3 server.py 가 8765에서 실행 중이어야 함)
// tools/capture_intro.js 와 같은 방식: 지어낸 학원(원생 · 반 · 상담 · 보강 · 수납)과 지어낸 채점 기록을 넣고 실제 화면을 그대로 찍는다.
// 찍은 PNG 는 tools/intro_webp.py 로 intro/*.webp 로 바꾼다.
// 크기 규칙: xdr-* = 앱 전체(메뉴 포함) 1760×990(Pro Display 16:9) · mac-* = 앱 전체 1512×982(MacBook) · pad-* = 834×1194(iPad 세로) · kiosk = 1194×834(iPad 가로) · cover-* = A4 표지
const {chromium,browserOptions}=require('../tests/runtime.cjs');const fs=require('fs');
const OUT=process.argv[2]||'intro_png';fs.mkdirSync(OUT,{recursive:true});
const BASE=process.env.BASE||'http://localhost:8765/';
const FAKE=`sess={access_token:'x',user:{id:'demo',email:'demo@solvi.kr'}};STU=[{id:'s1',name:'솔비 학생',grade:'고2',cls:'A반'},{id:'s2',name:'하늘 학생',grade:'고2',cls:'A반'},{id:'s3',name:'바다 학생',grade:'고1',cls:'B반'},{id:'s4',name:'별빛 학생',grade:'고1',cls:'B반'}];`;
// 지어낸 학원: 이름은 모두 「○○ 학생」, 연락처는 010-0000-0000 꼴
const ACADEMY=`(()=>{const d=n=>adDay(new Date(Date.now()+n*864e5)),mon=adDay().slice(0,7),w=adDow(adDay());
 const names=['솔비','하늘','바다','별빛','가람','나래','다온','라온','마루','보람','새봄','아라','온새','지음','한결','해솔','그린','누리'];
 AD.stu=names.map((n,i)=>({id:'s'+(i+1),name:n+' 학생',grade:['고1','고2','고3'][i%3],school:['솔빛고','한빛고','바른고'][i%3],status:i===15?'휴원':i===16?'상담':'재원',joined_on:i<2?mon+'-0'+(i+3):'2026-0'+(3+i%5)+'-02',guardian:n+' 보호자',guardian_phone:'010-0000-00'+String(10+i)}));
 AD.cls=[{id:1,name:'고2 화학 A',subject:'물질과 에너지',teacher:'김솔 선생님',room:'301',color:'#2f7fd0',tuition:320000,sched:[{d:w,s:'16:00',e:'17:50'},{d:(w%7)+2>7?1:(w%7)+2,s:'16:00',e:'17:50'}]},
  {id:2,name:'고1 생명 B',subject:'세포와 물질대사',teacher:'이빛 선생님',room:'302',color:'#1f9d55',tuition:300000,sched:[{d:w,s:'18:00',e:'19:50'},{d:w%7+1,s:'18:00',e:'19:50'}]},
  {id:3,name:'고3 물리 심화',subject:'역학과 에너지',teacher:'박결 선생님',room:'303',color:'#e09a00',tuition:360000,sched:[{d:w,s:'20:00',e:'21:50'},{d:(w+2)%7+1,s:'20:00',e:'21:50'}]},
  {id:4,name:'고2 국어',subject:'화법과 언어',teacher:'정음 선생님',room:'201',color:'#7a5cc7',tuition:280000,sched:[{d:(w+1)%7+1,s:'17:00',e:'18:50'},{d:(w+3)%7+1,s:'17:00',e:'18:50'}]}];
 AD.mem=AD.stu.slice(0,15).map((s,i)=>({class_id:1+i%4,student_id:s.id,since:'2026-03-02'}));
 AD.att=AD.mem.filter(m=>m.class_id<=2).map((m,i)=>({student_id:m.student_id,status:i%5===4?'late':i%7===6?'abs':'in',day:adDay()}));
 AD.matt=[];for(let k=0;k<180;k++)AD.matt.push({student_id:'s'+(1+k%15),status:k%13===0?'abs':k%9===0?'late':'in',day:adDay()});
 AD.fees=AD.stu.slice(0,15).map((s,i)=>({id:i+1,student_id:s.id,title:mon.slice(5)+'월 수강료',amount:[320000,300000,360000,280000][i%4],paid_amount:i%6===5?0:[320000,300000,360000,280000][i%4],due:i%6===5&&i<8?d(-3):mon+'-25',created_at:mon+'-01'}));
 AD.cns=[{id:1,student_id:'s3',day:d(-2),kind:'학부모',body:'모의고사 이후 화학 반응 속도 단원 보강 요청',next_on:d(1),next_todo:'반응 속도 유형 학습지 전달',done:false},
  {id:2,student_id:'s7',day:d(-5),kind:'진로',body:'이과 심화반 진학 상담',next_on:d(3),next_todo:'심화반 시간표 안내',done:false},
  {id:3,student_id:'s12',day:d(-1),kind:'학생',body:'취약 유형(열화학 반응식) 복습 계획',next_on:d(5),next_todo:'2주 뒤 재진단',done:false},
  {id:4,student_id:'s17',day:d(-3),kind:'입학',body:'고1 생명 B반 체험 수업 상담',next_on:d(2),next_todo:'체험 수업 후 등록 안내',done:false}];
 AD.mku=[{id:1,student_id:'s5',missed_on:d(-4),reason:'학교 행사',plan_at:d(2)+'T18:00:00+09:00',status:'예정'},{id:2,student_id:'s9',missed_on:d(-2),reason:'병결',plan_at:d(3)+'T17:00:00+09:00',status:'예정'},{id:3,student_id:'s14',missed_on:d(-1),reason:'',plan_at:'',status:'예정'}];
 AD.changes=[];AD.tasks=[];AD.appointments=[];AD.ld=1;AD.err=''})()`;
(async()=>{const b=await chromium.launch(browserOptions());
 const ctx=await b.newContext({viewport:{width:1760,height:990},deviceScaleFactor:2,serviceWorkers:'block'});
 await ctx.addInitScript(()=>{try{localStorage.setItem('omr_theme','light');localStorage.setItem('omr_glass','off');localStorage.setItem('omr_reload_seen',String(Date.now()));localStorage.setItem('omr_snpop','9')}catch(e){}});
 await ctx.route('**/supabase.co/**',r=>r.fulfill({json:[]}));
 const pg=await ctx.newPage();pg.on('dialog',d=>d.accept());pg.on('pageerror',e=>console.log('ERR',String(e)));
 await pg.goto(BASE+'index.html?app=1');await pg.waitForTimeout(1500);
 const quiet="document.documentElement.classList.remove('entry-mode','noauth');document.querySelectorAll('#toast,.tour,#tour,#instb,#bellN,#sitebanner').forEach(e=>e.remove());try{tourEnd&&tourEnd()}catch(e){};scrollTo(0,0)";
 const shot=async(name)=>{await pg.waitForTimeout(700);await pg.screenshot({path:OUT+'/'+name+'.png'});console.log(name)};
 await pg.evaluate(FAKE+"CUR_S='s1';setSubject('me')");await pg.waitForTimeout(1500);
 await pg.evaluate(`(async()=>{const qs=DATA.filter(q=>q.set==='mc'||q.set==='top');const types=[...new Set(qs.map(q=>q.type))];const weak=new Set(types.slice(2,6));
  let seed=7;const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647};
  hist=[];for(let d=9;d>=1;d--){for(const sid of ['s1','s2','s3','s4']){const pick=[];for(let k=0;k<12;k++)pick.push(qs[Math.floor(rnd()*qs.length)]);
   hist.push({t:Date.now()-d*3*864e5,set:'book',sub:'me-t:'+(10+d),sid,items:pick.map(q=>{const r=weak.has(q.type)?rnd()<.35+0.04*(9-d):rnd()<.82;return {c:q.code,a:r?String(q.ans):String(q.ans%5+1),r:r?1:0}})})}}
  try{localStorage.setItem(LS,JSON.stringify(hist))}catch(e){}})()`);
 // 1) Pro Display(16:9, 메뉴 포함): 학원 운영 대시보드 · 원생 · 반 시간표 · 상담 일지
 await pg.evaluate("if(!cloud()){CF.url=CF.url||'https://x.supabase.co';CF.key=CF.key||'k'}");
 await pg.evaluate("lazyLoad('admin')");await pg.waitForTimeout(800);
 await pg.evaluate(ACADEMY);
 for(const [sec,name] of [['dash','xdr-dash'],['stu','xdr-stu'],['cls','xdr-cls'],['cns','xdr-cns']]){
  await pg.evaluate(quiet+";tab='admin';AD.sec='"+sec+"';render()");await pg.waitForTimeout(900);await pg.evaluate(quiet+";AD.sec='"+sec+"';adminView()");await pg.waitForTimeout(600);await pg.evaluate(quiet);await shot(name)}
 await pg.evaluate(quiet+";CUR_S='s1';tab='weak';render()");await pg.waitForTimeout(1500);await pg.evaluate("try{autoPick()}catch(e){}");await pg.waitForTimeout(900);await pg.evaluate(quiet);await shot('xdr-weak');
 await pg.evaluate(quiet+";tab='ws';render()");await pg.waitForTimeout(800);await pg.evaluate("try{resetW&&resetW()}catch(e){};tab='build';render()");await pg.waitForTimeout(1500);await pg.evaluate(quiet);await shot('xdr-build');
 // 2) MacBook(1512×982): 선생님 홈 · 학생 · 오답 진단
 await pg.setViewportSize({width:1512,height:982});await pg.waitForTimeout(500);
 await pg.evaluate(quiet+";CUR_S='';tab='thome';render()");await pg.waitForTimeout(1500);await pg.evaluate(quiet);await shot('mac-thome');
 await pg.evaluate(quiet+";CUR_S='';tab='stu';render()");await pg.waitForTimeout(1200);await pg.evaluate(quiet);await shot('mac-stu');
 await pg.evaluate(quiet+";CUR_S='s1';WRM='diag';tab='wrong';render()");await pg.waitForTimeout(1500);await pg.evaluate(quiet);await shot('mac-diag');
 // 3) iPad 세로(834×1194): 학생 홈 · 학생 유형 분석
 await pg.setViewportSize({width:834,height:1194});await pg.waitForTimeout(500);
 await pg.evaluate(quiet+";previewStudent('s1')");await pg.waitForTimeout(1500);await pg.evaluate(quiet+";document.querySelectorAll('#pvbar,.pvbar').forEach(e=>e.remove())");await shot('pad-home');
 await pg.evaluate(quiet+";tab='stat';render()");await pg.waitForTimeout(1500);await pg.evaluate(quiet+";document.querySelectorAll('#pvbar,.pvbar').forEach(e=>e.remove())");await shot('pad-stat');
 await pg.evaluate("try{exitPreview()}catch(e){}");await pg.waitForTimeout(600);
 // 4) 출결 단말(iPad 가로 1194×834)
 await pg.setViewportSize({width:1194,height:834});await pg.evaluate(quiet);
 pg.removeAllListeners('dialog');pg.on('dialog',d=>d.accept('2580'));
 await pg.evaluate("lazyLoad('acad').then(()=>{kioskOpen()})");await pg.waitForTimeout(1200);
 await pg.evaluate("KIO.pin='123';kioskDraw()");await shot('kiosk');
 await pg.evaluate("kioskClose&&kioskClose()").catch(()=>{});
 // 5) 교재 표지: 과목별 개념서 · 유형서
 const bp=await ctx.newPage();await bp.setViewportSize({width:820,height:1160});
 for(const subj of ['me','cm']){await pg.evaluate("setSubject('"+subj+"')");await pg.waitForTimeout(1500);await pg.evaluate("bkLoad()");await pg.waitForTimeout(600);
  for(const k of ['c','t']){const html=await pg.evaluate(`(async()=>{await bkInit();await conceptLoad();const p=await bkPlan('${subj}-${k}');return p?bkDocHtml(p,true):''})()`);if(!html)continue;
   await bp.setContent(html.replace('<head>','<head><base href="'+BASE+'">'),{waitUntil:'load'});await bp.evaluate('document.fonts.ready');await bp.waitForTimeout(600);
   const el=await bp.$('.bp');if(el){await el.screenshot({path:OUT+'/cover-'+subj+'-'+k+'.png'});console.log('cover-'+subj+'-'+k)}
   // 개념서의 정답과 해설 첫 쪽(교재 넘김 장면의 마지막 쪽)
   if(subj==='me'&&k==='c'){const i=await pg.evaluate(`(async()=>{const p=await bkPlan('me-c');return p.pages.findIndex(x=>x.k==='ak')})()`);const els=await bp.$$('.bp:not(.bp .bp)');if(i>=0&&els[i]){await els[i].screenshot({path:OUT+'/book-answer.png'});console.log('book-answer',i+1)}}}}
 await b.close()})()
