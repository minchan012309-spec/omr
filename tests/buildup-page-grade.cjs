/* 해원고 빌드업 문항 모음(2264-3735): 번호 · QR로 열면 몇 쪽을 채점할지 묻고, 그 쪽 문항만 채점 → 다음 쪽. 쪽마다 따로 기록(rng p<n>), 채점한 쪽은 다시 못 고름. */
const assert=require('node:assert/strict');const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1280,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 await page.addInitScript(()=>{localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}}));const f=window.fetch.bind(window);window.fetch=(i,n)=>String(typeof i==='string'?i:i.url).includes('supabase.co')?Promise.resolve(new Response('[]',{status:200,headers:{'Content-Type':'application/json'}})):f(i,n)});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof openByNumber==='function'&&Object.keys(BIDX).length&&teacher());
 const d=await page.evaluate(async()=>{await setSubject('me');const d=await presetData('me-haewon-buildup');WSH.push({id:d.id,t:Date.now(),title:d.title,codes:d.codes,preset:'me-haewon-buildup'});STU.push({id:'s9',name:'예시'});CUR_S='s9';return {n:d.pages.length,p3:d.pages[2],p4:d.pages[3]}});
 assert.equal(d.n,53);
 await page.evaluate(()=>openByNumber('2264-3735'));await page.waitForSelector('#bpw .bpw-i.on');
 assert.match(await page.locator('#cfgBox h2').innerText(),/몇 쪽을 채점할까요/);
 assert.equal(await page.locator('#bpn').count(),0,'no keyboard input box');assert.equal(await page.locator('#bpw .bpw-i').count(),53);
 await page.evaluate(()=>{const w=document.getElementById('bpw');w.scrollTop=2*44});await page.waitForFunction(()=>BP.n===3&&document.querySelector('#bpw .bpw-i.on').dataset.n==='3');
 await page.keyboard.press('ArrowDown');await page.waitForFunction(()=>BP.n===4);await page.keyboard.press('ArrowUp');await page.waitForFunction(()=>BP.n===3);
 await page.click('.bpgo-b');await page.waitForFunction(()=>cur&&cur.ws&&cur.ws.pg===3);
 assert.deepEqual(await page.evaluate(()=>cur.qs.map(q=>q.code)),d.p3);
 await page.evaluate(()=>{cur.qs.forEach((q,i)=>cur.ans[i]=String(q.ans||'1'))});await page.evaluate(()=>finish(true));await page.waitForFunction(()=>cur&&cur.done);
 const rec=await page.evaluate(()=>{const h=hist[hist.length-1];return {set:h.set,sub:h.sub,rng:h.rng,n:h.items.length}});assert.deepEqual(rec,{set:'ws',sub:'22643735',rng:'p3',n:d.p3.length});
 await page.getByRole('button',{name:'다음 쪽(4쪽) 채점'}).click();await page.waitForFunction(()=>cur&&cur.ws&&cur.ws.pg===4&&!cur.done);
 assert.deepEqual(await page.evaluate(()=>cur.qs.map(q=>q.code)),d.p4);
 await page.evaluate(()=>{leaveGradeNow&&leaveGradeNow();bpAsk(3)});await page.waitForSelector('#bpw .bpw-i.on');assert.match(await page.locator('#bpw [data-n="3"]').innerText(),/채점함/);await page.click('.bpgo-b');assert.match(await page.locator('#bpm').innerText(),/이미 채점/);
 assert.deepEqual(errors,[]);
 console.log('PASS buildup page grading: 2264-3735 asks the page with a wheel picker, grades only that page (rng p3), next page button, graded page blocked');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
