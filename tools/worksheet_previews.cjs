/* 학습지 디자인(DZ_LIST)을 실제 엔진으로 그려 첫 쪽 캡처를 만든다(국어 · 과학). 디자인을 고치거나 새 시안을 낼 때 확인용.
   사용: python3 -m http.server 8803 &  node tools/worksheet_previews.cjs [디자인키] [출력폴더]  (기본 출력: /tmp/solvi-ws-previews) */
const path=require('path'),fs=require('fs');
const {chromium,browserOptions}=require('../tests/runtime.cjs');
const BASE=process.env.BASE||'http://127.0.0.1:8803',OUT=process.argv[3]||'/tmp/solvi-ws-previews';fs.mkdirSync(OUT,{recursive:true});
const ONLY=process.argv[2];
(async()=>{const b=await chromium.launch(browserOptions());const p=await b.newPage({viewport:{width:1000,height:1300}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto(BASE+'/index.html?app=1');await p.waitForFunction(()=>typeof openWs==='function');await p.waitForTimeout(1500);
 const ids=await p.evaluate(()=>DZ_LIST.map(d=>d.k));
 const sets=await p.evaluate(async()=>{const out={};
  await setSubject('me');out.me=DATA.filter(q=>q.set!=='essay'&&!isMulti(q)).slice(0,10).map(q=>q.code);
  await setSubject('hl');const L=[];for(const f of ['hl001','hl002','hl003','hl004','hl005']){const d=await (await fetch('hl/'+f+'.json')).json();(Array.isArray(d)?d:d.qs).forEach(q=>L.push(q))}
  const pr=L.filter(q=>/<div class="bogi"><p>/.test(q.q)).slice(0,3),lt=L.filter(q=>/class="bt"/.test(q.q)).slice(0,4),pl=L.filter(q=>!/bogi/.test(q.q)).slice(0,3);
  const all=[pr[0],lt[0],pl[0],lt[1],pr[1],lt[2],pl[1],pr[2],lt[3],pl[2]].filter(Boolean);all.forEach(q=>{byCode[q.code]=q});out.hl=all.map(q=>q.code);return out});
 const report=[];
 for(const k of ids){if(ONLY&&k!==ONLY)continue;
  for(const [subj,tag,title,subt] of [['me','sci','반응 엔탈피와 열화학 반응식','Ⅲ-A 반응 엔탈피 · 확인 문제'],['hl','kor','화법과 언어 · 발표와 문법','2학기 중간고사 대비 3회']]){
   const r=await p.evaluate(async([k,subj,codes,title,subt])=>{if(SUBJ!==subj)await setSubject(subj);await ensureCodes(codes);
    document.body.innerHTML='<div id="pv" style="width:210mm"></div>';
    await openWs({id:'12345678',t:new Date('2026-11-09').getTime(),title,subt,academy:'솔비 학원',name:'',style:k,color:'blue',font:STYLE_FONT[k],tags:{},cols:2,per:'auto',ans:1,qr:1,hdr:'qr',codes,cover:{}},document.getElementById('pv'));
    await new Promise(r=>setTimeout(r,1200));
    const R=document.getElementById('pv').shadowRoot,pg=R.querySelector('.pg'),ph=R.querySelector('.ph1'),pr=pg.getBoundingClientRect(),o=[];
    ph.querySelectorAll('*').forEach(el=>{const x=el.getBoundingClientRect();if(x.width&&(x.right>pr.right-14||x.left<pr.left+14))o.push('여백 밖 '+el.className)});
    const tt=ph.querySelector('.tt');if(tt&&tt.scrollWidth>tt.clientWidth+1)o.push('제목 넘침');
    const inf=ph.querySelector('.inf'),qr=ph.querySelector('.qrh');if(inf&&qr&&getComputedStyle(qr).display!=='none'){const c=qr.getBoundingClientRect();inf.querySelectorAll(':scope>span').forEach(s=>{const x=s.getBoundingClientRect();if(x.width&&x.right>c.left+1&&x.left<c.right-1&&x.bottom>c.top+1&&x.top<c.bottom-1)o.push('QR 겹침')})}
    return {o,n:R.querySelectorAll('.pg').length}},[k,subj,sets[subj],title,subt]);
   report.push(k+' '+tag+' '+r.n+'쪽 '+r.o.join(','));
   const pgs=p.locator('#pv').locator('css=.pg');
   for(let i=0;i<Math.min(2,r.n);i++){await p.evaluate(i=>{const R=document.getElementById('pv').shadowRoot;R.querySelectorAll('.pg').forEach((x,j)=>x.style.display=j===i?'':'none')},i);await p.locator('#pv').screenshot({path:path.join(OUT,`${k}-${tag}-${i+1}.png`)})}
  }}
 console.log(report.join('\n'));console.log(errs);await b.close()})();
