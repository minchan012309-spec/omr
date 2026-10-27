/* Solvi 늦게 불러오는 코드: acad — 출결 · 학부모 안내문 · 수납 · 출결 단말. index.html 의 전역(sb, rpc, esc, $, toast, STUD …)을 그대로 씁니다. */
const TOSS_KEY='test_ck_ALnQvDd2VJml6AZbKqDw3Mj7X41m';
const AC={sec:'day',day:'',mon:'',sid:'',stu:[],recs:[],mrecs:[],fees:[],notes:[],pay:{items:[],demo:false,clientKey:'',bank:''},ld:0,err:'',q:''};
const AST={in:['출석','#1f9d55'],late:['지각','#e09a00'],absent:['결석','#d9534f'],excused:['사유','#7a8aa0']};
const kstDay=(d)=>new Date((d||new Date()).getTime()+9*36e5).toISOString().slice(0,10);
const kstTime=t=>t?new Date(t).toLocaleTimeString('ko-KR',{hour:'2-digit',minute:'2-digit',hour12:false,timeZone:'Asia/Seoul'}):'';
const won=n=>(+n||0).toLocaleString('ko-KR')+'원';
const pinFrom=p=>{let d=String(p||'').replace(/\D/g,'');if(d.startsWith('010'))d=d.slice(3);return d.slice(0,5)};
const SQLMSG='<div class="hint"><b>서버에 출결·수납 표가 아직 없어요.</b> Supabase 「SQL Editor」에서 <code>supabase/sql_20_attendance_billing.sql</code> 내용을 한 번 실행해 주세요.</div>';
const needCloud=()=>!(typeof cloud==='function'&&cloud()&&sess);
const atNeed='<div class="card"><div class="hint"><b>온라인 저장에 로그인해야 쓸 수 있어요.</b> 출결·안내문·수납은 서버에 저장돼서 학부모 앱에도 보여요.</div></div>';
const SEGS=[['day','출결'],['month','월간 달력'],['pin','출결 번호']],FSEGS=[['bill','월 청구 · 영수증'],['fee','청구 · 납부 내역'],['rate','요금 · 계좌']]; // 왼쪽 메뉴 「출결」(att) · 「수납」(fee)

async function acJ(path,o){const r=await sb(path,o);if(!r.ok){const e=new Error('http '+r.status);e.status=r.status;try{e.body=await r.text()}catch(x){}throw e}const t=await r.text();return t?JSON.parse(t):null}
const acMissing=e=>e&&(e.status===404||e.status===400||/does not exist|schema cache|column/i.test(e.body||''));

async function attView(){
 const m=$('#main');if(needCloud()){m.innerHTML=atNeed;return}
 const isFee=tab==='fee',S=isFee?FSEGS:SEGS;
 if(!S.some(x=>x[0]===AC.sec)){AC.sec=S[0][0];AC.ld=0}if(!AC.day)AC.day=kstDay();if(!AC.mon)AC.mon=AC.day.slice(0,7);
 if(!AC.ld){m.innerHTML='<div class="card">'+ldg('불러오는 중…')+'</div>';await acLoad()}
 if(AC.sec==='bill'){await lazyLoad('admin');adCss();if(!AD.ld)await adLoad()} // 월 청구는 학원 운영 코드(admin.js)의 것을 그대로 쓴다
 const seg=`<div class="bkseg axseg" role="tablist">${S.map(([k,l])=>`<button role="tab" aria-selected="${AC.sec===k}" class="${AC.sec===k?'on':''}" onclick="acSec('${k}')">${l}${k==='fee'&&AC.fees.some(f=>(f.paid_amount||0)<f.amount)?' <i class="axdot"></i>':''}</button>`).join('')}</div>`;
 const err=AC.sec==='bill'&&AD.err?AD.err:AC.err;
 const body=err==='sql'?(AC.sec==='bill'?adSql:SQLMSG):err?`<div class="hint">${esc(err)}</div><button class="s sm" style="margin-top:10px" onclick="AC.ld=0;${AC.sec==='bill'?'AD.ld=0;':''}attView()">다시 불러오기</button>`:({day:acDayHtml,month:acMonthHtml,pin:acPinHtml,fee:acFeeHtml,rate:acRateHtml,bill:()=>adBillHtml()}[AC.sec]||S===SEGS&&acDayHtml||acFeeHtml)();
 m.innerHTML=isFee?`<div class="tsh"><div><h1>수납</h1><p>반 수강료로 한 달 청구를 만들고, 납부를 기록하고, 영수증을 내요. 학부모 앱에서 바로 납부할 수도 있어요.</p></div></div>${seg}${body}`
  :`<div class="tsh"><div><h1>출결</h1><p>등원 · 하원 기록과 월간 달력, 출결 단말 번호를 관리해요. 학부모 앱에서도 바로 확인할 수 있어요.</p></div><div class="tsb"><button class="p" onclick="kioskOpen()">출결 단말 시작</button></div></div>${seg}${body}`}
async function diaryView(){
 const m=$('#main');if(needCloud()){m.innerHTML=atNeed;return}
 if(!AC.ld||AC.sec!=='diary'){AC.sec='diary';m.innerHTML='<div class="card">'+ldg('불러오는 중…')+'</div>';AC.err='';
  try{AC.stu=await acJ('/rest/v1/students?select=id,name,grade,phone,att_pin&order=name.asc&limit=2000');const a=await acJ('/rest/v1/notices?select=*&order=t.desc&limit=60');let b=[];try{b=await acJ('/rest/v1/parent_notices?select=*&order=created_at.desc&limit=30')}catch(e){}AC.notes=[...a.map(n=>({src:'n',id:n.id,title:n.title,body:n.body,t:+n.t,sid:n.student_id,aud:n.audience||'student'})),...b.map(n=>({src:'p',id:n.id,title:n.title,body:n.body,t:new Date(n.created_at).getTime(),sid:n.student_id,aud:'parent'}))].sort((x,y)=>y.t-x.t);AC.tpl=Object.assign({hw:[],msg:[]},((await tsRaw())||{}).diaryTpl||{});AC.ld=1}
  catch(e){AC.err=acMissing(e)?'sql':'불러오지 못했어요. 연결을 확인해 주세요.'}}
 m.innerHTML=`<div class="tsh"><div><h1>알림장</h1><p>오늘 나간 진도와 숙제를 학생·학부모에게 보내요.</p></div></div>${AC.err==='sql'?SQLMSG:AC.err?`<div class="hint">${esc(AC.err)}</div><button class="s sm" style="margin-top:10px" onclick="AC.ld=0;AC.sec==='diary'?diaryView():attView()">다시 불러오기</button>`:acNoteHtml()}`;if(!AC.err)acDraftLoad()}
function acSec(k){AC.sec=k;AC.ld=0;if(k==='bill'&&typeof AD!=='undefined')AD.ld=0;attView()}
async function acLoad(){
 AC.err='';
 try{
  AC.stu=await acJ('/rest/v1/students?select=id,name,grade,phone,att_pin&order=name.asc&limit=2000');
  if(AC.sec==='day')AC.recs=await acJ('/rest/v1/attendance?select=*&day=eq.'+AC.day);
  if(AC.sec==='month'&&AC.sid)AC.mrecs=await acJ('/rest/v1/attendance?select=*&student_id=eq.'+AC.sid+'&day=gte.'+AC.mon+'-01&day=lte.'+AC.mon+'-31');
  if(AC.sec==='fee')AC.fees=await acJ('/rest/v1/fees?select=*&order=created_at.desc&limit=600');
  if(AC.sec==='fee'||AC.sec==='rate'){const d=(await tsRaw())||{};AC.pay=Object.assign({items:[],bank:''},d.pay||{})}
 }catch(e){AC.err=acMissing(e)?'sql':'불러오지 못했어요 ('+(e.status||'연결')+')'}
 AC.ld=1}
const acStuName=id=>{const s=AC.stu.find(x=>x.id===id);return s?s.name:'(삭제된 학생)'};

