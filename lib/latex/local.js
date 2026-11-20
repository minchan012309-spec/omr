/* XeTeX and xdvipdfmx run only in the creator's browser workers. */
(function(g){'use strict';
const base=new URL('./',document.currentScript.src),names=['ShinMyeongjo.ttf','KoPubWorldBold.ttf','KoPubWorldMedium.ttf','HancomEQN.ttf'];
let active=null,pool=null,fontPromise=null,resourcePromise=null,optionalManifestPromise=null;
const optionalFontPromises=new Map(),queue=[];
let draining=false;
function hex(bytes){return Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('')}
async function sha(bytes){return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))}
async function manifest(){const response=await fetch(new URL('font-manifest.json',base));if(!response.ok)throw Error('폰트 기준 파일을 읽지 못했습니다');return response.json()}
async function fonts(){
 if(!fontPromise)fontPromise=(async()=>{const expected=await manifest();return Promise.all(names.map(async name=>{const response=await fetch(new URL('fonts/'+name,base));if(!response.ok)throw Error('원본 글꼴을 내려받지 못했습니다: '+name);const bytes=await response.arrayBuffer();if(await sha(bytes)!==expected[name])throw Error('원본과 다른 글꼴입니다: '+name);return bytes}))})().catch(e=>{fontPromise=null;throw e});
 return fontPromise;
}
/* Kept for callers that verify supplied originals; normal printing always uses hosted files. */
async function importFonts(files){const expected=await manifest();for(const file of files){if(file.size>30000000)throw Error('폰트 파일이 너무 큽니다');const digest=await sha(await file.arrayBuffer());if(!names.some(name=>expected[name]===digest))throw Error('지정 원본과 다른 폰트입니다: '+file.name)}await fonts();return names.length}
async function optionalFonts(requested){
 if(!Array.isArray(requested)||requested.some(name=>typeof name!=='string'||!/^[-A-Za-z0-9]+\.ttf$/.test(name)))throw Error('교재 글꼴 목록을 확인해 주세요');
 if(!requested.length)return [];
 if(!optionalManifestPromise)optionalManifestPromise=(async()=>{const response=await fetch(new URL('optional-font-manifest.json',base));if(!response.ok)throw Error('선택 글꼴 기준 파일을 읽지 못했습니다');return response.json()})().catch(e=>{optionalManifestPromise=null;throw e});
 const expected=await optionalManifestPromise;
 return Promise.all([...new Set(requested)].map(name=>{
  if(!Object.hasOwn(expected,name))throw Error('지원하지 않는 교재 글꼴입니다: '+name);
  if(!optionalFontPromises.has(name))optionalFontPromises.set(name,(async()=>{const file=await fetch(new URL('fonts/'+name,base));if(!file.ok)throw Error('선택 글꼴을 내려받지 못했습니다: '+name);const bytes=await file.arrayBuffer();if(await sha(bytes)!==expected[name])throw Error('원본과 다른 글꼴입니다: '+name);return {name,bytes}})().catch(e=>{optionalFontPromises.delete(name);throw e}));
  return optionalFontPromises.get(name);
 }));
}
async function resources(){
 if(!resourcePromise)resourcePromise=(async()=>{const [fontData,stixResponse,templateResponse]=await Promise.all([fonts(),fetch(new URL('STIXTwoMath-Regular.otf',base)),fetch(new URL('template.tex?v=4',base))]);if(!stixResponse.ok)throw Error('지정 수식 글꼴을 읽지 못했습니다');if(!templateResponse.ok)throw Error('양식을 읽지 못했습니다');return {fontData,stix:new Uint8Array(await stixResponse.arrayBuffer()),template:await templateResponse.text()}})().catch(e=>{resourcePromise=null;throw e});
 return resourcePromise;
}
function dispose(engines){if(!engines)return;for(const engine of engines)if(engine.latexWorker)engine.latexWorker.terminate();if(pool===engines)pool=null}
function cancelActive(job,message){if(active!==job)return;active=null;job.cancelled=true;dispose(job.engines);job.reject(Error(message))}
function cancel(message='PDF 생성을 취소했습니다',owner=null){
 for(let i=queue.length-1;i>=0;i--)if(owner===null||queue[i].owner===owner){const [request]=queue.splice(i,1);request.reject(Error(message))}
 if(active&&(owner===null||active.owner===owner))cancelActive(active,message);
}
async function drain(){
 if(draining)return;draining=true;
 try{while(queue.length){const request=queue.shift();try{request.resolve(await compileNow(request.model,request.owner))}catch(e){request.reject(e)}}}finally{draining=false}
}
function compile(model,owner=null){return new Promise((resolve,reject)=>{queue.push({model,owner,resolve,reject});drain()})}
function check(job){if(job.cancelled||active!==job)throw Error('PDF 생성을 취소했습니다')}
function pageQr(url){
 if(typeof qrcode!=='function')throw Error('QR 생성기를 불러오지 못했습니다');
 const qr=qrcode(0,'M');qr.addData(url);qr.make();
 const count=qr.getModuleCount(),quiet=4,scale=6,canvas=document.createElement('canvas');canvas.width=canvas.height=(count+quiet*2)*scale;
 const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.fillStyle='#000';
 for(let row=0;row<count;row++)for(let col=0;col<count;col++)if(qr.isDark(row,col))ctx.fillRect((col+quiet)*scale,(row+quiet)*scale,scale,scale);
 const bytes=Uint8Array.from(atob(canvas.toDataURL('image/png').split(',')[1]),c=>c.charCodeAt(0));canvas.width=canvas.height=0;return bytes;
}

