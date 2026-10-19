/* Solvi 늦게 불러오는 코드: tset — index.html 의 전역(DATA, jget, render …)을 그대로 씁니다. */
const PERMS=[
 ['학습 도구','students','학생이 직접 문제를 만들고 푸는 기능',[['make','학습지 만들기 · 화면에서 풀기','유형을 골라 스스로 문제를 만들어요'],['print','인쇄용 학습지 만들기','PDF·종이로 뽑는 기능'],['ink','문제 위 필기','애플펜슬로 문제 위에 쓰기'],['pageSolve','교재 N쪽만 화면에서 풀기','교재의 한 쪽만 골라 풀기'],['showExp','풀이 후 해설 보기','답을 고른 뒤 바로 해설 공개']]],
 ['메뉴 접근','menu','학생 화면 위쪽 메뉴에 보이는 탭',[['tasks','과제','선생님이 낸 과제 목록'],['enter','번호 채점','학습지 번호·QR로 채점'],['shist','기록','내 풀이 기록'],['books','교재','교재 보기'],['stat','유형 분석','내 유형별 정답률'],['concept','개념학습','단원별 개념 정리'],['wrong','오답노트','틀린 문제 모음'],['diag','오답 진단','틀린 이유 분석']]],
 ['도움말','help','튜토리얼과 새 기능 안내',[['tour','도움말(?) · 처음 시작 튜토리얼','오른쪽 위 ? 버튼과 첫 로그인 안내'],['forceUpd','새 기능 튜토리얼 자동 표시','업데이트 후 처음 접속하면 자동으로 안내']]]];

const TI={students:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',menu:'<path d="M3 6h18M3 12h18M3 18h18"/>',help:'<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',doc:'<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',book:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5V21h16"/>',screen:'<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',bell:'<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0"/>',db:'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',srv:'<rect x="3" y="3" width="18" height="7" rx="2"/><rect x="3" y="14" width="18" height="7" rx="2"/><path d="M7 6.5h.01M7 17.5h.01"/>'};

const tIc=k=>`<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${TI[k]||''}</svg>`;

