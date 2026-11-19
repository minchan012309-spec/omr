/* Version is persisted on creation; absence always means legacy HTML. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.SolviPrint=api})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const ENGINE='xelatex-v1',TEMPLATE='haewon-2026-v1';
function engine(record){const v=record&&record.printEngine;if(!v||v==='html')return 'html';if(v!==ENGINE)throw Error('지원하지 않는 출력 방식입니다');return v}
function fresh(){return {printEngine:ENGINE,templateVersion:TEMPLATE}}
function bookId(id){return id+'~l'+Array.from(crypto.getRandomValues(new Uint8Array(8)),x=>x.toString(16).padStart(2,'0')).join('')}
function sourceBookId(id){return String(id).replace(/~l[0-9a-f]{16}/,'')}

async function imageAsset(element,assets){
 let url,revoke=false;
 if(element.localName==='svg'){
  const copy=element.cloneNode(true);copy.setAttribute('xmlns','http://www.w3.org/2000/svg');
  if(copy.querySelector('script,foreignObject,image[href^="http"],image[href^="file"]'))throw Error('지원하지 않는 SVG 그림입니다');
  const vb=element.viewBox&&element.viewBox.baseVal;copy.setAttribute('width',String(vb&&vb.width||element.width.baseVal.value||640));copy.setAttribute('height',String(vb&&vb.height||element.height.baseVal.value||400));
  url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(copy)],{type:'image/svg+xml'}));revoke=true;
 }else{url=element.currentSrc||element.src;if(!url)throw Error('그림 주소가 없습니다');const parsed=new URL(url,location.href);if(!['data:','blob:'].includes(parsed.protocol)&&parsed.origin!==location.origin&&!(typeof CF!=='undefined'&&CF.url&&parsed.origin===new URL(CF.url).origin))throw Error('같은 사이트의 그림만 사용할 수 있습니다')}
 try{const im=new Image();im.crossOrigin='anonymous';await new Promise((ok,no)=>{im.onload=ok;im.onerror=()=>no(Error('그림을 읽지 못했습니다'));im.src=url});
 if(!im.naturalWidth||im.naturalWidth*im.naturalHeight>20000000)throw Error('그림 크기 한도');
 const canvas=document.createElement('canvas');const scale=element.localName==='svg'&&im.naturalWidth*im.naturalHeight<=5000000?2:1;canvas.width=im.naturalWidth*scale;canvas.height=im.naturalHeight*scale;const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(im,0,0,canvas.width,canvas.height);
 const name='a'+Object.keys(assets).length+'.png';assets[name]=canvas.toDataURL('image/png').split(',')[1];canvas.width=canvas.height=0;return {tag:'img',asset:name};
 }finally{if(revoke)URL.revokeObjectURL(url)}
}
const ALLOWED=new Set('span div section article small label p li b strong i em u sub sup br hr h1 h2 h3 h4 h5 h6 ul ol table thead tbody tfoot tr td th caption a figure figcaption s colgroup col math mrow mi mn mo mtext mfrac msup msub msubsup msqrt mroot mover munder munderover mtable mtr mtd mspace mstyle mpadded mfenced'.split(' '));
async function ast(element,assets){
 if(element.nodeType===3)return {tag:'span',text:element.textContent};
 if(element.nodeType!==1)return null;
 const tag=element.localName.toLowerCase();
 if(tag==='svg'||tag==='img')return imageAsset(element,assets);
 if(!ALLOWED.has(tag))throw Error('지원하지 않는 문서 요소: '+tag);
 if(element.classList.contains('clp')){const child=element.firstElementChild;if(!child)return null;if(parseFloat(child.style.marginTop)<0)return null;return ast(child,assets)}
 if(tag==='colgroup'||tag==='col'||element.matches('.bogi > .bt,.tgs,.qh,.qh2,.no,.qc,.cd,.nc'))return null;
 const out={tag,children:[]};if(element.style.textDecoration?.includes('underline')||element.style.borderBottom)out.tag='u';if(element.dataset.c){out.tag='unit';out.code=element.dataset.c;const number=element.querySelector('.no,.qn,.nc > b')?.textContent.match(/\d+/);if(number)out.number=+number[0];out.keep=element.dataset.solviRole!=='answer';out.role=element.dataset.solviRole||'';if(element.dataset.solviNumber)out.number=+element.dataset.solviNumber;if(element.dataset.solviAnswer)out.answer=element.dataset.solviAnswer;const q=typeof byCode!=='undefined'?byCode[out.code]:null;if(q){out.type=q.type||'';out.points=element.querySelector('.qp,.pt')?.textContent||'';}}if(element.classList.contains('fr'))out.tag='fraction';else if(element.classList.contains('chs')){out.tag='choices-list';out.layout=element.classList.contains('v')?'vertical':'auto';}else if(element.classList.contains('ws-quick'))out.tag='quick-answers';else if(element.classList.contains('ws-quick-title'))out.tag='quick-title';else if(element.classList.contains('key')||element.classList.contains('kg'))out.tag='answer-grid';else if(element.classList.contains('qn'))out.tag='question-number';else if(element.classList.contains('qp'))out.tag='points';else if(element.classList.contains('qh')||element.classList.contains('qh2'))out.tag='question-head';else if(element.classList.contains('bogi')){out.tag='bogi';out.title=element.querySelector(':scope > .bt')?.textContent.trim()||'보기';}else if(element.classList.contains('psg')){out.tag='passage';out.group=element.dataset.g||'';const head=element.querySelector(':scope > .hd');if(head)out.heading=await ast(head,assets);}else if(element.classList.contains('rng'))out.tag='u';else if(element.classList.contains('q')&&!out.code)out.tag='question';
 for(const key of ['colspan','rowspan'])if(element.hasAttribute(key))out[key]=+element.getAttribute(key);
 for(const key of ['open','close'])if(element.hasAttribute(key))out[key]=element.getAttribute(key);
 if(!element.childElementCount){out.text=element.textContent;return out;}
 for(const child of element.childNodes){if(out.tag==='passage'&&child.nodeType===1&&child.classList.contains('hd'))continue;if(child.nodeType===3&&!child.textContent.trim()&&(element.namespaceURI==='http://www.w3.org/1998/Math/MathML'||['table','thead','tbody','tfoot','tr','ul','ol'].includes(tag)||['choices-list','answer-grid','fraction'].includes(out.tag)))continue;const converted=await ast(child,assets);if(converted)out.children.push(converted)}
 return out;
}
async function fragment(html,assets){const host=document.createElement('div');host.innerHTML=html;const out=[];for(const child of host.childNodes){const n=await ast(child,assets);if(n)out.push(n)}return out}
async function submit(model,owner){if(!globalThis.SolviLocalTex)throw Error('브라우저 조판 엔진을 불러오지 못했습니다');return globalThis.SolviLocalTex.compile(model,owner)}
async function lookup(id){if(!/^[a-f0-9]{32}$/.test(id))throw Error('채점 자료 번호 오류');const response=await rpc('latex_manifest_read',{p_id:id});if(!response.ok)throw Error('PDF 채점 자료를 찾지 못했습니다');const result=await response.json();if(!result)throw Error('PDF 채점 자료를 찾지 못했습니다');return result}

return {ENGINE,TEMPLATE,engine,fresh,bookId,sourceBookId,ast,fragment,submit,lookup};
});
