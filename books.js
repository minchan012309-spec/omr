/* Solvi 교재 — 개념서 · 유형서 · 실전 모의고사
   index.html 의 전역(DATA, CONC, byCode, SUBJ …)을 그대로 사용하는 보조 스크립트입니다. 교재 탭을 처음 열 때 불러옵니다.
   쪽 나눔은 books/heights.json 에 저장된 문항 높이로 계산하므로 어느 기기에서나 같은 쪽 번호가 나옵니다(QR 쪽 채점용). */
const BK_MM=96/25.4,BK_BODY=240,BK_COLW=89,BK_FULLW=186;
const BKP={},BKSELC={},BKH={};let BKHT=null,BKM=null,BKREADY=null;
const BKCIR='①②③④⑤⑥⑦⑧⑨⑩';
const bkLv=q=>q.lv0||q.lv||'';
const BKPAL={cm:{p:'#2f9d66',pd:'#1f7d4e',pl:'#eefcf5',pl2:'#d9f8e8',line:'#b0e3c9'},me:{p:'#2f7fd0',pd:'#1d5ca6',pl:'#eef5fc',pl2:'#d9e8f8',line:'#b9cfe6'}};
const bkVars=()=>{const c=BKPAL[SUBJ]||BKPAL.cm;return '--p:'+c.p+';--pd:'+c.pd+';--pl:'+c.pl+';--pl2:'+c.pl2+';--line:'+c.line+';--y:#ffca2c'};
const bkCir=a=>String(a).split(',').map(x=>BKCIR[(+x)-1]||x).join(', ');

/* ---------- 스타일 ---------- */
const BKCSS=`
.bkdoc{font-family:Pretendard,PretendardLocal,'Noto Sans CJK KR','Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;color:#111;font-weight:400;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all;overflow-wrap:break-word}
.bkdoc *{box-sizing:border-box}
.bkdoc i{font-family:'Times New Roman','Noto Serif CJK KR',serif;font-style:italic}.bkdoc sub,.bkdoc sup{font-size:70%;line-height:0}
.bkdoc .bp{position:relative;width:210mm;height:297mm;background:#fff;overflow:hidden;font-size:12px;line-height:1.5}
.bkdoc .hd{position:absolute;left:12mm;right:12mm;top:9mm;height:12mm;border-bottom:2.2px solid #111}
.bkdoc .hd:after{content:"";position:absolute;left:0;right:0;bottom:-4.6px;border-bottom:.8px solid #111}
.bkdoc .hd .t1{position:absolute;left:0;bottom:2mm;font-size:12.5px;font-weight:700;letter-spacing:-.2px;white-space:nowrap}
.bkdoc .hd .t1 em{font-style:normal;font-weight:400;color:#444;font-size:11px;margin-left:6px}
.bkdoc .hd .t2{position:absolute;right:0;bottom:2mm;font-size:12px;font-weight:700;white-space:nowrap}
.bkdoc .hd .t2 b{display:inline-block;background:#111;color:#fff;padding:1px 9px;border-radius:2px;margin-left:6px;font-weight:700}
.bkdoc .bd{position:absolute;left:12mm;right:12mm;top:27mm;height:${BK_BODY}mm}
.bkdoc .bd.one{overflow:hidden}
.bkdoc .cols{display:flex;gap:8mm;height:100%;position:relative}
.bkdoc .cols:before{content:"";position:absolute;left:50%;top:0;bottom:0;border-left:.7px solid #777}
.bkdoc .col{width:${BK_COLW}mm;flex:none;overflow:hidden}
.bkdoc .ft{position:absolute;left:12mm;right:12mm;bottom:7mm;height:20mm;border-top:.7px solid #111;display:grid;grid-template-columns:1fr auto 1fr;align-items:center}
.bkdoc .ft .fl{font-size:9.5px;color:#444}
.bkdoc .ft .pn{font-size:12px;font-weight:700;text-align:center}
.bkdoc .ft .fr2{justify-self:end;display:flex;align-items:center;gap:2.4mm}
.bkdoc .ft .qt{font-size:9px;line-height:1.35;color:#333;text-align:right}.bkdoc .ft .qt b{display:block;font-size:10px;color:#111}
.bkdoc .ft .qq{width:12mm;height:12mm;display:flex;align-items:center;justify-content:center;border:.6px solid #111;padding:.8mm;background:#fff}
.bkdoc .ft .qq svg{width:100%;height:100%;display:block}
.bkdoc .ft .fn{font-size:9.5px;color:#444;text-align:right}
/* 문항 */
.bkdoc .u.q{margin:0 0 4.6mm;font-size:12.2px;line-height:1.52}
.bkdoc .u.q .qs p{margin:0 0 1.6mm;text-align:justify}
.bkdoc .u.q .no{display:inline-block;min-width:6mm;font-weight:800;font-size:14.5px;margin-right:.6mm;letter-spacing:-.5px}
.bkdoc .u.q .pt{font-weight:700;font-size:11px;white-space:nowrap}
.bkdoc .u.q .lv{display:inline-block;margin-left:1.6mm;font-size:9px;font-weight:700;border:.5px solid #111;border-radius:2px;padding:0 1.3mm;line-height:3.5mm;vertical-align:1px;white-space:nowrap}
.bkdoc .u.q .lv.h{background:#111;color:#fff}
.bkdoc .u.q .fg{text-align:center;margin:1.6mm 0}.bkdoc .u.q .fg img{max-width:100%;max-height:62mm;height:auto}
.bkdoc .u.q .bogi,.bkdoc .u.q .bxx{border:.6px solid #111;padding:1.6mm 2.2mm;margin:2mm 0;font-size:11.8px;line-height:1.5}
.bkdoc .u.q .bogi{position:relative;padding-top:3.4mm;margin-top:4.2mm}
.bkdoc .u.q .bogi .bt{position:absolute;top:-2.9mm;left:50%;transform:translateX(-50%);background:#fff;padding:0 2mm;margin:0;font-weight:700;font-size:11.3px;white-space:nowrap}
.bkdoc .u.q .bogi p,.bkdoc .u.q .bxx p{margin:.5mm 0;padding-left:5mm;text-indent:-5mm;text-align:left}
.bkdoc .u.q .bxx{border-style:solid}
.bkdoc .u.q .eqn{text-align:center;margin:1.6mm 0;font-size:12.5px}
.bkdoc .u.q table.tb{border-collapse:collapse;margin:2mm auto;font-size:11px;line-height:1.35;max-width:100%}
.bkdoc .u.q table.tb th,.bkdoc .u.q table.tb td{border:.6px solid #111;padding:.6mm 1.8mm;text-align:center}
.bkdoc .u.q table.tb th{background:#eceff3;font-weight:700}
.bkdoc .u.q .chs{margin-top:1mm;font-size:11.8px;line-height:1.5}
.bkdoc .u.q .chs.sh{display:grid;grid-template-columns:repeat(3,1fr);row-gap:.4mm}
.bkdoc .u.q .chs.md{display:grid;grid-template-columns:repeat(2,1fr);row-gap:.4mm;column-gap:2mm}
.bkdoc .u.q .chs div{display:flex;gap:1.1mm;padding-left:0}.bkdoc .u.q .chs div b{flex:none;font-weight:500}
.bkdoc .u.q .chs.lg div{margin:.5mm 0}
.bkdoc .u.q .bk{display:inline-block;min-width:15mm;text-align:center;border-bottom:.6px solid #111;font-weight:700;color:#555;line-height:1.1;margin:0 .6mm}
.bkdoc .u.q .fr,.bkdoc .fr{display:inline-block;vertical-align:middle;text-align:center;line-height:1.12;margin:0 .6mm}.bkdoc .fr>span{display:block;padding:0 .6mm}.bkdoc .fr>span:first-child{border-bottom:.6px solid #111}
.bkdoc .u.q .ptn{text-align:right;font-size:10.5px;color:#444}
.bkdoc .u.q .gi{border:.6px solid #111;padding:1.4mm 2mm;margin:1.6mm 0}
.bkdoc .u.q .ans{margin-top:1.6mm;border:.6px solid #111;padding:.8mm 2.4mm}.bkdoc .u.q .ans div{height:6.4mm;border-bottom:.6px dotted #888}.bkdoc .u.q .ans div:last-child{border-bottom:0}
/* 실전 모의고사(출제 파일 서식) */
.bkdoc .mk .hd .t2 b{background:#111}
.bkdoc .mk .info{position:absolute;left:12mm;right:12mm;top:26mm;height:15mm;border:1px solid #111;display:grid;grid-template-columns:1fr 26mm;font-size:11px}
.bkdoc .mk .info .l{padding:1.6mm 3mm;font-weight:700;font-size:12.5px;border-right:1px solid #111;display:flex;flex-direction:column;justify-content:space-between}
.bkdoc .mk .info .l div{display:flex;font-weight:600;font-size:11px;border-top:1px solid #111;margin:0 -3mm -1.6mm}.bkdoc .mk .info .l div span{flex:1;padding:.6mm 3mm;border-right:1px solid #111}.bkdoc .mk .info .l div span:last-child{border-right:0}
.bkdoc .mk .info .r{text-align:center;padding-top:1mm;font-weight:700}.bkdoc .mk .info .r small{display:block;margin-top:2mm;font-size:12px;font-weight:400;color:#555}
.bkdoc .mk .bd.wi{top:46mm;height:${BK_BODY-19}mm}
.bkdoc .mk .u.q{font-size:12.4px}
.bkdoc .mk .cv2{position:absolute;inset:13mm 15mm 12mm 15mm}
.bkdoc .mk .cv2 .row1{display:flex;border:.35mm solid #000;height:11mm;font-size:13px}.bkdoc .mk .cv2 .row1 div{flex:1;text-align:center;line-height:11mm;border-right:.35mm solid #000;font-weight:600}.bkdoc .mk .cv2 .row1 div:last-child{border-right:0}
.bkdoc .mk .cv2 .ttl{margin-top:14mm;text-align:center}.bkdoc .mk .cv2 .a{font-size:19px;font-weight:600;letter-spacing:2px}.bkdoc .mk .cv2 .b{margin-top:5mm;font-size:46px;font-weight:800;letter-spacing:-1px;line-height:1.1}.bkdoc .mk .cv2 .c{margin-top:4mm;font-size:19px;font-weight:700;letter-spacing:1px}
.bkdoc .mk .cv2 .ln{margin:8mm auto 0;width:78%;border-top:.9mm solid #000;border-bottom:.25mm solid #000;height:1.4mm}
.bkdoc .mk .cv2 .info3{margin-top:12mm;width:100%;border-collapse:collapse;font-size:13px;line-height:1.6}.bkdoc .mk .cv2 .info3 th,.bkdoc .mk .cv2 .info3 td{border:.3mm solid #000;padding:2.6mm 3.5mm}.bkdoc .mk .cv2 .info3 th{width:28mm;text-align:center;font-weight:800}
.bkdoc .mk .cv2 .note{margin-top:9mm;border:.35mm solid #000;padding:5mm 6mm}.bkdoc .mk .cv2 .note h3{margin:0 0 3mm;font-size:14px;font-weight:800;text-align:center;border-bottom:.25mm solid #000;padding-bottom:2mm;letter-spacing:6px}.bkdoc .mk .cv2 .note ol{margin:0;padding-left:5mm;font-size:12.4px;line-height:1.8}
.bkdoc .mk .cv2 .idt{position:absolute;left:0;right:0;bottom:11mm;border-collapse:collapse;width:100%;font-size:14px}.bkdoc .mk .cv2 .idt td{border:.35mm solid #000;height:15mm;text-align:center}.bkdoc .mk .cv2 .idt td.k{width:20mm;font-weight:800;letter-spacing:3px}
.bkdoc .mk .cv2 .foot{position:absolute;left:0;right:0;bottom:0;text-align:center;font-size:11px;border-top:.25mm solid #000;padding-top:2mm}
/* 모의고사 정답·해설(새 레이아웃) */
.bkdoc .ma .sc{border:.35mm solid #111;margin:0 0 4mm}
.bkdoc .ma .sc h5{margin:0;background:#111;color:#fff;font-size:12px;font-weight:800;padding:1mm 3mm;letter-spacing:2px}
.bkdoc .ma .sc table{width:100%;border-collapse:collapse;font-size:11px;text-align:center;line-height:1.35}
.bkdoc .ma .sc th{background:#eceff3;border-bottom:.35mm solid #111;border-right:.3mm solid #aaa;padding:.8mm 1mm;font-weight:700}
.bkdoc .ma .sc td{border-bottom:.3mm solid #ccc;border-right:.3mm solid #aaa;padding:.7mm 1mm}.bkdoc .ma .sc td.a{font-weight:800;font-size:13px}
.bkdoc .ma .sc th:last-child,.bkdoc .ma .sc td:last-child{border-right:0}
.bkdoc .ma .sc td.ar{text-align:left;padding-left:2mm}
.bkdoc .ma .tot{display:flex;justify-content:space-between;align-items:center;border:.35mm solid #111;padding:2mm 3mm;margin:0 0 4mm;font-size:12px;font-weight:700}.bkdoc .ma .tot span.bx{display:inline-block;width:26mm;border-bottom:.35mm solid #111;height:6mm;vertical-align:bottom}
.bkdoc .ma .ex{display:grid;grid-template-columns:11mm 1fr;margin:0 0 3.6mm;font-size:10.8px;line-height:1.5;border-top:.6mm solid #111;border-bottom:.25mm solid #999}
.bkdoc .ma .ex .rl{border-right:.25mm solid #999;padding:1.6mm 0;text-align:center}.bkdoc .ma .ex .rl b{display:block;font-size:17px;font-weight:800;line-height:1.1}
.bkdoc .ma .ex .rl span{display:inline-block;margin-top:1.4mm;width:6.4mm;height:6.4mm;line-height:6.4mm;border:.45mm solid #111;border-radius:50%;font-weight:800;font-size:11px}
.bkdoc .ma .ex .rb{padding:1.4mm 0 1.4mm 2.4mm}
.bkdoc .ma .ex .core{font-weight:700;margin:0 0 1mm}
.bkdoc .ma .ex ul{list-style:none;margin:0;padding:0}.bkdoc .ma .ex li{display:flex;gap:1.6mm;margin:.5mm 0;align-items:flex-start}
.bkdoc .ma .ex li i{font-style:normal;flex:none;width:4.2mm;height:4.2mm;line-height:4.2mm;text-align:center;font-size:9px;font-weight:800;border:.4mm solid #111;border-radius:1px;margin-top:.5mm;font-family:inherit}
.bkdoc .ma .ex li.sm span{color:#333;font-weight:700}.bkdoc .ma .ex li i.x{background:#111;color:#fff}
.bkdoc .ma .ex li span{flex:1}
.bkdoc .ma .ex .ft2{margin-top:1.4mm;padding-top:1mm;border-top:.25mm dotted #999;font-size:9.6px;color:#444;line-height:1.45}.bkdoc .ma .ex .ft2 b{color:#111}
`;
/* 화면용(리더) 보조 스타일 */
const BKSCR=`
.bkw{position:relative;margin:0 auto 6px;background:#fff;box-shadow:0 1px 6px rgba(20,30,50,.28);overflow:hidden}
.bkzm{display:inline-flex;align-items:center;gap:4px}.bkzm b{min-width:44px;text-align:center;font-size:13px}.bkzm button{padding:6px 12px;border-radius:8px;font:inherit;font-size:15px}
#bkpages{display:flex;flex-direction:column;overflow-x:auto;-webkit-overflow-scrolling:touch}#bkpages>*{flex:none;margin-left:auto;margin-right:auto}
.bkbar{display:flex;gap:10px;align-items:center;flex-direction:row-reverse;justify-content:flex-end;margin:0 auto 14px;padding:6px 10px;font-size:12.5px;color:var(--m)}
.bkbar b{color:var(--t)}.bkbar button{padding:6px 14px;border-radius:8px;font:inherit;font-size:13px}
.bkrd{position:sticky;top:62px;z-index:4;background:#fff;border:1px solid var(--l);border-radius:12px;padding:8px 10px;margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.bkrd select{max-width:100%;flex:1 1 170px;min-width:0}
.bkshelf{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.bkcard{border:1px solid var(--l);border-radius:12px;background:#fff;padding:14px;display:flex;gap:14px}
.bkcov{flex:none;width:92px;height:130px;border:1.5px solid #111;background:#fff;position:relative;padding:7px 7px 0;font-family:Pretendard,sans-serif;display:flex;flex-direction:column}
.bkcov i{display:block;width:16px;height:3px;background:#111;margin:14px 0 6px}
.bkcov b{font-size:11.5px;line-height:1.25;word-break:keep-all;font-weight:800;letter-spacing:-.5px}.bkcov span{font-size:10px;color:#444;margin-top:3px}
.bkcov em{position:absolute;left:7px;right:7px;bottom:6px;border-top:1px solid #111;padding-top:3px;font-style:normal;font-size:8px;color:#555}
.bkcard .bi2{flex:1;min-width:0;display:flex;flex-direction:column}.bkcard h3{margin:0;font-size:16px}.bkcard p{margin:4px 0 8px;font-size:12.5px;color:var(--m);line-height:1.5}
.bkcard .bt2{margin-top:auto;display:flex;gap:6px;flex-wrap:wrap}.bkcard .bt2 button{padding:7px 12px;font-size:13px;border-radius:8px}
.bkpath{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;align-items:end}
.bkpath label{font-size:12px;color:var(--m);display:block;margin-bottom:3px}.bkpath select{width:100%}
@media(max-width:560px){.bkcard{flex-direction:row}.bkcov{width:76px;height:108px}}
`;

