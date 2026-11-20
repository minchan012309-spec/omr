const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.addInitScript(()=>{localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}}));const f=window.fetch.bind(window);window.fetch=(u,o)=>String(typeof u==='string'?u:u.url).includes('supabase.co')?Promise.resolve(new Response('[]',{headers:{'Content-Type':'application/json'}})):f(u,o)});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof openWs==='function'&&Object.keys(BIDX).length&&teacher());
 for(const liveDesign of [0,1]){
 const result=await page.evaluate(async(liveDesign)=>{
  await ensureTags([Object.keys(BIDX)[0]]);
  const codes=DATA.filter(q=>q.set==='bank').slice(0,4).map(q=>q.code);
  wsPopStart=()=>null;await openWs({id:'12345678',t:Date.now(),codes,title:'취약 유형 학습지',academy:'A1 수학과학',subt:'제거할 부제',name:'예시',style:'w-simple',liveDesign,ans:1,cols:2,per:2,qr:1});
  const root=document.querySelector('#wsPaper').shadowRoot;
  return [...root.querySelectorAll('.pg:not(.wblank)')].map(pg=>({kind:pg.dataset.solviKind,firstHeader:!!pg.querySelector('.ph1'),firstTitle:pg.querySelector('.ph1 .tt')?.textContent,head:[...pg.querySelector('.ws-simple-header')?.children||[]].map(e=>e.textContent),topQr:pg.querySelectorAll('.qrh').length,footer:pg.querySelector('.pf .qr')?.textContent,qrVisible:pg.querySelector('.pf .qr')?getComputedStyle(pg.querySelector('.pf .qr')).display:null,rule:pg.querySelector('.ws-simple-header')?getComputedStyle(pg.querySelector('.ws-simple-header')).borderBottomWidth:null}));
 },liveDesign);
 assert.ok(result.length>=3);
 assert.equal(result[0].firstHeader,true,'first page retains original header');assert.equal(result[0].firstTitle,'취약 유형 학습지');assert.equal(result[0].topQr,1);assert.equal(result[0].footer,undefined);
 for(const p of result.slice(1)){assert.deepEqual(p.head,['취약 유형 학습지','A1 수학과학']);assert.equal(p.topQr,0);assert.ok(parseFloat(p.rule)>0);if(p.kind==='questions'){assert.match(p.footer,/채점하려면 스캔하거나/);assert.match(p.footer,/1234-5678/);assert.notEqual(p.qrVisible,'none')}}
 }
 console.log('PASS original first page, simplified continuation header and original footer, live and legacy');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
