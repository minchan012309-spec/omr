const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.route(/supabase\.co/,r=>r.fulfill({json:[]}));
 await page.addInitScript(()=>localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}})));
 await page.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');
 await page.waitForFunction(()=>typeof bkLoad==='function'&&Object.keys(BIDX).length&&teacher());
 await page.evaluate(async()=>{await bkLoad();await bkInit();await conceptLoad()});
 for(const subject of ['me','cm','ph','hl','aim']){
  const result=await page.evaluate(async subject=>{
   await setSubject(subject);await conceptLoad();
   const d={kind:'free',parts:[{k:'c',lv:15},{k:'m',cap:4,lv:15}],subs:[0],ans:0,name:'필기 여백 검증',dz:{back:0}};
   const plan=async writing=>{d.writing=bkWriting(writing);const p=await bkSettle(()=>bkWithWriting(d.writing,()=>bkPlanFree('preview',d)));p.id='preview';p.writing=d.writing;p.pages.forEach((x,i)=>x.n=i+1);return p};
   const a=await plan({}),b=await plan({left:1,right:1,concept:false});
   const round=bkfParse(bkfPayload(d));
   const host=document.createElement('div');document.body.appendChild(host);
   const root=bkShadow(host,'<div class="bkdoc">'+b.pages.map((p,i)=>bkPageHtml(b,i)).join('')+'</div>');
   const cols=[...root.querySelectorAll('.col,.cnbody')],over=cols.filter(x=>x.scrollHeight>x.clientHeight+3).map(x=>({class:x.className,scroll:x.scrollHeight,height:x.clientHeight}));
   const widths=cols.map(x=>x.getBoundingClientRect().width/BK_MM);
   const first=root.querySelector('.cnbody');const conceptWidth=first&&first.getBoundingClientRect().width/BK_MM;
   const out={subject,baseNotes:a.pages.filter(x=>x.k==='nt').length,notes:b.pages.filter(x=>x.k==='nt').length,sideNotes:root.querySelectorAll('.cnnote').length,margins:root.querySelectorAll('.writing-margin').length,widths,conceptWidth,over,round:round.writing,default:bkWritingOf('not-a-book'),html:bkDocHtml(b,1).includes('writing-margin left')};if(subject==='hl')host.id='writing-proof';else host.remove();return out;
  },subject);
  if(subject==='hl'){await page.locator('#writing-proof .bp.cnp').first().screenshot({path:'/tmp/solvi-book-writing-concept.png'});await page.locator('#writing-proof .bp').filter({has:page.locator('.cols')}).first().screenshot({path:'/tmp/solvi-book-writing-questions.png'});await page.evaluate(()=>document.getElementById('writing-proof').remove())}
  assert.deepEqual(result.round,{left:22,right:22,concept:false});
  assert.deepEqual(result.default,{left:0,right:0,concept:true});
  assert.ok(result.margins>0&&result.html,JSON.stringify(result));
  assert.equal(result.notes,0);
  if(subject==='hl'){assert.equal(result.baseNotes,10);assert.equal(result.sideNotes,0);assert.ok(Math.abs(result.conceptWidth-142)<.1)}
  else assert.ok(Math.abs(result.conceptWidth-88)<.1);
  assert.deepEqual(result.over,[],JSON.stringify(result));
  assert.ok(result.widths.every(w=>w<143));
  console.log('PASS',subject,'real-width pagination and HTML/PDF source');
 }
 const overflow=await page.evaluate(async()=>{await setSubject('hl');const p=await bkPlan('hl-t~w3'),host=document.createElement('div');document.body.appendChild(host);const root=bkShadow(host,'<div class="bkdoc">'+p.pages.map((_,i)=>bkPageHtml(p,i)).join('')+'</div>');const errors=[...root.querySelectorAll('.col,.cnbody')].filter(x=>x.scrollHeight>x.clientHeight+3||x.scrollWidth>x.clientWidth+3).map(x=>({h:x.scrollHeight,ch:x.clientHeight,w:x.scrollWidth,cw:x.clientWidth,first:x.textContent.slice(0,30)}));host.remove();return errors});assert.deepEqual(overflow,[]);
 const frozen=await page.evaluate(async()=>{await setSubject('hl');bkWritingSet('hl-c','left',true);const id=bkPid('hl-c');bkWritingSet('hl-c','left',false);return {id,writing:bkWritingOf(id),bare:bkBare(id),parts:bkParts(id).kind,pid:bkPid('hl-c')}});
 assert.match(frozen.id,/~w1$/);assert.deepEqual(frozen.writing,{left:22,right:0,concept:true});assert.equal(frozen.bare,'hl-c');assert.equal(frozen.parts,'c');assert.match(frozen.pid,/~w0$/);
 for(const width of [1440,820,390]){
  await page.setViewportSize({width,height:1000});
  await page.evaluate(async()=>{await setSubject('hl');await conceptLoad();tab='books';bkNew('free');BKV.step=3;bkShow()});
  await page.locator('#bfwl').check();await page.locator('#bfwr').check();await page.locator('#bfwc').uncheck();
  await page.waitForTimeout(1500);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  assert.deepEqual(await page.evaluate(()=>BKV.d.writing),{left:22,right:22,concept:false});
  await page.screenshot({path:`/tmp/solvi-book-writing-${width}.png`});
 }
 console.log('PASS book writing controls at 1440/820/390');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
