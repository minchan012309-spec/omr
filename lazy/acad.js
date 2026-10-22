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
const SEGS=[['day','출결'],['month','월간 달력'],['pin','출결 번호'],['note','안내문'],['fee','수납'],['rate','요금·계좌']];

async function acJ(path,o){const r=await sb(path,o);if(!r.ok){const e=new Error('http '+r.status);e.status=r.status;try{e.body=await r.text()}catch(x){}throw e}const t=await r.text();return t?JSON.parse(t):null}
const acMissing=e=>e&&(e.status===404||e.status===400||/does not exist|schema cache|column/i.test(e.body||''));

async function attView(){
 const m=$('#main');if(needCloud()){m.innerHTML=atNeed;return}
 if(!AC.day)AC.day=kstDay();if(!AC.mon)AC.mon=AC.day.slice(0,7);
 if(!AC.ld){m.innerHTML='<div class="card">'+ldg('불러오는 중…')+'</div>';await acLoad()}
 const seg=`<div class="bkseg axseg" role="tablist">${SEGS.map(([k,l])=>`<button role="tab" class="${AC.sec===k?'on':''}" onclick="acSec('${k}')">${l}</button>`).join('')}</div>`;
 const body=AC.err==='sql'?SQLMSG:AC.err?`<div class="hint">${esc(AC.err)}</div>`:({day:acDayHtml,month:acMonthHtml,pin:acPinHtml,note:acNoteHtml,fee:acFeeHtml,rate:acRateHtml}[AC.sec]||acDayHtml)();
 m.innerHTML=`<div class="tsh"><div><h1>출결 · 수납</h1><p>등원·하원 기록, 학부모 안내문, 학원비·교재비 수납을 한곳에서 관리해요. 학부모 앱에서도 바로 확인할 수 있어요.</p></div><div class="tsb"><button class="p" onclick="kioskOpen()">출결 단말 시작</button></div></div>${seg}${body}`}
function acSec(k){AC.sec=k;AC.ld=0;attView()}
async function acLoad(){
 AC.err='';
 try{
  AC.stu=await acJ('/rest/v1/students?select=id,name,grade,phone,att_pin&order=name.asc&limit=2000');
  if(AC.sec==='day')AC.recs=await acJ('/rest/v1/attendance?select=*&day=eq.'+AC.day);
  if(AC.sec==='month'&&AC.sid)AC.mrecs=await acJ('/rest/v1/attendance?select=*&student_id=eq.'+AC.sid+'&day=gte.'+AC.mon+'-01&day=lte.'+AC.mon+'-31');
  if(AC.sec==='note')AC.notes=await acJ('/rest/v1/parent_notices?select=*&order=created_at.desc&limit=40');
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
  return `<div class="axr"><div class="axn"><b>${esc(s.name)}</b><small>${esc(s.grade||'')}</small></div>
  <div class="axt">${r&&r.t_in?'<span title="등원">▶ '+kstTime(r.t_in)+'</span>':''}${r&&r.t_out?'<span title="하원">■ '+kstTime(r.t_out)+'</span>':''}</div>
  <div class="axq">${Object.keys(AST).map(k=>`<button class="axb ${st===k?'on':''}" style="--c:${AST[k][1]}" onclick="acSet('${s.id}','${k}')">${AST[k][0]}</button>`).join('')}${r?`<button class="axb x" title="기록 지우기" onclick="acClr('${s.id}')">✕</button>`:''}</div></div>`}).join('');
 return `<div class="card"><div class="row" style="gap:8px;flex-wrap:wrap"><button class="s sm" onclick="acDay(-1)">‹</button><input type="date" value="${AC.day}" onchange="AC.day=this.value||AC.day;AC.ld=0;attView()"><button class="s sm" onclick="acDay(1)">›</button><button class="s sm" onclick="AC.day=kstDay();AC.ld=0;attView()">오늘</button>
 <input type="search" placeholder="이름·학년 검색" value="${esc(AC.q)}" oninput="AC.q=this.value;clearTimeout(window._acq);window._acq=setTimeout(()=>{const k=$('#acrows');if(k)k.innerHTML=acRowsOnly()},180)" style="margin-left:auto;width:190px"></div>
 <div class="axsum"><span style="--c:#1f9d55"><b>${cnt.in}</b>출석</span><span style="--c:#e09a00"><b>${cnt.late}</b>지각</span><span style="--c:#d9534f"><b>${cnt.absent}</b>결석</span><span style="--c:#7a8aa0"><b>${cnt.excused}</b>사유</span><span style="--c:#9aa6b4"><b>${cnt.none}</b>미기록</span></div>
 <div id="acrows">${rows||'<div class="empty">등록한 학생이 없어요.</div>'}</div>
 <p class="tsn2">출결 단말(태블릿)에서 번호를 입력하면 등원이 기록되고, 같은 날 한 번 더 입력하면 하원이 기록돼요. 여기서 직접 고칠 수도 있어요.</p></div>`}