/* ---------- 출결: 날짜별 ---------- */
function acDayHtml(){
 const by={};AC.recs.forEach(r=>by[r.student_id]=r);
 const q=AC.q.trim();const list=AC.stu.filter(s=>!q||(s.name+' '+(s.grade||'')).includes(q));
 const cnt={in:0,late:0,absent:0,excused:0,none:0};AC.stu.forEach(s=>{const r=by[s.id];cnt[r?r.status:'none']++});
 const rows=list.map(s=>{const r=by[s.id],st=r?r.status:'';
  return `<div class="axr"><div class="axn"><b class="axlk" role="button" tabindex="0" title="이 학생 출결 달력" onclick="AC.sid='${s.id}';acSec('month')">${esc(s.name)}</b><small>${esc(s.grade||'')}</small></div>
  <div class="axt">${r&&r.t_in?'<span title="등원">▶ '+kstTime(r.t_in)+'</span>':''}${r&&r.t_out?'<span title="하원">■ '+kstTime(r.t_out)+'</span>':''}</div>
  <div class="axq">${Object.keys(AST).map(k=>`<button class="axb ${st===k?'on':''}" style="--c:${AST[k][1]}" onclick="acSet('${s.id}','${k}')">${AST[k][0]}</button>`).join('')}${r?`<button class="axb x" title="기록 지우기" onclick="acClr('${s.id}')">✕</button>`:''}</div></div>`}).join('');
 return `<div class="card"><div class="row" style="gap:8px;flex-wrap:wrap"><button class="s sm" onclick="acDay(-1)">‹</button><input type="date" aria-label="출결 날짜" value="${AC.day}" onchange="AC.day=this.value||AC.day;AC.ld=0;attView()"><button class="s sm" onclick="acDay(1)">›</button><button class="s sm" onclick="AC.day=kstDay();AC.ld=0;attView()">오늘</button><button class="s sm" onclick="acAllIn()" title="아직 기록이 없는 학생을 모두 출석으로 기록해요">미기록 전원 출석</button>
 <input type="search" placeholder="이름·학년 검색" value="${esc(AC.q)}" oninput="AC.q=this.value;clearTimeout(window._acq);window._acq=setTimeout(()=>{const k=$('#acrows');if(k)k.innerHTML=acRowsOnly()},180)" style="margin-left:auto;width:190px"></div>
 ${AC.undo&&AC.undo.day===AC.day?`<div class="axundo" role="status"><span>${AC.undo.ids.length}명을 출석으로 기록했어요</span><button class="s sm" onclick="acUndo()">되돌리기</button></div>`:''}
 <div class="axsum"><span style="--c:#1f9d55"><b>${cnt.in}</b>출석</span><span style="--c:#e09a00"><b>${cnt.late}</b>지각</span><span style="--c:#d9534f"><b>${cnt.absent}</b>결석</span><span style="--c:#7a8aa0"><b>${cnt.excused}</b>사유</span><span style="--c:#9aa6b4"><b>${cnt.none}</b>미기록</span></div>
 <div id="acrows">${rows||'<div class="empty">등록한 학생이 없어요.</div>'}</div>
 <p class="tsn2">출결 단말(태블릿)에서 번호를 입력하면 등원이 기록되고, 같은 날 한 번 더 입력하면 하원이 기록돼요. 여기서 직접 고칠 수도 있어요.</p></div>`}
async function acAllIn(){
 const have=new Set(AC.recs.map(r=>r.student_id)),ids=AC.stu.filter(s=>!have.has(s.id)).map(s=>s.id);
 if(!ids.length){toast('기록이 없는 학생이 없어요');return}
 if(!confirm('기록이 없는 '+ids.length+'명을 '+AC.day.slice(5).replace('-','월 ')+'일 출석으로 기록할까요?'))return;
 const now=new Date().toISOString(),rows=ids.map(id=>({student_id:id,day:AC.day,status:'in',t_in:now}));
 try{await acJ('/rest/v1/attendance?on_conflict=student_id,day',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify(rows)});AC.undo={day:AC.day,ids};AC.ld=0;attView()}
 catch(e){toast('기록하지 못했어요. 연결을 확인하고 다시 눌러 주세요')}}
async function acUndo(){const u=AC.undo;if(!u)return;
 try{await acJ('/rest/v1/attendance?day=eq.'+u.day+'&student_id=in.('+u.ids.join(',')+')',{method:'DELETE'});AC.undo=null;AC.ld=0;attView()}
 catch(e){toast('되돌리지 못했어요')}}
