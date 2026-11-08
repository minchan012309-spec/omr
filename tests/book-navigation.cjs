const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');
 await page.waitForFunction(()=>typeof bkLoad==='function');
 await page.waitForTimeout(1800);
 await page.evaluate(async()=>{await bkLoad();await bkInit();await conceptLoad();tab='books';});
 for(const width of [1440,820,390]){
  await page.setViewportSize({width,height:1000});
  await page.evaluate(()=>bkBrowseStart('me-c'));
  await page.locator('.bk-navigation .bk-nav-row').first().click();
  await page.locator('.bk-navigation .bk-nav-row').first().click();
  assert.ok(await page.locator('.bk-navigation .bk-nav-row').count()>0);
  assert.ok(await page.locator('.bk-crumb').innerText());
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:`/tmp/solvi-book-nav-${width}.png`});
  await page.evaluate(async()=>{document.querySelector('#main').innerHTML='<div class="card" id="test-grade"></div>';await bkPathMount(document.getElementById('test-grade'));});
  // A real book plan, independent of the account's saved books.
  await page.evaluate(()=>{const o=new Option('검증용 개념서','me-c');document.getElementById('bkp1').add(o);document.getElementById('bkp1').value='me-c';return bkPath(1)});
  await page.locator('#bkp2').selectOption({index:1});
  // 한 쪽뿐인 구성은 자동 선택되고, 여러 쪽이면 첫 쪽을 직접 고른다
  if(await page.locator('.bk-page-choice[data-page][aria-pressed=false]').count())await page.locator('.bk-page-choice[data-page][aria-pressed=false]').first().click();
  assert.match(await page.locator('#bk-range-summary').innerText(),/문항 선택/);
  assert.equal(await page.locator('#bkpg').isEnabled(),true);
  await page.screenshot({path:`/tmp/solvi-book-grade-${width}.png`});
 }
 const result=await page.evaluate(async()=>{
  let renders=0;const orig=window.newCur,login=window.needLogin,guard=window.guardStu;
  window.newCur=()=>renders++;window.needLogin=()=>false;window.guardStu=()=>false;
  try{const id='me-c',plan=await bkPlan(id),n=plan.pages.find(p=>p.codes?.length).n;
   const a=bkGradePage(id,n),b=bkGradePage(id,n),visible=document.querySelector('#busy').classList.contains('on');await Promise.all([a,b]);return {renders,visible};
  }finally{window.newCur=orig;window.needLogin=login;window.guardStu=guard}
 });
 assert.deepEqual(result,{renders:1,visible:true});
 console.log('PASS book navigation, page range selection at 1440/820/390, loading and duplicate grading');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
