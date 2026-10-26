/* Solvi 늦게 불러오는 코드: admin — 학원 운영(원장·선생님): 대시보드 · 원생 · 반·시간표 · 상담 일지 · 보강 · 월 일괄 청구·영수증,
   학생·학부모: 시간표(반 · 보강 · 공유된 상담). index.html 의 전역(sb, rpc, esc, $, toast, ldg, STU, STUD, sess, cloud, tsRaw …)을 그대로 씁니다.
   서버 표는 supabase/sql_23_admin.sql (원생 열 · classes · class_members · counsels · makeups) 이고, 수납은 sql_20 의 fees 를 같이 씁니다. */
const AD={sec:'dash',ld:0,err:'',stu:[],cls:[],mem:[],cns:[],mku:[],fees:[],att:[],matt:[],q:'',st:'재원',cf:'',edit:null,bm:'',cnsF:'all',mkuF:'예정'};
const ADSEC=[['dash','대시보드'],['stu','원생'],['cls','반 · 시간표'],['cns','상담 일지'],['mku','보강'],['bill','월 청구 · 영수증']];
const ADST=['재원','휴원','상담','퇴원'],ADSTC={재원:'#1f9d55',휴원:'#e09a00',상담:'#2f7fd0',퇴원:'#8a94a3'};
const ADDAY=['','월','화','수','목','금','토','일'];
const ADCNS=['학생','학부모','입학','진로','기타'];
const adDay=d=>new Date((d||new Date()).getTime()+9*36e5).toISOString().slice(0,10); // 한국 시각 날짜
const adWon=n=>(+n||0).toLocaleString('ko-KR')+'원';
const adDow=day=>{const w=new Date(day+'T00:00:00Z').getUTCDay();return w===0?7:w}; // 1 월 … 7 일
const adSql='<div class="card"><div class="hint"><b>서버에 학원 운영 표가 아직 없어요.</b> Supabase 「SQL Editor」에서 <code>supabase/sql_23_admin.sql</code> 내용을 한 번 실행해 주세요. 실행 전에도 출결·수납·알림장 등 다른 기능은 그대로 쓸 수 있어요.</div></div>';
const adNeed='<div class="card"><div class="hint"><b>온라인 저장에 로그인해야 쓸 수 있어요.</b> 학원 운영 자료는 서버에 저장돼서 다른 선생님·학부모 앱과 함께 보여요.</div></div>';
async function adJ(path,o){const r=await sb(path,o);if(!r.ok){const e=new Error('http '+r.status);e.status=r.status;try{e.body=await r.text()}catch(x){}throw e}const t=await r.text();return t?JSON.parse(t):null}
const adMissing=e=>e&&(e.status===404||e.status===400||/does not exist|schema cache|column/i.test(e.body||''));
const adPost=(t,b,ret)=>adJ('/rest/v1/'+t,{method:'POST',headers:{Prefer:ret?'return=representation':'return=minimal'},body:JSON.stringify(b)});
const adPatch=(t,q,b)=>adJ('/rest/v1/'+t+'?'+q,{method:'PATCH',headers:{Prefer:'return=representation'},body:JSON.stringify(b)});
const adDel=(t,q)=>adJ('/rest/v1/'+t+'?'+q,{method:'DELETE',headers:{Prefer:'return=minimal'}});
const adStu=id=>AD.stu.find(s=>s.id===id);
const adName=id=>{const s=adStu(id);return s?s.name:'(삭제된 학생)'};
const adClsOf=sid=>AD.mem.filter(m=>m.student_id===sid).map(m=>AD.cls.find(c=>c.id===m.class_id)).filter(Boolean);
const adMembers=cid=>AD.mem.filter(m=>m.class_id===cid).map(m=>adStu(m.student_id)).filter(Boolean);
const adTime=t=>t?new Date(t).toLocaleString('ko-KR',{month:'numeric',day:'numeric',weekday:'short',hour:'2-digit',minute:'2-digit',hour12:false,timeZone:'Asia/Seoul'}):'';

async function adLoad(){
 AD.err='';const today=adDay(),mon=today.slice(0,7);
 try{
  AD.stu=await adJ('/rest/v1/students?select=id,name,grade,phone,memo,school,status,joined_on,left_on,guardian,guardian_phone&order=name.asc&limit=3000');
  const [c,m,n,k]=await Promise.all([adJ('/rest/v1/classes?select=*&order=name.asc&limit=500'),adJ('/rest/v1/class_members?select=class_id,student_id,since&limit=10000'),
   adJ('/rest/v1/counsels?select=*&order=day.desc,id.desc&limit=600'),adJ('/rest/v1/makeups?select=*&order=missed_on.desc&limit=600')]);
  AD.cls=c||[];AD.mem=m||[];AD.cns=n||[];AD.mku=k||[];
  try{AD.fees=await adJ('/rest/v1/fees?select=*&order=created_at.desc&limit=2000')}catch(e){AD.fees=[]}
  try{AD.att=await adJ('/rest/v1/attendance?select=student_id,status,day&day=eq.'+today);AD.matt=await adJ('/rest/v1/attendance?select=student_id,status,day&day=gte.'+mon+'-01&day=lte.'+mon+'-31&limit=20000')}catch(e){AD.att=[];AD.matt=[]}
 }catch(e){AD.err=adMissing(e)?'sql':'불러오지 못했어요 ('+(e.status||'연결')+')'}
 AD.ld=1}
function adCss(){if(document.getElementById('adcss'))return;const s=document.createElement('style');s.id='adcss';s.textContent=`
.adk{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin-bottom:14px}.adk>div{background:var(--surface);border:1px solid var(--l);border-radius:14px;padding:14px 16px}
.adk b{display:block;font-size:26px;letter-spacing:-.02em;font-variant-numeric:tabular-nums}.adk span{font-size:13px;color:var(--m)}.adk small{display:block;font-size:12px;color:var(--m);margin-top:2px}
.adk .warn b{color:#c0392b}.adg{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.adl{display:flex;flex-direction:column}.adl>div{display:flex;gap:10px;align-items:center;padding:9px 2px;border-top:1px solid var(--l);flex-wrap:wrap}.adl>div:first-child{border-top:0}
.adl .t{font-variant-numeric:tabular-nums;color:var(--m);font-size:13px;min-width:92px}.adl .g{flex:1;min-width:120px}.adl .g small{display:block;color:var(--m);font-size:12.5px}
.adchip{display:inline-block;font-size:12px;font-weight:700;padding:2px 9px;border-radius:999px;color:#fff;background:var(--c,#8a94a3);white-space:nowrap}
.adbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:10px}.adbar input[type=search]{flex:1 1 180px}
.adtab{width:100%;border-collapse:collapse}.adtab th{text-align:left;font-size:12.5px;color:var(--m);font-weight:600;padding:8px 6px;border-bottom:1px solid var(--l);background:none;white-space:nowrap}.adtab td{text-align:left;padding:9px 6px;border-bottom:1px solid var(--l);font-size:14px;vertical-align:top}
.adtab tr.rowl{cursor:pointer}.adtab tr.rowl:hover td{background:var(--sf1)}
.adtt{display:grid;grid-template-columns:44px repeat(7,1fr);border:1px solid var(--l);border-radius:12px;overflow:hidden;background:var(--surface);font-size:12.5px}
.adtt>div{border-left:1px solid var(--l);position:relative;min-height:0}.adtt>.h{background:var(--sf1);font-weight:700;text-align:center;padding:6px 0;border-bottom:1px solid var(--l)}.adtt>.h.today{color:var(--b)}
.adtt .tm{border-left:0;color:var(--m);font-size:11px;text-align:right;padding-right:6px}.adtt .col{height:calc(var(--rows)*32px)}
.adtt .blk{position:absolute;left:3px;right:3px;border-radius:8px;padding:4px 6px;background:color-mix(in srgb,var(--c,#2f7fd0) 16%,var(--surface));border-left:0;box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--c,#2f7fd0) 45%,transparent);overflow:hidden;cursor:pointer;line-height:1.3}
.adtt .blk b{display:block;font-size:12.5px}.adtt .blk span{font-size:11px;color:var(--m)}
.adform{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}.adform label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--m)}.adform input,.adform select,.adform textarea{font:inherit;color:var(--t)}
.adform .w{grid-column:1/-1}.adform textarea{min-height:90px;padding:8px 10px;border:1px solid var(--l2);border-radius:8px;background:var(--surface)}
.adsch{display:flex;flex-direction:column;gap:6px}.adsch>div{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.adpick{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:4px 10px;max-height:240px;overflow:auto;padding:8px;border:1px solid var(--l);border-radius:10px}
.adempty{color:var(--m);font-size:14px;padding:10px 2px}
@media(max-width:720px){.adtt{font-size:11px;grid-template-columns:34px repeat(7,1fr)}.adtt .blk span{display:none}.adtab .hm{display:none}}
`;document.head.appendChild(s)}

