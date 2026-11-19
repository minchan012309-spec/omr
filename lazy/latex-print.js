/* Only records explicitly marked xelatex-v1 enter this path. */
async function ltPageModel(element,assets,codes,kind){
 const clone=element.cloneNode(true);
 clone.querySelectorAll('.pg > .ph1,.pg > .ph2,.pg > .ft,.pg > .footer,.bp > .hd,.bp > .ft,.bp > .footer,.qrh,.bklg,.thr').forEach(n=>n.remove());
 const top=[...clone.querySelectorAll('.tp,.cntop')];const topNodes=[];for(const n of top){topNodes.push(...await SolviPrint.fragment(n.innerHTML,assets));n.remove()}
 const cols=[...clone.querySelectorAll('.cols>.col')];
 const content=cols.length?cols:[clone.querySelector('.bd')||clone];
 return {kind,codes,top:topNodes,columns:await Promise.all(content.slice(0,2).map(c=>SolviPrint.fragment(c.innerHTML,assets)))};
}
function ltBaseModel(rec){const c=rec.cover||{},opt=rec.latexOptions||{};
 return {templateVersion:rec.templateVersion||SolviPrint.TEMPLATE,publicBase:(CF.pub||location.origin+'/').split('#')[0].split('?')[0],title:opt.title||c.title||rec.title||rec.name||'학습 자료',name:rec.name||'',subjectId:SUBJ,subject:opt.subject||c.subject||SNAME[SUBJ],cover:{handwriting:opt.handwriting||'오늘의 배움을 내일의 실력으로',instructions:opt.instructions||'○ 답안지의 해당란에 성명과 수험번호를 쓰고, 답을 정확히 표시하시오.\n○ 단답형이 있는 경우 숫자 0도 답란에 반드시 표시하시오.\n○ 배점이 있는 문항은 물음 끝의 표시를 참고하시오.\n○ 계산은 문제지의 여백을 활용하시오.',organization:opt.organization||rec.academy||c.org||''},duplex:typeof dupGet==='function'&&dupGet(),assets:{},pages:[]};
}
function ltRanges(model){const labels={questions:'문제지',answers:'정답 및 해설',concept:'개념',contents:'차례',notes:'필기'};const lines=[];
 for(const [kind,label] of Object.entries(labels)){const ps=model.pages.flatMap((p,i)=>p.kind===kind?[i+1]:[]);if(ps.length)lines.push(label+' ··· '+ps[0]+'~'+ps.at(-1)+'쪽')}
 model.cover.ranges=lines.join('\n');
}
async function ltWorksheet(w,rec,root){
 const model=ltBaseModel(rec);model.material='worksheet';model.per=rec.per==='auto'||!rec.per?4:+rec.per;model.worksheetId=rec.id;model.questionKind=rec.codes.every(c=>{const host=document.createElement('div');host.innerHTML=byCode[c]?.q||'';return host.querySelector('.chs')?.children.length===5})?'5지선다형':'학습 문항';let qi=0;
 for(const pg of root.querySelectorAll('.pg')){
  if(pg.classList.contains('mcover')){model.pages.push({kind:'cover',codes:[],columns:[]});continue}
  if(pg.classList.contains('wblank')){model.pages.push({kind:'blank',codes:[],columns:[]});continue}
  const sol=pg.dataset.solviKind==='answers';const count=sol?0:pg.querySelectorAll('.wq').length;
  const codes=sol?[]:rec.codes.slice(qi,qi+count);if(!sol)[...pg.querySelectorAll('.wq')].forEach((el,i)=>el.dataset.c=codes[i]||'');qi+=count;
  model.pages.push(await ltPageModel(pg,model.assets,codes,sol?'answers':count?'questions':'concept'));
 }
 if(qi!==rec.codes.length&&rec.part!=='a')throw Error('문제 쪽과 문항 목록이 일치하지 않습니다');
 return ltViewer(w,model,rec,()=>{wsStore();if(srv==='cloud')wsPost(rec).catch(()=>{})});
}
async function ltBook(id,all,w){
 if(!await bkxAccess(id))return;
 w=w||popOpen('PDF를 준비하는 중…');
 try{await bkInit();const P=bkParts(id);if(P&&P.subj!==SUBJ)await setSubject(P.subj);const plan=await bkPlan(id);if(!plan)throw Error('교재를 찾지 못했습니다');
 const rec=bkxAll().find(b=>b.id===String(id).replace(/~g[1-3]$/,'').replace(/(~l[0-9a-f]{16})r\d+$/,'$1'));if(!rec)throw Error('새 교재 정의가 없습니다');
 const model=ltBaseModel({...rec,title:plan.title,name:''});model.material='book';model.bookId=id.replace(/~g[1-3]$/,'');model.contentsEntries=(plan.toc||[]).map(r=>({title:(r.sub?r.sub.k+' '+r.sub.name:r.title||''),items:(r.items||[]).map(x=>x[0])}));
 for(let i=0;i<plan.pages.length;i++){
  const pg=plan.pages[i];if(!all&&['ak','es'].includes(pg.k))continue;
  if(pg.k==='cover'||pg.k==='mcv'){model.pages.push({kind:'cover',codes:[],columns:[]});continue}
  if(pg.k==='back'){model.pages.push({kind:'back',codes:[],columns:[]});continue;}
  if(pg.k==='toc'){model.pages.push({kind:'contents',codes:[],columns:[]});continue;}
  if(pg.k==='nt'){model.pages.push({kind:'notes',codes:[],columns:[],noteStyle:pg.st||'lined',noteLabel:pg.label||'필기 노트'});continue;}
  const host=document.createElement('div');host.innerHTML=bkPageHtml(plan,i);
  const kind=pg.k==='cn'?'concept':pg.k==='toc'?'contents':pg.k==='nt'?'notes':['ak','es'].includes(pg.k)?'answers':'questions';
  model.pages.push(await ltPageModel(host,model.assets,kind==='questions'?pg.codes||[]:[],kind));
 }
 await ltViewer(w,model,rec,result=>{const items=bkxAll();const index=items.findIndex(b=>b.id===rec.id);if(index<0)throw Error('교재 저장 정보를 찾지 못했습니다');rec.latexOutputs=rec.latexOutputs||{};const outputs=rec.latexOutputs[id]=rec.latexOutputs[id]||{};outputs[all?'all':'questions']={id:rec.latexManifest,manifest:result.manifest};outputs.active=all?'all':'questions';rec.updatedAt=Date.now();items[index]=rec;bkxStore(items)});
 }catch(e){ltError(w,e)}
}
function ltError(w,e){if(w&&!w.closed){w.document.body.textContent=e?.message||'PDF 생성 실패';w.document.title='PDF 생성 실패'}else alert(e?.message||'PDF를 만들지 못했습니다')}
async function ltViewer(w,model,rec,save){
 if(!w)throw Error('PDF 창을 열 수 없습니다. 팝업을 허용한 뒤 다시 시도해 주세요');
 const doc=w.document;doc.open();doc.write('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PDF 출력</title><style>');
 doc.write('@font-face{font-family:Pretendard;src:url("'+new URL('fonts/Pretendard-Regular.woff2',location.href).href+'") }*{box-sizing:border-box}body{margin:0;background:#eef1f4;color:#182129;font:14px Pretendard,sans-serif}.layout{display:grid;grid-template-columns:280px 1fr;height:100dvh}aside{padding:24px;background:#fff;border-right:1px solid #dce2e7;overflow:auto}h1{font-size:19px;margin:0 0 24px}label{display:block;margin:16px 0 6px;font-size:13px}input,textarea,select,button{font:inherit;border:1px solid #c6d0d9;border-radius:7px;padding:10px;background:#fff;color:inherit}input,textarea,select{width:100%}textarea{min-height:90px;resize:vertical}button{cursor:pointer;width:100%;margin-top:14px;background:#173f66;color:#fff;border-color:#173f66}input[type=file]::file-selector-button{font:inherit;border:0;border-radius:4px;padding:6px 8px;margin-right:8px;background:#e8eef4;color:#173f66}button:disabled{opacity:.5;cursor:wait}.save{background:#fff;color:#173f66}.status{line-height:1.6;overflow-wrap:anywhere;margin:16px 0}iframe{width:100%;height:100%;border:0}main{min-width:0;position:relative}.skeleton{position:absolute;inset:24px;background:#fff;padding:12%;display:flex;flex-direction:column;gap:24px}.skeleton i{display:block;height:12px;background:#edf0f3}.skeleton i:nth-child(2){width:60%;margin-bottom:40px}.skeleton[hidden]{display:none}@media(max-width:700px){.layout{display:flex;flex-direction:column;height:auto}aside{border:0;padding:20px}main{height:80dvh}}');
 doc.write('</style><div class="layout"><aside><h1>출력 설정</h1><label for="fonts">원본 폰트 등록 (이 컴퓨터에 저장)</label><input id="fonts" type="file" multiple accept=".ttf,.otf"><form id="settings"><label for="title">제목</label><input id="title"><label for="subject">과목명</label><input id="subject"><label for="organization">학원·학교 이름</label><input id="organization"><label for="handwriting">필적확인 문구</label><input id="handwriting"><label for="instructions">유의사항</label><textarea id="instructions"></textarea><label for="cover">앞표지</label><select id="cover"><option value="1">넣기</option><option value="0">넣지 않기</option></select><button id="generate" type="submit">PDF 만들기</button></form><button class="save" id="cancel" disabled>생성 취소</button><p class="status" role="status" aria-live="polite" id="status">PDF를 준비합니다.</p><button class="save" id="download" disabled>PDF 저장</button></aside><main><div id="waiting" class="skeleton" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div><iframe title="인쇄용 PDF 미리보기" id="pdf"></iframe></main></div></html>');doc.close();
 const get=id=>doc.getElementById(id);get('fonts').onchange=async e=>{try{await SolviLocalTex.importFonts(e.target.files);get('status').textContent='원본 폰트를 등록했습니다. PDF 만들기를 눌러 주세요'}catch(err){get('status').textContent=err.message}};for(const k of ['title','subject'])get(k).value=model[k];for(const k of ['organization','handwriting','instructions'])get(k).value=model.cover[k];
 get('cover').value=(rec.latexOptions&&rec.latexOptions.coverOn!==undefined?rec.latexOptions.coverOn:model.pages.some(p=>p.kind==='cover'))?'1':'0';
 let blobUrl=null,generating=false;get('cancel').onclick=()=>SolviLocalTex.cancel();w.addEventListener('pagehide',()=>{if(generating)SolviLocalTex.cancel();if(blobUrl)URL.revokeObjectURL(blobUrl)},{once:true});
 const generate=async()=>{
  generating=true;get('waiting').hidden=false;get('pdf').hidden=true;get('cancel').disabled=false;get('generate').disabled=true;get('download').disabled=true;get('status').textContent='PDF를 만드는 중…';
  try{
   model.title=get('title').value;model.subject=get('subject').value;
   for(const k of ['organization','handwriting','instructions'])model.cover[k]=get(k).value;
   model.pages=model.pages.filter(p=>p.kind!=='cover');if(get('cover').value==='1')model.pages.unshift({kind:'cover',codes:[],columns:[]});ltRanges(model);
   const result=await SolviPrint.submit(model);
   rec.latexOptions={coverOn:get('cover').value==='1',title:model.title,subject:model.subject,...model.cover};rec.latexManifest=result.id;await save(result);
   if(blobUrl)URL.revokeObjectURL(blobUrl);blobUrl=URL.createObjectURL(result.blob);get('pdf').src=blobUrl;get('pdf').hidden=false;get('waiting').hidden=true;get('status').textContent=result.manifest.pages.length+'쪽 · PDF 생성 완료';get('download').disabled=false;
  }catch(e){get('status').textContent=e?.message||'PDF를 만들지 못했습니다'}finally{generating=false;get('waiting').hidden=true;if(blobUrl)get('pdf').hidden=false;get('cancel').disabled=true;get('generate').disabled=false}
 };
 get('settings').onsubmit=e=>{e.preventDefault();generate()};get('download').onclick=()=>{const a=doc.createElement('a');a.href=blobUrl;a.download=model.title.replace(/[\\/:*?"<>|]/g,' ')+'.pdf';a.click()};
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
