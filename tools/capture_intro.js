// 소개 페이지(intro.html)용 실제 앱 화면 캡처.  node tools/capture_intro.js <png 폴더>   (python3 server.py 가 8765에서 실행 중이어야 함)
// 개인정보가 담기지 않게 가짜 선생님·학생(이름은 「솔비 학생」처럼 지어낸 것)과 지어낸 채점 기록으로 찍는다.
// 찍은 PNG 는 tools/intro_webp.py 로 intro/*.webp 로 바꾼다.
const {chromium}=require(process.env.PW||'/opt/node-tools/node_modules/playwright');const fs=require('fs');
const OUT=process.argv[2]||'intro_png';fs.mkdirSync(OUT,{recursive:true});
const BASE=process.env.BASE||'http://localhost:8765/';
const FAKE=`sess={access_token:'x',user:{id:'demo',email:'demo@solvi.kr'}};STU=[{id:'s1',name:'솔비 학생',grade:'고2',cls:'A반'},{id:'s2',name:'하늘 학생',grade:'고2',cls:'A반'},{id:'s3',name:'바다 학생',grade:'고1',cls:'B반'},{id:'s4',name:'별빛 학생',grade:'고1',cls:'B반'}];`;
(async()=>{const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:1280,height:800},deviceScaleFactor:2,serviceWorkers:'block'});
 await ctx.addInitScript(()=>{try{localStorage.setItem('omr_theme','light');localStorage.setItem('omr_glass','off');localStorage.setItem('omr_glass_fps','60');localStorage.setItem('omr_reload_seen',String(Date.now()));localStorage.setItem('omr_snpop','9')}catch(e){}});
 const pg=await ctx.newPage();pg.on('dialog',d=>d.accept());pg.on('pageerror',e=>console.log('ERR',String(e)));
 await pg.goto(BASE+'index.html?app=1');await pg.waitForTimeout(1500);
 const shot=async(name,sel)=>{await pg.waitForTimeout(700);const el=sel?await pg.$(sel):null;
  // 앱 화면은 왼쪽 메뉴를 실제 너비(--sbw)만큼 잘라 본문만 크게
  const clip=name.startsWith('app-')?await pg.evaluate(()=>{const w=document.querySelector('body>header').getBoundingClientRect().width;return {x:Math.round(w),y:0,width:innerWidth-Math.round(w),height:innerHeight}}):null;
  await (el||pg).screenshot(clip?{path:OUT+'/'+name+'.png',clip}:{path:OUT+'/'+name+'.png'});console.log(name)};
 const quiet="document.querySelectorAll('#toast,.tour,#tour,#instb,#bellN,#sitebanner').forEach(e=>e.remove());try{tourEnd&&tourEnd()}catch(e){}";
 await pg.evaluate(FAKE+"CUR_S='s1';setSubject('me')");await pg.waitForTimeout(1500);
 // 지어낸 채점 기록: 한 달 동안 9번, 몇 유형은 자주 틀리게
 await pg.evaluate(`(async()=>{const qs=DATA.filter(q=>q.set==='mc'||q.set==='top');const types=[...new Set(qs.map(q=>q.type))];const weak=new Set(types.slice(2,6));
  let seed=7;const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647};
  hist=[];for(let d=9;d>=1;d--){for(const sid of ['s1','s2','s3']){const pick=[];for(let k=0;k<12;k++)pick.push(qs[Math.floor(rnd()*qs.length)]);
   hist.push({t:Date.now()-d*3*864e5,set:'book',sub:'me-t:'+(10+d),sid,items:pick.map(q=>{const r=weak.has(q.type)?rnd()<.35+0.04*(9-d):rnd()<.82;return {c:q.code,a:r?String(q.ans):'1',r:r?1:0}})})}}
  try{localStorage.setItem(LS,JSON.stringify(hist))}catch(e){}})()`);
 await pg.evaluate(quiet+"tab='thome';render()");await shot('app-home');
 await pg.evaluate(quiet+"CUR_S='s1';tab='weak';render()");await pg.waitForTimeout(1200);await shot('app-weak');
 await pg.evaluate(quiet+"tab='wrong';render()");await pg.waitForTimeout(1200);await shot('app-wrong');
 await pg.evaluate(quiet+"CUR_S='';tab='stu';render()");await pg.waitForTimeout(1000);await shot('app-stu');
 await pg.evaluate(quiet+"tab='ws';render()");await pg.waitForTimeout(800);await pg.evaluate("try{resetW&&resetW()}catch(e){};tab='build';render()");await pg.waitForTimeout(1500);await shot('app-build');
 await pg.evaluate(quiet+"tab='mock';render()");await pg.waitForTimeout(1500);await shot('app-mock');
 await pg.evaluate(quiet+"tab='diary';render()");await pg.waitForTimeout(2500);await shot('app-diary');
 // 출결 단말(학원 입구 태블릿, 가로): 번호를 누르는 중 + 등원 인사
 await pg.setViewportSize({width:1180,height:820});await pg.evaluate(quiet);
 pg.removeAllListeners('dialog');pg.on('dialog',d=>d.accept('2580'));
 await pg.evaluate("lazyLoad('acad').then(()=>{kioskOpen()})");await pg.waitForTimeout(1200);
 await pg.evaluate("KIO.pin='123';kioskDraw();document.getElementById('kclk').textContent='10월 27일 (화) 15:42';kioskShow('ok','솔비 학생, 어서 와요!<small>15:42 등원했어요</small>');clearTimeout(KIO.rt)");
 await shot('kiosk');await pg.evaluate("document.getElementById('kiosk').remove();clearInterval(KIO.ck);document.removeEventListener('keydown',kioskKd)");
 // 휴대폰 크기: 채점 결과(3배율)
 await pg.setViewportSize({width:390,height:844});await pg.waitForTimeout(500);
 await pg.evaluate(`(async()=>{${quiet};CUR_S='s1';const qs=DATA.filter(q=>q.set==='mc').slice(40,52);await ensureCodes(qs.map(q=>q.code));newCur(qs,{});cur.mark=false;qs.forEach((q,i)=>cur.ans[i]=(i%4===2)?String(q.ans%5+1):String(q.ans));render()})()`);
 await pg.waitForTimeout(1000);await shot('phone-omr');
 await pg.evaluate("finish(true)");await pg.waitForTimeout(1800);await pg.evaluate(quiet+"scrollTo(0,0)");await shot('phone-result');
 await pg.evaluate(quiet+"tab='weak';render();scrollTo(0,0)");await pg.waitForTimeout(1200);await shot('phone-weak');
 await pg.setViewportSize({width:1280,height:800});
 // 교재 쪽(화법과 언어, 2단 · QR)
 await pg.evaluate("setSubject('hl')");await pg.waitForTimeout(1200);await pg.evaluate('bkLoad()');await pg.waitForTimeout(400);
 const html=await pg.evaluate(`(async()=>{await bkInit();await conceptLoad();const p=await bkPlan('hl-hm');window._pl=p;return bkDocHtml(p,true)})()`);
 const want=await pg.evaluate(`(()=>{const p=window._pl,f=k=>p.pages.findIndex(k);return {cover:0,toc:1,concept:f(x=>x.k==='cn'&&x.kind==='c'),passage:f(x=>x.k==='pr'&&(x.cols||[]).flat().join('').includes('psgu bt')),problem:f(x=>x.k==='pr'&&x.label&&/Ⅱ-A/.test(x.sub&&x.sub.k||'')&&(x.cols||[]).flat().join('').includes('class="u q"')),note:f(x=>x.k==='nt')}})()`);
  const bp=await ctx.newPage();await bp.setViewportSize({width:820,height:1160});
 await bp.setContent(html.replace('<head>','<head><base href="'+BASE+'">'),{waitUntil:'load'});await bp.evaluate('document.fonts.ready');await bp.waitForTimeout(600);
 const els=await bp.$$('.bp:not(.bp .bp)');console.log('book pages',els.length);for(const [k,i] of Object.entries(want)){if(i>=0&&els[i]){await els[i].screenshot({path:OUT+'/book-'+k+'.png'});console.log('book-'+k,i+1)}}
 // 전범위 모의고사(물질과 에너지 1회) 표지 · 첫 쪽
 await pg.evaluate("setSubject('me')");await pg.waitForTimeout(1200);
 const mh=await pg.evaluate(`(async()=>{await bkInit();const p=await bkPlan('me-xe20r1');return bkDocHtml(p,true)})()`);
 await bp.setContent(mh.replace('<head>','<head><base href="'+BASE+'">'),{waitUntil:'load'});await bp.evaluate('document.fonts.ready');await bp.waitForTimeout(600);
 const me=await bp.$$('body>.bp');if(me[0])await me[0].screenshot({path:OUT+'/mock-cover.png'});if(me[1])await me[1].screenshot({path:OUT+'/mock-page.png'});console.log('mock')
 await b.close()})()
