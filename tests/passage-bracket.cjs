/* 국어 지문: 색칠 대신 오른쪽 긴 괄호 [A], 필기용 지문(psg sp)도 학습지·풀이 화면에서 상자 안에 있다 */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const b=await chromium.launch(browserOptions());try{const p=await b.newPage({viewport:{width:1000,height:1300}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto((process.env.BASE||'http://127.0.0.1:8765')+'/index.html?app=1');await p.waitForFunction(()=>typeof openWs==='function');await p.waitForTimeout(1200);
 const r=await p.evaluate(async()=>{await setSubject('hl');const out=[];const ok=(c,m)=>{if(!c)out.push(m)};
  const all=await (await fetch('hl/data.json')).json();const sp=all.filter(q=>/class="psg sp"/.test(q.q)).slice(0,40).map(q=>q.code);
  await ensureCodes(['H26-004','H26-007',...sp]);
  const q4=byCode['H26-004'].q;ok(!/class="rng"|class="rk"|class="re"/.test(q4),'색칠 표시가 남음');ok((q4.match(/data-bk="A"/g)||[]).length===1,'[A] 이름표가 하나가 아님');ok(/bk-s/.test(q4)&&/bk-e/.test(q4)&&/bk-m/.test(q4),'괄호 시작·중간·끝 조각 없음');
  const boxed=e=>{const c=getComputedStyle(e);return parseFloat(c.borderTopWidth)>=.3&&parseFloat(c.borderLeftWidth)>=.3};
  // 학습지: 필기용 지문 문항을 하나씩 그려 지문 상자를 확인(미리보기는 첫 쪽만 그리므로)
  let n=0;for(const c of ['H26-004',...sp.slice(0,12)]){document.body.innerHTML='<div id="pv"></div>';await openWs({id:'12345678',t:Date.now(),title:'t',style:'w-simple',color:'blue',tags:{},cols:1,per:'auto',ans:0,qr:0,codes:[c],cover:{}},document.getElementById('pv'));
   document.getElementById('pv').shadowRoot.querySelectorAll('.wq .psg').forEach(e=>{n++;if(!boxed(e))out.push('학습지 지문 상자 없음 '+c)})}
  ok(n>=8,'지문 검사 대상이 너무 적음 '+n);
  document.body.innerHTML='<div id="pv"></div>';await openWs({id:'12345678',t:Date.now(),title:'t',style:'w-simple',color:'blue',tags:{},cols:1,per:'auto',ans:0,qr:0,codes:['H26-004'],cover:{}},document.getElementById('pv'));const R=document.getElementById('pv').shadowRoot;
  const s=R.querySelector('.bk-s'),m=R.querySelector('.bk-m'),e=R.querySelector('.bk-e');
  ok(s&&getComputedStyle(s,'::after').borderTopWidth!=='0px'&&getComputedStyle(s,'::after').borderRightWidth!=='0px','괄호 윗변·오른쪽 선 안 그려짐');
  ok(m&&getComputedStyle(m,'::after').borderRightWidth!=='0px'&&getComputedStyle(m,'::after').borderTopWidth==='0px','괄호 중간 줄이 아님');
  ok(e&&getComputedStyle(e,'::after').borderBottomWidth!=='0px','괄호 아랫변 안 그려짐');
  const lab=R.querySelector('[data-bk]');ok(lab&&getComputedStyle(lab,'::before').content.includes('A'),'[A] 이름표 안 그려짐');
  // 풀이 화면
  for(const c of sp.slice(0,20)){const d=document.createElement('div');document.body.appendChild(d);mount(d,byCode[c].q);d.shadowRoot.querySelectorAll('.psg').forEach(x=>{if(!boxed(x))out.push('풀이 화면 지문 상자 없음 '+c)});d.remove()}
  return [...new Set(out)]});
 assert.deepEqual(errs,[]);assert.deepEqual(r,[]);console.log('PASS 지문 범위 [A] 긴 괄호 · 필기용 지문 상자(학습지 · 풀이 화면)');
}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
