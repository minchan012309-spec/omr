// 인쇄 옵션 「유형명」: 유형 제목 줄에 유형명을 넣거나 뺀다(쪽 계획 캐시도 따로)
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.route(/supabase\.co/, route=>route.fulfill({json:[]}));
 await page.addInitScript(()=>localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test-token',user:{id:'test'}})));
 await page.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');
 await page.waitForFunction(()=>typeof bkLoad==='function'&&!!Object.keys(BIDX).length&&teacher());
 const r=await page.evaluate(async()=>{await bkLoad();await bkInit();await conceptLoad();
  const ths=p=>p.pages.flatMap(x=>[...(x.cols||[]).flat(),...(x.top||[])]).join('').match(/<div class="th">.*?<\/div>/g)||[];
  bkOset({tn:''});const a=await bkPlan('me-t');const ta=ths(a),barA=bkBarHtml(a);
  bkOset({tn:'0'});const b=await bkPlan('me-t');const tb=ths(b),barB=bkBarHtml(b);
  bkOset({tn:''});const c=await bkPlan('me-c');
  return {th:a.th,na:ta.length,nb:tb.length,withName:ta.every(h=>h.includes('<span>')),noName:tb.every(h=>!h.includes('<span>')),same:a!==b,
   barA:/id="ptn"/.test(barA)&&/value="1" selected/.test(barA.split('id="ptn"')[1]),barB:/value="0" selected/.test(barB.split('id="ptn"')[1]),barC:/id="ptn"/.test(bkBarHtml(c))||!c.th}});
 assert.equal(r.th,true);assert.ok(r.na>0);assert.equal(r.na,r.nb);
 assert.equal(r.withName,true);assert.equal(r.noName,true);assert.equal(r.same,true);
 assert.equal(r.barA,true);assert.equal(r.barB,true);assert.equal(r.barC,true);
 console.log('PASS book type-name print option ('+r.na+' type headers)');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
