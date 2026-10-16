/* dev.js — 개발자 페이지 (index.html 이 개발자 탭을 처음 열 때 불러옵니다)
   왼쪽에서 항목을 고르면 오른쪽에 내용이 나옵니다. 서버 기능은 supabase/sql_15_developer.sql 이 준비돼 있어야 해요. */
const DEVNAV=[
 ['개요',[['home','대시보드'],['daily','사용량 분석']]],
 ['콘텐츠',[['notice','사이트 공지'],['db','문항 관리'],['ovr','수정·숨김 목록'],['types','과목·유형 현황'],['scan','DB 점검'],['qstat','문항 통계']]],
 ['사용자',[['users','계정·개발자'],['students','학생 목록'],['signups','가입 신청'],['attempts','최근 채점'],['bugs','버그 신고']]],
 ['사이트',[['site','배너·과목·기능'],['maint','점검 모드'],['deploy','업데이트 배포']]],
 ['시스템',[['pk','패스키 진단'],['curl','eBook 효과 진단'],['srv','서버 설정 점검'],['health','연결·성능'],['store','브라우저 저장소'],['tools','정리·도구'],['about','버전 정보']]],
 ['기록',[['log','활동 기록'],['export','내보내기']]]
];
const DEVSEC=()=>DEVNAV.flatMap(g=>g[1]);
const DVP=()=>document.getElementById('devb');
const DVS={home:()=>devHome(),daily:()=>devDaily(),notice:()=>devNotice(),db:()=>devDb(),ovr:()=>devOvr(),types:()=>devTypes(),scan:()=>devScanView(),qstat:()=>devQstat(),
 users:()=>devUsers(),students:()=>devStudents(),signups:()=>devSignups(),attempts:()=>devAttempts(),bugs:()=>devBugs(),site:()=>devSite(),maint:()=>devMaint(),deploy:()=>devDeploy(),
 pk:()=>devPk(),curl:()=>devCurl(),srv:()=>devSrv(),health:()=>devHealth(),store:()=>devStore(),tools:()=>devTools(),about:()=>devAbout(),log:()=>devLogView(),export:()=>devExport()};
function devMain(){
 if(!DEV.ok){$('#main').innerHTML='<div class="card empty">개발자 계정으로 로그인해야 볼 수 있어요.</div>';return}
 if(!DVS[DEV.sec])DEV.sec='home';
 $('#main').innerHTML=`<div class="tsh"><div><h1>개발자</h1><p>사이트 운영 · 문항 DB · 사용자 · 시스템</p></div><div class="tsb"><span>${esc((sess&&sess.user&&sess.user.email)||'')}</span></div></div>
 <div class="dvl"><nav class="dvn">${DEVNAV.map(([g,a])=>`<h4>${g}</h4>${a.map(([k,l])=>`<button data-k="${k}" class="${DEV.sec===k?'on':''}" onclick="devGo('${k}')">${l}</button>`).join('')}`).join('')}</nav><div class="dvr"><div id="devb"></div></div></div>`;
 devRender()}
function devGo(sec){DEV.sec=sec;document.querySelectorAll('.dvn button').forEach(b=>b.classList.toggle('on',b.dataset.k===sec));devRender();const r=document.querySelector('.dvr');if(r&&innerWidth<760)r.scrollIntoView({behavior:'smooth',block:'start'})}
async function devRender(){const p=DVP();if(!p)return;p.innerHTML='<div class="card">'+ldg('불러오는 중…')+'</div>';
 try{await DVS[DEV.sec]()}catch(e){const q=DVP();if(q)q.innerHTML='<div class="card"><div class="hint">'+esc(e.message||'불러오지 못했어요')+'</div></div>'}}
