/* 전범위 모의고사에서 긴 지문이 열 밖으로 잘리지 않고, 학습지 · 풀이 화면의 지문 · 보기는 모두 상자 안에 있다 */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const b=await chromium.launch(browserOptions());try{const p=await b.newPage({viewport:{width:1300,height:950}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');await p.waitForFunction(()=>typeof bkLoad==='function');await p.waitForTimeout(1500);
 const bad=await p.evaluate(async()=>{const out=[];
  for(const subj of ['hl','me']){await setSubject(subj);await bkLoad();await bkInit();await conceptLoad();
   for(const rd of [1,2,3]){const plan=bkPlanFull('t',{name:'전범위 모의고사',count:20,lv:15,subs:[]},rd);const host=document.createElement('div');document.body.appendChild(host);
    plan.pages.forEach((pg,i)=>{if(pg.k!=='mq')return;const R=bkShadow(host,'<div class="bkdoc">'+bkPageHtml(plan,i)+'</div>');
     R.querySelectorAll('.col').forEach(c=>{const cb=c.getBoundingClientRect();[...c.children].forEach(u=>{if(u.getBoundingClientRect().bottom>cb.bottom+1)out.push(subj+' '+rd+'회 '+i+'쪽 잘림 '+(u.dataset.c||u.className))})});
     R.querySelectorAll('.psgu .psg').forEach(e=>{const cs=getComputedStyle(e);if(parseFloat(cs.borderLeftWidth)<.3&&!e.closest('.hdu'))out.push(subj+' '+rd+'회 지문 상자 없음')})});
    host.remove()}}
  await setSubject('hl');const L=[];for(const t of Object.keys(BIDX)){if(L.length>=60)break;try{const d=await (await fetch('hl/'+t+'.json')).json();(Array.isArray(d)?d:d.qs||[]).forEach(q=>{if(L.length<60&&/class="psg|class="bogi/.test(q.q||''))L.push(q)})}catch(e){}}
  L.forEach(q=>byCode[q.code]=q);ok=el=>{const cs=getComputedStyle(el);return parseFloat(cs.borderTopWidth)>=.3&&parseFloat(cs.borderLeftWidth)>=.3};
  document.body.innerHTML='<div id="pv"></div>';await openWs({id:'12345678',t:Date.now(),title:'t',style:'w-simple',color:'blue',tags:{},cols:2,ans:0,qr:0,codes:L.map(q=>q.code),cover:{}},document.getElementById('pv'));
  document.getElementById('pv').shadowRoot.querySelectorAll('.wq .psg,.wq .bogi').forEach(e=>{if(!ok(e))out.push('학습지 상자 없음 '+e.className)});
  for(const q of L){const sc=document.createElement('div');document.body.appendChild(sc);mount(sc,q.q);sc.shadowRoot.querySelectorAll('.psg,.bogi').forEach(e=>{if(!ok(e))out.push('화면 상자 없음 '+q.code+' '+e.className)});sc.remove()}
  return [...new Set(out)]});
 assert.deepEqual(errs,[]);assert.deepEqual(bad,[]);console.log('PASS 전범위 모의고사 지문 안 잘림(국어·과학 1~3회), 학습지·화면 지문·보기 상자');
}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
