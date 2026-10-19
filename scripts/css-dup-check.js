#!/usr/bin/env node
/* 전역 CSS 클래스 이름 충돌 검사 (index.html · books.js)
   단일 클래스 선택자(.name)가 최상위에서 두 번 이상, 같은 속성을 다른 값으로 정의하면 보고합니다.
   기존 항목은 scripts/css-dup-baseline.txt 에 기록해 두고, 새로 생긴 충돌만 실패로 처리합니다.
   사용: node scripts/css-dup-check.js          (새 충돌이 있으면 종료 코드 1)
         node scripts/css-dup-check.js --update (현재 상태를 기준선으로 저장) */
const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..'),base=path.join(__dirname,'css-dup-baseline.txt');
const KEY=['display','position','width','height','background','background-color','color','padding','margin','font-size','border','border-radius','flex-direction','grid-template-columns'];
function cssBlocks(file){const t=fs.readFileSync(path.join(root,file),'utf8');const out=[];
 if(file.endsWith('.html')){for(const m of t.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g))out.push(m[1])}
 else{for(const m of t.matchAll(/const\s+(\w*CSS\w*)\s*=\s*`([\s\S]*?)`;/g))out.push(m[2])}
 return out}
function rules(css){css=css.replace(/\/\*[\s\S]*?\*\//g,'');const res=[];let i=0,depth=0,start=0,sel='';
 const n=css.length;
 while(i<n){const c=css[i];
  if(c==='{'){if(depth===0){sel=css.slice(start,i).trim();depth=1;const bodyStart=i+1;let d=1,j=i+1;while(j<n&&d>0){if(css[j]==='{')d++;else if(css[j]==='}')d--;j++}
    const body=css.slice(bodyStart,j-1);i=j;start=j;depth=0;if(!sel.startsWith('@'))res.push({sel,body});continue}}
  i++}
 return res}
function decls(body){const o={};body.split(';').forEach(d=>{const k=d.indexOf(':');if(k>0)o[d.slice(0,k).trim().toLowerCase()]=d.slice(k+1).trim()});return o}
const files=['index.html','books.js'],byClass={};
for(const f of files){let b;try{b=cssBlocks(f)}catch(e){continue}
 for(const css of b)for(const r of rules(css)){for(const s of r.sel.split(',').map(x=>x.trim())){if(!/^\.[A-Za-z0-9_-]+$/.test(s))continue;(byClass[s]=byClass[s]||[]).push({f,d:decls(r.body)})}}}
const found=[];
for(const [cls,list] of Object.entries(byClass)){if(list.length<2)continue;
 const seen={};let clash=[];for(const r of list)for(const k of KEY){if(r.d[k]===undefined)continue;if(seen[k]!==undefined&&seen[k]!==r.d[k])clash.push(k);seen[k]=r.d[k]}
 if(clash.length)found.push(cls+' ('+[...new Set(clash)].join(',')+')')}
found.sort();
if(process.argv.includes('--update')){fs.writeFileSync(base,found.join('\n')+'\n');console.log('기준선 저장:',found.length,'개');process.exit(0)}
const known=new Set(fs.existsSync(base)?fs.readFileSync(base,'utf8').split('\n').filter(Boolean):[]);
const fresh=found.filter(x=>!known.has(x));
if(fresh.length){console.error('새 클래스 이름 충돌 '+fresh.length+'건 — 기능 접두어를 붙여 다른 이름을 쓰세요:\n  '+fresh.join('\n  '));process.exit(1)}
console.log('새 충돌 없음 (기존 '+found.length+'건은 기준선에 있음)');
