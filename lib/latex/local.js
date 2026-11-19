/* XeTeX and xdvipdfmx run only in the creator's browser workers. */
(function(g){'use strict';
const base=new URL('./',document.currentScript.src),names=['ShinMyeongjo.ttf','KoPubWorldBold.ttf','KoPubWorldMedium.ttf','HancomEQN.ttf'];
let active=null,activeReject=null;
function hex(bytes){return Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('')}
async function sha(bytes){return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))}
async function db(){return new Promise((ok,no)=>{const r=indexedDB.open('solvi-latex-fonts-v1',1);r.onupgradeneeded=()=>r.result.createObjectStore('fonts');r.onsuccess=()=>ok(r.result);r.onerror=()=>no(Error('이 브라우저에 폰트를 저장할 수 없습니다'))})}
async function imported(){const d=await db();try{return await Promise.all(names.map(name=>new Promise((ok,no)=>{const r=d.transaction('fonts').objectStore('fonts').get(name);r.onsuccess=()=>ok(r.result);r.onerror=no})))}finally{d.close()}}
async function importFonts(files){const response=await fetch(new URL('font-manifest.json',base));if(!response.ok)throw Error('폰트 기준 파일을 읽지 못했습니다');const expected=await response.json(),found=[];
 for(const file of files){if(file.size>30000000)throw Error('폰트 파일이 너무 큽니다');const bytes=await file.arrayBuffer(),digest=await sha(bytes),name=names.find(k=>expected[k]===digest);if(!name)throw Error('지정 원본과 다른 폰트입니다: '+file.name);found.push([name,bytes])}
 const d=await db();try{await new Promise((ok,no)=>{const tx=d.transaction('fonts','readwrite');for(const [name,bytes] of found)tx.objectStore('fonts').put(bytes,name);tx.oncomplete=ok;tx.onerror=()=>no(Error('폰트를 저장하지 못했습니다'))})}finally{d.close()}
 const loaded=await imported(),missing=names.filter((n,i)=>!loaded[i]);if(missing.length)throw Error('추가로 필요한 폰트: '+missing.join(', '));return names.length;
}
function cancel(message='PDF 생성을 취소했습니다'){if(active){for(const engine of active)if(engine.latexWorker)engine.latexWorker.terminate();active=null}const reject=activeReject;activeReject=null;if(reject)reject(Error(message))}
async function compile(model){
 if(active)throw Error('이미 PDF를 만드는 중입니다');
 const fontData=await imported(),missing=names.filter((name,i)=>!fontData[i]);if(missing.length)throw Error('이 컴퓨터에 원본 폰트를 등록해 주세요: '+missing.join(', '));
 if(active)throw Error('이미 PDF를 만드는 중입니다');const en=new XeTeXEngine(),pdf=new DvipdfmxEngine(),engines=[en,pdf];active=engines;let timeout;
 const work=async()=>{
  await en.loadEngine();await pdf.loadEngine();
  const endpoint=new URL('texlive/',base).href;en.setTexliveEndpoint(endpoint);pdf.setTexliveEndpoint(endpoint);
  en.makeMemFSFolder('fonts');pdf.makeMemFSFolder('fonts');
  for(let i=0;i<names.length;i++){en.writeMemFSFile('fonts/'+names[i],new Uint8Array(fontData[i]));pdf.writeMemFSFile('fonts/'+names[i],new Uint8Array(fontData[i]))}
  const stixResponse=await fetch(new URL('STIXTwoMath-Regular.otf',base));if(!stixResponse.ok)throw Error('지정 수식 글꼴을 읽지 못했습니다');const stix=new Uint8Array(await stixResponse.arrayBuffer());en.writeMemFSFile('STIXTwoMath-Regular.otf',stix);pdf.writeMemFSFile('STIXTwoMath-Regular.otf',stix);
  const templateResponse=await fetch(new URL('template.tex',base));if(!templateResponse.ok)throw Error('양식을 읽지 못했습니다');const template=await templateResponse.text();
  const id=hex(crypto.getRandomValues(new Uint8Array(16)));let source=SolviLatexDocument.render(model,id,template);
  for(const [name,data] of Object.entries(model.assets||{})){if(!/^a\d+\.png$/.test(name))throw Error('그림 경로 오류');const bytes=Uint8Array.from(atob(data),c=>c.charCodeAt(0));en.writeMemFSFile(name,bytes);pdf.writeMemFSFile(name,bytes)}
  en.setEngineMainFile('main.tex');let tex,manifest,settled=false;
  for(let pass=0;pass<3;pass++){
   en.writeMemFSFile('main.tex',source);tex=await en.compileLaTeX();if(tex.status!==0||!tex.pdf)break;
   manifest=SolviLatexDocument.pageManifest(model,tex.log);const ranges=SolviLatexDocument.coverRanges(manifest);
   const oldRanges=model.cover&&model.cover.ranges||'',oldContents=model.contentsRanges||'';
   model.cover=model.cover||{};model.cover.ranges=ranges;model.contentsRanges=ranges;
   if(pass>0&&ranges===oldRanges&&ranges===oldContents){settled=true;break}
   source=SolviLatexDocument.render(model,id,template);
  }

  if(tex.status!==0||!tex.pdf){if(tex.log.includes('SOLVI COLUMN OVERFLOW'))throw Error('문항이 쪽 높이를 넘습니다. 문항 수를 줄이거나 쪽 나눔을 조정해 주세요');const missing=/File [`']([^`']+)' not found/.exec(tex.log);throw Error(missing?'필요한 조판 파일: '+missing[1]:'LaTeX 조판에 실패했습니다. 문항의 수식과 배치를 확인해 주세요')}
  if(/Overfull \\[hv]box/.test(tex.log))throw Error('내용이 인쇄 영역을 넘습니다. 문항 배치를 조정해 주세요');
  if(!settled)throw Error('쪽 번호가 안정되지 않았습니다. 문항 배치를 조정해 다시 시도해 주세요');manifest=SolviLatexDocument.pageManifest(model,tex.log);pdf.writeMemFSFile('main.xdv',tex.pdf);pdf.setEngineMainFile('main.xdv');const result=await pdf.compilePDF();if(result.status!==0||!result.pdf)throw Error('PDF 변환에 실패했습니다');
  const digest=await sha(result.pdf);
  if(typeof rpc!=='function')throw Error('QR 자료 저장 연결을 확인해 주세요');
  const stored=await rpc('latex_manifest_create',{p_id:id,p_manifest:manifest,p_digest:digest});if(!stored.ok)throw Error('PDF는 생성했지만 QR 정보를 저장하지 못했습니다. Supabase에 LaTeX 자료 저장 설정을 적용해 주세요');
  return {id,manifest,sha256:digest,blob:new Blob([result.pdf],{type:'application/pdf'})};
 };
 try{return await Promise.race([work(),new Promise((_,no)=>{activeReject=no;timeout=setTimeout(()=>cancel('PDF 생성 시간이 초과되었습니다. 문항 수를 줄여 다시 시도해 주세요'),120000)})])}finally{clearTimeout(timeout);for(const e of engines)if(e.latexWorker)e.latexWorker.terminate();if(active===engines){active=null;activeReject=null}}
}
g.SolviLocalTex={compile,cancel,importFonts,imported};
})(globalThis);