async function adminView(){
 const m=$('#main');adCss();if(!(typeof cloud==='function'&&cloud()&&sess)){m.innerHTML=adNeed;return}
 if(!AD.ld){m.innerHTML='<div class="card">'+ldg('학원 운영 자료를 불러오는 중…')+'</div>';await adLoad()}
 const seg=`<div class="bkseg axseg" role="tablist">${ADSEC.map(([k,l])=>`<button role="tab" aria-selected="${AD.sec===k}" class="${AD.sec===k?'on':''}" onclick="adSec('${k}')">${l}</button>`).join('')}</div>`;
 const body=AD.err==='sql'?adSql:AD.err?`<div class="card"><div class="hint">${esc(AD.err)}</div><button class="s sm" style="margin-top:10px" onclick="AD.ld=0;adminView()">다시 불러오기</button></div>`:({dash:adDash,stu:adStuHtml,cls:adClsHtml,cns:adCnsHtml,mku:adMkuHtml,bill:adBillHtml}[AD.sec]||adDash)();
 m.innerHTML=`<div class="tsh"><div><h1>학원 운영</h1><p>원생 · 반과 시간표 · 상담 · 보강 · 수납을 한곳에서 봐요. 다른 선생님 계정과 함께 쓰고, 학부모 앱에도 필요한 것만 보여요.</p></div><div class="tsb"><button class="s" onclick="tab='att';render()">출결 · 수납</button><button class="s" onclick="tab='diary';render()">알림장</button></div></div>${seg}${body}`}
function adSec(k){AD.sec=k;adminView();try{scrollTo(0,0)}catch(e){}}
function adReload(){AD.ld=0;adminView()}

/* ---------- 대시보드 ---------- */
function adToday(){const d=adDay(),w=adDow(d);const out=[];AD.cls.filter(c=>c.active!==false).forEach(c=>(c.sched||[]).forEach(t=>{if(+t.d===w)out.push({c,s:t.s||'',e:t.e||''})}));return out.sort((a,b)=>a.s.localeCompare(b.s))}
function adDash(){
 const today=adDay(),mon=today.slice(0,7),wk=adDay(new Date(Date.now()+7*864e5));
 const act=AD.stu.filter(s=>(s.status||'재원')==='재원'),hold=AD.stu.filter(s=>s.status==='휴원');
 const newM=AD.stu.filter(s=>(s.joined_on||'').startsWith(mon)).length,outM=AD.stu.filter(s=>(s.left_on||'').startsWith(mon)).length;
 const todayC=adToday(),attBy={};AD.att.forEach(a=>attBy[a.student_id]=a.status);
 const exp=new Set();todayC.forEach(x=>adMembers(x.c.id).forEach(s=>{if((s.status||'재원')==='재원')exp.add(s.id)}));
 const came=[...exp].filter(id=>attBy[id]==='in'||attBy[id]==='late').length;
 const mAtt=AD.matt.length?Math.round(AD.matt.filter(a=>a.status==='in'||a.status==='late').length/AD.matt.length*100):null;
 const mf=AD.fees.filter(f=>(f.due||f.created_at||'').slice(0,7)===mon),billed=mf.reduce((a,f)=>a+f.amount,0),paid=mf.reduce((a,f)=>a+Math.min(f.amount,f.paid_amount||0),0);
 const unpaid=AD.fees.filter(f=>(f.paid_amount||0)<f.amount),unpaidSum=unpaid.reduce((a,f)=>a+f.amount-(f.paid_amount||0),0),late=unpaid.filter(f=>f.due&&f.due<today);
 const cnsUp=AD.cns.filter(c=>c.next_on&&!c.done&&c.next_on<=wk).sort((a,b)=>a.next_on.localeCompare(b.next_on));
 const mkUp=AD.mku.filter(k=>k.status==='예정').sort((a,b)=>String(a.plan_at||'9').localeCompare(String(b.plan_at||'9')));
 const noCls=act.filter(s=>!adClsOf(s.id).length);
 const k=(v,l,sub,w)=>`<div class="${w?'warn':''}"><span>${l}</span><b>${v}</b>${sub?`<small>${sub}</small>`:''}</div>`;
 const tiles=`<div class="adk">${k(act.length+'명','재원생','휴원 '+hold.length+' · 상담 '+AD.stu.filter(s=>s.status==='상담').length)}${k('+'+newM+' / −'+outM,'이번 달 신규 / 퇴원','')}${k(todayC.length+'개','오늘 수업',exp.size?'등원 '+came+' / '+exp.size+'명':'')}${k(mAtt==null?'—':mAtt+'%','이번 달 출석률',AD.matt.length+'건 기록')}${k(billed?Math.round(paid/billed*100)+'%':'—','이번 달 수납률',adWon(paid)+' / '+adWon(billed))}${k(adWon(unpaidSum),'미수금',late.length?'기한 지남 '+late.length+'건':unpaid.length+'건',late.length)}${k(cnsUp.length+'건','상담 할 일 (7일)','')}${k(mkUp.length+'건','예정된 보강','')}</div>`;
 const tl=todayC.length?todayC.map(x=>{const mem=adMembers(x.c.id).filter(s=>(s.status||'재원')==='재원');const ok=mem.filter(s=>attBy[s.id]==='in'||attBy[s.id]==='late').length;
  return `<div><span class="t">${esc(x.s)}${x.e?'–'+esc(x.e):''}</span><span class="g"><b>${esc(x.c.name)}</b><small>${esc([x.c.teacher,x.c.room].filter(Boolean).join(' · '))}</small></span><span class="adchip" style="--c:${ok===mem.length&&mem.length?'#1f9d55':'#2f7fd0'}">등원 ${ok}/${mem.length}</span></div>`}).join(''):`<div class="adempty">오늘(${ADDAY[adDow(today)]}요일) 수업이 없어요. 「반 · 시간표」에서 요일과 시간을 넣으면 여기 나와요.</div>`;
 const ul=late.concat(unpaid.filter(f=>!late.includes(f))).slice(0,8).map(f=>`<div><span class="g"><b>${esc(adName(f.student_id))}</b><small>${esc(f.title)}${f.due?' · 기한 '+f.due:''}</small></span><b>${adWon(f.amount-(f.paid_amount||0))}</b>${f.due&&f.due<today?'<span class="adchip" style="--c:#d9534f">지남</span>':''}</div>`).join('')||'<div class="adempty">미납이 없어요.</div>';
 const cl=cnsUp.slice(0,6).map(c=>`<div><span class="t">${esc(c.next_on)}</span><span class="g"><b>${esc(adName(c.student_id))}</b><small>${esc(c.next_todo||c.body.slice(0,40))}</small></span><button class="s sm" onclick="adCnsDone(${c.id})">완료</button></div>`).join('')||'<div class="adempty">7일 안에 할 상담이 없어요.</div>';
 const ml=mkUp.slice(0,6).map(x=>`<div><span class="t">${x.plan_at?esc(adTime(x.plan_at)):'일정 미정'}</span><span class="g"><b>${esc(adName(x.student_id))}</b><small>${esc(x.missed_on)} 빠짐${x.reason?' · '+esc(x.reason):''}</small></span><button class="s sm" onclick="adMkuSet(${x.id},'완료')">완료</button></div>`).join('')||'<div class="adempty">예정된 보강이 없어요.</div>';
 const warn=[noCls.length?`반에 들지 않은 재원생 <b>${noCls.length}명</b> — <a href="#" onclick="AD.sec='stu';AD.cf='__none';adminView();return false">원생에서 보기</a>`:'',AD.cls.some(c=>c.active!==false&&!(c.sched||[]).length)?'요일·시간이 없는 반이 있어요 — 시간표에 나오지 않아요':'',act.some(s=>!s.guardian_phone)?`보호자 연락처가 없는 재원생 <b>${act.filter(s=>!s.guardian_phone).length}명</b>`:''].filter(Boolean);
 return tiles+(warn.length?`<div class="hint" style="margin-bottom:14px">${warn.join('<br>')}</div>`:'')+`<div class="adg"><div class="card"><h2>오늘 수업</h2><div class="adl">${tl}</div></div><div class="card"><h2>미납 · 기한 지남</h2><div class="adl">${ul}</div>${unpaid.length?`<button class="s sm" style="margin-top:8px" onclick="tab='att';render();setTimeout(()=>{try{acSec('fee')}catch(e){}},300)">수납 화면에서 보기</button>`:''}</div><div class="card"><h2>상담 할 일</h2><div class="adl">${cl}</div></div><div class="card"><h2>보강</h2><div class="adl">${ml}</div></div></div>`}