const dvKpi=a=>`<div class="rkp">${a.map(([k,v,s])=>`<div><small>${k}</small><b>${v}</b>${s?`<small>${s}</small>`:''}</div>`).join('')}</div>`;
const dvBars=(a,lab)=>{const mx=Math.max(1,...a.map(x=>x[1]));return `<div class="rbars">${a.map(([d,n])=>`<div title="${d} · ${n}${lab||''}"><i style="height:${Math.round(n/mx*100)}%"></i></div>`).join('')}</div>${a.length?`<div class="m" style="display:flex;justify-content:space-between"><span>${a[0][0]}</span><span>${a[a.length-1][0]}</span></div>`:''}`};
const dvDay=t=>new Date(t).toLocaleDateString('ko-KR');
async function dvRpc(fn,args){const r=await rpc(fn,args||{});if(!r.ok)throw new Error(devErr(r));return r.json()}
const stripH=h=>String(h||'').replace(/<svg[\s\S]*?<\/svg>/g,' [그림] ').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
/* --- 문항 관리 --- */
const DB={subj:'ph',tag:'',q:'',lv:'',page:0,codeQ:''};
async function devDb(){
 const idx=BIDXS[DB.subj]||{};const tags=Object.entries(idx).sort((a,b)=>String(a[1].sub).localeCompare(String(b[1].sub))||a[0].localeCompare(b[0]));
 if(!DB.tag||!idx[DB.tag])DB.tag=tags[0]?tags[0][0]:'';
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">문항 관리</h3><div class="m">문제·해설·정답·난이도를 고치거나 숨길 수 있어요. 원본 파일은 그대로 두고, 고친 내용은 서버에 저장돼 모든 사용자에게 적용돼요.</div>
 <div class="rform"><label>과목<select onchange="DB.subj=this.value;DB.tag='';DB.page=0;devDb()">${Object.keys(SNAME).map(k=>`<option value="${k}" ${DB.subj===k?'selected':''}>${esc(SNAME[k])}</option>`).join('')}</select></label>
 <label>유형<select onchange="DB.tag=this.value;DB.page=0;devDb()">${tags.map(([t,b])=>`<option value="${t}" ${DB.tag===t?'selected':''}>${esc(b.sub)} ${esc(b.label)} (${b.n})</option>`).join('')}</select></label>
 <label>난이도<select onchange="DB.lv=this.value;DB.page=0;devDb()"><option value="">전체</option>${['하','중','상','최'].map(l=>`<option ${DB.lv===l?'selected':''}>${l}</option>`).join('')}</select></label>
 <label>검색(코드·본문)<input value="${esc(DB.q)}" onchange="DB.q=this.value.trim();DB.page=0;devDb()" placeholder="예) G-ph065-0001 또는 단어"></label></div>
 <div class="row" style="gap:8px;margin-top:8px"><input id="db_code" placeholder="코드로 바로 열기" value="${esc(DB.codeQ)}" style="max-width:240px"><button class="s" onclick="devDbOpen()">열기</button><span class="m">수정한 문항 ${Object.keys(QOV).length}개</span></div></div><div id="dbl"><div class="card">${ldg('문항을 불러오는 중…')}</div></div>`;
 if(!DB.tag)return;await ensureTags([DB.tag]);
 let L=DATA.concat(POOL[DB.subj]).filter((q,i,a)=>a.indexOf(q)===i&&q.code&&tagOf(q.code)===DB.tag);
 // 숨긴 문항은 풀에서 빠져 있으므로 개발자 목록에는 파일에서 다시 읽어 포함
 try{const r=await fetch(DIRS[DB.subj]+DB.tag+'.json');if(r.ok){const a=await r.json();L=a.map(x=>byCode[x.code]||ovApply(x))}}catch(e){}
 if(DB.lv)L=L.filter(q=>(q.lv||'중')===DB.lv);if(DB.q){const k=DB.q.toLowerCase();L=L.filter(q=>q.code.toLowerCase().includes(k)||stripH(q.q).toLowerCase().includes(k))}
 const P=25,pages=Math.max(1,Math.ceil(L.length/P));DB.page=Math.min(DB.page,pages-1);const cur=L.slice(DB.page*P,DB.page*P+P);
 document.getElementById('dbl').innerHTML=`<div class="card"><div class="row"><b>${L.length}문항</b><span class="m">${DB.page+1} / ${pages}쪽</span><span style="margin-left:auto;display:flex;gap:6px"><button class="s sm" ${DB.page?'':'disabled'} onclick="DB.page--;devDb()">‹</button><button class="s sm" ${DB.page<pages-1?'':'disabled'} onclick="DB.page++;devDb()">›</button></span></div>
 <div class="tw"><table><tr><th>코드</th><th>난이도</th><th>정답</th><th>본문</th><th></th></tr>${cur.map(q=>`<tr><td>${esc(q.code)}${QOV[q.code]?` <span class="tag ${QOV[q.code].hidden?'r':'y'}">${QOV[q.code].hidden?'숨김':'수정됨'}</span>`:''}</td><td>${esc(q.lv||'')}</td><td>${esc(q.ans)}</td><td class="l" style="max-width:420px">${esc(stripH(q.q).slice(0,90))}</td><td><button class="s sm" onclick="devQEdit('${q.code}')">수정</button></td></tr>`).join('')}</table></div></div>`}
async function devDbOpen(){const c=($('#db_code')||{}).value.trim();DB.codeQ=c;if(!c)return;await ensureCodes([c]);if(!byCode[c]){toast('그 코드의 문항을 찾지 못했어요');return}devQEdit(c)}
async function devQEdit(code){await ensureCodes([code]);let q=byCode[code];if(!q){try{const r=await fetch(DIRS[TAGSUBJ[tagOf(code)]||DB.subj]+tagOf(code)+'.json');(await r.json()).forEach(x=>{if(x.code===code)q=x})}catch(e){}}
 if(!q){toast('문항을 찾지 못했어요');return}const o=QOV[code]||{};
 $('#cfgBox').innerHTML=`<h2 style="margin-top:0">${esc(code)} <small class="m">${esc(q.sub||'')} ${esc(q.type||'')}</small></h2>
 <div class="dq" id="dq_prev"></div><div class="form"><label>정답<input id="dq_ans" value="${esc(q.ans)}"></label><label>난이도<select id="dq_lv">${['하','중','상','최'].map(l=>`<option ${(q.lv||'중')===l?'selected':''}>${l}</option>`).join('')}</select></label>
 <label>문제 HTML<textarea id="dq_q" rows="6" style="font-family:monospace;font-size:12px">${esc(q.q)}</textarea></label><label>해설 HTML<textarea id="dq_e" rows="5" style="font-family:monospace;font-size:12px">${esc(q.exp||'')}</textarea></label>
 <label>메모<input id="dq_n" value="${esc(o.note||'')}" maxlength="200"></label><label class="chk"><input type="checkbox" id="dq_h" ${o.hidden?'checked':''}> 이 문항 숨기기(출제·검색에서 제외)</label></div>
 <div class="row" style="gap:8px;margin-top:12px;justify-content:flex-end"><button class="s" onclick="devQPrev()">미리보기</button>${QOV[code]?`<button class="s" onclick="devQReset('${code}')">원래대로</button>`:''}<button class="s" onclick="closeCfg()">닫기</button><button class="p" onclick="devQSave('${code}')">저장</button></div>`;
 $('#cfg').classList.add('open');window._dqOrig={ans:q.ans,lv:q.lv||'중',q:q.q,exp:q.exp||''};devQPrev()}
function devQPrev(){const el=document.getElementById('dq_prev');if(!el)return;mount(el,'<div>'+$('#dq_q').value+'</div><div style="margin-top:10px">'+$('#dq_e').value+'</div>')}
async function devQSave(code){const f=window._dqOrig,patch={};const ans=$('#dq_ans').value.trim(),lv=$('#dq_lv').value,q=$('#dq_q').value,e=$('#dq_e').value;
 if(ans!==f.ans)patch.ans=ans;if(lv!==f.lv)patch.lv=lv;if(q!==f.q)patch.q=q;if(e!==f.exp)patch.exp=e;
 const old=(QOV[code]||{}).patch||{};const merged={...old,...patch};const hidden=$('#dq_h').checked,note=$('#dq_n').value.trim();
 if(!Object.keys(merged).length&&!hidden&&!note){toast('바뀐 내용이 없어요');return}
 const r=await sb('/rest/v1/q_overrides?on_conflict=code',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify({code,patch:merged,hidden,note,by_email:(sess&&sess.user&&sess.user.email)||'',updated_at:new Date().toISOString()})});
 if(!r.ok){toast(devErr(r));return}QOV[code]={code,patch:merged,hidden,note};if(byCode[code])ovApply(byCode[code]);ovAll();devLog('문항 수정',code+(hidden?' (숨김)':''));closeCfg();toast('저장했어요');devRender()}
async function devQReset(code){if(!confirm('이 문항의 수정·숨김을 모두 되돌릴까요? (화면에는 새로고침 후 원래대로 보여요)'))return;const r=await sb('/rest/v1/q_overrides?code=eq.'+encodeURIComponent(code),{method:'DELETE'});if(!r.ok){toast(devErr(r));return}delete QOV[code];devLog('문항 복원',code);closeCfg();toast('되돌렸어요 · 새로고침하면 원래 내용이 보여요');devRender()}
/* --- DB 점검 --- */
const SCAN={subj:'ph',run:false,res:null};
function devScanView(){const R=SCAN.res;document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">DB 점검</h3><div class="m">과목의 모든 문항을 불러와 빈 본문·빈 해설·이상한 정답·같은 본문 중복·난이도 누락을 찾아요. 문항이 많으면 몇 분 걸려요.</div>
 <div class="row" style="gap:8px;margin-top:8px"><select onchange="SCAN.subj=this.value;SCAN.res=null;devScanView()">${Object.keys(SNAME).map(k=>`<option value="${k}" ${SCAN.subj===k?'selected':''}>${esc(SNAME[k])}</option>`).join('')}</select><button class="p" ${SCAN.run?'disabled':''} onclick="devScanRun()">점검 시작</button><span class="m" id="scn_p"></span></div></div>
 ${R?`<div class="card"><div class="rkp">${[['검사한 문항',R.n],['문제 없음',R.n-R.bad.length],['의심 문항',R.bad.length]].map(([k,v])=>`<div><small>${k}</small><b>${v.toLocaleString()}</b></div>`).join('')}</div>${R.bad.length?`<div class="tw"><table><tr><th>코드</th><th>문제점</th><th></th></tr>${R.bad.slice(0,300).map(x=>`<tr><td>${esc(x.code)}</td><td class="l">${esc(x.why.join(' · '))}</td><td><button class="s sm" onclick="devQEdit('${x.code}')">수정</button></td></tr>`).join('')}</table></div>${R.bad.length>300?`<div class="m">처음 300건만 보여요.</div>`:''}`:'<div class="m">의심 문항이 없어요 🎉</div>'}<div class="row" style="margin-top:8px"><button class="s" onclick="devScanCsv()">CSV로 저장</button></div></div>`:''}`}
