/* 스크롤 진행바 · 스켈레톤 · 문항 수 스테퍼 · 당겨서 새로고침 · 채점 완료 연출 */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
const SESS={access_token:'x',refresh_token:'y',expires_at:Math.floor(Date.now()/1000)+3600,user:{id:'t1',email:'t@t.t'}};
(async()=>{const b=await chromium.launch(browserOptions());try{
 const ctx=await b.newContext({viewport:{width:390,height:844},serviceWorkers:'block',hasTouch:true});
 await ctx.route(/supabase\.co/,r=>r.fulfill({json:[]}));await ctx.route(/jsdelivr|googleapis|gstatic|cdnjs/,r=>r.abort());
 await ctx.addInitScript(S=>{if(sessionStorage.getItem('__s'))return;sessionStorage.setItem('__s','1');localStorage.clear();localStorage.setItem('omr_sess_v1',JSON.stringify(S))},SESS);
 const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');await p.waitForFunction(()=>typeof celebrate==='function'&&document.querySelector('#main')?.children.length>0);await p.waitForTimeout(1200);
 // 스켈레톤: 막대(회전 표시) 대신 자리 표시
 const sk=await p.evaluate(()=>{const d=document.createElement('div');d.innerHTML=ldg('교재를 불러오는 중…');document.body.appendChild(d);const n=d.querySelectorAll('.sk').length,spin=!!d.querySelector('.ldg>i'),t=d.querySelector('.sr-only').textContent;d.remove();return {n,spin,t}});
 assert.ok(sk.n>=3&&!sk.spin&&sk.t==='교재를 불러오는 중…',JSON.stringify(sk));
 // 스크롤 진행바
 await p.evaluate(()=>{document.getElementById('main').insertAdjacentHTML('beforeend','<div style="height:3000px"></div>');scrollTo(0,0)});await p.waitForTimeout(1700);
 const p0=await p.evaluate(()=>getComputedStyle(document.querySelector('#sprog')).opacity);
 await p.evaluate(()=>scrollTo(0,document.documentElement.scrollHeight));await p.waitForTimeout(400);
 const sc=await p.evaluate(()=>new DOMMatrix(getComputedStyle(document.querySelector('#sprog i')).transform).a);assert.equal(p0,'1');assert.ok(sc>.95,'맨 아래에서 진행바가 가득 참 '+sc);
 // 스테퍼
 await p.evaluate(()=>{scrollTo(0,0);document.getElementById('main').innerHTML='<div id="t">'+numStepper(4,1,60,'bulkN',1)+'</div>';window.__v=[];window.bulkN=v=>window.__v.push(v)});
 await p.locator('.numstp button').nth(1).click();await p.locator('.numstp button').nth(1).click();await p.locator('.numstp button').nth(0).click();
 assert.deepEqual(await p.evaluate(()=>window.__v),[5,6,5]);assert.equal(await p.locator('.numstp input').inputValue(),'5');
 await p.fill('.numstp input','999');await p.press('.numstp input','Tab');assert.equal(await p.locator('.numstp input').inputValue(),'60','상한을 넘으면 상한으로');
 assert.ok((await p.locator('.numstp button').first().boundingBox()).height>=44,'터치 크기 44px');
 // 당겨서 새로고침
 const touch=(type,y)=>p.evaluate(([type,y])=>{const t=new Touch({identifier:1,target:document.body,clientX:195,clientY:y});document.body.dispatchEvent(new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true}))},[type,y]);
 await p.evaluate(()=>{window.__rf=0;window.hardRefresh=async()=>{window.__rf++}});
 await touch('touchstart',100);await touch('touchmove',150);await touch('touchend',150);await p.waitForTimeout(500);assert.equal(await p.evaluate(()=>window.__rf),0,'조금만 당기면 새로고침하지 않음');
 await touch('touchstart',100);await touch('touchmove',160);await touch('touchmove',260);assert.ok(await p.evaluate(()=>document.getElementById('ptr').classList.contains('rdy')),'충분히 당기면 준비 표시');
 await touch('touchend',260);await p.waitForTimeout(600);assert.equal(await p.evaluate(()=>window.__rf),1,'놓으면 새로고침');
 await p.evaluate(()=>{document.getElementById('main').insertAdjacentHTML('beforeend','<div style="height:3000px"></div>');window.scrollTo(0,300)});await p.waitForTimeout(100);assert.ok(await p.evaluate(()=>scrollY)>0);await touch('touchstart',100);await touch('touchmove',300);await touch('touchend',300);await p.waitForTimeout(500);assert.equal(await p.evaluate(()=>window.__rf),1,'맨 위가 아니면 쓰지 않음');
 // 완료 연출
 await p.evaluate(()=>{scrollTo(0,0);document.body.insertAdjacentHTML('beforeend','<div id="fx" style="position:absolute"><div class="mring"><b>80</b></div></div>');celebrate(.95)});
 await p.waitForTimeout(150);assert.equal(await p.locator('#donep').count(),1);assert.ok(await p.locator('#cft i').count()>=40,'색종이');
 await p.waitForTimeout(1900);assert.equal(await p.locator('#donep').count(),0,'완료 표시는 사라짐');assert.equal(await p.locator('#cft').count(),0,'색종이도 정리됨');assert.equal(await p.locator('#fx .mring b').textContent(),'80','점수가 최종값으로 끝남');
 await ctx.close();
 // 움직임 줄이기: 색종이 없음
 const c2=await b.newContext({viewport:{width:390,height:844},reducedMotion:'reduce',serviceWorkers:'block'});const q=await c2.newPage();await q.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');await q.waitForFunction(()=>typeof celebrate==='function');
 await q.evaluate(()=>celebrate(1));assert.equal(await q.locator('#cft').count(),0,'움직임 줄이기에서는 색종이 없음');await c2.close();
 assert.deepEqual(errs,[]);console.log('PASS 스켈레톤 · 스크롤 진행바 · 스테퍼 · 당겨서 새로고침 · 완료 연출(움직임 줄이기 포함)');
}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
