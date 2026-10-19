/* Solvi 늦게 불러오는 코드: omr-report — index.html 의 전역(DATA, jget, render …)을 그대로 씁니다. */
function reportCss(){return `.pages{--p:#2f7fd0;--pd:#1d5ca6;--pl:#eaf3fd;--pl2:#cfe2f7}.pg{width:210mm;min-height:297mm;background:#fff;margin:0 auto 7mm;box-shadow:0 2px 12px #0002;padding:14mm 14mm 12mm;position:relative;break-after:page;page-break-after:always;font-size:10pt;line-height:1.55;color:#1b2430}
.rh{border-top:1.6mm solid var(--p);padding-top:3mm;display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:5mm;border-bottom:.3mm solid var(--pl2);padding-bottom:3mm}.rh b{font-size:21pt}.rh span{color:#586476;font-size:9.5pt;text-align:right}
.kp{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin-bottom:5mm}.kp div{background:var(--pl);border-radius:2.4mm;padding:3mm 3.4mm}.kp small{display:block;color:#586476;font-size:8.5pt}.kp b{font-size:17pt;color:var(--pd)}
h4{font-size:11.5pt;margin:5mm 0 2mm;color:var(--pd)}
.bar{height:3.4mm;background:#e6ebf1;border-radius:2mm;overflow:hidden}.bar i{display:block;height:100%;background:var(--p)}.bar.lo i{background:#f7b928}.bar.vl i{background:#e5484d}
table{border-collapse:collapse;width:100%;font-size:9pt}th{background:var(--p);color:#fff;font-weight:500;padding:1.4mm 2mm}td{border-bottom:.2mm solid #d3dfec;padding:1.3mm 2mm;text-align:center}td.l{text-align:left}
.ic{display:inline-block;width:4.2mm;height:4.2mm;vertical-align:-1mm}.ic svg{width:100%;height:100%}
.lg{display:flex;gap:4mm;flex-wrap:wrap;font-size:8.5pt;color:#586476;margin:2mm 0}.lg span{display:flex;align-items:center;gap:1.2mm}
.cm{border:.3mm solid var(--pl2);border-radius:2.4mm;height:34mm;padding:2mm 3mm;color:#9aa7b6;font-size:9pt}
@media print{.pg{margin:0;box-shadow:none}}`}

function openReport(hsIn){
 const st=STU.find(s=>s.id===CUR_S);const hs=Array.isArray(hsIn)?hsIn:H();
 if(!hs.length){alert('채점 기록이 없어 리포트를 만들 수 없습니다.');return}
 const its=hs.flatMap(h=>h.items);const n=its.length,r=its.filter(x=>x.r).length;
 const t0=new Date(hs[0].t).toLocaleDateString('ko-KR'),t1=new Date(hs[hs.length-1].t).toLocaleDateString('ko-KR');
 const rows=typeRows(hs);const cnt={};rows.forEach(o=>cnt[o.lv]=(cnt[o.lv]||0)+1);
 const subst=statsFrom(hs,q=>q.sub+' '+q.subname).sort((a,b)=>a.k.localeCompare(b.k));
 const order={skull:0,red:1,yellow:2,green:3,star:4,gray:5};
 const weak=rows.filter(o=>o.n).sort((a,b)=>order[a.lv]-order[b.lv]||a.p-b.p).slice(0,8);
 const adv={skull:'개념 정리부터 다시 읽고, 쉬운 문제부터 반복',red:'유형 문제를 하·중 위주로 반복',yellow:'틀린 문제 복습과 쌍둥이 문제로 확인',green:'가끔 점검',star:'충분함'};
 const wsn=WSH.filter(w=>!CUR_S||w.sid===CUR_S).length;
 const L=lastRes();const wrongCodes=Object.entries(L).filter(([c,a])=>a[a.length-1]===0).map(([c])=>c);
 const recent=hs.slice(-10).reverse();
 const bar=p=>`<div class="bar ${p<.5?'vl':p<.75?'lo':''}"><i style="width:${Math.round(p*100)}%"></i></div>`;
 const legend=Object.keys(LV).map(k=>`<span><i class="ic">${ICON[k]}</i>${LV[k]} ${cnt[k]||0}</span>`).join('');
 const bySub={};rows.forEach(o=>(bySub[o.sub]=bySub[o.sub]||[]).push(o));
 const allRows=subs.map(([s,nm])=>(bySub[s]||[]).map((o,i)=>`<tr><td class="l">${i?'':esc(s+' '+nm)}</td><td class="l">${esc(o.type)}</td><td><i class="ic">${ICON[o.lv]}</i></td><td>${o.n?Math.round(o.p*100)+'%':'-'}</td><td>${o.n||0}</td></tr>`).join('')).join('');
 const lab=h=>h.set==='ws'?'학습지 · '+esc((WSH.find(w=>w.id===h.sub)||{}).title||fmtNo(h.sub)):h.set==='book'?esc(bookLbl(h.sub)):h.set==='practice'?'유형 반복 학습':esc((SETS[h.set]||h.set)+' '+(h.sub||'전체'));
 const html=`<style>${reportCss()}</style><div class="pages"><div class="pg">
 <div class="rh"><div><b>학습 리포트</b><div style="margin-top:1mm;font-size:11pt">${esc(st?st.name:'학생 선택 필요')}${st&&st.grade?' · '+esc(st.grade):''}</div></div><span>${t0} ~ ${t1}<br>출력일 ${new Date().toLocaleDateString('ko-KR')}</span></div>
 <div class="kp"><div><small>푼 문항</small><b>${n}</b></div><div><small>정답률</small><b>${Math.round(r/n*100)}%</b></div><div><small>채점 횟수</small><b>${hs.length}</b></div><div><small>만든 학습지</small><b>${wsn}</b></div></div>
 <h4>소단원별 정답률</h4><table><tr><th style="width:42%">소단원</th><th>정답률</th><th style="width:36%"></th><th>맞은/푼 문항</th></tr>${subst.map(x=>`<tr><td class="l">${esc(x.k)}</td><td>${Math.round(x.p*100)}%</td><td>${bar(x.p)}</td><td>${x.r}/${x.n}</td></tr>`).join('')}</table>
 <h4>집중 보강이 필요한 유형 (상위 ${weak.length}개)</h4><table><tr><th></th><th>유형</th><th>정답률</th><th>풀이</th><th>권장 학습</th></tr>${weak.map(o=>`<tr><td><i class="ic">${ICON[o.lv]}</i></td><td class="l">${esc(o.type)}</td><td>${Math.round(o.p*100)}%</td><td>${o.n}</td><td class="l">${adv[o.lv]}</td></tr>`).join('')||'<tr><td colspan="5">기록이 더 필요합니다.</td></tr>'}</table>
 <h4>선생님 코멘트</h4><div class="cm">　</div></div>
 <div class="pg"><div class="rh"><div><b>유형별 성취 지도</b></div><span>${esc(st?st.name:'학생 선택 필요')}</span></div><div class="lg">${legend}</div>
 <table><tr><th>소단원</th><th>유형</th><th></th><th>정답률</th><th>풀이</th></tr>${allRows}</table>
 <h4>최근 채점 기록</h4><table><tr><th>일시</th><th>범위</th><th>점수</th></tr>${recent.map(h=>`<tr><td>${new Date(h.t).toLocaleDateString('ko-KR')}</td><td class="l">${lab(h)}</td><td>${h.items.filter(x=>x.r).length}/${h.items.length}</td></tr>`).join('')}</table>
 ${wrongCodes.length?`<h4>마지막 풀이에서 틀린 문항 (${wrongCodes.length})</h4><div style="font-size:8.5pt;color:#586476;word-break:break-all">${wrongCodes.slice(0,120).join(', ')}${wrongCodes.length>120?' 외 '+(wrongCodes.length-120)+'개':''}</div>`:''}</div></div>`;
 mount($('#wsPaper'),html);
 let ps=document.getElementById('wsPrintStyle');if(!ps){ps=document.createElement('style');ps.id='wsPrintStyle';document.head.appendChild(ps)}ps.textContent='@page{size:A4;margin:0}';
 $('#wsBar').innerHTML='<button class="p" onclick="window.print()">인쇄 / PDF 저장</button><button class="wsx" onclick="closeWs()" title="닫기" aria-label="닫기">✕</button><span class="m">학생 리포트 · A4 2쪽</span>';
 $('#wsView').classList.add('open');$('#wsView').scrollTop=0;pushNav()}