/* ---------- 준비: 글꼴 · 높이표 · 개념 · 모의고사 ---------- */
const BKCDN='https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.css';
function bkFontCss(abs){const b=abs||'';return [[400,'Regular'],[500,'Medium'],[600,'SemiBold'],[700,'Bold'],[800,'ExtraBold']].map(([w,n])=>`@font-face{font-family:PretendardLocal;font-weight:${w};font-display:swap;src:url(${b}fonts/Pretendard-${n}.woff2) format('woff2')}`).join('')}
function bkInit(){
 if(BKREADY)return BKREADY;
 BKREADY=(async()=>{
  if(!document.getElementById('bkcss')){const s=document.createElement('style');s.id='bkcss';s.textContent=bkFontCss('')+BKSCR;document.head.appendChild(s)}
  try{await Promise.all([400,600,700,800].map(w=>document.fonts.load(w+' 12px Pretendard','가A1')))}catch(e){}
  try{const r=await fetch('books/heights.json');if(r.ok)BKHT=await r.json()}catch(e){}
  if(!BKHT)BKHT={};
  try{const r=await fetch('cm/mocks.json');if(r.ok)BKM=await r.json()}catch(e){}
  if(!BKM)BKM={};
 })();
 return BKREADY;
}
const BKSH=':host{all:initial;display:block}.bkdoc.scr .bp{position:absolute;left:0;top:0;transform-origin:0 0;transform:scale(var(--bks,1))}';
function bkShadow(host,html,css){const r=host.shadowRoot||host.attachShadow({mode:'open'});r.innerHTML='<style>'+BKSH+(css||BKCSS)+'</style>'+html;return r}
function bkProbe(){let p=document.getElementById('bkprobe');if(!p){p=document.createElement('div');p.id='bkprobe';p.style.cssText='position:absolute;left:-9999px;top:0;visibility:hidden;pointer-events:none;width:300mm';document.body.appendChild(p);bkShadow(p,'<div class="bkdoc"><div id="bkpm"></div></div>')}return p.shadowRoot.getElementById('bkpm')}
function bkMeasure(html,w,cls){const p=bkProbe();p.innerHTML='<div class="'+(cls||'bk')+'" style="'+bkVars()+';width:'+w+'mm;display:flow-root;font-size:12px;line-height:1.5">'+html+'</div>';return Math.ceil(p.firstChild.getBoundingClientRect().height/BK_MM*10)/10}
const BKHA={};
function bkH(u){const k=u.key;if(BKREC)BKREC.push(u);if(BKHT&&BKHT[k]!=null)return BKHT[k];if(BKHA[k]!=null)return BKHA[k];if(BKH[k]==null)BKH[k]=bkMeasureUnit(u);return BKH[k]}

