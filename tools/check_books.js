// 교재 쪽 자동 검사.  node tools/check_books.js [책 번호...]  (python3 server.py 가 8765에서 실행 중이어야 함)
// 책마다 bkDocHtml(plan,true)를 실제로 그린 뒤 쪽마다 아래를 검사하고 books/check.json 에 위반 목록을 남긴다.
//  overflow  열·본문 넘침(잘림)          orphan  열·쪽 바닥에 제목만 남음(또는 설명만 남고 상자·표는 다음 쪽)
//  gap       열 아래가 20mm 이상 비었는데 다음 단위가 들어갈 수 있음   table  표가 열보다 넓거나 머리글 칸이 줄바꿈됨
//  glyph     글꼴에 없는 옛한글·특수 문자(두부) / CSS 배지로 바꾸지 않은 원문자   qr  QR과 본문 겹침   order  한 쪽 안 문항 번호 순서
// 책 번호를 안 적으면 화법과 언어 주교재(화법·언어·혼합)와 다른 과목 개념서·유형서를 모두 검사한다.
const {chromium}=require(process.env.PW||'/opt/node-tools/node_modules/playwright');const fs=require('fs');const {execFileSync}=require('child_process');
const MM=96/25.4;
function cmapOf(){try{return new Set(JSON.parse(execFileSync('python3',['-c',"import json,sys\nfrom fontTools.ttLib import TTFont\ns=set()\nfor f in sys.argv[1:]:\n s|=set(TTFont(f).getBestCmap())\nprint(json.dumps(sorted(s)))",'fonts/KoPubDotum-Medium.subset.woff2','fonts/Pretendard-Regular.woff2','fonts/Pretendard-Light.cn.woff2','fonts/SolviSymbols.woff2','fonts/KoPubDotum-Bold.subset.woff2'],{maxBuffer:1<<26}).toString()))}catch(e){console.log('(fontTools 없음: 글꼴 결손 검사는 건너뜀)');return null}}
(async()=>{const arg=process.argv.slice(2);const ids=arg.length?arg:['hl-hs','hl-hg','hl-hm','me-c','me-t','cm-c','cm-t'];
 const cmap=cmapOf();
 const b=await chromium.launch(process.env.CHROME?{executablePath:process.env.CHROME}:{});const app=await b.newPage({viewport:{width:1300,height:950}});
 app.on('pageerror',e=>console.log('PAGEERR',String(e)));
 await app.goto((process.env.BASE||'http://localhost:8765/')+'index.html?app=1');await app.waitForTimeout(1500);
 await app.evaluate("sess={access_token:'x',user:{}};STU=[{id:'s1',name:'테스트',grade:'고2'}];CUR_S='s1'");
 const out={when:new Date().toISOString(),books:{},count:{}};
 for(const id of ids){const subj=id.split('-')[0];
  await app.evaluate(`setSubject('${subj}')`);await app.waitForTimeout(500);await app.evaluate('bkLoad()');await app.waitForTimeout(300);
  const r=await app.evaluate(`(async()=>{await bkInit();await conceptLoad();
   // 쪽에 놓인 단위의 높이·keep 정보: bkPack 결과를 HTML 문자열로 찾아 붙인다(모든 쪽 종류 공통)
   if(!window._bkPk0){window._bkPk0=bkPack;window._bkUM=new Map();bkPack=function(...a){const r=window._bkPk0(...a);r.forEach(p=>[...p.cols,p.top||[]].forEach(c=>c.forEach(u=>window._bkUM.set(typeof bkUH==='function'?bkUH(u):u.html,[u.key,u.h,u.keep?1:0,u.brk?1:0,u.code||'']))));return r}}
   window._bkUM.clear();const pl0=BKP['${id}'];delete BKP['${id}'];const plan=await bkPlan('${id}');if(!plan)return null;
   const sh=bkSheets(plan,true),M=h=>window._bkUM.get(h)||null;
   return {html:bkDocHtml(plan,true),sheets:sh,pages:plan.pages.map(p=>({n:p.n,k:p.k,label:p.label||'',sub:p.sub&&p.sub.k||'',um:p.cols?p.cols.map(c=>c.map(M)):null,tm:p.top?p.top.map(M):null}))}})()`);
  if(!r){console.log(id,'계획 없음');continue}
  const pg=await b.newPage({viewport:{width:900,height:1200}});
  await pg.setContent(r.html.replace('<head>','<head><base href="'+(process.env.BASE||'http://localhost:8765/')+'">'),{waitUntil:'load'});await pg.evaluate('document.fonts.ready');await pg.waitForTimeout(300);
  const v=await pg.evaluate(({sheets,pages,MM})=>{const V=[];const bps=[...document.querySelectorAll('body>.bp')];
   const H=['ct','th','sh2','sbn'];const isHead=el=>!!el&&(H.some(c=>el.classList.contains(c))||(el.classList.contains('cbk')&&el.children.length===1&&/^H[1-6]$/.test(el.firstElementChild.tagName))||(el.classList.contains('psgu')&&el.querySelectorAll('.psg>*').length===1&&!!el.querySelector('.psg>.hd')));
   const isBox=el=>!!el&&el.classList.contains('cbk')&&!!el.firstElementChild&&(/^(TABLE)$/.test(el.firstElementChild.tagName)||['ex','nt','eqn','fg','two-c'].some(c=>el.firstElementChild.classList.contains(c)));
   const lines=el=>{const lh=parseFloat(getComputedStyle(el.firstElementChild||el).lineHeight)||18;return Math.round(el.getBoundingClientRect().height/lh)};
   const codeOf=el=>{if(!el)return '';const c=el.getAttribute&&el.getAttribute('data-c');if(c)return c;const q=el.querySelector&&el.querySelector('[data-c]');return q?q.getAttribute('data-c'):''};
   const conts=bp=>{const a=[];const tp=bp.querySelector('.bd .tp');if(tp)a.push({el:tp,kind:'top'});bp.querySelectorAll('.bd .col').forEach((c,i)=>a.push({el:c,kind:'col',i}));const one=bp.querySelector('.bd.one');if(one&&!one.classList.contains('ntp'))a.push({el:one,kind:'one'});return a};
   const info=[];
   bps.forEach((bp,si)=>{const pi=sheets[si];const P=pi>=0?pages[pi]:null;if(!P||!['pr','cn','es','ak','toc'].includes(P.k)){info.push(null);return}
    const cs=conts(bp).map(c=>{const kids=[...c.el.children];const r=c.el.getBoundingClientRect();const last=kids[kids.length-1];
     return {...c,kids,top:r.top,bottom:c.kind==='top'?r.bottom:(c.kind==='col'?c.el.parentElement.getBoundingClientRect().bottom:r.bottom),right:r.right,left:r.left,lastB:last?Math.max(...kids.map(k=>k.getBoundingClientRect().bottom)):r.top}});
    info.push({P,cs,bp});
    const add=(t,c,el,x)=>V.push({t,n:P.n,k:P.k,label:P.label,col:c?c.kind+(c.i!=null?c.i:''):'',code:codeOf(el),...(x||{})});
    cs.forEach(c=>{
     // 넘침
     c.kids.forEach(k=>{const rb=k.getBoundingClientRect().bottom;if(rb>c.bottom+1.5)add('overflow',c,k,{by:+((rb-c.bottom)/MM).toFixed(1)})});
     if(c.kind!=='top'){const last=c.kids[c.kids.length-1],prev=c.kids[c.kids.length-2];
      if(isHead(last))add('orphan',c,last,{what:last.className})}
     // 표
     c.el.querySelectorAll('table').forEach(t=>{const tr=t.getBoundingClientRect();if(tr.right>c.right+1||t.scrollWidth>t.clientWidth+1)add('table',c,t.closest('.u')||t,{what:'넓음',by:+((tr.right-c.right)/MM).toFixed(1)});
      t.querySelectorAll('th').forEach(th=>{if(!th.textContent.trim()||th.textContent.trim().length>8)return;const rg=document.createRange();rg.selectNodeContents(th);const lh=parseFloat(getComputedStyle(th).lineHeight)||16;if(rg.getBoundingClientRect().height>lh*1.5)add('table',c,t.closest('.u')||t,{what:'머리글 줄바꿈',txt:th.textContent.trim()})})});
    });
    // QR 겹침
    const fq=bp.querySelector('.fq');if(fq){const q=fq.getBoundingClientRect();cs.forEach(c=>c.kids.forEach(k=>{const w=document.createTreeWalker(k,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){if(!n.textContent.trim())continue;const cl=n.parentElement&&n.parentElement.closest('.clp');const cr=cl&&cl.getBoundingClientRect();const rg=document.createRange();rg.selectNodeContents(n);for(const r of rg.getClientRects()){if(cr&&(r.bottom<=cr.top+1||r.top>=cr.bottom-1))continue;if(r.right>q.left&&r.left<q.right&&r.bottom>q.top&&r.top<q.bottom){add('qr',c,k);return}}}}))}
    // 번호 순서
    if((P.k==='pr'||P.k==='es')&&P.label!=='OX · 빈칸'){ // OX · 빈칸 쪽은 두 열이 따로 번호를 매긴다
    const ns=[];cs.forEach(c=>c.kids.forEach(k=>{const e=k.querySelector('.no')||k.querySelector('.nc>b');if(e&&/^\d+$/.test(e.textContent.trim()))ns.push(+e.textContent.trim())}));for(let i=1;i<ns.length;i++)if(ns[i]<=ns[i-1]){V.push({t:'order',n:P.n,k:P.k,label:P.label,nums:ns.join(',')});break}}
   });
   // 불필요한 넘김: 같은 묶음(같은 종류·라벨) 안에서만 본다
   const seq=[];info.forEach(x=>{if(!x)return;x.cs.filter(c=>c.kind!=='top').forEach((c,ci)=>seq.push({x,c,ci}))});
   for(let i=0;i+1<seq.length;i++){const a=seq[i],b=seq[i+1];if(a.x.P.k!==b.x.P.k||a.x.P.label!==b.x.P.label||a.x.P.sub!==b.x.P.sub||a.x.P.k==='toc'||a.x.P.label==='OX · 빈칸')continue; // OX · 빈칸 쪽은 두 열이 따로 채워진다
    {const ks=a.c.kids,last=ks[ks.length-1],prev=ks[ks.length-2];const nx=b.c.kids[0]; // 제목 + 3줄 이하 설명만 남고 바로 뒤 상자·표는 다음 열/쪽
     if(prev&&isHead(prev)&&last&&last.classList.contains('cbk')&&lines(last)<=3&&isBox(nx))V.push({t:'orphan',n:a.x.P.n,k:a.x.P.k,label:a.x.P.label,col:a.c.kind,code:'',what:'제목+짧은 설명'})}
    const mb=el=>el?parseFloat(getComputedStyle(el).marginBottom)||0:0,lk=a.c.kids[a.c.kids.length-1];
    const free=(a.c.bottom-a.c.lastB-mb(lk))/MM;if(free<20)continue;
    const um=b.x.P.um?(b.c.kind==='col'?b.x.P.um[b.c.i]:b.c.kind==='one'?b.x.P.um[0]:null):null;const u1=b.c.kids[0];if(!u1)continue;
    if(b.c.kind==='col'&&b.c.i===0&&b.x.P.tm&&b.x.P.tm.length)continue; // 다음 쪽 맨 위에 넓은 장문이 먼저 놓인 경우
    const h=el=>el?(el.getBoundingClientRect().height+mb(el)+(parseFloat(getComputedStyle(el).marginTop)||0))/MM:0;
    let need=h(u1);if(um&&um[0]){if(um[0][3])continue;for(let j=0;um[j]&&um[j][2]&&b.c.kids[j+1];j++)need+=h(b.c.kids[j+1])}else if(um&&!um[0]){}
    else if(isHead(u1))need+=h(b.c.kids[1]);
    if(u1.classList.contains('q'))need+=parseFloat(getComputedStyle(a.c.el).getPropertyValue('--g'))||2.8; // 열 첫 문항이 아니면 문제 간격이 붙는다
    if(need+4<free)V.push({t:'gap',n:a.x.P.n,k:a.x.P.k,label:a.x.P.label,col:a.c.kind+(a.c.i!=null?a.c.i:''),code:codeOf(u1),free:+free.toFixed(1),need:+need.toFixed(1)})}
   // 글꼴: 옛한글·원문자
   const chars=new Map();bps.forEach((bp,si)=>{const pi=sheets[si];const P=pi>=0?pages[pi]:null;if(!P)return;for(const ch of bp.textContent){const c=ch.codePointAt(0);if((c>=0x1100&&c<=0x11FF)||(c>=0xA960&&c<=0xA97F)||(c>=0xD7B0&&c<=0xD7FF)||(c>=0x3131&&c<=0x318E)||(c>=0x2460&&c<=0x24FF)||(c>=0x3200&&c<=0x32FF)||(c>=0x2300&&c<=0x23FF)||c===0x302E||c===0x302F){const k=c+'|'+P.n;if(!chars.has(k))chars.set(k,{c,n:P.n})}}});
   return {V,chars:[...chars.values()]}},{sheets:r.sheets,pages:r.pages,MM});
  const gl={};v.chars.forEach(({c,n})=>{const bad=cmap&&!cmap.has(c)?'번들 글꼴 없음':'';if(!bad)return;const k=bad+' U+'+c.toString(16).toUpperCase()+' '+String.fromCodePoint(c);(gl[k]=gl[k]||[]).push(n)});
  Object.entries(gl).forEach(([k,ns])=>v.V.push({t:'glyph',what:k,pages:ns.slice(0,12).join(',')+(ns.length>12?' 외 '+(ns.length-12)+'쪽':''),cnt:ns.length}));
  const cnt={};v.V.forEach(x=>cnt[x.t]=(cnt[x.t]||0)+1);
  out.books[id]={pages:r.pages.length,count:cnt,v:v.V};Object.entries(cnt).forEach(([k,n])=>out.count[k]=(out.count[k]||0)+n);
  console.log(id,r.pages.length+'쪽',JSON.stringify(cnt));await pg.close()}
 fs.mkdirSync('books',{recursive:true});fs.writeFileSync(process.env.OUT||'books/check.json',JSON.stringify(out,null,1));console.log('합계',JSON.stringify(out.count));
 await b.close()})()