async function tsetView(){
 if(!TSET.perms){$('#main').innerHTML='<div class="card">'+ldg('설정을 불러오는 중…')+'</div>';await tsetLoad();if(tab!=='tset')return}
 const P=TSET.perms;const on=k=>P[k]!==false&&P[k]!==0;
 const sw=(k,l,d)=>`<label class="swr"><span><b>${l}</b>${d?`<small>${d}</small>`:''}</span><input class="swi" type="checkbox" ${on(k)?'checked':''} onchange="tsetPerm('${k}',this.checked)"></label>`;
 const pf=(k,l,d)=>`<label class="swr"><span><b>${l}</b>${d?`<small>${d}</small>`:''}</span><input class="swi" type="checkbox" ${PREF[k]===0||(k==='big'&&!PREF[k])?'':'checked'} onchange="PREF.${k}=this.checked?1:0;prefSave();tsetSaved()"></label>`;
 const sel=(k,l,opts)=>`<div class="fld"><label>${l}</label><select onchange="PREF.${k}=${typeof opts[0][0]==='number'?'+this.value':'this.value'};prefSave();tsetSaved()">${opts.map(([v,n])=>`<option value="${v}" ${(PREF[k]??opts[0][0])===v?'selected':''}>${n}</option>`).join('')}</select></div>`;
 const selG=(k,l)=>`<div class="fld"><label>${l}</label><select onchange="PREF.${k}=this.value;prefSave();tsetSaved()">${fontOptsHtml(PREF[k]||'paper')}</select></div>`;
 const sec=(id,ic,h,sub,body,right)=>`<section class="tsc" id="ts_${id}"><div class="tsch"><i>${tIc(ic)}</i><div><h2>${h}</h2><p>${sub}</p></div>${right||''}</div>${body}</section>`;
 const off=Object.keys(P).filter(k=>P[k]===false).length;const mq=permNumT('maxQ',60);
 const NAV=[['acad','학원 정보'],['perm','학생 권한'],['ws','학습지'],['bk','교재'],['ui','화면'],['msg','알림·도움말'],['data','데이터·서버'],['join','가입'],['bug','신고'],['acct','계정']];
 $('#main').innerHTML=`<div class="tsh"><div><h1>학원 설정</h1><p>학원 이름·로고, 학생이 쓸 수 있는 기능, 학습지·교재 기본값을 정해요. 내 화면 설정은 오른쪽 위 ⚙ 「개인화 설정」에서 바꿔요.</p></div><div class="tsb"><span class="${off?'warn':''}">학생 기능 ${off?off+'개 제한':'모두 허용'}</span><span>${cloud()&&sess?'온라인 저장 연결됨':'이 기기에만 저장'}</span></div></div>
 <div class="dvl"><nav class="dvn">${NAV.map(([k,l])=>`<button data-k="${k}" onclick="tsSel('${k}')">${l}</button>`).join('')}</nav><div class="dvr">
 ${sec('acad','students','학원 정보','왼쪽 위 로고 옆과 학습지 머리글에 쓰이는 학원 이름·로고예요. 학생 화면에도 똑같이 보여요.',(()=>{const c=acCfg(),rp=jget('omr_rep_v1',[]);const mo=(v,t,d)=>`<label class="acm ${c.mode===v?'on':''}"><input type="radio" name="acmode" value="${v}" ${c.mode===v?'checked':''} onchange="acMode('${v}')"><b>${t}</b><small>${d}</small></label>`;
  return (cloud()&&sess?'':'<div class="hint"><b>온라인 저장에 로그인해야 학생 화면에도 표시돼요.</b></div>')+
  `<div class="tgp"><h3>왼쪽 위에 표시할 것</h3><div class="acms">${mo('text','학원 이름','글자로 Solvi 옆에 표시')}${mo('logo','로고 이미지','올린 이미지를 표시')}${mo('none','표시 안 함','Solvi만 표시')}</div></div>
  <div class="fld" style="max-width:460px"><label>학원 이름 <small class="m">20자까지 · 학습지 머리글에도 들어가요</small></label><input value="${esc(c.name||PREF.academy||'')}" maxlength="20" placeholder="예) 한빛학원" onchange="acName(this.value)"></div>
  <div class="tgp"><h3>로고 이미지 <small>라이트 모드와 다크 모드 로고를 따로 올릴 수 있어요</small></h3><div class="vsw2 stro acmsw ${ACM==='dark'?'r':''}" id="acmsw"><i class="stth"></i><button class="${ACM==='dark'?'':'on'}" onclick="acTheme('light')">☀ 라이트 모드</button><button class="${ACM==='dark'?'on':''}" onclick="acTheme('dark')">☾ 다크 모드</button></div><div id="acmbody">${acThemeBody(ACM)}</div></div>
  <div class="tgp"><h3>문항 · 신고 · 초기화</h3>
  <label class="swr"><span><b>난이도 자동 보정</b><small>풀이 5회 이상인 문항은 실제 정답률로 난이도(하·중·상·최)를 조정해요</small></span><input class="swi" type="checkbox" ${CALIB_ON?'checked':''} onchange="setCalib(this.checked)"></label>
  <div class="setr"><b>신고 내역</b><span class="m">${rp.length}건${rp.some(x=>!x.srv)?' (미전송 '+rp.filter(x=>!x.srv).length+')':''} · <a href="#" onclick="reportStatus();return false">처리 현황</a> · <a href="#" onclick="reportExport();return false">내려받기</a>${rp.length?' · <a href="#" onclick="if(confirm(\'신고 내역을 지울까요?\')){jset(\'omr_rep_v1\',[]);tsetView()}return false">비우기</a>':''}</span></div>
  <div class="dz"><b>학습 자료만 지우기 (학생 유지)</b><div class="m">만들어 둔 학습지·교재·모의고사·채점 기록·과제·즐겨찾기·신고·내 구성을 모두 지웁니다. 등록된 학생 정보와 로그인·설정은 남아요.</div><button class="s dgr" onclick="wipeContent()">학습 자료 지우기…</button></div>
  <div class="dz"><b>전체 초기화</b><div class="m">학생·채점 기록·학습지·모의고사·즐겨찾기·신고·설정을 모두 지웁니다. 로그인과 선택한 과목만 남습니다.</div><button class="s dgr" onclick="wipeAll()">모든 데이터 초기화…</button></div></div>`})())}
 ${sec('perm','students','학생 권한','모든 학생에게 똑같이 적용돼요. 학생 앱이 열려 있으면 1분 안에 반영돼요.',
 (TSET.err?`<div class="hint">${esc(TSET.err)}</div>`:'')+(cloud()&&sess?'':'<div class="hint"><b>온라인 저장에 로그인해야 학생에게 적용돼요.</b></div>')+
 PERMS.map(([g,ic,sub,a])=>`<div class="tgp"><h3>${g}<small>${sub}</small></h3><div class="swg">${a.map(([k,l,d])=>sw(k,l,d)).join('')}</div></div>`).join('')+
 `<div class="tgp"><h3>학습 한도</h3><div class="fld" style="max-width:340px"><label>학생이 한 번에 만들 수 있는 최대 문항 수</label><input type="number" min="5" max="60" value="${mq}" onchange="tsetNum('maxQ',this.value,5,60)"></div></div>
 <div class="row" style="margin-top:12px;flex-wrap:wrap"><button class="s sm" onclick="tsetAll(true)">모두 허용</button><button class="s sm" onclick="tsetPreset('exam')">시험 기간 (풀이·교재만)</button><button class="s sm" onclick="tsetPreset('print')">인쇄 학습 중심 (필기·해설 끔)</button><button class="s sm" onclick="STUD={preview:1,login:'',pw:''};tab='home';render()" ${STU.length?'':'hidden'}>학생 화면 미리보기</button></div>`)}
 ${sec('ws','doc','학습지 기본값','새 학습지를 만들 때 처음 채워지는 값이에요. 머리글의 학원 이름은 「학원 정보」의 이름을 써요.',`<div class="g2">
 <div class="fld"><label>선생님 이름</label><input value="${esc(teacherName())}" maxlength="20" onchange="try{localStorage.setItem(TN,this.value.trim())}catch(e){}tsetSaved()"></div>
 <div class="fld"><label>문항 수</label><input type="number" min="5" max="100" value="${PREF.total}" onchange="PREF.total=Math.max(5,Math.min(100,+this.value||15));prefSave();tsetSaved()"></div>
 ${sel('lvr','난이도 구성',[['basic','기초 (하 중심)'],['std','표준'],['hard','도전 (상 중심)']])}${sel('wsCols','단 수',[[2,'2단'],[1,'1단']])}${selG('wsFont','글꼴')}</div>
 <div class="tgp"><h3>문제 앞 태그 기본값<small>새 학습지에서 문제 번호 옆에 붙는 태그</small></h3><div class="swg">${Object.entries(TAGN).map(([k,v])=>`<label class="swr"><span><b>${esc(v)}</b></span><input class="swi" type="checkbox" ${(PREF.tags||{})[k]?'checked':''} onchange="PREF.tags=PREF.tags||{};PREF.tags['${k}']=this.checked?1:0;prefSave();tsetSaved()"></label>`).join('')}</div></div>
 <div class="swg" style="margin-top:12px">${pf('wsAns','정답·해설 페이지 포함','학습지 뒤에 정답과 해설을 붙여요')}${pf('wsQr','쪽마다 QR 넣기','QR을 찍어 바로 채점해요')}</div>`)}
 ${sec('bk','book','교재 인쇄 기본값','교재를 인쇄할 때의 기본 모양이에요.',`<div class="g2">${sel('bkGap','문제 간격',[[0,'기본'],[1,'조금 넓게'],[2,'넓게'],[3,'아주 넓게']])}${selG('bkFont','글꼴')}</div><p class="tsn2">교재를 새로 만들 때의 난이도·문항 수는 「교재 ▸ 교재 만들기」에서 정해요.</p>`)}
 ${sec('ui','screen','화면 · 편의','이 기기에 저장돼요.',`<div class="swg">${pf('guide','홈에 시작 가이드 보이기')}${pf('nextPage','교재 채점 후 다음 쪽 이어서 채점할지 묻기')}${pf('big','큰 글씨·큰 버튼 모드','태블릿에서 누르기 편하게 화면을 12% 키워요')}</div>
 <div class="g2" style="margin-top:12px">${sel('start','앱을 열면 먼저 보이는 화면',[['thome','홈'],['grade','채점'],['weak','취약 유형']])}</div>
 <p class="tsn2">테마(시스템·라이트·다크)와 로그인·패스키는 오른쪽 위 ⚙에서 바꿔요.</p>`)}
 ${sec('msg','bell','알림 · 도움말','학생에게 공지를 보내고 튜토리얼을 다시 볼 수 있어요.',`<div class="row"><button class="p" onclick="notifOpen(event)">공지 보내기 · 보낸 공지 보기</button></div>
 <div class="tgp"><h3>튜토리얼 다시 보기</h3><div class="row"><button class="s sm" onclick="tourStart('intro')">처음 시작하기 안내</button></div></div>`)}
 ${sec('data','db','데이터 · 서버','백업과 서버 설정 상태를 확인해요.',`<div class="row" style="flex-wrap:wrap"><button class="s" onclick="backupAll()">백업 내려받기</button><label class="s fl">백업 불러오기<input type="file" accept=".json" hidden onchange="restoreAll(this)"></label></div><p class="tsn2">서버 점검·시스템 점검·학습 자료 삭제 같은 관리 도구는 개발자 탭으로 옮겼어요.</p>`)}
 ${sec('bug','help','버그 신고 · 새로고침','앱에서 이상한 점을 알리고, 학생이 보낸 신고를 확인해요.',`<div class="row" style="flex-wrap:wrap"><button class="p" onclick="openBug()">버그 신고하기</button><button class="s" onclick="hardRefresh()">앱 새로고침 (캐시 비우기)</button></div><div id="bugbox" class="srvck" style="margin-top:12px"></div>`)}
 ${sec('join','students','학생 가입 · 승인','학생이 직접 회원가입을 신청하고, 선생님이 승인하면 로그인할 수 있어요.',`${SG.err?`<div class="hint">${esc(SG.err)}</div>`:''}<label class="swr"><span><b>가입 받기</b><small>끄면 새 신청을 받지 않아요</small></span><input class="swi" type="checkbox" ${SG.open?'checked':''} onchange="sgToggle(this.checked)"></label>${SG.code?`<div class="sgshare"><div><div class="m">선생님 코드</div><b class="sgcode">${esc(SG.code)}</b><div class="m" style="margin-top:10px;word-break:break-all">${esc(sgLink())}</div><div class="row" style="margin-top:10px"><button class="p sm" onclick="sgCopy()">가입 링크 복사</button><button class="s sm" onclick="sgRegen()">코드 다시 만들기</button></div></div><div class="sgqr" aria-label="가입 QR">${qrSvg(sgLink())}</div></div>`:'<div class="m">코드를 불러오는 중이에요…</div>'}<div class="tgp"><h3>대기 중인 신청 <small>${SG.list.length}건</small></h3>${sgReqHtml()}</div>`)}
 ${sec('acct','students','계정','이 기기에 저장된 계정을 전환하거나 로그아웃해요.',`<div id="acctbox">${acctHtml()}</div>`)}</div></div>`;tsSel(TSEL);bugLoad().then(bugRender)}