/* ---------- 문항 → HTML ---------- */
function bkDoc(h){return new DOMParser().parseFromString('<body>'+h+'</body>','text/html').body}
function bkChoices(root){const c=root.querySelector('.chs');if(!c)return;const t=[...c.querySelectorAll(':scope>div')].map(d=>(d.querySelector('span')||d).textContent.trim());const m=Math.max(0,...t.map(x=>x.length));c.classList.add(m<=10?'sh':m<=20?'md':'lg')}
function bkQHtml(q,no,o){o=o||{};
 const r=bkDoc(q.q);const qs=r.querySelector('.qs');if(!qs)return '<div class="u q">'+q.q+'</div>';
 const pt=o.pt!=null?'['+o.pt+'점]':'';
 bkChoices(qs);
 const first=qs.firstElementChild;const numH='<b class="no">'+no+'</b>';
 if(o.code)qs.insertAdjacentHTML('afterbegin','<div class="qh2">'+numH+'<span class="cd">'+(o.lv?'난이도 '+o.lv+' · ':'')+q.code+'</span></div>');
 else if(first&&first.tagName==='P')first.insertAdjacentHTML('afterbegin',numH);else qs.insertAdjacentHTML('afterbegin','<p>'+numH+'</p>');
 if(pt){const kids=[...qs.children];let tgt=null;for(const k of kids){if(k.classList.contains('chs')||k.classList.contains('bogi'))break;if(k.tagName==='P')tgt=k}
  if(!tgt)tgt=kids.filter(k=>k.tagName==='P').pop();if(tgt)tgt.insertAdjacentHTML('beforeend',' <span class="pt">'+pt+'</span>')}
 if(o.ans){qs.insertAdjacentHTML('beforeend','<div class="ans"><div></div><div></div><div></div></div>')}
 return '<div class="u q" data-c="'+q.code+'">'+qs.innerHTML.replace(/ id="[^"]*"/g,'')+'</div>'}
function bkOxHtml(q,no,kind){const r=bkDoc(q.q);const qs=r.querySelector('.qs')||r;let h=qs.innerHTML.replace(/^<p>/,'').replace(/<\/p>$/,'');
 return '<div class="u o '+(kind==='bl'?'b':'')+'" data-c="'+q.code+'"><span class="nc"><b>'+no+'</b><small>'+q.code+'</small></span><span class="tx">'+h+'</span>'+(kind==='ox'?'<span class="bx">O / X</span>':'')+'</div>'}
function bkAnsOf(q){if(q.set==='ox')return String(q.ans).toUpperCase()==='O'?'○':'×';if(q.set==='blank')return (q.blanks||[]).map((a,k)=>'㉠㉡㉢㉣㉤'[k]+' '+a).join(' · ');if(q.set==='essay')return '';return bkCir(q.ans)}
function bkXHtml(q,no){const r=bkDoc(q.exp||'');const sol=r.querySelector('.sol')||r;sol.querySelectorAll('.sh').forEach(e=>e.remove());
 let body=sol.innerHTML;if(!r.querySelector('.sol'))body=r.innerHTML;
 const a=q.set==='essay'?'모범 답안':'정답 '+bkAnsOf(q);
 return '<div class="u x"><div class="xh"><span class="xn">'+no+'</span><span class="xa">'+a+'</span><span class="xm">'+(bkLv(q)&&q.set!=='ox'&&q.set!=='blank'?'난이도 '+bkLv(q)+' · ':'')+q.code+'</span></div><div class="xb">'+body+'</div></div>'}

/* ---------- 구성 선택 ---------- */
function bkSubs(){const C=CONC[SUBJ]||{};const o=C.subs||{};const keys=Object.keys(o);if(keys.length)return keys.map(k=>({k,name:o[k].name,goal:o[k].goal||''}));
 const m=new Map();DATA.filter(q=>q.sub).forEach(q=>{if(!m.has(q.sub))m.set(q.sub,q.subname)});return [...m].map(([k,n])=>({k,name:n,goal:''}))}
function bkPickRound(a,n,pat){const by={};a.forEach(x=>(by[bkLv(x)]=by[bkLv(x)]||[]).push(x));const out=[],used=new Set(),fam=new Set();
 for(let pass=0;pass<2&&out.length<n;pass++){let guard=0,i=0;while(out.length<n&&guard++<400){const l=pat[i++%pat.length];const arr=by[l]||[];const x=arr.find(y=>!used.has(y.code)&&(pass||!fam.has(y.fam)));if(x){used.add(x.code);fam.add(x.fam);out.push(x)}if(guard>300&&!arr.length&&pass)break}}
 if(out.length<n)a.forEach(x=>{if(out.length<n&&!used.has(x.code)){used.add(x.code);out.push(x)}});return out}
function bkSel(){
 if(BKSELC[SUBJ])return BKSELC[SUBJ];
 const base=DATA.filter(q=>q.sub&&q.set!=='bank'&&!q.mock);
 const subs=bkSubs();const S={subs,ox:{},bl:{},basic:{},mc:[],top:[],essay:[]};
 const byNo=(a,b)=>(a.no||0)-(b.no||0);
 subs.forEach(s=>{S.ox[s.k]=base.filter(q=>q.sub===s.k&&q.set==='ox').sort(byNo);S.bl[s.k]=base.filter(q=>q.sub===s.k&&q.set==='blank').sort(byNo)});
 const used=new Set();
 subs.forEach(s=>{const lows=base.filter(q=>q.sub===s.k&&q.set==='mc'&&bkLv(q)==='하').sort(byNo);
  const pick=BKT?bkFitBasic(s,lows):lows.slice(0,8);S.basic[s.k]=pick;pick.forEach(q=>used.add(q.code))});
 const caps={me:{mc:195,top:70,essay:25},cm:{mc:999,top:999,essay:99}}[SUBJ]||{mc:195,top:70,essay:25};
 const so=s=>subs.findIndex(x=>x.k===s);
 const typeOrder=new Map();base.forEach(q=>{const k=q.sub+'|'+q.type;if(!typeOrder.has(k))typeOrder.set(k,typeOrder.size)});
 const sortT=a=>a.sort((x,y)=>so(x.sub)-so(y.sub)||typeOrder.get(x.sub+'|'+x.type)-typeOrder.get(y.sub+'|'+y.type)||(LVI[bkLv(x)]-LVI[bkLv(y)])||byNo(x,y));
 let mc=base.filter(q=>q.set==='mc'&&!used.has(q.code));if(mc.length>caps.mc)mc=bkPickType(mc,caps.mc);
 let top=base.filter(q=>q.set==='top');if(top.length>caps.top)top=bkPickType(top,caps.top);
 S.mc=sortT(mc);S.top=sortT(top);
 let es=base.filter(q=>q.set==='essay').sort((a,b)=>so(a.sub)-so(b.sub)||byNo(a,b));
 if(es.length>caps.essay){const t=es.length;es=Array.from({length:caps.essay},(_,i)=>es[Math.floor(i*t/caps.essay)])}
 S.essay=es;
 return BKSELC[SUBJ]=S}
function bkPickType(pool,cap){
 const g=new Map();pool.forEach(q=>{const k=q.sub+'|'+q.type;if(!g.has(k))g.set(k,[]);g.get(k).push(q)});
 const pat=['중','상','중','최','하','중','상'];const pk=new Map(),left=new Map();let tot=0;
 g.forEach((a,k)=>{const n=Math.min(a.length,Math.max(2,Math.round(cap*a.length/pool.length)));const o=bkPickRound(a,n,pat);pk.set(k,o);left.set(k,a.filter(x=>!o.includes(x)));tot+=o.length});
 const rank=x=>({'하':0,'중':1,'상':2,'최':3}[bkLv(x)]??1);
 while(tot>cap){let bk=null,bn=0;pk.forEach((o,k)=>{if(o.length>bn&&o.length>2){bn=o.length;bk=k}});if(!bk)break;const o=pk.get(bk);let wi=0;o.forEach((x,i)=>{if(rank(x)<rank(o[wi]))wi=i});o.splice(wi,1);tot--}
 while(tot<cap){let bk=null,br=0;left.forEach((l,k)=>{const r=l.length/(pk.get(k).length+1);if(l.length&&r>br){br=r;bk=k}});if(!bk)break;pk.get(bk).push(left.get(bk).shift());tot++}
 return [...pk.values()].flat()}

/* ---------- 쪽 나누기 ---------- */
function bkPack(units,ncol,cap,firstCap){
 const pages=[];let pg=null,ci=0,used=0;
 const capOf=()=>pages.length===1&&firstCap!=null?firstCap:cap;
 const np=()=>{pg={cols:Array.from({length:ncol},()=>[])};pages.push(pg);ci=0;used=0};
 for(let i=0;i<units.length;i++){const u=units[i];
  if(!pg||(u.brk&&pg.cols.some(c=>c.length)))np();
  let need=u.h;if(u.keep&&units[i+1])need+=units[i+1].h;
  if(used+need>capOf()&&used>0){ci++;used=0;if(ci>=ncol)np()}
  pg.cols[ci].push(u);used+=u.h}
 return pages}
const bkU=(key,html,o)=>{const u={key:SUBJ+'|'+key,html,w:(o&&o.w)||BK_COLW,...(o||{})};u.h=bkH(u)+(u.addh||0);return u};

/* ---------- 쪽 계획 ---------- */
function bkParts(id){const m=id.match(/^(me|cm)-(c|t|m\d+)$/);return m?{subj:m[1],kind:m[2]}:null}
/* ===== 기존 교재(old-*.json)의 디자인으로 개념서·유형서 만들기 ===== */
const BK_CAPN=261,BK_CAPQ=254,BK_W1=183,BK_W2=87.3;
let BKT=null;
const BKOLDX=`.bko{background:none!important}.bko.scr .page{position:absolute;left:0;top:0;margin:0!important;box-shadow:none!important;transform-origin:0 0;transform:scale(var(--bks,1))}
.q .qc{margin-left:auto}.q .ut+.qc{margin-left:2.4mm}.q .ut{margin-left:auto}
.qrc{display:block;width:10mm;height:10mm}.qrc svg{width:100%;height:100%;display:block}
.page.qrp .bd{bottom:23mm}.page.qrp .ftr{align-items:center}
td.b small.cd{display:block;font-size:6.8pt;font-weight:400;color:#94a8b8;line-height:1.15;letter-spacing:0}
.wans{height:34mm;margin:2mm 0 0;border:.3mm solid var(--p);border-radius:1.4mm;background:repeating-linear-gradient(transparent 0,transparent 8.4mm,var(--line) 8.4mm,var(--line) 8.8mm)}
.ansv .bl{display:inline-block;min-width:0;padding:0 1.2mm}`;
async function bkLoadTpl(){
 if(BKT&&BKT._s===SUBJ)return;
 try{const r=await fetch('books/old-'+SUBJ+'.json');BKT=await r.json()}catch(e){BKT={css:'',divp:{},subp:[],subhead:{},school:'',cfront:'',cover2:'',toc:'',guide:'',backc:''}}
 BKT._s=SUBJ;BKT.css=(BKT.css||'').replace(/Pretendard,/g,'Pretendard,PretendardLocal,');BKT.all=BKT.css+BKOLDX}
function bkProbeO(){let p=document.getElementById('bkprobeo');if(p&&p.dataset.s!==SUBJ){p.remove();p=null}
 if(!p){p=document.createElement('div');p.id='bkprobeo';p.dataset.s=SUBJ;p.style.cssText='position:absolute;left:-9999px;top:0;visibility:hidden;pointer-events:none;width:300mm';document.body.appendChild(p);bkShadow(p,'<div class="bko"><div id="bkpm"></div></div>',BKT.all)}
 return p.shadowRoot.getElementById('bkpm')}
function bkSetProbe(u){
 if(!u.o){const p=bkProbe();p.innerHTML='<div class="'+(u.cls||'bk')+'" style="'+bkVars()+';width:'+(u.w||BK_COLW)+'mm;display:flow-root;font-size:12px;line-height:1.5">'+u.html+'</div>';return p.firstChild}
 const p=bkProbeO();const one=u.mm!=='two';const w=one?BK_W1:BK_W2;
 const html=(u.pre||'')+u.html+(u.post||'');
 p.innerHTML='<div class="page" style="height:auto;width:auto;margin:0;box-shadow:none;overflow:visible"><div class="bd'+(one?'':' two')+'" style="position:static;display:block"><div class="col" style="width:'+(w+8.4)+'mm;padding:0 4.2mm;height:auto;overflow:visible"><div class="mw" style="width:'+w+'mm;display:flow-root">'+html+'</div></div></div></div>';
 return p.querySelector('.mw')}
function bkMeasureUnit(u){const e=bkSetProbe(u);return Math.max(1,Math.ceil((e.getBoundingClientRect().height/BK_MM-(u.sub||0))*10)/10)}
async function bkMeasureUnitAsync(u){const e=bkSetProbe(u);
 await Promise.all([...e.querySelectorAll('img')].map(i=>i.complete&&i.naturalWidth?1:new Promise(r=>{i.onload=i.onerror=()=>r();setTimeout(r,30000)})));
 return Math.max(1,Math.ceil((e.getBoundingClientRect().height/BK_MM-(u.sub||0))*10)/10)}

/* ---- 문항 · 표 · 해설 조각 ---- */
function bkChoicesO(root){const c=root.querySelector('.chs');if(!c)return;c.className='chs';const t=[...c.querySelectorAll(':scope>div')].map(d=>(d.querySelector('span')||d).textContent.trim());const m=Math.max(0,...t.map(x=>x.length));if(m>11)c.classList.add('v');else if(m>8)c.classList.add('w')}
function bkQO(q,no,o){o=o||{};const r=bkDoc(q.q);const qs=r.querySelector('.qs');if(!qs)return '<div class="q">'+q.q+'</div>';
 bkChoicesO(qs);if(o.wans)qs.insertAdjacentHTML('beforeend','<div class="wans"></div>');
 const qh='<div class="qh"><b class="qn">'+no+'</b>'+(o.ut?'<span class="ut">'+esc(o.ut)+'</span>':'')+(o.tag?'<span class="qp">'+esc(o.tag)+'</span>':'')+'<span class="qc">'+q.code+'</span></div>';
 return '<div class="q" data-c="'+q.code+'">'+qh+'<div class="qs">'+qs.innerHTML+'</div></div>'}
const BKTB={
 ox:{pre:'<table class="tb f"><colgroup><col style="width:17mm"/><col style="width:auto"/><col style="width:16mm"/></colgroup><tbody>',head:'<table class="tb f"><colgroup><col style="width:17mm"/><col style="width:auto"/><col style="width:16mm"/></colgroup><thead><tr><th>번호</th><th>문장</th><th>답</th></tr></thead><tbody>'},
 bl:{pre:'<table class="tb f"><colgroup><col style="width:17mm"/><col style="width:auto"/></colgroup><tbody>',head:'<table class="tb f"><colgroup><col style="width:17mm"/><col style="width:auto"/></colgroup><thead><tr><th>번호</th><th>문장</th></tr></thead><tbody>'},
 oa:{pre:'<table class="tb f"><colgroup><col style="width:17mm"/><col style="width:13mm"/><col style="width:auto"/><col style="width:26mm"/></colgroup><tbody>',head:'<table class="tb f"><colgroup><col style="width:17mm"/><col style="width:13mm"/><col style="width:auto"/><col style="width:26mm"/></colgroup><thead><tr><th>번호</th><th>정답</th><th>이유</th><th>틀렸다면</th></tr></thead><tbody>'},
 ba:{pre:'<table class="tb f"><colgroup><col style="width:17mm"/><col style="width:auto"/><col style="width:26mm"/></colgroup><tbody>',head:'<table class="tb f"><colgroup><col style="width:17mm"/><col style="width:auto"/><col style="width:26mm"/></colgroup><thead><tr><th>번호</th><th>정답</th><th>틀렸다면</th></tr></thead><tbody>'}};
function bkStmt(q){const r=bkDoc(q.q);const qs=r.querySelector('.qs')||r;return qs.innerHTML.replace(/^<p>/,'').replace(/<\/p>$/,'')}
function bkRow(kind,q,no,sec){
 if(kind==='ox')return '<tr data-c="'+q.code+'"><td class="b">'+no+'<small class="cd">'+q.code+'</small></td><td class="l">'+bkStmt(q)+'</td><td>(　　)</td></tr>';
 if(kind==='bl')return '<tr data-c="'+q.code+'"><td class="b">'+no+'<small class="cd">'+q.code+'</small></td><td class="l">'+bkStmt(q)+'</td></tr>';
 const rv=sec?esc(sec.sub)+' '+esc(sec.no)+'<br/>p.[[CP:'+sec.id+']]':'';
 if(kind==='oa'){const e=bkDoc(q.exp||'');const ps=[...e.querySelectorAll('p')];const why=(ps[1]||ps[0]||{innerHTML:''}).innerHTML;
  return '<tr><td class="b">'+no+'</td><td><b>'+(String(q.ans).toUpperCase()==='O'?'O':'X')+'</b></td><td class="l">'+why+'</td><td>'+rv+'</td></tr>'}
 const e=bkDoc(q.exp||'');const p=e.querySelector('p');let t=p?p.innerHTML:'';t=t.replace(/&lt;&lt;(.*?)&gt;&gt;/g,'<span class="bl">$1</span>');
 return '<tr><td class="b">'+no+'</td><td class="l ansv">'+t+'</td><td>'+rv+'</td></tr>'}
function bkSolO(q,no,secs){const r=bkDoc(q.exp||'');let sol=r.querySelector('.sol');if(!sol){r.innerHTML='<div class="sol"><div class="sh"><span class="sn">'+no+'</span></div>'+r.innerHTML+'</div>';sol=r.querySelector('.sol')}
 sol.removeAttribute('id');const sn=sol.querySelector('.sn');if(sn)sn.textContent=no;
 const rvEl=sol.querySelector('.rv');
 if(rvEl){const CS=(CONC[SUBJ]||{}).secs||[];rvEl.querySelectorAll('.sm').forEach(sm=>{const m=sm.textContent.match(/개념 정리\s*(\S+)\s+(\d+)/);if(!m)return;const sc=CS.find(x=>x.sub===m[1]&&String(x.no)===m[2]);sm.textContent='(개념서 '+m[1]+' '+m[2]+(sc?', p.[[CP:'+sc.id+']]':'')+')'})}
 else{const rv=(secs||[]).slice(0,2).map(sc=>'<div class="st">→ '+esc(sc.title)+' <span class="sm">(개념서 '+esc(sc.sub)+' '+esc(sc.no)+', p.[[CP:'+sc.id+']])</span></div>').join('');
  if(rv)sol.insertAdjacentHTML('beforeend','<div class="rv"><span class="lb">이 문제를 틀렸다면 다시 공부할 부분</span>'+rv+'</div>')}
 return sol.outerHTML}
function bkQa(label,sub,arr){const rows=[];for(let i=0;i<arr.length;i+=10){const ch=arr.slice(i,i+10);rows.push('<tr>'+ch.map(x=>'<td><b>'+x[0]+'</b>'+x[1]+'</td>').join('')+Array(10-ch.length).fill('<td class="e"></td>').join('')+'</tr>')}
 return '<div class="blk"><div class="qah"><i>'+esc(sub)+'</i>'+esc(label)+'</div><table class="qa"><tbody>'+rows.join('')+'</tbody></table></div>'}

/* ---- 서식 조각 ---- */
function bkDivO(oldNo,no,en,title,idx,ds){const d=bkDoc(BKT.divp[oldNo]||BKT.divp['01']||'<div></div>');
 const set=(sel,f)=>{const e=d.querySelector(sel);if(e)f(e)};
 set('.bigno',e=>e.textContent=no);set('.tt .en',e=>e.textContent=en);set('.tt h1',e=>e.textContent=title);
 set('.idx',e=>e.innerHTML=idx.map(([c,n,r])=>'<div class="it"><i>'+esc(c)+'</i>'+esc(n)+'<span>'+esc(r||'')+'</span></div>').join(''));
 set('.ds',e=>e.textContent=ds);return d.innerHTML}
function bkSubO(i,sno,en,title,rows,tip){const d=bkDoc(BKT.subp[i%Math.max(1,BKT.subp.length)]||'<div></div>');const set=(sel,f)=>{const e=d.querySelector(sel);if(e)f(e)};
 set('.sno',e=>e.textContent=sno);set('.ghost',e=>e.textContent=(String(sno).split('-')[1]||'A'));set('.stt .en',e=>e.textContent=en);set('.stt h1',e=>e.textContent=title);
 set('.rows',e=>e.innerHTML=rows.map((r,k)=>'<div class="r"><i>'+(k+1)+'</i><b>'+esc(r[0])+'</b><span>'+esc(r[1])+'</span></div>').join(''));set('.tip',e=>e.textContent=tip);return d.innerHTML}
function bkCoverO(kind,sub,chips){const a=bkDoc(BKT.cfront);const s=a.querySelector('.cf-s');if(s)s.textContent=kind;
 const b=bkDoc(BKT.cover2);const em=b.querySelector('h1 em');if(em)em.textContent=kind;const sb=b.querySelector('.sub');if(sb)sb.innerHTML=sub;const ft=b.querySelector('.ft');if(ft)ft.innerHTML=chips.map(c=>'<span>'+esc(c)+'</span>').join('');
 return [a.innerHTML,b.innerHTML]}
function bkTocO(rows){const d=bkDoc(BKT.toc);const h1=d.querySelector('h1');const wrap=h1?h1.parentElement:d;[...wrap.querySelectorAll('.r,.s')].forEach(e=>e.remove());
 wrap.insertAdjacentHTML('beforeend',rows.map(r=>r.s?'<div class="s"><span>'+esc(r.t)+'</span><span class="d"></span><span class="n">'+r.n+'</span></div>':'<div class="r"><i>'+r.i+'</i><b>'+esc(r.t)+'</b><span class="d"></span><span class="n">'+r.n+'</span></div>').join(''));return d.innerHTML}
function bkGuideO(steps){const d=bkDoc(BKT.guide);const g=d.querySelector('.guide');if(g){[...g.querySelectorAll('.gstep')].forEach(e=>e.remove());g.insertAdjacentHTML('beforeend',steps.map((t,i)=>'<div class="gstep"><i>'+(i+1)+'</i><div>'+t+'</div></div>').join(''))}return d.innerHTML}

/* ---- 쪽 만들기 ---- */
const bkUo=(key,html,o)=>bkU(key,html,{o:1,mm:'two',...o});
function bkColHtml(units,tb){let h='',open=false;const close=()=>{if(open){h+='</tbody></table>';open=false}};
 units.forEach(u=>{if(u.row){if(!open){h+=tb.head;open=true}h+=u.html}else{close();h+=u.html}});close();return h}
function bkFitBasic(s,cands){
 const order=[];const tg=new Map();cands.forEach(q=>{if(!tg.has(q.type))tg.set(q.type,[]);tg.get(q.type).push(q)});
 const lists=[...tg.values()];for(let i=0;order.length<cands.length;i++){let any=false;lists.forEach(l=>{if(l[i]){order.push(l[i]);any=true}});if(!any)break}
 const head=bkUo('ug:b:'+s.k,'<div class="ugrp">'+esc(s.k)+' '+esc(s.name)+'</div>',{keep:true});
 let best=order.slice(0,Math.min(6,order.length));
 for(let k=Math.min(7,order.length);k<=Math.min(16,order.length);k++){
  const items=order.slice(0,k).sort((a,b)=>(a.no||0)-(b.no||0));
  const us=[head,...items.map((q,i)=>bkUo('q:'+q.code+':b',bkQO(q,i+1),{code:q.code}))];
  if(bkPack(us,2,BK_CAPQ).length<=2)best=items;else break}
 return best.sort((a,b)=>(a.no||0)-(b.no||0))}

async function bkPlan(id){
 if(BKP[id]&&BKP[id].subj===SUBJ)return BKP[id];
 await bkInit();await conceptLoad();
 const P=bkParts(id);if(!P)return null;
 if(P.kind[0]==='m'){const plan=bkPlanMock(id,P.kind.slice(1));plan.pages.forEach((p,i)=>p.n=i+1);plan.id=id;plan.subj=SUBJ;return BKP[id]=plan}
 await bkLoadTpl();
 const c=BKP[SUBJ+'-c'],t=BKP[SUBJ+'-t'];
 if(!(c&&c.subj===SUBJ&&t&&t.subj===SUBJ))bkBuildBooks();
 return BKP[id]}

function bkBuildBooks(){
 const S=bkSel(),T=BKT,C=CONC[SUBJ]||{secs:[],subs:{}},secs=C.secs||[];
 const secOfType={},secOfCode={};secs.forEach(sc=>{(sc.types||[]).forEach(t=>(secOfType[t]=secOfType[t]||[]).push(sc));[...(sc.ox||[]),...(sc.blank||[])].forEach(c=>secOfCode[c]=sc)});
 const nm=SNAME[SUBJ];
 const cP={o:1,kind:'c',title:nm+' 개념서',short:'개념서',pages:[],jumps:[]},tP={o:1,kind:'t',title:nm+' 유형서',short:'유형서',pages:[],jumps:[]};
 const pgn=P=>P.pages.length+1;
 const raw=(P,cls,inner)=>P.pages.push({o:1,t:'raw',cls,inner});
 const cols=(P,label,foot,two,packed,tb,qr)=>packed.forEach(p=>P.pages.push({o:1,t:'body',label,foot,two,cols:p.cols.map(c=>bkColHtml(c,tb||{})),codes:qr?p.cols.flat().map(u=>u.code).filter(Boolean):[]}));
 /* ===== 개념서 ===== */
 {const P=cP;const toc=[];
  const [cf,cv]=bkCoverO('개념서','개념 정리 · OX · 빈칸 · 기초 5지선다<br>빠른 정답 · 해설',['개념 정리','OX','빈칸','기초 5지선다','빠른 정답 · 해설']);
  raw(P,'cover cfront',cf);raw(P,'cover',cv);raw(P,'toc','');
  raw(P,'toc guide',bkGuideO(['<b>개념 정리</b> — 소단원마다 1, 2, 3 … 순서로 정리했다. 소단원 제목 오른쪽의 <b>「확인 문제 쪽」</b>이 그 소단원의 OX · 빈칸 · 기초 문제의 쪽수이다.','<b>OX · 빈칸</b> — 개념을 읽은 직후 암기를 확인한다. 틀린 문장은 이유와 개념 위치가 맨 뒤 해설에 있다.','<b>기초 5지선다</b> — 소단원마다 기본 문항을 풀며 개념을 적용해 본다.','<b>채점</b> — 문제 쪽 아래 <b>QR</b>을 스캔하면 그 쪽이 바로 채점된다. 맨 뒤 빠른 정답으로 직접 채점해도 된다.','<b>문항 코드</b> — 모든 문항에는 C31-001 같은 코드가 있다. 틀린 문항은 코드로 해설과 취약 유형 분석을 찾아본다.','<b>유형서와 함께</b> — 개념서를 마치면 같은 과목 유형서로 소단원 → 유형 → 난이도 순 문제를 푼다.']));
  toc.push({i:'01',t:'개념 정리',n:pgn(P)});P.jumps.push(['개념 정리',pgn(P)]);
  raw(P,'divp',bkDivO('01','01','CONCEPT','개념 정리',S.subs.map(s=>[s.k,s.name,'']),'소단원마다 1, 2, 3 … 순서로 정리했다. 소단원 제목 오른쪽에서 확인 문제의 쪽수를 알려 준다.'));
  S.subs.forEach(s=>{
   const cu=[];const sh=(T.subhead||{})[s.k];
   cu.push(bkUo('sh:'+s.k,'<div class="blk">'+(sh||'<h2 class="sec"><span class="no">'+esc(s.k)+'</span><span>'+esc(s.name)+'</span><small>[[REFSUB:'+s.k+']]</small></h2>')+'</div>',{mm:'one',brk:true,keep:true}));
   secs.filter(x=>x.sub===s.k).forEach(sec=>{
    cu.push(bkUo('sc:'+sec.id,'<div class="blk"><h3 class="sub" id="'+esc(sec.id)+'"><i>'+esc(sec.no)+'</i><span>'+esc(sec.title)+'</span><span class="ref">[[REFTYPE:'+sec.id+']]</span></h3></div>',{mm:'one',keep:true,sec:sec.id}));
    const d=bkDoc('<div id="r">'+sec.html+'</div>').firstElementChild;
    [...d.children].forEach((el,i)=>cu.push(bkUo('cb:'+sec.id+':'+i,'<div class="blk">'+el.outerHTML+'</div>',{mm:'one'})))});
   toc.push({s:1,t:s.k+' '+s.name,n:pgn(P)});
   bkPack(cu,1,BK_CAPN).forEach(p=>P.pages.push({o:1,t:'body',label:'01 개념 정리',foot:'01 개념 정리',two:false,cols:[bkColHtml(p.cols[0],{})],codes:[],secs:p.cols[0].filter(u=>u.sec).map(u=>u.sec)}))});
  const csec={};P.pages.forEach((p,i)=>(p.secs||[]).forEach(sid=>{if(!csec[sid])csec[sid]=i+1}));P.csec=csec;
  let no=0;
  [['ox','02','OX','OX 문제','옳으면 O, 옳지 않으면 X를 쓴다. 정답과 이유는 맨 뒤 해설에 있다.'],['bl','03','FILL IN','빈칸 채우기','㉠, ㉡ … 에 알맞은 말을 쓴다. 정답은 맨 뒤 해설에 있다.']].forEach(([kd,on,en,ti,ds])=>{
   const arrAll=S.subs.map(s=>({s,a:(kd==='ox'?S.ox:S.bl)[s.k]||[]})).filter(x=>x.a.length);
   toc.push({i:on,t:ti,n:pgn(P)});P.jumps.push([ti,pgn(P)]);
   raw(P,'divp',bkDivO(on,on,en,ti,arrAll.map(x=>[x.s.k,x.s.name,x.a.length+'문항']),ds));
   const us=[];no=0;
   arrAll.forEach(x=>{us.push(bkUo('ug:'+kd+':'+x.s.k,'<div class="ugrp">'+esc(x.s.k)+' '+esc(x.s.name)+'</div>',{mm:'one',keep:true,addh:12}));
    x.a.forEach(q=>{no++;us.push(bkUo('r:'+q.code+':'+kd,bkRow(kd,q,no),{mm:'one',row:true,pre:BKTB[kd].pre,post:'</tbody></table>',sub:4.6,code:q.code}))})});
   cols(P,on+' '+ti,on+' '+ti,false,bkPack(us,1,BK_CAPQ-10),BKTB[kd],true)});
  toc.push({i:'04',t:'기초 5지선다 문제',n:pgn(P)});P.jumps.push(['기초 5지선다',pgn(P)]);
  raw(P,'divp',bkDivO('04','04','BASIC','기초 5지선다',S.subs.map(s=>[s.k,s.name,(S.basic[s.k]||[]).length+'문항']),'소단원마다 기본 문항을 푼다. 쪽 아래 QR로 바로 채점할 수 있다.'));
  no=0;const basicNo={};
  S.subs.forEach(s=>{const arr=S.basic[s.k]||[];if(!arr.length)return;
   const us=[bkUo('ug:b:'+s.k,'<div class="ugrp">'+esc(s.k)+' '+esc(s.name)+'</div>',{keep:true,brk:true})];
   arr.forEach(q=>{no++;basicNo[q.code]=no;us.push(bkUo('q:'+q.code+':b',bkQO(q,no),{code:q.code}))});
   toc.push({s:1,t:s.k+' '+s.name+' ('+arr.length+'문항)',n:pgn(P)});
   cols(P,'04 기초 5지선다 · '+s.k,'04 기초 5지선다',true,bkPack(us,2,BK_CAPQ),null,true)});
  toc.push({i:'05',t:'빠른 정답 · 해설',n:pgn(P)});P.jumps.push(['정답 · 해설',pgn(P)]);P.aStart=pgn(P);
  raw(P,'divp',bkDivO('07','05','SOLUTIONS','빠른 정답 · 해설',[['정답','빠른 정답','채점용'],['OX','OX · 빈칸 정답','이유와 개념 위치'],['해설','기초 5지선다 해설','']],'모든 해설 끝에 「이 문제를 틀렸다면 다시 공부할 부분」이 있다.'));
  const au=[bkUo('qa:h','<div class="blk"><h2 class="sec"><span class="no">정답</span><span>빠른 정답</span><small>채점용</small></h2></div>',{mm:'one',keep:true})];
  S.subs.forEach(s=>{const arr=S.basic[s.k]||[];if(arr.length)au.push(bkUo('qa:'+s.k+':'+arr.length,bkQa(s.name+' · 기초 5지선다 '+basicNo[arr[0].code]+'~'+basicNo[arr[arr.length-1].code]+'번',s.k,arr.map(q=>[basicNo[q.code],bkCir(q.ans)])),{mm:'one'}))});
  cols(P,'05 빠른 정답','05 빠른 정답',false,bkPack(au,1,BK_CAPN));
  [['oa','OX 정답','ox'],['ba','빈칸 정답','bl']].forEach(([tk,ti,kd])=>{
   const us=[];no=0;
   S.subs.forEach(s=>{const arr=(kd==='ox'?S.ox:S.bl)[s.k]||[];if(!arr.length)return;
    us.push(bkUo('ug:'+tk+':'+s.k,'<div class="ugrp">'+esc(s.k)+' '+esc(s.name)+'</div>',{mm:'one',keep:true,addh:12}));
    arr.forEach(q=>{no++;us.push(bkUo('r:'+q.code+':'+tk,bkRow(tk,q,no,secOfCode[q.code]),{mm:'one',row:true,pre:BKTB[tk].pre,post:'</tbody></table>',sub:4.6}))})});
   cols(P,'05 '+ti,'05 '+ti,false,bkPack(us,1,BK_CAPN-10),BKTB[tk])});
  S.subs.forEach(s=>{const arr=S.basic[s.k]||[];if(!arr.length)return;
   const us=arr.map(q=>bkUo('sol:'+q.code+':c',bkSolO(q,basicNo[q.code],secOfType[q.type]),{}));
   cols(P,'05 해설 · '+s.k,'05 해설',true,bkPack(us,2,BK_CAPN))});
  if(T.backc)raw(P,'backc',T.backc);
  P._toc=toc}
 /* ===== 유형서 ===== */
 {const P=tP;const toc=[];
  const [cf,cv]=bkCoverO('유형서','소단원별 유형 문제 · 최상위<br>서술형 · 빠른 정답 · 해설',['소단원별 유형 문제','최상위','서술형','빠른 정답 · 해설']);
  raw(P,'cover cfront',cf);raw(P,'cover',cv);raw(P,'toc','');
  raw(P,'toc guide',bkGuideO(['<b>소단원별 유형 문제</b> — 소단원 → 유형 순서로 정렬되어 있고, 같은 유형 안에서는 쉬운 문제부터 어려운 문제 순이다. 문항마다 난이도가 표시되어 있다.','<b>최상위 · 서술형</b> — 고난도 문제와 서술형이다. 서술형은 해설의 모범 답안과 비교해 스스로 채점한다.','<b>채점</b> — 문제 쪽 아래 <b>QR</b>을 스캔하면 그 쪽이 바로 채점된다. 맨 뒤 빠른 정답으로 직접 채점해도 된다.','<b>문항 코드</b> — 모든 문항에는 C31-001 같은 코드가 있다. 틀린 문항은 코드로 해설과 취약 유형 분석을 찾아본다.','<b>오답 복습</b> — 해설 끝 「이 문제를 틀렸다면 다시 공부할 부분」의 <b>개념서 쪽</b>으로 돌아가 개념을 다시 읽는다.']));
  const typeNo={},typeRange={};
  const addRange=(p)=>p.cols.flat().forEach(u=>{if(u.type){const r=typeRange[u.type]=typeRange[u.type]||[P.pages.length-1,P.pages.length-1];r[0]=Math.min(r[0],P.pages.length-1);r[1]=Math.max(r[1],P.pages.length-1)}});
  toc.push({i:'01',t:'소단원별 유형 문제',n:pgn(P)});P.jumps.push(['소단원별 유형 문제',pgn(P)]);
  raw(P,'divp',bkDivO('04','01','TYPES','소단원별 유형 문제',S.subs.map(s=>[s.k,s.name,S.mc.filter(q=>q.sub===s.k).length+'문항']),'소단원 → 유형 순서로 정렬했다. 같은 유형에서는 쉬운 문제부터 어려운 문제 순이다.'));
  let no=0,si=0;
  S.subs.forEach(s=>{const qs=S.mc.filter(q=>q.sub===s.k);if(!qs.length)return;
   const types=[];qs.forEach(q=>{if(!types.includes(q.type))types.push(q.type)});
   const us=[];const tinfo=[];
   types.forEach((tp,ti)=>{const g=qs.filter(q=>q.type===tp);const f=no+1;
    us.push(bkUo('th:'+s.k+':'+ti+':'+tp,'<div class="ugrp">유형 '+String(ti+1).padStart(2,'0')+' · '+esc(tp)+'</div>',{keep:true}));
    g.forEach(q=>{no++;typeNo[q.code]=no;us.push(bkUo('q:'+q.code+':t',bkQO(q,no,{ut:'난이도 '+bkLv(q)}),{code:q.code,type:tp}))});
    tinfo.push([tp,f+'~'+no+'번 · '+g.length+'문항'])});
   P.jumps.push([s.k+' '+s.name,pgn(P)]);toc.push({s:1,t:s.k+' '+s.name+' ('+qs.length+'문항)',n:pgn(P)});
   raw(P,'subp',bkSubO(si++,s.k,'01 소단원별 유형 문제',s.name,tinfo,'같은 유형끼리 모여 있다. 틀린 유형이 있으면 해설 끝의 개념서 쪽으로 돌아가 개념을 다시 읽는다.'));
   bkPack(us,2,BK_CAPQ).forEach(p=>{cols(P,'01 유형별 문제 · '+s.k,'01 유형별 문제',true,[p],null,true);addRange(p)})});
  const topNo={};
  if(S.top.length){toc.push({i:'02',t:'최상위 도전 문제',n:pgn(P)});P.jumps.push(['최상위 도전',pgn(P)]);
   raw(P,'divp',bkDivO('05','02','CHALLENGE','최상위 도전 문제',S.subs.map(s=>[s.k,s.name,S.top.filter(q=>q.sub===s.k).length+'문항']).filter(r=>r[2]!=='0문항'),'고난도 문제이다. 시간을 정해 놓고 풀고, 틀리면 해설 끝의 개념 위치로 돌아간다.'));
   no=0;const us=[];
   S.subs.forEach(s=>{const qs=S.top.filter(q=>q.sub===s.k);if(!qs.length)return;us.push(bkUo('ug:top:'+s.k,'<div class="ugrp">'+esc(s.k)+' '+esc(s.name)+'</div>',{keep:true}));
    qs.forEach(q=>{no++;topNo[q.code]=no;us.push(bkUo('q:'+q.code+':h',bkQO(q,no,{ut:'난이도 '+bkLv(q)}),{code:q.code,type:q.type}))})});
   bkPack(us,2,BK_CAPQ).forEach(p=>{cols(P,'02 최상위 도전 문제','02 최상위 도전',true,[p],null,true);addRange(p)})}
  const esNo={};
  if(S.essay.length){toc.push({i:'03',t:'서술형 문제',n:pgn(P)});P.jumps.push(['서술형',pgn(P)]);
   raw(P,'divp',bkDivO('06','03','WRITTEN','서술형 문제',[['서술','서술형',S.essay.length+'문항']],'풀이 과정과 근거를 함께 쓴다. 맨 뒤 모범 답안과 비교해 스스로 채점한다.'));
   no=0;const us=S.essay.map(q=>{no++;esNo[q.code]=no;return bkUo('q:'+q.code+':e',bkQO(q,no,{tag:'[서술형]',wans:1}),{code:q.code})});
   cols(P,'03 서술형 문제','03 서술형 문제',true,bkPack(us,2,BK_CAPN))}
  toc.push({i:'04',t:'빠른 정답 · 문제 해설',n:pgn(P)});P.jumps.push(['정답 · 해설',pgn(P)]);P.aStart=pgn(P);
  raw(P,'divp',bkDivO('07','04','SOLUTIONS','빠른 정답 · 문제 해설',[['정답','빠른 정답','채점용'],['해설','소단원별 해설','']],'모든 해설 끝에 「이 문제를 틀렸다면 다시 공부할 부분」이 있다.'));
  const au=[bkUo('qa:h','<div class="blk"><h2 class="sec"><span class="no">정답</span><span>빠른 정답</span><small>채점용</small></h2></div>',{mm:'one',keep:true})];
  S.subs.forEach(s=>{const arr=S.mc.filter(q=>q.sub===s.k);if(arr.length)au.push(bkUo('qa:t:'+s.k+':'+arr.length,bkQa(s.name+' · 유형 문제 '+typeNo[arr[0].code]+'~'+typeNo[arr[arr.length-1].code]+'번',s.k,arr.map(q=>[typeNo[q.code],bkCir(q.ans)])),{mm:'one'}))});
  if(S.top.length)au.push(bkUo('qa:top:'+S.top.length,bkQa('최상위 도전 문제 1~'+S.top.length+'번','최상위',S.top.map(q=>[topNo[q.code],bkCir(q.ans)])),{mm:'one'}));
  cols(P,'04 빠른 정답','04 빠른 정답',false,bkPack(au,1,BK_CAPN));
  const solSec=(lab,qs,numOf)=>{if(!qs.length)return;const us=qs.map(q=>bkUo('sol:'+q.code+':t',bkSolO(q,numOf[q.code],secOfType[q.type]),{}));cols(P,'04 해설 · '+lab,'04 해설',true,bkPack(us,2,BK_CAPN))};
  S.subs.forEach(s=>solSec(s.k,S.mc.filter(q=>q.sub===s.k),typeNo));
  solSec('최상위',S.top,topNo);solSec('서술형',S.essay,esNo);
  if(T.backc)raw(P,'backc',T.backc);
  P.typeRange=typeRange;P._toc=toc}
 [cP,tP].forEach(P=>{P.pages.forEach((p,i)=>p.n=i+1);P.id=SUBJ+'-'+P.kind;P.subj=SUBJ;P.pages[2].inner=bkTocO(P._toc);BKP[P.id]=P});
 const cpage=id=>cP.csec[id]||'';
 const tr=sid=>{const sc=secs.find(x=>x.id===sid);if(!sc)return '';let a=1e9,b=0;(sc.types||[]).forEach(t=>{const r=tP.typeRange[t];if(r){a=Math.min(a,r[0]+1);b=Math.max(b,r[1]+1)}});return b?(a===b?String(a):a+'~'+b):''};
 const subPages={};cP.pages.forEach(p=>{if(!p.codes||!p.codes.length)return;const q0=byCode[p.codes[0]];if(!q0)return;const k=q0.sub;(subPages[k]=subPages[k]||{});const kd=p.label.slice(0,2);(subPages[k][kd]=subPages[k][kd]||[]).push(p.n)});
 const refSub=k=>{const o=subPages[k]||{};const r=[];const f=(a,t)=>{if(a&&a.length)r.push(t+' p.'+(a[0]===a[a.length-1]?a[0]:a[0]+'~'+a[a.length-1]))};f(o['02'],'OX');f(o['03'],'빈칸');f(o['04'],'기초');return r.length?'확인 문제 '+r.join(' · '):''};
 [cP,tP].forEach(P=>P.pages.forEach(p=>{
  const fx=h=>String(h).replace(/\[\[CP:([^\]]+)\]\]/g,(m,id)=>cpage(id)||'–').replace(/\[\[REFSUB:([^\]]+)\]\]/g,(m,k)=>refSub(k)).replace(/<span class="ref">\[\[REFTYPE:([^\]]+)\]\]<\/span>/g,(m,id)=>{const r=tr(id);return r?'<span class="ref">유형서 p.'+r+' 풀기</span>':''});
  if(p.cols)p.cols=p.cols.map(fx);if(p.inner)p.inner=fx(p.inner)}));
 cP.total=Object.values(S.ox).flat().length+Object.values(S.bl).flat().length+Object.values(S.basic).flat().length;
 tP.total=S.mc.length+S.top.length+S.essay.length;
 return {c:cP,t:tP}}

