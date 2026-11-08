/* 승인된 학습지 디자인 19종: 2단, 머리글이 쪽 밖으로 나가지 않음, 제목 한 줄, 정보 줄과 QR이 겹치지 않음, 머리 숫자 반영 */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const b=await chromium.launch(browserOptions());try{const p=await b.newPage({viewport:{width:1000,height:1300}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');
 await p.waitForFunction(()=>typeof openWs==='function'&&typeof SV_LIST!=='undefined');await p.waitForTimeout(1200);
 const bad=await p.evaluate(async()=>{const codes=DATA.filter(q=>q.set!=='essay').slice(0,8).map(q=>q.code);await ensureCodes(codes);const out=[];
  assert0=(c,m)=>{if(!c)out.push(m)};
  assert0(SV_LIST.length===19,'19종이 아님: '+SV_LIST.length);
  for(const d of SV_LIST){document.body.innerHTML='<div id="pv"></div>';
   await openWs({id:'12345678',t:Date.now(),title:'반응 엔탈피와 열화학 반응식 확인 학습지 — 아주 긴 제목이 들어가도 한 줄',subt:'Ⅲ-A 반응 엔탈피',academy:'솔비 학원',style:d.k,color:'blue',font:STYLE_FONT[d.k],tags:{},cols:2,per:'auto',ans:1,qr:1,hdr:'qr',bno:'27',codes,cover:{}},document.getElementById('pv'));
   const R=document.getElementById('pv').shadowRoot,pg=R.querySelector('.pg'),ph=R.querySelector('.ph1'),pr=pg.getBoundingClientRect();
   assert0(pg.querySelectorAll('.col').length===2,d.k+' 2단 아님');
   ph.querySelectorAll('*').forEach(el=>{const r=el.getBoundingClientRect();if(r.width&&(r.right>pr.right+.5||r.left<pr.left-.5))out.push(d.k+' 쪽 밖: '+el.className)});
   const tt=ph.querySelector('.tt');if(tt){const rg=document.createRange();rg.selectNodeContents(tt);const tops=new Set([...rg.getClientRects()].filter(x=>x.width>1).map(x=>Math.round(x.top)));assert0(tops.size<=1,d.k+' 제목 두 줄');assert0(tt.scrollWidth<=tt.clientWidth+1,d.k+' 제목 잘림')}
   const inf=ph.querySelector('.inf'),qr=ph.querySelector('.qrh');if(inf&&qr&&getComputedStyle(qr).display!=='none'){const a=inf.getBoundingClientRect(),c=qr.getBoundingClientRect();let ov=false;inf.querySelectorAll(':scope>span').forEach(s=>{const r=s.getBoundingClientRect();if(r.width&&r.right>c.left+1&&r.left<c.right-1&&r.bottom>c.top+1&&r.top<c.bottom-1)ov=true});assert0(!ov,d.k+' 정보 줄과 QR 겹침')}
   if(d.head==='pub')assert0((ph.querySelector('.bno')||{}).textContent==='27',d.k+' 머리 숫자 미반영');
  }return out});
 assert.deepEqual(errs,[]);assert.deepEqual(bad,[]);console.log('PASS 승인 학습지 디자인 19종 (2단 · 머리글 · 제목 한 줄 · QR 겹침 · 머리 숫자)');
}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
