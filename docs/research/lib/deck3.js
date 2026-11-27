/* Solvi 발표 자료 v3 — 다음 버튼 = 다음 장. 장마다 다른 전환 효과, 들어오면 자동 연출 */
(()=>{
'use strict';
const ORIGINAL='<!doctype html>\n'+document.documentElement.outerHTML;
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=n=>Number(n).toLocaleString('ko-KR');
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
const EZ='cubic-bezier(.22,1,.36,1)',EIO='cubic-bezier(.76,0,.24,1)',EXIT='cubic-bezier(.55,0,1,.45)';
const slides=$$('.slide'),stage=$('#stage'),vp=$('#viewport'),FXL=$('#fx');
let cur=0,K=1,busy=false,tok=0;
const isShow=()=>document.body.classList.contains('show');
let seed=7;const rnd=()=>(seed=(seed*1103515245+12345)&0x7fffffff)/0x7fffffff;
const wait=ms=>new Promise(r=>setTimeout(r,RM?0:ms));
const NS='http://www.w3.org/2000/svg';
const FX={rise:[{opacity:0,transform:'translateY(14px)'},{opacity:1,transform:'none'}],right:[{opacity:0,transform:'translateX(18px)'},{opacity:1,transform:'none'}]};
function fit(){const r=vp.getBoundingClientRect();const s=Math.min(r.width/1920,r.height/1080)*(isShow()?1:.97);K=s;stage.style.transform=`translate(-50%,-50%) scale(${s})`}
addEventListener('resize',fit);
const rel=el=>{const r=el.getBoundingClientRect(),q=stage.getBoundingClientRect();return {x:(r.left-q.left)/K,y:(r.top-q.top)/K,w:r.width/K,h:r.height/K}};
function ghostOf(el,r){const g=el.cloneNode(true);[g,...g.querySelectorAll('*')].forEach(x=>{x.removeAttribute&&(x.removeAttribute('id'),x.removeAttribute('contenteditable'))});Object.assign(g.style,{position:'absolute',left:r.x+'px',top:r.y+'px',width:r.w+'px',height:r.h+'px',margin:'0',zIndex:60,pointerEvents:'none',transformOrigin:'0 0',opacity:'1',transform:'none'});g.classList&&g.classList.add('ghost');stage.appendChild(g);return g}
const tf=(a,b)=>`translate(${a.x-b.x}px,${a.y-b.y}px) scale(${a.w/Math.max(b.w,1)},${a.h/Math.max(b.h,1)})`;
function morphPair(g,a,el,b,d){g.animate([{transform:'none',opacity:1},{transform:tf(b,a),opacity:0}],{duration:d,easing:EZ,fill:'forwards'}).onfinish=()=>g.remove();el.animate([{transform:tf(a,b),opacity:0,transformOrigin:'0 0'},{opacity:1,offset:.5},{transform:'none',opacity:1,transformOrigin:'0 0'}],{duration:d,easing:EZ})}
function morphBox(a,toEl,css,d){if(RM||!toEl)return;const b=rel(toEl);const g=document.createElement('div');g.className='ghost';Object.assign(g.style,{position:'absolute',left:a.x+'px',top:a.y+'px',width:a.w+'px',height:a.h+'px',zIndex:60,pointerEvents:'none',transformOrigin:'0 0',borderRadius:'6px'},css||{});stage.appendChild(g);morphPair(g,a,toEl,b,d||520)}

/* 로고: 어두운 바탕용(글자 흰색 · 밑줄 노랑) */
const logoW=(window.LOGO||'').replace('#0D387E','#ffffff');
$$('.logo').forEach(l=>l.innerHTML=window.LOGO||'');
const HOOK={};
// --- 8 라이브 시연 (리모컨으로 9단계)
const POOL=window.POOL||{};const TYPES=Object.keys(POOL);const CIR='①②③④⑤';
const stemH=t=>{let h=esc(t);const i=h.indexOf('? &lt;보기&gt;');if(i>=0){h=h.slice(0,i+1)+'<div class="bogi">'+h.slice(i+2).replace('&lt;보기&gt; ','').replace(/ (ㄴ|ㄷ|ㄹ)\. /g,'<br>$1. ')+'</div>'}return h};
const qrSvg=t=>{try{const q=qrcode(0,'M');q.addData(t);q.make();return q.createSvgTag(4,0)}catch(e){return ''}};
const DM={};const dm=$('#demo');
function dReset(){Object.assign(DM,{st:0,unit:'효소',sel:[],n:8,sheet:null,ans:[],seen:new Set(),rounds:[],ts:{},serial:48271150,pick:-1,g:null,prevSheet:null,hist:[]});seed=31}
const dTypes=()=>TYPES.filter(t=>POOL[t][0].u===DM.unit);
function dPaper(){const s=DM.sheet;if(!s)return `<div class="paper" style="display:grid;place-items:center;text-align:center;color:#b0bccb"><div><div class="big" style="font-size:44px;color:#d3dbe6;margin-bottom:10px">학습지 미리보기</div><p style="font-size:19px">단원 · 유형을 고르면 문제은행에서 출제됩니다</p></div></div>`;
 const url='https://solvi.p-e.kr/#ws='+s.no.replace('-','');
 return `<div class="paper" id="paper"><div class="ph"><div><small>Solvi · 세포와 물질대사 · ${esc(s.kind)}</small><h4>${esc(s.title)}</h4><small>학습지 번호 <b>${s.no}</b> · ${s.qs.length}문항 · 이름 ________</small></div><div class="qr">${qrSvg(url)}</div></div>
 <div class="pq">${s.qs.map((q,i)=>`<div class="q" id="pq${i}"><b>${i+1}.</b>${stemH(q.s)}<div class="o">${q.o.map((o,k)=>`<span>${CIR[k]} ${esc(o)}</span>`).join('')}</div><span class="cd">${q.c} · ${esc(q.t)} · ${q.lv}</span></div>`).join('')}</div>
 <div class="cam" id="cam"><div class="vf"><div class="qrbig">${qrSvg(url)}</div><div class="scanl" id="scanl"></div></div><div class="msg" id="camMsg">쪽 QR을 찾는 중…</div></div><div class="confetti" id="conf"></div></div>`}
function dSteps(){const L=['출제','인쇄','QR 인식','답 입력','채점','재출제'];const at=[0,1,1,2,3,4,4,5,4,5][DM.st]??0;return `<div class="steps">${L.map((l,i)=>`<span class="${i<at?'on':i===at?'on cur':''}">${i+1} ${l}</span>`).join('')}</div>`}
function dPanel(){let R='';const s=DM.sheet;
 if(DM.st===0){R=`<h3 style="font-size:28px;margin-bottom:10px">학습지 만들기</h3><div class="lab">단원</div><div class="chips" style="margin-bottom:14px">${[...new Set(TYPES.map(t=>POOL[t][0].u))].map(u=>`<span class="chip ${u===DM.unit?'on':''}">${esc(u)}</span>`).join('')}</div>
  <div class="lab">유형 (문제은행 유형 체계)</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">${dTypes().map(t=>`<span class="chip ${DM.sel.includes(t)?'on':''}" data-t="${esc(t)}"><span class="ck">${DM.sel.includes(t)?'✓':''}</span>${esc(t)}</span>`).join('')}</div>
  <div style="display:flex;gap:30px"><div><div class="lab">문항 수</div><div class="chips">${[6,8,10].map(n=>`<span class="chip ${n===DM.n?'on':''}">${n}문항</span>`).join('')}</div></div><div><div class="lab">난이도</div><div class="chips"><span class="chip on">섞어서</span><span class="chip">하 · 중</span><span class="chip">중 · 상</span></div></div><div><div class="lab">출제 순서</div><div class="chips"><span class="chip on">오답 → 쌍둥이 → 새 문제</span></div></div></div>`}
 else if(DM.st===1){const cnt={};s.qs.forEach(q=>cnt[q.t]=(cnt[q.t]||0)+1);R=`<h3 style="font-size:28px;margin-bottom:4px">${esc(s.kind)} 완성</h3><p style="font-size:19px;color:var(--ink2);margin-bottom:14px">번호 <b>${s.no}</b> · ${s.qs.length}문항 · 인쇄해서 종이로 풀었다고 가정</p>
  <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:14px">${Object.entries(cnt).map(([t,n])=>`<div class="wi"><span class="t">${esc(t)}</span><span class="tag">${n}문항 · 남은 ${POOL[t].filter(q=>!DM.seen.has(q.c)).length}</span></div>`).join('')}</div>
  <pre style="font-size:15px;padding:14px 16px">${'<span class="kw">INSERT INTO</span> worksheets (wid, title, meta)\n<span class="kw">VALUES</span> (<span class="st">\''+s.no.replace('-','')+'\'</span>, <span class="st">\''+esc(s.title)+'\'</span>,\n        <span class="st">\'{"codes": ['+s.qs.slice(0,3).map(q=>'"'+q.c+'"').join(', ')+', …]}\'</span>);'}</pre>`}
 else if(DM.st===2){R=`<h3 style="font-size:28px">QR 인식</h3><p style="font-size:19px;color:var(--ink2);margin-top:8px">학생 휴대폰 카메라가 쪽 QR을 읽어 학습지 ${s.no}를 엽니다.</p><div class="card" style="margin-top:14px;background:#f6f8fb;border:0"><span class="lab">호출되는 SQL 함수</span><pre style="font-size:15px;padding:12px 14px;margin-top:6px"><span class="kw">SELECT</span> <span class="fn">ws_get</span>(<span class="st">'${s.no.replace('-','')}'</span>);  <span class="cm">-- 문항 목록 · 제출 여부</span></pre></div>`}
 else if(DM.st===3){const done=DM.ans.filter(a=>a).length;R=`<h3 style="font-size:28px;margin-bottom:6px">OMR에 학생 답 입력 <small style="font-size:16px;color:var(--mut)">${done}/${s.qs.length}</small></h3><div class="omr" id="omr">${s.qs.map((q,i)=>`<div class="om" data-r="${i}"><span class="n">${i+1}</span>${[1,2,3,4,5].map(k=>`<span class="bub ${DM.ans[i]===k?'sel':''}" data-k="${k}">${k}</span>`).join('')}<span class="mk"></span></div>`).join('')}</div>`}
 else if(DM.st===4||DM.st===5){const g=s.g;const wrong=s.qs.map((q,i)=>({q,i,a:DM.ans[i]})).filter(x=>x.a!==x.q.a);const ts=Object.entries(DM.ts).filter(([t])=>s.qs.some(q=>q.t===t));
  R=`<div style="display:flex;gap:22px;align-items:center"><div class="ring"><svg width="190" height="190"><circle cx="95" cy="95" r="82" fill="none" stroke="#edf1f6" stroke-width="16"/><circle id="rg" cx="95" cy="95" r="82" fill="none" stroke="${g.p>=.8?'#17956a':g.p>=.5?'#2f7fd0':'#d8443b'}" stroke-width="16" stroke-linecap="round" stroke-dasharray="515" stroke-dashoffset="${515*(1-g.p)}"/></svg><div class="v"><div><b id="rv">${Math.round(g.p*100)}</b><small>점 · ${g.r}/${s.qs.length}</small></div></div></div>
  <div style="flex:1;display:flex;flex-direction:column;gap:6px"><div class="lab">틀린 문항 ${wrong.length}개</div>${wrong.slice(0,4).map(x=>`<div class="wi ${DM.pick===x.i?'pick':''}" data-i="${x.i}"><span><span class="c">${x.i+1}번 · ${x.q.c}</span><br><span class="t">${esc(x.q.t)}</span></span><span class="tag r">${x.a?CIR[x.a-1]:'—'} → ${CIR[x.q.a-1]}</span></div>`).join('')}</div></div>
  <div id="qv" style="margin-top:12px">${DM.pick>=0?dQv(DM.pick):''}</div>
  <div class="lab" style="margin-top:12px">유형별 누적 정답률 (attempts 집계)</div>${ts.map(([t,o])=>`<div style="display:grid;grid-template-columns:300px 1fr 56px;gap:10px;align-items:center;font-size:15px;margin-bottom:6px"><span>${esc(t)}</span><span style="height:14px;background:#edf1f6;border-radius:5px;overflow:hidden"><i style="display:block;height:100%;width:${o.r/o.n*100}%;background:${o.r/o.n<.5?'#d8443b':o.r/o.n<.75?'#e09c12':'#17956a'};border-radius:5px"></i></span><b style="text-align:right">${Math.round(o.r/o.n*100)}%</b></div>`).join('')}`}
 else if(DM.st===6){const h=DM.hist;const types=[...new Set(h.flatMap(r=>Object.keys(r.rt)))];
  R=`<h3 style="font-size:28px;margin-bottom:4px">회차 비교 — 오답 학습지의 효과</h3><p style="font-size:16px;color:var(--mut);margin-bottom:14px">시연용 예시 학생 답 기준 · 실제 학습 효과 검증은 제언으로 남김</p>
  <div style="display:grid;grid-template-columns:330px 1fr;gap:28px;flex:1;min-height:0">
   <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:end;border-bottom:2px solid var(--navy);padding-bottom:0" id="cmpBars">${h.map((r,i)=>`<div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:8px;height:100%"><b class="big" style="font-size:46px;color:${i?'#17956a':'#d8443b'}">${Math.round(r.p*100)}</b><i class="cb" style="display:block;width:100%;height:${Math.max(10,r.p*100)*3.4}px;background:${i?'#17956a':'#e7a19c'};border-radius:10px 10px 0 0;transform-origin:bottom"></i></div>`).join('')}</div>
   <div style="display:flex;flex-direction:column;gap:0"><div class="lab">유형별 정답률 (1회차 → 2회차)</div>${types.map(t=>{const a=h[0].rt[t],b=h[1]&&h[1].rt[t];const pa=a?Math.round(a.r/a.n*100):null,pb=b?Math.round(b.r/b.n*100):null;return `<div style="display:grid;grid-template-columns:1fr 70px 30px 70px;gap:8px;align-items:center;padding:12px 0;border-bottom:1px solid var(--line);font-size:17px"><span style="font-weight:700">${esc(t)}</span><b style="text-align:right;color:#d8443b">${pa==null?'—':pa+'%'}</b><span style="text-align:center;color:var(--mut)">→</span><b style="color:#17956a">${pb==null?'—':pb+'%'}</b></div>`}).join('')}
    <div class="card" style="margin-top:auto;background:#f6f8fb;border:0;padding:14px 16px"><span class="lab">이 시연에서 DB에 쌓인 것</span><p style="font-size:16.5px;line-height:1.55">worksheets 2행 · attempts 2행(문항 결과 ${h.reduce((a,r)=>a+r.n,0)}개) → 다음 출제는 남은 약점 유형 우선</p></div></div>
  </div>
  <div style="display:grid;grid-template-columns:330px 1fr;gap:28px;margin-top:8px"><div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;text-align:center;font-weight:800;font-size:16px"><span>1회차 · 유형 학습지</span><span>2회차 · 오답 학습지</span></div><span></span></div>`}
 return `<div class="panel">${dSteps()}${R}</div>`}
function dQv(i){const q=DM.sheet.qs[i],a=DM.ans[i];return `<div class="qv"><b>${i+1}번</b> <span class="src">${q.c} · ${esc(q.u)} · 난이도 ${q.lv}</span><br>${stemH(q.s)}<ol>${q.o.map((o,k)=>`<li class="${k+1===q.a?'a':k+1===a?'m':''}">${esc(o)}</li>`).join('')}</ol><div style="margin-top:4px;color:var(--ink2)"><b>해설</b> ${esc(q.e).slice(0,170)}</div></div>`}
function dRender(){dm.innerHTML=dPaper()+dPanel()}
function dPick(kind,qs,title){DM.serial+=7311;const n=String(DM.serial);DM.sheet={kind,title,qs,no:n.slice(0,4)+'-'+n.slice(4,8)};DM.ans=new Array(qs.length).fill(0);qs.forEach(q=>DM.seen.add(q.c));DM.pick=-1}
function dSwap(fn,inst){const op=$('.paper',dm);const g=(!inst&&!RM&&op)?ghostOf(op,rel(op)):null;fn();const np=$('.paper',dm);if(g){g.animate([{opacity:1,transform:'none'},{opacity:0,transform:'translateX(-110px) rotate(-5deg)'}],{duration:480,easing:EZ,fill:'forwards'}).onfinish=()=>g.remove();np.animate([{opacity:0,transform:'translate(120px,30px) rotate(4deg)'},{opacity:1,transform:'none'}],{duration:620,easing:EZ})}}
function dMake(){const pools=DM.sel.map(t=>POOL[t].filter(q=>!DM.seen.has(q.c)));const out=[];for(let k=0;out.length<DM.n&&k<12;k++)pools.forEach(p=>{if(out.length<DM.n&&p[k])out.push(p[k])});dPick('유형 학습지',out,'효소 유형 연습')}
function dRetry(){const s=DM.sheet;const wrong=s.qs.filter((q,i)=>DM.ans[i]!==q.a);const out=[];wrong.forEach(w=>{out.push(...POOL[w.t].filter(q=>!DM.seen.has(q.c)&&!out.includes(q)).slice(0,2))});dPick('오답 학습지 · 2회차',out.slice(0,8),`틀린 유형 ${new Set(wrong.map(w=>w.t)).size}개 · 쌍둥이 문항`)}
function dAnswers(round){const s=DM.sheet;const weak=DM.sel[0];return s.qs.map(q=>{let p=q.lv==='하'?.85:q.lv==='중'?.72:.55;if(round===0&&q.t===weak)p=.15;if(round===1)p=Math.min(.95,p+.2);return rnd()<p?q.a:((q.a+Math.floor(rnd()*4))%5)+1})}
function dGradeCalc(){const s=DM.sheet;let r=0;const types=[];s.qs.forEach((q,i)=>{const ok=DM.ans[i]===q.a;r+=ok?1:0;types.push(q.t);const o=DM.ts[q.t]=DM.ts[q.t]||{n:0,r:0};o.n++;o.r+=ok?1:0});s.g={r,p:r/s.qs.length};const rt={};s.qs.forEach((q,i)=>{const o=rt[q.t]=rt[q.t]||{n:0,r:0};o.n++;o.r+=DM.ans[i]===q.a?1:0});DM.hist.push({p:s.g.p,n:s.qs.length,types,rt})}
async function dScan(inst){DM.st=2;dRender();if(inst||RM){DM.st=3;dRender();return}const cam=$('#cam');await new Promise(r=>requestAnimationFrame(r));cam.classList.add('on');const q=$('.paper .ph .qr',dm),vf=$('.vf',cam);if(q&&vf){const a=rel(q),b=rel(vf);vf.animate([{transform:tf(a,b),transformOrigin:'0 0'},{transform:'none',transformOrigin:'0 0'}],{duration:700,easing:EZ})}
 $('#scanl').animate([{top:'0%'},{top:'100%'},{top:'0%'}],{duration:1100,iterations:1,easing:'ease-in-out'});await wait(1150);cam.classList.add('lock');$('#camMsg').textContent=`인식됨 · 학습지 ${DM.sheet.no} · ${DM.sheet.qs.length}문항`;await wait(700);DM.st=3;dRender()}
async function dFill(round,inst){const ans=dAnswers(round);if(inst||RM){DM.ans=ans;dRender();return}for(let i=0;i<ans.length;i++){DM.ans[i]=ans[i];const row=$$('#omr .om')[i];if(row){row.style.background='#e7f0fb';const b=$(`.bub[data-k="${ans[i]}"]`,row);b.classList.add('sel');b.animate([{transform:'scale(1.12)'},{transform:'none'}],{duration:220,easing:EZ});const pq=$('#pq'+i);pq&&pq.classList.add('hl');setTimeout(()=>{row.style.background='';pq&&pq.classList.remove('hl')},260)}await wait(170)}const h=$('.panel h3 small',dm);h&&(h.textContent=`${ans.length}/${ans.length}`)}
async function dGrade(inst){const s=DM.sheet;dGradeCalc();if(!inst&&!RM){const rows=$$('#omr .om');for(let i=0;i<rows.length;i++){const ok=DM.ans[i]===s.qs[i].a;rows[i].classList.add(ok?'ok':'no');const mk=$('.mk',rows[i]);mk.textContent=ok?'✓':'✗';mk.animate([{transform:'scale(.8)',opacity:0},{transform:'none',opacity:1}],{duration:240,easing:EZ});if(!ok){const c=$(`.bub[data-k="${s.qs[i].a}"]`,rows[i]);c&&c.classList.add('ans')}await wait(90)}await wait(300)}
 DM.st=4;dRender();if(inst||RM)return;const rg=$('#rg');rg.animate([{strokeDashoffset:515},{strokeDashoffset:515*(1-s.g.p)}],{duration:900,easing:EZ});const rv=$('#rv'),to=Math.round(s.g.p*100),t0=performance.now();const f=t=>{const k=Math.min(1,(t-t0)/900);rv.textContent=Math.round(to*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(f)};requestAnimationFrame(f);
 $$('.panel .wi',dm).forEach((w,i)=>w.animate(FX.right,{duration:420,delay:200+i*80,easing:EZ,fill:'backwards'}));if(to>=70)dConfetti()}
function dConfetti(){const c=$('#conf');if(!c)return;const C=['#0d387e','#fdc62d','#2f7fd0','#17956a','#ef7d3c'];c.innerHTML=Array.from({length:50},(_,i)=>`<i style="left:${Math.random()*100}%;background:${C[i%5]}"></i>`).join('');$$('i',c).forEach(el=>{el.animate([{opacity:1,transform:'translate(0,0) rotate(0)'},{opacity:0,transform:`translate(${(Math.random()-.5)*180}px,${560+Math.random()*300}px) rotate(${Math.random()*600}deg)`}],{duration:1200+Math.random()*500,easing:EZ,delay:Math.random()*150,fill:'forwards'})})}
HOOK.demo={n:9,reset(){dReset();dRender()},
 async run(k,inst){const A=!inst&&!RM;
  if(k===1){const ts=dTypes().slice(0,3);if(!A){DM.sel=ts;dRender();return}for(const t of ts){DM.sel.push(t);dRender();const c=$(`.chip[data-t="${CSS.escape(t)}"]`,dm);;await wait(260)}}
  if(k===2){dSwap(()=>{dMake();DM.st=1;dRender()},inst)}
  if(k===3){await dScan(inst)}
  if(k===4){await dFill(0,inst)}
  if(k===5){await dGrade(inst)}
  if(k===6){const s=DM.sheet;const w=s.qs.findIndex((q,i)=>DM.ans[i]!==q.a);if(w<0)return;DM.pick=w;const from=$(`.wi[data-i="${w}"]`,dm);const a=from&&A?rel(from):null;dRender();if(a)morphBox(a,$('#qv .qv',dm),{background:'#fff6dc',borderRadius:'10px'},520);const pq=$('#pq'+w);pq&&pq.classList.add('hl')}
  if(k===7){dSwap(()=>{dRetry();DM.st=1;dRender()},inst)}
  if(k===8){await dScan(inst);await (A?wait(150):0);await dFill(1,inst);await (A?wait(200):0);await dGrade(inst)}
  if(k===9){DM.st=6;dRender();if(A)$$('#cmpBars .cb').forEach((b,i)=>b.animate([{transform:'scaleY(0)'},{transform:'none'}],{duration:800,delay:i*250,easing:EZ,fill:'backwards'}))}
 }};


/* ===== 장마다 들어오면 자동으로 펼쳐지는 연출 ===== */
// 문제: 점 600개(1점 = 15곳)
(()=>{const f=$('#dotsMath');f.innerHTML='<i></i>'.repeat(600);const ds=$$('i',f);
 HOOK.prob={enter(t,inst){ds.forEach((d,i)=>{if(inst||RM)return;const r=Math.floor(i/60),c=i%60;d.animate([{opacity:0,transform:'scale(.4)'},{opacity:1,transform:'none'}],{duration:500,delay:500+(9-r)*70+c*7,easing:EZ,fill:'backwards'})});
  const lone=$('.lone i');if(!inst&&!RM)lone.animate([{opacity:0},{opacity:0,offset:.7},{opacity:1}],{duration:2600,easing:'linear',fill:'backwards'})}};
})();

// 해법: 순환 고리를 빛나는 점이 한 바퀴
(()=>{const svg=$('#ring');const N=[['출제','학습지 · 교재'],['종이 풀이','쪽마다 QR'],['QR 채점','찍으면 채점'],['DB 기록','attempts 1행'],['취약 진단','GROUP BY'],['다음 학습지','틀린 유형 재출제']];
 const P=[[260,150],[800,150],[1340,150],[1340,410],[800,410],[260,410]];
 let g=`<defs><filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter></defs><path id="track" d="M260 150 H1340 A130 130 0 0 1 1340 410 H260 A130 130 0 0 1 260 150 Z" fill="none" stroke="#e5e8eb" stroke-width="4"/><path id="trackOn" d="M260 150 H1340 A130 130 0 0 1 1340 410 H260 A130 130 0 0 1 260 150 Z" fill="none" stroke="#2f7fd0" stroke-width="4" stroke-linecap="round"/>`;
 N.forEach((n,k)=>{const [x,y]=P[k];const up=y<300;g+=`<g class="nd" data-k="${k}"><circle cx="${x}" cy="${y}" r="46" fill="#ffffff" stroke="#d3dce8" stroke-width="3"/><text x="${x}" y="${y+11}" text-anchor="middle" font-family="Paperlogy" font-weight="900" font-size="32" fill="#9fb3c8">${k+1}</text><text x="${x}" y="${up?y-104:y+98}" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="30" fill="#191f28">${n[0]}</text><text x="${x}" y="${up?y-72:y+130}" text-anchor="middle" font-family="Pretendard" font-weight="600" font-size="19" fill="#6b778c">${n[1]}</text></g>`});
 g+=`<circle id="spark" r="12" fill="#fdc62d"/><circle id="sparkG" r="22" fill="#fdc62d" opacity=".5" filter="url(#gl)"/>`;
 svg.innerHTML=g;const tr=$('#trackOn'),L=tr.getTotalLength();tr.style.strokeDasharray=L;tr.style.strokeDashoffset=L;
 const near=k=>{const [x,y]=P[k];let best=0,bd=1e9;for(let t=0;t<=L;t+=5){const p=tr.getPointAtLength(t);const d=(p.x-x)**2+(p.y-y)**2;if(d<bd){bd=d;best=t}}return best};const at=N.map((_,k)=>near(k));
 const light=(k,on)=>{const nd=$(`#ring .nd[data-k="${k}"]`);const c=$('circle',nd),t=$('text',nd);c.setAttribute('fill',on?'#0d387e':'#ffffff');c.setAttribute('stroke',on?'#2f7fd0':'#d3dce8');t.setAttribute('fill',on?'#fdc62d':'#9fb3c8')};
 HOOK.loop={prep(){N.forEach((_,k)=>light(k,false));tr.style.strokeDashoffset=L;$('#spark').setAttribute('opacity',0);$('#sparkG').setAttribute('opacity',0)},enter(t,inst){N.forEach((_,k)=>light(k,false));const sp=$('#spark'),sg=$('#sparkG');if(inst||RM){tr.style.strokeDashoffset=0;N.forEach((_,k)=>light(k,true));sp.setAttribute('opacity',0);sg.setAttribute('opacity',0);return}sp.setAttribute('opacity',1);sg.setAttribute('opacity',.5);
  const t0=performance.now()+700,D=6200;const step=now=>{if(t!==tok)return;const k=Math.max(0,Math.min(1,(now-t0)/D));const e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;const pos=e*L;const p=tr.getPointAtLength(pos);sp.setAttribute('cx',p.x);sp.setAttribute('cy',p.y);sg.setAttribute('cx',p.x);sg.setAttribute('cy',p.y);tr.style.strokeDashoffset=L-pos;at.forEach((a,j)=>light(j,pos>=a-2));if(k<1)requestAnimationFrame(step)};requestAnimationFrame(step)}};
})();

// 시연: 들어오면 9단계 자동 재생
HOOK.demo.prep=function(){HOOK.demo.reset()};
let dStep=0;HOOK.demo.enter=async function(t,inst){HOOK.demo.reset();dStep=0;if(inst&&!isShow()){for(let k=1;k<=9;k++)await HOOK.demo.run(k,true);dStep=9}};
HOOK.demo.step=async function(){if(dStep>=9)return false;dStep++;await HOOK.demo.run(dStep,false);return true};

// 진단: 반 × 유형 지도(시뮬레이션)
(()=>{const CT=window.CMTYPES||[];const CLS=['1반','2반','3반','4반','5반','6반'];seed=20261125;
 const HEAT=CLS.map(()=>{const ce=(rnd()-.5)*.12;const weak=new Set([Math.floor(rnd()*40),Math.floor(rnd()*40),Math.floor(rnd()*40)]);return CT.map((t,ti)=>{const base=.82-(ti%7)*.035-(t[2]==='세포호흡'?.08:t[2]==='광합성'?.05:0);let p=base+ce+(rnd()-.5)*.18-(weak.has(ti)?.28:0);p=Math.max(.18,Math.min(.97,p));const n=380+Math.floor(rnd()*260);return {p,n,r:Math.round(p*n)}})});
 const col=p=>p<.5?`rgba(216,68,59,${.4+(.5-p)*1.3})`:p<.75?`rgba(224,156,18,${.25+(.75-p)*1.6})`:`rgba(23,149,106,${.18+(p-.75)*2.4})`;
 const H=$('#heat');H.style.gridTemplateColumns=`56px repeat(${CT.length},1fr)`;
 H.innerHTML=HEAT.map((row,ci)=>`<div class="rh">${CLS[ci]}</div>`+row.map((c,ti)=>`<div class="c" data-c="${ci}" data-t="${ti}" style="background:${col(c.p)}"></div>`).join('')).join('');
 let m=[1,0,0];HEAT.forEach((row,ci)=>row.forEach((c,ti)=>{if(c.p<m[0])m=[c.p,ci,ti]}));const [,wc,wt]=m;
 const info=()=>{const c=HEAT[wc][wt],t=CT[wt];const rank=HEAT[wc].map((x,k)=>[x.p,k]).sort((a,b)=>a[0]-b[0]).slice(0,3);
  $('#hinfo').innerHTML=`<span class="k">${CLS[wc]} · 가장 약한 유형</span><h3>${esc(t[3])}</h3><span class="num">${Math.round(c.p*100)}%</span><span class="k" style="margin-top:14px">${CLS[wc]} 취약 TOP 3 → 반 공통 학습지</span>${rank.map(([p,k],j)=>`<div class="row"><span>${j+1}. ${esc(CT[k][3])}</span><b>${Math.round(p*100)}%</b></div>`).join('')}`};info();
 HOOK.heat={prep(){$('#hinfo').style.opacity='0';$$('#heat .c').forEach(c=>{c.classList.remove('pick');c.getAnimations().forEach(a=>a.cancel())})},async enter(t,inst){const cells=$$('#heat .c');cells.forEach(c=>{c.classList.remove('pick');c.style.opacity=''});$('#hinfo').style.opacity=inst||RM?'1':'0';
  if(inst||RM){$(`#heat .c[data-c="${wc}"][data-t="${wt}"]`).classList.add('pick');return}
  cells.forEach(c=>{const d=(+c.dataset.t+ +c.dataset.c*4)*12;c.animate([{opacity:0,transform:'scale(.6)'},{opacity:1,transform:'none'}],{duration:500,delay:400+d,easing:EZ,fill:'backwards'})});
  await wait(1900);if(t!==tok)return;const cell=$(`#heat .c[data-c="${wc}"][data-t="${wt}"]`);cells.forEach(c=>{if(+c.dataset.c!==wc)c.animate([{opacity:1},{opacity:.28}],{duration:500,easing:EZ,fill:'forwards'})});cell.classList.add('pick');
  await wait(300);if(t!==tok)return;$('#hinfo').style.opacity='1';morphBox(rel(cell),$('#hinfo'),{background:'rgba(216,68,59,.85)',borderRadius:'8px'},700)}};
})();

// DB: ERD가 그려진다
(()=>{const E={auth:[40,40,'교사 계정','auth.users',1],set:[330,40,'학원 설정','teacher_settings',0],stu:[330,290,'학생','students',0],ws:[620,40,'학습지','worksheets',0],att:[620,290,'채점 기록','attempts',0],qb:[880,290,'문항(JSON)','question_bank',1],asg:[620,520,'과제 배정','assignments',0],wn:[880,520,'오답 메모','wrong_notes',0],cls:[40,520,'반','classes',0],cm:[40,290,'반 소속','class_members',0],pa:[330,560,'학부모 계정','parent_accounts',0],atd:[200,620,'출결','attendance',0]};
 const R=[['auth','set','1','1'],['auth','stu','1','n'],['stu','ws','1','n'],['stu','att','1','n'],['ws','att','1','n',1],['att','qb','m','n',1],['stu','asg','1','n'],['stu','wn','1','n'],['wn','qb','n','1',1],['cls','cm','1','n'],['stu','cm','1','n'],['stu','pa','1','n'],['stu','atd','1','n']];
 const W=150,Hh=56,c=k=>[E[k][0]+W/2,E[k][1]+Hh/2];let g='';
 R.forEach(([a,b,ca,cb,lg])=>{const [x1,y1]=c(a),[x2,y2]=c(b),mx=(x1+x2)/2,my=(y1+y2)/2;g+=`<line class="el" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${lg?'#b0b8c1':'#2f7fd0'}" stroke-width="2" ${lg?'stroke-dasharray="7 5"':''}/><polygon class="ed" points="${mx-22},${my} ${mx},${my-13} ${mx+22},${my} ${mx},${my+13}" fill="#fdc62d"/><text class="et" x="${x1+(x2-x1)*.22+6}" y="${y1+(y2-y1)*.22-7}" font-size="15" font-weight="800" fill="#4e5968">${ca}</text><text class="et" x="${x1+(x2-x1)*.78+6}" y="${y1+(y2-y1)*.78-7}" font-size="15" font-weight="800" fill="#4e5968">${cb}</text>`});
 Object.entries(E).forEach(([k,[x,y,ko,en,v]])=>{g+=`<g class="en"><rect x="${x}" y="${y}" width="${W}" height="${Hh}" rx="8" fill="${k==='stu'?'#0d387e':'#ffffff'}" stroke="${k==='stu'?'#0d387e':'#c3ccd8'}" stroke-width="1.6" ${v?'stroke-dasharray="5 4"':''}/><text x="${x+W/2}" y="${y+25}" text-anchor="middle" font-size="17" font-weight="800" fill="${k==='stu'?'#fff':'#191f28'}">${ko}</text><text x="${x+W/2}" y="${y+43}" text-anchor="middle" font-size="11.5" fill="${k==='stu'?'#c7d5ee':'#6b778c'}">${en}</text></g>`});
 const [cx,cy]=c('cm');g+=`<g id="nm"><circle cx="${cx}" cy="${cy}" r="92" fill="none" stroke="#fdc62d" stroke-width="4"/><text x="${cx-74}" y="${cy-108}" font-size="18" font-weight="900" fill="#b07a00">학생 ↔ 반 = N:M → 연결 표</text></g>`;
 $('#erd').innerHTML=g;
 HOOK.db={enter(t,inst){if(inst||RM)return;$$('#erd .el').forEach((l,i)=>{const L=l.getTotalLength();l.animate([{strokeDasharray:`0 ${L}`},{strokeDasharray:`${L} ${L}`}],{duration:700,delay:500+i*70,easing:EIO,fill:'backwards'})});
  $$('#erd .en').forEach((n,i)=>n.animate([{opacity:0,transform:'translateY(10px)'},{opacity:1,transform:'none'}],{duration:500,delay:300+i*60,easing:EZ,fill:'backwards'}));
  $$('#erd .ed,#erd .et').forEach((n,i)=>n.animate([{opacity:0},{opacity:1}],{duration:400,delay:1100+i*20,easing:EZ,fill:'backwards'}));
  $('#nm').animate([{opacity:0,transform:'scale(.9)'},{opacity:1,transform:'none'}],{duration:600,delay:2000,easing:EZ,fill:'backwards'});$('#nm').style.transformOrigin=`${cx}px ${cy}px`}};
})();

// 라즈베리파이: 구조도 + 채점 제출 요청이 흐른다
(()=>{const A=$('#arch');const BX={web:[0,40,280,100,'브라우저','학생 휴대폰 · 교사 PC'],pages:[0,330,280,100,'GitHub Pages','앱 화면 · 문제은행'],tun:[400,40,280,100,'HTTPS 터널','Tailscale / DuckDNS'],caddy:[800,40,280,100,'Caddy','게이트웨이'],rest:[1250,40,350,100,'PostgREST','/rest/v1 · SQL 함수'],auth:[1250,200,350,100,'GoTrue','/auth/v1 · 로그인'],pk:[1250,360,350,100,'Deno','/functions · 패스키'],db:[700,260,420,170,'PostgreSQL 15','표 36 · 함수 92 · RLS 76 · USB SSD']};
 const AL=[['web','tun'],['tun','caddy'],['web','pages'],['caddy','rest'],['caddy','auth'],['caddy','pk'],['rest','db'],['auth','db'],['pk','db']];const cc=k=>{const b=BX[k];return [b[0]+b[2]/2,b[1]+b[3]/2]};
 let s=`<svg width="1600" height="560" style="position:absolute;left:0;top:0;overflow:visible">${AL.map(([a,b])=>{const [x1,y1]=cc(a),[x2,y2]=cc(b);return `<path class="al" d="M${x1} ${y1} L${x2} ${y2}" stroke="#c9d6e8" stroke-width="3" fill="none"/>`}).join('')}</svg>`;
 s+=`<div style="position:absolute;left:660px;top:-10px;width:960px;height:520px;border:2px dashed #9fbfe8;border-radius:24px"></div><div style="position:absolute;left:684px;top:-44px;font:800 17px Pretendard;color:#2f7fd0">라즈베리파이 5 · Docker</div>`;
 s+=Object.entries(BX).map(([k,b])=>`<div class="box ${k==='db'?'pi':''}" id="ab-${k}" style="left:${b[0]}px;top:${b[1]}px;width:${b[2]}px;height:${b[3]}px"><h4>${b[4]}</h4><p>${b[5]}</p></div>`).join('')+`<div id="pkt" style="position:absolute;width:24px;height:24px;border-radius:50%;background:#fdc62d;opacity:0;z-index:5;left:0;top:0"></div><div id="plog" style="position:absolute;left:0;top:480px;font:700 20px Pretendard;color:#b07a00"></div>`;
 A.innerHTML=s;const path=[['web','학생: 채점 제출'],['tun','HTTPS 터널'],['caddy','Caddy → PostgREST'],['rest','st_submit 함수 호출'],['db','attempts에 1행 기록'],['web','채점 완료']];
 HOOK.pi={prep(){$$('#arch .box').forEach(b=>b.classList.remove('hot'));$('#pkt').style.opacity='0';$('#plog').textContent=''},async enter(t,inst){$$('#arch .box').forEach(b=>b.classList.remove('hot'));const p=$('#pkt');p.style.opacity='0';$('#plog').textContent='';
  if(inst||RM)return;$$('#arch .al').forEach((l,i)=>{const L=l.getTotalLength();l.animate([{strokeDasharray:`0 ${L}`},{strokeDasharray:`${L} ${L}`}],{duration:600,delay:400+i*80,easing:EIO,fill:'backwards'})});
  $$('#arch .box').forEach((b,i)=>b.animate([{opacity:0,transform:'translateY(12px)'},{opacity:1,transform:'none'}],{duration:500,delay:200+i*70,easing:EZ,fill:'backwards'}));
  await wait(1500);for(let i=0;i<path.length;i++){if(t!==tok)return;const [id,txt]=path[i],b=BX[id];$$('#arch .box').forEach(x=>x.classList.remove('hot'));$('#ab-'+id).classList.add('hot');p.style.opacity='1';p.style.transition='transform .5s cubic-bezier(.22,1,.36,1)';p.style.transform=`translate(${b[0]+b[2]-34}px,${b[1]+12}px)`;$('#plog').textContent=`${i+1}. ${txt}`;await wait(700)}
  p.style.opacity='0'}};
})();


// 문제은행: 막대가 자라고 숫자가 올라감
HOOK.bank={prep(){$$('.br i').forEach(i=>i.getAnimations().forEach(a=>a.cancel()))},enter(t,inst){if(inst||RM)return;$$('.br').forEach((r,i)=>{const bar=$('i',r),num=$('b',r),to=+num.dataset.to;bar.animate([{transform:'scaleX(0)'},{transform:'none'}],{duration:1100,delay:500+i*120,easing:EZ,fill:'backwards'});const t0=performance.now()+500+i*120;const f=n=>{if(t!==tok)return;const k=Math.max(0,Math.min(1,(n-t0)/1100));num.textContent=fmt(Math.round(to*(1-Math.pow(1-k,4))));if(k<1)requestAnimationFrame(f)};requestAnimationFrame(f)})}};
// 태블릿 출결: 등원 알림이 뜬다
HOOK.kiosk={prep(){$('#kToast').style.opacity='0'},async enter(t,inst){const k=$('#kToast');if(inst||RM){k.style.opacity='1';return}await wait(1300);if(t!==tok)return;k.style.opacity='1';k.animate([{opacity:0,transform:'translateY(-16px) scale(.96)'},{opacity:1,transform:'none'}],{duration:600,easing:EZ})}};
// 결제 흐름: 화살표가 차례로
HOOK.pay={enter(t,inst){if(inst||RM)return;$$('.payflow .arr path').forEach((p,i)=>{const L=p.getTotalLength();p.animate([{strokeDasharray:`0 ${L}`},{strokeDasharray:`${L} ${L}`}],{duration:600,delay:900+i*500,easing:EIO,fill:'backwards'})});const ck=$('.done .ck');ck.animate([{transform:'scale(.6)',opacity:0},{transform:'none',opacity:1}],{duration:600,delay:1900,easing:EZ,fill:'backwards'})}};

/* ===== 전환 효과 ===== */
const COLORS=['#0d387e','#2f7fd0','#fdc62d','#0d387e','#4b93ff','#0a2c63'];
function enterChoreo(nw){const h=$('h1,h2',nw);if(h)h.animate([{clipPath:'inset(0 0 100% 0)',transform:'translateY(40px)'},{clipPath:'inset(0 0 -30% 0)',transform:'none'}],{duration:900,delay:120,easing:EZ,fill:'backwards'});
 let n=0;$$('.ani',nw).forEach(el=>{if(el===h)return;el.animate([{opacity:0,transform:'translateY(36px) scale(.985)'},{opacity:1,transform:'none'}],{duration:900,delay:300+Math.min(n++,12)*(nw.dataset.id==='wall'?70:110),easing:EZ,fill:'backwards'})});
 const lg=$('.logo.sm',nw);lg&&lg.animate([{opacity:0},{opacity:1}],{duration:600,delay:200,fill:'backwards'})}
async function transition(old,nw,type,back,onShow){let shown=false;const fire=()=>{if(!shown){shown=true;onShow&&onShow()}};const show=()=>{old.classList.remove('on');nw.classList.add('on');fire()};
 const both=()=>{old.classList.add('on');nw.classList.add('on');fire()};
 if(RM||!type){show();return}
 if(type==='stripes'){const n=6;FXL.innerHTML=Array.from({length:n},(_,i)=>`<div class="bar" style="left:${i*100/n}%;width:${100/n+.2}%;background:${COLORS[i]}"></div>`).join('');const bars=$$('.bar',FXL);
  await Promise.all(bars.map((b,i)=>b.animate([{transform:'scaleY(0)',transformOrigin:i%2?'bottom':'top'},{transform:'scaleY(1)',transformOrigin:i%2?'bottom':'top'}],{duration:420,delay:i*45,easing:EIO,fill:'forwards'}).finished));
  show();await Promise.all(bars.map((b,i)=>b.animate([{transform:'scaleY(1)',transformOrigin:i%2?'top':'bottom'},{transform:'scaleY(0)',transformOrigin:i%2?'top':'bottom'}],{duration:460,delay:i*45,easing:EIO,fill:'forwards'}).finished));FXL.innerHTML='';return}
 if(type==='doors'){FXL.innerHTML=`<div class="door l"></div><div class="door r"></div><div class="dlogo">${logoW}</div>`;const [l,r]=$$('.door',FXL),dl=$('.dlogo',FXL);dl.animate([{opacity:0,transform:'translate(-50%,-50%) scale(.85)'},{opacity:1,transform:'translate(-50%,-50%)'}],{duration:420,delay:300,easing:EZ,fill:'both'});
  await Promise.all([l.animate([{transform:'translateX(-100%)'},{transform:'none'}],{duration:520,easing:EIO,fill:'forwards'}).finished,r.animate([{transform:'translateX(100%)'},{transform:'none'}],{duration:520,easing:EIO,fill:'forwards'}).finished]);
  show();await wait(260);dl.animate([{opacity:1},{opacity:0}],{duration:200,fill:'forwards'});await Promise.all([l.animate([{transform:'none'},{transform:'translateX(-100%)'}],{duration:620,easing:EIO,fill:'forwards'}).finished,r.animate([{transform:'none'},{transform:'translateX(100%)'}],{duration:620,easing:EIO,fill:'forwards'}).finished]);FXL.innerHTML='';return}
 both();old.style.zIndex=1;nw.style.zIndex=2;const clean=()=>{old.classList.remove('on');old.style.zIndex='';nw.style.zIndex='';old.getAnimations().forEach(a=>a.cancel())};
 const dir=back?-1:1;
 if(type==='zoom'){old.animate([{transform:'none',opacity:1},{transform:'scale(1.35)',opacity:0}],{duration:700,easing:EIO,fill:'forwards'});await nw.animate([{transform:'scale(.7)',opacity:0},{transform:'none',opacity:1}],{duration:800,easing:EZ}).finished;clean();return}
 if(type==='iris'){await nw.animate([{clipPath:'circle(0% at 50% 50%)'},{clipPath:'circle(75% at 50% 50%)'}],{duration:900,easing:EIO}).finished;clean();return}
 if(type==='push'){old.animate([{transform:'none'},{transform:`translateX(${-60*dir}%) scale(.9)`,opacity:.2}],{duration:750,easing:EIO,fill:'forwards'});await nw.animate([{transform:`translateX(${100*dir}%)`},{transform:'none'}],{duration:750,easing:EIO}).finished;clean();return}
 if(type==='flip'){nw.classList.remove('on');nw.style.zIndex=0;old.style.zIndex=1;shown=false;await old.animate([{transform:'none'},{transform:`rotateY(${-90*dir}deg) scale(.9)`}],{duration:420,easing:'cubic-bezier(.55,0,1,.45)',fill:'forwards'}).finished;old.classList.remove('on');nw.classList.add('on');fire();nw.style.zIndex=2;await nw.animate([{transform:`rotateY(${90*dir}deg) scale(.9)`},{transform:'none'}],{duration:520,easing:'cubic-bezier(0,.55,.45,1)'}).finished;clean();return}
 show();clean()}

async function go(i,opts={}){i=Math.max(0,Math.min(slides.length-1,i));if(i===cur&&opts.force!==true&&slides[i].classList.contains('on'))return;const old=slides[cur],nw=slides[i];const back=i<cur;const t=++tok;
 cur=i;$$('#side button').forEach((b,k)=>b.classList.toggle('cur',k===cur));$('#pg').textContent=`${cur+1} / ${slides.length}`;
 $('#notes').innerHTML=`<b>${cur+1}. ${esc(nw.dataset.title)}</b><br>${esc(nw.dataset.notes||'')}`;try{history.replaceState(null,'','#'+(cur+1))}catch(e){}
 const H=HOOK[nw.dataset.id];
 if(!isShow()||old===nw){slides.forEach(s=>s.classList.toggle('on',s===nw));H&&H.enter&&H.enter(t,true);return}
 H&&H.prep&&H.prep();
 await transition(old,nw,back?'push':(nw.dataset.tr||'zoom'),back,()=>{enterChoreo(nw);H&&H.enter&&H.enter(t,false)});}
const next=async()=>{if(busy)return;busy=true;const H=HOOK[slides[cur].dataset.id];if(isShow()&&H&&H.step){const did=await H.step();if(did){busy=false;return}}await go(cur+1);busy=false};
const prev=async()=>{if(busy)return;busy=true;await go(cur-1);busy=false};

/* ===== 편집 ===== */
const KEY='solvi-deck-v3';const SEL='h1,h2,p,li,figcaption,td,th,.who span,.who b,.vs p,.big3 span,.big3 small,.schools span';
const EDS=slides.map(s=>{const all=$$(SEL,s).filter(e=>!e.closest('#demo,#hinfo,#arch,svg'));return all.filter(e=>!all.some(o=>o!==e&&o.contains(e)))});
let edits={};try{const emb=document.getElementById('ppt-edits');if(emb)edits=JSON.parse(emb.textContent||'{}')}catch(e){}
try{const ls=JSON.parse(localStorage.getItem(KEY)||'null');if(ls)edits=Object.assign({},edits,ls)}catch(e){}
EDS.forEach((l,si)=>l.forEach((e,k)=>{e.dataset.ek=si+':'+k;if(edits[si+':'+k]!=null)e.innerHTML=edits[si+':'+k]}));
let editing=true;const editSync=()=>{const on=editing&&!isShow();document.body.classList.toggle('editing',on);EDS.flat().forEach(e=>on?e.setAttribute('contenteditable','true'):e.removeAttribute('contenteditable'));$('#bEdit').classList.toggle('on',editing)};
let sT;document.addEventListener('input',ev=>{const e=ev.target.closest&&ev.target.closest('[data-ek]');if(!e)return;edits[e.dataset.ek]=e.innerHTML;clearTimeout(sT);sT=setTimeout(()=>{try{localStorage.setItem(KEY,JSON.stringify(edits));$('#saved').textContent='자동 저장됨'}catch(err){$('#saved').textContent='HTML로 저장하세요'}},300)});
document.addEventListener('paste',ev=>{if(!ev.target.closest||!ev.target.closest('[data-ek]'))return;ev.preventDefault();document.execCommand('insertText',false,(ev.clipboardData||window.clipboardData).getData('text/plain'))});
$('#bEdit').onclick=()=>{editing=!editing;editSync()};
$('#bSave').onclick=()=>{let html=ORIGINAL.replace(/<script id="ppt-edits"[^>]*>[\s\S]*?<\/script>\n?/,'');html=html.replace('<script src="lib/qrcode.js">',`<script id="ppt-edits" type="application/json">${JSON.stringify(edits).replace(/</g,'\\u003c')}</script>\n<script src="lib/qrcode.js">`).replace(/<body class="[^"]*"/,'<body class="edit"');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([html],{type:'text/html'}));a.download='solvi-presentation.html';a.click()};

/* ===== 모드 · 키 · 터치 ===== */
$('#side').innerHTML=slides.map((s,i)=>`<button data-i="${i}"><i>${i+1}</i>${esc(s.dataset.title)}</button>`).join('');
$('#side').onclick=e=>{const b=e.target.closest('button');if(b)go(+b.dataset.i)};
let t0=Date.now();
function startShow(){document.body.classList.remove('edit');document.body.classList.add('show');editSync();document.activeElement&&document.activeElement.blur();t0=Date.now();document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen().catch(()=>{});fit();const s=slides[cur];enterChoreo(s);const H=HOOK[s.dataset.id];H&&H.enter&&H.enter(++tok,false);setTimeout(fit,80)}
function endShow(){document.body.classList.remove('show');document.body.classList.add('edit');$('#notes').classList.remove('on');$('#blk').classList.remove('on');if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});fit();go(cur,{force:true});editSync();setTimeout(fit,80)}
document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement&&isShow())endShow();setTimeout(fit,60)});
$('#bShow').onclick=startShow;$('#hX').onclick=endShow;$('#hN').onclick=()=>$('#notes').classList.toggle('on');
setInterval(()=>{const s=Math.floor((Date.now()-t0)/1000);const el=$('#timer');el.textContent=String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');el.className=s>=900?'over':s>=780?'warn':''},500);
const NEXT=['ArrowRight','ArrowDown','PageDown',' ','Enter','MediaTrackNext'],PREV=['ArrowLeft','ArrowUp','PageUp','Backspace','MediaTrackPrevious'];
document.addEventListener('keydown',e=>{const inEd=e.target.closest&&e.target.closest('[contenteditable=true]');
 if(e.key==='Escape'){if(inEd){e.target.blur();return}if(isShow())endShow();return}if(inEd)return;
 if(e.key==='F5'){e.preventDefault();if(!isShow())startShow();return}
 if($('#blk').classList.contains('on')){$('#blk').classList.remove('on');e.preventDefault();return}
 if(NEXT.includes(e.key)){e.preventDefault();next();return}if(PREV.includes(e.key)){e.preventDefault();prev();return}
 const k=e.key.toLowerCase();if(k==='b'||k==='.')$('#blk').classList.add('on');else if(k==='s')$('#notes').classList.toggle('on');else if(k==='t')t0=Date.now();else if(k==='e'&&!isShow()){editing=!editing;editSync()}});
stage.addEventListener('click',e=>{if(isShow())next()});stage.addEventListener('contextmenu',e=>{if(isShow()){e.preventDefault();prev()}});
let tx=null;stage.addEventListener('touchstart',e=>{tx=[e.touches[0].clientX,e.touches[0].clientY]},{passive:true});
stage.addEventListener('touchend',e=>{if(!tx||!isShow())return;const dx=e.changedTouches[0].clientX-tx[0],dy=e.changedTouches[0].clientY-tx[1];tx=null;if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)*1.5){e.preventDefault();dx<0?next():prev()}});
$('#blk').onclick=()=>$('#blk').classList.remove('on');

fit();const h0=parseInt(location.hash.slice(1));cur=h0>0?Math.min(h0,slides.length)-1:0;slides.forEach((s,i)=>s.classList.toggle('on',i===cur));$$('#side button').forEach((b,k)=>b.classList.toggle('cur',k===cur));$('#pg').textContent=`${cur+1} / ${slides.length}`;
slides.forEach(s=>{const H=HOOK[s.dataset.id];H&&H.enter&&H.enter(0,true)});editSync();
})();
