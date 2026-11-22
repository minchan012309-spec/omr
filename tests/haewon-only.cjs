/* 물질과 에너지 「해원고 부교재」 옵션: 학습지 만들기 · 전범위 모의고사에서 켜면 부교재 원본(o) · 변형(v) · 유사(s)에서만 출제. 유형 카드에 (해원고 n). */
const assert=require('node:assert/strict');const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>{localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}}));const fetch=window.fetch.bind(window);window.fetch=(input,init)=>String(typeof input==='string'?input:input.url).includes('supabase.co')?Promise.resolve(new Response('[]',{status:200,headers:{'Content-Type':'application/json'}})):fetch(input,init)});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof bkLoad==='function'&&Object.keys(BIDX).length&&teacher());
 const r=await page.evaluate(async()=>{await setSubject('me');const rows=typeRows().filter(o=>o.hwn>0).slice(0,4);
  const hwOk=c=>{const q=byCode[c];return q&&['o','v','s'].includes(q.hw)};
  W.sel=new Map(rows.map(o=>[o.k,8]));W.mode='per';W.essay=0;W.hw=1;const on=await pickCodes();
  W.hw=0;let mixed=false;for(let k=0;k<4&&!mixed;k++){const off=await pickCodes();mixed=off.some(c=>!hwOk(c))}
  tab='build';W.hw=1;STU.push({id:'s9',name:'예시'});buildView();const card=document.querySelector('#btypes .tc .hwn')?.textContent||'',opt=!!document.querySelector('.hwopt input:checked');bwClose&&bwClose();
  MKF.hw=1;MKF.scope='all';MKF.essay=0;mkEns();const sc=subs.map(x=>x[0]),obj=mkObjN(),ps=mkPerSub(sc,obj);const mock=await mockPick(sc,obj,ps,new Set());
  MKF.hw=1;MKF.essay=2;mkEns();const pool=DATA.filter(q=>q.set==='essay'&&(q.hw==='o'||q.hw==='v')).length;
  return {types:rows.length,on:on.length,onAll:on.every(hwOk),mixed,card,opt,mock:mock.length,obj,mockAll:mock.every(q=>['o','v','s'].includes(q.hw)),pool}});
 assert.ok(r.types>=2,'types with 해원고 questions');assert.ok(r.on>0,'questions picked');assert.equal(r.onAll,true,'option on: only 해원고 (원본/변형/유사)');
 assert.equal(r.mixed,true,'option off: other questions (유사 등) can appear');
 assert.match(r.card,/^\(해원고 [\d,]+\)$/,'type card shows 해원고 count');assert.equal(r.opt,true,'option toggle shown and on');
 assert.ok(r.mock>0&&r.mock<=r.obj,'mock picked');assert.equal(r.mockAll,true,'mock with option: only 해원고');
 assert.deepEqual(errors,[]);
 console.log('PASS 해원고 부교재 옵션: 학습지 '+r.on+'문항 · 모의고사 '+r.mock+'문항 모두 해원고 부교재 문항, 끄면 다른 문항도 섞임, 유형 카드 '+r.card);
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