let REP={kind:'stu',id:'',days:7,cm:'',bk:null};

function repMetrics(hs,days){const today=dayStart(Date.now()),a=today-(days-1)*864e5,b=a-days*864e5;
 const P=hs.filter(h=>h.t>=a),Q=hs.filter(h=>h.t>=b&&h.t<a),agg=l=>{const it=l.flatMap(h=>h.items),n=it.length,r=it.filter(x=>x.r).length;return {n,r,p:n?r/n:null,d:new Set(l.map(h=>dayStart(h.t))).size}};
 const per=[...Array(days)].map((_,i)=>{const d=a+i*864e5;return {d,n:hs.filter(h=>dayStart(h.t)===d).reduce((x,h)=>x+h.items.length,0)}});
 return {a,today,P:agg(P),Q:agg(Q),per,all:agg(hs)}}

function repOpen(kind,id){REP.kind=kind||'stu';REP.id=id||'';REP.cm='';REP.bk=null;repRender();repBook()}

function repDays(d){REP.days=d;repRender()}

async function repBook(){const my=REP;try{if(!(typeof bkLoad==='function'))return;await bkLoad();await bkInit();const books=bkBookList(),sid=REP.kind==='stu'?(teacher()?(REP.id||CUR_S):''):'';const hs=REP.kind==='stu'?(teacher()?hist.filter(h=>h.sid===sid):hist):[];const recs=bkRecs(hs);const out=[];
  for(const b of books){const pg=await bkPagesOf(b);out.push(bkStatOf(b,pg,recs));if(my!==REP)return}
  REP.bk=out;if($('#wsView').classList.contains('open'))repRender()}catch(e){}}