function bkPageO(plan,i){const p=plan.pages[i],n=p.n,pn=n%2?'odd':'even';
 if(p.t==='raw')return '<section class="page '+pn+' '+p.cls+'" data-pn="'+n+'">'+p.inner+'</section>';
 const hb=(BKT.school||'')+' '+SNAME[SUBJ]+' · '+plan.short;
 const L='<span><b>'+esc(hb)+'</b></span>',R='<span><span class="hr">'+esc(p.label)+'</span></span>';
 const qr=p.codes&&p.codes.length;
 const bd='<div class="bd'+(p.two?' two':'')+'">'+p.cols.map(c=>'<div class="col">'+c+'</div>').join('')+'</div>';
 const pt='<span class="pt">'+(qr?'<span class="qrc">'+qrSvg(bkUrl(plan,p))+'</span>':esc(p.foot||''))+'</span>';
 return '<section class="page '+pn+(qr?' qrp':'')+'" data-pn="'+n+'"><div class="hdr">'+(pn==='odd'?L+R:R+L)+'</div>'+bd+'<div class="ftr"><span class="pn">'+n+'</span>'+pt+'</div></section>'}

function bkPlanMock(id,rd){
 const M=BKM&&BKM[rd];if(!M)return {kind:'m',title:'모의고사',short:'모의고사',pages:[{k:'cover'}],toc:[]};
 const qs=M.codes.map(c=>byCode[c]).filter(Boolean);const pages=[{k:'mcv'}];
 const us=qs.map((q,i)=>bkU('mq:'+q.code,bkQHtml(q,i+1,{pt:M.pts[q.code]}),{code:q.code,cls:'mk'}));
 const pp=bkPack(us,2,BK_BODY,BK_BODY-19);const nq=pp.length;
 pp.forEach((p,i)=>pages.push({k:'mq',kind:'q',label:'문제지',idx:i+1,of:nq,first:i===0,cols:p.cols.map(c=>c.map(u=>u.html)),codes:p.cols.flat().map(u=>u.code).filter(Boolean)}));
 // 정답·해설 : 새 레이아웃
 const exu=qs.map((q,i)=>{const e=M.ex[q.code]||{};const lines=(e.core&&!/^<b>/.test(e.core)?[e.core]:[]).concat(e.ch||[]);const items=lines.map(t=>{const m=t.match(/<span class="(o|x)">/);if(!m)return '<li class="sm"><i style="visibility:hidden">·</i><span>'+t+'</span></li>';const ok=m[1]==='o';return '<li><i class="'+(ok?'':'x')+'">'+(ok?'○':'×')+'</i><span>'+t.replace(/<span class="[ox]">[^<]*<\/span>\s*/,'')+'</span></li>'}).join('');
  const html='<div class="u ex"><div class="rl"><b>'+(i+1)+'</b><span>'+bkCir(q.ans)+'</span></div><div class="rb">'+(e.core&&/^<b>/.test(e.core)?'<div class="core">'+e.core.replace(/<b>([^<]*)<\/b>\s*:\s*/,'<b>$1</b> ')+'</div>':'')+(items?'<ul>'+items+'</ul>':'')+'<div class="ft2"><b>개념</b> '+esc(e.need||'')+' <br><b>복습</b> '+esc(e.rv||'')+'</div></div></div>';
  return bkU('mx:'+q.code,html,{cls:'mk ma'})});
 // 요약(정답표)용 높이: 1쪽에 고정 블록
 const sumH=118;const xp=bkPack(exu,2,BK_BODY,BK_BODY-sumH);
 xp.forEach((p,i)=>pages.push({k:'ma',kind:'a',label:'정답 및 해설',idx:i+1,of:xp.length,first:i===0,cols:p.cols.map(c=>c.map(u=>u.html))}));
 return {kind:'m',rd,title:M.title,short:rd+'회 모의고사',pages,toc:[],M,qs,aStart:nq+2,nq}}

