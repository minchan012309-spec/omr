/* Original book page geometry, with selectable native PDF text over artwork. */
(function(g){'use strict';
const MM=25.4/96;
const WEIGHTS=[[400,'Regular'],[500,'Medium'],[600,'SemiBold'],[700,'Bold'],[800,'ExtraBold'],[900,'Black']];
function weightName(value){const w=Number(value)||400;return WEIGHTS.reduce((a,b)=>Math.abs(b[0]-w)<Math.abs(a[0]-w)?b:a)[1]}
function fontFile(style,character,extra){
 const families=style.fontFamily.split(',').map(s=>s.trim().replace(/^['"]|['"]$/g,''));
 if(families.includes('YetHangul')&&/[\u1100-\u11ff\ua960-\ua97f\ud7b0-\ud7ff\u3165-\u318e\u302e-\u302f]/u.test(character))return 'KoPubDotum'+(Number(style.fontWeight)>=700?'Bold':'Medium')+'Subset.ttf';
 if(families.includes('SolviCn')&&/[①-⑳]/u.test(character))return 'PretendardLightCn.ttf';
 if(families.includes('SolviSymbols')&&/[\u2300-\u24ff\u3200-\u32ff]/u.test(character))return 'SolviSymbols.ttf';
 const family=families.find(f=>!['YetHangul','SolviSymbols','SolviCn'].includes(f));
 if(/^[∧∨¬→⇒≤≥≠±×÷∈∉∑∏∫√∞⊂⊆⋅]$/u.test(character))return 'HancomEQN.ttf';
 const w=weightName(style.fontWeight);
 if(family==='Pretendard'||family==='PretendardLocal')return 'Pretendard'+(w==='Black'?'ExtraBold':w)+'.ttf';
 if(family==='Paperozi')return 'Paperlogy'+(w==='SemiBold'?'Bold':w)+'.ttf';
 if(extra&&extra[family])return extra[family];
 throw Error('기존 교재 글꼴의 원본 TTF가 필요합니다: '+family+' ('+style.fontWeight+')');
}
function visible(el,win){for(let p=el;p&&p.nodeType===1;p=p.parentElement){const s=win.getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return false}return true}
function rasterText(el,root,win){
 if(el.closest('svg,math,canvas,script,style,.qq'))return true;
 for(let p=el;p&&p!==root;p=p.parentElement){const s=win.getComputedStyle(p);if(s.transform!=='none'||s.writingMode!=='horizontal-tb')return true}
 // Embedded formula and italic serif fragments retain their original glyphs in artwork.
 return /Times New Roman|Noto Serif|(^|,)\s*serif\s*(,|$)/.test(win.getComputedStyle(el).fontFamily);
}
function rgba(s){const a=s.match(/[\d.]+/g);if(!a||a.length<3)return {color:'000000',alpha:1};return {color:a.slice(0,3).map(v=>Math.max(0,Math.min(255,Math.round(+v))).toString(16).padStart(2,'0')).join('').toUpperCase(),alpha:a[3]===undefined?1:+a[3]}}
function textRuns(root,options){
 const doc=root.ownerDocument,win=doc.defaultView,rect=root.getBoundingClientRect(),walker=doc.createTreeWalker(root,4),canvas=doc.createElement('canvas'),ctx=canvas.getContext('2d'),runs=[],owners=new Set(),fonts=new Set();
 const segmenter=typeof Intl.Segmenter==='function'?new Intl.Segmenter('ko',{granularity:'grapheme'}):null;
 let node;while((node=walker.nextNode())){
  const el=node.parentElement;if(!node.data.trim()||!visible(el,win)||rasterText(el,root,win))continue;
  const s=win.getComputedStyle(el),size=parseFloat(s.fontSize),paint=rgba(s.color);for(let parent=el;parent&&parent!==root;parent=parent.parentElement)paint.alpha*=Number(win.getComputedStyle(parent).opacity);if(!size||paint.alpha===0)continue;
  ctx.font=s.fontStyle+' '+s.fontWeight+' '+s.fontSize+' '+s.fontFamily;const metrics=ctx.measureText('Hg가');
  const ascent=metrics.fontBoundingBoxAscent||size*.9;
  const pieces=segmenter?[...segmenter.segment(node.data)].map(x=>({text:x.segment,index:x.index})):[...node.data].map((text,index)=>({text,index}));
  let current=null;
  for(const part of pieces){
   const range=doc.createRange();range.setStart(node,part.index);range.setEnd(node,part.index+part.text.length);const boxes=range.getClientRects();const box=boxes.length?boxes[boxes.length-1]:null;
   if(!box||!box.width||box.bottom<=rect.top||box.top>=rect.bottom||box.right<=rect.left||box.left>=rect.right){current=null;continue}
   let value=part.text;if(s.textTransform==='uppercase')value=value.toUpperCase();if(s.textTransform==='lowercase')value=value.toLowerCase();if(/[\r\n\t]/.test(value)){current=null;continue}
   const file=fontFile(s,value,options.fontMap),x=(box.left-rect.left)*MM,y=(box.top-rect.top+ascent)*MM,w=box.width*MM;
   fonts.add(file);owners.add(el);
   if(current&&current.fontFile===file&&Math.abs(current.y-y)<.03&&Math.abs(current.x+current.width-x)<.04){current.text+=value;current.width=x+w-current.x}
   else {current={text:value,x,y,width:w,fontFile:file,fontSize:size*.75,color:paint.color,alpha:paint.alpha,italic:s.fontStyle==='italic'};runs.push(current)}
  }
 }
 let index=0;for(const el of owners)el.setAttribute('data-bk-native',String(index++));
 return {runs,fonts:[...fonts]};
}
function kind(pg){return pg.k==='cover'||pg.k==='mcv'?'cover':pg.k==='back'?'back':pg.k==='toc'?'contents':pg.k==='nt'?'notes':pg.k==='cn'?'concept':['ak','es'].includes(pg.k)?'answers':'questions'}
async function mathRuns(root){
 const rect=root.getBoundingClientRect(),win=root.ownerDocument.defaultView,items=[];
 for(const el of root.querySelectorAll('math')){
  if(el.parentElement?.closest('math')||!visible(el,win))continue;
  const style=win.getComputedStyle(el),probe=root.ownerDocument.createElementNS('http://www.w3.org/1998/Math/MathML','mspace');probe.setAttribute('width','0px');probe.setAttribute('height','0px');probe.setAttribute('depth','0px');el.appendChild(probe);
  const boxes=[...el.children].filter(c=>c!==probe).map(c=>c.getBoundingClientRect()).filter(b=>b.width&&b.height),outer=el.getBoundingClientRect(),baseline=probe.getBoundingClientRect().top;probe.remove();const box=boxes.length?{left:Math.min(...boxes.map(b=>b.left)),top:Math.min(...boxes.map(b=>b.top)),width:Math.max(...boxes.map(b=>b.right))-Math.min(...boxes.map(b=>b.left)),height:Math.max(...boxes.map(b=>b.bottom))-Math.min(...boxes.map(b=>b.top))}:outer;if(!box.width||!box.height)continue;
  const formula=await SolviPrint.ast(el,{});items.push({x:(box.left-rect.left)*MM,y:(baseline-rect.top)*MM,width:box.width*MM,height:box.height*MM,fontSize:parseFloat(style.fontSize)*.75,color:rgba(style.color).color,display:el.getAttribute('display')==='block',formula});el.setAttribute('data-bk-math','');
 }
 return items;
}
async function capturePage(root,options={}){
 const win=root.ownerDocument.defaultView,rect=root.getBoundingClientRect(),data=textRuns(root,options),math=await mathRuns(root),qrs=[];
 for(const qr of root.querySelectorAll('.qq')){const b=qr.getBoundingClientRect();qrs.push({x:(b.left-rect.left)*MM,y:(b.top-rect.top)*MM,width:b.width*MM,height:b.height*MM});qr.setAttribute('data-bk-qr','')}
 const h2c=options.html2canvas||g.html2canvas;if(typeof h2c!=='function')throw Error('교재 그림 라이브러리를 불러오지 못했습니다');
 const cv=await h2c(root,{scale:options.scale||1.7,backgroundColor:'#ffffff',useCORS:true,logging:false,onclone(doc){
  // Freeze decorative colors before clearing the text paint. Borders, backgrounds,
  // SVG artwork and mathematical fragments remain the original browser rendering.
  const css=[];let i=0;
  for(const el of doc.querySelectorAll('[data-bk-native]')){
   const st=doc.defaultView.getComputedStyle(el);el.style.borderTopColor=st.borderTopColor;el.style.borderRightColor=st.borderRightColor;el.style.borderBottomColor=st.borderBottomColor;el.style.borderLeftColor=st.borderLeftColor;el.style.textDecorationColor=st.textDecorationColor;el.style.backgroundColor=st.backgroundColor;
   for(const pseudo of ['::before','::after']){const ps=doc.defaultView.getComputedStyle(el,pseudo);if(ps.content&&ps.content!=='none')css.push('[data-bk-native="'+el.getAttribute('data-bk-native')+'"]'+pseudo+'{color:'+ps.color+'!important}')}
   // A raster text child may inherit its parent's color; lock it first.
   for(const child of el.children){const cs=doc.defaultView.getComputedStyle(child);child.style.setProperty('color',cs.color,'important')}
   el.style.setProperty('color','transparent','important');el.style.setProperty('text-shadow','none','important');i++;
  }
  for(const el of doc.querySelectorAll('[data-bk-math]'))el.style.visibility='hidden';
  for(const el of doc.querySelectorAll('[data-bk-qr]'))el.style.visibility='hidden';
  const style=doc.createElement('style');style.textContent=css.join('\n');doc.head.appendChild(style);
 }});
 // Match translucent ink against the already captured decoration beneath it.
 const pixels=cv.getContext('2d');for(const run of data.runs)if(run.alpha<1){const x=Math.max(0,Math.min(cv.width-1,Math.round((run.x+run.width/2)/210*cv.width))),y=Math.max(0,Math.min(cv.height-1,Math.round((run.y-run.fontSize*.12)/297*cv.height))),bg=pixels.getImageData(x,y,1,1).data;run.color=[0,1,2].map(i=>Math.round(parseInt(run.color.slice(i*2,i*2+2),16)*run.alpha+bg[i]*(1-run.alpha)).toString(16).padStart(2,'0')).join('').toUpperCase()}
 const background=cv.toDataURL('image/png').split(',')[1];cv.width=cv.height=0;
 for(const el of root.querySelectorAll('[data-bk-native]'))el.removeAttribute('data-bk-native');
 for(const el of root.querySelectorAll('[data-bk-qr]'))el.removeAttribute('data-bk-qr');
 return {drawing:{width:210,height:297,text:data.runs,math,qrs},background,fonts:data.fonts};
}
async function capture(plan,all,options={}){
 if(!plan||!Array.isArray(plan.pages))throw Error('교재 쪽 정보를 확인해 주세요');
 if(!g.html2canvas&&typeof bkLoadJs==='function')await bkLoadJs('lib/html2canvas.min.js',()=>g.html2canvas);
 const frame=document.createElement('iframe');frame.setAttribute('aria-hidden','true');frame.style.cssText='position:fixed;left:-1200px;top:0;width:820px;height:1200px;border:0;pointer-events:none';
 const ready=new Promise((resolve,reject)=>{frame.onload=resolve;frame.onerror=reject});frame.srcdoc=bkDocHtml(plan,all);document.body.appendChild(frame);
 try{
  await ready;const doc=frame.contentDocument;const printStyle=doc.createElement('style');printStyle.textContent='@font-face{font-family:LatinModernMath;src:url("'+new URL('fonts/LatinModernMath.woff2',location.href).href+'")}math,math *,.mx{font-family:LatinModernMath!important}.bkdoc .ft .qq,.bkdoc .fb .qq,.bkdoc .fq{width:20mm!important;height:20mm!important}.bkdoc .fq{bottom:7mm!important}';doc.head.appendChild(printStyle);await doc.fonts.load('16px LatinModernMath');await doc.fonts.ready;
  await Promise.all([...doc.images].map(im=>im.complete?Promise.resolve():new Promise(resolve=>{im.onload=im.onerror=resolve;setTimeout(resolve,8000)})));
  const elements=[...doc.querySelectorAll('.bp')],sheets=bkSheets(plan,all),model={layout:'book-original-v1',title:plan.title,material:'book',bookId:plan.id,assets:{},pages:[],bookFonts:[]};
  if(elements.length!==sheets.length)throw Error('기존 교재의 쪽 나눔과 출력 쪽 수가 다릅니다');
  for(let i=0;i<elements.length;i++){
   options.onProgress?.(i+1,elements.length);const result=await capturePage(elements[i],options),pg=sheets[i]<0?null:plan.pages[sheets[i]],name='a'+i+'.png',k=pg?kind(pg):'blank';
   model.assets[name]=result.background;model.bookFonts.push(...result.fonts);model.pages.push({kind:k,codes:k==='questions'?(pg.codes||[]):[],nums:pg&&typeof bkPageNums==='function'?bkPageNums(pg):{},originalPage:pg?.n||0,drawing:{...result.drawing,background:name}});
   await new Promise(resolve=>setTimeout(resolve,0));
  }
  model.bookFonts=[...new Set(model.bookFonts)];return model;
 }finally{frame.remove()}
}
g.SolviLatexBookLayout={capture,capturePage,fontFile};
})(globalThis);
