/* 학생 채점 · 연습: 서술형과 수식/화학식이 든 단답형은 입력 대신 「정답 보고 스스로 채점 → 맞았어요/틀렸어요」. 객관식은 그대로. */
const assert=require('node:assert/strict');const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const ctx=await browser.newContext({viewport:{width:1280,height:900},serviceWorkers:'block'});const sent=[];
 await ctx.route(/supabase\.co/,r=>{const fn=new URL(r.request().url()).pathname.split('/').pop();if(fn==='st_submit'){sent.push(r.request().postDataJSON());return r.fulfill({json:null})}if(fn==='st_data')return r.fulfill({json:{student:{id:'s1',name:'가학생',grade:'고2'},attempts:[],assignments:[]}});return r.fulfill({json:fn==='st_perms'?{}:[]})});
 await ctx.route(/jsdelivr|googleapis|gstatic|cdnjs/,r=>r.abort());
 await ctx.addInitScript(()=>{if(sessionStorage.getItem('__s'))return;sessionStorage.setItem('__s','1');localStorage.clear();localStorage.setItem('omr_stud_v1',JSON.stringify({login:'ga01',pw:'1234'}));localStorage.setItem('omr_auto','1')});
 const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof STUD!=='undefined'&&STUD&&STUD.login==='ga01'&&typeof setSubject==='function',null,{timeout:20000});
 await page.evaluate(()=>setSubject('me'));
 const codes=await page.evaluate(async()=>{await ensureCodes(['G-hwea3-0155','G-hwea1-0153','G-hwb4-0184']);return ['G-hwea3-0155','G-hwea1-0153','G-hwb4-0184'].map(c=>[c,byCode[c]&&byCode[c].set,selfQ(byCode[c])])});
 assert.deepEqual(codes,[['G-hwea3-0155','essay',true],['G-hwea1-0153','essay',true],['G-hwb4-0184','bank',false]]);
 assert.equal(await page.evaluate(()=>selfQ({set:'blank',ans:'H<sub>2</sub>O'})),true,'formula short answer');assert.equal(await page.evaluate(()=>selfQ({set:'blank',ans:'12'})),false,'plain short answer stays typed');
 // 채점 화면
 await page.evaluate(()=>{newCur(['G-hwea3-0155','G-hwea1-0153','G-hwb4-0184'].map(c=>byCode[c]))});await page.waitForSelector('.selfq .selfr');
 assert.equal(await page.locator('.selfq .selfr').count(),2,'two self-check questions');assert.equal(await page.locator('.selfa').count(),0,'answer hidden until asked');
 await page.locator('.selfq .selfr').first().click();await page.waitForSelector('.selfa');assert.match(await page.locator('.selfa').first().innerText(),/정답/);
 assert.equal(await page.locator('.selfa math, .selfa sub').count()>0,true,'answer shows formulas, not tag text');assert.doesNotMatch(await page.locator('.selfa').first().innerText(),/<sub>|<math>/);
 await page.getByRole('button',{name:'맞았어요'}).first().click();
 await page.locator('.selfq .selfr').first().click();await page.getByRole('button',{name:'틀렸어요'}).nth(1).click();
 await page.evaluate(()=>{cur.ans[2]=String(byCode['G-hwb4-0184'].ans)});
 await page.evaluate(()=>finish(true));await page.waitForFunction(()=>cur&&cur.done,null,{timeout:20000});
 const rec=await page.evaluate(()=>HS().slice(-1)[0].items.map(x=>[x.c,x.a,x.r]));
 assert.deepEqual(rec,[['G-hwea3-0155','O',1],['G-hwea1-0153','X',0],['G-hwb4-0184',await page.evaluate(()=>String(byCode['G-hwb4-0184'].ans)),1]]);
 assert.match(await page.locator('#main').innerText(),/틀림/,'result screen marks the self-marked wrong answer');
 // 연습(풀기) 화면
 await page.evaluate(()=>{cur=null;practice(['G-hwea3-0155'],'연습')});await page.waitForSelector('.selfq .selfr');
 await page.keyboard.press('1');assert.equal(await page.evaluate(()=>PR.shown),false,'number keys do nothing on self-check');
 await page.click('.selfq .selfr');await page.getByRole('button',{name:'틀렸어요'}).click();await page.waitForFunction(()=>PR.shown);
 assert.match(await page.locator('#main').innerText(),/틀렸다고 표시했어요/);assert.equal(await page.evaluate(()=>PR.ans[0].r),0);
 assert.deepEqual(errors,[]);
 console.log('PASS self-check answers: essays and formula short answers reveal the answer then mark 맞았어요/틀렸어요 (grading list and practice); records O=correct X=wrong; plain answers unchanged');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