/* ---------- 원생 ---------- */
function adStuHtml(){
 const q=AD.q.trim(),cf=AD.cf;let L=AD.stu.filter(s=>(AD.st==='all'||(s.status||'재원')===AD.st)&&(!q||(s.name+' '+(s.grade||'')+' '+(s.school||'')+' '+(s.guardian||'')).includes(q)));
 if(cf==='__none')L=L.filter(s=>!adClsOf(s.id).length);else if(cf)L=L.filter(s=>AD.mem.some(m=>m.student_id===s.id&&String(m.class_id)===cf));
 const cnt={};AD.stu.forEach(s=>{const k=s.status||'재원';cnt[k]=(cnt[k]||0)+1});
 const rows=L.map(s=>`<tr class="rowl" onclick="adStuEdit('${s.id}')"><td><b>${esc(s.name)}</b><div class="m">${esc(s.grade||'')}</div></td><td class="hm">${esc(s.school||'')}</td><td>${adClsOf(s.id).map(c=>`<span class="adchip" style="--c:${esc(c.color||'#2f7fd0')}">${esc(c.name)}</span>`).join(' ')||'<span class="m">—</span>'}</td><td><span class="adchip" style="--c:${ADSTC[s.status||'재원']}">${esc(s.status||'재원')}</span></td><td class="hm">${esc(s.guardian||'')}<div class="m">${esc(s.guardian_phone||s.phone||'')}</div></td><td class="hm">${esc(s.joined_on||'')}</td></tr>`).join('');
 return `<div class="card"><div class="adbar"><div class="bkseg" role="group">${[['all','전체']].concat(ADST.map(x=>[x,x])).map(([v,l])=>`<button class="${AD.st===v?'on':''}" onclick="AD.st='${v}';adminView()">${l}${v==='all'?'':' '+(cnt[v]||0)}</button>`).join('')}</div>
 <select onchange="AD.cf=this.value;adminView()" aria-label="반으로 거르기"><option value="">모든 반</option><option value="__none" ${cf==='__none'?'selected':''}>반 없음</option>${AD.cls.map(c=>`<option value="${c.id}" ${cf===String(c.id)?'selected':''}>${esc(c.name)}</option>`).join('')}</select>
 <input type="search" placeholder="이름 · 학년 · 학교 · 보호자 검색" value="${esc(AD.q)}" oninput="AD.q=this.value;clearTimeout(window._adq);window._adq=setTimeout(adminView,250)">
 <button class="p" onclick="adStuEdit('')">＋ 원생 등록</button><button class="s" onclick="adStuCsv()">명단 내려받기</button></div>
 <div class="tw"><table class="adtab"><thead><tr><th>이름</th><th class="hm">학교</th><th>반</th><th>상태</th><th class="hm">보호자</th><th class="hm">입원일</th></tr></thead><tbody>${rows||'<tr><td colspan="6" class="adempty">조건에 맞는 원생이 없어요.</td></tr>'}</tbody></table></div>
 <p class="tsn2">「학생」 메뉴의 채점·학습 기록과 같은 학생이에요. 퇴원 처리해도 기록은 남고, 학생 계정 로그인은 「학생」 메뉴에서 관리해요.</p></div>`}