let TSEL='acad';

function tsSel(k){if(!document.getElementById('ts_'+k))k='acad';TSEL=k;document.querySelectorAll('.dvr>.tsc').forEach(e=>{e.hidden=e.id!=='ts_'+k});document.querySelectorAll('.dvn button[data-k]').forEach(b=>b.classList.toggle('on',b.dataset.k===k))}

async function srvCheck(){const el=$('#srvck');if(!el)return;if(!cloud()||!sess){el.innerHTML='<div class="hint">온라인 저장에 로그인해야 점검할 수 있어요.</div>';return}
 el.innerHTML='<div class="m">점검 중…</div>';
 const T=[['공지 (notices 테이블)','11',()=>sb('/rest/v1/notices?select=id&limit=1')],['학생 공지 읽기 (st_notices)','11',()=>rpc('st_notices',{p_login:'_',p_pw:'_'})],['학부모 로그인 (pa_login)','16',()=>rpc('pa_login',{p_login:'_',p_pw:'_'})],['학생 권한 저장 (teacher_settings)','12',()=>sb('/rest/v1/teacher_settings?select=user_id&limit=1')],['학생 권한 읽기 (st_perms)','12',()=>rpc('st_perms',{p_login:'_',p_pw:'_'})],['패스키 (passkeys 테이블)','10',()=>sb('/rest/v1/passkeys?select=id&limit=1')],['버그 신고 (bug_reports 테이블)','13',()=>sb('/rest/v1/bug_reports?select=id&limit=1')],['학생 버그 신고 (st_bug)','13',()=>rpc('st_bug',{p_login:'_',p_pw:'_',p_msg:'',p_info:{}})],['자동 로그인 (st_logout)','10',()=>rpc('st_logout',{p_login:'_',p_token:'_'})]];
 const out=[];for(const [n,sec,f] of T){let ok=false,msg='';try{const r=await f();ok=r.ok||r.status===204;msg=ok?'정상':(r.status===404?'없음 — setup.sql '+sec+'번을 실행하세요':'오류 '+r.status)}catch(e){msg='연결 실패'}out.push(`<div class="${ok?'ok':'bad'}"><i></i><span>${n}</span><em>${msg}</em></div>`)}
 el.innerHTML=out.join('')}

