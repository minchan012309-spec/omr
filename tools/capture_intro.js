// 소개 페이지(intro.html)용 실제 앱 화면 캡처.  node tools/capture_intro.js <png 폴더>   (python3 server.py 가 8765에서 실행 중이어야 함)
// 개인정보가 담기지 않게 가짜 선생님·학생(이름은 「솔비 학생」처럼 지어낸 것)과 지어낸 채점 기록으로 찍는다.
// 찍은 PNG 는 tools/intro_webp.py 로 intro/*.webp 로 바꾼다.
//  PW=<playwright 경로>  CHANNEL=chrome(설치된 크롬으로 찍기)  BASE=<주소>
// 크기 규칙: phone-* = 390×844 · book-*/mock-* = A4 한 쪽. 디스플레이 · 노트북 · 태블릿 화면과 표지는 tools/capture_cine.js 가 찍는다
const {chromium}=require(process.env.PW||'/opt/node-tools/node_modules/playwright');const fs=require('fs');
const OUT=process.argv[2]||'intro_png';fs.mkdirSync(OUT,{recursive:true});
const BASE=process.env.BASE||'http://localhost:8765/';
const FAKE=`sess={access_token:'x',user:{id:'demo',email:'demo@solvi.kr'}};STU=[{id:'s1',name:'솔비 학생',grade:'고2',cls:'A반'},{id:'s2',name:'하늘 학생',grade:'고2',cls:'A반'},{id:'s3',name:'바다 학생',grade:'고1',cls:'B반'},{id:'s4',name:'별빛 학생',grade:'고1',cls:'B반'}];`;
(async()=>{const b=await chromium.launch(process.env.CHANNEL?{channel:process.env.CHANNEL}:{});
 const ctx=await b.newContext({viewport:{width:1600,height:900},deviceScaleFactor:2,serviceWorkers:'block'});
 await ctx.addInitScript(()=>{try{localStorage.setItem('omr_theme','light');localStorage.setItem('omr_glass','off');localStorage.setItem('omr_glass_fps','60');localStorage.setItem('omr_reload_seen',String(Date.now()));localStorage.setItem('omr_snpop','9')}catch(e){}});
 const pg=await ctx.newPage();pg.on('dialog',d=>d.accept());pg.on('pageerror',e=>console.log('ERR',String(e)));
 await pg.goto(BASE+'index.html?app=1');await pg.waitForTimeout(1500);
 // 본문만 찍을 때: 왼쪽 메뉴 너비만큼 창을 넓혀 본문이 정확히 1280×800 이 되게
 const sbw=async()=>pg.evaluate(()=>Math.round(document.querySelector('body>header').getBoundingClientRect().width));
 const shot=async(name,mode)=>{await pg.waitForTimeout(700);
  const clip=mode==='body'?{x:await sbw(),y:0,width:1280,height:800}:null;
  await pg.screenshot(clip?{path:OUT+'/'+name+'.png',clip}:{path:OUT+'/'+name+'.png'});console.log(name)};
 const quiet="document.querySelectorAll('#toast,.tour,#tour,#instb,#bellN,#sitebanner').forEach(e=>e.remove());try{tourEnd&&tourEnd()}catch(e){};scrollTo(0,0)";
 await pg.evaluate(FAKE+"CUR_S='s1';setSubject('me')");await pg.waitForTimeout(1500);
 // 지어낸 채점 기록: 한 달 동안 9번, 몇 유형은 자주 틀리게
 await pg.evaluate(`(async()=>{const qs=DATA.filter(q=>q.set==='mc'||q.set==='top');const types=[...new Set(qs.map(q=>q.type))];const weak=new Set(types.slice(2,6));
  let seed=7;const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647};
  hist=[];for(let d=9;d>=1;d--){for(const sid of ['s1','s2','s3','s4']){const pick=[];for(let k=0;k<12;k++)pick.push(qs[Math.floor(rnd()*qs.length)]);
   hist.push({t:Date.now()-d*3*864e5,set:'book',sub:'me-t:'+(10+d),sid,items:pick.map(q=>{const r=weak.has(q.type)?rnd()<.35+0.04*(9-d):rnd()<.82;return {c:q.code,a:r?String(q.ans):String(q.ans%5+1),r:r?1:0}})})}}
  try{localStorage.setItem(LS,JSON.stringify(hist))}catch(e){}})()`);
 // 3) 휴대폰(390×844): 채점 화면 · 결과 · 학생 홈 · 학부모 홈
 await pg.setViewportSize({width:390,height:844});await pg.waitForTimeout(500);
 await pg.evaluate(`(async()=>{${quiet};CUR_S='s1';const qs=DATA.filter(q=>q.set==='mc').slice(40,52);await ensureCodes(qs.map(q=>q.code));newCur(qs,{});cur.mark=false;qs.forEach((q,i)=>cur.ans[i]=(i%4===2)?String(q.ans%5+1):String(q.ans));render()})()`);
 await pg.waitForTimeout(1000);await pg.evaluate("scrollTo(0,0)");await shot('phone-omr');
 await pg.evaluate("finish(true)");await pg.waitForTimeout(1800);await pg.evaluate(quiet);await shot('phone-result');
 await pg.evaluate(quiet+";CUR_S='s1';tab='weak';render()");await pg.waitForTimeout(1200);await pg.evaluate(quiet);await shot('phone-weak');
 await pg.evaluate(quiet+";previewStudent('s1')");await pg.waitForTimeout(1500);await pg.evaluate(quiet+";document.querySelectorAll('#pvbar,.pvbar').forEach(e=>e.remove())");await shot('phone-home');
 await pg.evaluate("try{exitPreview()}catch(e){}");await pg.waitForTimeout(600);
 await pg.evaluate(quiet+";previewStudent('s1',1)");await pg.waitForTimeout(1500);await pg.evaluate(quiet+";document.querySelectorAll('#pvbar,.pvbar').forEach(e=>e.remove())");await shot('phone-parent');
 await pg.evaluate("try{exitPreview()}catch(e){}");await pg.waitForTimeout(600);
 await pg.setViewportSize({width:1280,height:800});
 // 4) A4 쪽: 학습지 한 장(2단 · QR)
 const bp=await ctx.newPage();await bp.setViewportSize({width:820,height:1160});
 const wsHost=await pg.evaluate(`(async()=>{const qs=DATA.filter(q=>q.set==='mc').slice(60,68);await ensureCodes(qs.map(q=>q.code));const h=document.createElement('div');h.id='wsCap';h.style.cssText='position:absolute;left:0;top:0;width:820px;background:#fff';document.body.appendChild(h);
  await openWs({id:'04271938',t:Date.now(),codes:qs.map(q=>q.code),title:'촉매와 반응 속도',cols:2,style:'basic',color:'blue'},h);await new Promise(r=>setTimeout(r,800));return h.shadowRoot?h.shadowRoot.innerHTML:''})()`);
 if(wsHost){await bp.setContent('<!doctype html><html><head><base href="'+BASE+'"></head><body style="margin:0;background:#fff">'+wsHost+'</body></html>',{waitUntil:'load'});await bp.evaluate('document.fonts.ready');await bp.waitForTimeout(600);const p=await bp.$('.pg');if(p){await p.screenshot({path:OUT+'/book-sheet.png'});console.log('book-sheet')}}
 await pg.evaluate("const h=document.getElementById('wsCap');if(h)h.remove()");
 // 5) 교재 쪽: 물질과 에너지 개념서(표지 · 개념 · OX · 빈칸) · 유형서 문제 쪽
 await pg.evaluate("bkLoad()");await pg.waitForTimeout(400);
 const book=async(id,want)=>{const html=await pg.evaluate(`(async()=>{await bkInit();await conceptLoad();const p=await bkPlan('${id}');window._pl=p;return bkDocHtml(p,true)})()`);
  const idx=await pg.evaluate(`(()=>{const p=window._pl,r={};${want};return r})()`);
  await bp.setContent(html.replace('<head>','<head><base href="'+BASE+'">'),{waitUntil:'load'});await bp.evaluate('document.fonts.ready');await bp.waitForTimeout(600);
  const els=await bp.$$('.bp:not(.bp .bp)');for(const [k,i] of Object.entries(idx)){if(i>=0&&els[i]){await els[i].screenshot({path:OUT+'/book-'+k+'.png'});console.log('book-'+k,i+1)}}};
 const has=s=>`(x.cols||[]).flat().join('').includes('${s}')`;
 await book('me-c',`const f=k=>p.pages.findIndex(k);r.cover=0;r.concept=f(x=>x.k==='cn'&&x.kind==='c');r.ox=f(x=>x.k==='pr'&&x.kind==='ox');r.basic=f(x=>x.k==='pr'&&x.kind==='mc')`);
 await book('me-t',`const f=k=>p.pages.findIndex(k);r.toc=1;r.problem=f(x=>x.k==='pr'&&${has('class="u q"')})`);
 // 6) 전범위 모의고사(물질과 에너지 1회) 표지
 const mh=await pg.evaluate(`(async()=>{await bkInit();const p=await bkPlan('me-xe20r1');return bkDocHtml(p,true)})()`);
 await bp.setContent(mh.replace('<head>','<head><base href="'+BASE+'">'),{waitUntil:'load'});await bp.evaluate('document.fonts.ready');await bp.waitForTimeout(600);
 const me=await bp.$$('body>.bp');if(me[0])await me[0].screenshot({path:OUT+'/mock-cover.png'});console.log('mock');
 await b.close()})()