function repRender(){const days=REP.days,cls=REP.kind==='cls';let body='',title='';
 const esc2=esc,sp=SNAME[SUBJ],now=new Date().toLocaleDateString('ko-KR');
 const css=`.pg{width:210mm;min-height:297mm;background:#fff;margin:0 auto 6mm;padding:14mm 15mm;box-shadow:0 2px 12px #0002;font-family:Pretendard,PretendardLocal,sans-serif;color:#1b2430;font-size:10pt;line-height:1.5;position:relative}.pg *{box-sizing:border-box}h1{margin:0;font-size:19pt;color:#1d5ca6}.sub{color:#586476;font-size:9.5pt;margin:1mm 0 5mm}h2{font-size:11.5pt;margin:5mm 0 2mm;padding-bottom:1mm;border-bottom:.4mm solid #2f7fd0;color:#1d5ca6}
 .kp{display:grid;grid-template-columns:repeat(5,1fr);gap:3mm}.kp div{border:.3mm solid #cfd7e1;border-radius:2mm;padding:2.5mm 3mm}.kp small{display:block;color:#586476;font-size:8pt}.kp b{font-size:15pt;color:#1d5ca6}.kp em{font-style:normal;font-size:8pt;color:#586476;margin-left:1mm}
 table{width:100%;border-collapse:collapse;font-size:9pt}th,td{border-bottom:.2mm solid #dfe5ec;padding:1.4mm 1.6mm;text-align:center}th{background:#eaf3fd;color:#1d5ca6;font-weight:600}td.l{text-align:left}.bar{height:3.2mm;background:#e8eef5;border-radius:2mm;overflow:hidden}.bar i{display:block;height:100%;background:#2a72bf}
 .cm{min-height:24mm;border:.3mm dashed #9aa7b6;border-radius:2mm;padding:2.5mm 3mm;white-space:pre-wrap;outline:none}.cm:empty::before{content:'여기를 눌러 코멘트를 입력하세요 (인쇄에 포함돼요)';color:#9aa7b6}.ft{position:absolute;left:15mm;right:15mm;bottom:8mm;text-align:center;font-size:8pt;color:#8794a3}.g2{display:grid;grid-template-columns:1fr 1fr;gap:5mm}@media print{.pg{box-shadow:none;margin:0}.cm:empty::before{content:''}}`;
 const chart=(per)=>{const mx=Math.max(1,...per.map(x=>x.n)),w=170,h=34,bw=w/per.length;return `<svg viewBox="0 0 ${w} ${h+8}" style="width:100%;height:30mm">${per.map((x,i)=>{const bh=x.n/mx*h;return `<rect x="${i*bw+1}" y="${h-bh}" width="${Math.max(1,bw-2)}" height="${Math.max(bh,x.n?.6:0)}" fill="${x.n?'#2a72bf':'#e8eef5'}" rx=".8"/>${per.length<=14||i%Math.ceil(per.length/14)===0?`<text x="${i*bw+bw/2}" y="${h+5.5}" font-size="3.2" text-anchor="middle" fill="#586476">${new Date(x.d).getDate()}</text>`:''}${x.n?`<text x="${i*bw+bw/2}" y="${h-bh-1}" font-size="3" text-anchor="middle" fill="#1d5ca6">${x.n}</text>`:''}`}).join('')}</svg>`};
 if(!cls){const sid=teacher()?(REP.id||CUR_S):'',st=teacher()?STU.find(x=>x.id===sid):null;if(teacher()&&!st){toast('학생을 먼저 선택하세요');return}
  const hs=teacher()?hist.filter(h=>h.sid===sid):hist,name=teacher()?st.name:(STINFO&&STINFO.name)||'',grade=teacher()?clsName(st):(STINFO&&STINFO.grade)||'';
  const M=repMetrics(hs,days),S=habitStats(hs),rows=typeRows(hs).filter(o=>o.n),weak=rows.filter(o=>['skull','red','yellow'].includes(o.lv)).sort((a,b)=>a.p-b.p).slice(0,5),strong=rows.filter(o=>['star','green'].includes(o.lv)&&o.n>=3).sort((a,b)=>b.p-a.p).slice(0,3);
  const as=teacher()?ASSIGN.filter(x=>x.student_id===sid):ASSIGN,done=as.filter(x=>hs.some(h=>h.set==='ws'&&h.sub===x.wid)).length,late=as.filter(x=>x.due&&x.due<new Date().toISOString().slice(0,10)&&!hs.some(h=>h.set==='ws'&&h.sub===x.wid)).length;
  const ex=ddayList(grade).find(x=>x.days>=0);title=name+' 학습 리포트';
  body=`<h1>${esc2(name)} 학습 리포트</h1><div class="sub">${grade?esc2(grade)+' · ':''}${esc2(sp)} · 최근 ${days}일 (${fmtD(M.today-(days-1)*864e5).slice(5)} ~ ${fmtD(M.today).slice(5)}) · 발행 ${now}</div>
  <div class="kp"><div><small>푼 문항</small><b>${M.P.n}</b><em>${M.Q.n?repDelta(M.P.n,M.Q.n):''}</em></div><div><small>정답률</small><b>${M.P.p===null?'-':Math.round(M.P.p*100)+'%'}</b><em>${repDelta(M.P.p,M.Q.p,1)}</em></div><div><small>학습한 날</small><b>${M.P.d}<small style="display:inline">/${days}</small></b></div><div><small>연속 학습</small><b>${S.streak}일</b><em>최고 ${S.best}</em></div><div><small>레벨</small><b>Lv.${S.lv}</b><em>${S.title}</em></div></div>
  <h2>일별 학습량</h2>${chart(M.per)}
  <div class="g2"><div><h2>보강이 필요한 유형</h2>${weak.length?`<table><tr><th>유형</th><th>정답률</th><th>풀이</th></tr>${weak.map(o=>`<tr><td class="l">${esc2(o.type)}<br><small style="color:#8794a3">${esc2(o.subname||'')}</small></td><td><b style="color:#d9534f">${Math.round(o.p*100)}%</b></td><td>${o.n}</td></tr>`).join('')}</table>`:'<div style="color:#586476">뚜렷한 약점이 없어요.</div>'}</div>
  <div><h2>잘하는 유형</h2>${strong.length?`<table><tr><th>유형</th><th>정답률</th><th>풀이</th></tr>${strong.map(o=>`<tr><td class="l">${esc2(o.type)}</td><td><b style="color:#2b9a5b">${Math.round(o.p*100)}%</b></td><td>${o.n}</td></tr>`).join('')}</table>`:'<div style="color:#586476">기록이 쌓이면 보여요.</div>'}${as.length?`<h2>과제</h2><div>배정 ${as.length}개 · 제출 ${done}개${late?` · <b style="color:#d9534f">기한 지남 ${late}개</b>`:''}</div>`:''}${ex?`<h2>시험</h2><div><b>${esc2(ex.name)}</b> ${ex.days===0?'D-DAY':'D-'+ex.days}</div>`:''}</div></div>
  ${REP.bk?`<h2>교재 진도</h2><table><tr><th style="width:26%">교재</th><th>진도</th><th>채점한 쪽</th><th>정답률</th></tr>${REP.bk.map(x=>`<tr><td class="l">${esc2(x.b.name)}</td><td><div class="bar"><i style="width:${x.pct||0}%"></i></div></td><td>${x.done}${x.tot?'/'+x.tot:''}</td><td>${x.acc===null?'-':Math.round(x.acc*100)+'%'}</td></tr>`).join('')}</table>`:''}
  <h2>선생님 코멘트</h2><div class="cm" contenteditable="true" oninput="REP.cm=this.innerText">${esc2(REP.cm)}</div>`}
 else{const ss=clsMembers();if(!ss.length){toast('반을 먼저 선택하세요');return}const nm=SGR==='__none'?'반 미지정':SGR;title=nm+' 반 리포트';
  const rowsS=ss.map(x=>{const h=hist.filter(y=>y.sid===x.id),m=repMetrics(h,days),sh=habitStats(h),w=typeRows(h).filter(o=>o.n&&['skull','red','yellow'].includes(o.lv)).sort((a,b)=>a.p-b.p)[0];return {x,m,sh,w}});
  const all=repMetrics(hist.filter(h=>ss.some(x=>x.id===h.sid)),days),CS=clsStats(ss),act=rowsS.filter(r=>r.m.P.n).length;
  body=`<h1>${esc2(nm)} 학습 리포트</h1><div class="sub">${esc2(sp)} · 최근 ${days}일 (${fmtD(all.today-(days-1)*864e5).slice(5)} ~ ${fmtD(all.today).slice(5)}) · 학생 ${ss.length}명 · 발행 ${now}</div>
  <div class="kp"><div><small>학생</small><b>${ss.length}</b></div><div><small>푼 문항 합계</small><b>${all.P.n}</b><em>${all.Q.n?repDelta(all.P.n,all.Q.n):''}</em></div><div><small>반 평균 정답률</small><b>${all.P.p===null?'-':Math.round(all.P.p*100)+'%'}</b><em>${repDelta(all.P.p,all.Q.p,1)}</em></div><div><small>학습한 학생</small><b>${act}/${ss.length}</b></div><div><small>1인 평균 문항</small><b>${ss.length?Math.round(all.P.n/ss.length):0}</b></div></div>
  <h2>일별 반 전체 학습량</h2>${chart(all.per)}
  <h2>학생별 현황</h2><table><tr><th>이름</th><th>푼 문항</th><th>정답률</th><th>학습일</th><th>연속</th><th>가장 약한 유형</th></tr>${rowsS.sort((a,b)=>b.m.P.n-a.m.P.n).map(r=>`<tr><td class="l">${esc2(r.x.name)}</td><td>${r.m.P.n}</td><td>${r.m.P.p===null?'-':Math.round(r.m.P.p*100)+'%'}</td><td>${r.m.P.d}/${days}</td><td>${r.sh.streak}일</td><td class="l">${r.w?esc2(r.w.type):'<span style="color:#8794a3">-</span>'}</td></tr>`).join('')}</table>
  <div class="g2"><div><h2>반이 어려워하는 유형</h2>${CS.tr.slice(0,5).length?`<table><tr><th>유형</th><th>정답률</th><th>풀이</th></tr>${CS.tr.slice(0,5).map(o=>`<tr><td class="l">${esc2(o.type)}</td><td><b style="color:#d9534f">${Math.round(o.p*100)}%</b></td><td>${o.n}</td></tr>`).join('')}</table>`:'<div style="color:#586476">기록이 없어요.</div>'}</div>
  <div><h2>이 기간에 안 푼 학생</h2><div>${rowsS.filter(r=>!r.m.P.n).map(r=>esc2(r.x.name)).join(', ')||'모두 풀었어요!'}</div></div></div>
  <h2>선생님 코멘트</h2><div class="cm" contenteditable="true" oninput="REP.cm=this.innerText">${esc2(REP.cm)}</div>`}
 mount($('#wsPaper'),`<style>${css}</style><div class="pg">${body}<div class="ft">Solvi · ${esc2(title)} · ${now}</div></div>`);
 $('#wsBar').innerHTML=`<button class="p" onclick="window.print()">인쇄 / PDF로 저장</button><span class="seg" style="margin:0 8px">${[7,14,30].map(d=>`<label><input type="radio" name="rd" ${REP.days===d?'checked':''} onchange="repDays(${d})"><span>${d}일</span></label>`).join('')}</span><button class="wsx" onclick="closeWs()" title="닫기" aria-label="닫기">✕</button><span class="m">인쇄 창에서 「PDF로 저장」을 고르면 파일로 받을 수 있어요 · 코멘트는 페이지 아래 칸에서 직접 쓸 수 있어요</span>`;
 let ps=document.getElementById('wsPrintStyle');if(!ps){ps=document.createElement('style');ps.id='wsPrintStyle';document.head.appendChild(ps)}ps.textContent='@page{size:A4;margin:0}';$('#wsView').classList.add('open');pushNav()}

const OMRMK=[[12,12],[198,12],[12,285],[198,285]],OMRMS=8;

const OMRSUBJ={me:'01',cm:'02',ph:'03'};

function omrInfoGeom(mock){const g=[];const d=3.8,pitch=4.4,y0=46;const digits=[...Array(10).keys()].map(String);
 if(mock){for(let i=0;i<8;i++)g.push({k:'수험번호',i,x:112+i*6.4,y0,pitch,d,lab:digits,grp:'수험번호'});for(let i=0;i<2;i++)g.push({k:'과목번호',i,x:166+i*6.4,y0,pitch,d,lab:digits,grp:'과목번호'});g.push({k:'홀짝',i:0,x:184,y0,pitch,d,lab:['홀','짝'],grp:'형'})}
 else{g.push({k:'학년',i:0,x:112,y0,pitch,d,lab:digits,grp:'학년'});for(let i=0;i<2;i++)g.push({k:'반',i,x:130+i*6.4,y0,pitch,d,lab:digits,grp:'반'});for(let i=0;i<2;i++)g.push({k:'번호',i,x:154+i*6.4,y0,pitch,d,lab:digits,grp:'번호'})}
 return g}

const OMRMKL=[[12,12],[285,12],[12,198],[285,198]],OMRMS2=10,OMRPAGE={L:[297,210],P:[210,297]};