function acRowsOnly(){const d=document.createElement('div');d.innerHTML=acDayHtml();const k=d.querySelector('#acrows');return k?k.innerHTML:''}
function acDay(n){const d=new Date(AC.day+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+n);AC.day=d.toISOString().slice(0,10);AC.ld=0;attView()}
async function acSet(sid,st){const body={student_id:sid,day:AC.day,status:st};if(st==='in'||st==='late'){const r=AC.recs.find(x=>x.student_id===sid);if(!r||!r.t_in)body.t_in=new Date().toISOString()}
 try{const rs=await acJ('/rest/v1/attendance?on_conflict=student_id,day',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=representation'},body:JSON.stringify(body)});const n=(rs&&rs[0])||body;const i=AC.recs.findIndex(x=>x.student_id===sid);if(i>=0)AC.recs[i]=Object.assign(AC.recs[i],n);else AC.recs.push(n);attView()}catch(e){toast('저장하지 못했어요')}}
async function acClr(sid){try{await acJ('/rest/v1/attendance?student_id=eq.'+sid+'&day=eq.'+AC.day,{method:'DELETE'});AC.recs=AC.recs.filter(x=>x.student_id!==sid);attView()}catch(e){toast('지우지 못했어요')}}

/* ---------- 월간 달력 (선생님·학부모 공용) ---------- */
function acCal(recs,ym,o){o=o||{};
 const by={};recs.forEach(r=>by[r.day]=r);const [Y,M]=ym.split('-').map(Number);const first=new Date(Date.UTC(Y,M-1,1)).getUTCDay(),n=new Date(Date.UTC(Y,M,0)).getUTCDate(),td=kstDay();
 let h='<div class="axcal">'+['일','월','화','수','목','금','토'].map((d,i)=>`<i class="dw${i%6?'':' we'}">${d}</i>`).join('');
 for(let i=0;i<first;i++)h+='<u></u>';
 for(let d=1;d<=n;d++){const k=ym+'-'+String(d).padStart(2,'0'),r=by[k],st=r?AST[r.status]:null;
  h+=`<b class="${k===td?'td':''}${st?' has':''}" ${st?`style="--c:${st[1]}" title="${st[0]}${!o.noTime&&r.t_in?' · 등원 '+kstTime(r.t_in):''}${!o.noTime&&r.t_out?' · 하원 '+kstTime(r.t_out):''}"`:''}><em>${d}</em>${st?`<span>${st[0]}</span>${!o.noTime&&r.t_in?`<small>${kstTime(r.t_in)}${r.t_out?'–'+kstTime(r.t_out):''}</small>`:''}`:''}</b>`}
 h+='</div>';
 const c={in:0,late:0,absent:0,excused:0};recs.forEach(r=>{if(c[r.status]!=null)c[r.status]++});
 return h+`<div class="axsum" style="margin-top:12px"><span style="--c:#1f9d55"><b>${c.in}</b>출석</span><span style="--c:#e09a00"><b>${c.late}</b>지각</span><span style="--c:#d9534f"><b>${c.absent}</b>결석</span><span style="--c:#7a8aa0"><b>${c.excused}</b>사유</span></div>`}
const ymAdd=(ym,n)=>{const [Y,M]=ym.split('-').map(Number);const d=new Date(Date.UTC(Y,M-1+n,1));return d.toISOString().slice(0,7)};
function acMonthHtml(){
 const opts=AC.stu.map(s=>`<option value="${s.id}" ${s.id===AC.sid?'selected':''}>${esc(s.name)} ${esc(s.grade||'')}</option>`).join('');
 return `<div class="card"><div class="row" style="gap:8px;flex-wrap:wrap"><select onchange="AC.sid=this.value;AC.ld=0;attView()"><option value="">학생 선택</option>${opts}</select><button class="s sm" onclick="AC.mon=ymAdd(AC.mon,-1);AC.ld=0;attView()">‹</button><b>${AC.mon.replace('-','년 ')}월</b><button class="s sm" onclick="AC.mon=ymAdd(AC.mon,1);AC.ld=0;attView()">›</button>${AC.mon!==kstDay().slice(0,7)?`<button class="s sm" onclick="AC.mon=kstDay().slice(0,7);AC.ld=0;attView()">이번 달</button>`:''}</div>
 ${AC.sid?acCal(AC.mrecs,AC.mon):'<div class="empty">학생을 고르면 한 달 출결이 달력으로 보여요. 학부모 앱에서도 같은 모양으로 보여요.</div>'}</div>`}

/* ---------- 출결 번호(전화번호 일부가 기본값) ---------- */
function acPinHtml(){
 const cnt={};AC.stu.forEach(s=>{if(s.att_pin)cnt[s.att_pin]=(cnt[s.att_pin]||0)+1});const dup=Object.values(cnt).filter(n=>n>1).length;
 const rows=AC.stu.map(s=>`<div class="axp"><b>${esc(s.name)}<small>${esc(s.grade||'')}</small></b><input type="tel" inputmode="numeric" placeholder="전화번호 예) 010-1234-5678" value="${esc(s.phone||'')}" onchange="acPhone('${s.id}',this.value)"><input class="pin ${s.att_pin&&cnt[s.att_pin]>1?'dup':''}" type="text" inputmode="numeric" maxlength="8" placeholder="출결 번호" value="${esc(s.att_pin||'')}" onchange="acPin('${s.id}',this.value)"></div>`).join('');
 return `<div class="card"><h2 style="margin-top:0">학생별 출결 번호</h2><p class="m">학원 입구 태블릿에서 학생이 누르는 번호예요. 전화번호를 적으면 <b>010 뒤의 앞 5자리</b>가 자동으로 들어가요 (예: 010-<b>12345</b>678). 직접 바꿔도 돼요.</p>
 ${dup?`<div class="hint">번호가 겹치는 학생이 있어요. 단말에서 이름을 골라 입력하게 되지만, 겹치지 않게 바꾸는 편이 편해요.</div>`:''}
 <div class="row" style="margin:6px 0"><button class="s sm" onclick="acFillPins()">전화번호로 빈 번호 채우기</button></div>
 <div class="axps"><div class="axp hd"><b>학생</b><span>전화번호</span><span>출결 번호</span></div>${rows||'<div class="empty">등록한 학생이 없어요.</div>'}</div></div>`}
async function acPatch(id,o){const s=AC.stu.find(x=>x.id===id);try{await acJ('/rest/v1/students?id=eq.'+id,{method:'PATCH',headers:{Prefer:'return=minimal'},body:JSON.stringify(o)});if(s)Object.assign(s,o);return true}catch(e){toast(acMissing(e)?'서버에 sql_20 을 먼저 실행해 주세요':'저장하지 못했어요');return false}}
async function acPhone(id,v){const o={phone:v.trim()||null};const s=AC.stu.find(x=>x.id===id);if(s&&!s.att_pin&&pinFrom(v).length>=4)o.att_pin=pinFrom(v);if(await acPatch(id,o)&&o.att_pin){AC.ld=1;attView()}}
async function acPin(id,v){const d=v.replace(/\D/g,'');if(await acPatch(id,{att_pin:d||null})){AC.ld=1;attView()}}
async function acFillPins(){let n=0;for(const s of AC.stu){if(!s.att_pin&&pinFrom(s.phone).length>=4){if(await acPatch(s.id,{att_pin:pinFrom(s.phone)}))n++}}toast(n+'명의 번호를 채웠어요');AC.ld=1;attView()}

/* ---------- 학부모 안내문 ---------- */
function acNoteHtml(){
 const cls=[...new Set(AC.stu.map(s=>String(s.grade||'').trim()).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'ko',{numeric:true}));
 const opts='<option value="">전체 학생</option>'+cls.map(g=>`<option value="c:${esc(g)}">반 전체 · ${esc(g)}</option>`).join('')+AC.stu.map(s=>`<option value="${s.id}">${esc(s.name)} ${esc(s.grade||'')}</option>`).join('');
 const ws=(typeof WSH!=='undefined'?WSH.slice().sort((a,b)=>b.t-a.t).slice(0,20):[]);
 const wo='<option value="">첨부 안 함</option>'+ws.map(w=>`<option value="${esc(w.id)}">${esc(w.title)} · ${esc(fmtNo(w.id))}</option>`).join('');
 const tag={all:'학생·학부모',parent:'학부모',student:'학생'};
 const list=AC.notes.map(n=>`<div class="axnl"><div><b>${esc(n.title)}</b><small>${new Date(n.t).toLocaleString('ko-KR')} · ${n.sid?esc(acStuName(n.sid)):'전체'} · ${tag[n.aud]||'학생'}</small><p>${esc(n.body).replace(/\n/g,'<br>')}</p></div><span class="axna"><button class="s sm" aria-label="다시 쓰기: ${esc(n.title)}" onclick="acNoteReuse('${n.src}',${n.id})">다시 쓰기</button><button class="s sm" aria-label="삭제: ${esc(n.title)}" onclick="acNoteDel('${n.src}',${n.id})">삭제</button></span></div>`).join('');
 return `<div class="card axform" oninput="acDraftSave()" onchange="acDraftSave()"><h2 style="margin-top:0">알림장 쓰기</h2><p class="m" style="margin:0 0 12px">오늘 수업 진도와 숙제를 적어 학생과 학부모에게 보내요. 학생은 알림(종)에서, 학부모는 「알림장」 탭에서 봐요.</p>
 <div class="g2"><div class="fld"><label for="ntTo">받는 사람</label><select id="ntTo">${opts}</select></div><div class="fld"><label for="ntAud">보낼 곳</label><select id="ntAud"><option value="all">학생 + 학부모</option><option value="parent">학부모만</option><option value="student">학생만</option></select></div></div>
 <div class="fld" style="margin-top:10px"><label for="ntP">오늘 진도</label><input id="ntP" maxlength="120" placeholder="예) 유형서 p.12~15 · 엔탈피와 열화학 반응식"></div>
 <div class="fld" style="margin-top:10px"><label for="ntH">숙제</label>${acTplChips('hw')}<textarea id="ntH" style="width:100%" rows="2" maxlength="300" placeholder="예) 유형서 p.16~17 풀어오기"></textarea></div>
 <div class="fld" style="margin-top:10px"><label for="ntW">숙제 학습지 붙이기 <small>학습지 이름과 번호가 함께 들어가요</small></label><select id="ntW">${wo}</select></div>
 <div class="fld" style="margin-top:10px"><label for="ntB">전달 사항</label>${acTplChips('msg')}<textarea id="ntB" style="width:100%" rows="2" maxlength="500" placeholder="예) 다음 주 수요일 쪽지시험이 있어요"></textarea></div>
 <div class="fld" style="margin-top:10px"><label for="ntT">제목 <small>비우면 「10월 23일 알림장」으로 보내요</small></label><input id="ntT" maxlength="60"></div>
 <div class="row" style="gap:8px;margin-top:8px;flex-wrap:wrap"><button class="s sm" onclick="acNoteLast()" ${AC.notes.length?'':'disabled'}>지난 알림장 불러오기</button><span class="m" id="acdraftst" style="margin-left:auto"></span></div>
 <button class="p axwide" onclick="acNoteSend()">알림장 보내기</button></div>
 <div class="card"><h2 style="margin-top:0">보낸 알림장 · 안내문</h2>${list||'<div class="empty">아직 보낸 글이 없어요.</div>'}</div>`}
const TPK={hw:'ntH',msg:'ntB'};
function acTplChips(k){const L=(AC.tpl&&AC.tpl[k])||[];return `<div class="axtpl" data-k="${k}">${L.map((t,i)=>`<span class="axchip"><button type="button" onclick="acTplUse('${k}',${i})" title="${esc(t)}">${esc(t.length>16?t.slice(0,16)+'…':t)}</button><button type="button" class="x" aria-label="양식 삭제" onclick="acTplDel('${k}',${i})">×</button></span>`).join('')}<button type="button" class="axchip add" onclick="acTplAdd('${k}')">+ 지금 내용을 양식으로 저장</button></div>`}
function acTplUse(k,i){const el=$('#'+TPK[k]);if(!el)return;const t=AC.tpl[k][i];el.value=el.value.trim()?el.value.trim()+'\n'+t:t;el.focus()}
async function acTplSave(){const d=(await tsRaw())||{};d.diaryTpl=AC.tpl;const r=await sb('/rest/v1/teacher_settings?on_conflict=user_id',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify({data:d,updated_at:new Date().toISOString()})});if(!r.ok)toast('양식을 저장하지 못했어요');return r.ok}
function acTplRefresh(k){document.querySelectorAll('.axtpl').forEach(b=>{if(b.dataset.k===k)b.outerHTML=acTplChips(k)})}
async function acTplAdd(k){const v=($('#'+TPK[k]).value||'').trim();if(!v){toast('먼저 칸에 양식으로 쓸 내용을 적어 주세요');return}
 if((AC.tpl[k]||[]).includes(v)){toast('이미 저장된 양식이에요');return}if((AC.tpl[k]||[]).length>=20){toast('양식은 20개까지 저장할 수 있어요');return}
 AC.tpl[k]=(AC.tpl[k]||[]).concat([v]);if(await acTplSave()){acTplRefresh(k);toast('양식으로 저장했어요')}}
async function acTplDel(k,i){AC.tpl[k].splice(i,1);await acTplSave();acTplRefresh(k)}
const ACDK='omr_diary_draft_v1';
function acDraftSave(){const g=id=>{const e=document.getElementById(id);return e?e.value:''};try{localStorage.setItem(ACDK,JSON.stringify({to:g('ntTo'),aud:g('ntAud'),p:g('ntP'),h:g('ntH'),b:g('ntB'),t:g('ntT'),w:g('ntW'),at:Date.now()}));const s=document.getElementById('acdraftst');if(s)s.textContent='초안을 저장했어요'}catch(e){}}
function acDraftLoad(){let d=null;try{d=JSON.parse(localStorage.getItem(ACDK)||'null')}catch(e){}if(!d)return;const set=(id,v)=>{const e=document.getElementById(id);if(e&&v!=null&&v!=='')e.value=v};
 set('ntTo',d.to);set('ntAud',d.aud);set('ntP',d.p);set('ntH',d.h);set('ntB',d.b);set('ntT',d.t);set('ntW',d.w);
 if(d.p||d.h||d.b){const s=document.getElementById('acdraftst');if(s)s.textContent='쓰던 초안을 불러왔어요'}}
function acDraftClear(){try{const t=document.getElementById('ntTo'),u=document.getElementById('ntAud');if(t||u)localStorage.setItem(ACDK,JSON.stringify({to:t?t.value:'',aud:u?u.value:''}));else localStorage.removeItem(ACDK)}catch(e){}}
function acNoteFill(n){const lines=String(n.body||'').split('\n'),g=k=>{const l=lines.find(x=>x.startsWith(k+':'));return l?l.slice(k.length+1).trim():''};
 const set=(id,v)=>{const e=document.getElementById(id);if(e)e.value=v};set('ntP',g('오늘 진도'));set('ntH',g('숙제'));set('ntB',g('전달 사항'));set('ntT','');
 const tg=n.aud,a=document.getElementById('ntAud');if(a&&['all','parent','student'].includes(tg))a.value=tg;acDraftSave();window.scrollTo({top:0,behavior:'smooth'});const e=document.getElementById('ntP');if(e)e.focus()}
function acNoteLast(){const n=AC.notes.find(x=>/오늘 진도:|숙제:|전달 사항:/.test(x.body||''))||AC.notes[0];if(n)acNoteFill(n)}
function acNoteReuse(src,id){const n=AC.notes.find(x=>x.src===src&&x.id===id);if(n)acNoteFill(n)}
let AC_SENDING=0;
async function acNoteSend(){
 if(AC_SENDING)return;
 const to=$('#ntTo').value,aud=$('#ntAud').value,pg=$('#ntP').value.trim(),hw=$('#ntH').value.trim(),etc=$('#ntB').value.trim(),wid=$('#ntW').value;let t=$('#ntT').value.trim();
 if(!pg&&!hw&&!etc){toast('진도, 숙제, 전달 사항 중 하나는 적어 주세요');return}
 const d=new Date(Date.now()+9*36e5);if(!t)t=(d.getUTCMonth()+1)+'월 '+d.getUTCDate()+'일 알림장';
 const w=wid?WSH.find(x=>x.id===wid):null;const L=[];
 if(pg)L.push('오늘 진도: '+pg);if(hw||w)L.push('숙제: '+[hw,w?'학습지 「'+w.title+'」 번호 '+fmtNo(w.id):''].filter(Boolean).join(' · '));if(etc)L.push('전달 사항: '+etc);
 const ids=to.startsWith('c:')?AC.stu.filter(s=>String(s.grade||'').trim()===to.slice(2)).map(s=>s.id):[to||null];
 if(!ids.length){toast('그 반에 학생이 없어요');return}
 const rows=ids.map(id=>({title:t,body:L.join('\n'),student_id:id,audience:aud}));
 AC_SENDING=1;const sb_=document.querySelector('.axform .axwide');if(sb_){sb_.disabled=true;sb_.textContent='보내는 중…'}
 try{await acJ('/rest/v1/notices',{method:'POST',headers:{Prefer:'return=minimal'},body:JSON.stringify(rows)});toast('알림장을 보냈어요'+(ids.length>1?' · '+ids.length+'명':''));acDraftClear();AC_SENDING=0;AC.ld=0;diaryView()}
 catch(e){if(e.status===400&&aud==='student'){try{await acJ('/rest/v1/notices',{method:'POST',headers:{Prefer:'return=minimal'},body:JSON.stringify(rows.map(r=>({title:r.title,body:r.body,student_id:r.student_id})))});toast('알림장을 보냈어요');acDraftClear();AC_SENDING=0;AC.ld=0;diaryView();return}catch(x){}}
  toast(e.status===400?'학부모에게 보내려면 서버 SQL(setup.sql)을 먼저 실행해 주세요':(!navigator.onLine||!e.status)?'인터넷 연결을 확인하고 다시 눌러 주세요. 적은 내용은 그대로예요':'보내지 못했어요. 잠시 뒤 다시 눌러 주세요. 적은 내용은 그대로예요');AC_SENDING=0;if(sb_){sb_.disabled=false;sb_.textContent='알림장 보내기'}}}
async function acNoteDel(src,id){if(!confirm('이 글을 삭제할까요? 학생·학부모 화면에서도 사라져요.'))return;try{await acJ('/rest/v1/'+(src==='p'?'parent_notices':'notices')+'?id=eq.'+id,{method:'DELETE'});AC.ld=0;diaryView()}catch(e){toast('삭제하지 못했어요')}}

/* ---------- 수납 ---------- */
function acFeeHtml(){
 const today=kstDay(),fs=AC.fees,paid=f=>f.paid_amount>=f.amount;
 const tot=fs.reduce((a,f)=>a+f.amount,0),got=fs.reduce((a,f)=>a+Math.min(f.paid_amount,f.amount),0),late=fs.filter(f=>!paid(f)&&f.due&&f.due<today).reduce((a,f)=>a+f.amount-f.paid_amount,0);
 const items=AC.pay.items||[];
 const rows=fs.filter(f=>!AC.q||(acStuName(f.student_id)+f.title).includes(AC.q)).map(f=>{const p=paid(f),od=!p&&f.due&&f.due<today;
  return `<div class="axf ${p?'ok':od?'od':''}"><div><b>${esc(acStuName(f.student_id))}</b><small>${esc(f.title)}${f.due?' · '+f.due.slice(5).replace('-','/')+'까지':''}</small></div><span class="axamt">${won(f.amount)}</span><span class="axst">${p?'납부 완료'+(f.method?' · '+esc(f.method):''):od?'연체':'미납'}</span><span class="axab">${p?`<button class="s sm" onclick="acFeeUndo(${f.id})">취소</button>`:`<button class="p sm" onclick="acFeePay(${f.id})">납부 처리</button>`}<button class="s sm" onclick="acFeeDel(${f.id})">삭제</button></span></div>`}).join('');
 const sel=AC.stu.map(s=>`<label class="chk"><input type="checkbox" value="${s.id}" class="acfs">${esc(s.name)}<small>${esc(s.grade||'')}</small></label>`).join('');
 return `<div class="card"><div class="axsum big"><span style="--c:#2a72bf"><b>${won(tot)}</b>총 청구</span><span style="--c:#1f9d55"><b>${won(got)}</b>수납</span><span style="--c:#d9534f"><b>${won(Math.max(0,tot-got))}</b>미수${late?` (연체 ${won(late)})`:''}</span></div>${fs.some(f=>!paid(f))?`<div class="row" style="margin-top:12px;gap:8px;flex-wrap:wrap"><button class="s sm" onclick="acFeeRemind(false)">미납 학부모에게 안내 보내기</button>${late?`<button class="s sm" onclick="acFeeRemind(true)">연체만 보내기</button>`:''}</div>`:''}</div>
 <div class="card"><h2 style="margin-top:0">청구 만들기</h2>
 <div class="g2"><div class="fld"><label>항목</label><select id="fiSel" onchange="acFiPick(this.value)"><option value="">직접 입력</option>${items.map((it,i)=>`<option value="${i}">${esc(it.name)} · ${won(it.amount)}</option>`).join('')}</select></div><div class="fld"><label>이름</label><input id="fiT" placeholder="예) 10월 수강료" maxlength="40"></div><div class="fld"><label>금액(원)</label><input id="fiA" type="number" min="0" step="1000" placeholder="300000"></div><div class="fld"><label>납부 기한</label><input id="fiD" type="date"></div></div>
 <div class="row" style="margin:8px 0 4px"><b>대상 학생</b><button class="s sm" onclick="document.querySelectorAll('.acfs').forEach(c=>c.checked=true)">전체 선택</button><button class="s sm" onclick="document.querySelectorAll('.acfs').forEach(c=>c.checked=false)">해제</button></div><div class="axchk">${sel||'<span class="m">등록한 학생이 없어요</span>'}</div>
 <button class="p" style="margin-top:10px" onclick="acFeeAdd()">청구하기</button>${items.length?'':'<p class="tsn2">자주 쓰는 학원비·교재비는 「요금·결제 설정」에서 미리 등록해 두면 고르기만 하면 돼요.</p>'}</div>
 <div class="card"><div class="row"><h2 style="margin:0">청구 내역</h2><input type="search" placeholder="이름·항목 검색" value="${esc(AC.q)}" oninput="AC.q=this.value;clearTimeout(window._acq);window._acq=setTimeout(attView,200)" style="margin-left:auto;width:190px"></div>${rows||'<div class="empty">청구 내역이 없어요.</div>'}</div>`}
function acFiPick(i){const it=(AC.pay.items||[])[+i];if(!it)return;$('#fiT').value=it.name;$('#fiA').value=it.amount}
async function acFeeRemind(onlyLate){
 const today=kstDay(),by={};
 AC.fees.filter(f=>f.paid_amount<f.amount&&(!onlyLate||(f.due&&f.due<today))).forEach(f=>{(by[f.student_id]=by[f.student_id]||[]).push(f)});
 const ids=Object.keys(by);if(!ids.length){toast('보낼 대상이 없어요');return}
 const total=ids.reduce((a,id)=>a+by[id].length,0);
 if(!confirm((onlyLate?'연체된':'아직 납부하지 않은')+' 청구 '+total+'건, 학생 '+ids.length+'명의 학부모에게 납부 안내를 보낼까요?\n(학생 화면에는 보이지 않아요)'))return;
 const rows=ids.map(id=>({student_id:id,audience:'parent',title:'납부 안내',body:by[id].map(f=>f.title+' '+won(f.amount-f.paid_amount)+(f.due?' (기한 '+f.due.slice(5).replace('-','/')+')':'')).join('\n')+'\n납부 방법은 「납부」 탭에서 확인할 수 있어요.'}));
 try{await acJ('/rest/v1/notices',{method:'POST',headers:{Prefer:'return=minimal'},body:JSON.stringify(rows)});toast('납부 안내를 보냈어요 · '+ids.length+'명')}
 catch(e){toast(e.status===400?'서버 SQL(setup.sql)을 먼저 실행해 주세요':'보내지 못했어요. 연결을 확인해 주세요')}}
async function acFeeAdd(){const title=$('#fiT').value.trim(),amount=Math.round(+$('#fiA').value||0),due=$('#fiD').value||null,ids=[...document.querySelectorAll('.acfs:checked')].map(c=>c.value);
 if(!title||!amount||!ids.length){toast('이름·금액·대상 학생을 확인해 주세요');return}
 const it=(AC.pay.items||[]).find(x=>x.name===title);const kind=it&&it.kind||'tuition';
 try{await acJ('/rest/v1/fees',{method:'POST',headers:{Prefer:'return=minimal'},body:JSON.stringify(ids.map(id=>({student_id:id,title,amount,due,kind})))});toast(ids.length+'명에게 청구했어요');AC.ld=0;attView()}catch(e){toast(acMissing(e)?'서버에 sql_20 을 먼저 실행해 주세요':'청구하지 못했어요')}}
async function acFeePay(id){const f=AC.fees.find(x=>x.id===id);if(!f)return;const m=prompt('납부 방법 (현금 · 계좌이체 · 카드)','계좌이체');if(m===null)return;
 try{await acJ('/rest/v1/fees?id=eq.'+id,{method:'PATCH',headers:{Prefer:'return=minimal'},body:JSON.stringify({paid_amount:f.amount,paid_at:new Date().toISOString(),method:m.trim()||'직접 확인'})});AC.ld=0;attView()}catch(e){toast('처리하지 못했어요')}}
async function acFeeUndo(id){if(!confirm('납부 완료를 취소할까요?'))return;try{await acJ('/rest/v1/fees?id=eq.'+id,{method:'PATCH',headers:{Prefer:'return=minimal'},body:JSON.stringify({paid_amount:0,paid_at:null,method:null,pay_key:null})});AC.ld=0;attView()}catch(e){toast('취소하지 못했어요')}}
async function acFeeDel(id){if(!confirm('이 청구를 삭제할까요?'))return;try{await acJ('/rest/v1/fees?id=eq.'+id,{method:'DELETE'});AC.ld=0;attView()}catch(e){toast('삭제하지 못했어요')}}

/* ---------- 요금표 · 결제 설정 ---------- */
function acRateHtml(){
 const P=AC.pay,items=(P.items||[]).map((it,i)=>`<div class="axit"><input value="${esc(it.name)}" placeholder="이름" onchange="acItem(${i},'name',this.value)"><input type="number" min="0" step="1000" value="${it.amount}" onchange="acItem(${i},'amount',this.value)"><select onchange="acItem(${i},'kind',this.value)"><option value="tuition" ${it.kind!=='book'?'selected':''}>학원비</option><option value="book" ${it.kind==='book'?'selected':''}>교재비</option></select><button class="s sm" onclick="acItemDel(${i})">삭제</button></div>`).join('');
 return `<div class="card"><h2 style="margin-top:0">요금표</h2><p class="m">자주 쓰는 학원비·교재비를 등록해 두면 「수납」에서 고르기만 하면 돼요.</p>${items||'<div class="empty">등록한 항목이 없어요.</div>'}<div class="row" style="margin-top:8px"><button class="s" onclick="acItemAdd()">항목 추가</button></div></div>
 <div class="card"><h2 style="margin-top:0">계좌 이체 안내</h2><p class="m">학부모 앱의 「납부」 화면에 그대로 보여요. 입금을 확인하면 「수납」에서 납부 처리를 눌러 주세요.</p><div class="fld" style="max-width:460px"><input value="${esc(P.bank||'')}" placeholder="예) 국민 000-00-000000 홍길동" maxlength="80" onchange="acPaySet('bank',this.value.trim())"></div>
 <label class="swr" style="margin-top:12px"><span><b>결제 완료 자동 처리 (시연용)</b><small>카드 결제가 끝나면 서버 승인 없이도 납부 완료로 바꿔요. 실제 결제를 받을 땐 꺼 주세요.</small></span><input class="swi" type="checkbox" ${P.demo?'checked':''} onchange="acPaySet('demo',this.checked)"></label></div>`}
async function acPaySave(){const d=(await tsRaw())||{};d.pay=AC.pay;const r=await sb('/rest/v1/teacher_settings?on_conflict=user_id',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify({data:d,updated_at:new Date().toISOString()})});if(!r.ok)toast('저장하지 못했어요');else toast('저장했어요')}
function acPaySet(k,v){AC.pay[k]=v;acPaySave()}
function acItem(i,k,v){const it=AC.pay.items[i];if(!it)return;it[k]=k==='amount'?Math.max(0,Math.round(+v||0)):v;acPaySave()}
function acItemAdd(){AC.pay.items=(AC.pay.items||[]).concat([{name:'',amount:0,kind:'tuition'}]);attView()}
function acItemDel(i){AC.pay.items.splice(i,1);acPaySave();attView()}

/* ---------- 출결 단말(키오스크) ----------
   학원 입구 태블릿(가로)용: 왼쪽 남색 면에 학원 이름 · 큰 시계 · 안내, 오른쪽에 번호 칸과 큰 숫자판.
   기록되면 화면 전체에 인사(등원 초록 · 하원 남색)가 3초 동안 뜨고, 틀린 번호는 번호 칸이 흔들리며 아래에 이유가 나온다. 세로 화면은 위아래로 쌓는다 */
const KLK='omr_kiosk';
const KIOCSS=`#kiosk{--kn:#0d387e;--ky:#fdc62d;--kg:#15804c;--kt:#14213d;--km:#5b6678;--kl:#dde3ec;position:fixed;inset:0;z-index:99990;display:grid;grid-template-columns:minmax(0,44fr) minmax(0,56fr);background:#f3f5f9;color:var(--kt);font-family:Pretendard,PretendardLocal,sans-serif;user-select:none;-webkit-user-select:none;touch-action:manipulation;font-variant-numeric:tabular-nums;word-break:keep-all}
#kiosk .kl{background:var(--kn);color:#fff;display:flex;flex-direction:column;justify-content:space-between;padding:clamp(28px,5vh,56px) clamp(28px,4.4vw,64px);min-width:0}
#kiosk .kbr{display:flex;align-items:center;gap:14px;min-height:48px}#kiosk .kbr svg{height:58px;width:auto}#kiosk .kbr img{max-height:48px;max-width:70%;object-fit:contain}#kiosk .kbr b{font-size:clamp(20px,2.2vw,26px);font-weight:700;letter-spacing:-.02em}
#kiosk .ktm{font-size:clamp(76px,10.5vw,148px);font-weight:700;line-height:1;letter-spacing:-.04em}#kiosk .kdt{margin-top:14px;font-size:clamp(17px,1.8vw,22px);color:#c9d6ee;font-weight:500}
#kiosk .kgd h1{margin:0;font-size:clamp(24px,2.7vw,34px);font-weight:700;letter-spacing:-.03em;line-height:1.25}#kiosk .kgd p{margin:12px 0 0;font-size:clamp(15px,1.5vw,18px);line-height:1.6;color:#c9d6ee}#kiosk .kgd p b{color:var(--ky);font-weight:700}
#kiosk .klb{margin:0 0 -8px;font-size:clamp(15px,1.4vw,17px);font-weight:600;color:var(--km)}#kiosk .kr{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:clamp(18px,3vh,28px);padding:clamp(24px,4vh,48px);min-width:0}
#kiosk .kdg{display:flex;gap:12px}#kiosk .kdg i{width:clamp(48px,5.2vw,60px);height:clamp(60px,8vh,72px);border-radius:14px;background:#fff;border:1.5px solid var(--kl);display:grid;place-items:center;transition:border-color .15s,background .15s}
#kiosk .kdg i.f:after{content:"";width:16px;height:16px;border-radius:50%;background:var(--kn)}#kiosk .kdg i.c{border-color:var(--kn);box-shadow:0 0 0 3px #0d387e1f}
#kiosk .kdg.sh{animation:ksh .42s cubic-bezier(.36,.07,.19,.97)}@keyframes ksh{20%,60%{transform:translateX(-9px)}40%,80%{transform:translateX(9px)}}
#kiosk .kms{min-height:48px;text-align:center;font-size:clamp(16px,1.6vw,19px);font-weight:600;color:#c2362f;line-height:1.4}#kiosk .kms small{display:block;font-size:.85em;font-weight:500;color:var(--km)}
#kiosk .kp{display:grid;grid-template-columns:repeat(3,clamp(88px,10.5vw,124px));gap:clamp(10px,1.4vw,14px)}
#kiosk .kp button{height:clamp(72px,10.4vh,92px);border-radius:18px;border:1.5px solid var(--kl);background:#fff;color:var(--kt);font:inherit;font-size:clamp(28px,3vw,36px);font-weight:600;cursor:pointer;transition:transform .08s,background .12s,border-color .12s;display:grid;place-items:center}
#kiosk .kp button:active{transform:scale(.96);background:#e8eef7}#kiosk .kp button svg{width:34px;height:34px}
#kiosk .kp .go{background:var(--kn);border-color:var(--kn);color:#fff;font-size:clamp(20px,2vw,24px);font-weight:700}#kiosk .kp .go:active{background:#0a2c64}#kiosk .kp .go:disabled{background:#c9d2df;border-color:#c9d2df;cursor:default}
#kiosk .khi{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:clamp(14px,2.4vh,22px);text-align:center;color:#fff;background:var(--kg);padding:32px;z-index:2}
#kiosk .khi.on{display:flex;animation:khi .26s cubic-bezier(.2,.8,.2,1)}@keyframes khi{from{opacity:0;transform:scale(.985)}}
#kiosk .khi.out{background:var(--kn)}#kiosk .khi.dup{background:#3d4a5e}#kiosk .khi.who{background:#f3f5f9;color:var(--kt)}
#kiosk .khi .ck{width:clamp(84px,11vh,112px);height:clamp(84px,11vh,112px);border-radius:50%;background:#ffffff26;display:grid;place-items:center}#kiosk .khi .ck svg{width:56%;height:56%}
#kiosk .khi h2{margin:0;font-size:clamp(40px,6vw,76px);font-weight:800;letter-spacing:-.035em;line-height:1.1}#kiosk .khi p{margin:0;font-size:clamp(20px,2.4vw,30px);font-weight:600;opacity:.92}
#kiosk .khi .tm{display:inline-flex;align-items:center;gap:10px;padding:10px 22px;border-radius:999px;background:#ffffff26;font-size:clamp(18px,2vw,24px);font-weight:700}
#kiosk .kch{display:flex;gap:14px;flex-wrap:wrap;justify-content:center;max-width:760px}#kiosk .kch button{min-width:180px;padding:22px 28px;border-radius:18px;border:1.5px solid var(--kl);background:#fff;font:inherit;font-size:26px;font-weight:700;color:var(--kt);cursor:pointer}#kiosk .kch button small{display:block;margin-top:4px;font-size:15px;font-weight:500;color:var(--km)}#kiosk .kch button:active{background:#e8eef7}
#kiosk .kx{position:absolute;right:0;top:0;width:72px;height:72px;background:none;border:0;opacity:0;z-index:3}
@media(max-aspect-ratio:1/1){#kiosk{grid-template-columns:1fr;grid-template-rows:auto 1fr}#kiosk .kl{flex-direction:row;flex-wrap:wrap;align-items:flex-end;gap:12px 28px}#kiosk .kbr{flex-basis:100%}#kiosk .ktm{font-size:clamp(56px,13vw,96px)}#kiosk .kgd{flex:1 1 260px}#kiosk .kgd h1{font-size:clamp(20px,4.4vw,28px)}}
@media(prefers-reduced-motion:reduce){#kiosk .kdg.sh,#kiosk .khi.on{animation:none}}`;
const KIOIC={ok:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',del:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5h10a2 2 0 012 2v10a2 2 0 01-2 2H9l-6-7z"/><path d="M12.5 9.5l5 5M17.5 9.5l-5 5"/></svg>'};
function kioskBrand(){try{const c=acCfg(),u=c.logoDark||c.logo;if(c.mode==='logo'&&u)return `<img src="${u}" alt="${esc(c.name||'학원 로고')}">`;if(c.mode==='text'&&c.name)return `<b>${esc(c.name)}</b>`}catch(e){}return lgStack('#fff')}
function kioskOpen(){
 if(needCloud()){toast('온라인 저장에 로그인해야 해요');return}
 if(!localStorage.getItem(KLK+'_pw')){const p=prompt('단말을 닫을 때 쓸 해제 번호를 정해 주세요 (숫자 4자리 이상)','');if(!p||!/^\d{4,}$/.test(p)){toast('숫자 4자리 이상으로 정해 주세요');return}localStorage.setItem(KLK+'_pw',p)}
 try{localStorage.setItem(KLK,'1')}catch(e){}
 let k=document.getElementById('kiosk');if(k)k.remove();
 k=document.createElement('div');k.id='kiosk';k.innerHTML=`<style>${KIOCSS}</style>
<button class="kx" aria-label="해제" onclick="kioskTap()"></button>
<section class="kl"><div class="kbr">${kioskBrand()}</div><div><div class="ktm" id="ktm"></div><div class="kdt" id="kclk"></div></div><div class="kgd"><h1>출결 번호를 누르면<br>등원 · 하원이 기록돼요</h1><p>전화번호가 010-<b>12345</b>678 이면 <b>12345</b>를 누르세요. 같은 날 한 번 더 누르면 하원이에요.</p></div></section>
<section class="kr"><p class="klb">출결 번호</p><div class="kdg" id="kdg" aria-live="polite"></div><div class="kms" id="kms" role="status"></div>
<div class="kp">${[1,2,3,4,5,6,7,8,9].map(n=>`<button onclick="kioskKey('${n}')">${n}</button>`).join('')}<button onclick="kioskKey('c')" aria-label="지우기">${KIOIC.del}</button><button onclick="kioskKey('0')">0</button><button class="go" id="kgo" onclick="kioskGo()">확인</button></div></section>
<div class="khi" id="khi" onclick="kioskHiEnd()"></div>`;
 document.body.appendChild(k);KIO.pin='';KIO.n=0;kioskDraw();clearInterval(KIO.ck);KIO.ck=setInterval(kioskClock,15000);kioskClock();
 try{(document.documentElement.requestFullscreen||function(){}).call(document.documentElement)}catch(e){}
 document.addEventListener('keydown',kioskKd)}
const KIO={pin:'',n:0,ck:0,rt:0,busy:0};
function kioskClock(){const d=new Date(),o={timeZone:'Asia/Seoul'},t=document.getElementById('ktm'),e=document.getElementById('kclk');
 if(t)t.textContent=d.toLocaleTimeString('ko-KR',{...o,hour:'2-digit',minute:'2-digit',hour12:false});if(e)e.textContent=d.toLocaleDateString('ko-KR',{...o,month:'long',day:'numeric',weekday:'long'})}
function kioskDraw(){const e=document.getElementById('kdg');if(!e)return;const n=Math.max(5,KIO.pin.length);e.innerHTML=Array.from({length:n},(_,i)=>`<i class="${KIO.pin[i]?'f':i===KIO.pin.length?'c':''}"></i>`).join('');e.setAttribute('aria-label','입력한 숫자 '+KIO.pin.length+'개');const g=document.getElementById('kgo');if(g)g.disabled=KIO.pin.length<3}
function kioskKd(e){if(!document.getElementById('kiosk'))return;if(/^\d$/.test(e.key))kioskKey(e.key);else if(e.key==='Backspace')kioskKey('c');else if(e.key==='Enter')kioskGo();else if(e.key==='Escape')kioskHiEnd()}
function kioskKey(k){if(KIO.busy)return;if(KIO.rt)kioskHiEnd();if(k==='c')KIO.pin=KIO.pin.slice(0,-1);else if(KIO.pin.length<8)KIO.pin+=k;kioskDraw();kioskMsg('');if(KIO.pin.length>=5&&!KIO.auto){clearTimeout(KIO.at);KIO.at=setTimeout(()=>{if(KIO.pin.length>=5)kioskGo()},900)}}
// 번호 칸 아래 안내(틀린 번호 · 연결 실패). 틀리면 번호 칸이 흔들린다
function kioskMsg(t,sub,shake){const m=document.getElementById('kms');if(m)m.innerHTML=t?esc(t)+(sub?'<small>'+esc(sub)+'</small>':''):'';if(shake){const d=document.getElementById('kdg');if(d){d.classList.remove('sh');void d.offsetWidth;d.classList.add('sh')}}}
// 기록되면 화면 전체 인사: kind = in(등원) · out(하원) · dup(이미 기록)
function kioskHi(kind,name,t){const h=document.getElementById('khi');if(!h)return;
 const msg={in:['어서 와요!',t+' 등원'],out:['잘 가요!',t+' 하원'],dup:['이미 기록됐어요','잠시 뒤 다시 눌러 주세요']}[kind]||['','']; 
 h.className='khi on '+kind;h.innerHTML=`<div class="ck">${KIOIC.ok}</div><h2>${esc(name)} 학생</h2><p>${msg[0]}</p>${kind==='dup'?`<p style="font-size:.7em;font-weight:500">${msg[1]}</p>`:`<span class="tm">${esc(msg[1])}</span>`}`;
 clearTimeout(KIO.rt);KIO.rt=setTimeout(kioskHiEnd,3200)}
function kioskHiEnd(){clearTimeout(KIO.rt);KIO.rt=0;const h=document.getElementById('khi');if(h){h.className='khi';h.innerHTML=''}}
async function kioskGo(sid){clearTimeout(KIO.at);if(KIO.busy||KIO.pin.length<3)return;KIO.busy=1;const pin=KIO.pin;
 try{const r=await rpc('att_checkin',{p_pin:pin,p_student:sid||null});const j=r.ok?await r.json():null;
  if(!j){kioskHiEnd();kioskMsg('연결에 실패했어요','잠시 뒤 다시 눌러 주세요',1)}
  else if(j.ok){KIO.pin='';kioskDraw();kioskMsg('');kioskHi(j.kind==='in'||j.kind==='out'?j.kind:'dup',j.name,kstTime(j.t))}
  else if(j.err==='choose'){const h=document.getElementById('khi');h.className='khi on who';h.onclick=null;h.innerHTML='<h2 style="font-size:clamp(32px,4vw,48px)">누구세요?</h2><p style="color:#5b6678;font-size:20px;font-weight:500">같은 번호를 쓰는 학생이 있어요. 이름을 눌러 주세요.</p><div class="kch">'+j.choose.map(c=>`<button onclick="event.stopPropagation();kioskPick('${c.id}')">${esc(c.name)}${c.grade?'<small>'+esc(c.grade)+'</small>':''}</button>`).join('')+'</div>';clearTimeout(KIO.rt);KIO.rt=setTimeout(()=>{const x=document.getElementById('khi');if(x)x.onclick=kioskHiEnd;KIO.pin='';kioskDraw();kioskHiEnd()},20000)}
  else{KIO.pin='';kioskDraw();kioskMsg('번호를 찾을 수 없어요','선생님께 출결 번호를 물어보세요',1)}
 }catch(e){kioskMsg('연결에 실패했어요','잠시 뒤 다시 눌러 주세요',1)}
 KIO.busy=0}
function kioskPick(id){const h=document.getElementById('khi');if(h)h.onclick=kioskHiEnd;kioskGo(id)}
let _kt=0,_ktm=0;
function kioskTap(){_kt++;clearTimeout(_ktm);_ktm=setTimeout(()=>_kt=0,2500);if(_kt>=5){_kt=0;const p=prompt('해제 번호');if(p===localStorage.getItem(KLK+'_pw'))kioskClose();else if(p!==null)toast('번호가 달라요')}}
function kioskClose(){try{localStorage.removeItem(KLK)}catch(e){}clearInterval(KIO.ck);document.removeEventListener('keydown',kioskKd);const k=document.getElementById('kiosk');if(k)k.remove();try{if(document.fullscreenElement)document.exitFullscreen()}catch(e){}}

/* ---------- 학부모 화면: 출결 달력 · 안내문 · 납부 ---------- */
const PA={sec:'att',mon:'',recs:[],notes:[],fees:[],pay:{},ld:0,err:''};
async function pAttView(){
 const m=$('#main');if(!STUD||!STUD.parent){m.innerHTML='';return}
 if(!PA.mon)PA.mon=kstDay().slice(0,7);
 try{if(localStorage.getItem('omr_tosspend'))await tossReturn()}catch(e){}
 if(!PA.ld||Date.now()-(PA.t||0)>15000){if(!PA.ld)m.innerHTML='<div class="card">'+ldg('불러오는 중…')+'</div>';await paLoad()}
 clearTimeout(PA.pt);PA.pt=setTimeout(()=>{if(tab==='patt'&&STUD&&STUD.parent){PA.t=0;pAttView()}},60000)
 const S=[['att','출결'],['note','알림장'],['fee','납부']];
 const seg=`<div class="bkseg axseg" role="tablist">${S.map(([k,l])=>`<button role="tab" class="${PA.sec===k?'on':''}" onclick="PA.sec='${k}';pAttView()">${l}${k==='fee'&&PA.fees.some(f=>f.paid_amount<f.amount)?' <i class="axdot"></i>':''}</button>`).join('')}</div>`;
 let b='';
 if(PA.err)b=`<div class="card"><div class="hint">${esc(PA.err)}</div><button class="s sm" style="margin-top:10px" onclick="PA.ld=0;pAttView()">다시 불러오기</button></div>`;
 else if(PA.sec==='att')b=`<div class="card"><div class="row" style="gap:8px"><button class="s sm" onclick="PA.mon=ymAdd(PA.mon,-1);PA.ld=0;pAttView()">‹</button><b style="flex:1;text-align:center">${PA.mon.replace('-','년 ')}월 출결</b><button class="s sm" onclick="PA.mon=ymAdd(PA.mon,1);PA.ld=0;pAttView()">›</button>${PA.mon!==kstDay().slice(0,7)?`<button class="s sm" onclick="PA.mon=kstDay().slice(0,7);PA.ld=0;pAttView()">이번 달</button>`:''}</div>${acCal(PA.recs,PA.mon)}</div>`;
 else if(PA.sec==='note')b=`<div class="card">${PA.notes.length?PA.notes.map(n=>`<div class="axnl"><div><b>${esc(n.title)}</b><small>${new Date(n.t).toLocaleString('ko-KR')}</small><p>${esc(n.body).replace(/\n/g,'<br>')}</p></div></div>`).join(''):'<div class="empty">받은 안내문이 없어요.</div>'}</div>`;
 else b=paFeeHtml();
 m.innerHTML=`<div class="tsh"><div><h1>${esc((STINFO&&STINFO.name)||'자녀')} 학생</h1><p>출결과 알림장, 납부 내역을 확인해요.</p></div></div>${seg}${b}`}
async function paLoad(){PA.err='';const a={p_login:STUD.login,p_pw:STUD.pw};
 if(STUD.preview){try{const[y,mo]=PA.mon.split('-').map(Number),to=PA.mon+'-'+String(new Date(Date.UTC(y,mo,0)).getUTCDate()).padStart(2,'0'),id=STUD.sid;
  const[rc,nt,pn,fe]=await Promise.all([acJ('/rest/v1/attendance?select=*&student_id=eq.'+id+'&day=gte.'+PA.mon+'-01&day=lte.'+to),acJ('/rest/v1/notices?select=*&order=t.desc&limit=60'),acJ('/rest/v1/parent_notices?select=*&order=created_at.desc&limit=30').catch(()=>[]),acJ('/rest/v1/fees?select=*&student_id=eq.'+id+'&order=created_at.desc&limit=100').catch(()=>[])]);
  PA.recs=rc||[];PA.notes=[...(nt||[]).filter(n=>(!n.student_id||n.student_id===id)&&['parent','all'].includes(n.audience||'student')).map(n=>({id:n.id,title:n.title,body:n.body,t:+n.t})),...(pn||[]).filter(n=>!n.student_id||n.student_id===id).map(n=>({id:-n.id,title:n.title,body:n.body,t:new Date(n.created_at).getTime()}))].sort((x,y)=>y.t-x.t);
  PA.fees=fe||[];PA.pay=((await tsRaw())||{}).pay||{};PA.pay.clientKey=PA.pay.clientKey||TOSS_KEY}catch(e){PA.err='미리보기를 불러오지 못했어요.'}PA.ld=1;PA.t=Date.now();return}
 try{const[y,mo]=PA.mon.split('-').map(Number);const to=PA.mon+'-'+String(new Date(Date.UTC(y,mo,0)).getUTCDate()).padStart(2,'0');
  const rs=await Promise.all([rpc('pa_attendance',{...a,p_from:PA.mon+'-01',p_to:to}),rpc('pa_notices',a),rpc('pa_fees',a)]);
  const bad=rs.find(r=>!r.ok);
  if(bad){let m='';try{m=(await bad.text()).slice(0,160)}catch(e){}console.warn('parent rpc',bad.status,m);
   PA.err=bad.status===404?'학원에서 아직 출결·안내문 기능을 켜지 않았어요. (서버 준비가 필요해요)':'불러오지 못했어요 (오류 '+bad.status+'). 선생님께 알려 주세요.'+(m?' · '+m:'');PA.ld=1;PA.t=Date.now();return}
  const [r1,r2,r3]=await Promise.all(rs.map(r=>r.json()));
  if(r1===null&&r2===null&&r3===null){PA.err='로그인 정보를 확인하지 못했어요. 다시 로그인해 주세요.';PA.ld=1;PA.t=Date.now();return}
  PA.recs=r1||[];PA.notes=r2||[];PA.fees=(r3&&r3.fees)||[];PA.pay=(r3&&r3.pay)||{};PA.pay.clientKey=PA.pay.clientKey||TOSS_KEY
 }catch(e){PA.err='불러오지 못했어요. 연결을 확인해 주세요.'}
 PA.ld=1;PA.t=Date.now()}
function paFeeHtml(){
 if(!PA.fees.length)return '<div class="card"><div class="empty">청구된 내역이 없어요.</div></div>';
 const today=kstDay(),P=PA.pay||{};
 const rows=PA.fees.map(f=>{const p=f.paid_amount>=f.amount,od=!p&&f.due&&f.due<today;
  return `<div class="axf ${p?'ok':od?'od':''}"><div><b>${esc(f.title)}</b><small>${f.due?f.due.slice(5).replace('-','/')+'까지':''}${p&&f.paid_at?' · '+new Date(f.paid_at).toLocaleDateString('ko-KR')+' 납부':''}</small></div><span class="axamt">${won(f.amount)}</span><span class="axst">${p?'납부 완료':od?'연체':'미납'}</span><span class="axab">${p?'':`<button class="p axwide" onclick="paPay(${f.id})">납부하기</button>`}</span></div>`}).join('');
 return `<div class="card">${rows}<div id="axpay"></div></div>`}

function paPay(id){const f=PA.fees.find(x=>x.id===id),P=PA.pay||{},e=document.getElementById('axpay');if(!f||!e)return;
 if(STUD&&STUD.preview){e.innerHTML='<div class="hint" style="margin-top:10px">선생님 화면의 미리보기에서는 결제할 수 없어요. 결제는 학부모 계정(아이디·비밀번호)으로 접속해서 해 주세요.</div>';return}
 e.innerHTML=`<div class="hint" style="margin-top:10px"><b>${esc(f.title)} · ${won(f.amount)}</b><button class="p axwide" onclick="paToss(${f.id})">카드로 결제하기</button>${P.bank?`<b>계좌 이체</b><br><span style="font-size:16px;font-weight:700;color:var(--t);letter-spacing:.01em">${esc(P.bank)}</span><div style="margin-top:8px"><button class="s axwide" onclick="paCopy()">계좌 복사</button></div><small style="display:block;margin-top:6px">입금하시면 선생님이 확인한 뒤 납부 완료로 바꿔 드려요.</small>`:'아직 계좌 안내가 등록되지 않았어요. 학원에 문의해 주세요.'}</div>`;
 e.scrollIntoView({behavior:'smooth',block:'nearest'})}
function paCopy(){const b=(PA.pay||{}).bank||'';try{navigator.clipboard.writeText(b).then(()=>toast('계좌를 복사했어요'),()=>toast('복사하지 못했어요'))}catch(e){toast('복사하지 못했어요')}}

let PA_PAYING=0;
async function paToss(id){const f=PA.fees.find(x=>x.id===id);if(!f||PA_PAYING)return;PA_PAYING=1;setTimeout(()=>{PA_PAYING=0},8000);
 try{if(!window.TossPayments){await new Promise((ok,no)=>{const s=document.createElement('script');s.src='https://js.tosspayments.com/v2/standard';s.onload=ok;s.onerror=no;document.head.appendChild(s)})}
  const tp=window.TossPayments(PA.pay.clientKey||TOSS_KEY),pay=tp.payment({customerKey:'solvi-'+String(STUD.login).replace(/[^A-Za-z0-9_-]/g,'').slice(0,40).padEnd(2,'x')});
  const base=location.origin+location.pathname;
  try{localStorage.setItem('omr_tosspend',JSON.stringify({f:f.id,t:f.title,w:f.amount}))}catch(x){}
  const res=await pay.requestPayment({method:'CARD',amount:{currency:'KRW',value:f.amount},orderId:'solvi-'+f.id+'-'+Date.now().toString(36),orderName:f.title,successUrl:base+'?tosspay='+f.id,failUrl:base+'?tosspay=fail',customerName:(STINFO&&STINFO.name)||undefined});
  /* PC 결제창은 페이지를 옮기지 않고 결과만 돌려주기도 해요 */
  PA_PAYING=0;if(res&&res.paymentKey)await tossConfirm({k:res.paymentKey,o:res.orderId,a:res.amount&&res.amount.value!=null?res.amount.value:f.amount,f:f.id})
 }catch(e){PA_PAYING=0;try{localStorage.removeItem('omr_tosspend')}catch(x){}if(e&&e.code==='USER_CANCEL')return;payDone(false,'결제하지 못했어요',(e&&e.message)||'결제창을 열지 못했어요. 잠시 뒤 다시 시도해 주세요.')}}
function payDone(ok,title,sub){const o=document.getElementById('paydone');if(o)o.remove();const d=document.createElement('div');d.id='paydone';d.className='paok'+(ok?'':' bad');d.setAttribute('role','alertdialog');d.setAttribute('aria-modal','true');d.setAttribute('aria-label',title);const prev=document.activeElement;const close=()=>{d.remove();document.removeEventListener('keydown',kd,true);try{prev&&prev.focus&&prev.focus()}catch(e){}};const kd=e=>{if(e.key==='Escape'||e.key==='Enter'){e.preventDefault();close()}};
 d.innerHTML='<div class="pdc"><svg class="pdi" viewBox="0 0 84 84" aria-hidden="true"><circle cx="42" cy="42" r="42"/>'+(ok?'<path d="M25 43l12 12 23-25"/>':'<path d="M28 28l28 28M56 28L28 56"/>')+'</svg><h2>'+esc(title)+'</h2><p>'+esc(sub||'')+'</p><button class="p axwide" id="paydoneok">확인</button></div>';document.body.appendChild(d);d.querySelector('#paydoneok').onclick=close;d.addEventListener('click',e=>{if(e.target===d)close()});document.addEventListener('keydown',kd,true);d.querySelector('#paydoneok').focus();try{navigator.vibrate&&navigator.vibrate(ok?[30,40,30]:80)}catch(e){}}
/* 결제창에서 돌아오면: 서버 승인 함수(toss-confirm)가 있으면 그걸로, 없으면 「테스트 결제 완료 처리」가 켜져 있을 때만 납부 완료로 바꿔요 */
async function tossReturn(){
 let p=null;try{p=JSON.parse(localStorage.getItem('omr_tosspend')||'null')}catch(e){}
 const q=new URLSearchParams(location.search);
 if(q.get('paymentKey')){p={...(p||{}),k:q.get('paymentKey'),o:q.get('orderId'),a:q.get('amount'),f:+q.get('tosspay')};try{localStorage.setItem('omr_tosspend',JSON.stringify(p))}catch(e){}history.replaceState(null,'',location.pathname+location.hash)}
 else if(q.get('tosspay')==='fail'){history.replaceState(null,'',location.pathname+location.hash);try{localStorage.removeItem('omr_tosspend')}catch(e){}payDone(false,'결제가 취소됐어요','결제는 진행되지 않았어요. 필요하면 다시 시도해 주세요.');return}
 if(!p||!p.k||!p.f)return;if(!STUD||!STUD.parent||STUD.preview)return;
 await tossConfirm(p)}
/* 결제 승인: 서버 승인 함수(toss-confirm)가 있으면 그걸로, 없으면 「테스트 결제 완료 처리」가 켜져 있을 때만 납부 완료로 바꿔요 */
async function tossConfirm(p){
 try{localStorage.removeItem('omr_tosspend')}catch(e){}
 toast('결제를 확인하는 중이에요…');let msg='',ok=false;
 try{const r=await fetch(base_()+'/functions/v1/toss-confirm',{method:'POST',headers:hdr({'Content-Type':'application/json'}),body:JSON.stringify({login:STUD.login,pw:STUD.pw,feeId:p.f,paymentKey:p.k,orderId:p.o,amount:+p.a})});
  if(r.status!==404){const j=await r.json().catch(()=>({}));ok=!!j.ok;msg=j.err||''}
  else{const r2=await rpc('pa_fee_demo_pay',{p_login:STUD.login,p_pw:STUD.pw,p_fee:p.f});ok=r2.ok&&await r2.json();if(!ok)msg='결제는 됐지만 서버 승인 함수가 아직 없어서 납부 완료로 바꾸지 못했어요. 학원에 알려 주세요'}}
 catch(e){msg='결제를 확인하지 못했어요'}
 const f=(PA.fees||[]).find(x=>x.id===p.f),what=f?f.title+' · '+won(f.amount):(p.t?p.t+' · '+won(p.w||0):'');
 PA.ld=0;PA.sec='fee';tab='patt';render();
 if(ok)payDone(true,'결제가 완료됐어요',what||'납부 내역에 반영됐어요');else payDone(false,'결제를 확인하지 못했어요',msg||'잠시 뒤 납부 내역을 다시 확인해 주세요.')}

/* ---------- 학생 앱: 출결 달력만 (시각·납부는 보이지 않아요) ---------- */
const SA={mon:'',recs:[],ld:0,err:''};
async function sAttView(){
 const m=$('#main');if(!STUD||STUD.parent){m.innerHTML='';return}
 if(!SA.mon)SA.mon=kstDay().slice(0,7);
 if(!SA.ld){m.innerHTML='<div class="card">'+ldg('불러오는 중…')+'</div>';SA.err='';
  try{const[y,mo]=SA.mon.split('-').map(Number);const to=SA.mon+'-'+String(new Date(Date.UTC(y,mo,0)).getUTCDate()).padStart(2,'0');const r=await rpc('st_attendance',{p_login:STUD.login,p_pw:STUD.pw,p_from:SA.mon+'-01',p_to:to});
   if(r.status===404)SA.err='아직 출결 달력을 쓸 수 없어요. 선생님께 문의해 주세요.';else{const j=r.ok?await r.json():null;SA.recs=j||[]}}catch(e){SA.err='불러오지 못했어요. 연결을 확인해 주세요.'}SA.ld=1}
 m.innerHTML=`<div class="tsh"><div><h1>내 출결</h1><p>이번 달 출석 현황이에요.</p></div></div>${SA.err?`<div class="card"><div class="hint">${esc(SA.err)}</div><button class="s sm" style="margin-top:10px" onclick="SA.ld=0;sAttView()">다시 불러오기</button></div>`:`<div class="card"><div class="row" style="gap:8px"><button class="s sm" onclick="SA.mon=ymAdd(SA.mon,-1);SA.ld=0;sAttView()">‹</button><b style="flex:1;text-align:center">${SA.mon.replace('-','년 ')}월</b><button class="s sm" onclick="SA.mon=ymAdd(SA.mon,1);SA.ld=0;sAttView()">›</button>${SA.mon!==kstDay().slice(0,7)?`<button class="s sm" onclick="SA.mon=kstDay().slice(0,7);SA.ld=0;sAttView()">이번 달</button>`:''}</div>${acCal(SA.recs,SA.mon,{noTime:true})}</div>`}`}
