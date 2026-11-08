/* 학습지 디자인 14종(기본 + 승인 13종): 2단, 머리글이 쪽 안, 아주 긴 제목도 한 줄, 정보 줄·QR 겹침 없음, 문항 번호는 숫자만,
   수능형 영역·교시 직접 입력, 예전 디자인 키는 새 디자인으로 연결 */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const b=await chromium.launch(browserOptions());try{const p=await b.newPage({viewport:{width:1000,height:1300}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');
 await p.waitForFunction(()=>typeof openWs==='function'&&typeof DZ_LIST!=='undefined');await p.waitForTimeout(1200);
 const bad=await p.evaluate(async()=>{const out=[],ok=(c,m)=>{if(!c)out.push(m)};
  ok(JSON.stringify(DZ_LIST.map(d=>d.k))===JSON.stringify(['w-simple','w-kice','w-school','w-school2','w-mock','w-unit','w-book','w-modern','w-drill','w-text','w-edit','w-note','w-academy','w-gray']),'디자인 목록: '+DZ_LIST.map(d=>d.k));
  ok(Object.keys(STYLES).length===14,'선택 목록 '+Object.keys(STYLES).length+'개');
  ok(WDEF.style==='w-simple','기본 디자인이 '+WDEF.style);
  ['kice','frame','naesin','sv-x04','basic','nae2','mock'].forEach(k=>ok(STYLES[styNorm(k)]&&STYLE_CSS[k],'예전 키 '+k+' 연결 안 됨'));
  const codes=DATA.filter(q=>q.set!=='essay').slice(0,8).map(q=>q.code);await ensureCodes(codes);
  for(const d of DZ_LIST){document.body.innerHTML='<div id="pv"></div>';
   await openWs({id:'12345678',t:Date.now(),title:'반응 엔탈피와 열화학 반응식 확인 학습지 — 아주 긴 제목이 들어가도 한 줄',subt:'Ⅲ-A 반응 엔탈피',academy:'솔비 학원',style:d.k,color:'blue',font:STYLE_FONT[d.k],tags:{},cols:2,per:'auto',ans:1,qr:1,hdr:'qr',karea:'사회탐구 영역',kper:'3',codes,cover:{}},document.getElementById('pv'));
   const R=document.getElementById('pv').shadowRoot,pg=R.querySelector('.pg'),ph=R.querySelector('.ph1'),pr=pg.getBoundingClientRect();
   ok(pg.querySelectorAll('.col').length===2,d.k+' 2단 아님');
   ph.querySelectorAll('*').forEach(el=>{const r=el.getBoundingClientRect();if(r.width&&(r.right>pr.right+.5||r.left<pr.left-.5))out.push(d.k+' 쪽 밖: '+el.className)});
   ph.querySelectorAll('.tt,.qrh .no').forEach(t=>{const rg=document.createRange();rg.selectNodeContents(t);const tops=new Set([...rg.getClientRects()].filter(x=>x.width>1).map(x=>Math.round(x.top)));ok(tops.size<=1,d.k+' 두 줄: '+t.className);ok(t.scrollWidth<=t.clientWidth+1,d.k+' 넘침: '+t.className)});
   const inf=ph.querySelector('.inf'),qr=ph.querySelector('.qrh');if(inf&&qr){const c=qr.getBoundingClientRect();inf.querySelectorAll(':scope>span').forEach(s=>{const r=s.getBoundingClientRect();if(r.width&&r.right>c.left+1&&r.left<c.right-1&&r.bottom>c.top+1&&r.top<c.bottom-1)out.push(d.k+' 정보 줄과 QR 겹침')})}
   const qn=R.querySelector('.q .qn'),cs=getComputedStyle(qn);ok(cs.backgroundColor==='rgba(0, 0, 0, 0)'&&parseFloat(cs.borderBottomWidth)===0&&parseFloat(cs.borderTopWidth)===0,d.k+' 문항 번호 장식');
   if(d.head==='kice'){ok(/사회탐구 영역/.test(ph.querySelector('.kar').textContent),d.k+' 영역 입력 미반영');ok(/제 3 교시/.test(ph.querySelector('.kpill').textContent),d.k+' 교시 입력 미반영')}
  }return out});
 assert.deepEqual(errs,[]);assert.deepEqual(bad,[]);console.log('PASS 학습지 디자인 14종 (2단 · 한 줄 · QR · 숫자 번호 · 수능형 영역·교시 · 예전 키 연결)');
}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