function tsetSaved(){toast('저장했어요')}

async function tsetNum(k,v,lo,hi){const old=TSET.perms[k];TSET.perms[k]=Math.max(lo,Math.min(hi,Math.round(+v)||hi));try{await tsetSave();tsetSaved()}catch(e){TSET.perms[k]=old;toast(e.message)}tsetView()}

async function tsetAll(on){const old={...TSET.perms};const n={};if(TSET.perms.maxQ)n.maxQ=TSET.perms.maxQ;TSET.perms=n;try{await tsetSave();tsetSaved()}catch(e){TSET.perms=old;toast(e.message)}tsetView()}

async function tsetPreset(k){const old={...TSET.perms};const off={exam:['make','print','tasks','shist','wrong','diag','concept','stat'],print:['ink','showExp','pageSolve']}[k];const n={};if(old.maxQ)n.maxQ=old.maxQ;off.forEach(x=>n[x]=false);TSET.perms=n;try{await tsetSave();tsetSaved()}catch(e){TSET.perms=old;toast(e.message)}tsetView()}

async function tsetPerm(k,on){TSET.perms[k]=on;try{await tsetSave();tsetSaved()}catch(e){TSET.perms[k]=!on;toast(e.message);tsetView()}}

const sgLink=()=>((CF&&CF.pub)||location.origin+'/').replace(/#.*$/,'')+'#join='+SG.code;

async function sgToggle(on){try{const r=await rpc('join_open_set',{p_open:on});if(!r.ok)throw 0;SG.open=on;toast(on?'가입을 받아요':'가입을 받지 않아요')}catch(e){toast('저장하지 못했어요');tsetView()}}

function sgCopy(){const s=sgLink();try{navigator.clipboard.writeText(s);toast('링크를 복사했어요')}catch(e){prompt('링크를 복사하세요',s)}}

async function sgRegen(){if(!confirm('가입 코드를 새로 만들까요?\n지금 코드는 바로 쓸 수 없게 돼요. 이미 받은 가입 링크·QR도 새 것으로 바꿔 나눠 주세요.'))return;try{const r=await rpc('join_code_regen',{});if(!r.ok)throw new Error(r.status===404?'서버에 sql_18_join_code.sql을 먼저 실행해 주세요':'다시 만들지 못했어요 ('+r.status+')');const j=await r.json();SG.code=(j&&j.code)||j;toast('새 가입 코드를 만들었어요');if(tab==='tset')tsetView()}catch(e){toast(e.message||'다시 만들지 못했어요')}}

function acPick(inp,m){const key=m==='dark'?'logoDark':'logo';const f=inp.files&&inp.files[0];if(!f)return;if(!/^image\/(png|jpeg|webp)$/.test(f.type)){toast('PNG·JPG·WEBP 이미지를 골라 주세요');return}
 const im=new Image(),rd=new FileReader();rd.onload=()=>{im.onload=async()=>{let k=Math.min(1,360/im.width,120/im.height),url='';for(let t=0;t<4;t++){const c=document.createElement('canvas');c.width=Math.max(1,Math.round(im.width*k));c.height=Math.max(1,Math.round(im.height*k));c.getContext('2d').drawImage(im,0,0,c.width,c.height);url=c.toDataURL(f.type==='image/jpeg'?'image/jpeg':'image/png',.88);if(url.length<=80000)break;k*=.7}
  if(url.length>80000||!LOGO_RE.test(url)){toast('이미지가 너무 커요. 더 단순한 로고를 써 주세요');return}if(await acSave({[key]:url,acmode:'logo'}))toast((m==='dark'?'다크 모드':'라이트 모드')+' 로고를 저장했어요');tsetView()};im.onerror=()=>toast('이미지를 읽지 못했어요');im.src=rd.result};rd.readAsDataURL(f);inp.value=''}

async function acSet(url,m){const key=m==='dark'?'logoDark':'logo';const c=acCfg();const left=m==='dark'?c.logo:c.logoDark;if(await acSave({[key]:url||'',...(url||left?{}:{acmode:(c.name?'text':'none')})}))toast(url?'로고를 저장했어요':'로고를 지웠어요');tsetView()}

let ACM='light';

function acTheme(m){if(ACM===m)return;ACM=m;const b=document.getElementById('acmbody'),t=document.getElementById('acmsw');if(!b||!t){tsetView();return}t.classList.toggle('r',m==='dark');t.querySelectorAll('button').forEach((x,i)=>x.classList.toggle('on',(i?'dark':'light')===m));b.style.setProperty('--dx',(m==='dark'?16:-16)+'px');b.innerHTML=acThemeBody(m);b.classList.remove('in');void b.offsetWidth;b.classList.add('in')}

function acPrev(m){const c=acCfg(),u=acLogoFor(c,m==='dark')||'';const body=c.mode==='logo'?(u?`<img src="${u}" alt="">`:'<span class="m" style="color:inherit;opacity:.7;margin-left:8px">(로고를 올려 주세요)</span>'):c.mode==='text'?(c.name?`<span class="acn">${esc(c.name)}</span>`:'<span class="m" style="color:inherit;opacity:.7;margin-left:8px">(이름을 입력하세요)</span>'):'';return `<div class="acprev ${m}"><svg class="slg" viewBox="${WMVB}" aria-hidden="true"><path d="${WMD}" fill="currentColor"/><path d="${WMU}" fill="none" stroke="#ffc21a" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>${body?`<span class="acdv"></span>${body}`:''}</div>`}

function acThemeBody(m){const c=acCfg(),key=m==='dark'?'logoDark':'logo',u=c[key];const ttl=m==='dark'?'다크 모드':'라이트 모드';
 return `<label class="acdrop ${u?'has':''}"><input type="file" accept="image/png,image/jpeg,image/webp" onchange="acPick(this,'${m}')">${u?`<img src="${u}" alt="" class="acpv ${m}">`:'<span class="acic" aria-hidden="true">⬆</span>'}<span class="acdt"><b>${u?ttl+' 로고 바꾸기':ttl+' 로고 올리기'}</b><small>눌러서 사진 고르기 · PNG(투명 배경 가능)·JPG·WEBP</small></span></label>${u?`<div style="margin-top:8px"><button class="s sm" onclick="acSet('','${m}')">이 로고 지우기</button></div>`:''}${(m==='dark'&&!c.logoDark&&c.logo)?'<p class="m" style="margin:8px 0 0">다크 모드 로고가 없어서 라이트 모드 로고를 대신 써요.</p>':''}<h4 class="acph">${ttl} 미리보기</h4>${acPrev(m)}`}

async function acMode(m){if(await acSave({acmode:m}))tsetView()}

async function acName(v){v=v.trim().slice(0,20);if(await acSave({acname:v,...(v&&acCfg().mode==='none'?{acmode:'text'}:{})}))tsetView()}