function omrInfoGeomL(mock){const g=[],d=3.8,pitch=4.4,y0=86,dg=[...Array(10).keys()].map(String);
 if(mock){for(let i=0;i<8;i++)g.push({k:'수험번호',i,x:26+i*6,y0,pitch,d,lab:dg,grp:'수험번호'});for(let i=0;i<2;i++)g.push({k:'과목번호',i,x:77+i*6,y0,pitch,d,lab:dg,grp:'과목번호'});g.push({k:'홀짝',i:0,x:91,y0,pitch,d,lab:['홀','짝'],grp:'형'})}
 else{g.push({k:'학년',i:0,x:36,y0,pitch,d,lab:dg,grp:'학년'});for(let i=0;i<2;i++)g.push({k:'반',i,x:55+i*6.4,y0,pitch,d,lab:dg,grp:'반'});for(let i=0;i<2;i++)g.push({k:'번호',i,x:76+i*6.4,y0,pitch,d,lab:dg,grp:'번호'})}
 return g}

function omrGeomL(qs,mock){const n=qs.length;let cols=n<=15?1:n<=40?2:n<=75?3:n<=100?4:5;let rows=Math.max(10,Math.ceil(Math.ceil(n/cols)/5)*5);if(rows>25)rows=25;
 const RX=100,RW=177,gap=4,W=Math.min(56,(RW-gap*(cols-1))/cols),total=cols*W+gap*(cols-1),xs0=RX+(RW-total)/2;
 const mo=Math.max(5,...qs.map(q=>(q.set==='ox'?2:nOpts(q)))),optP=Math.min(9.2,(W-11)/(mo+.15)),yTop=50,rowH=Math.min(8,(187-yTop)/rows),d=Math.min(5.4,rowH-1.6),b=[];
 qs.forEach((q,i)=>{if(i>=cols*rows)return;const c=Math.floor(i/rows),r=i%rows;const k=q.set==='blank'||q.set==='noxq'||q.set==='essay'?0:(q.set==='ox'?2:nOpts(q));
  for(let o=0;o<k;o++)b.push({q:i,o,x:xs0+c*(W+gap)+10.5+o*optP+optP/2,y:yTop+r*rowH+rowH/2})});
 const info=omrInfoGeomL(!!mock).map(g=>({...g,pts:g.lab.map((l,r)=>({r,x:g.x,y:g.y0+r*g.pitch}))}));
 return {b,cols,rows,W,gap,xs0,optP,rowH,yTop,d,mo,cap:cols*rows,info,mock:!!mock,land:1}}

function omrGeom(qs,mock,land){if(land)return omrGeomL(qs,mock);const n=qs.length,per=n>50?30:25,cols=Math.min(3,Math.ceil(n/per)||1);const colW=cols===1?120:cols===2?88:60,xs0=cols===1?45:cols===2?17:15;
 const mo=Math.max(5,...qs.map(q=>(q.set==='ox'?2:nOpts(q))));const optP=Math.min(10.5,(colW-14)/(mo+.2));const y0=96,rowH=Math.min(7.3,(274-y0)/per),d=Math.min(5.6,rowH-1.4);const b=[];
 qs.forEach((q,i)=>{if(i>=per*3)return;const c=Math.floor(i/per),r=i%per;const k=q.set==='blank'||q.set==='noxq'||q.set==='essay'?0:(q.set==='ox'?2:nOpts(q));
  for(let o=0;o<k;o++)b.push({q:i,o,x:xs0+c*colW+12+o*optP+optP/2,y:y0+r*rowH+rowH/2});});
 const info=omrInfoGeom(!!mock).map(g=>({...g,pts:g.lab.map((l,r)=>({r,x:g.x,y:g.y0+r*g.pitch}))}));
 return {b,per,cols,colW,xs0,optP,rowH,y0,d,mo,cap:per*3,info,mock:!!mock}}

function omrCard(id,ori){ori=ori||localStorage.getItem('omr_ori')||'L';if(ori==='L')return omrCardL(id);return omrCardP(id)}