async function devScanRun(){SCAN.run=true;devScanView();const idx=BIDXS[SCAN.subj]||{},tags=Object.keys(idx);const bad=[],seen=new Map();let n=0;const P=document.getElementById('scn_p');
 for(let i=0;i<tags.length;i++){if(P)P.textContent=`불러오는 중 ${i+1} / ${tags.length}`;let a=[];try{const r=await fetch(DIRS[SCAN.subj]+tags[i]+'.json');if(r.ok)a=await r.json()}catch(e){}
  for(const q0 of a){const q=ovApply({...q0});n++;const why=[];const t=stripH(q.q);
   if(!t||t.length<8)why.push('본문이 비어 있음');if(!stripH(q.exp)||stripH(q.exp).length<4)why.push('해설이 비어 있음');
   if(q.set==='bank'||q.set==='mc'){if(!/^[1-5](,[1-5])*$/.test(String(q.ans)))why.push('정답 형식 이상('+q.ans+')')}
   if(!q.lv)why.push('난이도 없음');if(/undefined|NaN|\{\{|%s|\bnull\b/.test(q.q+q.exp))why.push('깨진 문자(undefined/NaN 등)');
   const k=t.slice(0,160)+'|'+(q.ans);if(seen.has(k))why.push('본문 중복('+seen.get(k)+')');else seen.set(k,q.code);
   if(why.length)bad.push({code:q.code,why})}
  await new Promise(r=>setTimeout(r,0))}
 SCAN.res={n,bad};SCAN.run=false;devLog('DB 점검',SNAME[SCAN.subj]+' '+n+'문항 · 의심 '+bad.length);devScanView()}
function devScanCsv(){const R=SCAN.res;if(!R)return;devDownload('db-scan-'+SCAN.subj+'.csv','코드,문제점\n'+R.bad.map(x=>x.code+',"'+x.why.join(' / ')+'"').join('\n'),'text/csv')}
function devDownload(name,text,type){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['﻿'+text],{type:(type||'application/json')+';charset=utf-8'}));a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},3000)}
/* --- 문항 통계 --- */
async function devQstat(){const r=await rpc('dev_qstats',{p_min:5});if(!r.ok)throw new Error(devErr(r));const L=await r.json();await ensureCodes(L.slice(0,60).map(x=>x.code));
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">정답률이 낮은 문항 <small class="m">5회 이상 푼 문항 · 모든 사용자 합산</small></h3>${L.length?`<div class="tw"><table><tr><th>코드</th><th>유형</th><th>푼 횟수</th><th>정답률</th><th></th></tr>${L.slice(0,100).map(x=>{const q=byCode[x.code]||{};return `<tr><td>${esc(x.code)}</td><td class="l">${esc(q.sub||'')} ${esc(q.type||'')}</td><td>${x.n}</td><td>${Math.round(x.right/x.n*100)}%</td><td><button class="s sm" onclick="devQEdit('${x.code}')">확인·수정</button></td></tr>`}).join('')}</table></div><div class="m" style="margin-top:6px">정답률이 지나치게 낮으면 정답이나 해설이 틀렸을 수 있어요.</div>`:'<div class="m">아직 통계가 쌓이지 않았어요.</div>'}</div>`}
/* --- 기능 켜기/끄기 · 내보내기 · 활동 기록 --- */
const FEATS=[['rec','학습 현황 탭'],['sim','오답 유사 학습지'],['chal','단원 챌린지'],['ebook','교재 eBook 뷰어']];
async function devLogView(){const r=await sb('/rest/v1/dev_log?select=who,act,info,t&order=t.desc&limit=100');if(!r.ok)throw new Error(devErr(r));const L=await r.json();
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">개발자 활동 기록</h3>${L.length?`<div class="tw"><table><tr><th>시각</th><th>계정</th><th>작업</th><th>내용</th></tr>${L.map(x=>`<tr><td>${new Date(+x.t).toLocaleString('ko-KR')}</td><td class="l">${esc(x.who||'')}</td><td>${esc(x.act)}</td><td class="l">${esc(x.info)}</td></tr>`).join('')}</table></div>`:'<div class="m">기록이 없어요.</div>'}</div>`}
async function devExport(){document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">데이터 내보내기</h3><div class="m">서버에 저장된 관리 데이터를 파일로 받아 보관하세요.</div><div class="row" style="gap:8px;margin-top:10px;flex-wrap:wrap">${[['site_notices','사이트 공지'],['site_config','사이트 설정'],['q_overrides','문항 수정·숨김'],['bug_reports','버그 신고'],['dev_log','활동 기록']].map(([t,n])=>`<button class="s" onclick="devExportGet('${t}')">${n} JSON</button>`).join('')}</div></div>`}
async function devExportGet(t){const r=await sb('/rest/v1/'+t+'?select=*&limit=10000');if(!r.ok){toast(devErr(r));return}devDownload(t+'-'+fmtD(Date.now())+'.json',JSON.stringify(await r.json(),null,1));devLog('내보내기',t)}

const devErr=r=>r.status===404?'서버에 15번 SQL이 아직 없어요. supabase/sql_15_developer.sql 을 SQL Editor에서 실행하세요.':r.status===401||r.status===403?'권한이 없어요(개발자 등록을 확인하세요).':'요청에 실패했어요 ('+r.status+')';
async function devNoticeTog(id,on){const r=await sb('/rest/v1/site_notices?id=eq.'+id,{method:'PATCH',headers:{Prefer:'return=minimal'},body:JSON.stringify({active:on})});if(!r.ok){toast(devErr(r));return}devRender();siteFetch()}
async function devNoticeDel(id){if(!confirm('이 공지를 삭제할까요?'))return;devLog('공지 삭제','#'+id);const r=await sb('/rest/v1/site_notices?id=eq.'+id,{method:'DELETE'});if(!r.ok){toast(devErr(r));return}devRender();siteFetch()}
async function devUsers(){const [a,b]=await Promise.all([rpc('dev_stats',{}),rpc('dev_users',{})]);if(!a.ok)throw new Error(devErr(a));const st=await a.json(),u=b.ok?await b.json():[];
 const K=[['teachers','선생님 계정'],['students','학생'],['attempts','채점 기록'],['worksheets','학습지'],['bugs','버그 신고'],['pending','가입 대기']];
 const me=sess&&sess.user&&sess.user.id;
 document.getElementById('devb').innerHTML=`<div class="card"><div class="rkp">${K.map(([k,v])=>`<div><small>${v}</small><b>${(+st[k]||0).toLocaleString()}</b></div>`).join('')}</div></div>
 <div class="card"><h3 style="margin-top:0">개발자 추가</h3><div class="row" style="gap:8px"><input id="dv_e" type="email" placeholder="가입된 선생님 계정 이메일" style="max-width:300px"><button class="p" onclick="devAdd()">개발자로 지정</button></div></div>
 <div class="card"><h3 style="margin-top:0">선생님 계정</h3><div class="tw"><table><tr><th>이메일</th><th>가입일</th><th>마지막 로그인</th><th>학생 수</th><th>상태</th><th></th></tr>${u.map(x=>`<tr><td class="l">${esc(x.email||'')}</td><td>${x.created_at?new Date(x.created_at).toLocaleDateString('ko-KR'):'-'}</td><td>${x.last_sign_in_at?new Date(x.last_sign_in_at).toLocaleDateString('ko-KR'):'-'}</td><td>${x.students}</td><td>${x.dev?'<span class="tag">개발자</span> ':''}${x.banned?'<span class="tag r">정지</span>':''}</td><td style="white-space:nowrap">${x.id===me?'':`${x.dev?`<button class="s sm" onclick="devRemove('${x.id}')">개발자 해제</button> `:''}<button class="s sm" onclick="devBan('${x.id}',${!x.banned})">${x.banned?'정지 해제':'계정 정지'}</button>`}</td></tr>`).join('')}</table></div></div>`}
async function devAdd(){const email=$('#dv_e').value.trim();if(!email)return;const r=await rpc('dev_add',{p_email:email});if(!r.ok){toast(devErr(r));return}toast(await r.json()?'개발자로 지정했어요':'그 이메일의 계정이 없어요');devLog('개발자 지정',email);devRender()}
async function devRemove(id){if(!confirm('개발자 권한을 해제할까요?'))return;const r=await rpc('dev_remove',{p_uid:id});if(!r.ok){toast(devErr(r));return}devLog('개발자 해제',id);devRender()}
async function devBan(id,ban){if(!confirm(ban?'이 계정을 정지할까요? 로그인할 수 없게 돼요.':'정지를 해제할까요?'))return;const r=await rpc('dev_ban',{p_uid:id,p_ban:ban});if(!r.ok){toast(devErr(r));return}devLog(ban?'계정 정지':'정지 해제',id);devRender()}
async function devBugs(){const r=await sb('/rest/v1/bug_reports?select=id,who,msg,info,t&order=t.desc&limit=100');if(!r.ok)throw new Error(devErr(r));const L=await r.json();
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">버그 신고 ${L.length}건</h3>${L.length?L.map(x=>`<div class="wn"><div class="wnh"><b>${esc(x.who||'선생님')}</b><span class="m">${new Date(+x.t).toLocaleString('ko-KR')}</span><button class="s sm" style="margin-left:auto" onclick="devBugDel(${x.id})">삭제</button></div><div style="margin:6px 0;white-space:pre-wrap">${esc(x.msg)}</div>${[...new Set(String(x.msg).match(/\b[A-Z]-?[a-z]*\d*-?\d{2,4}(?:-\d{3,4})?\b/g)||[])].filter(c=>tagOf(c)).slice(0,4).map(c=>`<button class="s sm" onclick="devQEdit('${c}')">${c} 열기</button>`).join(' ')}<div class="m" style="font-size:11px;word-break:break-all">${esc(JSON.stringify(x.info||{}).slice(0,300))}</div></div>`).join(''):'<div class="m">신고가 없어요.</div>'}</div>`}
async function devBugDel(id){if(!confirm('이 신고를 삭제할까요?'))return;const r=await sb('/rest/v1/bug_reports?id=eq.'+id,{method:'DELETE'});if(!r.ok){toast(devErr(r));return}devRender()}

/* --- 개요 --- */
async function devHome(){const [st,dl]=await Promise.all([dvRpc('dev_stats'),dvRpc('dev_daily',{p_days:14}).catch(()=>[])]);
 const K=[['선생님 계정',st.teachers],['학생',st.students],['채점 기록',st.attempts],['학습지',st.worksheets],['버그 신고',st.bugs],['가입 대기',st.pending]].map(([k,v])=>[k,(+v||0).toLocaleString()]);
 const nz=Object.keys(QOV).length;
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">한눈에 보기</h3>${dvKpi(K)}</div>
 <div class="card"><h3 style="margin-top:0">최근 14일 채점 횟수</h3>${dl.length?dvBars(dl.map(x=>[x.d,+x.n]),'회'):'<div class="m">기록이 없어요.</div>'}</div>
 <div class="card"><h3 style="margin-top:0">바로가기</h3><div class="row" style="gap:8px;flex-wrap:wrap"><button class="s" onclick="devGo('notice')">공지 올리기</button><button class="s" onclick="devGo('db')">문항 수정 <small class="m">(${nz}개 수정됨)</small></button><button class="s" onclick="devGo('scan')">DB 점검</button><button class="s" onclick="devGo('bugs')">버그 신고 ${st.bugs||0}건</button><button class="s" onclick="devGo('signups')">가입 대기 ${st.pending||0}건</button><button class="s" onclick="devGo('pk')">패스키 진단</button><button class="s" onclick="devGo('maint')">점검 모드</button></div></div>`}
async function devDaily(){const days=DEV.days||30;const L=await dvRpc('dev_daily',{p_days:days});
 const tot=L.reduce((a,x)=>a+ +x.n,0),q=L.reduce((a,x)=>a+ +x.q,0);
 document.getElementById('devb').innerHTML=`<div class="card"><div class="row"><h3 style="margin:0">사용량 분석</h3><div class="rtabs sm" style="margin:0 0 0 auto">${[7,14,30,90].map(d=>`<button class="${days===d?'on':''}" onclick="DEV.days=${d};devRender()">${d}일</button>`).join('')}</div></div>
 ${dvKpi([['채점 횟수',tot.toLocaleString()],['푼 문항',q.toLocaleString()],['활동한 날',L.length+'일'],['하루 평균',L.length?Math.round(q/L.length).toLocaleString()+'문항':'-']])}
 <h4>일별 푼 문항</h4>${dvBars(L.map(x=>[x.d,+x.q]),'문항')}</div>
 <div class="card"><div class="tw"><table><tr><th>날짜</th><th>채점</th><th>푼 문항</th><th>활동 계정</th></tr>${L.slice().reverse().map(x=>`<tr><td>${x.d}</td><td>${x.n}</td><td>${x.q}</td><td>${x.u}</td></tr>`).join('')}</table></div></div>`}
/* --- 공지 --- */
const NTPL=[['점검 안내','오늘 밤 12시부터 1시까지 점검이 있어요. 이 시간에는 채점 기록이 저장되지 않을 수 있어요.','점검'],['업데이트 안내','새 기능이 추가됐어요. 화면을 새로고침(캐시 비우기)하면 바로 보여요.','업데이트'],['이벤트','이번 주 목표를 달성하면 뱃지를 받아요!','이벤트']];
async function devNotice(){const r=await sb('/rest/v1/site_notices?select=*&order=t.desc&limit=100');if(!r.ok)throw new Error(devErr(r));const L=await r.json();
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">새 공지</h3><div class="row" style="gap:6px;flex-wrap:wrap;margin-bottom:8px"><span class="m">템플릿</span>${NTPL.map((x,i)=>`<button class="s sm" onclick="devNtpl(${i})">${x[0]}</button>`).join('')}</div>
 <div class="form"><label>제목<input id="dn_t" maxlength="60"></label><label>내용<textarea id="dn_b" rows="3" maxlength="600"></textarea></label><label>종류<select id="dn_g"><option>공지</option><option>업데이트</option><option>점검</option><option>이벤트</option></select></label>
 <label>게시 시작(선택)<input id="dn_s" type="datetime-local"></label><label>게시 종료(선택)<input id="dn_e" type="datetime-local"></label><label class="chk"><input type="checkbox" id="dn_p"> 처음 접속할 때 팝업으로도 띄우기</label></div>
 <div class="row" style="margin-top:10px;gap:8px"><button class="p" onclick="devNoticeAdd()">등록</button><span class="m">모든 학생·선생님의 알림 목록에 나타나요.</span></div></div>
 <div class="card"><h3 style="margin-top:0">등록된 공지 ${L.length}개</h3>${L.length?`<div class="tw"><table><tr><th>날짜</th><th>종류</th><th>제목</th><th>게시 기간</th><th>상태</th><th></th></tr>${L.map(x=>`<tr><td>${dvDay(+x.t)}</td><td>${esc(x.tag)}${x.popup?' · 팝업':''}</td><td class="l"><b>${esc(x.title)}</b><div class="m">${esc(x.body)}</div></td><td class="m">${x.start_at?dvDay(+x.start_at):'즉시'} ~ ${x.end_at?dvDay(+x.end_at):'계속'}</td><td>${x.active?'공개':'숨김'}</td><td style="white-space:nowrap"><button class="s sm" onclick="devNoticeTog(${x.id},${!x.active})">${x.active?'숨기기':'공개'}</button> <button class="s sm" onclick="devNoticeDel(${x.id})">삭제</button></td></tr>`).join('')}</table></div>`:'<div class="m">아직 없어요.</div>'}</div>`}
function devNtpl(i){const x=NTPL[i];$('#dn_t').value=x[0];$('#dn_b').value=x[1];$('#dn_g').value=x[2]}
async function devNoticeAdd(){const title=$('#dn_t').value.trim(),body=$('#dn_b').value.trim(),tag=$('#dn_g').value;if(!title){toast('제목을 입력하세요');return}
 const ms=id=>{const v=$(id).value;return v?new Date(v).getTime():null};
 const r=await sb('/rest/v1/site_notices',{method:'POST',headers:{Prefer:'return=minimal'},body:JSON.stringify({title,body,tag,popup:$('#dn_p').checked,start_at:ms('#dn_s'),end_at:ms('#dn_e')})});if(!r.ok){toast(r.status===400||r.status===404?'15번 SQL을 다시 실행해 주세요(새 열 추가)':devErr(r));return}devLog('공지 등록',title);toast('공지를 올렸어요');devRender();siteFetch()}
/* --- 수정·숨김 목록 / 과목·유형 현황 --- */
function devOvr(){const L=Object.values(QOV);
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">수정·숨김한 문항 ${L.length}개</h3>${L.length?`<div class="tw"><table><tr><th>코드</th><th>바뀐 항목</th><th>상태</th><th>메모</th><th></th></tr>${L.map(o=>`<tr><td>${esc(o.code)}</td><td class="l">${esc(Object.keys(o.patch||{}).map(k=>({ans:'정답',lv:'난이도',q:'문제',exp:'해설'}[k]||k)).join(', ')||'-')}</td><td>${o.hidden?'<span class="tag r">숨김</span>':'수정됨'}</td><td class="l">${esc(o.note||'')}</td><td style="white-space:nowrap"><button class="s sm" onclick="devQEdit('${o.code}')">열기</button> <button class="s sm" onclick="devQReset('${o.code}')">복원</button></td></tr>`).join('')}</table></div>`:'<div class="m">아직 없어요. 「문항 관리」에서 문항을 고치거나 숨기면 여기에 모여요.</div>'}</div>`}
async function devTypes(){const subj=DEV.tsubj||'ph';const idx=BIDXS[subj]||{};const rows=Object.entries(idx).sort((a,b)=>String(a[1].sub).localeCompare(String(b[1].sub))||a[0].localeCompare(b[0]));
 const ovCnt={};Object.values(QOV).forEach(o=>{const t=tagOf(o.code);if(t){(ovCnt[t]=ovCnt[t]||[0,0])[o.hidden?1:0]++}});
 const tot=rows.reduce((a,[t,b])=>a+b.n,0);
 document.getElementById('devb').innerHTML=`<div class="card"><div class="row"><h3 style="margin:0">과목·유형 현황</h3><select style="margin-left:auto" onchange="DEV.tsubj=this.value;devRender()">${Object.keys(SNAME).map(k=>`<option value="${k}" ${k===subj?'selected':''}>${esc(SNAME[k])}</option>`).join('')}</select></div>
 ${dvKpi([['유형',rows.length],['문제 은행 문항',tot.toLocaleString()],['교재 문항',(POOL[subj]||[]).filter(q=>q.set!=='bank').length.toLocaleString()]])}
 <div class="tw"><table><tr><th>소단원</th><th>유형</th><th>문항</th><th>하</th><th>중</th><th>상</th><th>수정/숨김</th><th></th></tr>${rows.map(([t,b])=>{const lv=b.lv||{};const o=ovCnt[t]||[0,0];return `<tr><td>${esc(b.sub)}</td><td class="l">${esc(b.label)}</td><td>${b.n}</td><td>${lv['하']||0}</td><td>${lv['중']||0}</td><td>${(lv['상']||0)+(lv['최']||0)}</td><td>${o[0]}/${o[1]}</td><td style="white-space:nowrap"><button class="s sm" onclick="DB.subj='${subj}';DB.tag='${t}';DB.page=0;devGo('db')">문항 보기</button> <button class="s sm" onclick="devTagHide('${subj}','${t}',true)">전체 숨김</button> <button class="s sm" onclick="devTagHide('${subj}','${t}',false)">숨김 해제</button></td></tr>`}).join('')}</table></div></div>`}
async function devTagHide(subj,tag,hide){if(!confirm(hide?'이 유형의 모든 문항을 숨길까요? (출제·검색에서 제외돼요)':'이 유형의 숨김을 모두 해제할까요?'))return;
 let a=[];try{const r=await fetch(DIRS[subj]+tag+'.json');a=await r.json()}catch(e){toast('문항을 불러오지 못했어요');return}
 const rows=a.filter(q=>hide||ovHidden(q.code)).map(q=>({code:q.code,patch:(QOV[q.code]||{}).patch||{},hidden:hide,note:(QOV[q.code]||{}).note||'',by_email:(sess&&sess.user&&sess.user.email)||'',updated_at:new Date().toISOString()}));
 if(!rows.length){toast('바꿀 문항이 없어요');return}
 for(let i=0;i<rows.length;i+=200){const r=await sb('/rest/v1/q_overrides?on_conflict=code',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify(rows.slice(i,i+200))});if(!r.ok){toast(devErr(r));return}}
 rows.forEach(o=>{QOV[o.code]={code:o.code,patch:o.patch,hidden:o.hidden,note:o.note}});ovAll();devLog(hide?'유형 전체 숨김':'유형 숨김 해제',subj+' '+tag+' '+rows.length+'개');toast(rows.length+'문항 처리했어요');devRender()}
/* --- 학생·가입·채점 --- */
async function devStudents(){const L=await dvRpc('dev_students',{p_limit:500});const q=(DEV.sq||'').toLowerCase();const F=L.filter(x=>!q||(x.name+' '+(x.teacher||'')+' '+(x.grade||'')).toLowerCase().includes(q));
 document.getElementById('devb').innerHTML=`<div class="card"><div class="row"><h3 style="margin:0">학생 ${L.length}명</h3><input type="search" placeholder="이름·선생님 검색" value="${esc(DEV.sq||'')}" style="margin-left:auto;max-width:240px" onchange="DEV.sq=this.value;devRender()"></div><div class="tw"><table><tr><th>이름</th><th>학년</th><th>담당 선생님</th><th>로그인</th><th>채점</th><th>마지막 채점</th></tr>${F.map(x=>`<tr><td>${esc(x.name)}</td><td>${esc(x.grade||'')}</td><td class="l">${esc(x.teacher||'')}</td><td>${x.has_login?'사용':'-'}</td><td>${x.attempts}</td><td>${x.last_t?dvDay(+x.last_t):'-'}</td></tr>`).join('')}</table></div></div>`}
async function devSignups(){const L=await dvRpc('dev_signups');const nm={pending:'대기',approved:'승인',rejected:'거절'};
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">학생 가입 신청 ${L.length}건</h3>${L.length?`<div class="tw"><table><tr><th>신청일</th><th>이름</th><th>학년</th><th>아이디</th><th>선생님</th><th>상태</th></tr>${L.map(x=>`<tr><td>${dvDay(+x.t)}</td><td>${esc(x.name)}</td><td>${esc(x.grade||'')}</td><td>${esc(x.login)}</td><td class="l">${esc(x.teacher||'')}</td><td>${nm[x.status]||esc(x.status)}</td></tr>`).join('')}</table></div>`:'<div class="m">신청이 없어요.</div>'}<div class="m" style="margin-top:6px">승인·거절은 각 선생님의 설정 ▸ 가입에서 해요.</div></div>`}
async function devAttempts(){const L=await dvRpc('dev_attempts',{p_limit:100});
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">최근 채점 ${L.length}건</h3><div class="tw"><table><tr><th>시각</th><th>학생</th><th>선생님</th><th>범위</th><th>점수</th></tr>${L.map(x=>`<tr><td>${new Date(+x.t).toLocaleString('ko-KR')}</td><td>${esc(x.student||'(선생님)')}</td><td class="l">${esc(x.teacher||'')}</td><td class="l">${esc((SETS[x.set]||x.set||'')+' '+(x.sub||''))}</td><td>${x.right}/${x.n}</td></tr>`).join('')}</table></div></div>`}
/* --- 사이트 설정 · 점검 · 배포 --- */
function devSite(){const b=SITE.cfg.banner||{on:false,text:'',level:'info'},off=snOff();
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">상단 안내 배너</h3><div class="m">켜면 모든 화면 맨 위에 한 줄 안내가 보여요.</div>
 <div class="form" style="margin-top:8px"><label>문구<input id="ds_t" maxlength="120" value="${esc(b.text||'')}"></label><label>색<select id="ds_l"><option value="info" ${b.level!=='warn'?'selected':''}>일반(파랑)</option><option value="warn" ${b.level==='warn'?'selected':''}>경고(주황)</option></select></label><label class="chk"><input type="checkbox" id="ds_on" ${b.on?'checked':''}> 배너 켜기</label></div></div>
 <div class="card"><h3 style="margin-top:0">과목 공개</h3><div class="m">체크하면 과목 선택에서 「점검 중」으로 잠겨요(데이터는 그대로).</div><div style="display:flex;gap:6px 18px;flex-wrap:wrap;margin-top:8px">${SUBJECTS.filter(s=>s.id).map(s=>`<label class="chk"><input type="checkbox" class="ds_off" value="${s.id}" ${off.includes(s.id)?'checked':''}> ${esc(s.n)} 잠그기</label>`).join('')}</div></div>
 <div class="card"><h3 style="margin-top:0">기능 켜기/끄기</h3><div class="m">끄면 모든 사용자 화면에서 해당 기능이 사라져요(문제가 생겼을 때 임시로 끄세요).</div><div style="display:flex;gap:6px 18px;flex-wrap:wrap;margin-top:8px">${FEATS.map(([k,n])=>`<label class="chk"><input type="checkbox" class="ds_ft" value="${k}" ${ft(k)?'checked':''}> ${n}</label>`).join('')}</div></div>
 <div class="row" style="gap:8px"><button class="p" onclick="devSiteSave()">저장</button></div>`}
async function devCfgSave(key,value){const r=await sb('/rest/v1/site_config?on_conflict=key',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify({key,value,updated_at:new Date().toISOString()})});if(!r.ok)throw new Error(devErr(r))}
async function devSiteSave(){const banner={on:$('#ds_on').checked,text:$('#ds_t').value.trim(),level:$('#ds_l').value},off=[...document.querySelectorAll('.ds_off:checked')].map(e=>e.value),foff=[...document.querySelectorAll('.ds_ft')].filter(e=>!e.checked).map(e=>e.value);
 try{await devCfgSave('banner',banner);await devCfgSave('subjects',{off});await devCfgSave('features',{off:foff})}catch(e){toast(e.message);return}
 devLog('사이트 설정 저장','배너 '+(banner.on?'켬':'끔')+' · 잠긴 과목 '+off.length+' · 끈 기능 '+foff.length);toast('저장했어요');await siteFetch();nav();devRender()}
function devMaint(){const m=SITE.cfg.maintenance||{on:false,msg:''};
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">점검 모드</h3><div class="m">켜면 개발자를 뺀 모든 사용자에게 「점검 중」 안내 화면이 덮여요. 큰 작업(DB 변경 등)을 할 때 쓰세요. 끄면 바로 풀려요(최대 1분).</div>
 <div class="form" style="margin-top:8px"><label>안내 문구<input id="dm_t" maxlength="160" value="${esc(m.msg||'잠시 점검 중이에요. 곧 다시 열게요!')}"></label><label class="chk"><input type="checkbox" id="dm_on" ${m.on?'checked':''}> 점검 모드 켜기</label></div>
 <div class="row" style="margin-top:10px"><button class="p" onclick="devMaintSave()">저장</button></div></div>`}
async function devMaintSave(){const v={on:$('#dm_on').checked,msg:$('#dm_t').value.trim()};if(v.on&&!confirm('점검 모드를 켜면 개발자 외 모두가 앱을 쓸 수 없어요. 켤까요?'))return;
 try{await devCfgSave('maintenance',v)}catch(e){toast(e.message);return}devLog('점검 모드',v.on?'켬':'끔');toast('저장했어요');await siteFetch();devRender()}
function devDeploy(){const r=SITE.cfg.reload||{};
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">새 버전 배포 후 하는 일</h3><div class="m">코드를 올린(PR 병합) 뒤 모든 사용자의 화면을 새 버전으로 바꾸게 해요. 접속 중이거나 다음에 접속하는 사용자의 저장된 앱 파일(캐시)이 지워지고 한 번 새로고침돼요. 기록·학습지는 지워지지 않아요.</div>
 <div class="row" style="margin-top:10px;gap:8px;flex-wrap:wrap"><button class="p" onclick="devReloadAll()">모두 새로고침 요구</button><span class="m">마지막 요청: ${r.at?new Date(r.at).toLocaleString('ko-KR'):'없음'}</span></div></div>
 <div class="card"><h3 style="margin-top:0">업데이트 공지 만들기</h3><div class="m">알림 목록에 업데이트 소식을 올려요.</div><div class="row" style="margin-top:8px"><button class="s" onclick="DEV.sec='notice';devMain();setTimeout(()=>devNtpl(1),300)">업데이트 안내 템플릿으로 열기</button></div></div>`}
async function devReloadAll(){if(!confirm('모든 사용자에게 새로고침을 요구할까요?'))return;try{await devCfgSave('reload',{at:Date.now()})}catch(e){toast(e.message);return}devLog('모두 새로고침 요구','');toast('요청했어요');await siteFetch();devRender()}
/* --- 패스키 진단 --- */
async function devPk(){const el=document.getElementById('devb');el.innerHTML=`<div class="card"><h3 style="margin-top:0">패스키 진단</h3><div class="m">브라우저·주소·서버 함수(Edge Function)를 차례로 확인해요.</div><div id="pkr" class="srvck" style="margin-top:10px"></div></div>`;
 const out=[];const add=(ok,l,m,h)=>{out.push(`<div class="${ok?'ok':'bad'}"><i></i><span>${l}</span><em>${esc(m)}${!ok&&h?' — '+esc(h):''}</em></div>`);document.getElementById('pkr').innerHTML=out.join('')};
 add(!!window.isSecureContext,'보안 연결(HTTPS)',location.origin,'패스키는 https 주소에서만 돼요');
 add(!!window.PublicKeyCredential,'브라우저 지원',window.PublicKeyCredential?'지원':'미지원','다른 브라우저(최신 Safari·Chrome)로 시도하세요');
 try{if(window.PublicKeyCredential&&PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable){const v=await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();add(v,'기기 인증(지문·얼굴·암호)',v?'사용 가능':'없음','기기에 화면 잠금/생체 인증을 설정하세요')}}catch(e){}
 add(cloud(),'서버 연결 설정',cloud()?base_():'설정 안 됨');
 if(!cloud())return;
 const t0=performance.now();let r,txt='';try{r=await fetch(base_()+'/functions/v1/passkey',{method:'POST',headers:hdr(),body:JSON.stringify({action:'ping'})});txt=await r.text()}catch(e){add(false,'함수 호출','연결 실패 ('+e.message+')','Edge Function이 배포됐는지, CORS(SITE_URL)가 이 주소와 같은지 확인하세요');return}
 const ms=Math.round(performance.now()-t0);let j=null;try{j=JSON.parse(txt)}catch(e){}
 if(r.status===401){add(false,'함수 호출','HTTP 401 ('+ms+'ms) '+txt.slice(0,80),'Edge Function 설정에서 「Verify JWT」(JWT 검증)를 끄세요. 로그인 전에도 호출해야 해서 꺼 둬야 해요');return}
 if(r.status===404){add(false,'함수 호출','HTTP 404','함수 이름이 passkey 인지, 배포됐는지 확인하세요');return}
 add(r.ok,'함수 호출','HTTP '+r.status+' ('+ms+'ms)',txt.slice(0,120));if(!j||!j.ok)return;
 add(j.rpID===location.hostname,'rpID(도메인)',j.rpID+' / 현재 '+location.hostname,'함수의 SITE_URL 이 지금 주소와 달라요. 값을 '+location.origin+' 로 바꾸세요. 주소를 바꿨다면 이전 패스키는 다시 등록해야 해요');
 add((j.origins||[]).includes(location.origin),'허용 주소(origin)',(j.origins||[]).join(', ')+' / 현재 '+location.origin,'SITE_URL 환경변수를 확인하세요(끝에 / 없이)');
 Object.entries(j.checks||{}).forEach(([k,v])=>{if(k==='SITE_URL')add(!/기본값/.test(v)||v.startsWith(location.origin),'SITE_URL',v,'환경변수가 없어 기본값(solvi.p-e.kr)을 써요. 다른 주소를 쓴다면 설정하세요');else add(v==='ok','DB · '+k,v,'setup.sql 10번을 실행했는지 확인하세요')})}
/* --- 서버 점검 · 연결 · 저장소 · 도구 · 버전 --- */
function devSrv(){document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">서버 설정 점검</h3><div class="m">setup.sql 로 만든 테이블·함수가 서버에 있는지 확인해요.</div><div class="row" style="margin-top:8px"><button class="p" onclick="srvCheck()">점검 시작</button></div><div id="srvck" class="srvck" style="margin-top:10px"></div></div>`;srvCheck()}
async function devHealth(){const el=document.getElementById('devb');el.innerHTML='<div class="card"><h3 style="margin-top:0">연결 · 성능</h3><div id="hl2" class="srvck"></div><div class="row" style="margin-top:10px;gap:8px"><button class="s" onclick="devHealth()">다시 측정</button><button class="s" onclick="healthView()">전체 시스템 점검 창</button></div></div>';
 const out=[];const add=(ok,l,m)=>{out.push(`<div class="${ok?'ok':'bad'}"><i></i><span>${l}</span><em>${esc(m)}</em></div>`);document.getElementById('hl2').innerHTML=out.join('')};
 add(navigator.onLine,'인터넷',navigator.onLine?'연결됨':'끊김');
 const ping=async(l,u,o)=>{const a=[];for(let i=0;i<3;i++){const t=performance.now();try{const r=await fetch(u,o);await r.text();a.push(Math.round(performance.now()-t))}catch(e){a.push(-1)}}const g=a.filter(x=>x>=0);add(g.length>0,l,g.length?'평균 '+Math.round(g.reduce((s,x)=>s+x,0)/g.length)+'ms ('+a.join(', ')+')':'실패')};
 await ping('사이트 파일',location.origin+'/index.html?_='+Date.now(),{cache:'no-store'});
 if(cloud()){await ping('Supabase REST',base_()+'/rest/v1/site_config?select=key&limit=1',{headers:hdr()});await ping('패스키 함수',base_()+'/functions/v1/passkey',{method:'POST',headers:hdr(),body:JSON.stringify({action:'ping'})})}
 try{const e=await navigator.storage.estimate();add(true,'브라우저 저장 공간','사용 '+Math.round(e.usage/1048576)+'MB / 한도 약 '+Math.round(e.quota/1048576)+'MB')}catch(e){}}
function devStore(){const ks=Object.keys(localStorage).sort();const rows=ks.map(k=>[k,(localStorage.getItem(k)||'').length*2]);const tot=rows.reduce((a,x)=>a+x[1],0);
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">브라우저 저장소 (이 기기)</h3>${dvKpi([['항목',ks.length],['사용량',(tot/1024).toFixed(1)+'KB']])}<div class="tw"><table><tr><th>키</th><th>크기</th><th></th></tr>${rows.sort((a,b)=>b[1]-a[1]).map(([k,n])=>`<tr><td class="l" style="word-break:break-all">${esc(k)}</td><td>${(n/1024).toFixed(1)}KB</td><td style="white-space:nowrap"><button class="s sm" onclick="devStoreView('${esc(k).replace(/'/g,"\\'")}')">보기</button> <button class="s sm" onclick="devStoreDel('${esc(k).replace(/'/g,"\\'")}')">삭제</button></td></tr>`).join('')}</table></div></div>`}
function devStoreView(k){$('#cfgBox').innerHTML=`<h2 style="margin-top:0;word-break:break-all">${esc(k)}</h2><textarea readonly rows="14" style="width:100%;font-family:monospace;font-size:12px">${esc((localStorage.getItem(k)||'').slice(0,20000))}</textarea><div class="row" style="justify-content:flex-end;margin-top:10px"><button class="s" onclick="closeCfg()">닫기</button></div>`;$('#cfg').classList.add('open')}
function devStoreDel(k){if(!confirm('「'+k+'」 값을 이 기기에서 지울까요? 되돌릴 수 없어요.'))return;localStorage.removeItem(k);devLog('저장소 항목 삭제',k);devRender()}
function devTools(){const days=PREF.bkDays===undefined?14:PREF.bkDays;
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">서버 정리</h3><div class="m">만료된 패스키 요청·자동 로그인 토큰·180일 지난 활동 기록을 지워요.</div><div class="row" style="margin-top:8px"><button class="s" onclick="devCleanup()">정리 실행</button></div></div>
 <div class="card"><h3 style="margin-top:0">앱 도구</h3><div class="row" style="gap:8px;flex-wrap:wrap"><button class="s" onclick="healthView()">시스템 점검 창</button><button class="s" onclick="hardRefresh()">내 기기 캐시 비우기·새로고침</button><button class="s" onclick="backupAll()">내 데이터 백업</button></div>
 <div class="fld" style="max-width:260px;margin-top:12px"><label>백업 알림 주기</label><select onchange="PREF.bkDays=+this.value;prefSave();tsetSaved()">${[[14,'14일마다'],[7,'7일마다'],[30,'30일마다'],[0,'알리지 않음']].map(([v,n])=>`<option value="${v}" ${days===v?'selected':''}>${n}</option>`).join('')}</select></div></div>
 <div class="card"><h3 style="margin-top:0">튜토리얼 다시 보기</h3><div class="row" style="flex-wrap:wrap;gap:6px">${Object.entries(TOURS).map(([k,v])=>`<button class="s sm" onclick="tourStart('${k}')">${esc(v.name)}</button>`).join('')}</div></div>
 <div class="card"><div class="dz"><b>학습 자료만 지우기 (학생 유지)</b><div class="m">만들어 둔 학습지·교재·모의고사·채점 기록·과제·즐겨찾기·신고·내 구성을 모두 지워요. 등록된 학생 정보와 로그인·설정은 남아요.</div><button class="s dgr" onclick="wipeContent()">학습 자료 지우기…</button></div></div>`}
async function devCleanup(){const r=await dvRpc('dev_cleanup');devLog('서버 정리',JSON.stringify(r));toast(`정리했어요 · 패스키 요청 ${r.challenges} · 토큰 ${r.tokens} · 기록 ${r.logs}`)}
async function devAbout(){let sw='없음';try{const ks=await caches.keys();sw=ks.join(', ')||'없음'}catch(e){}
 const bk=[...document.scripts].map(s=>s.src).filter(s=>/books\.js|dev\.js/.test(s)).map(s=>s.split('/').pop()).join(', ');
 const rows=[['앱 버전',typeof APPV!=='undefined'?APPV:'-'],['불러온 스크립트',bk],['서비스 워커 캐시',sw],['사이트 주소',location.origin],['브라우저',navigator.userAgent],['화면',innerWidth+'×'+innerHeight+' @'+devicePixelRatio+'x'],['과목 수',Object.keys(SNAME).length],['불러온 문항',Object.keys(byCode).length.toLocaleString()],['수정·숨김 문항',Object.keys(QOV).length],['공지(공개)',SITE.notices.length],['업데이트 소식',UPDATES.length+'건 (최신: '+(UPDATES[0]||{}).title+')']];
 document.getElementById('devb').innerHTML=`<div class="card"><h3 style="margin-top:0">버전 정보</h3><div class="tw"><table>${rows.map(([k,v])=>`<tr><th style="width:150px">${k}</th><td class="l" style="word-break:break-all">${esc(String(v))}</td></tr>`).join('')}</table></div></div>`}

/* --- eBook 말아 올리기 효과 진단: 이 기기에서 WebGL·쪽 그림 만들기가 되는지 확인 --- */
async function devCurl(){const el=document.getElementById('devb');el.innerHTML='<div class="card"><h3 style="margin-top:0">eBook 말아 올리기 효과 진단</h3><div class="m">이 기기(브라우저)에서 효과에 필요한 기능이 되는지 확인해요. 효과가 안 나오는 기기에서 열어 보세요.</div><div id="cvr" class="srvck" style="margin-top:10px"></div></div>';
 const out=[];const add=(ok,l,m,h)=>{out.push(`<div class="${ok?'ok':'bad'}"><i></i><span>${l}</span><em>${esc(m)}${!ok&&h?' — '+esc(h):''}</em></div>`);document.getElementById('cvr').innerHTML=out.join('')};
 try{await bkLoad()}catch(e){add(false,'교재 스크립트','불러오지 못함');return}
 add(true,'브라우저',navigator.userAgent.slice(0,90));
 let gl=null;try{const c=document.createElement('canvas');gl=c.getContext('webgl')||c.getContext('experimental-webgl')}catch(e){}
 if(!gl){add(false,'WebGL','사용 불가','Safari 설정(고급 ▸ 실험적 기능)에서 WebGL이 꺼져 있거나, 저전력 모드/하드웨어 가속이 꺼져 있을 수 있어요');return}
 let rend='';try{const x=gl.getExtension('WEBGL_debug_renderer_info');rend=x?gl.getParameter(x.UNMASKED_RENDERER_WEBGL):''}catch(e){}
 add(true,'WebGL','사용 가능 · 최대 텍스처 '+gl.getParameter(gl.MAX_TEXTURE_SIZE)+(rend?' · '+rend:''));
 const sh=(t,s)=>{const o=gl.createShader(t);gl.shaderSource(o,s);gl.compileShader(o);return gl.getShaderParameter(o,gl.COMPILE_STATUS)?'':gl.getShaderInfoLog(o)};
 const e1=sh(gl.VERTEX_SHADER,EBVS),e2=sh(gl.FRAGMENT_SHADER,EBFS);add(!e1&&!e2,'셰이더 컴파일',e1||e2||'정상');
 try{const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);const cv=document.createElement('canvas');cv.width=714;cv.height=1010;cv.getContext('2d').fillRect(0,0,9,9);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,cv);const er=gl.getError();add(er===0,'그림 올리기(텍스처)',er===0?'정상':'오류 '+er)}catch(e){add(false,'그림 올리기(텍스처)',String(e.message||e))}
 try{await bkLoadJs('lib/html2canvas.min.js',()=>window.html2canvas);add(!!window.html2canvas,'쪽 그림 라이브러리','불러옴')}catch(e){add(false,'쪽 그림 라이브러리','불러오지 못함');return}
 try{await bkInit();await conceptLoad();const plan=await bkPlan(SUBJ+'-t');const n=Math.min(3,plan.pages.length);
  const hs=document.createElement('style');hs.textContent=BKCSS+'.bkdoc .bp{margin:0!important;box-shadow:none!important}';document.head.appendChild(hs);
  const h=document.createElement('div');h.className='bkdoc';h.style.cssText='position:fixed;left:-20000px;top:0;width:210mm;background:#fff';document.body.appendChild(h);h.innerHTML=bkPageHtml(plan,n-1);
  const t0=performance.now();const cv=await window.html2canvas(h.firstElementChild,{scale:1.2,backgroundColor:'#fff',logging:false});const ms=Math.round(performance.now()-t0);h.remove();hs.remove();
  add(cv.width>10&&ms<4000,'쪽 그림 만들기',cv.width+'×'+cv.height+' · '+ms+'ms',ms>=4000?'너무 느려요(4.5초 넘으면 기본 효과로 바뀌어요)':'')}
 catch(e){add(false,'쪽 그림 만들기',String(e.message||e))}
 const err=(typeof EBK!=='undefined'&&EBK.curlErr)||'';if(err)add(false,'마지막 넘김 실패 이유',err)}
