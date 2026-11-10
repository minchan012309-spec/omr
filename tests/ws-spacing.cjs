/* 학습지 「문제 간격」이 쪽당 문항 수를 정한다: 기본 6 · 조금 넓게 5 · 넓게 4 · 아주 넓게 3 (첫 쪽, 짧은 문항 기준).
   「한 쪽 최대 문항」을 숫자로 고르면 그 숫자가 그대로 우선 */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const b=await chromium.launch(browserOptions());try{const p=await b.newPage({viewport:{width:1000,height:1300}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');await p.waitForFunction(()=>typeof openWs==='function');await p.waitForTimeout(1200);
 const r=await p.evaluate(async()=>{await setSubject('hl');const L=[];
  for(const f of ['hl042','hl036','hl037','hl043']){const d=await (await fetch('hl/'+f+'.json')).json();(Array.isArray(d)?d:d.qs||[]).forEach(q=>{if(!['ox','blank','essay'].includes(q.set)&&!/psg|bogi/.test(q.q)&&L.length<24)L.push(q)})}
  L.forEach(q=>byCode[q.code]=q);const cs=L.map(q=>q.code),out={};
  for(const [per,g,one] of [['auto',0],['auto',4],['auto',8],['auto',14],[2,0],['auto',0,1]]){document.body.innerHTML='<div id="pv"></div>';
   await openWs({id:'12345678',t:Date.now(),title:'t',style:'w-simple',color:'blue',tags:{},cols:one?1:2,per,gapmm:g,ans:0,qr:0,codes:cs,cover:{}},document.getElementById('pv'));
   const pg=document.getElementById('pv').shadowRoot.querySelector('.pg');out[per+'/'+g+(one?'/1단':'')]=[...pg.querySelectorAll('.col')].map(c=>c.querySelectorAll('.wq').length).join('+');
   const over=[...pg.querySelectorAll('.col')].some(c=>c.scrollHeight>c.clientHeight+1);if(over)out[per+'/'+g+(one?'/1단':'')]+=' 넘침'}
  return out});
 assert.deepEqual({a:r['auto/0'],b:r['auto/4'],c:r['auto/8'],d:r['auto/14'],e:r['2/0'],f:r['auto/0/1단']},{a:'3+3',b:'3+2',c:'2+2',d:'2+1',e:'1+1',f:'4+0'});
 assert.deepEqual(errs,[]);console.log('PASS 학습지 문제 간격: 기본 6 · 조금 넓게 5 · 넓게 4 · 아주 넓게 3문항, 숫자로 고르면 그대로');
}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
