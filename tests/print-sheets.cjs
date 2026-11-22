/* 인쇄 창: 학습지 양면 인쇄 빈 쪽에 로고가 보이는지, 교재를 해설 없이 만들었어도 인쇄 창에서 문제지 · 답안지 · 해설을 켜고 끌 수 있는지. */
const assert=require('node:assert/strict');const {chromium,browserOptions}=require('./runtime.cjs');
async function app(browser,{width=1440,tablet=false}={}){const ctx=await browser.newContext({viewport:{width,height:1000},hasTouch:tablet,userAgent:tablet?'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1':undefined});const page=await ctx.newPage();
 await page.addInitScript(()=>{localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}}));localStorage.setItem('omr_duplex','1');const fetch=window.fetch.bind(window);window.fetch=(input,init)=>String(typeof input==='string'?input:input.url).includes('supabase.co')?Promise.resolve(new Response('[]',{status:200,headers:{'Content-Type':'application/json'}})):fetch(input,init)});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof bkLoad==='function'&&Object.keys(BIDX).length&&teacher());return page}
(async()=>{const browser=await chromium.launch(browserOptions());try{
 // 1) 학습지 양면 인쇄 빈 쪽 로고
 {const page=await app(browser);const pp=page.waitForEvent('popup');
  await page.evaluate(async()=>{await setSubject('me');const qs=DATA.filter(q=>q.set==='mc').slice(0,5).map(q=>q.code);const r=mkWs(qs,{...wsOpts(),ans:1,cols:2});r.title='양면 검증';await openWs(r)});
  const pop=await pp;await pop.waitForSelector('#pb-print');
  const logos=await pop.evaluate(()=>[...document.getElementById('paper').shadowRoot.querySelectorAll('.pg.wblank')].map(p=>{const l=p.querySelector('.bklg');const r=l&&l.getBoundingClientRect();return l?{shown:getComputedStyle(l).display!=='none',w:r.width,h:r.height}:null}));
  assert.ok(logos.length>0,'duplex adds blank pages');
  for(const l of logos){assert.ok(l&&l.shown&&l.w>10&&l.h>10,'logo visible on duplex blank page: '+JSON.stringify(l))}
  await page.context().close()}
 // 2) 교재: 만들 때 해설 없음(ans 2) → 인쇄 창에서 답안지 · 해설 켜기, 문제지 끄기 (태블릿 포함)
 for(const tablet of [false,true]){const page=await app(browser,{width:tablet?1024:1440,tablet});await page.evaluate(()=>localStorage.setItem('omr_duplex','0'));const pp=page.waitForEvent('popup');
  await page.evaluate(async()=>{await setSubject('me');await bkLoad();await bkInit();await conceptLoad();const d={kind:'free',name:'해설 없이 만든 교재',parts:[{k:'m',cap:3,lv:15}],subs:[0],ans:2,writing:{left:0,right:0,concept:false},dz:{back:0}};window._id=bkxId('me',d);bkxStore([...bkxAll(),{id:_id,subj:'me',kind:'free',name:d.name,printEngine:'html'}]);bkPrint(_id,0)});
  const pop=await pp;await pop.waitForSelector('#psq',{timeout:60000});const flip=async(sel,want)=>{for(let k=0;k<4;k++){await pop.click(sel);try{await pop.waitForSelector(want,{timeout:k<3?5000:60000});await wired();return}catch(e){if(k===3)throw e}}};const wired=()=>pop.waitForFunction(()=>['psq','psa','psx'].every(i=>document.getElementById(i)&&document.getElementById(i).onclick),null,{timeout:60000});await wired();
  const state=()=>pop.evaluate(()=>({q:document.getElementById('psq').classList.contains('on'),a:document.getElementById('psa').classList.contains('on'),x:document.getElementById('psx').classList.contains('on'),pages:document.querySelectorAll('.bkdoc>.bp').length,key:document.querySelectorAll('.bkdoc .kg').length,expl:document.querySelectorAll('.bkdoc .u.x').length,qs:document.querySelectorAll('.bkdoc .u.q').length,label:document.querySelector('#pb-print .lb').textContent}));
  let s=await state();assert.deepEqual([s.q,s.a,s.x,s.key,s.expl],[true,false,false,0,0],'starts with questions only');assert.ok(s.qs>0);
  if(tablet)assert.equal(s.label,'A4 PDF 저장','tablet saves an A4 PDF from the print window');
  await flip('#psa','#psa.on');s=await state();assert.ok(s.key>0&&s.expl>0,'answers with explanations appear although the book was made without them');
  await flip('#psx','#psx:not(.on)');s=await state();assert.ok(s.key>0&&s.expl===0,'answer key only');
  await flip('#psq','#psq:not(.on)');s=await state();assert.ok(s.key>0&&s.qs===0,'answer sheet only');
  await flip('#psa','#psa:not(.on)');s=await state();assert.ok(s.q&&!s.a&&s.qs>0,'cannot turn both off');
  await page.context().close()}
 console.log('PASS print: duplex blank-page logo visible; book print window toggles question/answer/explanation sheets (desktop and tablet)');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