/* ---------- 쪽 HTML ---------- */
const BKCAP=BK_BODY;
function bkBase(){if(window.BKBASE)return window.BKBASE;return ((typeof CF!=='undefined'&&CF&&CF.pub)||location.href).split('#')[0].split('?')[0]}
function bkUrl(plan,p){return bkBase()+'#bk='+plan.id+':'+p.n}
function bkHd(l,r,b){return '<div class="hd"><span class="t1">'+l+'</span><span class="t2">'+r+'<b>'+b+'</b></span></div>'}
function bkFt(plan,p,o){o=o||{};const qr=p.codes&&p.codes.length;
 return '<div class="ft"><span class="fl">'+(o.left||'Solvi · '+esc(plan.title))+'</span><span class="pn">'+(o.pn!=null?o.pn:p.n)+'</span>'+
  (qr?'<div class="fr2"><div class="qq">'+qrSvg(bkUrl(plan,p))+'</div></div>':o.right?'<div class="fr2"><span class="fn">'+o.right+'</span></div>':'<div></div>')+'</div>'}
function bkMockCover(plan){const M=plan.M;
 return '<div class="cv2"><div class="row1"><div>'+esc(M.head)+'</div><div>'+esc(M.grade)+'</div><div>'+esc(M.subj)+'</div></div><div class="ttl"><div class="a">실 전 동 형 모 의 고 사</div><div class="b">'+esc(M.sname)+'</div><div class="c">제 '+M.round+' 회 [ '+esc(M.kind)+' ]</div><div class="ln"></div></div>'+
 '<table class="info3"><tr><th>출제 범위</th><td>'+M.range.map(esc).join('<br>')+'</td></tr><tr><th>문항 · 배점</th><td>객관식 '+M.codes.length+'문항 · '+M.tot+'점</td></tr><tr><th>시험 시간</th><td>'+esc(M.time)+'</td></tr></table>'+
 '<div class="note"><h3>유 의 사 항</h3><ol><li>시험 시작 종이 울린 후 문제지의 해당란에 학년, 반, 번호, 이름을 정확히 쓰시오.</li><li>모든 문항은 객관식이며, ①~⑤ 중 가장 적절한 것 하나를 고르시오.</li><li>각 문항의 끝에 표시된 배점을 참고하여 시간을 안배하시오.</li><li>문제지 뒤의 정답 및 해설은 시험이 끝난 후에 확인하시오.</li><li>각 쪽 아래 QR을 스캔하면 그 쪽의 답을 바로 채점할 수 있다.</li></ol></div>'+
 '<table class="idt"><tr><td class="k">학 년</td><td style="width:20mm"></td><td class="k">반</td><td style="width:20mm"></td><td class="k">번 호</td><td style="width:20mm"></td><td class="k">이 름</td><td></td></tr></table><div class="foot">이 문제지의 저작권은 출제자에게 있으며, 무단 복제 · 전재를 금합니다.</div></div>'}