function omrCardL(id){const w=WSH.find(x=>x.id===id);if(!w)return;const qs=w.codes.map(c=>byCode[c]).filter(Boolean),n=qs.length,mock=!!w.mock,G=omrGeomL(qs,mock);
 const base=(CF.pub||location.href).split('#')[0].split('?')[0],url=base+'#ws='+w.id,cv=w.cover||{},sj=subjOf(qs[0]&&qs[0].code)||SUBJ,subjN=cv.subject||SNAME[sj]||'',sc=OMRSUBJ[sj]||'';
 const RD='#d4381f',RT='#fdf0ec',RM='#f3b9ab';
 const mk=OMRMKL.map(([x,y],i)=>`<s style="left:${x}mm;top:${y}mm${i===3?`;width:${OMRMS2}mm;height:${OMRMS2}mm`:''}"></s>`).join('');
 const fs=Math.max(5,Math.min(7,G.d*1.3)).toFixed(1),bw=(G.d*.78).toFixed(2);
 const blk=[],zeb=[],nums=[];
 for(let c=0;c<G.cols;c++){const x=G.xs0+c*(G.W+G.gap),cnt=Math.min(G.rows,n-c*G.rows);if(cnt<=0)break;
  blk.push(`<div class="bk" style="left:${x}mm;top:${G.yTop-6.4}mm;width:${G.W}mm;height:${6.4+cnt*G.rowH+1.2}mm"></div><div class="bh" style="left:${x}mm;top:${G.yTop-6.4}mm;width:${G.W}mm"><span style="width:10.5mm">번호</span><span style="flex:1">답 란</span></div>`);
  for(let g5=0;g5*5<cnt;g5++)if(g5%2===1)zeb.push(`<div class="zb" style="left:${x+.3}mm;top:${G.yTop+g5*5*G.rowH}mm;width:${G.W-.6}mm;height:${Math.min(5,cnt-g5*5)*G.rowH}mm"></div>`);
  for(let r=0;r<cnt;r++){const i=c*G.rows+r,q=qs[i],y=G.yTop+r*G.rowH+G.rowH/2;nums.push(`<b style="left:${x+8.6}mm;top:${y}mm">${i+1}</b>${q.set==='blank'||q.set==='essay'?`<span class="bl" style="left:${x+11}mm;top:${y}mm">직접 풀이·입력</span>`:''}`)}}
 const bub=G.b.map(p=>`<i style="left:${p.x}mm;top:${p.y}mm;width:${bw}mm;height:${G.d}mm">${(optsOf(qs[p.q])[p.o])||p.o+1}</i>`).join('');
 const ib=G.info.map(g=>g.pts.map(p=>`<i class="n" style="left:${p.x}mm;top:${p.y}mm">${g.lab[p.r]}</i>`).join('')).join('');
 const gp={};G.info.forEach(g=>{(gp[g.grp]=gp[g.grp]||[]).push(g.x)});const y0=G.info[0].y0;
 const grpLab=Object.entries(gp).map(([k,xs])=>`<u class="gl" style="left:${(Math.min(...xs)+Math.max(...xs))/2}mm;top:${y0-9}mm">${k}</u>${xs.map(x=>`<span class="gx" style="left:${x}mm;top:${y0-4.4}mm"></span>`).join('')}`).join('');
 const ipw=mock?78:66,ipx=mock?20.5:24;
 const css=`.pg{width:297mm;height:210mm;background:#fff;margin:0 auto 6mm;box-shadow:0 2px 12px #0002;font-family:Pretendard,PretendardLocal,sans-serif;color:#1b2430;position:relative;overflow:hidden;break-after:page;-webkit-print-color-adjust:exact;print-color-adjust:exact}.pg *{box-sizing:border-box}
.pg s{position:absolute;width:${OMRMS}mm;height:${OMRMS}mm;background:#000;transform:translate(-50%,-50%);text-decoration:none}
.pg .fr{position:absolute;left:20mm;top:20mm;width:257mm;height:170mm;border:.5mm solid ${RD};border-radius:1.6mm}
.pg .hb{position:absolute;left:20mm;top:20mm;width:257mm;height:13mm;background:${RD};border-radius:1.6mm 1.6mm 0 0;color:#fff}
.pg .hb .t0{position:absolute;left:6mm;top:0;height:13mm;display:flex;align-items:center;gap:3mm}.pg .hb .t0 small{font-size:6.5pt;letter-spacing:.32em;font-weight:600;opacity:.85;writing-mode:horizontal-tb}.pg .hb .t0 b{position:static;transform:none;color:#fff;font-size:17pt;font-weight:800;letter-spacing:.1em}
.pg .hb .t1{position:absolute;left:64mm;right:92mm;top:0;height:13mm;display:flex;align-items:center;font-size:11.5pt;font-weight:700;line-height:1.2;padding-left:5mm;border-left:.3mm solid #ffffff66}.pg .hb .t1 span{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pg .hb .t2{position:absolute;right:6mm;top:0;height:13mm;display:flex;align-items:center;font-size:8.5pt;opacity:.95;text-align:right;line-height:1.35}
.pg .sh{position:absolute;font-size:7pt;font-weight:800;letter-spacing:.14em;color:${RD};display:flex;align-items:center;gap:2mm;white-space:nowrap}.pg .sh::after{content:'';flex:1;border-top:.25mm solid ${RM}}
.pg .box{position:absolute;border:.3mm solid ${RD};background:#fff;border-radius:.8mm}.pg .bt{position:absolute;font-size:8pt;color:${RD};font-weight:700;transform:translate(0,-50%);white-space:nowrap}.pg .fx{position:absolute;font-size:9.5pt;line-height:1}
.pg .ip{position:absolute;left:${ipx}mm;top:${y0-11.6}mm;width:${ipw}mm;height:${(10-1)*4.4+3.8+11.6+2.6}mm;background:${RT};border-radius:1.6mm}
.pg .gl{position:absolute;transform:translate(-50%,-50%);text-decoration:none;font-size:8pt;font-weight:800;color:${RD}}.pg .gx{position:absolute;transform:translate(-50%,-50%);width:4.6mm;height:4.6mm;border:.3mm solid ${RD};background:#fff;border-radius:.6mm}
.pg i{position:absolute;border:.28mm solid ${RD};border-radius:50%;transform:translate(-50%,-50%);background:#fff;color:${RD};font-style:normal;font-size:${fs}pt;line-height:1;display:flex;align-items:center;justify-content:center;font-weight:500}.pg i.n{width:3.1mm;height:3.8mm;font-size:5.2pt}
.pg .bk{position:absolute;border:.3mm solid ${RD};border-radius:1mm}.pg .bh{position:absolute;height:5mm;background:${RD};color:#fff;font-size:7.5pt;font-weight:700;display:flex;align-items:center;text-align:center;border-radius:1mm 1mm 0 0}.pg .bh span{display:block}.pg .zb{position:absolute;background:${RT}}
.pg b{position:absolute;transform:translate(-100%,-50%);font-size:9pt;font-weight:700;color:${RD};font-variant-numeric:tabular-nums}.pg .bl{position:absolute;transform:translate(0,-50%);font-size:7.2pt;color:#8794a3}
.pg .qrb{position:absolute;left:24mm;top:155mm;width:26mm;text-align:center}.pg .qrb svg{width:26mm;height:26mm;display:block}.pg .qrb b{position:static;transform:none;display:block;font-family:ui-monospace,Menlo,monospace;font-size:7pt;letter-spacing:.1em;font-weight:500;margin-top:.8mm;color:#1b2430}
.pg .nb2{position:absolute;left:54mm;top:154mm;width:40mm;font-size:6.6pt;line-height:1.55;color:#586476}.pg .nb2 em{font-style:normal;color:${RD};font-weight:800;display:block;margin-bottom:.8mm;font-size:7pt}.pg .nb2 .ex{display:flex;gap:1.6mm;align-items:center;margin:1mm 0}.pg .nb2 .ex i{position:static;transform:none;width:2.6mm;height:3.4mm;display:inline-block}.pg .nb2 .ex i.f{background:#222;border-color:#222}.pg .nb2 .ex u{text-decoration:none;color:#8794a3;font-size:7pt}
.pg .ft{position:absolute;left:100mm;width:177mm;top:193mm;font-size:7pt;color:#8794a3;text-align:center}@media print{.pg{box-shadow:none;margin:0}}`;
 const html=`<style>${css}</style><div class="pg" data-n="${n}" data-ori="L">${mk}<div class="fr"></div><div class="hb"><div class="t0"><small>OMR</small><b>답안지</b></div><div class="t1"><span>${esc(w.title)}</span></div><div class="t2">${esc(subjN)}${mock&&cv.area?' · '+esc(cv.area):''}<br>${n}문항 · ${new Date(w.t).toLocaleDateString('ko-KR')}</div></div>
 <div class="sh" style="left:24mm;top:38mm;width:70mm">인적사항</div>
 <span class="bt" style="left:24mm;top:46.5mm">성 명</span><div class="box" style="left:44mm;top:43mm;width:50mm;height:7mm"></div>
 <span class="bt" style="left:24mm;top:56.5mm">${mock?'선택과목':'학교·학원'}</span><div class="box" style="left:44mm;top:53mm;width:50mm;height:7mm">${mock?`<span class="fx" style="left:2mm;top:2.2mm;position:absolute">${esc(subjN)} (${sc})</span>`:`<span class="fx" style="left:2mm;top:2.4mm;position:absolute;font-size:8.5pt">${esc(w.academy||'')}</span>`}</div>
 <span class="bt" style="left:24mm;top:66.5mm">응시일</span><div class="box" style="left:44mm;top:63mm;width:50mm;height:7mm"></div>
 <div class="sh" style="left:24mm;top:70.8mm;width:70mm">${mock?'수험번호 · 과목번호':'학년 · 반 · 번호'} 표기</div><div class="ip"></div>${grpLab}${ib}
 <div class="sh" style="left:24mm;top:135mm;width:70mm">확인란</div>
 <span class="bt" style="left:24mm;top:145.5mm">감독 확인</span><div class="box" style="left:44mm;top:139mm;width:22mm;height:13mm"></div><span class="bt" style="left:69mm;top:145.5mm;font-size:7.5pt">점수</span><div class="box" style="left:78mm;top:139mm;width:16mm;height:13mm"></div>
 <div class="qrb">${qrSvg(url)}<b>${fmtNo(w.id)}</b></div>
 <div class="nb2"><em>답안 표기 방법</em><div class="ex"><i class="f"></i>올바른 표기</div><div class="ex"><u>✓ ✗ ○ ◔</u>잘못된 표기</div>칸 안을 <b style="position:static;transform:none;font-size:inherit;color:#1b2430">진하게 모두</b> 칠해요. 복수 정답은 모두 칠하고, 네 모서리의 검은 네모는 가리지 마세요.</div>
 ${zeb.join('')}${blk.join('')}${nums.join('')}${bub}
 <div class="ft">${esc(w.title)} · 번호 ${fmtNo(w.id)} · 채점 화면의 「OMR 사진으로 입력」으로 읽어요${n>G.cap?` · ${G.cap}번까지만 인쇄돼요`:''}</div></div>`;
 mount($('#wsPaper'),html);omrBar(id,'L');
 let ps=document.getElementById('wsPrintStyle');if(!ps){ps=document.createElement('style');ps.id='wsPrintStyle';document.head.appendChild(ps)}ps.textContent='@page{size:A4 landscape;margin:0}';$('#wsView').classList.add('open');pushNav()}

function omrBar(id,ori){$('#wsBar').innerHTML=`<button class="p" onclick="window.print()">인쇄</button><span class="seg" style="margin:0 8px"><label><input type="radio" name="oo" ${ori==='L'?'checked':''} onchange="localStorage.setItem('omr_ori','L');omrCard('${id}','L')"><span>가로형</span></label><label><input type="radio" name="oo" ${ori==='P'?'checked':''} onchange="localStorage.setItem('omr_ori','P');omrCard('${id}','P')"><span>세로형(예전)</span></label></span><button class="wsx" onclick="closeWs()" title="닫기" aria-label="닫기">✕</button><span class="m">OMR 답안지 · A4 ${ori==='L'?'가로':'세로'} · 100% 크기로 인쇄하세요</span>`}

