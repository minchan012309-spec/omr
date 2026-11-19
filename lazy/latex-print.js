/* Only records explicitly marked xelatex-v1 enter this path. */
async function ltPageModel(element,assets,codes,kind){
 const clone=element.cloneNode(true);
 clone.querySelectorAll('.pg > .ph1,.pg > .ph2,.pg > .ft,.pg > .footer,.bp > .hd,.bp > .ft,.bp > .footer,.qrh,.bklg,.thr').forEach(n=>n.remove());
 // Answer headings carry semantic metadata; old HTML headings would leak codes when hidden.
 for(const el of clone.querySelectorAll('.sb.wq,.u.x')){
  const head=el.querySelector(':scope > .h,:scope > .xh');
  const code=el.dataset.c||head?.querySelector('.xm')?.textContent.trim().split(/\s+/).at(-1);
  if(code&&byCode[code])el.dataset.c=code;
  el.dataset.solviRole='answer';
  if(!el.dataset.solviNumber){const number=head?.querySelector('.xn')?.textContent||head?.textContent.match(/^\s*(\d+)/)?.[1];if(number)el.dataset.solviNumber=number}
  el.dataset.solviAnswer=head?.querySelector('.ws-answer,.xa')?.textContent||'';
  if(head)head.remove();el.querySelectorAll('.sol > .sh').forEach(n=>n.remove());
 }
 const top=[...clone.querySelectorAll('.tp,.cntop')];const topNodes=[];for(const n of top){topNodes.push(...await SolviPrint.fragment(n.innerHTML,assets));n.remove()}
 const cols=[...clone.querySelectorAll('.cols>.col')];
 const content=cols.length?cols:[clone.querySelector('.bd')||clone];
 return {kind,codes,top:topNodes,columns:await Promise.all(content.slice(0,2).map(c=>SolviPrint.fragment(c.innerHTML,assets)))};
}
function ltAppearance(value={}){const fontSize=Number(value.fontSize);return {fontFamily:['shin','kopub','pretendard'].includes(value.fontFamily)?value.fontFamily:'shin',fontSize:Number.isFinite(fontSize)&&fontSize>=8&&fontSize<=14?Math.round(fontSize*2)/2:10,design:['reference','simple','boxed'].includes(value.design)?value.design:'reference'}}
function ltBaseModel(rec){const c=rec.cover||{},opt=rec.latexOptions||{};
 return {...ltAppearance({...rec,...opt}),showTypes:opt.showTypes!==false,showCodes:opt.showCodes===true,roundLabel:rec.roundLabel||(rec.round?'제 '+rec.round+'회':''),templateVersion:rec.templateVersion||SolviPrint.TEMPLATE,publicBase:(CF.pub||location.origin+'/').split('#')[0].split('?')[0],title:opt.title||c.title||rec.title||rec.name||'학습 자료',name:rec.name||'',subjectId:SUBJ,subject:opt.subject||c.subject||SNAME[SUBJ],cover:{handwriting:opt.handwriting||'오늘의 배움을 내일의 실력으로',instructions:opt.instructions||'○ 답안지의 해당란에 성명과 수험번호를 쓰고, 또 수험번호, 문항, 답을 정확히 표시하시오.\n○ 단답형 답의 숫자에 ‘0’이 포함되면 그 ‘0’도 답란에 반드시 표시하시오.\n○ 문항에 따라 배점이 다르니, 각 물음의 끝에 표시된 배점을 참고하시오. 배점은 2점, 3점 또는 4점입니다.\n○ 계산은 문제지의 여백을 활용하시오.',organization:opt.organization||rec.academy||c.org||''},duplex:typeof dupGet==='function'&&dupGet(),assets:{},pages:[]};
}
function ltRanges(model){const labels={questions:'문제지',answers:'정답 및 해설',concept:'개념',contents:'차례',notes:'필기'};const lines=[];
 for(const [kind,label] of Object.entries(labels)){const ps=model.pages.flatMap((p,i)=>p.kind===kind?[i+1]:[]);if(ps.length)lines.push(label+' ··· '+ps[0]+'~'+ps.at(-1)+'쪽')}
 model.cover.ranges=lines.join('\n');
}
async function ltWorksheetModel(rec,root){
 const model=ltBaseModel(rec);model.material='worksheet';model.per=rec.per==='auto'||!rec.per?4:+rec.per;model.worksheetId=rec.id;model.questionKind=rec.codes.every(c=>{const host=document.createElement('div');host.innerHTML=byCode[c]?.q||'';return host.querySelector('.chs')?.children.length===5})?'5지선다형':'학습 문항';let qi=0,ai=0;
 for(const pg of root.querySelectorAll('.pg')){
  if(pg.classList.contains('mcover')){model.pages.push({kind:'cover',codes:[],columns:[]});continue}
  if(pg.classList.contains('wblank')){model.pages.push({kind:'blank',codes:[],columns:[]});continue}
  const sol=pg.dataset.solviKind==='answers';const count=sol?0:pg.querySelectorAll('.wq').length;
  const codes=sol?[]:rec.codes.slice(qi,qi+count);if(sol)[...pg.querySelectorAll('.sb.wq')].forEach(el=>{el.dataset.c=rec.codes[ai]||'';el.dataset.solviNumber=String(++ai);el.dataset.solviRole='answer'});if(!sol)[...pg.querySelectorAll('.wq')].forEach((el,i)=>el.dataset.c=codes[i]||'');qi+=count;
  model.pages.push(await ltPageModel(pg,model.assets,codes,sol?'answers':count?'questions':'concept'));
 }
 if(qi!==rec.codes.length&&rec.part!=='a')throw Error('문제 쪽과 문항 목록이 일치하지 않습니다');
 return model;
}
async function ltWorksheet(w,rec,root){return ltViewer(w,await ltWorksheetModel(rec,root),rec,()=>{wsStore();if(srv==='cloud')wsPost(rec).catch(()=>{})})}
let LTINLINE_RUNNING=false,LTINLINE_NEXT=null;const LTINLINE_OWNER={};
async function ltInlinePreview(model,apply,onError){LTINLINE_NEXT={model,apply,onError};if(LTINLINE_RUNNING)return;LTINLINE_RUNNING=true;try{while(LTINLINE_NEXT){const job=LTINLINE_NEXT;LTINLINE_NEXT=null;try{const result=await SolviPrint.submit(job.model,LTINLINE_OWNER);if(!LTINLINE_NEXT)job.apply(result)}catch(e){if(!LTINLINE_NEXT)job.onError(e)}}}finally{LTINLINE_RUNNING=false}}
async function ltBook(id,all,w){
 if(!await bkxAccess(id))return;
 w=w||popOpen('PDF를 준비하는 중…');
 try{await bkInit();const P=bkParts(id);if(P&&P.subj!==SUBJ)await setSubject(P.subj);const plan=await bkPlan(id);if(!plan)throw Error('교재를 찾지 못했습니다');
 const rec=bkxAll().find(b=>b.id===String(id).replace(/~g[1-3]$/,'').replace(/(~l[0-9a-f]{16})r\d+$/,'$1'));if(!rec)throw Error('새 교재 정의가 없습니다');
 let model=ltBaseModel({...rec,title:plan.title,name:'',round:P&&P.def&&P.def.round||0});model.material='book';model.bookId=id.replace(/~g[1-3]$/,'');model.contentsEntries=(plan.toc||[]).map(r=>({title:(r.sub?r.sub.k+' '+r.sub.name:r.title||''),items:(r.items||[]).map(x=>x[0])}));
 if(plan.kind!=='m'){const basic=model;model={...basic,...await SolviLatexBookLayout.capture(plan,all,{onProgress:(n,total)=>{if(w.closed)throw Error('교재 출력을 취소했습니다');w.document.body.textContent='교재 '+n+' / '+total+'쪽을 준비하는 중…'}}),publicBase:basic.publicBase,subjectId:SUBJ,subject:basic.subject,bookId:id.replace(/~g[1-3]$/,'')};}else{ for(let i=0;i<plan.pages.length;i++){
  const pg=plan.pages[i];if(!all&&['ak','es'].includes(pg.k))continue;
  if(pg.k==='cover'||pg.k==='mcv'){model.pages.push({kind:'cover',codes:[],columns:[]});continue}
  if(pg.k==='back'){model.pages.push({kind:'back',codes:[],columns:[]});continue;}
  if(pg.k==='toc'){model.pages.push({kind:'contents',codes:[],columns:[]});continue;}
  if(pg.k==='nt'){model.pages.push({kind:'notes',codes:[],columns:[],noteStyle:pg.st||'lined',noteLabel:pg.label||'필기 노트'});continue;}
  const host=document.createElement('div');host.innerHTML=bkPageHtml(plan,i);
  const kind=pg.k==='cn'?'concept':pg.k==='toc'?'contents':pg.k==='nt'?'notes':['ak','es'].includes(pg.k)?'answers':'questions';
  model.pages.push(await ltPageModel(host,model.assets,kind==='questions'?pg.codes||[]:[],kind));
 }
 }
 await ltViewer(w,model,rec,result=>{const items=bkxAll();const index=items.findIndex(b=>b.id===rec.id);if(index<0)throw Error('교재 저장 정보를 찾지 못했습니다');const latest=items[index],latexOutputs={...(latest.latexOutputs||{})},outputs={...(latexOutputs[id]||{})};outputs[all?'all':'questions']={id:result.id,manifest:result.manifest};outputs.active=all?'all':'questions';latexOutputs[id]=outputs;items[index]={...latest,latexOptions:{...rec.latexOptions},latexManifest:result.id,latexOutputs,updatedAt:Date.now()};bkxStore(items)});
 }catch(e){ltError(w,e)}
}
function ltError(w,e){if(w&&!w.closed){w.document.body.textContent=e?.message||'PDF 생성 실패';w.document.title='PDF 생성 실패'}else alert(e?.message||'PDF를 만들지 못했습니다')}
async function ltViewer(w,model,rec,save){
 if(!w)throw Error('PDF 창을 열 수 없습니다. 팝업을 허용한 뒤 다시 시도해 주세요');
 const isBook=model.layout==='book-original-v1',doc=w.document;doc.open();doc.write('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PDF 출력</title><style>');
 doc.write('@font-face{font-family:Pretendard;src:url("'+new URL('fonts/Pretendard-Regular.woff2',location.href).href+'") }*{box-sizing:border-box}body{margin:0;background:#eef1f4;color:#182129;font:14px Pretendard,sans-serif}.layout{display:grid;grid-template-columns:280px 1fr;height:100dvh}aside{padding:24px;background:#fff;border-right:1px solid #dce2e7;overflow:auto}h1{font-size:19px;margin:0 0 24px}label{display:block;margin:16px 0 6px;font-size:13px}input,textarea,select,button{font:inherit;border:1px solid #c6d0d9;border-radius:7px;padding:10px;background:#fff;color:inherit}input,textarea,select{width:100%}textarea{min-height:90px;resize:vertical}button{cursor:pointer;width:100%;margin-top:14px;background:#173f66;color:#fff;border-color:#173f66}button:disabled{opacity:.5;cursor:wait}.save{background:#fff;color:#173f66}.status{line-height:1.6;overflow-wrap:anywhere;margin:16px 0}button[hidden]{display:none}iframe{width:100%;height:100%;border:0}main{min-width:0;position:relative}.skeleton{position:absolute;inset:24px;background:#fff;padding:12%;display:flex;flex-direction:column;gap:24px}.skeleton i{display:block;height:12px;background:#edf0f3}.skeleton i:nth-child(2){width:60%;margin-bottom:40px}.skeleton[hidden]{display:none}@media(max-width:700px){.layout{display:flex;flex-direction:column;height:auto}aside{border:0;padding:20px}main{height:80dvh}}');
 doc.write('</style><div class="layout"><aside><h1>출력 설정</h1><form id="settings"><label for="design">디자인</label><select id="design"><option value="reference">원본 양식</option><option value="simple">간결형</option><option value="boxed">박스형</option></select><label for="fontFamily">본문 글꼴</label><select id="fontFamily"><option value="shin">신명조 · 원본</option><option value="kopub">KoPubWorld 돋움</option><option value="pretendard">Pretendard</option></select><label for="fontSize">본문 글자 크기 (pt)</label><input id="fontSize" type="number" min="8" max="14" step="0.5"><label for="title">제목</label><input id="title"><label for="subject">과목명</label><input id="subject"><label for="organization">학원·학교 이름</label><input id="organization"><label for="handwriting">필적확인 문구</label><input id="handwriting"><label for="instructions">유의사항</label><textarea id="instructions"></textarea><label for="cover">앞표지</label><select id="cover"><option value="1">넣기</option><option value="0">넣지 않기</option></select><label for="showTypes">유형명</label><select id="showTypes"><option value="1">표시</option><option value="0">표시하지 않기</option></select><label for="showCodes">문항코드</label><select id="showCodes"><option value="1">표시</option><option value="0">표시하지 않기</option></select><button id="generate" type="submit" hidden>다시 만들기</button></form><button class="save" id="cancel" disabled>생성 취소</button><p class="status" role="status" aria-live="polite" id="status">PDF를 준비합니다.</p><button class="save" id="download" disabled>PDF 저장</button><button class="save" id="print" disabled>인쇄</button></aside><main><div id="waiting" class="skeleton" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div><iframe title="인쇄용 PDF 미리보기" id="pdf"></iframe></main></div></html>');doc.close();
 const owner={},get=id=>doc.getElementById(id);for(const [key,value] of Object.entries(ltAppearance(model)))get(key).value=value;if(typeof isMob==='function'&&isMob())get('print').hidden=true;for(const k of ['title','subject'])get(k).value=model[k];for(const k of ['organization','handwriting','instructions'])get(k).value=model.cover[k];
 get('cover').value=(rec.latexOptions&&rec.latexOptions.coverOn!==undefined?rec.latexOptions.coverOn:model.pages.some(p=>p.kind==='cover'))?'1':'0';
 for(const key of ['showTypes','showCodes'])get(key).value=(key==='showTypes'?model[key]!==false:model[key]===true)?'1':'0';
 if(isBook){get('settings').hidden=true;get('settings').insertAdjacentHTML('beforebegin','<p>기존 교재 디자인으로 출력합니다.</p><button class="save" id="bookedit">교재 미리보기 · 설정</button>');get('bookedit').onclick=()=>{w.close();bkEbook(model.bookId)}}
 let blobUrl=null,generating=false,closed=false,revision=0,timer=null,ready=null,exporting=false,queued=false;
 const buttons=()=>{const disabled=exporting||generating||!!timer||!ready||ready.revision!==revision;get('download').disabled=disabled;get('print').disabled=disabled;get('cancel').disabled=!generating;get('generate').disabled=generating};
 const snapshot=()=>{const next=JSON.parse(JSON.stringify(model));if(isBook)return next;Object.assign(next,ltAppearance({fontFamily:get('fontFamily').value,fontSize:get('fontSize').value,design:get('design').value}));for(const key of ['showTypes','showCodes'])next[key]=get(key).value==='1';next.title=get('title').value;next.subject=get('subject').value;for(const k of ['organization','handwriting','instructions'])next.cover[k]=get(k).value;next.pages=next.pages.filter(p=>p.kind!=='cover');if(get('cover').value==='1')next.pages.unshift({kind:'cover',codes:[],columns:[]});ltRanges(next);return next};
 const generate=async()=>{
  if(closed)return;if(generating){queued=true;return}
  clearTimeout(timer);timer=null;queued=false;const version=revision,next=snapshot();generating=true;get('waiting').hidden=!!blobUrl;get('generate').hidden=true;get('status').textContent=blobUrl?'설정을 반영하는 중… 이전 미리보기를 표시합니다.':'글꼴과 PDF를 준비하는 중…';buttons();
  try{
   const result=await SolviPrint.submit(next,owner);
   if(closed||version!==revision)return;
   const previous=blobUrl;blobUrl=URL.createObjectURL(result.blob);ready={result,model:next,revision:version};get('pdf').src=blobUrl+'#toolbar=0&navpanes=0';get('pdf').hidden=false;if(previous)URL.revokeObjectURL(previous);get('status').textContent=result.manifest.pages.length+'쪽 · PDF 생성 완료 · 설정은 자동 반영됩니다.';
  }catch(e){if(!closed&&version===revision){get('status').textContent=e?.message||'PDF를 만들지 못했습니다';get('generate').hidden=false}}
  finally{generating=false;if(!closed){get('waiting').hidden=true;buttons();if(queued&&!timer){queued=false;generate()}}}
 };
 const changed=()=>{revision++;ready=null;queued=true;clearTimeout(timer);get('generate').hidden=true;get('status').textContent='변경한 설정을 반영합니다…';timer=setTimeout(()=>{timer=null;generate()},650);buttons()};
 get('settings').addEventListener('input',changed);get('settings').addEventListener('change',e=>{if(e.target.tagName==='SELECT')changed()});
 get('settings').onsubmit=e=>{e.preventDefault();generate()};
 get('cancel').onclick=()=>{revision++;queued=false;clearTimeout(timer);timer=null;SolviLocalTex.cancel(undefined,owner);get('status').textContent='PDF 생성을 취소했습니다. 설정을 바꾸면 다시 반영됩니다.';get('generate').hidden=false;buttons()};
 w.addEventListener('pagehide',()=>{closed=true;clearTimeout(timer);if(generating)SolviLocalTex.cancel(undefined,owner);SolviLocalTex.release();if(blobUrl)URL.revokeObjectURL(blobUrl)},{once:true});
 const finalOutput=async action=>{
  const current=ready;if(!current||current.revision!==revision||generating||exporting||timer)return;exporting=true;buttons();get('status').textContent='QR 채점 정보를 저장하는 중…';
  try{
   await SolviLocalTex.persist(current.result);if(closed||current.revision!==revision)return;
   if(!isBook)rec.latexOptions={...ltAppearance(current.model),showTypes:current.model.showTypes,showCodes:current.model.showCodes,coverOn:current.model.pages.some(p=>p.kind==='cover'),title:current.model.title,subject:current.model.subject,...current.model.cover};rec.latexManifest=current.result.id;await save(current.result);
   if(closed||current.revision!==revision)return;
   if(action==='print'){get('pdf').contentWindow.focus();get('pdf').contentWindow.print()}else{const a=doc.createElement('a');a.href=blobUrl;a.download=current.model.title.replace(/[\\/:*?"<>|]/g,' ')+'.pdf';a.click()}
   get('status').textContent=current.result.manifest.pages.length+'쪽 · QR 채점 정보 저장 완료';
  }catch(e){if(!closed&&current.revision===revision)get('status').textContent=e?.message||'PDF를 저장하지 못했습니다'}finally{exporting=false;if(!closed)buttons()}
 };
 get('download').onclick=()=>finalOutput('download');get('print').onclick=()=>finalOutput('print');
 await generate();
}
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