function bkMockSum(plan){const M=plan.M,cs=M.codes;
 const row=(a,b)=>{const ids=cs.slice(a,b);return '<table><tr><th>번호</th>'+ids.map((c,i)=>'<th>'+(a+i+1)+'</th>').join('')+'</tr><tr><th>정답</th>'+ids.map(c=>'<td class="a">'+bkCir(byCode[c].ans)+'</td>').join('')+'</tr><tr><th>배점</th>'+ids.map(c=>'<td>'+M.pts[c]+'</td>').join('')+'</tr></table>'};
 const ar=new Map();cs.forEach((c,i)=>{const a=M.area[c]||'기타';if(!ar.has(a))ar.set(a,{n:[],p:0});const o=ar.get(a);o.n.push(i+1);o.p+=parseFloat(M.pts[c])||0});
 let t='<table><tr><th>영역</th><th>문항</th><th>배점 합</th><th>내 득점</th></tr>';ar.forEach((o,a)=>{t+='<tr><td class="ar">'+esc(a)+'</td><td>'+o.n.join(', ')+'</td><td>'+o.p.toFixed(1)+'</td><td></td></tr>'});
 t+='<tr><th colspan="2">합계</th><th>'+cs.reduce((s,c)=>s+(parseFloat(M.pts[c])||0),0).toFixed(1)+'</th><th></th></tr></table>';
 return '<div class="sc"><h5>정답표</h5>'+row(0,Math.ceil(cs.length/2))+row(Math.ceil(cs.length/2),cs.length)+'</div><div class="sc"><h5>영역별 분석 · 자기 채점</h5>'+t+'</div>'}
