// 「그림은 …」이라고 쓰였는데 그림(<img>·<svg>·.fg)이 없는 문항을 찾아 표로 만든다.
// 실행: node scripts/figure-gap-check.js  →  scripts/figure-gaps.tsv
const fs=require('fs'),path=require('path'),root=path.join(__dirname,'..');
const strip=s=>String(s||'').replace(/<[^>]+>/g,'').replace(/\s+/g,' ').trim();
const fig=q=>/<img|<svg|class="fg|<canvas/.test(q||'');
const stem=q=>String(q||'').split('<div class="chs')[0].split('<div class="bog')[0];
const out=[['과목','파일','코드','세트','교재쪽','문항 앞부분']];
function add(subj,file,it){if(!it||!it.q)return;if(/그림/.test(strip(stem(it.q)))&&!fig(it.q))out.push([subj,file,it.code,it.set||'',it.pg||'',strip(stem(it.q)).slice(0,90)])}
const DATA=eval(fs.readFileSync(path.join(root,'bank/data.js'),'utf8')+';DATA');DATA.forEach(q=>add('물질과 에너지','bank/data.js',q));
for(const [subj,dir] of [['물질과 에너지','bank'],['세포와 물질대사','cm'],['역학과 에너지','ph']])for(const f of fs.readdirSync(path.join(root,dir)).filter(f=>f.endsWith('.json')&&f!=='index.json')){try{const a=JSON.parse(fs.readFileSync(path.join(root,dir,f),'utf8'));if(Array.isArray(a))a.forEach(it=>add(subj,dir+'/'+f,it))}catch(e){}}
fs.writeFileSync(path.join(__dirname,'figure-gaps.tsv'),out.map(r=>r.join('\t')).join('\n')+'\n');
const c={};out.slice(1).forEach(r=>{const k=r[0]+' · '+(r[3]||'-');c[k]=(c[k]||0)+1});console.log(out.length-1+'건',c);
