/* Solvi 발표 자료 — 리모컨 한 버튼 진행(단계 빌드) · 모핑 · 도표 애니메이션 · 라이브 시연 · 편집 모드 */
(()=>{
'use strict';
const ORIGINAL='<!doctype html>\n'+document.documentElement.outerHTML;
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=n=>Number(n).toLocaleString('ko-KR');
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
const EZ='cubic-bezier(.22,1,.36,1)',EIO='cubic-bezier(.65,0,.35,1)',EXIT='cubic-bezier(.4,0,1,1)';
const slides=$$('.slide'),stage=$('#stage'),vp=$('#viewport');
let cur=0,step=0,K=1;
const isShow=()=>document.body.classList.contains('show');
const KEY='solvi-deck-edits-v2';
let seed=7;const rnd=()=>(seed=(seed*1103515245+12345)&0x7fffffff)/0x7fffffff;
const wait=ms=>new Promise(r=>setTimeout(r,RM?0:ms));
const NS='http://www.w3.org/2000/svg';

/* ---------- 화면 맞춤 ---------- */
function fit(){const r=vp.getBoundingClientRect();const s=Math.min(r.width/1920,r.height/1080)*(isShow()?1:.97);K=s;stage.style.transform=`translate(-50%,-50%) scale(${s})`}
addEventListener('resize',fit);

/* ---------- 모핑 엔진 ---------- */
const rel=el=>{const r=el.getBoundingClientRect(),q=stage.getBoundingClientRect();return {x:(r.left-q.left)/K,y:(r.top-q.top)/K,w:r.width/K,h:r.height/K}};
function ghostOf(el,r){const g=el.cloneNode(true);[g,...g.querySelectorAll('*')].forEach(x=>{x.removeAttribute&&(x.removeAttribute('id'),x.removeAttribute('contenteditable'),x.removeAttribute('data-morph'))});
 g.classList&&g.classList.add('ghost');Object.assign(g.style,{position:'absolute',left:r.x+'px',top:r.y+'px',width:r.w+'px',height:r.h+'px',margin:'0',zIndex:60,pointerEvents:'none',transformOrigin:'0 0',opacity:'1',transform:'none',transition:'none'});stage.appendChild(g);return g}
const tf=(a,b)=>`translate(${a.x-b.x}px,${a.y-b.y}px) scale(${a.w/Math.max(b.w,1)},${a.h/Math.max(b.h,1)})`;
function morphPair(g,a,el,b,d){g.animate([{transform:'none',opacity:1},{transform:tf(b,a),opacity:0}],{duration:d,easing:EZ,fill:'forwards'}).onfinish=()=>g.remove();
 el.animate([{transform:tf(a,b),opacity:0,transformOrigin:'0 0'},{opacity:1,offset:.5},{transform:'none',opacity:1,transformOrigin:'0 0'}],{duration:d,easing:EZ})}
function morphFromTo(fromEl,toEl,d){if(RM||!fromEl||!toEl)return;const a=rel(fromEl),b=rel(toEl);if(!a.w||!b.w)return;morphPair(ghostOf(fromEl,a),a,toEl,b,d||480)}
function morphBox(a,toEl,css,d){if(RM||!toEl)return;const b=rel(toEl);const g=document.createElement('div');g.className='ghost';Object.assign(g.style,{position:'absolute',left:a.x+'px',top:a.y+'px',width:a.w+'px',height:a.h+'px',zIndex:60,pointerEvents:'none',transformOrigin:'0 0',borderRadius:'6px'},css||{});stage.appendChild(g);morphPair(g,a,toEl,b,d||520)}

/* ---------- 효과 ---------- */
const FX={rise:[{opacity:0,transform:'translateY(14px)'},{opacity:1,transform:'none'}],left:[{opacity:0,transform:'translateX(-18px)'},{opacity:1,transform:'none'}],right:[{opacity:0,transform:'translateX(18px)'},{opacity:1,transform:'none'}],
 pop:[{opacity:0,transform:'scale(.94)'},{opacity:1,transform:'none'}],zoom:[{opacity:0,transform:'scale(1.03)'},{opacity:1,transform:'none'}],fade:[{opacity:0},{opacity:1}],
 growx:[{opacity:1,transform:'scaleX(0)'},{opacity:1,transform:'none'}],growy:[{opacity:1,transform:'scaleY(0)'},{opacity:1,transform:'none'}],
 wipe:[{opacity:1,clipPath:'inset(0 100% 0 0)'},{opacity:1,clipPath:'inset(0 0 0 0)'}],drop:[{opacity:0,transform:'translateY(-10px)'},{opacity:1,transform:'none'}]};
function countUp(el,delay){const to=+el.dataset.count;const dec=+(el.dataset.dec||0);const suf=el.dataset.suf||'';if(RM){el.textContent=fmt(to.toFixed(dec))+suf;return}el.textContent=(0).toFixed(dec)+suf;
 setTimeout(()=>{const t0=performance.now(),D=1200;const f=t=>{const k=Math.min(1,(t-t0)/D),v=to*(1-Math.pow(1-k,4));el.textContent=(dec?v.toFixed(dec):fmt(Math.round(v)))+suf;if(k<1)requestAnimationFrame(f)};requestAnimationFrame(f)},delay)}
function show(el,instant){el.classList.add('shown');const counts=[...(el.matches('[data-count]')?[el]:[]),...$$('[data-count]',el)];
 if(instant||RM){counts.forEach(c=>{const to=+c.dataset.count,dec=+(c.dataset.dec||0);c.textContent=(dec?to.toFixed(dec):fmt(to))+(c.dataset.suf||'')});if(el.dataset.fx==='draw')el.style.strokeDashoffset='0';return}
 const fx=el.dataset.fx||'rise',d=+el.dataset.d||0,dur=+el.dataset.dur||(fx==='growx'||fx==='growy'?900:fx==='wipe'?700:640);
 if(fx==='draw'){const L=el.getTotalLength?el.getTotalLength():0;el.style.strokeDasharray=L+' '+L;el.animate([{strokeDashoffset:L},{strokeDashoffset:0}],{duration:dur||1000,delay:d,easing:EIO,fill:'backwards'});el.style.strokeDashoffset='0'}
 else el.animate(FX[fx]||FX.rise,{duration:dur,delay:d,easing:fx==='wipe'?EIO:EZ,fill:'backwards'});
 counts.forEach(c=>countUp(c,d+80))}

/* ---------- 로고 ---------- */
$$('.brand').forEach(b=>{b.innerHTML=window.LOGO||'';b.dataset.morph='logo'});
{const e=$('#endLogo');if(e){delete e.dataset.morph;const p0=$('svg path',e);p0&&p0.setAttribute('fill','#ffffff')}}


/* ---------- SVG 도우미 ---------- */
const sv=(w,h,inner,extra='')=>`<svg viewBox="0 0 ${w} ${h}" width="100%" height="100%" ${extra}>${inner}</svg>`;
const T=(x,y,t,o={})=>`<text x="${x}" y="${y}" font-size="${o.fs||16}" font-weight="${o.fw||600}" fill="${o.c||'#3a4556'}" text-anchor="${o.a||'start'}" font-family="${o.ff||'Pretendard'}" ${o.b!=null?`data-b="${o.b}" data-fx="${o.fx||'fade'}" data-d="${o.d||0}"`:''}>${t}</text>`;
const B=(b,fx,d,extra='')=>b==null?'':`data-b="${b}" data-fx="${fx}" data-d="${d||0}" ${extra}`;

/* ===== 슬라이드별 그리기 ===== */
const HOOK={};const H=i=>HOOK[slides[i]&&slides[i].dataset.id];
// --- 문제: 점 9,000 ≈ 600개(1점 = 15곳)
(()=>{const f=$('#dotsMath');if(!f)return;f.innerHTML='<i></i>'.repeat(600);const ds=$$('i',f);
 HOOK.prob={n:3,reset(){ds.forEach(d=>d.style.opacity='0')},run(k,inst){if(k!==1)return;ds.forEach((d,i)=>{d.style.opacity='1';if(!inst&&!RM){const r=Math.floor(i/60),c=i%60;d.animate([{opacity:0,transform:'scale(.6)'},{opacity:1,transform:'none'}],{duration:420,delay:(9-r)*60+c*6,easing:EZ,fill:'backwards'})}})}};
 const cap=$('.cmpviz .side:first-child .cap');if(cap){cap.dataset.b='1';cap.dataset.fx='rise';cap.dataset.d='500'}
})();
// --- 4 비교표: 열 단위 공개
HOOK.cmp={n:5,reset(){$$('#mx [data-c]').forEach(c=>{c.style.opacity='0'})},run(k,inst){const cells=$$(`#mx [data-c="${k}"]`);cells.forEach((c,i)=>{c.style.opacity='1';if(!inst&&!RM)c.animate(k===5?FX.wipe:FX.drop,{duration:k===5?520:420,delay:i*45,easing:EZ,fill:'backwards'})})},edit(){$$('#mx [data-c]').forEach(c=>c.style.opacity='1')}};

// --- 5 순환(원형)
const LOOP=[['출제','학습지 · 교재 · 모의고사','유형 · 난이도 · 문항 수만 고르면 자동 출제','INSERT INTO worksheets (wid, meta)','img/app/xdr-build.webp'],
 ['종이 풀이','A4 인쇄 · PDF · HWPX','쪽마다 QR · 문항 코드 인쇄','문항 코드 G-cm05-0002 = 종이 ↔ DB 열쇠','img/app/book-problem.webp'],
 ['QR 채점','휴대폰 카메라 · OMR 사진','쪽 QR을 찍으면 그 쪽만 바로 채점','SELECT ws_get(wid); SELECT st_submit(…);','img/app/phone-omr.webp'],
 ['DB 기록','attempts 표 1행','채점 한 번 = attempts 한 행','attempts(student_id, t, set, sub, items)','img/erd/attempts.png'],
 ['취약 진단','GROUP BY · 윈도 함수','유형별 정답률 · 오답 원인 분석','GROUP BY student_id, type · rank() OVER (…)','img/app/xdr-weak.webp'],
 ['다음 학습지','쌍둥이 · 오답 학습지','틀린 유형의 새 문항으로 재출제','→ 다시 1. 출제 — 돌수록 진단이 정확해짐','img/fig/demo-retry.png']];
(()=>{const svg=$('#ring');const cx=380,cy=380,R=285,C=2*Math.PI*R;const ang=k=>(-90+k*60)*Math.PI/180;const np=k=>[cx+R*Math.cos(ang(k)),cy+R*Math.sin(ang(k))];
 let g=`<circle cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="#e3e9f1" stroke-width="16" ${B(0,'fade',0)}/>`+`<circle id="ringP" cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="#2f7fd0" stroke-width="16" stroke-linecap="round" stroke-dasharray="${C}" stroke-dashoffset="${C}" transform="rotate(-90 ${cx} ${cy})"/>`;
 for(let k=0;k<6;k++){const a=ang(k)+Math.PI/6;const ax=cx+R*Math.cos(a),ay=cy+R*Math.sin(a);g+=`<path d="M${ax-9} ${ay-11} L${ax+9} ${ay} L${ax-9} ${ay+11}" fill="#9fb3c8" transform="rotate(${(-90+k*60+30)+90} ${ax} ${ay})" ${B(0,'fade',600)}/>`}
 LOOP.forEach((n,k)=>{const [x,y]=np(k);g+=`<g class="rn" data-k="${k}" ${B(0,'pop',150+k*110)} style="transform-origin:${x}px ${y}px;transform-box:view-box"><circle cx="${x}" cy="${y}" r="66" fill="#fff" stroke="#d3dce8" stroke-width="3"/>${T(x,y-14,k+1,{a:'middle',fs:28,fw:900,c:'#9fb3c8',ff:'Paperlogy'})}${T(x,y+16,n[0],{a:'middle',fs:21,fw:800,c:'#121a27'})}</g>`});
 g+=`<g id="rc" ${B(0,'fade',700)}><text id="rcN" x="${cx}" y="${cy-30}" text-anchor="middle" font-family="Paperlogy" font-weight="900" font-size="92" fill="#0d387e">6</text><text id="rcT" x="${cx}" y="${cy+20}" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="30" fill="#121a27">단계 순환</text><text id="rcS" x="${cx}" y="${cy+58}" text-anchor="middle" font-family="Pretendard" font-weight="600" font-size="19" fill="#6c778a">돌 때마다 attempts에 기록이 쌓인다</text></g>`;
 svg.innerHTML=g;
 const panel=(k,inst)=>{const P=$('#lpanel');if(k<0){P.innerHTML=`<div class="shotw"><img src="img/app/mac-thome.webp" alt=""></div><div class="lt"><span class="big">한 바퀴</span><span>모든 기능의 기준</span></div><p>종이 → DB → 다시 종이</p><div class="db"><b>핵심</b>문항 코드 하나로 종이 · QR · DB가 같은 문항을 가리킨다</div>`;return}
  const n=LOOP[k];P.innerHTML=`<div class="shotw"><img src="${n[4]}" alt=""></div><div class="lt"><span class="big">${k+1}. ${n[0]}</span><span>${n[1]}</span></div><p>${n[2]}</p><div class="db"><b>DB에서는</b>${esc(n[3])}</div>`;
  if(!inst&&!RM){$('.shotw',P).animate([{opacity:0,transform:'scale(.96)'},{opacity:1,transform:'none'}],{duration:520,easing:EZ});$$('.lt,p,.db',P).forEach((e,i)=>e.animate(FX.rise,{duration:480,delay:80+i*70,easing:EZ,fill:'backwards'}))}};
 const setRing=(k,inst)=>{const p=$('#ringP');const to=C*(1-(k+1)/6);const from=+p.getAttribute('stroke-dashoffset');p.setAttribute('stroke-dashoffset',to);if(!inst&&!RM)p.animate([{strokeDashoffset:from},{strokeDashoffset:to}],{duration:650,easing:EZ});
  $$('#ring .rn').forEach((r,j)=>{const c=$('circle',r),ts=$$('text',r);const on=j===k,done=j<k;c.setAttribute('fill',on?'#0d387e':'#fff');c.setAttribute('stroke',on?'#0d387e':done?'#2f7fd0':'#d3dce8');ts[0].setAttribute('fill',on?'#fdc62d':done?'#2f7fd0':'#9fb3c8');ts[1].setAttribute('fill',on?'#fff':'#121a27');});
  $('#rcN').textContent=k+1;$('#rcT').textContent=LOOP[k][0];$('#rcS').textContent=LOOP[k][1];if(!inst&&!RM)$('#rc').animate([{opacity:0,transform:'translateY(10px)'},{opacity:1,transform:'none'}],{duration:420,easing:EZ})};
 HOOK.loop={n:6,reset(){$('#ringP').setAttribute('stroke-dashoffset',C);$$('#ring .rn').forEach(r=>{$('circle',r).setAttribute('fill','#fff');$('circle',r).setAttribute('stroke','#d3dce8');const ts=$$('text',r);ts[0].setAttribute('fill','#9fb3c8');ts[1].setAttribute('fill','#121a27')});$('#rcN').textContent='6';$('#rcT').textContent='단계 순환';$('#rcS').textContent='돌 때마다 attempts에 기록이 쌓인다';panel(-1,true)},
  run(k,inst){setRing(k-1,inst);panel(k-1,inst)}};
})();

// --- 7 출제: 켄 번스
const KB=[['xdr-build','학습지 만들기 3단계','유형 → 문항 확인 → 디자인 · 배포',{s:1.55,x:-2,y:-4}],
 ['book-problem','교재 만들기','개념 · 유형 · 서술형, 쪽마다 QR',{s:1.25,x:-8,y:-30}],
 ['mock-cover','모의고사','평가원식 표지 · 배점 · 회차 관리',{s:1.15,x:-6,y:-12}],
 ['xdr-dash','배포 · 한글 편집','반에 바로 배포 · 한글 파일 편집',{s:1.4,x:-20,y:-6}]];
(()=>{$('#kbList').innerHTML=KB.map((k,i)=>`<div class="card kbi" data-i="${i}" ${B(0,'right',i*90)} style="padding:16px 18px;transition:border-color .25s,background .25s"><div style="display:flex;gap:12px;align-items:baseline"><span class="big" style="font-size:30px;color:#b9c8da" data-n>${i+1}</span><div><h3 style="font-size:24px;margin-bottom:4px">${k[1]}</h3><p style="font-size:19px;line-height:1.5;color:var(--ink2)">${k[2]}</p></div></div></div>`).join('');
 const img=$('#kbImg');const kb=(i,inst)=>{const k=KB[i];$$('.kbi').forEach((c,j)=>{c.style.borderColor=j===i?'#2f7fd0':'';c.style.background=j===i?'#f5f9ff':'';$('[data-n]',c).style.color=j===i?'#2f7fd0':'#b9c8da'});
  const go=()=>{const z=k[3];img.getAnimations().forEach(a=>a.cancel());if(inst||RM){img.style.transform=`scale(${z.s}) translate(${z.x}%,${z.y}%)`;return}img.animate([{transform:'scale(1) translate(0,0)'},{transform:`scale(${z.s}) translate(${z.x}%,${z.y}%)`}],{duration:5200,easing:'cubic-bezier(.33,0,.2,1)',fill:'forwards'})};
  if(img.dataset.src!==k[0]){if(!inst&&!RM){const g=ghostOf(img,rel(img));g.style.objectFit='cover';g.style.objectPosition='top left';g.animate([{opacity:1},{opacity:0}],{duration:450,easing:EZ,fill:'forwards'}).onfinish=()=>g.remove()}img.src='img/app/'+k[0]+'.webp';img.dataset.src=k[0];img.style.transform='none'}go()};
 HOOK.kb={n:4,reset(){img.getAnimations().forEach(a=>a.cancel());img.src='img/app/xdr-build.webp';img.dataset.src='xdr-build';img.style.transform='none';$$('.kbi').forEach(c=>{c.style.borderColor='';c.style.background='';$('[data-n]',c).style.color='#b9c8da'})},run(k,inst){kb(k-1,inst)}};
})();

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

// --- 9 히트맵
const CT=window.CMTYPES||[];const CLS=['1반','2반','3반','4반','5반','6반'];seed=20261125;
const HEAT=CLS.map((c,ci)=>{const ce=(rnd()-.5)*.12;const weak=new Set([Math.floor(rnd()*40),Math.floor(rnd()*40),Math.floor(rnd()*40)]);return CT.map((t,ti)=>{const base=.82-(ti%7)*.035-(t[2]==='세포호흡'?.08:t[2]==='광합성'?.05:0);let p=base+ce+(rnd()-.5)*.18-(weak.has(ti)?.28:0);p=Math.max(.18,Math.min(.97,p));const n=380+Math.floor(rnd()*260);return {p,n,r:Math.round(p*n)}})});
const hcol=p=>p<.5?`rgba(216,68,59,${.38+(.5-p)*1.3})`:p<.75?`rgba(224,156,18,${.3+(.75-p)*1.6})`:`rgba(23,149,106,${.22+(p-.75)*2.4})`;
(()=>{const H=$('#heat');H.style.gridTemplateColumns=`52px repeat(${CT.length},1fr)`;
 H.innerHTML=`<div></div>`+CT.map((t,i)=>`<div class="src" style="font-size:11px;text-align:center">${i%5===0?i+1:''}</div>`).join('')+HEAT.map((row,ci)=>`<div class="rh">${CLS[ci]}</div>`+row.map((c,ti)=>`<div class="c" data-c="${ci}" data-t="${ti}" style="background:${hcol(c.p)}"></div>`).join('')).join('')+
 `<div></div><div style="grid-column:2/-1;display:flex;justify-content:space-between;margin-top:10px" class="src">${[...new Set(CT.map(t=>t[2]))].map(u=>`<span>${esc(u)} (${CT.filter(t=>t[2]===u).length})</span>`).join('')}</div>`;
 $('#heatAvg').innerHTML=HEAT.map((row,ci)=>{const n=row.reduce((s,c)=>s+c.n,0),r=row.reduce((s,c)=>s+c.r,0);return `<div class="tile" style="padding:12px 14px" ${B(0,'rise',900+ci*60)}><span class="lab">${CLS[ci]} 평균</span><span class="big" style="font-size:34px"><span data-count="${Math.round(r/n*100)}">${Math.round(r/n*100)}</span>%</span><span class="src">풀이 ${fmt(n)}건</span></div>`}).join('');
 let m=[1,0,0];HEAT.forEach((row,ci)=>row.forEach((c,ti)=>{if(c.p<m[0])m=[c.p,ci,ti]}));const [,wc,wt]=m;
 const info=()=>{const c=HEAT[wc][wt],t=CT[wt];const rank=HEAT[wc].map((x,k)=>[x.p,k]).sort((a,b)=>a[0]-b[0]).slice(0,3);
  $('#heatInfo').innerHTML=`<span class="lab">${CLS[wc]} · ${esc(t[2])} · 가장 약한 칸</span><h3 style="font-size:23px;margin:4px 0 6px">${esc(t[3])}</h3><div style="display:flex;align-items:baseline;gap:14px"><span class="big" style="font-size:72px;color:var(--r)">${Math.round(c.p*100)}%</span><span style="font-size:17px;color:var(--ink2)">정답 ${fmt(c.r)} / 풀이 ${fmt(c.n)}<br>처방 <b style="color:var(--r)">개념부터 다시</b></span></div><div class="lab" style="margin-top:10px">${CLS[wc]} 취약 유형 TOP 3 → 반 공통 학습지</div>${rank.map(([p,k],j)=>`<div class="wi" style="margin-bottom:5px"><span><b>${j+1}</b> ${esc(CT[k][3])}</span><b style="color:var(--r)">${Math.round(p*100)}%</b></div>`).join('')}`};info();
 // 곡선(시뮬레이션 모델)
 const rounds=[0,1,2,3,4],weakP=[38];for(let i=1;i<5;i++)weakP.push(weakP[i-1]+.35*(85-weakP[i-1]));const other=[76,77,77.5,78,78.4];
 const X=r=>70+r*110,Y=v=>200-(v-20)/80*180;let g='';[20,40,60,80,100].forEach(v=>{g+=`<line x1="60" x2="530" y1="${Y(v)}" y2="${Y(v)}" stroke="#edf1f6"/>`+T(52,Y(v)+5,v,{a:'end',fs:12,c:'#8a96a6'})});
 rounds.forEach(r=>g+=T(X(r),226,r?`${r}회`:'진단',{a:'middle',fs:13,fw:700}));
 g+=`<path d="M${rounds.map(r=>X(r)+' '+Y(other[r])).join(' L')}" fill="none" stroke="#b9c8da" stroke-width="3" stroke-dasharray="6 6" ${B(2,'fade',200)}/>`+T(X(4)+8,Y(other[4])-8,'다른 유형',{fs:13,fw:700,c:'#8a96a6',b:2,d:400});
 g+=`<path d="M${rounds.map(r=>X(r)+' '+Y(weakP[r])).join(' L')}" fill="none" stroke="#d8443b" stroke-width="5" stroke-linecap="round" ${B(2,'draw',300,'data-dur="1200"')}/>`;rounds.forEach(r=>{g+=`<circle cx="${X(r)}" cy="${Y(weakP[r])}" r="7" fill="#fff" stroke="#d8443b" stroke-width="4" ${B(2,'pop',400+r*220)}/>`});
 g+=T(X(0)+10,Y(weakP[0])+22,Math.round(weakP[0])+'%',{fs:15,fw:800,c:'#d8443b',b:2,d:400})+T(X(4)-4,Y(weakP[4])-14,Math.round(weakP[4])+'%',{a:'end',fs:18,fw:900,c:'#17956a',b:2,d:1400});
 $('#ch-curve').innerHTML=sv(560,240,g);
 HOOK.heat={n:2,reset(){$$('#heat .c').forEach(c=>{c.style.opacity='0';c.classList.remove('pick')});$$('#heat .rh').forEach(r=>r.style.opacity='')},
  enter(inst){const cells=$$('#heat .c');cells.forEach(c=>{c.style.opacity='1';if(!inst&&!RM){const d=(+c.dataset.t+ +c.dataset.c*3)*14;c.animate([{opacity:0},{opacity:1}],{duration:500,delay:d*.6,easing:EZ,fill:'backwards'})}})},
  run(k,inst){if(k===1){const cell=$(`#heat .c[data-c="${wc}"][data-t="${wt}"]`);$$('#heat .c').forEach(c=>{if(+c.dataset.c!==wc)c.style.opacity='.25'});cell.classList.add('pick');if(!inst&&!RM){setTimeout(()=>morphBox(rel(cell),$('#heatInfo'),{background:hcol(HEAT[wc][wt].p)},600),250)}}}};
})();

// --- 11 휴대폰 부채꼴
(()=>{const P=[['phone-omr','OMR 채점',-9],['phone-result','채점 결과',-3],['phone-weak','취약 유형',3],['phone-parent','학부모 홈',9]];
 $('#phones').innerHTML=P.map((p,i)=>`<figure style="position:absolute;left:${115+i*380}px;top:${i%2?40:0}px;text-align:center" class="ph-f" data-i="${i}"><div class="phone" style="width:250px"><img src="img/app/${p[0]}.webp" alt=""></div><figcaption style="font-size:20px;font-weight:800;margin-top:14px">${p[1]}</figcaption></figure>`).join('');
 HOOK.phones={n:1,reset(){$$('.ph-f').forEach(f=>f.style.opacity='0')},enter(inst){$$('.ph-f').forEach((f,i)=>{f.style.opacity='1';if(!inst&&!RM)f.animate([{opacity:0,transform:'translateY(40px)'},{opacity:1,transform:'none'}],{duration:800,delay:i*90,easing:EZ,fill:'backwards'})})}};
})();

// --- 12 꿈두레 대응 + ERD
(()=>{const MAP=[['꿈두레','기본키(PK)','모든 표 · 복합키 class_members'],['꿈두레','외래키 · 무결성','외래키 51개 · CASCADE / SET NULL'],['꿈두레','정규화','학생 ↔ 반 N:M → 연결 표'],['꿈두레','JOIN','학습지 · 채점 · 학생 조인'],['꿈두레','GROUP BY · HAVING','유형별 정답률 · 반복 오답'],['확장','윈도 함수','최근 6회 · 취약 TOP3'],['확장','함수 · 트리거','함수 92개 · 감사 기록'],['확장','행 수준 보안','정책 76개 · 학원별 분리']];
 $('#kmap').innerHTML=MAP.map((m,i)=>`<div style="display:grid;grid-template-columns:200px 34px 1fr;align-items:stretch;gap:0" ${B(0,'left',i*80)}><div class="card" style="padding:9px 13px;${m[0]==='확장'?'background:#f6f8fb':''}"><span class="lab" style="display:block;margin:0 0 2px;color:${m[0]==='꿈두레'?'var(--b)':'var(--mut)'}">${m[0]==='꿈두레'?'꿈두레에서 배움':'연구 중 확장'}</span><b style="font-size:17.5px">${m[1]}</b></div><div style="display:grid;place-items:center;color:var(--b);font-weight:900">→</div><div class="card" style="padding:9px 16px;font-size:19px;font-weight:600;line-height:1.4;display:flex;align-items:center;border-color:#cfe0f3;background:#f7fbff">${m[2]}</div></div>`).join('');
 const E={auth:[40,40,'교사 계정','auth.users',1,1],set:[330,40,'학원 설정','teacher_settings',1,0],stu:[330,290,'학생','students',1,0],ws:[620,40,'학습지','worksheets',1,0],att:[620,290,'채점 기록','attempts',1,0],qb:[880,290,'문항(JSON)','question_bank',1,1],asg:[620,520,'과제 배정','assignments',1,0],wn:[880,520,'오답 메모','wrong_notes',1,0],cls:[40,520,'반','classes',2,0],cm:[40,290,'반 소속','class_members',2,0],pa:[330,560,'학부모 계정','parent_accounts',2,0],atd:[200,620,'출결','attendance',2,0]};
 const R=[['auth','set','1','1',1],['auth','stu','1','n',1],['stu','ws','1','n',1],['stu','att','1','n',1],['ws','att','1','n',1,1],['att','qb','m','n',1,1],['stu','asg','1','n',1],['stu','wn','1','n',1],['wn','qb','n','1',1,1],['cls','cm','1','n',2],['stu','cm','1','n',2],['stu','pa','1','n',2],['stu','atd','1','n',2]];
 const W=150,H=56,c=k=>[E[k][0]+W/2,E[k][1]+H/2];let g='';
 R.forEach(([a,b,ca,cb,bb,lg],i)=>{const [x1,y1]=c(a),[x2,y2]=c(b),mx=(x1+x2)/2,my=(y1+y2)/2;g+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#555" stroke-width="1.6" ${lg?'stroke-dasharray="7 5"':''} ${B(bb,lg?'fade':'draw',200+i*40,'data-dur="600"')}/>`;
  g+=`<g ${B(bb,'pop',450+i*40)} style="transform-origin:${mx}px ${my}px;transform-box:view-box"><polygon points="${mx-24},${my} ${mx},${my-14} ${mx+24},${my} ${mx},${my+14}" fill="#f7b58e" stroke="#e08a5a"/></g>`+T(x1+(x2-x1)*.22+6,y1+(y2-y1)*.22-7,ca,{fs:15,fw:800,c:'#222',b:bb,d:600})+T(x1+(x2-x1)*.78+6,y1+(y2-y1)*.78-7,cb,{fs:15,fw:800,c:'#222',b:bb,d:600})});
 Object.entries(E).forEach(([k,[x,y,ko,en,bb,v]])=>{g+=`<g id="er-${k}" ${B(bb,'pop',(k.length%4)*60)} style="transform-origin:${x+W/2}px ${y+H/2}px;transform-box:view-box"><rect x="${x}" y="${y}" width="${W}" height="${H}" rx="4" fill="${v?'#f4f5f6':'#e6e8eb'}" stroke="#8c939c" stroke-width="1.4" ${v?'stroke-dasharray="5 4"':''}/>${T(x+W/2,y+25,ko,{a:'middle',fs:17,fw:800,c:'#2a2f36'})}${T(x+W/2,y+43,en,{a:'middle',fs:11.5,c:'#6b7480'})}</g>`});
 const [cmx,cmy]=c('cm');g+=`<g ${B(3,'pop',0)}><circle cx="${cmx}" cy="${cmy}" r="96" fill="none" stroke="#fdc62d" stroke-width="5"/><rect x="${cmx-20}" y="${cmy+100}" width="290" height="58" rx="10" fill="#0d387e"/>${T(cmx-6,cmy+124,'학생 ↔ 반 = N:M',{fs:17,fw:900,c:'#fdc62d'})}${T(cmx-6,cmy+146,'→ 연결 표 class_members(복합키)',{fs:14,fw:700,c:'#fff'})}</g>`;
 $('#erd').innerHTML=g;
 HOOK.kkum={n:3,run(k,inst){if(k===3&&!inst&&!RM){}}};
})();

// --- 15 라즈베리파이 구조
(()=>{const A=$('#arch');const BX={web:[0,20,250,96,'브라우저','학생 휴대폰 · 교사 PC'],pages:[0,300,250,96,'GitHub Pages','앱 화면 · 문제은행 JSON'],tun:[330,20,250,96,'HTTPS 터널','Tailscale Funnel / DuckDNS'],caddy:[700,20,250,96,'Caddy','게이트웨이 · CORS · /health'],rest:[700,190,250,90,'PostgREST','/rest/v1 · SQL 함수 호출'],auth:[700,330,250,90,'GoTrue','/auth/v1 · 교사 로그인'],pk:[700,470,250,90,'Deno','/functions/v1/passkey'],db:[330,330,270,140,'PostgreSQL 15','표 36 · 함수 92 · RLS 76 · USB SSD']};
 const AL=[['web','tun'],['tun','caddy'],['web','pages'],['caddy','rest'],['rest','auth'],['auth','pk'],['rest','db'],['auth','db'],['pk','db']];const cc=k=>{const b=BX[k];return [b[0]+b[2]/2,b[1]+b[3]/2]};
 let s=`<svg width="980" height="640" style="position:absolute;left:0;top:0;overflow:visible" id="archSvg">${AL.map(([a,b],i)=>{const [x1,y1]=cc(a),[x2,y2]=cc(b);return `<path id="al${i}" d="M${x1} ${y1} L${x2} ${y2}" stroke="#c3d1e3" stroke-width="3" fill="none" ${B(0,'draw',300+i*80,'data-dur="500"')}/>`}).join('')}<g id="parts"></g></svg>`;
 s+=`<div style="position:absolute;left:300px;top:150px;width:690px;height:450px;border:2.5px dashed #9fb3c8;border-radius:20px" ${B(0,'fade',100)}></div><div style="position:absolute;left:320px;top:162px;font:800 15px Pretendard;color:var(--navy)" ${B(0,'fade',200)}>라즈베리파이 5 · 2GB · Docker Compose</div>`;
 s+=Object.entries(BX).map(([k,b],i)=>`<div class="box ${k==='db'?'pi':''}" id="ab-${k}" style="left:${b[0]}px;top:${b[1]+(k==='tun'||k==='caddy'||k==='web'?0:0)}px;width:${b[2]}px;height:${b[3]}px" ${B(0,'pop',i*70)}><h4>${b[4]}</h4><p>${b[5]}</p></div>`).join('')+`<div id="pkt" style="position:absolute;width:26px;height:26px;border-radius:50%;background:#ef7d3c;box-shadow:0 0 0 7px rgba(239,125,60,.25);opacity:0;z-index:5;left:0;top:0"></div>`;
 A.innerHTML=s;
 // 흐르는 입자
 let raf=0;const parts=$('#parts');const P=[];AL.forEach((l,i)=>{for(let j=0;j<2;j++){const c=document.createElementNS(NS,'circle');c.setAttribute('r','3.5');c.setAttribute('fill','#2f7fd0');parts.appendChild(c);P.push({c,i,t:Math.random()})}});
 const loop=()=>{P.forEach(p=>{const path=$('#al'+p.i);const L=path.getTotalLength();p.t=(p.t+0.004)%1;const pt=path.getPointAtLength(p.t*L);p.c.setAttribute('cx',pt.x);p.c.setAttribute('cy',pt.y)});raf=requestAnimationFrame(loop)};
 const TR={1:[['web','학생 휴대폰: POST /rest/v1/rpc/st_submit'],['tun','HTTPS 터널 통과'],['caddy','Caddy: /rest/v1 → PostgREST'],['rest','PostgREST: JWT 확인, 함수 호출'],['db','st_submit → attempts에 1행 INSERT'],['rest','204 응답'],['web','채점 완료 화면 · 축하']],
  2:[['web','교사: POST /auth/v1/token'],['tun','HTTPS 터널 통과'],['caddy','Caddy: /auth/v1 → GoTrue'],['auth','GoTrue: 비밀번호 해시 확인'],['db','auth.users 조회'],['auth','JWT 발급(HS256, gen-keys.sh의 비밀키)'],['web','로그인 완료']]};
 let tok=0;async function trace(k,inst){const path=TR[k];const my=++tok;const log=$('#traceLog');log.innerHTML='';const p=$('#pkt');
  if(inst||RM){log.innerHTML=path.map((s,i)=>`<div><b style="color:var(--o)">${i+1}</b> ${esc(s[1])}</div>`).join('');return}p.style.opacity='1';
  for(let i=0;i<path.length;i++){if(my!==tok)return;const [id,t]=path[i];const b=BX[id];$$('#arch .box').forEach(x=>x.classList.remove('hot'));$('#ab-'+id).classList.add('hot');p.style.transition='transform .42s cubic-bezier(.23,1,.32,1)';p.style.transform=`translate(${b[0]+b[2]-30}px,${b[1]+10}px)`;
   const d=document.createElement('div');d.innerHTML=`<b style="color:var(--o)">${i+1}</b> ${esc(t)}`;log.appendChild(d);d.animate(FX.right,{duration:300,easing:EZ});await wait(560)}
  $$('#arch .box').forEach(x=>x.classList.remove('hot'));p.style.opacity='0'}
 HOOK.pi={n:3,reset(){tok++;$('#traceLog').textContent='다음 버튼을 누르면 요청이 흐릅니다';$('#pkt').style.opacity='0';$$('#arch .box').forEach(x=>x.classList.remove('hot'))},
  run(k,inst){if(k<3)trace(k,inst)}};
 const MEM=[['db',600,'#0d387e'],['passkey',200,'#2f7fd0'],['auth',150,'#5a8fd6'],['rest',150,'#8fb3e6'],['gateway',60,'#b9cdea'],['여유',888,'#eef2f7']];let x=0,g='';
 MEM.forEach((m,i)=>{const w=m[1]/2048*470;g+=`<rect x="${x}" y="8" width="${w-2}" height="40" rx="5" fill="${m[2]}" ${B(3,'growx',i*120)} style="transform-origin:${x}px 0;transform-box:view-box"/>`;if(w>40)g+=T(x+6,33,m[0],{fs:13,fw:800,c:i<2?'#fff':'#121a27',b:3,d:200+i*120});if(i===0||i===5)g+=T(x+4,72,(i===5?'여유 ':'')+m[1]+'MB',{fs:14,fw:700,c:'#6c778a',b:3,d:300+i*120});x+=w});
 g+=T(470,72,'한도 합계 1,160MB',{a:'end',fs:14,fw:800,c:'#0d387e',b:3,d:900});$('#ch-mem').innerHTML=sv(470,80,g);
})();

// --- 16 검증 차트 · 점
(()=>{const AU=[['물질과 에너지',13943,'verify.py'],['화법과 언어',13258,'audit.py --all'],['인공지능 수학',14400,'독립 풀이 대조']];let g='';const mx=15000;
 AU.forEach((a,i)=>{const y=30+i*150,w=a[1]/mx*620;g+=T(0,y+16,a[0],{fs:18,fw:800,c:'#121a27'})+T(180,y+16,a[2],{fs:13,c:'#6c778a'})+`<rect x="0" y="${y+28}" width="${w}" height="38" rx="7" fill="#2f7fd0" ${B(0,'growx',i*180)} style="transform-origin:0 0;transform-box:view-box"/>`+T(14,y+53,`<tspan data-count="${a[1]}">${fmt(a[1])}</tspan>문항`,{fs:17,fw:800,c:'#fff',b:0,d:200+i*180});
  g+=`<g ${B(0,'pop',700+i*180)} style="transform-origin:${w+70}px ${y+47}px;transform-box:view-box"><circle cx="${w+70}" cy="${y+47}" r="34" fill="#fff" stroke="#17956a" stroke-width="4"/>${T(w+70,y+44,'오류',{a:'middle',fs:12,fw:800,c:'#17956a'})}${T(w+70,y+62,'0',{a:'middle',fs:20,fw:900,c:'#17956a',ff:'Paperlogy'})}</g>`});
 $('#ch-audit').innerHTML=sv(780,470,g);
 $('#dots').innerHTML=Array.from({length:50},(_,i)=>`<i style="display:block;aspect-ratio:1;border-radius:50%;background:${['#0d387e','#2f7fd0','#5a8fd6'][i%3]}" class="dt"></i>`).join('');
 HOOK.verify={n:2,reset(){$$('#dots .dt').forEach(d=>d.style.opacity='0')},run(k,inst){if(k===1)$$('#dots .dt').forEach((d,i)=>{d.style.opacity='1';if(!inst&&!RM)d.animate([{opacity:0,transform:'scale(.6)'},{opacity:1,transform:'none'}],{duration:500,delay:150+((i%25)+Math.floor(i/25)*3)*18,easing:EZ,fill:'backwards'})})},edit(){$$('#dots .dt').forEach(d=>d.style.opacity='1')}};
})();

/* ---------- 도넛 조각 그리기 효과(전용) ---------- */
const _show=show;
function showX(el,inst){if(el.dataset&&el.dataset.fx==='seg'){el.classList.add('shown');if(inst||RM)return;const len=+el.dataset.len,C=2*Math.PI*150;el.animate([{strokeDasharray:`0 ${C}`},{strokeDasharray:`${len} ${C-len}`}],{duration:700,delay:+el.dataset.d||0,easing:EIO,fill:'backwards'});return}_show(el,inst)}

/* ---------- 단계 진행 엔진 ---------- */
const maxB=s=>Math.max(0,...$$('[data-b]',s).map(e=>+e.dataset.b));
const steps=i=>Math.max(maxB(slides[i]),(H(i)&&H(i).n)||0);
function stepEls(i,k){return $$(`[data-b="${k}"]`,slides[i])}
function resetSlide(i){$$('[data-b]',slides[i]).forEach(e=>{e.classList.remove('shown');e.getAnimations&&e.getAnimations().forEach(a=>a.cancel())});H(i)&&H(i).reset&&H(i).reset()}
function enterSlide(i,inst){stepEls(i,0).forEach(e=>showX(e,inst));H(i)&&H(i).enter&&H(i).enter(inst)}
function doStep(i,k,inst){stepEls(i,k).forEach(e=>showX(e,inst));H(i)&&H(i).run&&H(i).run(k,inst)}
async function replayTo(i,k){resetSlide(i);enterSlide(i,true);for(let j=1;j<=k;j++){stepEls(i,j).forEach(e=>showX(e,true));if(H(i)&&H(i).run){const r=H(i).run(j,true);if(r&&r.then)await r}}step=k;hud()}
let busy=false;
async function next(){if(busy)return;const n=steps(cur);if(step<n){step++;hud();busy=true;stepEls(cur,step).forEach(e=>showX(e,false));const r=H(cur)&&H(cur).run&&H(cur).run(step,false);if(r&&r.then){const to=setTimeout(()=>busy=false,8000);try{await r}finally{clearTimeout(to);busy=false}}else setTimeout(()=>busy=false,150)}else{busy=true;await go(cur+1);setTimeout(()=>busy=false,200)}}
async function prev(){if(step>0){await replayTo(cur,step-1)}else if(cur>0){go(cur-1,true)}}
function hud(){const n=steps(cur);$('#stepi').textContent=n?`단계 ${step}/${n}`:'';$('#pg').textContent=`${cur+1} / ${slides.length}`;$('#bar i').style.width=((cur+(n?step/n:1))/slides.length*100)+'%';
 $$('.ft .pg').forEach((p,i)=>p.textContent=String(i+1).padStart(2,'0')+' / '+slides.length)}

/* ---------- 슬라이드 전환 ---------- */
let booted=false;
function enterSeq(nw){const h=$('h2',nw),k=$('.kick',nw);
 if(k)k.animate([{opacity:0,transform:'translateX(-10px)'},{opacity:1,transform:'none'}],{duration:520,delay:40,easing:EZ,fill:'backwards'});
 if(h)h.animate([{clipPath:'inset(0 0 100% 0)',transform:'translateY(26px)'},{clipPath:'inset(0 0 -20% 0)',transform:'none'}],{duration:720,delay:90,easing:EZ,fill:'backwards'});
 let n=0;$$('.body>*, .ft',nw).forEach(el=>{if(el.matches('[data-b]')||el.closest('[data-b]'))return;el.animate(FX.rise,{duration:640,delay:240+Math.min(n++,6)*60,easing:EZ,fill:'backwards'})})}
async function go(i,toEnd){i=Math.max(0,Math.min(slides.length-1,i));if(i===cur&&booted&&!toEnd)return;const old=slides[cur],nw=slides[i];const anim=booted&&isShow()&&!RM&&old!==nw;const prevI=cur;
 H(cur)&&H(cur).leave&&H(cur).leave();$$('.ghost',stage).forEach(g=>g.remove());
 const logoMorph=false;let lg=null;
 if(logoMorph){const e=$('#coverLogo');lg={el:e,r:rel(e)}}
 if(anim&&!logoMorph){await old.animate([{opacity:1,transform:'none'},{opacity:0,transform:'translateY(-8px)'}],{duration:220,easing:EXIT,fill:'forwards'}).finished.catch(()=>{});}
 old.getAnimations().forEach(a=>a.cancel());old.classList.remove('on');cur=i;nw.classList.add('on');step=0;
 $$('#side button').forEach((b,k)=>b.classList.toggle('cur',k===cur));const cb=$$('#side button')[cur];cb&&cb.scrollIntoView({block:'nearest'});
 $('#notes').innerHTML=`<b>${cur+1}. ${esc(nw.dataset.title)}</b> · 권장 ${nw.dataset.time||''} · 단계 ${steps(cur)}<br>${esc(nw.dataset.notes||'')}`;
 try{history.replaceState(null,'','#'+(cur+1))}catch(e){}
 if(!isShow()||toEnd){await replayTo(cur,steps(cur));hud();if(!isShow())editSync();booted=true;return}
 resetSlide(cur);
 if(logoMorph){old.classList.add('on');old.style.zIndex=0;nw.style.zIndex=1;nw.animate([{clipPath:'circle(0% at 88% 14%)'},{clipPath:'circle(150% at 88% 14%)'}],{duration:900,easing:EIO});setTimeout(()=>{old.classList.remove('on');old.style.zIndex='';nw.style.zIndex=''},900);
  const to=$('.brand',nw);if(to){const g=ghostOf(lg.el,lg.r);morphPair(g,lg.r,to,rel(to),900)}}
 if(anim)enterSeq(nw);
 enterSlide(cur,!anim&&!isShow());hud();booted=true}

/* ---------- 편집 모드 ---------- */
const SEL='h1,h2,h3,h4,p,figcaption,li,td,th,.kick,.lab,.t,.fb,.ft>span:first-child,.meta div';
const EDS=slides.map(s=>{const all=$$(SEL,s).filter(e=>!e.closest('svg,#demo,#heatInfo,#lpanel,#kbList,#mosaic,#phones,#kmap,#code,#traceLog,#codeAna,#dots,#heat,#heatAvg'));return all.filter(e=>!all.some(o=>o!==e&&o.contains(e)))});
let edits={};try{const emb=document.getElementById('ppt-edits');if(emb)edits=JSON.parse(emb.textContent||'{}')}catch(e){}
try{const ls=JSON.parse(localStorage.getItem(KEY)||'null');if(ls&&ls.v)edits=Object.assign({},edits,ls.v)}catch(e){}
EDS.forEach((l,si)=>l.forEach((e,k)=>{e.dataset.ek=si+':'+k;const v=edits[si+':'+k];if(v!=null)e.innerHTML=v}));
let editing=true;
function editSync(){const on=editing&&!isShow();document.body.classList.toggle('editing',on);EDS.flat().forEach(e=>on?e.setAttribute('contenteditable','true'):e.removeAttribute('contenteditable'));$('#bEdit').classList.toggle('on',editing)}
let sT;document.addEventListener('input',ev=>{const e=ev.target.closest&&ev.target.closest('[data-ek]');if(!e)return;edits[e.dataset.ek]=e.innerHTML;clearTimeout(sT);$('#saved').textContent='저장 중…';sT=setTimeout(()=>{try{localStorage.setItem(KEY,JSON.stringify({v:edits}));$('#saved').textContent='자동 저장됨'}catch(err){$('#saved').textContent='이 브라우저에 저장 못 함 — HTML로 저장하세요'}},300)});
document.addEventListener('paste',ev=>{if(!ev.target.closest||!ev.target.closest('[data-ek]'))return;ev.preventDefault();document.execCommand('insertText',false,(ev.clipboardData||window.clipboardData).getData('text/plain'))});
$('#bEdit').onclick=()=>{editing=!editing;editSync()};$('#bB').onclick=()=>document.execCommand('bold');$('#bHl').onclick=()=>document.execCommand('foreColor',false,'#2f7fd0');$('#bUndo').onclick=()=>document.execCommand('undo');
$('#bReset').onclick=()=>{if(!confirm('이 슬라이드에서 고친 글자를 원래대로 돌릴까요?'))return;EDS[cur].forEach(e=>edits[e.dataset.ek]=null);try{localStorage.setItem(KEY,JSON.stringify({v:edits}))}catch(e){}location.reload()};
$('#bSave').onclick=()=>{const clean={};Object.entries(edits).forEach(([k,v])=>{if(v!=null)clean[k]=v});let html=ORIGINAL.replace(/<script id="ppt-edits"[^>]*>[\s\S]*?<\/script>\n?/,'');html=html.replace('<script src="lib/qrcode.js">',`<script id="ppt-edits" type="application/json">${JSON.stringify(clean).replace(/</g,'\\u003c')}</script>\n<script src="lib/qrcode.js">`).replace(/<body class="[^"]*"/,'<body class="edit"');
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([html],{type:'text/html'}));a.download='solvi-presentation.html';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000);$('#saved').textContent='내려받은 파일을 이 폴더(fonts · img · lib 옆)에 덮어쓰세요'};