function bkPageHtml(plan,i){
 const p=plan.pages[i];if(p.o)return bkPageO(plan,i);
 if(p.k==='mcv')return '<div class="bp mk">'+bkMockCover(plan)+'</div>';
 if(p.k==='mq'||p.k==='ma'){const M=plan.M,mq=p.k==='mq';
  const t1=mq?esc(M.head)+'<em>'+esc(M.grade.replace('제 ','')+' '+M.sname+' · 실전 동형 모의고사 '+M.round+'회')+'</em>':'정답 및 해설<em>'+esc(M.sname)+' · 실전 동형 모의고사 '+M.round+'회 ('+esc(M.kind)+')</em>';
  const h2='<div class="hd"><span class="t1">'+t1+'</span><span class="t2">'+(mq?'문제지':'해설지')+'<b>'+p.idx+' / '+p.of+'</b></span></div>';
  const info=mq&&p.first?'<div class="info"><div class="l">'+esc(M.head.replace(' 대비',''))+' '+esc(M.sname)+' · 제 '+M.round+'회<div><span>학년</span><span>반</span><span>번호</span><span>이름</span></div></div><div class="r">점 수<small>/ '+M.tot+'</small></div></div>':'';
  const sum=!mq&&p.first?'<div style="position:absolute;left:12mm;right:12mm;top:27mm;height:112mm">'+bkMockSum(plan)+'</div>':'';
  const bdc=mq?(p.first?'bd wi':'bd'):(p.first?'bd':'bd');const st=(!mq&&p.first)?' style="top:'+(27+118)+'mm;height:'+(BK_BODY-118)+'mm"':'';
  const cls=mq?'bp mk':'bp mk ma';
  return '<div class="'+cls+'">'+h2+info+sum+'<div class="'+bdc+'"'+st+'><div class="cols">'+p.cols.map(c=>'<div class="col">'+c.join('')+'</div>').join('')+'</div></div>'+
   (mq?bkFt(plan,{...p,n:p.idx},{left:'Solvi · 실전 동형 모의고사',pn:p.idx,right:'※ 제시된 시간 안에 풀고 답을 점검하시오.'}):bkFt(plan,{...p,codes:[]},{left:'Solvi · 정답 및 해설',pn:p.idx,right:'※ 틀린 문항은 「필요한 개념」을 다시 확인하시오.'}))+'</div>'}
}

/* ---------- 채점 · 경로 ---------- */
async function bkGradePage(id,n){
 if(needLogin()){askLogin('BK:'+id+':'+n);return}
 await bkInit();const P=bkParts(id);if(!P)return;
 if(P.subj!==SUBJ)await setSubject(P.subj);
 await conceptLoad();const plan=await bkPlan(id);const p=plan&&plan.pages.find(x=>x.n===+n);
 if(!p||!p.codes||!p.codes.length){const ks=plan?plan.pages.filter(x=>x.codes&&x.codes.length).map(x=>x.n):[];toast('p.'+n+'에는 채점할 문제가 없어요'+(ks.length?' (문제가 있는 쪽: p.'+ks[0]+' ~ p.'+ks[ks.length-1]+')':''));return}
 if(guardStu())return;
  const qs=p.codes.map(c=>byCode[c]).filter(Boolean);if(!qs.length){toast('문항을 불러오지 못했어요');return}
 const key=id+':'+p.n,bk={page:key,bk:id,n:p.n,label:plan.short+' p.'+p.n};
 {const lk=recLock('book',key);if(lk&&lk.items){showLockedRec(lk,{book:bk});return}}
 newCur(qs,{book:bk})}
async function bkGradeAll(id){
 if(needLogin()){askLogin('BK:'+id+':all');return}
 await bkInit();const P=bkParts(id);if(P.subj!==SUBJ)await setSubject(P.subj);
 const plan=await bkPlan(id);if(guardStu())return;
 const qs=(plan.M?plan.M.codes:[]).map(c=>byCode[c]).filter(Boolean);if(!qs.length)return;
 const key=id+':all',bk={page:key,bk:id,n:0,all:1,label:plan.short+' 전체'};
 {const lk=recLock('book',key);if(lk&&lk.items){showLockedRec(lk,{book:bk});return}}
 newCur(qs,{book:bk})}
function bkRouteStr(s){const m=String(s).match(/^((?:me|cm)-(?:c|t|m\d+)):(\d+|all)$/);if(!m)return;return m[2]==='all'?bkGradeAll(m[1]):bkGradePage(m[1],+m[2])}
function bkNextHtml(){const b=cur&&cur.book;if(!b||!b.bk||b.all)return '';const plan=BKP[b.bk];if(!plan)return '';
 const nx=plan.pages.find(p=>p.n>b.n&&p.codes&&p.codes.length);
 return nx?'<div class="hint" style="margin:10px 0">'+esc(plan.short)+' p.'+b.n+' 채점을 마쳤습니다. 다음 문제 쪽(<b>p.'+nx.n+'</b>)도 이어서 채점할까요? <button class="p" style="margin-left:8px" onclick="bkGradePage(\''+b.bk+'\','+nx.n+')">p.'+nx.n+' 채점하기</button></div>':''}

/* ---------- 교재함 · 리더 ---------- */
let BKV={v:'shelf',id:null,z:1};
function bkZoom(d){const Z=[1,1.6,2.4,3.2];let i=Z.indexOf(BKV.z||1);i=Math.max(0,Math.min(Z.length-1,i+d));BKV.z=Z[i];bkScale();const l=document.getElementById('bkzl');if(l)l.textContent=Math.round(Z[i]*100)+'%'}
function bkBookList(){const S=bkSel();const L=[
 {id:SUBJ+'-c',name:'개념서',sub:'개념 정리 · OX · 빈칸 · 기초 5지선다 · 정답 · 해설',meta:'OX '+Object.values(S.ox).reduce((a,x)=>a+x.length,0)+' · 빈칸 '+Object.values(S.bl).reduce((a,x)=>a+x.length,0)+' · 기초 '+Object.values(S.basic).reduce((a,x)=>a+x.length,0)+'문항'},
 {id:SUBJ+'-t',name:'유형서',sub:'소단원별 유형 · 최상위 · 서술형 · 정답 · 해설',meta:'유형 '+S.mc.length+' · 최상위 '+S.top.length+' · 서술형 '+S.essay.length+'문항 (총 '+(S.mc.length+S.top.length+S.essay.length)+')'}];
 if(SUBJ==='cm'&&BKM)Object.keys(BKM).forEach(k=>L.push({id:'cm-m'+k,name:k+'회 실전 모의고사',sub:BKM[k].kind+' · '+BKM[k].codes.length+'문항 · '+BKM[k].time,meta:'문제지 · 정답표 · 해설',mock:1}));
 return L}
