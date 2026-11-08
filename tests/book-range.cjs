/* 교재 채점 범위(여러 쪽 · 쪽 번호 입력 · 문항 번호 검증)와 제출 중복 실행 방지 */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errs=[];page.on('pageerror',e=>errs.push(e.message));
 await page.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');
 await page.waitForFunction(()=>typeof bkLoad==='function');await page.waitForTimeout(1500);
 await page.evaluate(async()=>{await bkLoad();await bkInit();await conceptLoad();document.getElementById('main').innerHTML='<div id="rp"></div>';await bkPathMount(document.getElementById('rp'))});
 await page.evaluate(()=>{const s=document.getElementById('bkp1');if(s.options.length<2)s.add(new Option('물질과 에너지','me-c'));s.selectedIndex=1;bkPath(1)});await page.waitForFunction(()=>!document.getElementById('bkp2').disabled);
 await page.evaluate(()=>{const s=document.getElementById('bkp2');if(!s.value){s.selectedIndex=1;bkPath(2)}});
 const pages=await page.evaluate(()=>BKPATHPLAN.pages.filter(p=>p.codes&&p.codes.length).map(p=>p.n));
 assert.ok(pages.length>=2,'문제 쪽이 2쪽 이상 있어야 함');
 // 존재하지 않는 쪽 → 오류 문구, 선택 안 바뀜
 await page.fill('#bk-page-input','9999');await page.press('#bk-page-input','Enter');
 assert.match(await page.textContent('#bk-range-err'),/9999쪽에는 채점할 문제가 없어요/);
 // 쪽 범위 입력 → 여러 쪽 선택, 버튼 문구와 문항 수
 await page.fill('#bk-page-input',pages[0]+','+pages[1]);await page.press('#bk-page-input','Enter');
 assert.match(await page.textContent('#bk-range-summary'),/2쪽|, /);assert.equal(await page.textContent('#bkpg'),'2쪽 차례로 채점');
 assert.equal(await page.isDisabled('#bk-q-input'),true,'여러 쪽이면 문항 번호 입력 비활성');
 // 한 쪽 + 없는 문항 번호 → 검증 오류, 버튼 비활성
 await page.fill('#bk-page-input',String(pages[0]));await page.press('#bk-page-input','Enter');
 await page.fill('#bk-q-input','999');assert.match(await page.textContent('#bk-range-err'),/없는 문항 번호: 999/);assert.equal(await page.isDisabled('#bkpg'),true);
 // 제출 중복 실행: 두 번 눌러도 저장 · 결과 화면은 한 번
 const r=await page.evaluate(async()=>{const qs=Object.values(byCode).slice(0,2);newCur(qs,{});cur.ans=qs.map(q=>q.ans);let n=0;const o=window.render;window.render=function(){n++;return o.apply(this,arguments)};const h0=hist.length;
  const a=finish(),b=finish();await Promise.all([a,b]);await finish();window.render=o;return {added:hist.length-h0,n}});
 assert.equal(r.added,1,'기록은 한 번만 저장');assert.equal(r.n,1,'결과 화면은 한 번만 그림');
 assert.deepEqual(errs,[]);console.log('PASS 교재 채점 범위 · 제출 중복 방지');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