async function compileNow(model,owner){
 const job={engines:null,cancelled:false,reject:null,owner};active=job;let timeout;
 const cancelled=new Promise((_,no)=>{job.reject=no;timeout=setTimeout(()=>cancelActive(job,'PDF 생성 시간이 초과되었습니다. 문항 수를 줄여 다시 시도해 주세요'),120000)});
 const work=async()=>{
  const {fontData,stix,template}=await resources();check(job);const requestedFonts=model.layout==='book-original-v1'?model.bookFonts:model.fontFamily==='pretendard'?['PretendardRegular.ttf','PretendardBold.ttf']:[];const extraFonts=await optionalFonts((requestedFonts||[]).filter(name=>!names.includes(name)));check(job);
  const reused=!!pool,engines=pool||[new XeTeXEngine(),new DvipdfmxEngine()];job.engines=engines;const [en,pdf]=engines;
  if(!reused){await Promise.all(engines.map(e=>e.loadEngine()));check(job);pool=engines;const endpoint=new URL('texlive/',base).href;for(const e of engines)e.setTexliveEndpoint(endpoint)}
  // Clear document files and auxiliary state while keeping loaded engines and TeX packages warm.
  for(const e of engines){e.latexWorker.postMessage({cmd:'flushcache'});e.makeMemFSFolder('fonts');for(let i=0;i<names.length;i++)e.writeMemFSFile('fonts/'+names[i],new Uint8Array(fontData[i]));for(const font of extraFonts)e.writeMemFSFile('fonts/'+font.name,new Uint8Array(font.bytes));e.writeMemFSFile('STIXTwoMath-Regular.otf',stix)}
  const id=hex(crypto.getRandomValues(new Uint8Array(16)));let source=SolviLatexDocument.render(model,id,template);
  for(const [name,data] of Object.entries(model.assets||{})){if(!/^a\d+\.png$/.test(name))throw Error('그림 경로 오류');const bytes=Uint8Array.from(atob(data),c=>c.charCodeAt(0));en.writeMemFSFile(name,bytes);pdf.writeMemFSFile(name,bytes)}
  en.setEngineMainFile('main.tex');let tex,manifest,settled=false,qrCount=0;
  for(let pass=0;pass<3;pass++){
   en.writeMemFSFile('main.tex',source);tex=await en.compileLaTeX();check(job);if(tex.status!==0||!tex.pdf)break;
   manifest=SolviLatexDocument.pageManifest(model,tex.log);const ranges=SolviLatexDocument.coverRanges(manifest);
   const measured=Object.fromEntries([...tex.log.matchAll(/SOLVIMEASURE:([-A-Za-z0-9_.~]+):([\d.]+)pt/g)].map(m=>[m[1],Math.round(+m[2]/2.8452755906*1000)/1000]));const layoutChanged=Object.keys(measured).length&&JSON.stringify(measured)!==JSON.stringify(model.unitHeights);if(Object.keys(measured).length)model.unitHeights=measured;
   // A geometry-identical placeholder on pass one reveals physical page numbers cheaply.
   // PNGs then replace it on every final page, without running TeX's QR calculations.
   const addedQr=manifest.pages.length>qrCount;
   for(let page=qrCount+1;page<=manifest.pages.length;page++){const bytes=pageQr(model.publicBase+'#lt='+id+':'+page);for(const e of engines)e.writeMemFSFile('qr'+page+'.png',bytes)}
   qrCount=Math.max(qrCount,manifest.pages.length);
   const oldRanges=model.cover&&model.cover.ranges||'',oldContents=model.contentsRanges||'';
   model.cover=model.cover||{};model.cover.ranges=ranges;model.contentsRanges=ranges;
   if(pass>0&&!layoutChanged&&!addedQr&&ranges===oldRanges&&ranges===oldContents){settled=true;break}
   source=SolviLatexDocument.render(model,id,template);
  }
  if(tex.status!==0||!tex.pdf){if(tex.log.includes('SOLVI COLUMN OVERFLOW'))throw Error('문항이 쪽 높이를 넘습니다. 문항 수를 줄이거나 쪽 나눔을 조정해 주세요');const missing=/File [`']([^`']+)' not found/.exec(tex.log);throw Error(missing?'필요한 조판 파일: '+missing[1]:'LaTeX 조판에 실패했습니다. 문항의 수식과 배치를 확인해 주세요')}
  if(/Overfull \\[hv]box/.test(tex.log))throw Error('내용이 인쇄 영역을 넘습니다. 문항 배치를 조정해 주세요');
  if(!settled)throw Error('쪽 번호가 안정되지 않았습니다. 문항 배치를 조정해 다시 시도해 주세요');manifest=SolviLatexDocument.pageManifest(model,tex.log);pdf.writeMemFSFile('main.xdv',tex.pdf);pdf.setEngineMainFile('main.xdv');const result=await pdf.compilePDF();check(job);if(result.status!==0||!result.pdf)throw Error('PDF 변환에 실패했습니다');
  const digest=await sha(result.pdf);check(job);
  return {id,manifest,sha256:digest,blob:new Blob([result.pdf],{type:'application/pdf'})};
 };
 try{return await Promise.race([work(),cancelled])}catch(e){dispose(job.engines);throw e}finally{clearTimeout(timeout);if(active===job)active=null}
}
const persisted=new WeakMap();
async function persist(result){
 if(!result||!result.blob||!/^[a-f0-9]{32}$/.test(result.id))throw Error('저장할 PDF가 없습니다');
 if(!persisted.has(result))persisted.set(result,(async()=>{if(typeof rpc!=='function')throw Error('QR 자료 저장 연결을 확인해 주세요');const stored=await rpc('latex_manifest_create',{p_id:result.id,p_manifest:result.manifest,p_digest:result.sha256});if(!stored.ok)throw Error('QR 정보를 저장하지 못했습니다. 연결을 확인한 뒤 다시 저장해 주세요');return result})().catch(e=>{persisted.delete(result);throw e}));
 return persisted.get(result);
}
function release(){if(!active)dispose(pool)}
g.SolviLocalTex={compile,cancel,persist,release,importFonts,imported:fonts};
})(globalThis);