async function bkShow(){
 await bkInit();await conceptLoad();await bkLoadTpl();
 if(BKV.id&&bkParts(BKV.id)&&bkParts(BKV.id).subj!==SUBJ){BKV={v:'shelf',id:null}}
 if(BKV.v==='read'&&BKV.id)return bkReader(BKV.id);
 const L=bkBookList(),m=$('#main');
 m.innerHTML=`<div class="card"><h2>교재 <small style="font-weight:400;color:var(--m);font-size:13px">${esc(SNAME[SUBJ])}</small></h2>
 <p style="margin:-4px 0 14px;font-size:13px;color:var(--m);line-height:1.6">책을 열어 보거나 PDF로 인쇄하세요. 문제 쪽 아래의 <b>QR</b>을 스캔하면 그 쪽이 바로 채점됩니다. 아래 「경로로 채점」에서 책 → 구간 → 쪽을 골라 채점할 수도 있어요.</p>
 <div class="bkshelf">${L.map(b=>`<div class="bkcard"><div class="bkcov"><i></i><b>${esc(SNAME[SUBJ])}</b><span>${b.mock?'실전 모의고사':esc(b.name)}</span><em>Solvi</em></div><div class="bi2"><h3>${esc(b.name)}</h3><p>${esc(b.sub)}<br><small>${esc(b.meta)}</small></p><div class="bt2"><button class="p" onclick="bkOpen('${b.id}')">열기</button><button onclick="bkPrint('${b.id}',1)">인쇄 · PDF</button></div></div></div>`).join('')}</div>
 ${SUBJ==='cm'?'':`<p style="margin:14px 0 0;font-size:12.5px;color:var(--m)">실전 모의고사는 「모의고사」 탭에서 직접 만들 수 있어요.</p>`}</div>
 <div class="card"><h2>경로로 채점</h2><p style="margin:-4px 0 12px;font-size:13px;color:var(--m)">QR을 찍을 수 없을 때는 여기서 책 → 구간 → 쪽을 골라 채점하세요.</p>
 <div class="bkpath"><div><label>책</label><select id="bkp1" onchange="bkPath(1)"><option value="">책 고르기</option>${L.map(b=>`<option value="${b.id}">${esc(b.name)}</option>`).join('')}</select></div>
 <div><label>구간</label><select id="bkp2" onchange="bkPath(2)" disabled><option value="">구간 고르기</option></select></div>
 <div><label>쪽</label><select id="bkp3" disabled><option value="">쪽 고르기</option></select></div>
 <div><button class="p" id="bkpg" onclick="bkPathGo()" disabled style="width:100%">채점 시작</button></div></div></div>`}
function bkGroups(plan){const g=new Map();plan.pages.forEach(p=>{if(!p.codes||!p.codes.length)return;const k=plan.kind==='m'?'문제지':(p.label||'');if(!g.has(k))g.set(k,[]);g.get(k).push(p)});return g}
async function bkPath(lv){
 const s1=$('#bkp1'),s2=$('#bkp2'),s3=$('#bkp3'),go=$('#bkpg');
 if(lv===1){s2.innerHTML='<option value="">구간 고르기</option>';s3.innerHTML='<option value="">쪽 고르기</option>';s2.disabled=s3.disabled=go.disabled=true;if(!s1.value)return;
  const plan=await bkPlan(s1.value);BKV._g=bkGroups(plan);BKV._plan=plan;
  s2.innerHTML='<option value="">구간 고르기</option>'+[...BKV._g].map(([k,a])=>`<option value="${esc(k)}">${esc(k)} (${a.length}쪽)</option>`).join('')+(plan.kind==='m'?'<option value="__all">시험 전체 (한 번에)</option>':'');s2.disabled=false;return}
 if(lv===2){s3.innerHTML='<option value="">쪽 고르기</option>';s3.disabled=true;go.disabled=true;const v=s2.value;if(!v)return;if(v==='__all'){go.disabled=false;return}
  const a=BKV._g.get(v)||[];s3.innerHTML=a.map(p=>`<option value="${p.n}">p.${p.n} · ${p.codes.length}문항</option>`).join('');s3.disabled=false;go.disabled=false}}
function bkPathGo(){const id=$('#bkp1').value,v=$('#bkp2').value;if(!id||!v)return;if(v==='__all')return bkGradeAll(id);const n=$('#bkp3').value;if(n)bkGradePage(id,+n)}
function bkOpen(id){BKV={v:'read',id};tab='books';render();scrollTo(0,0)}
function bkClose(){BKV={v:'shelf',id:null};render();scrollTo(0,0)}
function bkScale(){const w=document.getElementById('bkpages');if(!w)return;const W=w.clientWidth;const s=Math.min(1,W/(210*BK_MM))*(BKV.z||1);w.style.setProperty('--bks',s.toFixed(4));w.style.setProperty('--bkw',(210*BK_MM*s)+'px');w.style.setProperty('--bkh',(297*BK_MM*s)+'px')}
async function bkReader(id){
 const m=$('#main');m.innerHTML='<div class="card">'+ldg('책을 펴는 중…')+'</div>';
 const plan=await bkPlan(id);if(!plan){bkClose();return}
 const jumps=[];if(plan.o){plan.jumps.forEach(j=>jumps.push(j))}
 else{jumps.push(['문제지',2],['정답 및 해설',plan.aStart])}
 const seen=new Set();const J=jumps.filter(j=>j[1]&&!seen.has(j[0]+j[1]) && seen.add(j[0]+j[1]));
 m.innerHTML=`<div class="bkrd"><button onclick="bkClose()">‹ 교재함</button><b style="font-size:14px">${esc(plan.title)}</b><select id="bkj" onchange="bkJump(this.value)"><option value="">이동…</option><option value="1">표지</option>${J.map(j=>`<option value="${j[1]}">${esc(j[0])} · p.${j[1]}</option>`).join('')}</select>${plan.kind==='m'?`<button class="p" onclick="bkGradeAll('${id}')">시험 전체 채점</button>`:''}<span class="bkzm"><button onclick="bkZoom(-1)" aria-label="작게">－</button><b id="bkzl">${Math.round((BKV.z||1)*100)}%</b><button onclick="bkZoom(1)" aria-label="크게">＋</button></span><button onclick="bkPrint('${id}',0)">문제만 인쇄</button><button class="p" onclick="bkPrint('${id}',1)">전체 인쇄 · PDF</button></div><div id="bkpages"></div>`;
 const hdr=document.querySelector('header');const rd=document.querySelector('.bkrd');if(rd&&hdr)rd.style.top=(hdr.getBoundingClientRect().height+6)+'px';const box=$('#bkpages');bkScale();
 box.innerHTML=plan.pages.map((p,i)=>`<div class="bkw" id="bkpg${p.n}" data-i="${i}" style="width:var(--bkw);height:var(--bkh)"></div>`+(p.codes&&p.codes.length?`<div class="bkbar" style="width:var(--bkw)"><span><b>p.${p.n}</b> · ${p.codes.length}문항</span><button class="p" onclick="bkGradePage('${id}',${p.n})">이 쪽 채점하기</button></div>`:'<div style="height:10px"></div>')).join('');
 const fill=el=>{if(el.dataset.f)return;el.dataset.f=1;bkShadow(el,plan.o?'<div class="bko scr">'+bkPageHtml(plan,+el.dataset.i)+'</div>':'<div class="bkdoc scr">'+bkPageHtml(plan,+el.dataset.i)+'</div>',plan.o?BKT.all:null)};
 if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){fill(e.target);io.unobserve(e.target)}}),{rootMargin:'900px 0px'});box.querySelectorAll('.bkw').forEach(e=>io.observe(e))}
 else box.querySelectorAll('.bkw').forEach(fill);
 if(!window._bkrs){window._bkrs=1;addEventListener('resize',()=>{if(tab==='books'&&BKV.v==='read')bkScale()})}}
function bkJump(n){const e=document.getElementById('bkpg'+n);if(e){const y=e.getBoundingClientRect().top+scrollY-64;scrollTo({top:y,behavior:'smooth'})}const s=$('#bkj');if(s)s.value=''}

/* ---------- 인쇄 ---------- */
function bkDocHtml(plan,all){
 const abs=location.origin+location.pathname.replace(/[^/]*$/,'');
 const n=all?plan.pages.length:Math.max(1,(plan.aStart||plan.pages.length+1)-1);
 let pg='';for(let i=0;i<n;i++)pg+=bkPageHtml(plan,i);
 if(plan.o)return '<!doctype html><html><head><meta charset="utf-8"><title>'+esc(plan.title)+'</title><link rel="stylesheet" href="'+BKCDN+'"><style>'+bkFontCss(abs)+BKT.all+'@page{size:A4;margin:0}html,body{margin:0;padding:0}.bko{background:#dfe6ee!important}.bko .page{margin:6mm auto!important}@media print{.bko{background:#fff!important}.bko .page{margin:0!important;box-shadow:none!important}}</style></head><body class="bko">'+pg+'</body></html>';
 return '<!doctype html><html><head><meta charset="utf-8"><title>'+esc(plan.title)+'</title><link rel="stylesheet" href="'+BKCDN+'"><style>'+bkFontCss(abs)+'@page{size:A4;margin:0}html,body{margin:0;padding:0;background:#d9dde3}'+BKCSS+'.bkdoc .bp{margin:8mm auto;box-shadow:0 1px 8px rgba(0,0,0,.25);page-break-after:always;break-after:page}.bkdoc .bp:last-child{page-break-after:auto;break-after:auto}@media print{html,body{background:#fff}.bkdoc .bp{margin:0;box-shadow:none}}</style></head><body class="bkdoc">'+pg+'</body></html>'}
async function bkPrint(id,all){
 const pw=typeof popOpen==='function'?popOpen('인쇄할 책을 만드는 중…'):null;
 await bkInit();const P=bkParts(id);if(P&&P.subj!==SUBJ)await setSubject(P.subj);
 busyRun('인쇄할 책을 만드는 중…',async()=>{await conceptLoad();const plan=await bkPlan(id);if(!plan){if(pw)pw.close();return}await cbPrintHtml(bkDocHtml(plan,all),pw)})}

/* ---------- 단독 HTML 파일(내려받아 열어보는 교재) ---------- */
function bkStandalone(plan){
 const cdn='';
 let pg='';for(let i=0;i<plan.pages.length;i++)pg+=bkPageHtml(plan,i);
 return '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(plan.title)+'</title><link rel="stylesheet" href="'+BKCDN+'"><style>'+cdn+(plan.o?BKT.all.replace(/\.bko\{background:none!important\}/,'')+'html,body{margin:0;padding:0;background:#dfe6ee}.bko{background:#dfe6ee!important}':'@page{size:A4;margin:0}*{box-sizing:border-box}html,body{margin:0;padding:0;background:#d9dde3}'+BKCSS+'.bkdoc .bp{margin:8mm auto;box-shadow:0 1px 8px rgba(0,0,0,.25)}@media print{html,body{background:#fff}.bkdoc .bp{margin:0;box-shadow:none;page-break-after:always;break-after:page}.bkdoc .bp:last-child{page-break-after:auto;break-after:auto}}')+'</style></head><body class="'+(plan.o?'bko':'bkdoc')+'">'+pg+'<script>(function(){function f(){var s=Math.min(1,innerWidth/(210*96/25.4+16));document.body.style.zoom=s<1?s:""}f();addEventListener("resize",f);addEventListener("beforeprint",function(){document.body.style.zoom=""});addEventListener("afterprint",f)})()</script></body></html>'}
/* ---------- 높이표 만들기(개발용) : 콘솔/자동화에서 await bkMeasureAll() ---------- */
let BKREC=null;
async function bkMeasureAll(){
 await bkInit();await bkLoadTpl();BKHT={};const subj=SUBJ;const ids=[subj+'-c',subj+'-t',...(BKM&&subj==='cm'?Object.keys(BKM).map(k=>'cm-m'+k):[])];
 for(let pass=0;pass<8;pass++){
  delete BKSELC[subj];ids.forEach(id=>delete BKP[id]);
  BKREC=[];for(const id of ids)await bkPlan(id);
  const rec=BKREC;BKREC=null;const todo=rec.filter(u=>BKHA[u.key]==null);
  const seen=new Set();let n=0;
  for(const u of todo){if(seen.has(u.key))continue;seen.add(u.key);BKHA[u.key]=await bkMeasureUnitAsync(u);n++}
  if(!n)break}
 delete BKSELC[subj];ids.forEach(id=>delete BKP[id]);for(const id of ids)await bkPlan(id);
 return BKHA}
window.bkShow=bkShow;