function adStuEdit(id){const s=id?adStu(id):{name:'',grade:'',status:'재원',joined_on:adDay()};if(!s)return;AD.edit=id||'';
 const v=k=>esc(s[k]||''),mine=new Set(AD.mem.filter(m=>m.student_id===id).map(m=>m.class_id));
 $('#cfgBox').innerHTML=`<h2 style="margin-top:0">${id?esc(s.name)+' 원생 정보':'원생 등록'}</h2><div class="adform">
 <label>이름<input id="ads_name" value="${v('name')}" maxlength="20"></label><label>학년 · 반 표기<input id="ads_grade" value="${v('grade')}" placeholder="예: 고2 A반" maxlength="20"></label>
 <label>학교<input id="ads_school" value="${v('school')}" maxlength="30"></label><label>상태<select id="ads_status">${ADST.map(x=>`<option ${(s.status||'재원')===x?'selected':''}>${x}</option>`).join('')}</select></label>
 <label>입원일<input id="ads_joined" type="date" value="${v('joined_on')}"></label><label>퇴원일<input id="ads_left" type="date" value="${v('left_on')}"></label>
 <label>학생 연락처<input id="ads_phone" type="tel" value="${v('phone')}" maxlength="20"></label><label>보호자<input id="ads_guard" value="${v('guardian')}" placeholder="예: 어머니 김○○" maxlength="20"></label>
 <label>보호자 연락처<input id="ads_gphone" type="tel" value="${v('guardian_phone')}" maxlength="20"></label>
 <label class="w">메모<textarea id="ads_memo" maxlength="500">${v('memo')}</textarea></label>
 <div class="w"><div class="m" style="margin-bottom:4px">반</div><div class="adpick">${AD.cls.map(c=>`<label class="chk"><input type="checkbox" value="${c.id}" ${mine.has(c.id)?'checked':''}> ${esc(c.name)}</label>`).join('')||'<span class="m">아직 반이 없어요. 「반 · 시간표」에서 만들어요.</span>'}</div></div></div>
 <div class="row" style="margin-top:14px;justify-content:flex-end">${id?`<button class="s" onclick="AD.sec='cns';AD.cnsF='${id}';closeCfg();adminView()">상담 기록</button>`:''}<button class="s" onclick="closeCfg()">닫기</button><button class="p" onclick="adStuSave()">저장</button></div>`;
 $('#cfg').classList.add('open');try{cfgChrome()}catch(e){}setTimeout(()=>{const e=$('#ads_name');if(e&&!id)e.focus()},60)}
async function adStuSave(){const g=k=>{const e=$('#ads_'+k);return e?e.value.trim():''};const name=g('name');if(!name){toast('이름을 입력해 주세요');return}
 const st=g('status');let left=g('left');if(st==='퇴원'&&!left)left=adDay();
 const body={name,grade:g('grade')||null,school:g('school')||null,status:st,joined_on:g('joined')||null,left_on:left||null,phone:g('phone')||null,guardian:g('guard')||null,guardian_phone:g('gphone')||null,memo:g('memo')||null};
 const want=new Set([...document.querySelectorAll('#cfgBox .adpick input:checked')].map(i=>+i.value));
 try{let id=AD.edit;
  if(id){await adPatch('students','id=eq.'+id,body)}else{const r=await adPost('students',{...body,t:Date.now()},1);id=r&&r[0]&&r[0].id;if(id&&typeof STU!=='undefined'){STU.push({id,name,grade:body.grade||'',memo:body.memo||'',t:Date.now()});try{jset(LST,STU)}catch(e){}}}
  if(id&&typeof STU!=='undefined'){const x=STU.find(s=>s.id===id);if(x){x.name=name;x.grade=body.grade||'';x.memo=body.memo||'';try{jset(LST,STU)}catch(e){}}}
  const have=new Set(AD.mem.filter(m=>m.student_id===id).map(m=>m.class_id));
  for(const c of want)if(!have.has(c))await adPost('class_members',{class_id:c,student_id:id});
  for(const c of have)if(!want.has(c))await adDel('class_members','class_id=eq.'+c+'&student_id=eq.'+id);
  closeCfg();toast('저장했어요');adReload()}catch(e){toast(adMissing(e)?'서버에 원생 열이 없어요. sql_23_admin.sql 을 실행해 주세요':'저장하지 못했어요')}}