function acRowsOnly(){const d=document.createElement('div');d.innerHTML=acDayHtml();const k=d.querySelector('#acrows');return k?k.innerHTML:''}
function acDay(n){const d=new Date(AC.day+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+n);AC.day=d.toISOString().slice(0,10);AC.ld=0;attView()}
async function acSet(sid,st){const body={student_id:sid,day:AC.day,status:st};if(st==='in'||st==='late'){const r=AC.recs.find(x=>x.student_id===sid);if(!r||!r.t_in)body.t_in=new Date().toISOString()}
 try{const rs=await acJ('/rest/v1/attendance?on_conflict=student_id,day',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=representation'},body:JSON.stringify(body)});const n=(rs&&rs[0])||body;const i=AC.recs.findIndex(x=>x.student_id===sid);if(i>=0)AC.recs[i]=Object.assign(AC.recs[i],n);else AC.recs.push(n);attView()}catch(e){toast('저장하지 못했어요')}}
async function acClr(sid){try{await acJ('/rest/v1/attendance?student_id=eq.'+sid+'&day=eq.'+AC.day,{method:'DELETE'});AC.recs=AC.recs.filter(x=>x.student_id!==sid);attView()}catch(e){toast('지우지 못했어요')}}

/* ---------- 월간 달력 (선생님·학부모 공용) ---------- */
function acCal(recs,ym){
 const by={};recs.forEach(r=>by[r.day]=r);const [Y,M]=ym.split('-').map(Number);const first=new Date(Date.UTC(Y,M-1,1)).getUTCDay(),n=new Date(Date.UTC(Y,M,0)).getUTCDate(),td=kstDay();
 let h='<div class="axcal">'+['일','월','화','수','목','금','토'].map((d,i)=>`<i class="dw${i%6?'':' we'}">${d}</i>`).join('');
 for(let i=0;i<first;i++)h+='<u></u>';
 for(let d=1;d<=n;d++){const k=ym+'-'+String(d).padStart(2,'0'),r=by[k],st=r?AST[r.status]:null;
  h+=`<b class="${k===td?'td':''}${st?' has':''}" ${st?`style="--c:${st[1]}" title="${st[0]}${r.t_in?' · 등원 '+kstTime(r.t_in):''}${r.t_out?' · 하원 '+kstTime(r.t_out):''}"`:''}><em>${d}</em>${st?`<span>${st[0]}</span>${r.t_in?`<small>${kstTime(r.t_in)}${r.t_out?'–'+kstTime(r.t_out):''}</small>`:''}`:''}</b>`}
 h+='</div>';
 const c={in:0,late:0,absent:0,excused:0};recs.forEach(r=>{if(c[r.status]!=null)c[r.status]++});
 return h+`<div class="axsum" style="margin-top:12px"><span style="--c:#1f9d55"><b>${c.in}</b>출석</span><span style="--c:#e09a00"><b>${c.late}</b>지각</span><span style="--c:#d9534f"><b>${c.absent}</b>결석</span><span style="--c:#7a8aa0"><b>${c.excused}</b>사유</span></div>`}
const ymAdd=(ym,n)=>{const [Y,M]=ym.split('-').map(Number);const d=new Date(Date.UTC(Y,M-1+n,1));return d.toISOString().slice(0,7)};
function acMonthHtml(){
 const opts=AC.stu.map(s=>`<option value="${s.id}" ${s.id===AC.sid?'selected':''}>${esc(s.name)} ${esc(s.grade||'')}</option>`).join('');
 return `<div class="card"><div class="row" style="gap:8px;flex-wrap:wrap"><select onchange="AC.sid=this.value;AC.ld=0;attView()"><option value="">학생 선택</option>${opts}</select><button class="s sm" onclick="AC.mon=ymAdd(AC.mon,-1);AC.ld=0;attView()">‹</button><b>${AC.mon.replace('-','년 ')}월</b><button class="s sm" onclick="AC.mon=ymAdd(AC.mon,1);AC.ld=0;attView()">›</button></div>
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
 const opts=AC.stu.map(s=>`<option value="${s.id}">${esc(s.name)} ${esc(s.grade||'')}</option>`).join('');
 const list=AC.notes.map(n=>`<div class="axnl"><div><b>${esc(n.title)}</b><small>${new Date(n.created_at).toLocaleString('ko-KR')} · ${n.student_id?esc(acStuName(n.student_id)):'전체 학부모'}</small><p>${esc(n.body).replace(/\n/g,'<br>')}</p></div><button class="s sm" onclick="acNoteDel(${n.id})">삭제</button></div>`).join('');
 return `<div class="card"><h2 style="margin-top:0">안내문 보내기</h2><div class="g2"><div class="fld"><label>받는 사람</label><select id="ntTo"><option value="">모든 학부모</option>${opts}</select></div><div class="fld"><label>제목</label><input id="ntT" maxlength="60" placeholder="예) 10월 셋째 주 보강 안내"></div><div class="fld"><label>내용</label><textarea id="ntB" rows="5" maxlength="1500" placeholder="학부모 앱의 「납부·안내」에 보여요"></textarea></div></div><button class="p" onclick="acNoteSend()">보내기</button></div>
 <div class="card"><h2 style="margin-top:0">보낸 안내문</h2>${list||'<div class="empty">아직 보낸 안내문이 없어요.</div>'}</div>`}
async function acNoteSend(){const t=$('#ntT').value.trim(),b=$('#ntB').value.trim(),to=$('#ntTo').value;if(!t){toast('제목을 적어 주세요');return}
 try{await acJ('/rest/v1/parent_notices',{method:'POST',headers:{Prefer:'return=minimal'},body:JSON.stringify({title:t,body:b,student_id:to||null})});toast('안내문을 보냈어요');AC.ld=0;attView()}catch(e){toast(acMissing(e)?'서버에 sql_20 을 먼저 실행해 주세요':'보내지 못했어요')}}
async function acNoteDel(id){if(!confirm('이 안내문을 삭제할까요? 학부모 앱에서도 사라져요.'))return;try{await acJ('/rest/v1/parent_notices?id=eq.'+id,{method:'DELETE'});AC.ld=0;attView()}catch(e){toast('삭제하지 못했어요')}}

/* ---------- 수납 ---------- */
function acFeeHtml(){
 const today=kstDay(),fs=AC.fees,paid=f=>f.paid_amount>=f.amount;
 const tot=fs.reduce((a,f)=>a+f.amount,0),got=fs.reduce((a,f)=>a+Math.min(f.paid_amount,f.amount),0),late=fs.filter(f=>!paid(f)&&f.due&&f.due<today).reduce((a,f)=>a+f.amount-f.paid_amount,0);
 const items=AC.pay.items||[];
 const rows=fs.filter(f=>!AC.q||(acStuName(f.student_id)+f.title).includes(AC.q)).map(f=>{const p=paid(f),od=!p&&f.due&&f.due<today;
  return `<div class="axf ${p?'ok':od?'od':''}"><div><b>${esc(acStuName(f.student_id))}</b><small>${esc(f.title)}${f.due?' · '+f.due.slice(5).replace('-','/')+'까지':''}</small></div><span class="axamt">${won(f.amount)}</span><span class="axst">${p?'납부 완료'+(f.method?' · '+esc(f.method):''):od?'연체':'미납'}</span><span class="axab">${p?`<button class="s sm" onclick="acFeeUndo(${f.id})">취소</button>`:`<button class="p sm" onclick="acFeePay(${f.id})">납부 처리</button>`}<button class="s sm" onclick="acFeeDel(${f.id})">삭제</button></span></div>`}).join('');
 const sel=AC.stu.map(s=>`<label class="chk"><input type="checkbox" value="${s.id}" class="acfs">${esc(s.name)}<small>${esc(s.grade||'')}</small></label>`).join('');
 return `<div class="card"><div class="axsum big"><span style="--c:#2a72bf"><b>${won(tot)}</b>총 청구</span><span style="--c:#1f9d55"><b>${won(got)}</b>수납</span><span style="--c:#d9534f"><b>${won(Math.max(0,tot-got))}</b>미수${late?` (연체 ${won(late)})`:''}</span></div></div>
 <div class="card"><h2 style="margin-top:0">청구 만들기</h2>
 <div class="g2"><div class="fld"><label>항목</label><select id="fiSel" onchange="acFiPick(this.value)"><option value="">직접 입력</option>${items.map((it,i)=>`<option value="${i}">${esc(it.name)} · ${won(it.amount)}</option>`).join('')}</select></div><div class="fld"><label>이름</label><input id="fiT" placeholder="예) 10월 수강료" maxlength="40"></div><div class="fld"><label>금액(원)</label><input id="fiA" type="number" min="0" step="1000" placeholder="300000"></div><div class="fld"><label>납부 기한</label><input id="fiD" type="date"></div></div>
 <div class="row" style="margin:8px 0 4px"><b>대상 학생</b><button class="s sm" onclick="document.querySelectorAll('.acfs').forEach(c=>c.checked=true)">전체 선택</button><button class="s sm" onclick="document.querySelectorAll('.acfs').forEach(c=>c.checked=false)">해제</button></div><div class="axchk">${sel||'<span class="m">등록한 학생이 없어요</span>'}</div>
 <button class="p" style="margin-top:10px" onclick="acFeeAdd()">청구하기</button>${items.length?'':'<p class="tsn2">자주 쓰는 학원비·교재비는 「요금·결제 설정」에서 미리 등록해 두면 고르기만 하면 돼요.</p>'}</div>
 <div class="card"><div class="row"><h2 style="margin:0">청구 내역</h2><input type="search" placeholder="이름·항목 검색" value="${esc(AC.q)}" oninput="AC.q=this.value;clearTimeout(window._acq);window._acq=setTimeout(attView,200)" style="margin-left:auto;width:190px"></div>${rows||'<div class="empty">청구 내역이 없어요.</div>'}</div>`}
function acFiPick(i){const it=(AC.pay.items||[])[+i];if(!it)return;$('#fiT').value=it.name;$('#fiA').value=it.amount}
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
 <label class="swr" style="margin-top:12px"><span><b>테스트 결제 완료 처리</b><small>카드 테스트 결제가 끝나면 서버 승인 없이도 납부 완료로 바꿔요. 시연용이에요. 실제 결제를 받을 땐 꺼 주세요.</small></span><input class="swi" type="checkbox" ${P.demo?'checked':''} onchange="acPaySet('demo',this.checked)"></label></div>`}
async function acPaySave(){const d=(await tsRaw())||{};d.pay=AC.pay;const r=await sb('/rest/v1/teacher_settings?on_conflict=user_id',{method:'POST',headers:{Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify({data:d,updated_at:new Date().toISOString()})});if(!r.ok)toast('저장하지 못했어요');else toast('저장했어요')}
function acPaySet(k,v){AC.pay[k]=v;acPaySave()}
function acItem(i,k,v){const it=AC.pay.items[i];if(!it)return;it[k]=k==='amount'?Math.max(0,Math.round(+v||0)):v;acPaySave()}
function acItemAdd(){AC.pay.items=(AC.pay.items||[]).concat([{name:'',amount:0,kind:'tuition'}]);attView()}
function acItemDel(i){AC.pay.items.splice(i,1);acPaySave();attView()}

/* ---------- 출결 단말(키오스크) ---------- */
const KLK='omr_kiosk';
function kioskOpen(){
 if(needCloud()){toast('온라인 저장에 로그인해야 해요');return}
 if(!localStorage.getItem(KLK+'_pw')){const p=prompt('단말을 닫을 때 쓸 해제 번호를 정해 주세요 (숫자 4자리 이상)','');if(!p||!/^\d{4,}$/.test(p)){toast('숫자 4자리 이상으로 정해 주세요');return}localStorage.setItem(KLK+'_pw',p)}
 try{localStorage.setItem(KLK,'1')}catch(e){}
 let k=document.getElementById('kiosk');if(k)k.remove();
 k=document.createElement('div');k.id='kiosk';k.innerHTML=`<style>#kiosk{position:fixed;inset:0;z-index:99990;background:linear-gradient(160deg,#eaf3fd,#fff7dc);color:#1f2933;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;font-family:Pretendard,PretendardLocal,sans-serif;user-select:none;-webkit-user-select:none;touch-action:manipulation}
#kiosk .kt{font-size:clamp(20px,3.4vw,34px);font-weight:800;letter-spacing:-.02em;text-align:center}#kiosk .kc{font-size:clamp(15px,2vw,20px);color:#5f6c7b;margin-top:-10px}
#kiosk .kd{display:flex;gap:12px;min-height:58px}#kiosk .kd i{width:46px;height:58px;border-radius:14px;background:#fff;border:2px solid #cfe0f3;display:grid;place-items:center;font-style:normal;font-size:30px;font-weight:800;color:#1d5ca6}
#kiosk .kp{display:grid;grid-template-columns:repeat(3,clamp(76px,12vmin,110px));gap:12px}#kiosk .kp button{height:clamp(66px,10.5vmin,96px);border-radius:22px;border:0;background:#fffc;box-shadow:0 2px 10px #1d5ca62a;font:inherit;font-size:clamp(26px,4vmin,38px);font-weight:700;color:#1f2933;cursor:pointer}#kiosk .kp button:active{background:#d9e8f8}#kiosk .kp .go{background:#2a72bf;color:#fff;font-size:clamp(18px,2.6vmin,24px)}
#kiosk .kh{background:#fff9;border-radius:14px;padding:9px 16px;font-size:clamp(14px,1.9vw,18px);color:#394553}#kiosk .kh b{color:#1d5ca6}#kiosk .kr{min-height:90px;text-align:center;font-size:clamp(20px,3vw,30px);font-weight:800}#kiosk .kr.ok{color:#1f9d55}#kiosk .kr.no{color:#d9534f}#kiosk .kr small{display:block;font-size:.55em;font-weight:500;color:#5f6c7b;margin-top:4px}
#kiosk .kch{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:8px}#kiosk .kch button{padding:12px 20px;border-radius:14px;border:0;background:#fff;box-shadow:0 2px 8px #0002;font:inherit;font-size:18px;font-weight:700;cursor:pointer}
#kiosk .kx{position:absolute;right:0;top:0;width:70px;height:70px;background:none;border:0;opacity:0}</style>
<button class="kx" aria-label="해제" onclick="kioskTap()"></button>
<svg viewBox="0 8 162 76" width="130" aria-hidden="true"><path d="M23.8 56.8C36.1 56.8 43.8 51.6 45.4 42.2C46.7 34.4 42.6 29.9 32.2 28L28.6 27.3C23.9 26.4 22.3 25.2 22.7 22.9C23.1 20.6 25.9 18.9 29.6 18.9C33.6 18.9 35.7 20.8 35.5 24.2H47.4C48.7 14.4 42.1 8.7 30.4 8.7C19.4 8.7 11.1 14.3 9.7 22.8C8.4 30.1 12.8 35.2 21.5 36.9L26 37.8C31.1 38.8 32.9 40.2 32.5 42.4C32.1 44.8 29.1 46.5 25 46.5C20.3 46.5 17.7 44.3 18.1 40.5H5.8C4.2 50.7 10.6 56.8 23.8 56.8Z M63.1 56.8C75.6 56.8 83.5 47.7 83.5 36.8C83.5 27.8 77.3 22.2 67.5 22.2C55.6 22.2 47.1 30.6 47.1 42.2C47.1 51.2 53.3 56.8 63.1 56.8ZM63.9 47C61.7 47 59.6 45.5 59.6 42.3C59.6 37.6 62 32 66.7 32C68.9 32 71 33.5 71 36.7C71 41.4 68.6 47 63.9 47Z M102.9 9.4H90.4L82.7 56H95.2Z M107.6 56H121.9L139.2 23H125.8L119.6 37C118.5 39.6 117.3 42.1 116.3 44.7C116 42.1 115.8 39.6 115.4 37L113.7 23H101.2Z M134.3 56H146.8L152.3 23H139.8ZM146.5 20.3C150.1 20.3 153.3 17.6 153.9 14.2C154.5 10.8 152.1 8.1 148.5 8.1C144.9 8.1 141.7 10.8 141.1 14.2C140.5 17.6 142.9 20.3 146.5 20.3Z" fill="#1d5ca6"/><path d="M4 68 L27.1 78 L150.3 62" fill="none" stroke="#ffc21a" stroke-width="7" stroke-linecap="round"/></svg>
<div class="kt">출결 번호를 눌러 주세요</div><div class="kc" id="kclk"></div><div class="kh">예) 전화번호가 010-<b>12345</b>678 이면 <b>12345</b> 를 누르고 「확인」</div><div class="kd" id="kdg"></div>
<div class="kp">${[1,2,3,4,5,6,7,8,9].map(n=>`<button onclick="kioskKey('${n}')">${n}</button>`).join('')}<button onclick="kioskKey('c')" aria-label="지우기">⌫</button><button onclick="kioskKey('0')">0</button><button class="go" onclick="kioskGo()">확인</button></div>
<div class="kr" id="krs"></div>`;
 document.body.appendChild(k);KIO.pin='';KIO.n=0;kioskDraw();clearInterval(KIO.ck);KIO.ck=setInterval(kioskClock,15000);kioskClock();
 try{(document.documentElement.requestFullscreen||function(){}).call(document.documentElement)}catch(e){}
 document.addEventListener('keydown',kioskKd)}
const KIO={pin:'',n:0,ck:0,rt:0,busy:0};
function kioskClock(){const e=document.getElementById('kclk');if(e)e.textContent=new Date().toLocaleString('ko-KR',{month:'long',day:'numeric',weekday:'short',hour:'2-digit',minute:'2-digit',hour12:false,timeZone:'Asia/Seoul'})}
function kioskDraw(){const e=document.getElementById('kdg');if(!e)return;const n=Math.max(5,KIO.pin.length);e.innerHTML=Array.from({length:n},(_,i)=>`<i>${KIO.pin[i]?'●':''}</i>`).join('')}
function kioskKd(e){if(!document.getElementById('kiosk'))return;if(/^\d$/.test(e.key))kioskKey(e.key);else if(e.key==='Backspace')kioskKey('c');else if(e.key==='Enter')kioskGo()}
function kioskKey(k){if(KIO.busy)return;if(k==='c')KIO.pin=KIO.pin.slice(0,-1);else if(KIO.pin.length<8)KIO.pin+=k;kioskDraw();const r=document.getElementById('krs');if(r&&!KIO.rt)r.textContent='';if(KIO.pin.length>=5&&!KIO.auto){clearTimeout(KIO.at);KIO.at=setTimeout(()=>{if(KIO.pin.length>=5)kioskGo()},900)}}
function kioskShow(cls,html){const r=document.getElementById('krs');if(!r)return;r.className='kr '+cls;r.innerHTML=html;clearTimeout(KIO.rt);KIO.rt=setTimeout(()=>{KIO.rt=0;const x=document.getElementById('krs');if(x){x.textContent='';x.className='kr'}},4200)}
async function kioskGo(sid){clearTimeout(KIO.at);if(KIO.busy||KIO.pin.length<3)return;KIO.busy=1;const pin=KIO.pin;
 try{const r=await rpc('att_checkin',{p_pin:pin,p_student:sid||null});const j=r.ok?await r.json():null;
  if(!j){kioskShow('no','연결에 실패했어요<small>잠시 뒤 다시 눌러 주세요</small>')}
  else if(j.ok){KIO.pin='';kioskDraw();const t=kstTime(j.t);kioskShow('ok',j.kind==='in'?esc(j.name)+' 학생, 어서 와요!<small>'+t+' 등원했어요</small>':j.kind==='out'?esc(j.name)+' 학생, 잘 가요!<small>'+t+' 하원했어요</small>':esc(j.name)+' 학생은 이미 기록됐어요<small>잠시 뒤 다시 눌러 주세요</small>')}
  else if(j.err==='choose'){const r2=document.getElementById('krs');r2.className='kr';r2.innerHTML='누구세요?<div class="kch">'+j.choose.map(c=>`<button onclick="kioskPick('${c.id}')">${esc(c.name)}<small style="font-size:12px;font-weight:500"> ${esc(c.grade||'')}</small></button>`).join('')+'</div>';clearTimeout(KIO.rt);KIO.rt=1}
  else{KIO.pin='';kioskDraw();kioskShow('no','번호를 찾을 수 없어요<small>선생님께 출결 번호를 물어보세요</small>')}
 }catch(e){kioskShow('no','연결에 실패했어요')}
 KIO.busy=0}
function kioskPick(id){KIO.rt=0;kioskGo(id)}
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
 const S=[['att','출결'],['note','안내문'],['fee','납부']];
 const seg=`<div class="bkseg axseg" role="tablist">${S.map(([k,l])=>`<button role="tab" class="${PA.sec===k?'on':''}" onclick="PA.sec='${k}';pAttView()">${l}${k==='fee'&&PA.fees.some(f=>f.paid_amount<f.amount)?' <i class="axdot"></i>':''}</button>`).join('')}</div>`;
 let b='';
 if(PA.err)b=`<div class="card"><div class="hint">${esc(PA.err)}</div></div>`;
 else if(PA.sec==='att')b=`<div class="card"><div class="row" style="gap:8px"><button class="s sm" onclick="PA.mon=ymAdd(PA.mon,-1);PA.ld=0;pAttView()">‹</button><b style="flex:1;text-align:center">${PA.mon.replace('-','년 ')}월 출결</b><button class="s sm" onclick="PA.mon=ymAdd(PA.mon,1);PA.ld=0;pAttView()">›</button></div>${acCal(PA.recs,PA.mon)}</div>`;
 else if(PA.sec==='note')b=`<div class="card">${PA.notes.length?PA.notes.map(n=>`<div class="axnl"><div><b>${esc(n.title)}</b><small>${new Date(n.t).toLocaleString('ko-KR')}</small><p>${esc(n.body).replace(/\n/g,'<br>')}</p></div></div>`).join(''):'<div class="empty">받은 안내문이 없어요.</div>'}</div>`;
 else b=paFeeHtml();
 m.innerHTML=`<div class="tsh"><div><h1>${esc((STINFO&&STINFO.name)||'자녀')} 학생</h1><p>출결과 학원 안내, 납부 내역을 확인해요.</p></div></div>${seg}${b}`}
async function paLoad(){PA.err='';const a={p_login:STUD.login,p_pw:STUD.pw};
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
  return `<div class="axf ${p?'ok':od?'od':''}"><div><b>${esc(f.title)}</b><small>${f.due?f.due.slice(5).replace('-','/')+'까지':''}${p&&f.paid_at?' · '+new Date(f.paid_at).toLocaleDateString('ko-KR')+' 납부':''}</small></div><span class="axamt">${won(f.amount)}</span><span class="axst">${p?'납부 완료':od?'연체':'미납'}</span><span class="axab">${p?'':`<button class="p sm" onclick="paPay(${f.id})">납부하기</button>`}</span></div>`}).join('');
 return `<div class="card">${rows}<div id="axpay"></div></div>`}

function paPay(id){const f=PA.fees.find(x=>x.id===id),P=PA.pay||{},e=document.getElementById('axpay');if(!f||!e)return;
 e.innerHTML=`<div class="hint" style="margin-top:10px"><b>${esc(f.title)} · ${won(f.amount)}</b><div style="margin:8px 0"><button class="p" onclick="paToss(${f.id})">카드로 결제하기</button> <small>(테스트 결제 · 실제 금액이 빠져나가지 않아요)</small></div>${P.bank?`<b>계좌 이체</b><br><span style="font-size:16px;font-weight:700;color:var(--t);letter-spacing:.01em">${esc(P.bank)}</span><div style="margin-top:8px"><button class="s sm" onclick="paCopy()">계좌 복사</button></div><small style="display:block;margin-top:6px">입금하시면 선생님이 확인한 뒤 납부 완료로 바꿔 드려요.</small>`:'아직 계좌 안내가 등록되지 않았어요. 학원에 문의해 주세요.'}</div>`;
 e.scrollIntoView({behavior:'smooth',block:'nearest'})}
function paCopy(){const b=(PA.pay||{}).bank||'';try{navigator.clipboard.writeText(b).then(()=>toast('계좌를 복사했어요'),()=>toast('복사하지 못했어요'))}catch(e){toast('복사하지 못했어요')}}

async function paToss(id){const f=PA.fees.find(x=>x.id===id);if(!f)return;
 try{if(!window.TossPayments){await new Promise((ok,no)=>{const s=document.createElement('script');s.src='https://js.tosspayments.com/v2/standard';s.onload=ok;s.onerror=no;document.head.appendChild(s)})}
  const tp=window.TossPayments(PA.pay.clientKey||TOSS_KEY),pay=tp.payment({customerKey:'solvi-'+String(STUD.login).replace(/[^A-Za-z0-9_-]/g,'').slice(0,40).padEnd(2,'x')});
  const base=location.origin+location.pathname;
  await pay.requestPayment({method:'CARD',amount:{currency:'KRW',value:f.amount},orderId:'solvi-'+f.id+'-'+Date.now().toString(36),orderName:f.title,successUrl:base+'?tosspay='+f.id,failUrl:base+'?tosspay=fail',customerName:(STINFO&&STINFO.name)||undefined})
 }catch(e){if(e&&e.code!=='USER_CANCEL')toast('결제창을 열지 못했어요'+(e&&e.message?' ('+e.message+')':''))}}
/* 결제창에서 돌아오면: 서버 승인 함수(toss-confirm)가 있으면 그걸로, 없으면 「테스트 결제 완료 처리」가 켜져 있을 때만 납부 완료로 바꿔요 */
async function tossReturn(){
 let p=null;try{p=JSON.parse(localStorage.getItem('omr_tosspend')||'null')}catch(e){}
 const q=new URLSearchParams(location.search);
 if(q.get('paymentKey')){p={k:q.get('paymentKey'),o:q.get('orderId'),a:q.get('amount'),f:+q.get('tosspay')};try{localStorage.setItem('omr_tosspend',JSON.stringify(p))}catch(e){}history.replaceState(null,'',location.pathname+location.hash)}
 else if(q.get('tosspay')==='fail'){history.replaceState(null,'',location.pathname+location.hash);toast('결제가 취소되었어요');return}
 if(!p||!p.k||!p.f)return;if(!STUD||!STUD.parent)return;
 try{localStorage.removeItem('omr_tosspend')}catch(e){}
 toast('결제를 확인하는 중이에요…');let msg='',ok=false;
 try{const r=await fetch(base_()+'/functions/v1/toss-confirm',{method:'POST',headers:hdr({'Content-Type':'application/json'}),body:JSON.stringify({login:STUD.login,pw:STUD.pw,feeId:p.f,paymentKey:p.k,orderId:p.o,amount:+p.a})});
  if(r.status!==404){const j=await r.json().catch(()=>({}));ok=!!j.ok;msg=j.err||''}
  else{const r2=await rpc('pa_fee_demo_pay',{p_login:STUD.login,p_pw:STUD.pw,p_fee:p.f});ok=r2.ok&&await r2.json();if(!ok)msg='결제는 됐지만 서버 승인 함수가 아직 없어서 납부 완료로 바꾸지 못했어요. 학원에 알려 주세요'}}
 catch(e){msg='결제를 확인하지 못했어요'}
 toast(ok?'결제가 완료됐어요':msg||'결제를 확인하지 못했어요');PA.ld=0;PA.sec='fee';tab='patt';render()}