function omrCardP(id){const w=WSH.find(x=>x.id===id);if(!w)return;const qs=w.codes.map(c=>byCode[c]).filter(Boolean);const n=qs.length;const mock=!!w.mock;const G=omrGeom(qs,mock);
 const base=(CF.pub||location.href).split('#')[0].split('?')[0],url=base+'#ws='+w.id;const cv=w.cover||{};const subjN=cv.subject||SNAME[(qs[0]&&subjOf(qs[0].code))||SUBJ]||'';const sc=OMRSUBJ[(qs[0]&&subjOf(qs[0].code))||SUBJ]||'';
 const RD='#e0452b',RL='#fdeeea';
 const nums=qs.slice(0,G.cap).map((q,i)=>{const c=Math.floor(i/G.per),r=i%G.per,x=G.xs0+c*G.colW,y=G.y0+r*G.rowH+G.rowH/2;return `<b style="left:${x+10}mm;top:${y}mm">${i+1}</b>${q.set==='blank'||q.set==='essay'?`<span class="bl" style="left:${x+12}mm;top:${y}mm">직접 풀이·입력</span>`:''}`}).join('');
 const bw=Math.min(G.colW-2,12+G.mo*G.optP+3),blk=[];
 for(let c=0;c<G.cols;c++){const x=G.xs0+c*G.colW,cnt=Math.min(G.per,n-c*G.per);if(cnt<=0)break;
  blk.push(`<div class="bk" style="left:${x+1}mm;top:${G.y0-7}mm;width:${bw}mm;height:${7+cnt*G.rowH+1}mm"></div><div class="bh" style="left:${x+1}mm;top:${G.y0-7}mm;width:${bw}mm"><span style="width:10mm">번호</span><span style="flex:1">답  란</span></div>`);
  for(let r=5;r<cnt;r+=5)blk.push(`<div class="sp" style="left:${x+1}mm;top:${G.y0+r*G.rowH}mm;width:${bw}mm"></div>`)}
 const fs=Math.max(5,Math.min(7,G.d*1.25)).toFixed(1);
 const bub=G.b.map(p=>`<i style="left:${p.x}mm;top:${p.y}mm;width:${(G.d*.78).toFixed(2)}mm;height:${G.d}mm">${(optsOf(qs[p.q])[p.o])||p.o+1}</i>`).join('');
 const ib=G.info.map(g=>g.pts.map(p=>`<i class="n" style="left:${p.x}mm;top:${p.y}mm">${g.lab[p.r]}</i>`).join('')).join('');
 const grpPos={};G.info.forEach(g=>{(grpPos[g.grp]=grpPos[g.grp]||[]).push(g.x)});
 const grpLab=Object.entries(grpPos).map(([k,xs])=>`<u class="gl" style="left:${(Math.min(...xs)+Math.max(...xs))/2}mm;top:37.4mm">${k}</u>${xs.map(x=>`<span class="gx" style="left:${x}mm;top:41.8mm"></span>`).join('')}`).join('');
 const mk=OMRMK.map(([x,y])=>`<s style="left:${x}mm;top:${y}mm"></s>`).join('');
 const html=`<style>.pg{width:210mm;height:297mm;background:#fff;margin:0 auto 6mm;box-shadow:0 2px 12px #0002;font-family:Pretendard,PretendardLocal,sans-serif;color:#1b2430;position:relative;overflow:hidden;break-after:page;-webkit-print-color-adjust:exact;print-color-adjust:exact}.pg *{box-sizing:border-box}.pg s{position:absolute;width:${OMRMS}mm;height:${OMRMS}mm;background:#000;transform:translate(-50%,-50%);text-decoration:none}
.pg i{position:absolute;border:.3mm solid ${RD};border-radius:50%;transform:translate(-50%,-50%);background:#fff;color:${RD};font-style:normal;font-size:${fs}pt;line-height:1;display:flex;align-items:center;justify-content:center}.pg i.n{width:3.1mm;height:3.8mm;font-size:5.2pt}
.pg b{position:absolute;transform:translate(-100%,-50%);font-size:9.5pt;font-weight:700;color:${RD}}.pg .bl{position:absolute;transform:translate(0,-50%);font-size:7.5pt;color:#8794a3}.pg .gl{position:absolute;transform:translate(-50%,-50%);text-decoration:none;font-size:8.5pt;font-weight:700;color:${RD}}.pg .gx{position:absolute;transform:translate(-50%,-50%);width:4.6mm;height:4.6mm;border:.35mm solid ${RD};background:#fff}
.pg .box{position:absolute;border:.35mm solid ${RD};background:#fff}.pg .bt{position:absolute;font-size:8.5pt;color:${RD};font-weight:700;transform:translate(0,-50%)}.pg .fx{position:absolute;font-size:10.5pt}
.pg .fr{position:absolute;left:18mm;top:34mm;width:174mm;height:243mm;border:.7mm solid ${RD}}.pg .fr2{position:absolute;left:19.6mm;top:35.4mm;width:170.8mm;height:240.2mm;border:.2mm solid ${RD}}.pg .ip{position:absolute;left:104mm;top:36mm;width:${mock?86:66}mm;height:52.5mm;background:${RL}}
.pg .bk{position:absolute;border:.35mm solid ${RD}}.pg .bh{position:absolute;height:4.6mm;background:${RD};color:#fff;font-size:7.5pt;font-weight:700;display:flex;align-items:center;text-align:center}.pg .bh span{display:block}.pg .sp{position:absolute;height:0;border-top:.2mm dashed #f0a090}
.pg .tb{position:absolute;left:24mm;top:10mm;width:30mm;height:14mm;background:${RD};color:#fff;border-radius:1.5mm;text-align:center;font-weight:800;font-size:17pt;letter-spacing:.12em;line-height:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding-left:.12em}.pg .tb small{font-size:6.5pt;letter-spacing:.3em;font-weight:600;margin-bottom:1mm;padding-left:.3em}
.h{position:absolute;left:58mm;width:104mm;top:10mm}.h strong{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:${mock?'15':'13.5'}pt;line-height:1.25;color:${RD}}.h span{display:block;font-size:9pt;color:#586476;margin-top:1.2mm}
.qrb{position:absolute;left:165mm;top:8mm;width:22mm;text-align:center}.qrb svg{width:22mm;height:22mm;display:block}.qrb b{position:static;transform:none;display:block;font-family:ui-monospace,Menlo,monospace;font-size:7pt;letter-spacing:.1em;font-weight:400;margin-top:.5mm;color:#1b2430}
.note{position:absolute;left:24mm;right:24mm;bottom:12mm;font-size:7.4pt;color:#586476;line-height:1.5;text-align:center}.note b{position:static;transform:none;font-weight:700;font-size:inherit;color:${RD}}.note .ok{color:#111}.ft{position:absolute;left:24mm;right:24mm;bottom:8mm;font-size:7.5pt;color:#8794a3;text-align:center}@media print{.pg{box-shadow:none;margin:0}}</style>
 <div class="pg" data-n="${n}">${mk}<div class="tb"><small>OMR</small>답안지</div><div class="h"><strong>${esc(w.title)}</strong><span>${esc(subjN)}${mock&&cv.area?' · '+esc(cv.area):''} · ${n}문항 · ${new Date(w.t).toLocaleDateString('ko-KR')}</span></div>
 <div class="qrb">${qrSvg(url)}<b>${fmtNo(w.id)}</b></div><div class="fr"></div><div class="fr2"></div><div class="ip"></div>
 <span class="bt" style="left:24mm;top:41mm">성 명</span><div class="box" style="left:38mm;top:37.5mm;width:54mm;height:7.5mm"></div>
 <span class="bt" style="left:24mm;top:53mm">${mock?'선택과목':'학교·학원'}</span><div class="box" style="left:38mm;top:49.5mm;width:54mm;height:7.5mm">${mock?`<span class="fx" style="left:2mm;top:1mm;position:absolute">${esc(subjN)} (${sc})</span>`:`<span class="fx" style="left:2mm;top:1mm;position:absolute;font-size:9pt">${esc(w.academy||'')}</span>`}</div>
 <span class="bt" style="left:24mm;top:65mm">응시일</span><div class="box" style="left:38mm;top:61.5mm;width:54mm;height:7.5mm"></div>
 <span class="bt" style="left:24mm;top:82mm">감독 확인</span><div class="box" style="left:38mm;top:73.5mm;width:25mm;height:14mm"></div><span class="bt" style="left:66mm;top:82mm">점 수</span><div class="box" style="left:76mm;top:73.5mm;width:16mm;height:14mm"></div>
 ${grpLab}${ib}${blk.join('')}${nums}${bub}
 <div class="note"><b>답안 표기 방법</b> 올바른 표기 <span class="ok">●</span> · 잘못된 표기 ✓ ✗ ○ — 정답 칸을 <b>진하게 칠하세요</b>(✓ 표시는 인식이 어려워요). 복수 정답은 모두 칠합니다. ${mock?'수험번호·과목번호·형도 해당 숫자를 칠하세요. ':'학년·반·번호도 해당 숫자를 칠하세요. '}네 모서리의 검은 네모는 가리지 마세요.</div>
 <div class="ft">${esc(w.title)} · 번호 ${fmtNo(w.id)} · 채점 화면의 「OMR 사진으로 입력」으로 읽어요${n>G.cap?` · ${G.cap}번까지만 인쇄돼요`:''}</div></div>`;
 mount($('#wsPaper'),html);omrBar(id,'P');
 let ps=document.getElementById('wsPrintStyle');if(!ps){ps=document.createElement('style');ps.id='wsPrintStyle';document.head.appendChild(ps)}ps.textContent='@page{size:A4;margin:0}';$('#wsView').classList.add('open');pushNav()}

