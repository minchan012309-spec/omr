/* Read-only compatibility for QR codes already printed on earlier PDFs. */
const LTMANIFESTS=new Map();
async function ltRoute(value,sourceId){
 try{
  const m=/^([a-f0-9]{32}):(\d+|all)$/.exec(value);if(!m)throw Error('채점 경로 오류');
  const doc=await SolviPrint.lookup(m[1]);LTMANIFESTS.set(m[1],doc);
  if(doc.material==='worksheet'&&doc.worksheetId)return openByNumber(doc.worksheetId);
  const page=m[2]==='all'?null:doc.pages[+m[2]-1];const codes=m[2]==='all'?[...new Set(doc.pages.filter(p=>p.kind==='questions').flatMap(p=>p.codes))]:page&&page.codes;
  if(!codes||!codes.length)throw Error('채점할 문항이 없습니다');
  const subj=SNAME[doc.subject]?doc.subject:Object.keys(SNAME).find(k=>SNAME[k]===doc.subject);if(!subj)throw Error('과목 오류');
  if(needLogin()){askLogin('LT:'+value);return}if(guardStu())return;
  if(SUBJ!==subj)await setSubject(subj);await ensureCodes(codes);const qs=codes.map(c=>byCode[c]);if(qs.some(q=>!q))throw Error('문항을 찾지 못했습니다');
  const digest=doc.bookId?Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(doc.bookId+'\n'+codes.slice().sort().join('\n')))),v=>v.toString(16).padStart(2,'0')).join('').slice(0,32):null;const nums=m[2]==='all'?Object.assign({},...doc.pages.map(p=>p.nums||{})):page.nums||{};const key=digest?'ltb-'+digest:'lt-'+m[1]+':'+m[2],bk={lt:m[1],bk:sourceId&&/^[-A-Za-z0-9_.~]+$/.test(sourceId)?sourceId:'lt-'+m[1],nums,page:key,n:m[2]==='all'?0:+m[2],all:m[2]==='all'?1:0,label:SNAME[subj]+' '+(m[2]==='all'?'전체':m[2]+'쪽')};
  const locked=recLock('book',key);if(locked&&locked.items){showLockedRec(locked,{book:bk});return}newCur(qs,{book:bk});
 }catch(e){alert(e.message||'채점 자료를 열지 못했습니다')}
}

function ltNextHtml(book){const doc=LTMANIFESTS.get(book.lt);if(!doc)return '';let next;if(typeof BKQ!=='undefined'&&BKQ&&BKQ.id===book.bk){BKQ.pages=BKQ.pages.filter(n=>n!==book.n);next=BKQ.pages[0];if(!next)return ''}else{const index=doc.pages.findIndex((p,i)=>i+1>book.n&&p.kind==='questions'&&p.codes.length);next=index<0?null:index+1}return next?'<div class="hint" style="margin:10px 0">다음 문제 쪽(<b>p.'+next+'</b>)도 이어서 채점할까요? <button class="p" onclick="ltRoute(\''+book.lt+':'+next+'\',\''+book.bk+'\')">p.'+next+' 채점하기</button></div>':''}
