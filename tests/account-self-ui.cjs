/* 계정 화면: 선생님이 발급한 학생 계정의 첫 로그인 재설정 창, 학생 · 학부모 설정의 「개인정보 수정」, 선생님 비밀번호 변경. 서버는 가짜 응답. */
const assert=require('node:assert/strict');const {chromium,browserOptions}=require('./runtime.cjs');
const SESS={access_token:'t1',refresh_token:'r1',user:{id:'u-t',email:'teacher@example.com'}};
async function app(browser,{teacher=false}={}){const ctx=await browser.newContext({viewport:{width:1280,height:900},serviceWorkers:'block'});const calls=[];
 const cred={login:'ga01',pw:'1234',reset:true};
 await ctx.route(/supabase\.co/,route=>{const req=route.request(),u=new URL(req.url()),b=req.postDataJSON?.()||{};calls.push({path:u.pathname,method:req.method(),body:b});
  const fn=u.pathname.split('/').pop();
  if(fn==='st_login')return route.fulfill({json:b.p_login===cred.login&&b.p_pw===cred.pw?{id:'s1',name:'가학생',grade:'고2',must_reset:cred.reset}:null});
  if(fn==='st_change_credentials'){if(b.p_pw!==cred.pw)return route.fulfill({json:'auth'});if(b.p_new_login==='taken1')return route.fulfill({json:'taken'});Object.assign(cred,{login:b.p_new_login,pw:b.p_new_pw,reset:false});return route.fulfill({json:'ok'})}
  if(fn==='st_issue_token')return route.fulfill({json:null});
  if(fn==='st_data')return route.fulfill({json:{student:{id:'s1',name:'가학생',grade:'고2'},attempts:[],assignments:[]}});
  if(u.pathname.endsWith('/auth/v1/token'))return route.fulfill(b.password==='oldpass1'||b.refresh_token?{json:SESS}:{status:400,json:{error_description:'Invalid login credentials'}});
  if(u.pathname.endsWith('/auth/v1/user')&&req.method()==='PUT')return route.fulfill({json:{id:'u-t',email:SESS.user.email}});
  return route.fulfill({json:[]})});
 await ctx.route(/jsdelivr|googleapis|gstatic|cdnjs/,r=>r.abort());
 await ctx.addInitScript(({teacher,SESS})=>{if(sessionStorage.getItem('__s'))return;sessionStorage.setItem('__s','1');localStorage.clear();if(teacher)localStorage.setItem('omr_sess_v1',JSON.stringify(SESS))},{teacher,SESS});
 const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof render==='function'&&document.querySelector('#main')&&document.querySelector('#main').children.length>0);await page.waitForTimeout(600);
 return {ctx,page,calls,cred,errors}}
const typeLogin=(page,id,pw)=>page.evaluate(([id,pw])=>{for(const [k,v] of [['stid',id],['stpw',pw]]){let e=document.getElementById(k);if(!e){e=document.createElement('input');e.id=k;e.hidden=true;document.body.appendChild(e)}e.value=v}PRL=0;stLogin()},[id,pw]);
(async()=>{const browser=await chromium.launch(browserOptions());try{
 // 1) 첫 로그인: 재설정 창이 먼저, 정하기 전에는 로그인되지 않음
 {const {ctx,page,calls,cred,errors}=await app(browser);
  await typeLogin(page,'ga01','1234');await page.waitForSelector('#cfg.open .credf');
  assert.match(await page.locator('#cfgBox h2').innerText(),/처음 로그인/);assert.equal(await page.locator('#crl').inputValue(),'ga01');assert.equal(await page.locator('#crc').count(),0,'no current-password field on first login');
  assert.equal(await page.evaluate(()=>!!STUD),false,'not logged in before choosing new credentials');
  await page.fill('#crl','gahak');await page.fill('#crp','abcdef');await page.fill('#crp2','abcdeX');await page.click('#crs');assert.match(await page.locator('#crm').innerText(),/서로 달라요/);
  await page.fill('#crp','abc');await page.fill('#crp2','abc');await page.click('#crs');assert.match(await page.locator('#crm').innerText(),/6자 이상/);
  await page.fill('#crl','taken1');await page.fill('#crp','abcdef');await page.fill('#crp2','abcdef');await page.click('#crs');await page.waitForFunction(()=>/이미 쓰고/.test(document.getElementById('crm').textContent));
  await page.fill('#crl','gahak');await page.click('#crs');await page.waitForFunction(()=>STUD&&STUD.login==='gahak');
  const ch=calls.filter(c=>c.path.endsWith('st_change_credentials')).pop();assert.deepEqual([ch.body.p_login,ch.body.p_pw,ch.body.p_new_login,ch.body.p_new_pw],['ga01','1234','gahak','abcdef']);
  assert.equal(await page.evaluate(()=>STUD.pw),'abcdef','session uses the new password');
  // 2) 학생 설정: 개인정보 수정 → 틀린 지금 비밀번호, 맞으면 변경
  await page.evaluate(()=>openSettings());await page.waitForSelector('#sprof');assert.match(await page.locator('#sprof').innerText(),/gahak/);
  await page.click('#sprof button');await page.waitForSelector('.credf #crc');
  await page.fill('#crc','wrong');await page.fill('#crp','newpass');await page.fill('#crp2','newpass');await page.click('#crs');await page.waitForFunction(()=>/맞지 않아요/.test(document.getElementById('crm').textContent));
  await page.fill('#crc','abcdef');await page.click('#crs');await page.waitForFunction(()=>STUD&&STUD.pw==='newpass');assert.equal(cred.pw,'newpass');
  assert.deepEqual(errors,[]);await ctx.close()}
 // 3) 선생님: 개인정보 수정 → 비밀번호 바꾸기
 {const {ctx,page,calls,errors}=await app(browser,{teacher:true});
  await page.evaluate(()=>openCfg());await page.waitForSelector('#tprof');assert.match(await page.locator('#tprof').innerText(),/teacher@example\.com/);
  await page.fill('#tpc','bad');await page.fill('#tpn','newpass1');await page.fill('#tpn2','newpass1');await page.click('#tps');await page.waitForFunction(()=>/맞지 않아요/.test(document.getElementById('tpm').textContent));
  await page.fill('#tpc','oldpass1');await page.click('#tps');await page.waitForFunction(()=>/바꿨어요/.test(document.getElementById('tpm').textContent));
  const put=calls.find(c=>c.path.endsWith('/auth/v1/user')&&c.method==='PUT');assert.equal(put.body.password,'newpass1');
  assert.deepEqual(errors,[]);await ctx.close()}
 console.log('PASS account UI: first-login reset before sign-in (validation, taken id), student settings change with current password, teacher password change');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