function omrSolve(A,b){const n=b.length;for(let i=0;i<n;i++){let m=i;for(let r=i+1;r<n;r++)if(Math.abs(A[r][i])>Math.abs(A[m][i]))m=r;[A[i],A[m]]=[A[m],A[i]];[b[i],b[m]]=[b[m],b[i]];for(let r=i+1;r<n;r++){const f=A[r][i]/A[i][i];for(let c=i;c<n;c++)A[r][c]-=f*A[i][c];b[r]-=f*b[i]}}
 const x=Array(n).fill(0);for(let i=n-1;i>=0;i--){let s=b[i];for(let c=i+1;c<n;c++)s-=A[i][c]*x[c];x[i]=s/A[i][i]}return x}

function omrHomography(src,dst){const A=[],b=[];for(let i=0;i<4;i++){const [x,y]=src[i],[u,v]=dst[i];A.push([x,y,1,0,0,0,-x*u,-y*u]);b.push(u);A.push([0,0,0,x,y,1,-x*v,-y*v]);b.push(v)}const h=omrSolve(A,b);return [...h,1]}

const omrMap=(H,x,y)=>{const d=H[6]*x+H[7]*y+1;return [(H[0]*x+H[1]*y+H[2])/d,(H[3]*x+H[4]*y+H[5])/d]};

async function omrLoadImg(file){let bmp;try{bmp=await createImageBitmap(file,{imageOrientation:'from-image'})}catch(e){bmp=await createImageBitmap(file)}
 const sc=Math.min(1,1800/Math.max(bmp.width,bmp.height)),w=Math.round(bmp.width*sc),h=Math.round(bmp.height*sc);const cv=document.createElement('canvas');cv.width=w;cv.height=h;const cx=cv.getContext('2d',{willReadFrequently:true});cx.drawImage(bmp,0,0,w,h);return {cv,cx,w,h}}

function omrBinary(cx,w,h){const d=cx.getImageData(0,0,w,h).data,n=w*h,g=new Float32Array(n);for(let i=0;i<n;i++)g[i]=d[i*4]/* 빨간 인쇄(틀·번호)는 빨간 채널에서 밝게 보여 사라지고, 연필·사인펜 자국과 검은 모서리 표시만 남습니다 */;
 const W1=w+1,I=new Float64Array(W1*(h+1));for(let y=0;y<h;y++){let row=0;for(let x=0;x<w;x++){row+=g[y*w+x];I[(y+1)*W1+x+1]=I[y*W1+x+1]+row}}
 const R=Math.max(14,Math.round(Math.min(w,h)/20)),bin=new Uint8Array(n);
 for(let y=0;y<h;y++){const y0=Math.max(0,y-R),y1=Math.min(h,y+R+1);for(let x=0;x<w;x++){const x0=Math.max(0,x-R),x1=Math.min(w,x+R+1);const s=I[y1*W1+x1]-I[y0*W1+x1]-I[y1*W1+x0]+I[y0*W1+x0];const mean=s/((y1-y0)*(x1-x0));bin[y*w+x]=g[y*w+x]<mean*.8&&g[y*w+x]<175?1:0}}
 return bin}

function omrMarkers(bin,w,h){const lab=new Int32Array(w*h),comps=[];let id=0;const st=[];
 for(let s=0;s<w*h;s++){if(!bin[s]||lab[s])continue;id++;let a=0,sx=0,sy=0,x0=w,x1=0,y0=h,y1=0;st.push(s);lab[s]=id;
  while(st.length){const p=st.pop(),x=p%w,y=(p-x)/w;a++;sx+=x;sy+=y;if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;
   if(x>0&&bin[p-1]&&!lab[p-1]){lab[p-1]=id;st.push(p-1)}if(x<w-1&&bin[p+1]&&!lab[p+1]){lab[p+1]=id;st.push(p+1)}if(y>0&&bin[p-w]&&!lab[p-w]){lab[p-w]=id;st.push(p-w)}if(y<h-1&&bin[p+w]&&!lab[p+w]){lab[p+w]=id;st.push(p+w)}}
  const bw=x1-x0+1,bh=y1-y0+1;if(a<120||bw<8||bh<8||bw>.14*Math.max(w,h)||bh>.14*Math.max(w,h))continue;const asp=bw/bh,fill=a/(bw*bh);if(asp<.55||asp>1.6||fill<.66)continue;comps.push({a,cx:sx/a,cy:sy/a,bw,bh})}
 if(comps.length<4)return null;const amax=Math.max(...comps.map(c=>c.a));const big=comps.filter(c=>c.a>=amax*.45);
 const cs=[[0,0],[w,0],[0,h],[w,h]];const pick=cs.map(([qx,qy])=>{let best=null,bd=1e18;big.forEach(c=>{if((c.cx<w/2)!==(qx===0)||(c.cy<h/2)!==(qy===0))return;const dd=(c.cx-qx)**2+(c.cy-qy)**2;if(dd<bd){bd=dd;best=c}});return best});
 return pick.every(Boolean)?pick:null}

