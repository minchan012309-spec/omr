/* 왼쪽 메뉴: 접기 첫 클릭부터 동작, 숨기면 본문이 가장자리까지 채워짐, 새로고침해도 상태 유지, 바뀐 뒤 resize 알림 (태블릿 세로 820 · 744) */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
const SESS={access_token:'x',refresh_token:'y',expires_at:Math.floor(Date.now()/1000)+3600,user:{id:'t1',email:'t@t.t'}};
(async()=>{const b=await chromium.launch(browserOptions());try{
 for(const [w,h] of [[820,1180],[744,1133]]){
  const ctx=await b.newContext({viewport:{width:w,height:h},serviceWorkers:'block',hasTouch:true});
  await ctx.route(/supabase\.co/,r=>r.fulfill({json:[]}));await ctx.route(/jsdelivr|googleapis|gstatic|cdnjs/,r=>r.abort());
  await ctx.addInitScript(S=>{if(sessionStorage.getItem('__s'))return;sessionStorage.setItem('__s','1');localStorage.clear();localStorage.setItem('omr_sess_v1',JSON.stringify(S))},SESS);
  const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  const go=async()=>{await p.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');await p.waitForFunction(()=>typeof sbState==='function'&&document.querySelector('#main')?.children.length>0);await p.waitForTimeout(900)};
  const geo=()=>p.evaluate(()=>{const m=document.getElementById('main').getBoundingClientRect();return {sb:document.documentElement.dataset.sb,l:Math.round(m.left),w:Math.round(m.width)}});
  await go();let g=await geo();assert.deepEqual(g,{sb:'open',l:264,w:w-264},w+' 처음');
  await p.locator('#sbTg').click();await p.waitForTimeout(400);g=await geo();assert.deepEqual(g,{sb:'mini',l:68,w:w-68},w+' 접기 첫 클릭');
  await p.locator('#sbTg').click();await p.waitForTimeout(400);g=await geo();assert.equal(g.sb,'open');
  await p.evaluate(()=>{window.__rz=0;addEventListener('resize',()=>window.__rz++)});
  await p.locator('#sbHide').click();await p.waitForTimeout(500);g=await geo();assert.deepEqual(g,{sb:'hide',l:0,w},w+' 숨김: 본문이 가장자리까지');
  assert.ok(await p.evaluate(()=>window.__rz)>=1,w+' 상태가 바뀌면 resize 알림');
  await go();g=await geo();assert.deepEqual(g,{sb:'hide',l:0,w},w+' 새로고침 뒤에도 숨김 유지');
  await p.locator('#sbh').click();await p.waitForTimeout(400);g=await geo();assert.equal(g.sb,'open');
  assert.deepEqual(errs,[]);await ctx.close()}
 console.log('PASS 왼쪽 메뉴 상태: 접기 첫 클릭 · 숨김 시 본문 채움 · 새로고침 유지 · resize 알림 (820 · 744)');
}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
