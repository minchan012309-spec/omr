const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.addInitScript(()=>{localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}}));const f=window.fetch.bind(window);window.fetch=(u,o)=>String(typeof u==='string'?u:u.url).includes('supabase.co')?Promise.resolve(new Response('[]',{headers:{'Content-Type':'application/json'}})):f(u,o)});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof openWs==='function'&&Object.keys(BIDX).length&&teacher());
 const result=await page.evaluate(async()=>{
  await setSubject('hl');await ensureTags(['hl035']);
  const q=byCode['G-hl035-0035'];if(!q)throw Error('Missing real question fixture');
  const host=document.createElement('div');document.body.appendChild(host);
  const rec={id:'test-header',t:Date.now(),codes:[q.code,...DATA.filter(x=>x.code!==q.code&&x.set==='bank').slice(0,2).map(x=>x.code)],title:'평가원 해설 확인',style:'w-evaluation',font:'shin',liveDesign:1,ans:1,cols:2,per:2,qr:1,tags:{code:1}};
  wsPopStart=()=>null;await openWs(rec);await document.fonts.ready;
  const root=document.querySelector('#wsPaper').shadowRoot,s=root.querySelector('.pg[data-solvi-kind="answers"] .sb.wq'),h=root.querySelector('.ph2.ref2'),sub=h.querySelector('.ref-running-subject'),a=h.getBoundingClientRect(),b=sub.getBoundingClientRect();
  return {oldHeads:s.querySelectorAll('.sol .sh').length,answers:s.querySelectorAll('.ws-answer').length,numbers:[...s.querySelectorAll('.sol p.st')].slice(0,5).map(p=>p.textContent.trim()[0]),font:getComputedStyle(sub).fontFamily,delta:Math.abs((a.left+a.right-b.left-b.right)/2)};
 });
 assert.equal(result.oldHeads,0,'original answer heading must not duplicate worksheet heading');assert.equal(result.answers,1);assert.deepEqual(result.numbers,['①','②','③','④','⑤'],'explanations are labeled with current choice numbers and sorted into choice order');assert.match(result.font,/SolviKoPub/);assert.ok(result.delta<1,JSON.stringify(result));
 console.log('PASS single answer heading, real shuffled choice labels, KoPub and centered continuation header');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