function adStuCsv(){const q=s=>'"'+String(s==null?'':s).replace(/"/g,'""')+'"';const rows=[['이름','학년·반','학교','상태','반','입원일','퇴원일','학생 연락처','보호자','보호자 연락처','메모']].concat(AD.stu.map(s=>[s.name,s.grade,s.school,s.status||'재원',adClsOf(s.id).map(c=>c.name).join(' / '),s.joined_on,s.left_on,s.phone,s.guardian,s.guardian_phone,s.memo]));
 const blob=new Blob(['﻿'+rows.map(r=>r.map(q).join(',')).join('\r\n')],{type:'text/csv'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='원생명단_'+adDay()+'.csv';document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},3000)}

/* ---------- 반 · 시간표 ---------- */
function adTimetable(classes,o){o=o||{};const list=[];classes.forEach(c=>(c.sched||[]).forEach(t=>{if(t.d&&t.s)list.push({c,d:+t.d,s:t.s,e:t.e||''})}));
 const toM=x=>{const [h,m]=String(x).split(':').map(Number);return h*60+(m||0)};
 let lo=Math.min(...list.map(x=>toM(x.s)),14*60),hi=Math.max(...list.map(x=>toM(x.e||x.s)+60),22*60);lo=Math.floor(lo/60)*60;hi=Math.ceil(hi/60)*60;
 const rows=(hi-lo)/30,td=adDow(adDay()),days=o.days||[1,2,3,4,5,6,7];
 const head=`<div class="h tm"></div>${days.map(d=>`<div class="h ${d===td?'today':''}">${ADDAY[d]}</div>`).join('')}`;
 const tmc=`<div class="tm col" style="--rows:${rows}">${Array.from({length:rows/2},(_,i)=>`<div style="position:absolute;right:6px;top:${i*64+2}px">${String(lo/60+i).padStart(2,'0')}:00</div>`).join('')}</div>`;
 const cols=days.map(d=>`<div class="col" style="--rows:${rows};background:repeating-linear-gradient(to bottom,transparent 0 63px,var(--l) 63px 64px)">${list.filter(x=>x.d===d).map(x=>{const t=(toM(x.s)-lo)/30*32,h=Math.max(28,((toM(x.e||x.s)||toM(x.s)+60)-toM(x.s))/30*32-2);
  return `<div class="blk" style="--c:${esc(x.c.color||'#2f7fd0')};top:${t}px;height:${h}px" ${o.click?`onclick="${o.click}(${x.c.id})"`:''} title="${esc(x.c.name+' '+x.s+'–'+x.e)}"><b>${esc(x.c.name)}</b><span>${esc(x.s)}–${esc(x.e)}${x.c.room?' · '+esc(x.c.room):''}</span></div>`}).join('')}</div>`).join('');
 return list.length?`<div class="adtt">${head}${tmc}${cols}</div>`:'<div class="adempty">요일·시간이 들어간 반이 없어요.</div>'}
function adClsHtml(){
 const act=AD.cls.filter(c=>c.active!==false),old=AD.cls.filter(c=>c.active===false);
 const li=c=>{const mem=adMembers(c.id);return `<tr class="rowl" onclick="adClsEdit(${c.id})"><td><span class="adchip" style="--c:${esc(c.color||'#2f7fd0')}">${esc(c.name)}</span></td><td class="hm">${esc(c.subject||'')}</td><td>${(c.sched||[]).map(t=>ADDAY[t.d]+' '+esc(t.s||'')+(t.e?'–'+esc(t.e):'')).join(', ')||'<span class="m">시간 없음</span>'}</td><td class="hm">${esc(c.teacher||'')}${c.room?' · '+esc(c.room):''}</td><td>${mem.length}명</td><td class="hm">${c.tuition?adWon(c.tuition):''}</td></tr>`};
 return `<div class="card"><div class="adbar"><h2 style="margin:0;flex:1">주간 시간표</h2><button class="s" onclick="adTtPrint()">시간표 인쇄</button></div>${adTimetable(act,{click:'adClsEdit'})}</div>
 <div class="card"><div class="adbar"><h2 style="margin:0;flex:1">반 <small class="m">${act.length}개</small></h2><button class="p" onclick="adClsEdit(0)">＋ 반 만들기</button></div>
 <div class="tw"><table class="adtab"><thead><tr><th>반</th><th class="hm">과목</th><th>요일 · 시간</th><th class="hm">담당 · 강의실</th><th>학생</th><th class="hm">월 수강료</th></tr></thead><tbody>${act.map(li).join('')||'<tr><td colspan="6" class="adempty">아직 반이 없어요. 반을 만들고 학생을 넣으면 시간표·출결·월 청구에 쓰여요.</td></tr>'}</tbody></table></div>
 ${old.length?`<details style="margin-top:10px"><summary class="m">쉬는 반 ${old.length}개</summary><div class="tw"><table class="adtab"><tbody>${old.map(li).join('')}</tbody></table></div></details>`:''}</div>`}
const ADCOL=['#2f7fd0','#2f9d66','#d9622b','#6d4cc4','#c0392b','#0e9aa7','#b8860b','#596579'];
function adClsEdit(id){const c=id?AD.cls.find(x=>x.id===id):{name:'',sched:[],color:ADCOL[AD.cls.length%ADCOL.length],active:true};if(!c)return;AD.edit=id||0;AD.sch=JSON.parse(JSON.stringify(c.sched||[]));
 const mine=new Set(AD.mem.filter(m=>m.class_id===id).map(m=>m.student_id)),v=k=>esc(c[k]==null?'':c[k]);
 $('#cfgBox').innerHTML=`<h2 style="margin-top:0">${id?esc(c.name)+' 반':'반 만들기'}</h2><div class="adform">
 <label>반 이름<input id="adc_name" value="${v('name')}" maxlength="30" placeholder="예: 고2 화학 A"></label><label>과목<input id="adc_subject" value="${v('subject')}" maxlength="20"></label>
 <label>담당 선생님<input id="adc_teacher" value="${v('teacher')}" maxlength="20"></label><label>강의실<input id="adc_room" value="${v('room')}" maxlength="20"></label>
 <label>월 수강료(원)<input id="adc_tuition" type="number" min="0" step="1000" value="${v('tuition')}"></label><label>색<select id="adc_color">${ADCOL.map(x=>`<option value="${x}" ${c.color===x?'selected':''} style="color:${x}">■ ${x}</option>`).join('')}</select></label>
 <div class="w"><div class="m" style="margin-bottom:4px">요일 · 시간</div><div class="adsch" id="adc_sch">${adSchRows()}</div><button class="s sm" style="margin-top:6px" onclick="adSchAdd()">＋ 요일 추가</button></div>
 <div class="w"><div class="m" style="margin-bottom:4px">학생 (재원·휴원)</div><div class="adpick">${AD.stu.filter(s=>(s.status||'재원')!=='퇴원').map(s=>`<label class="chk"><input type="checkbox" value="${s.id}" ${mine.has(s.id)?'checked':''}> ${esc(s.name)} <small class="m">${esc(s.grade||'')}</small></label>`).join('')||'<span class="m">원생이 없어요</span>'}</div></div>
 <label class="w">메모<textarea id="adc_memo" maxlength="400">${v('memo')}</textarea></label>
 ${id?`<label class="chk w"><input type="checkbox" id="adc_active" ${c.active!==false?'checked':''}> 수업 중인 반 (끄면 시간표·월 청구에서 빠져요)</label>`:''}</div>
 <div class="row" style="margin-top:14px;justify-content:flex-end">${id?`<button class="s" onclick="adClsDel(${id})">반 지우기</button>`:''}<button class="s" onclick="closeCfg()">닫기</button><button class="p" onclick="adClsSave()">저장</button></div>`;
 $('#cfg').classList.add('open');try{cfgChrome()}catch(e){}}
function adSchRows(){return AD.sch.map((t,i)=>`<div><select aria-label="요일" onchange="AD.sch[${i}].d=+this.value">${[1,2,3,4,5,6,7].map(d=>`<option value="${d}" ${+t.d===d?'selected':''}>${ADDAY[d]}요일</option>`).join('')}</select><input type="time" aria-label="시작" value="${esc(t.s||'')}" onchange="AD.sch[${i}].s=this.value"> ~ <input type="time" aria-label="끝" value="${esc(t.e||'')}" onchange="AD.sch[${i}].e=this.value"><button class="s sm" aria-label="이 요일 빼기" onclick="AD.sch.splice(${i},1);$('#adc_sch').innerHTML=adSchRows()">✕</button></div>`).join('')||'<span class="m">요일을 추가하세요</span>'}
function adSchAdd(){const last=AD.sch[AD.sch.length-1];AD.sch.push(last?{d:Math.min(7,+last.d+2),s:last.s,e:last.e}:{d:1,s:'18:00',e:'20:00'});$('#adc_sch').innerHTML=adSchRows()}
async function adClsSave(){const g=k=>{const e=$('#adc_'+k);return e?e.value.trim():''};const name=g('name');if(!name){toast('반 이름을 입력해 주세요');return}
 const sched=AD.sch.filter(t=>t.d&&t.s).map(t=>({d:+t.d,s:t.s,e:t.e||''})).sort((a,b)=>a.d-b.d||a.s.localeCompare(b.s));
 const body={name,subject:g('subject')||null,teacher:g('teacher')||null,room:g('room')||null,tuition:g('tuition')?Math.max(0,Math.round(+g('tuition'))):null,color:g('color')||null,memo:g('memo')||null,sched};
 const ae=$('#adc_active');if(ae)body.active=ae.checked;
 const want=new Set([...document.querySelectorAll('#cfgBox .adpick input:checked')].map(i=>i.value));
 try{let id=AD.edit;if(id)await adPatch('classes','id=eq.'+id,body);else{const r=await adPost('classes',body,1);id=r&&r[0]&&r[0].id}
  const have=new Set(AD.mem.filter(m=>m.class_id===id).map(m=>m.student_id));
  const add=[...want].filter(s=>!have.has(s)).map(s=>({class_id:id,student_id:s}));if(add.length)await adPost('class_members',add);
  for(const s of have)if(!want.has(s))await adDel('class_members','class_id=eq.'+id+'&student_id=eq.'+s);
  closeCfg();toast('저장했어요');adReload()}catch(e){toast(adMissing(e)?'서버에 반 표가 없어요. sql_23_admin.sql 을 실행해 주세요':'저장하지 못했어요')}}
async function adClsDel(id){const c=AD.cls.find(x=>x.id===id);if(!c||!confirm('「'+c.name+'」 반을 지울까요? 학생 기록은 남고 반 배정만 사라져요.\n(잠시 쉬는 반이면 지우지 말고 「수업 중인 반」을 끄세요)'))return;try{await adDel('classes','id=eq.'+id);closeCfg();adReload()}catch(e){toast('지우지 못했어요')}}
function adTtPrint(){const w=typeof popOpen==='function'?popOpen('시간표를 만드는 중…'):window.open('','_blank');if(!w)return;
 const css=document.getElementById('adcss').textContent+':root{--surface:#fff;--l:#d9dee5;--sf1:#f3f5f8;--m:#5f6c7b;--b:#2a72bf;--t:#1f2933}body{font:13px Pretendard,sans-serif;margin:12mm;color:#1f2933}h1{font-size:20px;margin:0 0 8px}@page{size:A4 landscape;margin:0}';
 w.document.open();w.document.write('<!doctype html><meta charset="utf-8"><title>주간 시간표</title><style>'+css+'</style><h1>주간 시간표 · '+esc(adDay())+'</h1>'+adTimetable(AD.cls.filter(c=>c.active!==false))+'<script>setTimeout(()=>print(),400)<\/script>');w.document.close()}

/* ---------- 상담 일지 ---------- */
function adCnsHtml(){const f=AD.cnsF;const today=adDay();
 let L=AD.cns;if(f==='todo')L=L.filter(c=>c.next_on&&!c.done);else if(f&&f!=='all')L=L.filter(c=>c.student_id===f);
 const sname=f&&f!=='all'&&f!=='todo'?adName(f):'';
 return `<div class="card"><div class="adbar"><select onchange="AD.cnsF=this.value;adminView()" aria-label="학생으로 거르기"><option value="all">모든 상담</option><option value="todo" ${f==='todo'?'selected':''}>할 일 남은 상담</option>${AD.stu.map(s=>`<option value="${s.id}" ${f===s.id?'selected':''}>${esc(s.name)}</option>`).join('')}</select><span style="flex:1"></span><button class="p" onclick="adCnsEdit(0)">＋ 상담 기록</button></div>
 ${sname?`<p class="m" style="margin:0 0 8px">${esc(sname)} 학생 상담 ${L.length}건</p>`:''}
 <div class="adl">${L.slice(0,200).map(c=>`<div><span class="t">${esc(c.day)}</span><span class="g"><b>${esc(adName(c.student_id))}</b> <span class="adchip" style="--c:${c.kind==='학부모'?'#6d4cc4':c.kind==='입학'?'#2f9d66':'#596579'}">${esc(c.kind)}</span>${c.share?' <span class="adchip" style="--c:#0e9aa7">학부모 공유</span>':''}<small style="white-space:pre-wrap;color:var(--t);margin-top:4px">${esc(c.body)}</small>${c.next_on||c.next_todo?`<small>다음: ${esc(c.next_on||'')} ${esc(c.next_todo||'')}${c.done?' · 완료':c.next_on&&c.next_on<today?' · <b style="color:#c0392b">지남</b>':''}</small>`:''}${c.by_name?`<small>기록: ${esc(c.by_name)}</small>`:''}</span>${c.next_on&&!c.done?`<button class="s sm" onclick="adCnsDone(${c.id})">완료</button>`:''}<button class="s sm" onclick="adCnsEdit(${c.id})">고치기</button></div>`).join('')||'<div class="adempty">상담 기록이 없어요.</div>'}</div></div>`}
function adCnsEdit(id){const c=id?AD.cns.find(x=>x.id===id):{student_id:AD.cnsF&&AD.cnsF.length>10?AD.cnsF:'',day:adDay(),kind:'학생',body:'',share:false};if(!c)return;AD.edit=id||0;
 $('#cfgBox').innerHTML=`<h2 style="margin-top:0">${id?'상담 고치기':'상담 기록'}</h2><div class="adform">
 <label>학생<select id="adn_stu">${AD.stu.map(s=>`<option value="${s.id}" ${c.student_id===s.id?'selected':''}>${esc(s.name)} ${esc(s.grade||'')}</option>`).join('')}</select></label><label>날짜<input id="adn_day" type="date" value="${esc(c.day)}"></label>
 <label>상담 대상 · 종류<select id="adn_kind">${ADCNS.map(k=>`<option ${c.kind===k?'selected':''}>${k}</option>`).join('')}</select></label><label>기록한 사람<input id="adn_by" value="${esc(c.by_name||'')}" maxlength="20" placeholder="예: 김 선생님"></label>
 <label class="w">내용<textarea id="adn_body" maxlength="3000" placeholder="무엇을 이야기했는지, 학생·학부모의 요청, 합의한 것">${esc(c.body)}</textarea></label>
 <label>다음 상담·확인 날짜<input id="adn_next" type="date" value="${esc(c.next_on||'')}"></label><label>다음에 할 일<input id="adn_todo" value="${esc(c.next_todo||'')}" maxlength="100"></label>
 <label class="chk w"><input type="checkbox" id="adn_share" ${c.share?'checked':''}> 학부모 앱에 이 기록 보여 주기</label></div>
 <div class="row" style="margin-top:14px;justify-content:flex-end">${id?`<button class="s" onclick="adCnsDel(${id})">지우기</button>`:''}<button class="s" onclick="closeCfg()">닫기</button><button class="p" onclick="adCnsSave()">저장</button></div>`;
 $('#cfg').classList.add('open');try{cfgChrome()}catch(e){}}
async function adCnsSave(){const g=k=>{const e=$('#adn_'+k);return e?e.value.trim():''};const body=g('body');if(!body){toast('내용을 적어 주세요');return}if(!g('stu')){toast('학생을 골라 주세요');return}
 const b={student_id:g('stu'),day:g('day')||adDay(),kind:g('kind'),body,by_name:g('by')||null,next_on:g('next')||null,next_todo:g('todo')||null,share:$('#adn_share').checked};
 try{if(AD.edit)await adPatch('counsels','id=eq.'+AD.edit,b);else await adPost('counsels',b);closeCfg();toast('저장했어요');adReload()}catch(e){toast(adMissing(e)?'서버에 상담 표가 없어요. sql_23_admin.sql 을 실행해 주세요':'저장하지 못했어요')}}
async function adCnsDone(id){try{await adPatch('counsels','id=eq.'+id,{done:true});const c=AD.cns.find(x=>x.id===id);if(c)c.done=true;adminView()}catch(e){toast('바꾸지 못했어요')}}
async function adCnsDel(id){if(!confirm('이 상담 기록을 지울까요?'))return;try{await adDel('counsels','id=eq.'+id);closeCfg();adReload()}catch(e){toast('지우지 못했어요')}}

/* ---------- 보강 ---------- */
function adMkuHtml(){const f=AD.mkuF,L=AD.mku.filter(k=>f==='all'||k.status===f);
 // 최근 30일 결석·사유 결석 중 보강이 없는 것
 const since=adDay(new Date(Date.now()-30*864e5)),have=new Set(AD.mku.map(k=>k.student_id+'|'+k.missed_on));
 const miss=AD.matt.filter(a=>(a.status==='absent'||a.status==='excused')&&a.day>=since&&!have.has(a.student_id+'|'+a.day));
 return `${miss.length?`<div class="card"><h2>보강이 없는 결석 <small class="m">최근 30일 · 이번 달 출결 기록</small></h2><div class="adl">${miss.slice(0,20).map(a=>`<div><span class="t">${esc(a.day)}</span><span class="g"><b>${esc(adName(a.student_id))}</b><small>${a.status==='excused'?'사유 결석':'결석'} · ${adClsOf(a.student_id).map(c=>esc(c.name)).join(', ')||'반 없음'}</small></span><button class="s sm" onclick="adMkuEdit(0,'${a.student_id}','${a.day}')">보강 잡기</button></div>`).join('')}</div></div>`:''}
 <div class="card"><div class="adbar"><div class="bkseg">${[['예정','예정'],['완료','완료'],['취소','취소'],['all','전체']].map(([v,l])=>`<button class="${f===v?'on':''}" onclick="AD.mkuF='${v}';adminView()">${l}</button>`).join('')}</div><span style="flex:1"></span><button class="p" onclick="adMkuEdit(0)">＋ 보강 등록</button></div>
 <div class="adl">${L.map(k=>`<div><span class="t">${k.plan_at?esc(adTime(k.plan_at)):'일정 미정'}</span><span class="g"><b>${esc(adName(k.student_id))}</b><small>${esc(k.missed_on)} 빠짐${k.class_id?' · '+esc((AD.cls.find(c=>c.id===k.class_id)||{}).name||''):''}${k.reason?' · '+esc(k.reason):''}${k.memo?' · '+esc(k.memo):''}</small></span><span class="adchip" style="--c:${k.status==='완료'?'#1f9d55':k.status==='취소'?'#8a94a3':'#2f7fd0'}">${esc(k.status)}</span>${k.status==='예정'?`<button class="s sm" onclick="adMkuSet(${k.id},'완료')">완료</button>`:''}<button class="s sm" onclick="adMkuEdit(${k.id})">고치기</button></div>`).join('')||'<div class="adempty">보강이 없어요.</div>'}</div></div>`}
function adMkuEdit(id,sid,day){const k=id?AD.mku.find(x=>x.id===id):{student_id:sid||'',missed_on:day||adDay(),status:'예정'};if(!k)return;AD.edit=id||0;
 const cls=k.student_id?adClsOf(k.student_id):AD.cls;const pl=k.plan_at?new Date(new Date(k.plan_at).getTime()+9*36e5).toISOString().slice(0,16):'';
 $('#cfgBox').innerHTML=`<h2 style="margin-top:0">${id?'보강 고치기':'보강 등록'}</h2><div class="adform">
 <label>학생<select id="adm_stu">${AD.stu.map(s=>`<option value="${s.id}" ${k.student_id===s.id?'selected':''}>${esc(s.name)} ${esc(s.grade||'')}</option>`).join('')}</select></label><label>반<select id="adm_cls"><option value="">—</option>${cls.map(c=>`<option value="${c.id}" ${k.class_id===c.id?'selected':''}>${esc(c.name)}</option>`).join('')}</select></label>
 <label>빠진 날<input id="adm_miss" type="date" value="${esc(k.missed_on)}"></label><label>보강 일시<input id="adm_plan" type="datetime-local" value="${pl}"></label>
 <label>사유<input id="adm_reason" value="${esc(k.reason||'')}" maxlength="60" placeholder="예: 병결, 학교 행사"></label><label>상태<select id="adm_status">${['예정','완료','취소'].map(x=>`<option ${k.status===x?'selected':''}>${x}</option>`).join('')}</select></label>
 <label class="w">메모<input id="adm_memo" value="${esc(k.memo||'')}" maxlength="120"></label></div>
 <div class="row" style="margin-top:14px;justify-content:flex-end">${id?`<button class="s" onclick="adMkuDel(${id})">지우기</button>`:''}<button class="s" onclick="closeCfg()">닫기</button><button class="p" onclick="adMkuSave()">저장</button></div>`;
 $('#cfg').classList.add('open');try{cfgChrome()}catch(e){}}
async function adMkuSave(){const g=k=>{const e=$('#adm_'+k);return e?e.value.trim():''};if(!g('stu')||!g('miss')){toast('학생과 빠진 날을 넣어 주세요');return}
 const p=g('plan');const b={student_id:g('stu'),class_id:g('cls')?+g('cls'):null,missed_on:g('miss'),plan_at:p?new Date(p+':00+09:00').toISOString():null,reason:g('reason')||null,status:g('status'),memo:g('memo')||null};
 try{if(AD.edit)await adPatch('makeups','id=eq.'+AD.edit,b);else await adPost('makeups',b);closeCfg();toast('저장했어요');adReload()}catch(e){toast(adMissing(e)?'서버에 보강 표가 없어요. sql_23_admin.sql 을 실행해 주세요':'저장하지 못했어요')}}
async function adMkuSet(id,st){try{await adPatch('makeups','id=eq.'+id,{status:st});const k=AD.mku.find(x=>x.id===id);if(k)k.status=st;adminView()}catch(e){toast('바꾸지 못했어요')}}
async function adMkuDel(id){if(!confirm('이 보강을 지울까요?'))return;try{await adDel('makeups','id=eq.'+id);closeCfg();adReload()}catch(e){toast('지우지 못했어요')}}

/* ---------- 월 일괄 청구 · 영수증 ---------- */
function adBillPlan(ym){const [y,m]=ym.split('-').map(Number),title=y+'년 '+m+'월 ';const out=[];
 AD.cls.filter(c=>c.active!==false&&c.tuition>0).forEach(c=>adMembers(c.id).filter(s=>(s.status||'재원')==='재원').forEach(s=>{const t=title+c.name+' 수강료';
  out.push({s,c,title:t,amount:c.tuition,dup:AD.fees.some(f=>f.student_id===s.id&&f.title===t)})}));return out}
function adBillHtml(){if(!AD.bm){const d=new Date(Date.now()+9*36e5);AD.bm=d.toISOString().slice(0,7)}
 const P=adBillPlan(AD.bm),todo=P.filter(x=>!x.dup),sum=todo.reduce((a,x)=>a+x.amount,0);
 const paid=AD.fees.filter(f=>(f.paid_amount||0)>=f.amount&&f.paid_at).slice(0,60);
 return `<div class="card"><h2>월 수강료 일괄 청구</h2><p class="m" style="margin:-6px 0 10px">「반 · 시간표」의 월 수강료로 재원생에게 한 번에 청구해요. 이미 같은 이름으로 청구한 학생은 건너뛰어요. 학부모 앱의 수납 화면에 바로 보여요.</p>
 <div class="adbar"><label class="m">청구할 달 <input type="month" value="${AD.bm}" onchange="AD.bm=this.value||AD.bm;adminView()"></label><label class="m">납부 기한 <input type="date" id="adb_due" value="${AD.bm}-10"></label><span style="flex:1"></span><button class="p" ${todo.length?'':'disabled'} onclick="adBillGo()">${todo.length}건 · ${adWon(sum)} 청구하기</button></div>
 <div class="tw"><table class="adtab"><thead><tr><th>학생</th><th>반</th><th>금액</th><th></th></tr></thead><tbody>${P.map(x=>`<tr><td>${esc(x.s.name)}</td><td>${esc(x.c.name)}</td><td>${adWon(x.amount)}</td><td>${x.dup?'<span class="adchip" style="--c:#8a94a3">이미 청구</span>':''}</td></tr>`).join('')||'<tr><td colspan="4" class="adempty">월 수강료가 있는 반에 든 재원생이 없어요. 「반 · 시간표」에서 반마다 월 수강료를 넣어 주세요.</td></tr>'}</tbody></table></div></div>
 <div class="card"><h2>영수증</h2><p class="m" style="margin:-6px 0 10px">납부를 마친 청구의 영수증을 인쇄하거나 PDF로 저장해요. 학원 이름·로고는 「학원 설정」을 따라요.</p><div class="adl">${paid.map(f=>`<div><span class="t">${esc(String(f.paid_at).slice(0,10))}</span><span class="g"><b>${esc(adName(f.student_id))}</b><small>${esc(f.title)} · ${esc(f.method||'')}</small></span><b>${adWon(f.amount)}</b><button class="s sm" onclick="adReceipt(${f.id})">영수증</button></div>`).join('')||'<div class="adempty">납부 완료된 청구가 없어요.</div>'}</div></div>`}
async function adBillGo(){const todo=adBillPlan(AD.bm).filter(x=>!x.dup);if(!todo.length)return;const due=($('#adb_due')||{}).value||null;
 if(!confirm(todo.length+'건, 모두 '+adWon(todo.reduce((a,x)=>a+x.amount,0))+'을 청구할까요?'))return;
 try{await adPost('fees',todo.map(x=>({student_id:x.s.id,kind:'tuition',title:x.title,amount:x.amount,due})));toast(todo.length+'건을 청구했어요');adReload()}catch(e){toast(adMissing(e)?'서버에 수납 표가 없어요. sql_20_attendance_billing.sql 을 실행해 주세요':'청구하지 못했어요')}}
function adReceipt(id){const f=AD.fees.find(x=>x.id===id);if(!f)return;const s=adStu(f.student_id)||{};let ac={};try{ac=acCfg()}catch(e){}
 const name=ac.name||'학원',no='R-'+String(f.id).padStart(6,'0');const w=typeof popOpen==='function'?popOpen('영수증을 만드는 중…'):window.open('','_blank');if(!w)return;
 const row=(k,v)=>'<tr><th>'+k+'</th><td>'+v+'</td></tr>';
 w.document.open();w.document.write('<!doctype html><meta charset="utf-8"><title>영수증 '+no+'</title><style>body{font:14px Pretendard,"Apple SD Gothic Neo",sans-serif;color:#1f2933;margin:0}@page{size:A5;margin:0}.r{width:148mm;min-height:200mm;margin:0 auto;padding:16mm 14mm;box-sizing:border-box}h1{font-size:24px;letter-spacing:.4em;text-align:center;margin:0 0 4mm}.no{text-align:center;color:#5f6c7b;font-size:12px;margin-bottom:10mm}table{width:100%;border-collapse:collapse}th,td{border-bottom:1px solid #d9dee5;padding:3mm 2mm;text-align:left}th{width:32mm;color:#5f6c7b;font-weight:600}.amt{font-size:22px;font-weight:800}.ft{margin-top:14mm;text-align:right}.ft b{font-size:18px}.note{margin-top:8mm;font-size:12px;color:#5f6c7b;line-height:1.6}</style><div class="r"><h1>영 수 증</h1><div class="no">'+no+'</div><table>'+
  row('학생',esc(s.name||''))+row('보호자',esc(s.guardian||''))+row('내용',esc(f.title))+row('금액','<span class="amt">'+adWon(f.amount)+'</span>')+row('납부일',esc(String(f.paid_at||'').slice(0,10)))+row('납부 방법',esc(f.method||''))+'</table><div class="ft">위 금액을 정히 영수합니다.<br><br><b>'+esc(name)+'</b></div><div class="note">이 영수증은 학원 내부 확인용이에요. 교육비 소득공제·현금영수증·카드 매출전표가 필요하면 학원에 따로 요청해 주세요.</div></div><script>setTimeout(()=>print(),400)<\/script>');w.document.close()}

/* ---------- 학생 · 학부모: 시간표 ---------- */
const SCH={d:null,ld:0,err:''};
async function schedView(){const m=$('#main');adCss();
 if(!STUD){m.innerHTML='<div class="card"><div class="hint">학생·학부모 계정으로 로그인하면 내 반 시간표와 보강 일정을 볼 수 있어요.</div></div>';return}
 if(!SCH.ld){m.innerHTML='<div class="card">'+ldg('시간표를 불러오는 중…')+'</div>';SCH.err='';
  try{const r=await rpc(STUD.parent?'pa_schedule':'st_schedule',{p_login:STUD.login,p_pw:STUD.pw});if(!r.ok){SCH.err=r.status===404?'준비 중':'불러오지 못했어요';}else SCH.d=await r.json()}catch(e){SCH.err='불러오지 못했어요'}SCH.ld=1}
 if(SCH.err||!SCH.d){m.innerHTML=`<div class="card"><h2>시간표</h2><div class="hint">${SCH.err==='준비 중'?'선생님이 아직 시간표를 준비하지 않았어요.':esc(SCH.err||'시간표가 없어요.')}</div><button class="s sm" style="margin-top:10px" onclick="SCH.ld=0;schedView()">다시 불러오기</button></div>`;return}
 const d=SCH.d,today=adDay(),w=adDow(today);const cls=d.classes||[];
 const td=[];cls.forEach(c=>(c.sched||[]).forEach(t=>{if(+t.d===w)td.push({c,s:t.s,e:t.e})}));td.sort((a,b)=>String(a.s).localeCompare(String(b.s)));
 const mk=(d.makeups||[]).filter(x=>x.status==='예정'),cn=d.counsels||[];
 m.innerHTML=`<div class="tsh"><div><h1>시간표</h1><p>${STUD.parent?'자녀의 ':''}반 시간표와 보강 일정이에요.</p></div></div>
 <div class="card"><h2>오늘 (${ADDAY[w]}요일)</h2><div class="adl">${td.map(x=>`<div><span class="t">${esc(x.s)}${x.e?'–'+esc(x.e):''}</span><span class="g"><b>${esc(x.c.name)}</b><small>${esc([x.c.teacher,x.c.room].filter(Boolean).join(' · '))}</small></span></div>`).join('')||'<div class="adempty">오늘은 수업이 없어요.</div>'}</div></div>
 <div class="card"><h2>주간 시간표</h2>${adTimetable(cls)}</div>
 <div class="card"><h2>보강</h2><div class="adl">${mk.map(x=>`<div><span class="t">${x.plan_at?esc(adTime(x.plan_at)):'일정 미정'}</span><span class="g"><b>${esc(x.class||'보강')}</b><small>${esc(x.missed_on)} 빠진 수업${x.reason?' · '+esc(x.reason):''}</small></span></div>`).join('')||'<div class="adempty">예정된 보강이 없어요.</div>'}</div></div>
 ${STUD.parent?`<div class="card"><h2>상담 기록</h2><div class="adl">${cn.map(c=>`<div><span class="t">${esc(c.day)}</span><span class="g"><b>${esc(c.kind)} 상담</b><small style="white-space:pre-wrap;color:var(--t)">${esc(c.body)}</small>${c.next_on||c.next_todo?`<small>다음: ${esc(c.next_on||'')} ${esc(c.next_todo||'')}</small>`:''}</span></div>`).join('')||'<div class="adempty">선생님이 공유한 상담 기록이 없어요.</div>'}</div></div>`:''}`}
