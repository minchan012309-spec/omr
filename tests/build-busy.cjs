/* 학습지 만들기 「다음 · 문항 확인」: 누르면 바로 버튼이 잠기고 「문항 구성 중…」, 진행 표시가 출제 창 위에 보이며, 끝나면 다음 단계로. 여러 번 눌러도 한 번만. */
const assert=require('node:assert/strict');const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>{localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}}));const fetch=window.fetch.bind(window);window.fetch=(input,init)=>{const u=String(typeof input==='string'?input:input.url);if(u.includes('supabase.co'))return Promise.resolve(new Response('[]',{status:200,headers:{'Content-Type':'application/json'}}));if(/\/bank\/hw[a-z0-9]+\.json/.test(u))return new Promise(r=>setTimeout(r,700)).then(()=>fetch(input,init));return fetch(input,init)}});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof bkLoad==='function'&&Object.keys(BIDX).length&&teacher());
 await page.evaluate(async()=>{await setSubject('me');STU.push({id:'s9',name:'예시'});W.hw=1;W.mode='per';const rows=typeRows().filter(o=>o.hwn>0).slice(5,9);W.sel=new Map(rows.map(o=>[o.k,4]));tab='build';buildView();window.__calls=0;const mk=window.makeNow;window.makeNow=function(){window.__calls++;return mk.apply(this,arguments)}});
 const btn=page.locator('button[onclick="bdGo()"]').first();await btn.click();
 const s=await page.evaluate(()=>{const b=document.querySelector('button[onclick="bdGo()"]'),o=document.getElementById('busy'),r=o&&o.getBoundingClientRect();const top=r&&document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return {txt:b.textContent,dis:b.disabled,busy:!!o&&getComputedStyle(o).display!=='none',onTop:!!top&&!!o&&o.contains(top),label:(document.getElementById('busyt')||{}).textContent}});
 await btn.click({force:true}).catch(()=>{});await page.evaluate(()=>bdGo());
 assert.equal(s.txt,'문항 구성 중…','button shows progress');assert.equal(s.dis,true,'button locked');assert.equal(s.busy,true,'busy overlay shown');assert.equal(s.onTop,true,'busy overlay above the build window');assert.match(s.label,/문항을 구성하는 중/);
 await page.waitForFunction(()=>!document.getElementById('busy')||getComputedStyle(document.getElementById('busy')).display==='none',null,{timeout:60000});
 assert.equal(await page.evaluate(()=>window.__calls),1,'only one build for repeated clicks');
 assert.equal(await page.evaluate(()=>tab==='review'&&RV&&RV.codes.length>0),true,'moved on to 문항 확인 with picked questions');
 assert.deepEqual(errors,[]);
 console.log('PASS build busy: 다음 · 문항 확인 locks the button, shows 「문항을 구성하는 중…」 above the build window, builds once');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
