/* 로그인 화면의 「회원가입」을 누르면 가입 폼이 뜨고, 신청하면 승인 대기 화면, 닫으면 로그인으로 돌아온다 (1440 · 390) */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const b=await chromium.launch(browserOptions());try{
 for(const width of [1440,390]){
  const ctx=await b.newContext({viewport:{width,height:900}});const p=await ctx.newPage();
  await ctx.route('**/rest/v1/rpc/**',r=>{const f=r.request().url().split('/').pop();r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:f==='st_signup'?'{"ok":true}':'"pending"'})}); // 서버 호출은 가짜로 막아 실제 가입 요청이 나가지 않게
const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');await p.waitForFunction(()=>typeof sgOpen==='function');await p.waitForTimeout(1500);
  await p.locator('#er-tab-student').click();
  await p.locator('.sgjoin button:has-text("회원가입")').click();
  assert.equal(await p.locator('#sgc').count(),1,width+': 가입 폼이 안 뜸');
  assert.match(await p.locator('#stbody h2').innerText(),/학생 회원가입/);
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,width+': 가로 넘침');
  // 빈 입력 → 오류 문구
  await p.locator('#sgbtn').click();assert.match(await p.locator('#sgerr').innerText(),/코드/);
  await p.fill('#sgc','ABC123');await p.fill('#sgn','테스트');await p.fill('#sgl','test_01');await p.fill('#sgp','1234');await p.fill('#sgp2','1234');
  await p.locator('#sgbtn').click();await p.waitForFunction(()=>/승인 대기/.test(document.querySelector('#stbody')?.innerText||''));
  assert.equal(await p.locator('.entry-card .card').count(),0,width+': 카드 안에 카드');
  await p.evaluate(()=>{try{localStorage.removeItem(SGK)}catch(e){}});await p.evaluate(()=>{sgOpen('login')});
  assert.match(await p.locator('#stbody h2').innerText(),/학생 로그인/);
  assert.deepEqual(errs,[]);await ctx.close()}
 console.log('PASS 학생 회원가입: 폼 → 신청 → 승인 대기 → 로그인 (1440 · 390)');
}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
