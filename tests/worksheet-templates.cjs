/* 학습지 시안: 머리말·라벨이 두 줄로 넘치거나, 문장 끝 한두 글자만 다음 줄로 떨어지거나, 단이 넘치면 실패 */
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const b=await chromium.launch(browserOptions());
for(const vw of [1440,390]){const p=await b.newPage({viewport:{width:vw,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto((process.env.BASE||'http://127.0.0.1:8765')+'/design/worksheet-templates/');await p.waitForTimeout(1500);
const r=await p.evaluate(async()=>{const out=[];
 const lines=el=>{const tops=new Map();const tw=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let n;const rs=[];while(n=tw.nextNode()){if(n.parentElement.closest('.cond,.fr'))continue;const rg=document.createRange();rg.selectNodeContents(n);rs.push(...rg.getClientRects())}const L=[];for(const r of rs.filter(r=>r.width>=1).sort((a,b)=>a.top-b.top)){const m=(r.top+r.bottom)/2;const l=L.find(x=>m>x.t&&m<x.b);if(l){l.w+=r.width;l.t=Math.min(l.t,r.top);l.b=Math.max(l.b,r.bottom)}else L.push({t:r.top,b:r.bottom,w:r.width})}return L.map(x=>x.w)};
 // 갤러리 이름
 document.querySelectorAll('.cap').forEach(c=>{if(c.scrollWidth>c.clientWidth+1||lines(c.querySelector('span')).length>1)out.push('gallery-cap '+c.textContent)});
 for(let i=0;i<WT.T.length;i++){const t=WT.T[i];const host=document.createElement('div');document.body.appendChild(host);WT.apply(t,host);WT.build(t,host,{long:1});
  const fs=parseFloat(getComputedStyle(host).fontSize);
  host.querySelectorAll('header *:not(.stat *):not(.wk):not(li), footer *, .n:not(.n-level), .tl, .bx .bt, .psg-h, .ch-row span, .run').forEach(el=>{if(![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))return;const L=lines(el);if(L.length>1)out.push(t.id+' 두줄 '+el.className+' "'+el.textContent.trim().slice(0,20)+'"');if(el.scrollWidth>el.clientWidth+1&&getComputedStyle(el).overflow!=='visible')out.push(t.id+' 잘림 '+el.textContent.trim().slice(0,20))});
  host.querySelectorAll('header').forEach(h=>{if(h.scrollWidth>h.clientWidth+1)out.push(t.id+' 머리말 넘침')});
  host.querySelectorAll('.qt, .ch-stack span, .bx p, .psg p').forEach(el=>{const L=lines(el);if(L.length>1&&L[L.length-1]<fs*(el.matches('.psg p')?1.6:2.6))out.push(t.id+' 외톨이 "'+el.textContent.trim().slice(-8)+'"')});
  host.querySelectorAll('.col').forEach(c=>{if(c.scrollHeight>c.clientHeight+1)out.push(t.id+' 단 넘침')});
  host.remove()}
 return out});
assert.deepEqual(errs,[]);assert.deepEqual(r,[],vw+'px: '+r.slice(0,10).join(' | '));await p.close()}
await b.close();console.log('PASS 학습지 시안 43개 줄넘김 · 외톨이 글자 · 단 넘침 없음 (1440 · 390)')})().catch(e=>{console.error(e.message);process.exit(1)});
