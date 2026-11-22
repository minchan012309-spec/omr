/* 학생 계정: 통합검색에 문항 코드(대소문자 · 자릿수 상관없이)를 넣으면 그 문항을 풀기 화면으로 연다. 없는 코드는 안내. */
const assert=require('node:assert/strict');const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const ctx=await browser.newContext({viewport:{width:1280,height:900},serviceWorkers:'block'});
 await ctx.route(/supabase\.co/,r=>{const fn=new URL(r.request().url()).pathname.split('/').pop();if(fn==='st_data')return r.fulfill({json:{student:{id:'s1',name:'가학생',grade:'고2'},attempts:[],assignments:[]}});return r.fulfill({json:fn==='st_perms'?{}:[]})});
 await ctx.route(/jsdelivr|googleapis|gstatic|cdnjs/,r=>r.abort());
 await ctx.addInitScript(()=>{if(sessionStorage.getItem('__s'))return;sessionStorage.setItem('__s','1');localStorage.clear();localStorage.setItem('omr_stud_v1',JSON.stringify({login:'ga01',pw:'1234'}));localStorage.setItem('omr_auto','1')});
 const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof STUD!=='undefined'&&STUD&&STUD.login==='ga01'&&typeof setSubject==='function',null,{timeout:20000});
 await page.evaluate(()=>setSubject('me'));
 await page.evaluate(()=>openPalette());await page.fill('#pal','g-hwd3-233');
 const first=await page.locator('#pall .pit').first().innerText();assert.equal(first,'문항 코드로 열기 · G-hwd3-0233');
 await page.keyboard.press('Enter');await page.waitForFunction(()=>PR&&PR.qs&&PR.qs.length===1,null,{timeout:20000});
 assert.equal(await page.evaluate(()=>PR.qs[0].code),'G-hwd3-0233');
 await page.evaluate(()=>{PR=null;render()});
 await page.evaluate(()=>openPalette());await page.fill('#pal','G-hwd3-9999');await page.keyboard.press('Enter');
 await page.waitForFunction(()=>/찾지 못했어요/.test(document.body.innerText),null,{timeout:20000});
 assert.equal(await page.evaluate(()=>qCodeNorm('q31-1')),'Q31-001');assert.equal(await page.evaluate(()=>qCodeNorm('엔탈피')),'');
 assert.deepEqual(errors,[]);
 console.log('PASS student code search: palette opens G-hwd3-0233 (typed g-hwd3-233) in practice, unknown code shows a message');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