async function omrRead(file,qs){const im=await omrLoadImg(file);const bin=omrBinary(im.cx,im.w,im.h);const mk=omrMarkers(bin,im.w,im.h);
 if(!mk)throw new Error('markers');
 /* 모서리 네모 중 하나가 눈에 띄게 크면(가로형: 오른쪽 아래) 그것으로 종이 방향을 알아냅니다. 같은 크기면 예전 세로형 */
 let src=OMRMK,pts=mk,land=false;
 {const A=mk.map(c=>c.a);for(let k=0;k<4;k++){const o=A.filter((_,i)=>i!==k),mo=(o[0]+o[1]+o[2])/3;
   if(A[k]>mo*1.42&&Math.max(...o)<A[k]&&Math.max(...o)/Math.min(...o)<1.3){land=true;const cw=[mk[0],mk[1],mk[3],mk[2]],ci=[0,1,3,2][k],sh=(ci-2+4)%4,rot=[0,1,2,3].map(i=>cw[(i+sh)%4]);pts=[rot[0],rot[1],rot[3],rot[2]];src=OMRMKL;break}}}
 const H=omrHomography(src,pts.map(c=>[c.cx,c.cy]));const G=omrGeom(qs,!!(cur&&cur.ws&&cur.ws.mock),land);const [ux0,uy0]=omrMap(H,src[0][0],src[0][1]),[vx0,vy0]=omrMap(H,src[0][0]+100,src[0][1]);const s=Math.hypot(vx0-ux0,vy0-uy0)/100;
 const rr=Math.max(2,G.d*.36*s),fills=qs.map(()=>[]);
 G.b.forEach(p=>{const [u,v]=omrMap(H,p.x,p.y);let t=0,dk=0;const R=Math.ceil(rr);for(let y=-R;y<=R;y++)for(let x=-R;x<=R;x++){if(x*x+y*y>rr*rr)continue;const px=Math.round(u+x),py=Math.round(v+y);if(px<0||py<0||px>=im.w||py>=im.h)continue;t++;dk+=bin[py*im.w+px]}
  fills[p.q][p.o]=t?dk/t:0;p.u=u;p.v=v});
 const res=qs.map((q,i)=>{const f=fills[i];if(!f.length)return {skip:true,f:[]};const mx=Math.max(...f);const marked=f.map((x,k)=>x>=.32&&x>=mx*.55?k:-1).filter(k=>k>=0);const multi=isMulti(q);
  return {f,marked,flag:!marked.length?'none':(!multi&&marked.length>1?'multi':'')}});
 const fillAt=(x,y,r)=>{const [u,v]=omrMap(H,x,y);let t=0,dk=0;const R=Math.ceil(r);for(let yy=-R;yy<=R;yy++)for(let xx=-R;xx<=R;xx++){if(xx*xx+yy*yy>r*r)continue;const px=Math.round(u+xx),py=Math.round(v+yy);if(px<0||py<0||px>=im.w||py>=im.h)continue;t++;dk+=bin[py*im.w+px]}return {f:t?dk/t:0,u,v}};
 const info={};G.info.forEach(g=>{const rr2=Math.max(1.6,g.d*.36*s);const f=g.pts.map(p=>{const o=fillAt(p.x,p.y,rr2);p.u=o.u;p.v=o.v;return o.f});const mx=Math.max(...f);const on=f.map((x,r)=>x>=.32&&x>=mx*.6?r:-1).filter(r=>r>=0);const ch=on.length===0?'-':on.length>1?'?':g.lab[on[0]];(info[g.grp]=info[g.grp]||[]).push(ch);g.on=on});
 return {res,G,H,im,mk,s,rr,info}}

function omrOverlay(R){const cv=document.createElement('canvas');const im=R.im;cv.width=im.w;cv.height=im.h;const cx=cv.getContext('2d');cx.drawImage(im.cv,0,0);cx.lineWidth=Math.max(2,R.rr*.35);
 R.mk.forEach(c=>{cx.strokeStyle='#2f7fd0';cx.strokeRect(c.cx-c.bw/2-3,c.cy-c.bh/2-3,c.bw+6,c.bh+6)});
 R.G.info.forEach(g=>g.pts.forEach(p=>{if(g.on&&g.on.includes(p.r)){cx.beginPath();cx.arc(p.u,p.v,R.rr*.8,0,7);cx.strokeStyle='#7048e8';cx.fillStyle='#7048e855';cx.fill();cx.stroke()}}));
 R.G.b.forEach(p=>{const r=R.res[p.q];if(!r||r.skip)return;const on=r.marked.includes(p.o);cx.beginPath();cx.arc(p.u,p.v,R.rr*(on?1.25:.5),0,7);cx.strokeStyle=on?(r.flag?'#e8590c':'#2b9a5b'):'#9aa7b6';cx.fillStyle=on?(r.flag?'#e8590c55':'#2b9a5b55'):'transparent';if(on)cx.fill();cx.stroke()});return cv}

let OMRS=null;

function omrOpen(){const bx=$('#cfgBox');if(bx)bx.classList.remove('omrw');if(!cur||!cur.ws){alert('OMR 사진 읽기는 학습지 번호로 채점할 때 쓸 수 있어요.');return}
 OMRS={R:null};const m=$('#cfg');$('#cfgBox').innerHTML=`<h2 style="margin-top:0">OMR 사진으로 입력</h2><div class="m">인쇄한 OMR 답안지를 네 모서리가 모두 보이게 찍어 올리세요. 밝은 곳에서 위에서 곧게 찍을수록 정확해요.</div>
 <div class="row" style="margin:12px 0"><button class="p" onclick="$('#omrf').click()">📷 사진 찍기·선택</button><input id="omrf" type="file" accept="image/*" capture="environment" style="display:none" onchange="omrPick(this.files[0])"><button class="s" onclick="closeCfg()">닫기</button></div><div id="omrout"></div>`;m.classList.add('open')}

async function omrPick(file){if(!file)return;const out=$('#omrout');out.innerHTML='<div class="m">읽는 중…</div>';
 try{const R=await omrRead(file,cur.qs);OMRS.R=R;omrShow()}catch(e){out.innerHTML=`<div class="hint">${e.message==='markers'?'종이 네 모서리의 검은 네모를 찾지 못했어요. 종이 전체가 화면에 들어오게, 그림자 없이 다시 찍어 주세요.':'사진을 읽지 못했어요. 다른 사진으로 다시 시도해 주세요.'}</div>`}}

function omrShow(){const R=OMRS.R,out=$('#omrout');const flags=R.res.filter(r=>r.flag).length,read=R.res.filter(r=>!r.skip).length;
 const infoTxt=Object.entries(R.info).map(([k,v])=>k+' <b>'+v.join('')+'</b>').join(' · ');
 $('#cfgBox').classList.add('omrw');
 out.innerHTML=`<div class="omrs"><div class="omrl"><div id="omrcv"></div><div class="m" style="margin-top:6px">초록=읽은 답 · 주황=확인 필요 · 보라=인적사항</div></div>
 <div class="omrr"><div class="omrsum"><span class="omrst ok"><b>${read}</b>문항 읽음</span><span class="omrst ${flags?'fl':'ok'}"><b>${flags}</b>확인 필요</span></div>${infoTxt?`<div class="m" style="margin:6px 0">인적사항 ${infoTxt}</div>`:''}
 <div class="omrg">${R.res.map((r,i)=>{if(r.skip)return `<div class="omrq"><b>${i+1}</b><span class="m">직접 입력</span></div>`;const q=cur.qs[i];const o=optsOf(q);return `<div class="omrq ${r.flag?'fl':''}"><b>${i+1}</b>${o.map((lb,k)=>`<button class="${r.marked.includes(k)?'on':''}" onclick="omrTog(${i},${k})">${lb}</button>`).join('')}</div>`}).join('')}</div>
 <div class="row" style="margin-top:10px;justify-content:flex-end"><button class="s" onclick="$('#omrf').click()">다시 찍기</button><button class="p" onclick="omrApply()">이 답으로 입력</button></div></div></div>`;
 const box=$('#omrcv');box.appendChild(omrOverlay(R));const c=box.firstChild;c.style.width='100%';c.style.display='block'}

function omrTog(i,k){const r=OMRS.R.res[i];const q=cur.qs[i];if(isMulti(q)){const s=new Set(r.marked);s.has(k)?s.delete(k):s.add(k);r.marked=[...s].sort()}else r.marked=r.marked.includes(k)?[]:[k];r.flag=!r.marked.length?'none':(!isMulti(q)&&r.marked.length>1?'multi':'');omrShow()}

function omrApply(){const R=OMRS.R;let n=0;R.res.forEach((r,i)=>{if(r.skip)return;const q=cur.qs[i],o=optsOf(q);const val=r.marked.map(k=>o[k]).join(',');n++;
  if(cur.mark)cur.ans[i]=val&&ok(q,val)?ansOf(q):'';else cur.ans[i]=val});
 closeCfg();render();toast('OMR '+n+'문항을 입력했어요. 확인 후 채점하세요.')}