/* ---------- 목록 · 모드 · 키 ---------- */
$('#side').innerHTML=slides.map((s,i)=>`<button data-i="${i}"><i>${i+1}</i><span>${esc(s.dataset.title)}<small>${s.dataset.time||''} · 단계 ${steps(i)}</small></span></button>`).join('');
$('#side').onclick=e=>{const b=e.target.closest('button');if(b)go(+b.dataset.i)};
let t0=Date.now();
function startShow(){document.body.classList.remove('edit');document.body.classList.add('show');editSync();document.activeElement&&document.activeElement.blur();t0=Date.now();document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen().catch(()=>{});fit();booted=false;const c=cur;cur=c;go(c);setTimeout(fit,80)}
function endShow(){document.body.classList.remove('show');document.body.classList.add('edit');$('#notes').classList.remove('on');$('#blk').classList.remove('on');if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});fit();go(cur,true);editSync();setTimeout(fit,80)}
document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement&&isShow())endShow();setTimeout(fit,60)});
$('#bShow').onclick=startShow;$('#hX').onclick=endShow;$('#hN').onclick=()=>$('#notes').classList.toggle('on');$('#hH').onclick=()=>$('#help').classList.toggle('on');
const toggleOv=()=>{const o=$('#ov');o.classList.toggle('on');o.innerHTML=slides.map((s,i)=>`<button class="th ${i===cur?'cur':''}" data-i="${i}"><small>${i+1} · ${s.dataset.time||''}</small>${esc(s.dataset.title)}</button>`).join('')};
$('#hO').onclick=toggleOv;$('#ov').onclick=e=>{const b=e.target.closest('.th');if(b){$('#ov').classList.remove('on');go(+b.dataset.i)}};
setInterval(()=>{const s=Math.floor((Date.now()-t0)/1000);const el=$('#timer');el.textContent=String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');el.className=s>=900?'over':s>=780?'warn':''},500);
const NEXT=['ArrowRight','ArrowDown','PageDown',' ','Enter','MediaTrackNext'],PREV=['ArrowLeft','ArrowUp','PageUp','Backspace','MediaTrackPrevious'];
document.addEventListener('keydown',e=>{const inEd=e.target.closest&&e.target.closest('[contenteditable=true],input,select,textarea');
 if(e.key==='Escape'){if(inEd){e.target.blur();return}if($('#ov').classList.contains('on')){$('#ov').classList.remove('on');return}if(isShow())endShow();return}
 if(inEd)return;
 if(e.key==='F5'||(e.shiftKey&&e.key==='F5')){e.preventDefault();isShow()?null:startShow();return}
 if($('#blk').classList.contains('on')&&!['b','B','.','w','W'].includes(e.key)){$('#blk').classList.remove('on');e.preventDefault();return}
 if(NEXT.includes(e.key)){e.preventDefault();isShow()?next():go(cur+1);return}
 if(PREV.includes(e.key)){e.preventDefault();isShow()?prev():go(cur-1);return}
 const k=e.key.toLowerCase();
 if(k==='b'||k==='.'||k==='w'){$('#blk').style.background=k==='w'?'#fff':'#000';$('#blk').classList.toggle('on')}
 else if(k==='s')$('#notes').classList.toggle('on');else if(k==='o')toggleOv();else if(k==='t')t0=Date.now();else if(k==='?')$('#help').classList.toggle('on');
 else if(k==='e'&&!isShow()){editing=!editing;editSync()}else if(e.key==='Home')go(0);else if(e.key==='End')go(slides.length-1);
 else if(k==='f'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen().catch(()=>{})}});
stage.addEventListener('click',e=>{if(!isShow())return;if(e.target.closest('button,a'))return;next()});
let tx=null;stage.addEventListener('touchstart',e=>{tx=[e.touches[0].clientX,e.touches[0].clientY]},{passive:true});
stage.addEventListener('touchend',e=>{if(!tx||!isShow())return;const dx=e.changedTouches[0].clientX-tx[0],dy=e.changedTouches[0].clientY-tx[1];tx=null;if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)*1.5){e.preventDefault();dx<0?next():prev()}});
stage.addEventListener('contextmenu',e=>{if(isShow()){e.preventDefault();prev()}});
$('#blk').addEventListener('click',()=>$('#blk').classList.remove('on'));

/* ---------- 시작 ---------- */
fit();const h0=parseInt(location.hash.slice(1));go(h0>0?h0-1:0,true);editSync();
})();
