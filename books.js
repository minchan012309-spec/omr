/* Solvi 교재 — 개념서 · 유형서 · 실전 모의고사
   index.html 의 전역(DATA, CONC, byCode, SUBJ …)을 그대로 사용하는 보조 스크립트입니다. 교재 탭을 처음 열 때 불러옵니다.
   쪽 나눔은 books/heights.json 에 저장된 문항 높이로 계산하므로 어느 기기에서나 같은 쪽 번호가 나옵니다(QR 쪽 채점용). */
const BK_MM=96/25.4,BK_BODY=240,BK_COLW=89,BK_FULLW=186;
const BKP={},BKSELC={},BKH={};let BKHT=null,BKREADY=null;
const BKCIR='①②③④⑤⑥⑦⑧⑨⑩';
const bkLv=q=>q.lv0||q.lv||'';
const BKPAL={cm:{p:'#2f9d66',pd:'#1f7d4e',pl:'#eefcf5',pl2:'#d9f8e8',line:'#b0e3c9'},me:{p:'#2f7fd0',pd:'#1d5ca6',pl:'#eef5fc',pl2:'#d9e8f8',line:'#b9cfe6'},ph:{p:'#6d4cc4',pd:'#5a3bad',pl:'#f3effc',pl2:'#e4dbf8',line:'#cdbfef'}};
const BKPADS=[2.8,4.5,6.5,9];
let BKO=(()=>{try{return JSON.parse(localStorage.getItem('omr_bko')||'{}')}catch(e){return {}}})();
const bkOsig=()=>(BKO.color||'')+'|'+(BKO.font||'')+'|'+(BKO.design||'');
function bkOset(o){Object.assign(BKO,o);try{localStorage.setItem('omr_bko',JSON.stringify(BKO))}catch(e){}}
let BKDZ=null;
const bkPal=()=>{const ck=(BKDZ&&BKDZ.color)||BKO.color;if(ck&&typeof PAL!=='undefined'&&PAL[ck]){const v=PAL[ck];return {p:v[0],pd:v[1],pl:v[2],pl2:v[3],line:v[3]}}return BKPAL[SUBJ]||BKPAL.cm};
const bkVars=()=>{const c=bkPal();return '--p:'+c.p+';--pd:'+c.pd+';--pl:'+c.pl+';--pl2:'+c.pl2+';--line:'+c.line+';--y:#ffca2c'};
const bkCir=a=>String(a).split(',').map(x=>BKCIR[(+x)-1]||x).join(', ');

/* ---------- 스타일 ---------- */
const BKCSS=`
@font-face{font-family:Paperozi;src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@1.0/Paperlogy-4Regular.woff2') format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:Paperozi;src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@1.0/Paperlogy-5Medium.woff2') format('woff2');font-weight:500;font-display:swap}
@font-face{font-family:Paperozi;src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@1.0/Paperlogy-7Bold.woff2') format('woff2');font-weight:700;font-display:swap}
@font-face{font-family:Paperozi;src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@1.0/Paperlogy-8ExtraBold.woff2') format('woff2');font-weight:800;font-display:swap}
@font-face{font-family:Paperozi;src:url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@1.0/Paperlogy-9Black.woff2') format('woff2');font-weight:900;font-display:swap}
.bkdoc{font-family:Pretendard,PretendardLocal,'Noto Sans CJK KR','Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;color:#111;font-weight:400;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all;overflow-wrap:break-word}
.bkdoc *{box-sizing:border-box}
.bkdoc i{font-family:'Times New Roman','Noto Serif CJK KR',serif;font-style:italic}.bkdoc sub,.bkdoc sup{font-size:70%;line-height:0}
.bkdoc .bkblank .bklg{position:absolute;right:12mm;bottom:10mm;display:flex;align-items:center;gap:1.4mm;font:800 8.5pt/1 Pretendard,sans-serif;letter-spacing:-.02em;color:#8a96a6}.bkdoc .bkblank .bklg svg{height:6.5mm;width:auto;display:block}.bkdoc .bkblank .bklg img{height:6.5mm;width:auto;max-width:34mm;object-fit:contain;display:block}.bkdoc .bkblank .bklg .bld{width:.3mm;height:5mm;background:#9aa5b1;display:block}.bkdoc .bkblank .bklg .blt{font-weight:800;font-size:8.5pt;color:#8a96a6;white-space:nowrap}
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
.bkdoc .col>.u+.u{padding-top:var(--g,0mm)}
.bkdoc .ft{position:absolute;left:12mm;right:12mm;bottom:7mm;height:20mm;border-top:.7px solid #111;display:grid;grid-template-columns:1fr auto 1fr;align-items:center}
.bkdoc .ft .fl{font-size:9.5px;color:#444}
.bkdoc .ft .pn{font-size:12px;font-weight:700;text-align:center}
.bkdoc .ft .fr2{justify-self:end;display:flex;align-items:center;gap:2.4mm}
.bkdoc .ft .qt{font-size:9px;line-height:1.35;color:#333;text-align:right}.bkdoc .ft .qt b{display:block;font-size:10px;color:#111}
.bkdoc .ft .qq{width:11mm;height:11mm;border:0;padding:0;background:none;display:flex;align-items:center;justify-content:center}
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
.bkdoc .u.q .bogi{position:relative;padding-top:3.4mm;margin-top:4.4mm}
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
.bkdoc .u.q .fr,.bkdoc .fr{text-indent:0;display:inline-block;vertical-align:middle;text-align:center;line-height:1.12;margin:0 .6mm}.bkdoc .fr>span{display:block;padding:0 .6mm}.bkdoc .fr>span:first-child{border-bottom:.6px solid #111}
.bkdoc .u.q .ptn{text-align:right;font-size:10.5px;color:#444}
.bkdoc .u.q .gi{border:.6px solid #111;padding:1.4mm 2mm;margin:1.6mm 0}
.bkdoc .u.q .ans{margin-top:1.6mm;border:.6px solid #111;padding:.8mm 2.4mm}.bkdoc .u.q .ans div{height:6.4mm;border-bottom:.6px dotted #888}.bkdoc .u.q .ans div:last-child{border-bottom:0}
/* ---- 교재(개념서·유형서) : 포인트 색을 절제해서 쓴 서식 ---- */
.bkdoc .hd2{position:absolute;left:12mm;right:12mm;top:8mm;height:7mm;border-bottom:.3mm solid var(--line);display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:1.4mm;font-size:9.5px;color:#555;line-height:1}
.bkdoc .hd2 b{color:#111;font-weight:600}.bkdoc .hd2 .lb2{color:var(--pd);font-weight:600}
.bkdoc .hd2 .lb2:before,.bkdoc .fb .lab:before{content:"";display:inline-block;width:1.6mm;height:1.6mm;border-radius:50%;background:var(--y);margin-right:1.6mm;vertical-align:.05mm}
.bkdoc .fb{position:absolute;left:12mm;right:12mm;bottom:7mm;height:18mm;border-top:.25mm solid var(--line);display:grid;grid-template-columns:1fr auto 1fr;align-items:center;font-size:9.5px;color:#555;line-height:1}
.bkdoc .fb .pn{color:var(--p);font-weight:700;font-size:13.5px;min-width:12mm}.bkdoc .fb .pn.r{text-align:right}.bkdoc .fb>:first-child{justify-self:start}.bkdoc .fb>:last-child{justify-self:end}.bkdoc .bp[data-gut]>*{transform:translateX(var(--gx))}
.bkdoc .fq{position:absolute;bottom:26mm;width:9.5mm;height:9.5mm;z-index:2}.bkdoc .fq.o-l{left:12mm}.bkdoc .fq.o-r{right:12mm}.bkdoc .fq .qq{width:100%;height:100%;border:0;padding:0;background:none}.bkdoc .fq svg{width:100%;height:100%;display:block}
.bkdoc .fb .qrb{display:flex;align-items:center;gap:2.8mm}
.bkdoc .fb .qt{font-size:9.2px;line-height:1.45;color:#444}
.bkdoc .fb .qq{width:11mm;height:11mm;border:0;padding:0;background:none;display:flex;align-items:center;justify-content:center}.bkdoc .fb .qq svg{width:100%;height:100%;display:block}
.bkdoc .bk .bd{top:21mm;height:${BK_BODY}mm}
.bkdoc .bk .cols:before{border-left:.3mm solid var(--line)}
.bkdoc .ct{background:var(--pl);color:var(--pd);font-weight:800;font-size:12.5px;padding:1.5mm 3mm;border-radius:1.6mm;margin:0 0 3.6mm;display:flex;gap:2.4mm;align-items:baseline}
.bkdoc .ct small{margin-left:auto;font-weight:600;font-size:10px;color:var(--p)}
.bkdoc .ct.sm{font-size:11.5px;padding:1mm 2.6mm;margin-bottom:1.8mm}
.bkdoc .sbn{margin:0 0 6mm;padding:4.6mm 5.2mm 4.2mm;background:var(--pl);border-radius:3mm}
.bkdoc .sbn b{display:block;position:relative;font-size:19px;font-weight:800;letter-spacing:-.5px;line-height:1.3;padding-bottom:2.4mm}
.bkdoc .sbn b:after{content:"";position:absolute;left:0;bottom:0;width:14mm;height:1.2mm;background:var(--y);border-radius:1mm}
.bkdoc .sbn b i{font-style:normal;font-family:inherit;color:var(--p);margin-right:2.6mm}
.bkdoc .sbn .g{display:block;margin-top:2.8mm;font-size:11px;color:#444;line-height:1.55}
.bkdoc .sbn .rf{display:flex;gap:1.6mm;flex-wrap:wrap;margin-top:3mm}.bkdoc .sbn .rf em{font-style:normal;font-size:9.5px;background:#fff;color:var(--pd);border:.25mm solid var(--line);border-radius:2mm;padding:.3mm 2.4mm;font-weight:600}
.bkdoc .th{display:flex;gap:2.4mm;align-items:baseline;margin:1mm 0 4.2mm;padding-bottom:1.3mm;border-bottom:.3mm solid var(--line);font-size:12.6px;font-weight:800}
.bkdoc .th b{color:var(--p);font-size:10.5px;letter-spacing:.4px;white-space:nowrap}
.bkdoc .th small{margin-left:auto;color:#d9a300;letter-spacing:1px;font-weight:600;font-size:10.5px;white-space:nowrap}
.bkdoc .sh2{display:flex;gap:2.6mm;align-items:center;margin:2.4mm 0 3.2mm;padding-bottom:1.6mm;border-bottom:.3mm solid var(--line);font-size:14px;font-weight:800;line-height:1.3}
.bkdoc .sh2 i{flex:none;width:6.6mm;height:6.6mm;line-height:6.6mm;border-radius:50%;background:var(--p);color:#fff;text-align:center;font-style:normal;font-family:inherit;font-size:11.5px}
.bkdoc .bk .u.q{margin:0 0 9mm;font-size:12.4px;line-height:1.64}
.bkdoc .bk .u.q .qs p{margin:0 0 2.2mm}
.bkdoc .bk .u.q .no{color:var(--pd);font-size:15px}
.bkdoc .bk .u.q .qh2{display:flex;justify-content:space-between;align-items:baseline;margin:0 0 1.8mm;padding-bottom:1mm;border-bottom:.25mm solid var(--line)}.bkdoc .bk .u.q .cd{font-size:9px;color:#8a8f98;font-weight:500;letter-spacing:.2px}
.bkdoc .bk .u.q .fg{margin:2.2mm 0}
.bkdoc .bk .u.q .bogi,.bkdoc .bk .u.q .bxx{margin:2.6mm 0}
.bkdoc .bk .u.q .chs{margin-top:1.8mm}
.bkdoc .u.o{display:flex;gap:2mm;margin:0 0 4.6mm;font-size:12.2px;line-height:1.62;align-items:flex-start}
.bkdoc .u.o .nc{flex:none;width:11.5mm}.bkdoc .u.o .nc b{display:block;font-size:13.5px;color:var(--pd);font-weight:800;line-height:1.3}
.bkdoc .u.o .nc small{display:block;font-size:7.6px;color:#999;line-height:1.2;letter-spacing:.1px}
.bkdoc .u.o .tx{flex:1;text-align:justify}
.bkdoc .u.o .bx{flex:none;width:10mm;height:6.2mm;border:.3mm solid var(--p);border-radius:1mm;margin-left:1.2mm;align-self:center;text-align:center;line-height:5.6mm;font-size:9.5px;color:#aaa}
.bkdoc .u.o .bk{display:inline-block;min-width:14mm;text-align:center;border-bottom:.3mm solid #333;font-weight:700;color:#777;line-height:1.1;margin:0 .6mm}
.bkdoc .u.b .tx{line-height:1.8}
.bkdoc .u.x{margin:0 0 5.4mm;font-size:10.9px;line-height:1.58}
.bkdoc .u.x .xh{display:flex;gap:2.2mm;align-items:baseline;border-bottom:.3mm solid var(--line);padding-bottom:.9mm;margin-bottom:1.4mm}
.bkdoc .u.x .xn{font-size:14px;font-weight:800;color:var(--pd)}
.bkdoc .u.x .xa{font-weight:700;background:var(--pl2);color:var(--pd);padding:0 1.8mm;border-radius:1mm;font-size:10.8px}
.bkdoc .u.x .xm{margin-left:auto;font-size:8.6px;color:#999;text-align:right;line-height:1.3}
.bkdoc .u.x .xb p{margin:1mm 0}
.bkdoc .u.x .lb{display:inline-block;font-size:9px;font-weight:700;background:var(--pl2);color:var(--pd);border-radius:1mm;padding:0 1.4mm;margin-right:1.2mm;line-height:3.6mm;vertical-align:1px}
.bkdoc .u.x .ss{display:none}
.bkdoc .u.x .o{color:var(--pd);font-weight:800}.bkdoc .u.x .x{color:#c0392b;font-weight:800}
.bkdoc .u.k{margin:0 0 5mm}
.bkdoc .u.k .kg{display:grid;grid-template-columns:repeat(5,1fr);border-top:.25mm solid var(--line);border-left:.25mm solid var(--line)}
.bkdoc .u.k .kg div{border-right:.25mm solid var(--line);border-bottom:.25mm solid var(--line);padding:.9mm 1.6mm;font-size:10.8px;line-height:1.4;display:flex;justify-content:space-between;gap:1mm}
.bkdoc .u.k .kg div b{font-weight:800;color:var(--pd)}.bkdoc .u.k .kg.w2{grid-template-columns:repeat(2,1fr)}.bkdoc .u.k .kg div span{text-align:right}
/* 개념 본문 */
.bkdoc .cbk{font-size:12.8px;line-height:1.72;color:#17251e}
.bkdoc .cbk p{margin:0 0 1.8mm}.bkdoc .cbk b,.bkdoc .cbk strong{font-weight:700}
.bkdoc .cbk .hl{background:linear-gradient(transparent 38%,#fff06b 38%,#fff06b 94%,transparent 94%);padding:0 .3mm;font-weight:700;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.bkdoc .cbk h4{margin:3.2mm 0 1.6mm;font-size:13px;font-weight:700;color:var(--pd)}.bkdoc .cbk h4:before{content:"";display:inline-block;width:2.2mm;height:2.2mm;background:var(--y);border-radius:50%;margin-right:1.8mm;vertical-align:.1mm}
.bkdoc .cbk ul.l{margin:.6mm 0 2.2mm;padding-left:4.6mm;list-style:none}.bkdoc .cbk ul.l>li{position:relative;margin:.7mm 0}
.bkdoc .cbk ul.l>li:before{content:"";position:absolute;left:-4mm;top:.68em;width:1.5mm;height:1.5mm;background:var(--p)}
.bkdoc .cbk ul.l ul.l>li:before{background:#fff;border:.3mm solid var(--p)}
.bkdoc .cbk table.tb{width:100%;border-collapse:collapse;margin:2mm 0 3.4mm;font-size:11.5px;line-height:1.5;background:#fff}
.bkdoc .cbk table.tb th{background:var(--p);color:#fff;border:.25mm solid var(--p);padding:1.2mm 1.8mm;font-weight:600;text-align:center}
.bkdoc .cbk table.tb td{border:.25mm solid var(--line);padding:1.2mm 1.8mm;text-align:center;vertical-align:middle}
.bkdoc .cbk table.tb td.l,.bkdoc .cbk table.tb th.l{text-align:left}.bkdoc .cbk table.tb td.b{font-weight:700;white-space:nowrap}
.bkdoc .cbk .nt{margin:5mm 0 3.4mm;padding:3.6mm 3.6mm 1.6mm;border:.3mm solid var(--pl2);border-radius:2mm;background:var(--pl);position:relative;break-inside:avoid}
.bkdoc .cbk .nt>.lb{display:inline-block;font-size:10px;font-weight:700;color:#fff;background:var(--p);border-radius:1.2mm;padding:0 2.2mm;margin:-6.8mm 0 1.4mm;line-height:4.4mm}
.bkdoc .cbk .nt.wa{border-color:#f3dd8c;background:#fff8dc}.bkdoc .cbk .nt.wa>.lb{color:#4a3600;background:var(--y)}
.bkdoc .cbk .nt.ds{background:#fff;border-color:var(--p)}.bkdoc .cbk .nt.es{background:#fff;border:.3mm dashed var(--p)}
.bkdoc .cbk .eqn{margin:2mm 0 3mm;padding:1.6mm 2.4mm;text-align:center;font-weight:700;border-top:.3mm solid var(--p);border-bottom:.3mm solid var(--p);background:#fff}
.bkdoc .cbk .eqn small{display:block;font-weight:400;font-size:.88em;color:#555}
.bkdoc .cbk .fg{margin:2mm 0 3mm;text-align:center;break-inside:avoid}.bkdoc .cbk .fg img,.bkdoc .cbk .fg svg{max-width:100%;height:auto;max-height:66mm}
.bkdoc .cbk .fg .cap{font-size:10.6px;color:#555;margin-top:1mm}
.bkdoc .cbk .two-c{display:grid;grid-template-columns:1fr 1fr;gap:5mm;align-items:start}
.bkdoc .cbk .tag{display:inline-block;font-size:.9em;font-weight:700;color:#fff;background:var(--p);padding:0 1.2mm;margin-right:1mm}
.bkdoc .cbk .tp{white-space:nowrap}.bkdoc .cbk .sm{font-size:.92em;color:#555}
.bkdoc .cbk .fr{text-indent:0;display:inline-block;vertical-align:middle;text-align:center;line-height:1.12;margin:0 .6mm}.bkdoc .cbk img{max-width:100%}
/* 표지 */
.bkdoc .cv{position:absolute;inset:0;overflow:hidden}
.bkdoc .cv .c1{position:absolute;left:16mm;right:16mm;top:14mm;display:flex;justify-content:space-between;font-size:10.5px;letter-spacing:2px;color:#444;font-weight:600;padding-bottom:3mm;border-bottom:.3mm solid var(--line)}
.bkdoc .cv .c1 span:first-child:before{content:"";display:inline-block;width:1.8mm;height:1.8mm;border-radius:50%;background:var(--y);margin-right:2mm;vertical-align:.1mm}
.bkdoc .cv .c2{position:absolute;left:16mm;right:16mm;top:56mm}
.bkdoc .cv .bar{width:16mm;height:1.8mm;background:var(--y);border-radius:1mm;margin-bottom:8mm}
.bkdoc .cv .kd{font-size:13px;font-weight:700;letter-spacing:5px;color:var(--p)}
.bkdoc .cv h1{margin:5mm 0 0;font-size:52px;line-height:1.12;font-weight:800;letter-spacing:-1.8px;color:#17251e}
.bkdoc .cv h2{margin:3mm 0 0;font-size:30px;font-weight:300;letter-spacing:1px;color:#333}
.bkdoc .cv .ln{margin:11mm 0 0;border-top:.6mm solid var(--p);width:100%}
.bkdoc .cv ul{list-style:none;margin:8mm 0 0;padding:0;font-size:12.5px;line-height:2;width:60%}
.bkdoc .cv li{display:flex;gap:4mm;border-bottom:.2mm solid var(--line);padding:.4mm 0}.bkdoc .cv li b{width:24mm;flex:none;font-weight:700;color:var(--pd)}
.bkdoc .cv .deco{position:absolute;right:8mm;bottom:50mm;width:96mm;height:96mm}
.bkdoc .cv .c3{position:absolute;left:16mm;right:16mm;bottom:22mm;border-collapse:collapse;width:calc(100% - 32mm);font-size:13px}
.bkdoc .cv .c3 td{border:.3mm solid var(--line);height:13mm;text-align:center}.bkdoc .cv .c3 td.k{width:21mm;font-weight:800;letter-spacing:3px;background:var(--pl);color:var(--pd)}
.bkdoc .cv.nv{position:absolute;inset:0;overflow:hidden;color:#f4f6f3;background:radial-gradient(120% 90% at 85% 55%,var(--c3,#1a3d7c) 0%,rgba(0,0,0,0) 60%),linear-gradient(160deg,var(--c1,#081a3d) 0%,var(--c2,#0e2a5c) 100%);font-family:Paperozi,Pretendard,PretendardLocal,'Noto Sans KR',sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.bkdoc .cv.nv::after{content:'';position:absolute;inset:0;background:repeating-linear-gradient(115deg,rgba(255,255,255,.018) 0 2px,rgba(255,255,255,0) 2px 7px);pointer-events:none}
.bkdoc .cv.nv .wm{position:absolute;left:72mm;top:46mm;font-size:250mm;font-weight:900;line-height:1;color:rgba(255,255,255,.07)}
.bkdoc .cv.nv .tl{position:absolute;top:26mm;left:24mm}.bkdoc .cv.nv .sr{font-size:4.2mm;font-weight:800;letter-spacing:.34em}.bkdoc .cv.nv .bk{margin-top:1.6mm;font-size:3.4mm;font-weight:400;opacity:.8}
.bkdoc .cv.nv .tb{position:absolute;left:24mm;top:90mm;right:20mm}.bkdoc .cv.nv .sm{position:relative;display:inline-block;font-size:11mm;font-weight:800;letter-spacing:.1em;color:rgba(255,255,255,.55);line-height:1}.bkdoc .cv.nv .sm::after{content:'';position:absolute;left:-1mm;right:-1mm;top:52%;height:.9mm;background:var(--acc,#ffc933)}
.bkdoc .cv.nv .bg{margin-top:6mm;font-size:27mm;font-weight:800;line-height:1.02;letter-spacing:-.035em;color:#f4f6f3}.bkdoc .cv.nv .ru{margin-top:14mm;width:30mm;height:2.4mm;background:var(--acc,#ffc933)}.bkdoc .cv.nv .ko{margin-top:6mm;font-size:8.4mm;font-weight:800;letter-spacing:-.01em}.bkdoc .cv.nv .bn{margin-top:3mm;font-size:4.2mm;font-weight:500;opacity:.75}
.bkdoc .cv.nv .sb{position:absolute;left:24mm;bottom:23mm}.bkdoc .cv.nv .sl{font-size:4.4mm;font-weight:500;letter-spacing:.22em;color:rgba(255,255,255,.6)}.bkdoc .cv.nv .sn{margin-top:1mm;font-size:13mm;font-weight:800;letter-spacing:-.02em;line-height:1.1}.bkdoc .cv.nv .gr{display:inline-block;margin-top:3mm;padding:1.6mm 6mm;background:var(--acc,#ffc933);color:var(--on,#081a3d);border-radius:2.5mm;font-size:6.2mm;font-weight:700}
.bkdoc .cv.nv.bkn{background:radial-gradient(120% 90% at 15% 55%,var(--c3,#1a3d7c) 0%,rgba(0,0,0,0) 60%),linear-gradient(160deg,var(--c1,#081a3d) 0%,var(--c2,#0e2a5c) 100%)}.bkdoc .cv.nv.bkn .wm{left:auto;right:60mm}
.bkdoc .cv.nv .ct2{position:absolute;left:0;right:0;top:112mm;text-align:center}.bkdoc .cv.nv .ct2 .ru{margin:0 auto 10mm}.bkdoc .cv.nv .ct2 .bg{margin-top:0;font-size:16.2mm}.bkdoc .cv.nv .ct2 .ko{margin-top:8mm;font-size:6mm;font-weight:500;opacity:.9}
.bkdoc .cv.nv .bt2{position:absolute;left:24mm;right:24mm;bottom:23mm;display:flex;justify-content:space-between;align-items:flex-end}.bkdoc .cv.nv .bt2 .sr{font-size:3.8mm}.bkdoc .cv.nv .sc2{text-align:right;font-size:5mm;font-weight:700}.bkdoc .cv.nv .sc2 span{display:inline-block;margin-left:2mm;padding:.8mm 3.6mm;background:var(--acc,#ffc933);color:var(--on,#081a3d);border-radius:2mm;font-size:4.4mm}
.bkdoc .cv.cs1 .deco,.bkdoc .cv.cs2 .deco{display:none}
.bkdoc .cvlogo{position:absolute;bottom:24mm;height:10mm;display:flex;align-items:center}.bkdoc .cvlogo.L{left:24mm}.bkdoc .cvlogo.R{right:24mm}.bkdoc .cvlogo.C{left:0;right:0;justify-content:center}.bkdoc .cv.cs3 .cvlogo.C{left:30mm}.bkdoc .cvlogo .lg{height:10mm;width:auto;max-width:46mm;object-fit:contain;display:block}.bkdoc .cvlogo .tx,.bkdoc .cvlg .tx{font-weight:800;font-size:13px;color:var(--pd);white-space:nowrap}
.bkdoc .cvb{position:absolute;inset:0;overflow:hidden;background:var(--pl)}.bkdoc .cvb:before{content:"";position:absolute;left:0;right:0;top:0;height:7mm;background:var(--p)}.bkdoc .cvb .cvbt{position:absolute;left:24mm;right:24mm;top:104mm;text-align:center}.bkdoc .cvb .cvbt b{display:block;font-size:30px;font-weight:800;color:var(--pd);letter-spacing:-.5px}.bkdoc .cvb .cvbt span{display:block;margin-top:4mm;font-size:14px;color:#445}
.bkdoc .cvb .cvlg{position:absolute;left:0;right:0;display:flex;justify-content:center}.bkdoc .cvb .cvlg.bc{bottom:44mm}.bkdoc .cvb .cvlg.tc{top:44mm}.bkdoc .cvb .cvlg .lg{height:16mm;width:auto;max-width:70mm;object-fit:contain}
.bkdoc .cv.cs3 .deco,.bkdoc .cv.cs4 .deco,.bkdoc .cv.cs5 .deco{display:none}
.bkdoc .cv.cs3:before{content:"";position:absolute;left:0;top:0;bottom:0;width:30mm;background:var(--p)}.bkdoc .cv.cs3 .c1{left:42mm}.bkdoc .cv.cs3 .c2{left:42mm;top:62mm}.bkdoc .cv.cs3 .c3{left:42mm;width:calc(100% - 58mm)}.bkdoc .cv.cs3 h1{font-size:46px}.bkdoc .cv.cs3 .cvlogo.L{left:44mm}
.bkdoc .cv.cs4 .c1{left:22mm;right:22mm}.bkdoc .cv.cs4 .c2{left:22mm;right:22mm;top:70mm;text-align:center}.bkdoc .cv.cs4 .ln{width:40%;margin-left:auto;margin-right:auto}.bkdoc .cv.cs4 ul{width:80%;margin-left:auto;margin-right:auto;text-align:left}.bkdoc .cv.cs4 .bar{margin-left:auto;margin-right:auto}.bkdoc .cv.cs4 .c4{bottom:15mm}
.bkdoc .cv.cs5:before{content:"";position:absolute;left:0;right:0;bottom:0;height:104mm;background:var(--p)}.bkdoc .cv.cs5 .c2{top:40mm}.bkdoc .cv.cs5 ul{margin-top:6mm}.bkdoc .cv.cs5 .c3{bottom:30mm;background:#fff}.bkdoc .cv.cs5 .c4{color:#fff;bottom:12mm}.bkdoc .cv.cs5 .cvlogo{bottom:24mm}.bkdoc .cv.cs5 .cvlogo svg path:first-child{fill:#fff}.bkdoc .cv.cs5 .cvlogo .tx{color:#fff}
.bkdoc .cv.cs1:before{content:"";position:absolute;left:0;right:0;top:0;height:108mm;background:var(--p)}.bkdoc .cv.cs1 .c2{top:44mm}.bkdoc .cv.cs1 .c1{color:#fff}.bkdoc .cv.cs1 .c1 span:first-child:before{background:#fff}.bkdoc .cv.cs1 .bar{background:#fff}.bkdoc .cv.cs1 .kd,.bkdoc .cv.cs1 h1,.bkdoc .cv.cs1 h2{color:#fff}.bkdoc .cv.cs1 .ln{border-color:#fff8;margin-top:8mm}.bkdoc .cv.cs1 ul{margin-top:20mm;width:72%}
.bkdoc .cv.cs2 .c2{top:78mm}.bkdoc .cv.cs2 .bar{width:44mm;height:2.4mm}.bkdoc .cv.cs2 h1{font-size:46px}.bkdoc .cv.cs2 ul{width:70%}
.bkdoc .cv .c4{position:absolute;left:0;right:0;bottom:9mm;text-align:center;font-size:10px;color:#666;letter-spacing:.3px}
/* 차례 */
.bkdoc .toc h3{margin:0 0 6mm;padding-bottom:3mm;font-size:22px;font-weight:800;letter-spacing:3px;border-bottom:.6mm solid var(--p)}
.bkdoc .toc table{width:100%;border-collapse:collapse;font-size:12.6px;line-height:1.5;margin-bottom:7mm}
.bkdoc .toc th{background:var(--p);color:#fff;font-weight:600;padding:1.4mm 2mm;font-size:11.5px}
.bkdoc .toc td{border-bottom:.25mm solid var(--line);padding:1.8mm 2mm;vertical-align:top}.bkdoc .toc td.n{text-align:center;white-space:nowrap;font-variant-numeric:tabular-nums;color:var(--pd);font-weight:600}
.bkdoc .toc td.s{font-weight:700}
.bkdoc .toc .how{border-radius:2.4mm;background:var(--pl);padding:4mm 5mm;font-size:12px;line-height:1.85}.bkdoc .toc .how b{font-weight:800;color:var(--pd)}
.bkdoc .toc .how h4{margin:0 0 2mm;font-size:13.5px;font-weight:800;color:var(--pd)}
/* 실전 모의고사(출제 파일 서식) */
.bkdoc .mk .hd .t2 b{background:#111}
.bkdoc .mk.cl .hd .t2 b{background:var(--pd)}.bkdoc .mk.cl *{border-color:var(--pd)!important}.bkdoc .mk.cl .cv2 .ttl .a,.bkdoc .mk.cl .info .r{color:var(--pd)}.bkdoc .mk .cv2 .cvqr{position:absolute;right:0;bottom:30mm;display:flex;align-items:center;gap:3mm;font-size:10px;color:#444;line-height:1.4;text-align:right}.bkdoc .mk .cv2 .cvqr .qq{width:16mm;height:16mm;order:2}.bkdoc .mk .cv2 .cvqr .qq svg{width:100%;height:100%;display:block}
.bkdoc .mk.cl .cv2 .ln{border-color:var(--pd)!important}
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
`;
/* 화면용(리더) 보조 스타일 */
const BKSCR=`
.bkw{position:relative;margin:0 auto 6px;background:#fff;box-shadow:0 1px 6px rgba(20,30,50,.28);overflow:hidden}
.bkzm{display:inline-flex;align-items:center;gap:4px}.bkzm b{min-width:44px;text-align:center;font-size:13px}.bkzm button{padding:6px 12px;border-radius:8px;font:inherit;font-size:15px}
#bkpages{display:flex;flex-direction:column;overflow-x:auto;-webkit-overflow-scrolling:touch}#bkpages>*{flex:none;margin-left:auto;margin-right:auto}
.bkbar{display:flex;gap:10px;align-items:center;flex-direction:row-reverse;justify-content:flex-end;margin:0 auto 14px;padding:6px 10px;font-size:12.5px;color:var(--m)}
.bkbar b{color:var(--t)}.bkbar button{padding:6px 14px;border-radius:8px;font:inherit;font-size:13px}
.bkrd{position:sticky;top:62px;z-index:4;background:#fff;border:1px solid var(--l);border-radius:12px;padding:8px 10px;margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.bkrd .bkt{font-size:14px;min-width:60px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:0 6px}.bkrd .sp1{flex:1}.bkrd{gap:2px;padding:5px 8px;overflow-x:auto;flex-wrap:nowrap;scrollbar-width:none}.bkrd::-webkit-scrollbar{display:none}
.bkshelf{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.bkcard{border:1px solid var(--l);border-radius:12px;background:#fff;padding:14px;display:flex;gap:14px}
.bkcov{flex:none;width:92px;height:130px;border:1.5px solid #111;background:#fff;position:relative;padding:7px 7px 0;font-family:Pretendard,sans-serif;display:flex;flex-direction:column}
.bkcov i{display:block;width:16px;height:3px;background:#111;margin:14px 0 6px}
.bkcov b{font-size:11.5px;line-height:1.25;word-break:keep-all;font-weight:800;letter-spacing:-.5px}.bkcov span{font-size:10px;color:#444;margin-top:3px}
.bkcov em{position:absolute;left:7px;right:7px;bottom:6px;border-top:1px solid #111;padding-top:3px;font-style:normal;font-size:8px;color:#555}
.bkcard .bi2{flex:1;min-width:0;display:flex;flex-direction:column}.bkcard h3{margin:0;font-size:16px}.bkcard small{word-break:keep-all;display:block}.bkcard p{margin:4px 0 8px;font-size:12.5px;color:var(--m);line-height:1.5}
.bkcard .bt2{margin-top:auto;display:flex;gap:6px;flex-wrap:wrap}.bkcard .bt2 button{padding:7px 12px;font-size:13px;border-radius:8px}
.bkrl{display:flex;flex-direction:column;border-top:1px solid var(--l)}.bkrr{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:8px 2px;border-bottom:1px solid var(--l)}.bkrr b{min-width:42px;font-size:15px}.bkrr span{flex:1 1 140px;font-size:12.5px;color:var(--m)}.bkrr button{padding:6px 12px;font-size:13px;border-radius:8px}.bklm{display:inline-flex;gap:4px}.bklm button{padding:5px 12px;font-size:13px;border-radius:8px}
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
 })();
 return BKREADY;
}
const BKSH=':host{all:initial;display:block}.bkdoc.scr .bp{position:absolute;left:0;top:0;transform-origin:0 0;transform:scale(var(--bks,1))}';
function bkShadow(host,html){const r=host.shadowRoot||host.attachShadow({mode:'open'});r.innerHTML='<style>'+BKSH+BKCSS+'</style>'+html;return r}
function bkProbe(){let p=document.getElementById('bkprobe');if(!p){p=document.createElement('div');p.id='bkprobe';p.style.cssText='position:absolute;left:-9999px;top:0;visibility:hidden;pointer-events:none;width:300mm';document.body.appendChild(p);bkShadow(p,'<div class="bkdoc"><div id="bkpm"></div></div>')}return p.shadowRoot.getElementById('bkpm')}
function bkMeasure(html,w,cls){const p=bkProbe();p.innerHTML='<div class="'+(cls||'bk')+'" style="'+bkVars()+';width:'+w+'mm;display:flow-root;font-size:12px;line-height:1.5">'+html+'</div>';return Math.ceil(p.firstChild.getBoundingClientRect().height/BK_MM*10)/10}
const BKHA={};
function bkH(u){const k=u.key;if(BKREC)BKREC.push(u);if(BKHT&&BKHT[k]!=null)return BKHT[k];if(BKHA[k]!=null)return BKHA[k];if(BKH[k]==null)BKH[k]=bkMeasure(u.html,u.w||BK_COLW,u.cls);return BKH[k]}

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
function bkOxHtml(q,no,kind){const r=bkDoc(q.q);const qs=r.querySelector('.qs')||r;let h=qs.innerHTML.replace(/^<p>/,'').replace(/<\/p>$/,'');if(kind==='bl')h=h.replace(/<span class="bk">[^<]*<\/span>/g,'<span class="bk">&nbsp;</span>');
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
 const subs=bkSubs();const S={subs,ox:{},bl:{},basic:{},type:[],essay:[]};
 const byNo=(a,b)=>(a.no||0)-(b.no||0);
 subs.forEach(s=>{const r=bkFitOxBl(s,base.filter(q=>q.sub===s.k&&q.set==='ox').sort(byNo),base.filter(q=>q.sub===s.k&&q.set==='blank').sort(byNo));S.ox[s.k]=r.ox;S.bl[s.k]=r.bl});
 const used=new Set();
 subs.forEach(s=>{const lows=base.filter(q=>q.sub===s.k&&q.set==='mc'&&bkLv(q)==='하').sort(byNo);
  const pick=bkFitBasic(s,lows);S.basic[s.k]=pick;pick.forEach(q=>used.add(q.code))});
 const cap={me:255,cm:999,ph:999}[SUBJ]||255,ecap={me:25,cm:99,ph:99}[SUBJ]||25;
 let pool=base.filter(q=>(q.set==='mc'||q.set==='top')&&!used.has(q.code));
 if(pool.length>cap)pool=bkPickType(pool,cap);
 const so=s=>subs.findIndex(x=>x.k===s);
 const typeOrder=new Map();base.forEach(q=>{const k=q.sub+'|'+q.type;if(!typeOrder.has(k))typeOrder.set(k,typeOrder.size)});
 pool.sort((a,b)=>so(a.sub)-so(b.sub)||typeOrder.get(a.sub+'|'+a.type)-typeOrder.get(b.sub+'|'+b.type)||(LVI[bkLv(a)]-LVI[bkLv(b)])||byNo(a,b));
 S.type=pool;
 let es=base.filter(q=>q.set==='essay').sort((a,b)=>so(a.sub)-so(b.sub)||byNo(a,b));
 if(es.length>ecap){const t=es.length;es=Array.from({length:ecap},(_,i)=>es[Math.floor(i*t/ecap)])}
 S.essay=es;
 return BKSELC[SUBJ]=S}
function bkTags(s){const C=(CONC[SUBJ]||{}).secs||[];let n=0;const t=[];
 for(const sc of C.filter(x=>x.sub===s.k)){const w='#'+String(sc.title).replace(/[\s·,]+/g,'').slice(0,14);if(n+w.length>100)break;t.push(w);n+=w.length+2}
 return t.map(x=>'<span style="white-space:nowrap;margin-right:2.4mm">'+esc(x)+'</span>').join(' ')}
function bkFitCol(s,kd,cands){
 const nm=kd==='ox'?'OX 확인':'빈칸 채우기';const order=[];const tg=new Map();cands.forEach(q=>{const k=q.type||'';if(!tg.has(k))tg.set(k,[]);tg.get(k).push(q)});
 const lists=[...tg.values()];for(let i=0;order.length<cands.length;i++){let any=false;lists.forEach(l=>{if(l[i]){order.push(l[i]);any=true}});if(!any)break}
 const head=bkU('h:'+kd+':'+s.k,'<div class="u ct"><span>'+nm+'</span><small>'+esc(s.k)+'</small></div>',{});
 let used=head.h;const out=[];
 for(const q of order){const u=bkU('o:'+q.code+':'+kd,bkOxHtml(q,out.length+1,kd),{code:q.code});if(used+u.h>BK_BODY)break;used+=u.h;out.push(q)}
 return out.sort((a,b)=>(a.no||0)-(b.no||0))}
function bkFitOxBl(s,ox,bl){return {ox:bkFitCol(s,'ox',ox),bl:bkFitCol(s,'bl',bl)}}
function bkFitBasic(s,cands){
 const order=[];const tg=new Map();cands.forEach(q=>{if(!tg.has(q.type))tg.set(q.type,[]);tg.get(q.type).push(q)});
 const lists=[...tg.values()];for(let i=0;order.length<cands.length;i++){let any=false;lists.forEach(l=>{if(l[i]){order.push(l[i]);any=true}});if(!any)break}
 const head=bkU('h:mc:'+s.k,'<div class="u ct"><span>기초 5지선다</span><small>'+esc(s.k)+'</small></div>',{keep:true,brk:true});
 let best=order.slice(0,Math.min(6,order.length));
 for(let k=Math.min(7,order.length);k<=Math.min(14,order.length);k++){
  const items=order.slice(0,k).sort((a,b)=>(a.no||0)-(b.no||0));
  const us=[head,...items.map((q,i)=>bkU('q:'+q.code,bkQHtml(q,i+1,{code:1}),{code:q.code}))];
  if(bkPack(us,2,BK_BODY).length<=2)best=items;else break}
 return best.sort((a,b)=>(a.no||0)-(b.no||0))}
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
  let need=u.h+(u.pad||0);for(let j=i;units[j].keep&&units[j+1];){j++;need+=units[j].h+(units[j].pad||0)}
  if(used+need>capOf()&&used>0){ci++;used=0;if(ci>=ncol)np()}
  pg.cols[ci].push(u);used+=u.h+(u.pad||0)}
 return pages}
function bkGap(c){const n=c.length;if(n<2)return 0;const pad=c.reduce((m,u)=>Math.max(m,u.pad||0),0);const used=c.reduce((a,u)=>a+u.h,0);if(used<BK_BODY*.55)return pad;return Math.max(pad,Math.min(14,Math.round((BK_BODY-used-8)/(n-1)*10)/10))}
function bkCI(p){return {cols:p.cols.map(c=>c.map(u=>u.html)),gaps:p.cols.map(bkGap)}}
const bkU=(key,html,o)=>{const u={key:SUBJ+'|'+key,html,w:(o&&o.w)||BK_COLW,...(o||{})};u.h=bkH(u);u.pad=/^<div class="u q"/.test(html)?BKPADS[BKO.gap||0]:0;return u};

/* ---------- 쪽 계획 ---------- */
async function bkPlan(id){
 if(BKP[id]&&BKP[id].subj===SUBJ&&BKP[id].sig===bkOsig())return BKP[id];
 await bkInit();await conceptLoad();
 const P=bkParts(id);if(!P)return null;
 const mk0=()=>P.kind==='c'?bkPlanConcept(id):P.kind==='t'?bkPlanType(id):P.def.kind==='free'?bkPlanFree(id,P.def):P.def.kind==='full'?(P.def.round?bkPlanFull(id,P.def,P.def.round):null):bkPlanCustom(id,P.def);
 const mk=()=>{const og=BKO.gap;BKO.gap=P.gap||0;try{return mk0()}finally{BKO.gap=og}};
 const plan=BKREC?mk():await bkSettle(mk);if(!plan)return null;
 plan.pages.forEach((p,i)=>p.n=i+1);
 plan.id=id;plan.subj=SUBJ;plan.sig=bkOsig();return BKP[id]=plan}
function bkPageObjs(pg,extra){return pg.cols.map(c=>c.map(u=>u.html))}
function bkQrPg(pages,k,kind,sub,label,pgs,extra){pgs.forEach(p=>{pages.push({k,kind,sub,label,...bkCI(p),codes:p.cols.flat().map(u=>u.code).filter(Boolean),...extra})})}

function bkSbn(s,extra){return '<div class="u sbn"><b><i>'+esc(s.k)+'</i>'+esc(s.name)+'</b>'+(s.goal?'<span class="g">'+esc(s.goal)+'</span>':'')+(extra||'')+'</div>'}
const bkScope=S=>{const sc=(CONC[SUBJ]||{}).scope;const a=sc&&sc.length?S.subs.filter(s=>sc.includes(s.k)):S.subs;return a.length?a:S.subs};
function bkPlanConcept(id){
 const S=bkSel(),C=CONC[SUBJ]||{secs:[]};const pages=[{k:'cover'},{k:'toc'}];const toc=[];
 bkScope(S).forEach(s=>{
  const row={sub:s,c:null,ox:null,bl:null,mc:null};
  const secs=(C.secs||[]).filter(x=>x.sub===s.k);
  const cu=[bkU('sb:'+s.k+':c',bkSbn(s,'<div class="rf">[[REF:'+s.k+']]</div>'),{w:BK_FULLW,brk:true,keep:true})];
  secs.forEach(sec=>{
   cu.push(bkU('ch:'+sec.id,'<div class="u sh2"><i>'+esc(sec.no)+'</i><span>'+esc(sec.title)+'</span></div>',{w:BK_FULLW,keep:true}));
   const d=bkDoc('<div class="cbk">'+sec.html+'</div>').firstElementChild;
   [...d.children].forEach((el,i)=>cu.push(bkU('cb:'+sec.id+':'+i,'<div class="u cbk">'+el.outerHTML+'</div>',{w:BK_FULLW})))});
  const cp=bkPack(cu,1,BK_BODY);row.c=pages.length+1;
  cp.forEach(p=>pages.push({k:'cn',kind:'c',sub:s,label:'개념 정리',cols:[p.cols[0].map(u=>u.html)]}));
  {const cols=[],codes=[];
   [['ox','OX 확인',S.ox[s.k]],['bl','빈칸 채우기',S.bl[s.k]]].forEach(([kd,nm,arr])=>{const us=[];
    if(arr&&arr.length){us.push(bkU('h:'+kd+':'+s.k,'<div class="u ct"><span>'+nm+'</span><small>'+esc(s.k)+' · '+arr.length+'문항</small></div>',{}));
     arr.forEach((q,i)=>{us.push(bkU('o:'+q.code+':'+kd,bkOxHtml(q,i+1,kd),{code:q.code}));codes.push(q.code)})}
    cols.push(us.map(u=>u.html))});
   if(codes.length){row.ox=row.bl=pages.length+1;pages.push({k:'pr',kind:'ox',sub:s,label:'OX · 빈칸',cols,codes})}}
  {const arr=S.basic[s.k];if(arr&&arr.length){
   const hu=bkU('h:mc:'+s.k,'<div class="u ct"><span>기초 5지선다</span><small>'+esc(s.k)+' · '+arr.length+'문항</small></div>',{keep:true,brk:true});
   const us=arr.map((q,i)=>bkU('q:'+q.code,bkQHtml(q,i+1,{code:1}),{code:q.code}));
   row.mc=pages.length+1;
   bkPack([hu,...us],2,BK_BODY).forEach(p=>pages.push({k:'pr',kind:'mc',sub:s,label:'기초 5지선다',...bkCI(p),codes:p.cols.flat().map(u=>u.code).filter(Boolean)}))}}
  toc.push(row)});
 // 정답
 const au=[];
 bkScope(S).forEach(s=>{
  au.push(bkU('as:'+s.k,'<div class="u ct"><span>'+esc(s.k)+' '+esc(s.name)+'</span></div>',{keep:true}));
  [['ox','OX 정답',S.ox[s.k]],['bl','빈칸 정답',S.bl[s.k]]].forEach(([kd,nm,arr])=>{if(!arr||!arr.length)return;
   const cells=arr.map((q,i)=>'<div><b>'+(i+1)+'</b><span>'+(kd==='ox'?bkAnsOf(q):esc((q.blanks||[]).join(' / ')))+'</span></div>').join('');
   au.push(bkU('ak:'+kd+':'+s.k,'<div class="u k"><div class="ct sm"><span>'+nm+'</span></div><div class="kg '+(kd==='ox'?'':'w2')+'">'+cells+'</div></div>',{}))});
  const b=S.basic[s.k]||[];
  if(b.length){au.push(bkU('ak:mc:'+s.k,'<div class="u k"><div class="ct sm"><span>기초 5지선다 정답</span></div><div class="kg">'+b.map((q,i)=>'<div><b>'+(i+1)+'</b><span>'+bkCir(q.ans)+'</span></div>').join('')+'</div></div>',{}));
   b.forEach((q,i)=>au.push(bkU('x:'+q.code,bkXHtml(q,i+1),{})))}});
 const ap=bkPack(au,2,BK_BODY);const aStart=pages.length+1;
 ap.forEach(p=>pages.push({k:'ak',kind:'a',label:'정답 · 해설',...bkCI(p)}));
 // 소단원 머리글의 「확인 문제」 쪽 안내
 const ref=r=>[r.ox?'OX p.'+r.ox:'',r.bl?'빈칸 p.'+r.bl:'',r.mc?'기초 5지선다 p.'+r.mc:''].filter(Boolean).map(t=>'<em>'+t+'</em>').join('');
 toc.forEach(r=>pages.forEach(pg=>{if(pg.cols)pg.cols=pg.cols.map(c=>c.map(h=>h.replace('[[REF:'+r.sub.k+']]',ref(r))))}));
 return {kind:'c',title:SNAME[SUBJ]+' 개념서',short:'개념서',pages,toc,aStart,sel:S}}

function bkPlanType(id){
 const S=bkSel();const esS=S.essay.filter(q=>bkScope(S).some(s=>s.k===q.sub));const pages=[{k:'cover'},{k:'toc'}];const toc=[];let no=0;const nums=new Map();
 bkScope(S).forEach(s=>{
  const qs=S.type.filter(q=>q.sub===s.k);if(!qs.length)return;
  const units=[bkU('sb:'+s.k+':t',bkSbn({k:s.k,name:s.name,goal:''},'<span class="g">'+bkTags(s)+'</span>'),{brk:true,keep:true})];
  let cur=null,ti=0;
  qs.forEach(q=>{if(q.type!==cur){cur=q.type;ti++;const grp=qs.filter(x=>x.type===cur);const av=grp.reduce((a,x)=>a+LVI[bkLv(x)],0)/grp.length;const n=Math.max(1,Math.min(4,Math.round(av)+1));const st='★'.repeat(n)+'☆'.repeat(4-n);
    units.push(bkU('th:'+s.k+':'+ti+':'+cur,'<div class="th"><b>유형 '+String(ti).padStart(2,'0')+'</b><span>'+esc(cur)+'</span><small>'+st+'</small></div>',{keep:true}))}
   no++;nums.set(q.code,no);units.push(bkU('q:'+q.code+':t',bkQHtml(q,no,{lv:bkLv(q),code:1}),{code:q.code}))});
  const row={sub:s,n:qs.length,p:pages.length+1};toc.push(row);
  bkPack(units,2,BK_BODY).forEach(p=>pages.push({k:'pr',kind:'t',sub:s,label:'유형 문제',...bkCI(p),codes:p.cols.flat().map(u=>u.code).filter(Boolean)}))});
 // 서술형
 if(esS.length){const eu=[bkU('sb:es',bkSbn({k:'서술형',name:'서술형 · 최상위 도전',goal:''},'<span class="g">풀이 과정을 서술해 보세요. 맨 뒤 모범 답안과 비교해 스스로 채점합니다.</span>'),{brk:true,keep:true})];
  esS.forEach((q,i)=>{no++;nums.set(q.code,no);eu.push(bkU('q:'+q.code+':e',bkQHtml(q,no,{ans:1,code:1,lv:bkLv(q)}),{code:q.code}))});
  toc.es={n:esS.length,p:pages.length+1};
  bkPack(eu,2,BK_BODY).forEach(p=>pages.push({k:'es',kind:'e',label:'서술형',...bkCI(p)}))}
 // 정답·해설
 const au=[];
 bkScope(S).forEach(s=>{const qs=S.type.filter(q=>q.sub===s.k);if(!qs.length)return;
  au.push(bkU('as:'+s.k,'<div class="u ct"><span>'+esc(s.k)+' '+esc(s.name)+'</span></div>',{keep:true}));
  au.push(bkU('akt:'+s.k,'<div class="u k"><div class="ct sm"><span>빠른 정답</span></div><div class="kg">'+qs.map(q=>'<div><b>'+nums.get(q.code)+'</b><span>'+bkCir(q.ans)+'</span></div>').join('')+'</div></div>',{}));
  qs.forEach(q=>au.push(bkU('x:'+q.code,bkXHtml(q,nums.get(q.code)),{})))});
 if(esS.length){au.push(bkU('as:es','<div class="u ct"><span>서술형 모범 답안</span></div>',{keep:true}));esS.forEach(q=>au.push(bkU('x:'+q.code,bkXHtml(q,nums.get(q.code)),{})))}
 const aStart=pages.length+1;
 bkPack(au,2,BK_BODY).forEach(p=>pages.push({k:'ak',kind:'a',label:'정답 · 해설',...bkCI(p)}));
 return {kind:'t',title:SNAME[SUBJ]+' 유형서',short:'유형서',pages,toc,aStart,sel:S,total:no}}

/* ---------- 내 교재 : 직접 만든 책 · 전범위 모의고사 ---------- */
const BKXK='omr_books_v1',BKXF={concept:1,ox:2,bl:4,basic:8,type:16,essay:32,all:64,last:128};
function bkxLocal(){try{return JSON.parse(localStorage.getItem(BKXK)||'[]')}catch(e){return[]}}
function bkAsgRecs(){const o=[];(typeof BKASG!=='undefined'?BKASG:[]).forEach(a=>{try{const n=JSON.parse(a.note||'{}');if(n&&n.bk&&n.bk.id&&!o.some(x=>x.id===n.bk.id))o.push({...n.bk,asg:1,due:a.due||''})}catch(e){}});return o}
function bkxAll(){const l=bkxLocal();bkAsgRecs().forEach(r=>{if(!l.some(x=>x.id===r.id))l.push(r)});return l}
function bkxStore(a){try{localStorage.setItem(BKXK,JSON.stringify((a||[]).filter(x=>!x.asg)))}catch(e){}}
function bkxId(subj,d){
 if(d.kind==='free')return subj+'-xf'+bkfPayload(d);
 const lvS=(d.lv&&d.lv!==15?'l'+d.lv.toString(16):'');
 if(d.kind==='full'){const fs=(d.subs||[]).slice().sort((a,b)=>a-b);return subj+'-xe'+(d.count||20)+lvS+(fs.length?'s'+fs.join('.'):'')}
 let m=0;Object.keys(BKXF).forEach(k=>{if(k==='all'?d.all:k==='last'?d.last:(d.inc||{})[k])m|=BKXF[k]});
 const si=(d.subs||[]).slice().sort((a,b)=>a-b);return subj+'-xb'+m.toString(36)+(si.length?'-'+si.join('.'):'')+(lvS||d.cap>0?'_'+lvS+(d.cap>0?'n'+d.cap:''):'')}
function bkxDefOf(m){ // 경로 문자열에서 책 정의 복원 → 다른 기기에서도 QR 채점 가능
 if(m[4]!=null)return {kind:'full',count:+m[4],lv:m[6]!=null?parseInt(m[6],16):15,round:m[5]?+m[5]:0,subs:m[8]?String(m[8]).split('.').map(Number).filter(x=>!isNaN(x)):[]};
 const mask=parseInt(m[2],36)||0,inc={};Object.keys(BKXF).forEach(k=>{if(k!=='all'&&k!=='last'&&(mask&BKXF[k]))inc[k]=1});
 return {kind:'std',inc,all:!!(mask&BKXF.all),last:!!(mask&BKXF.last),subs:m[3]?m[3].split('.').map(Number):[],lv:m[6]!=null?parseInt(m[6],16):15,cap:m[7]?+m[7]:0}}
function bkGapOf(id){const g=String(id).match(/~g([1-3])$/);return g?+g[1]:0}
function bkBare(id){return String(id).replace(/~g[1-3]$/,'')}
function bkPid(id){const g=BKO.gap||0;return bkBare(id)+(g?'~g'+g:'')}
function bkParts(id){const gap=bkGapOf(id);id=bkBare(id);
 const mf=String(id).match(/^(me|cm|ph)-xf([0-9a-z._]+)$/);
 if(mf){const d=bkfParse(mf[2]);if(!d)return null;const rec=bkxAll().find(b=>b.id===id);d.name=rec?rec.name:'맞춤 교재';d.subt=rec?rec.sub:'';d.base=id;d.dz=rec?{color:rec.color||'',cover:rec.cover|0,noqr:rec.noqr?1:0,font:rec.font||'',lf:rec.lf||'solvi',lfp:rec.lfp||'br',lb:rec.lb||'solvi',lbp:rec.lbp||'bc',back:rec.back?1:0,cx:rec.cx||null}:{color:'',cover:0,noqr:0,font:'',lf:'solvi',lfp:'br',lb:'solvi',lbp:'bc',back:0,cx:null};return {subj:mf[1],kind:'x',def:d,gap}}
 const m=String(id).match(/^(me|cm|ph)-(c|t|x(?:b([0-9a-z]+)(?:-([\d.]+))?(?:_(?:l([0-9a-f]))?(?:n(\d+))?)?|e(\d+)(?:l([0-9a-f]))?(?:s([\d.]+))?(?:r(\d+))?))$/);if(!m)return null;
 if(m[2]==='c'||m[2]==='t')return {subj:m[1],kind:m[2],gap};
 const d=bkxDefOf(m[7]!=null?[0,0,0,0,m[7],m[10],m[8],0,m[9]]:[0,0,m[3],m[4],undefined,0,m[5],m[6]]);
 const lvS=d.lv&&d.lv!==15?'l'+d.lv.toString(16):'';
 const baseId=m[1]+'-'+(d.kind==='full'?'xe'+d.count+lvS+((d.subs||[]).length?'s'+d.subs.join('.'):''):'xb'+m[3]+(m[4]?'-'+m[4]:'')+(lvS||d.cap>0?'_'+lvS+(d.cap>0?'n'+d.cap:''):''));
 const rec=bkxAll().find(b=>b.id===baseId);
 d.name=rec?rec.name:(d.kind==='full'?'전범위 모의고사':'맞춤 교재');d.subt=rec?rec.sub:'';d.rounds=rec&&rec.rounds||20;
 d.base=baseId;
 return {subj:m[1],kind:'x',def:d,gap}}
function bkxPreset(kind){const B={
 std:{name:'나만의 교재',sub:'개념 · 확인 문제 · 유형',inc:{concept:1,ox:1,bl:1,basic:1,type:1},all:0},
 last:{name:'직전 대비 교재',sub:'시험 직전 핵심 압축 정리',inc:{concept:1,ox:1,bl:1,type:1},all:0,last:1},
 drill:{name:'개념 양치기',sub:'OX · 빈칸 집중 반복',inc:{ox:1,bl:1},all:1},
 part:{name:'특정 부분 양치기',sub:'고른 소단원만 파고들기',inc:{ox:1,bl:1,basic:1,type:1},all:1},
 full:{name:'전범위 모의고사',sub:'전 범위에서 뽑은 실전 연습',inc:{},all:0,count:20,rounds:20}}[kind];
 return {kind,subs:[],...JSON.parse(JSON.stringify(B))}}
const BKLVB={'하':1,'중':2,'상':4,'최':8};
const bkLvOk=(q,lv)=>!lv||lv===15||!!(lv&(BKLVB[bkLv(q)]||2));
function bkRng(seed){let a=seed>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function bkMockSet(count,rd,lv,sel){
 const subs=bkSubs().filter((s,i)=>!(sel||[]).length||sel.includes(i));const base=DATA.filter(q=>q.sub&&(q.set==='mc'||q.set==='top')&&!q.mock&&bkLvOk(q,lv));
 const rnd=bkRng([...SUBJ+count+(lv&&lv!==15?'l'+lv:'')+((sel||[]).length?'s'+sel.join('.'):'')].reduce((a,c)=>a*31+c.charCodeAt(0)|0,7));
 const L=subs.map(s=>{const a=base.filter(q=>q.sub===s.k);for(let i=a.length-1;i>0;i--){const j=Math.floor(rnd()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}).filter(a=>a.length);
 const tot=L.reduce((a,x)=>a+x.length,0);const n=L.map(a=>Math.max(1,Math.round(count*a.length/tot)));
 for(let g=0;g<200;g++){const sm=n.reduce((a,b)=>a+b,0);if(sm===count)break;const i=n.indexOf(sm>count?Math.max(...n):Math.min(...n));n[i]+=sm>count?-1:1}
 const out=[];L.forEach((a,i)=>{for(let k=0;k<n[i];k++)out.push(a[(((rd-1)*n[i])+k)%a.length])});
 const rank=q=>LVI[bkLv(q)]??1;const si=q=>subs.findIndex(s=>s.k===q.sub);
 return out.sort((a,b)=>rank(a)-rank(b)||si(a)-si(b)||(a.no||0)-(b.no||0))}
function bkMockPts(qs){const w={'하':2,'중':3,'상':4,'최':5};const raw=qs.map(q=>w[bkLv(q)]||3),sm=raw.reduce((a,b)=>a+b,0);
 const p=raw.map(x=>Math.floor(x*100/sm));let left=100-p.reduce((a,b)=>a+b,0);const ord=raw.map((x,i)=>i).sort((a,b)=>raw[b]-raw[a]);for(let k=0;left>0;k++,left--)p[ord[k%ord.length]]++;
 const m={};qs.forEach((q,i)=>m[q.code]=p[i]);return m}
function bkPlanFull(id,d,rd){
 const subs=bkSubs();const qs=bkMockSet(d.count,rd,d.lv,d.subs),pts=bkMockPts(qs);
 const used=[...new Set(qs.map(q=>q.sub))];
 const M={title:d.name,round:rd,sname:SNAME[SUBJ],codes:qs.map(q=>q.code),pts,tot:100,time:Math.max(30,Math.round(d.count*2.2/5)*5)+'분',range:subs.filter(s=>used.includes(s.k)).map(s=>s.k+' '+s.name)};
 const pages=[{k:'mcv'}];
 const us=qs.map((q,i)=>bkU('mq:'+q.code,bkQHtml(q,i+1,{pt:pts[q.code]}),{code:q.code,cls:'mk'}));
 const pp=bkPack(us,2,BK_BODY,BK_BODY-19);const nq=pp.length;
 pp.forEach((p,i)=>pages.push({k:'mq',kind:'q',label:'문제지',idx:i+1,of:nq,first:i===0,...bkCI(p),gaps:p.cols.map(c=>c.reduce((m,u)=>Math.max(m,u.pad||0),0)),codes:p.cols.flat().map(u=>u.code).filter(Boolean)}));
 const au=[bkU('fa:'+rd,'<div class="u ct"><span>정답표</span><small>'+d.count+'문항 · 100점</small></div>',{keep:true}),
  bkU('fk:'+qs.map(q=>q.code).join(','),'<div class="u k"><div class="kg">'+qs.map((q,i)=>'<div><b>'+(i+1)+'</b><span>'+bkCir(q.ans)+'</span></div>').join('')+'</div></div>',{}),
  ...qs.map((q,i)=>bkU('x:'+q.code,bkXHtml(q,i+1),{}))];
 const aStart=pages.length+1;
 bkPack(au,2,BK_BODY).forEach(p=>pages.push({k:'ak',kind:'a',label:'정답 · 해설',...bkCI(p)}));
 return {kind:'m',rd,title:d.name+' '+rd+'회',short:d.name+' '+rd+'회',pages,toc:[],M,qs,aStart,nq}}
function bkPlanCustom(id,d){
 const S=bkSel(),C=CONC[SUBJ]||{secs:[]},inc=d.inc||{};
 const subs=S.subs.filter((s,i)=>!(d.subs||[]).length||d.subs.includes(i));
 const base=DATA.filter(q=>q.sub&&q.set!=='bank'&&!q.mock),byNo=(a,b)=>(a.no||0)-(b.no||0);
 const of=(s,f)=>base.filter(q=>q.sub===s.k&&f(q)).sort(byNo);
 const typeOrder=new Map();base.forEach(q=>{const k=q.sub+'|'+q.type;if(!typeOrder.has(k))typeOrder.set(k,typeOrder.size)});
 const pages=[{k:'cover'},{k:'toc'}],toc=[],nums=new Map();let no=0,total=0;
 const qp=(units,kind,label,s)=>bkPack(units,2,BK_BODY).forEach(p=>pages.push({k:'pr',kind,sub:s,label,...bkCI(p),codes:p.cols.flat().map(u=>u.code).filter(Boolean)}));
 const usedBasic=new Set();
 subs.forEach(s=>{
  const r={sub:s,items:[],ox:[],bl:[],mc:[],ty:[]};
  if(inc.concept){
   const cu=[bkU('sb:'+s.k+':c',bkSbn(s),{w:BK_FULLW,brk:true,keep:true})];
   (C.secs||[]).filter(x=>x.sub===s.k).forEach(sec=>{
    cu.push(bkU('ch:'+sec.id,'<div class="u sh2"><i>'+esc(sec.no)+'</i><span>'+esc(sec.title)+'</span></div>',{w:BK_FULLW,keep:true}));
    const dd=bkDoc('<div class="cbk">'+sec.html+'</div>').firstElementChild;
    [...dd.children].forEach((el,i)=>cu.push(bkU('cb:'+sec.id+':'+i,'<div class="u cbk">'+el.outerHTML+'</div>',{w:BK_FULLW})))});
   r.items.push(['개념',pages.length+1]);
   bkPack(cu,1,BK_BODY).forEach(p=>pages.push({k:'cn',kind:'c',sub:s,label:'개념 정리',cols:[p.cols[0].map(u=>u.html)]}))}
  r.ox=inc.ox?(d.all?of(s,q=>q.set==='ox'):S.ox[s.k]||[]):[];r.bl=inc.bl?(d.all?of(s,q=>q.set==='blank'):S.bl[s.k]||[]):[];
  if(d.all){
   [['ox','OX 확인',r.ox],['bl','빈칸 채우기',r.bl]].forEach(([kd,nm,arr])=>{if(!arr.length)return;
    const us=[bkU('h:'+kd+':'+s.k+':'+arr.length,'<div class="u ct"><span>'+nm+'</span><small>'+esc(s.k)+' · '+arr.length+'문항</small></div>',{keep:true,brk:kd==='ox'&&!!(inc.concept||inc.basic||inc.type)})];
    arr.forEach((q,i)=>us.push(bkU('o:'+q.code+':'+kd,bkOxHtml(q,i+1,kd),{code:q.code})));
    r.items.push([kd==='ox'?'OX':'빈칸',pages.length+1]);qp(us,kd,nm,s)})}
  else if(r.ox.length||r.bl.length){const cols=[],codes=[];
   [['ox','OX 확인',r.ox],['bl','빈칸 채우기',r.bl]].forEach(([kd,nm,arr])=>{const us=[];
    if(arr.length){us.push(bkU('h:'+kd+':'+s.k,'<div class="u ct"><span>'+nm+'</span><small>'+esc(s.k)+' · '+arr.length+'문항</small></div>',{}));
     arr.forEach((q,i)=>{us.push(bkU('o:'+q.code+':'+kd,bkOxHtml(q,i+1,kd),{code:q.code}));codes.push(q.code)})}
    cols.push(us.map(u=>u.html))});
   r.items.push(['OX · 빈칸',pages.length+1]);pages.push({k:'pr',kind:'ox',sub:s,label:'OX · 빈칸',cols,codes})}
  r.mc=inc.basic&&bkLvOk({lv:'하'},d.lv)?(d.all?of(s,q=>q.set==='mc'&&bkLv(q)==='하'):S.basic[s.k]||[]):[];
  if(r.mc.length){r.mc.forEach(q=>usedBasic.add(q.code));
   const us=[bkU('h:mc:'+s.k+':'+r.mc.length,'<div class="u ct"><span>기초 5지선다</span><small>'+esc(s.k)+' · '+r.mc.length+'문항</small></div>',{keep:true,brk:true}),...r.mc.map((q,i)=>bkU('q:'+q.code,bkQHtml(q,i+1,{code:1}),{code:q.code}))];
   r.items.push(['기초',pages.length+1]);qp(us,'mc','기초 5지선다',s)}
  if(inc.type){
   r.ty=d.all?of(s,q=>(q.set==='mc'||q.set==='top')&&!usedBasic.has(q.code)).sort((a,b)=>typeOrder.get(a.sub+'|'+a.type)-typeOrder.get(b.sub+'|'+b.type)||(LVI[bkLv(a)]-LVI[bkLv(b)])||byNo(a,b)):S.type.filter(q=>q.sub===s.k);
   if(d.lv&&d.lv!==15)r.ty=r.ty.filter(q=>bkLvOk(q,d.lv));
   if(d.cap>0&&r.ty.length>d.cap)r.ty=bkPickRound(r.ty,d.cap,['중','상','중','최']).sort((a,c)=>typeOrder.get(a.sub+'|'+a.type)-typeOrder.get(c.sub+'|'+c.type)||(LVI[bkLv(a)]-LVI[bkLv(c)])||byNo(a,c));
   else if(d.last&&r.ty.length>8)r.ty=bkPickRound(r.ty,8,['중','상','중','최']).sort((a,c)=>typeOrder.get(a.sub+'|'+a.type)-typeOrder.get(c.sub+'|'+c.type)||byNo(a,c));
   if(r.ty.length){const units=[bkU('sb:'+s.k+':t',bkSbn({k:s.k,name:s.name,goal:''},'<span class="g">'+bkTags(s)+'</span>'),{brk:true,keep:true})];
    let cur=null,ti=0;
    r.ty.forEach(q=>{if(q.type!==cur){cur=q.type;ti++;const grp=r.ty.filter(x=>x.type===cur);const av=grp.reduce((a,x)=>a+LVI[bkLv(x)],0)/grp.length;const n=Math.max(1,Math.min(4,Math.round(av)+1));const st='★'.repeat(n)+'☆'.repeat(4-n);
     units.push(bkU('th:'+s.k+':'+ti+':'+cur,'<div class="th"><b>유형 '+String(ti).padStart(2,'0')+'</b><span>'+esc(cur)+'</span><small>'+st+'</small></div>',{keep:true}))}
     no++;nums.set(q.code,no);units.push(bkU('q:'+q.code+':t',bkQHtml(q,no,{lv:bkLv(q),code:1}),{code:q.code}))});
    r.items.push(['유형',pages.length+1]);qp(units,'t','유형 문제',s)}}
  total+=r.ox.length+r.bl.length+r.mc.length+r.ty.length;
  if(r.items.length)toc.push(r)});
 let es=[];
 if(inc.essay){es=d.all?base.filter(q=>q.set==='essay'&&subs.some(s=>s.k===q.sub)).sort(byNo):S.essay.filter(q=>subs.some(s=>s.k===q.sub));
  if(es.length){const eu=[bkU('sb:es',bkSbn({k:'서술형',name:'서술형 · 최상위 도전',goal:''},'<span class="g">풀이 과정을 서술해 보세요. 맨 뒤 모범 답안과 비교해 스스로 채점합니다.</span>'),{brk:true,keep:true})];
   es.forEach(q=>{no++;nums.set(q.code,no);eu.push(bkU('q:'+q.code+':e',bkQHtml(q,no,{ans:1,code:1,lv:bkLv(q)}),{code:q.code}))});
   toc.es={n:es.length,p:pages.length+1};total+=es.length;
   bkPack(eu,2,BK_BODY).forEach(p=>pages.push({k:'es',kind:'e',label:'서술형',...bkCI(p)}))}}
 const au=[];
 toc.forEach(r=>{const s=r.sub;au.push(bkU('as:'+s.k,'<div class="u ct"><span>'+esc(s.k)+' '+esc(s.name)+'</span></div>',{keep:true}));
  [['ox','OX 정답',r.ox],['bl','빈칸 정답',r.bl]].forEach(([kd,nm,arr])=>{if(!arr.length)return;
   const cells=arr.map((q,i)=>'<div><b>'+(i+1)+'</b><span>'+(kd==='ox'?bkAnsOf(q):esc((q.blanks||[]).join(' / ')))+'</span></div>').join('');
   au.push(bkU('ak:'+kd+':'+s.k+':'+arr.length,'<div class="u k"><div class="ct sm"><span>'+nm+'</span></div><div class="kg '+(kd==='ox'?'':'w2')+'">'+cells+'</div></div>',{}))});
  if(r.mc.length){au.push(bkU('ak:mc:'+s.k+':'+r.mc.length,'<div class="u k"><div class="ct sm"><span>기초 5지선다 정답</span></div><div class="kg">'+r.mc.map((q,i)=>'<div><b>'+(i+1)+'</b><span>'+bkCir(q.ans)+'</span></div>').join('')+'</div></div>',{}));r.mc.forEach((q,i)=>au.push(bkU('x:'+q.code,bkXHtml(q,i+1),{})))}
  if(r.ty.length){au.push(bkU('akt:'+s.k+':'+r.ty.length,'<div class="u k"><div class="ct sm"><span>유형 문제 정답</span></div><div class="kg">'+r.ty.map(q=>'<div><b>'+nums.get(q.code)+'</b><span>'+bkCir(q.ans)+'</span></div>').join('')+'</div></div>',{}));r.ty.forEach(q=>au.push(bkU('x:'+q.code,bkXHtml(q,nums.get(q.code)),{})))}});
 if(es.length){au.push(bkU('as:es','<div class="u ct"><span>서술형 모범 답안</span></div>',{keep:true}));es.forEach(q=>au.push(bkU('x:'+q.code,bkXHtml(q,nums.get(q.code)),{})))}
 const aStart=pages.length+1;
 bkPack(au,2,BK_BODY).forEach(p=>pages.push({k:'ak',kind:'a',label:'정답 · 해설',...bkCI(p)}));
 const parts=[inc.concept?'개념':'',inc.ox?'OX':'',inc.bl?'빈칸':'',inc.basic?'기초':'',inc.type?'유형':'',inc.essay?'서술형':''].filter(Boolean);
 return {kind:'x',title:d.name,short:d.name,sub:d.subt||'',pages,toc,aStart,total,parts,subs,drill:!!d.all,last:!!d.last}}

/* ---------- 자유 구성 교재 (xf) : 구성 순서·문항 수·난이도·정렬·정답 방식을 책 ID에 담아 다른 기기에서도 QR 채점 ---------- */
const BKFP=[['c','개념 정리'],['o','OX'],['b','빈칸'],['m','기초 5지선다'],['t','유형 문제'],['e','서술형']],BKFN=Object.fromEntries(BKFP);
const BKFLV=new Set(['t','e']);
function bkfParse(str){const d={kind:'free',parts:[],subs:[],sort:0,grp:0,ans:0,brk:0},seen={};
 for(const t of String(str).split('_')){let m;
  if((m=t.match(/^([cobmte])(a|\d{1,3})?(?:v([1-9a-f]))?$/))){if(seen[m[1]])return null;seen[m[1]]=1;d.parts.push({k:m[1],all:m[2]==='a',cap:/^\d/.test(m[2]||'')?+m[2]:0,lv:m[3]?parseInt(m[3],16):15})}
  else if((m=t.match(/^r(\d+(?:\.\d+)*)$/)))d.subs=m[1].split('.').map(Number);
  else if((m=t.match(/^z([0-9a-z]{1,4})$/)))d.copy=m[1];
  else if((m=t.match(/^([sgap])([0-3])$/)))d[{s:'sort',g:'grp',a:'ans',p:'brk'}[m[1]]]=+m[2];
  else return null}
 return d.parts.length?d:null}
function bkfPayload(d){const o=[];
 (d.parts||[]).forEach(p=>o.push(p.k+(p.all?'a':p.cap>0?p.cap:'')+(BKFLV.has(p.k)&&p.lv&&p.lv!==15?'v'+p.lv.toString(16):'')));
 const si=(d.subs||[]).slice().sort((a,b)=>a-b);if(si.length)o.push('r'+si.join('.'));
 if(d.sort)o.push('s'+d.sort);if(d.copy)o.push('z'+d.copy);if(d.grp)o.push('g'+d.grp);if(d.ans)o.push('a'+d.ans);if(d.brk)o.push('p'+d.brk);
 return o.join('_')}
const bkSpread=(a,n)=>{if(n>=a.length)return a.slice();const o=[];for(let i=0;i<n;i++)o.push(a[Math.floor(i*a.length/n)]);return o};
function bkfSort(a,mode,typeOrder,seed){const byNo=(x,y)=>(x.no||0)-(y.no||0);
 if(mode===1)return a.slice().sort((x,y)=>LVI[bkLv(x)]-LVI[bkLv(y)]||byNo(x,y));
 if(mode===3)return a.slice().sort((x,y)=>LVI[bkLv(y)]-LVI[bkLv(x)]||byNo(x,y));
 if(mode===2){const r=bkRng([...seed].reduce((h,c)=>h*31+c.charCodeAt(0)|0,11)),b=a.slice();for(let i=b.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[b[i],b[j]]=[b[j],b[i]]}return b}
 return a.slice().sort((x,y)=>(typeOrder.get(x.sub+'|'+x.type)||0)-(typeOrder.get(y.sub+'|'+y.type)||0)||LVI[bkLv(x)]-LVI[bkLv(y)]||byNo(x,y))}
/* 소단원 하나에서 구성 하나가 담을 문항 */
function bkfPick(d,s,pt,S,base,ctx){const byNo=(a,b)=>(a.no||0)-(b.no||0),of=f=>base.filter(q=>q.sub===s.k&&f(q)).sort(byNo);
 const lim=a=>pt.all?a:pt.cap>0?bkSpread(a,pt.cap):a;
 if(pt.k==='o'){const a=pt.all||pt.cap>0?of(q=>q.set==='ox'):(S.ox[s.k]||[]);return lim(a)}
 if(pt.k==='b'){const a=pt.all||pt.cap>0?of(q=>q.set==='blank'):(S.bl[s.k]||[]);return lim(a)}
 if(pt.k==='m'){const a=pt.all||pt.cap>0?of(q=>q.set==='mc'&&bkLv(q)==='하'):(S.basic[s.k]||[]);return lim(a)}
 const lvf=a=>pt.lv&&pt.lv!==15?a.filter(q=>bkLvOk(q,pt.lv)):a;
 if(pt.k==='t'){const used=ctx.basic[s.k]||new Set();
  let a=pt.all||pt.cap>0?of(q=>(q.set==='mc'||q.set==='top')&&!used.has(q.code)):S.type.filter(q=>q.sub===s.k&&!used.has(q.code));
  a=lvf(a);if(pt.cap>0&&!pt.all&&a.length>pt.cap)a=bkPickRound(a,pt.cap,['중','상','중','최']);return a}
 if(pt.k==='e'){let a=pt.all||pt.cap>0?of(q=>q.set==='essay'):S.essay.filter(q=>q.sub===s.k);a=lvf(a);return lim(a)}
 return []}
function bkfBlocks(d){const S=bkSel(),base=DATA.filter(q=>q.sub&&q.set!=='bank'&&!q.mock);
 const subs=S.subs.filter((s,i)=>!(d.subs||[]).length||d.subs.includes(i));
 const typeOrder=new Map();base.forEach(q=>{const k=q.sub+'|'+q.type;if(!typeOrder.has(k))typeOrder.set(k,typeOrder.size)});
 const ctx={basic:{}},pick={};
 const order=['m','t'].concat(['c','o','b','e']);
 subs.forEach(s=>{order.forEach(k=>{const pt=d.parts.find(x=>x.k===k);if(!pt)return;
  if(k==='c'){pick[s.k+'|c']=[];return}
  let a=bkfPick(d,s,pt,S,base,ctx);
  if(k==='m')ctx.basic[s.k]=new Set(a.map(q=>q.code));
  if(k==='t'||k==='e')a=bkfSort(a,d.sort,typeOrder,SUBJ+s.k+k);
  pick[s.k+'|'+k]=a})});
 const blocks=[];
 const add=(s,pt)=>{const a=pick[s.k+'|'+pt.k]||[];if(pt.k==='c'||a.length)blocks.push({s,pt,k:pt.k,arr:a})};
 if(d.grp===1)d.parts.forEach(pt=>subs.forEach(s=>add(s,pt)));else subs.forEach(s=>d.parts.forEach(pt=>add(s,pt)));
 return {S,subs,blocks,base,typeOrder}}
function bkPlanFree(id,d){
 const {S,subs,blocks,typeOrder}=bkfBlocks(d),C=CONC[SUBJ]||{secs:[]};
 const pages=[{k:'cover'},{k:'toc'}],nums=new Map(),tocM=new Map();let no=0,total=0,buf=[];const hdKey=new Map();
 const bi=new Map();blocks.forEach((b,i)=>bi.set(b,i));
 const flush=()=>{if(!buf.length)return;const u=buf;buf=[];
  bkPack(u,2,BK_BODY).forEach(p=>{const pg={k:'pr',kind:'f',label:'문제',...bkCI(p),codes:p.cols.flat().map(x=>x.code).filter(Boolean)};pages.push(pg);
   p.cols.flat().forEach(x=>{if(hdKey.has(x.key)&&!hdKey.get(x.key).p)hdKey.get(x.key).p=pages.length})})};
 let lastSub=null;
 blocks.forEach((b,i)=>{const s=b.s,nm=BKFN[b.k];
  const item={name:nm,p:0};const row=tocM.get(s.k)||(tocM.set(s.k,{sub:s,items:[]}),tocM.get(s.k));row.items.push(item);
  if(b.k==='c'){flush();
   const cu=[bkU('sb:'+s.k+':c'+i,bkSbn(s),{w:BK_FULLW,brk:true,keep:true})];
   (C.secs||[]).filter(x=>x.sub===s.k).forEach(sec=>{
    cu.push(bkU('ch:'+sec.id,'<div class="u sh2"><i>'+esc(sec.no)+'</i><span>'+esc(sec.title)+'</span></div>',{w:BK_FULLW,keep:true}));
    const dd=bkDoc('<div class="cbk">'+sec.html+'</div>').firstElementChild;
    [...dd.children].forEach((el,k)=>cu.push(bkU('cb:'+sec.id+':'+k,'<div class="u cbk">'+el.outerHTML+'</div>',{w:BK_FULLW})))});
   item.p=pages.length+1;
   bkPack(cu,1,BK_BODY).forEach(p=>pages.push({k:'cn',kind:'c',sub:s,label:'개념 정리',cols:[p.cols[0].map(u=>u.html)]}));lastSub=s.k;return}
  const newSub=d.grp!==1&&lastSub!==s.k;
  if(newSub&&d.brk)flush();
  if(d.grp===1&&i>0&&blocks[i-1].k!==b.k&&d.brk)flush();
  const units=[];
  if(newSub)units.push(bkU('sb:'+s.k+':'+i,bkSbn(s),{keep:true}));
  const hk='h:'+b.k+':'+s.k+':'+b.arr.length+':'+i;
  units.push(bkU(hk,'<div class="u ct"><span>'+nm+'</span><small>'+esc(s.k)+' · '+b.arr.length+'문항</small></div>',{keep:true}));hdKey.set(SUBJ+'|'+hk,item);
  b._n=[];
  if(b.k==='o'||b.k==='b')b.arr.forEach((q,k)=>{no++;b._n[k]=no;units.push(bkU('o:'+q.code+':'+b.k,bkOxHtml(q,no,b.k==='o'?'ox':'bl'),{code:q.code}))});
  else if(b.k==='m')b.arr.forEach((q,k)=>{no++;b._n[k]=no;units.push(bkU('q:'+q.code,bkQHtml(q,no,{code:1}),{code:q.code}))});
  else if(b.k==='t'){let cur=null,ti=0;
   b.arr.forEach(q=>{if(d.sort===0&&q.type!==cur){cur=q.type;ti++;const grp=b.arr.filter(x=>x.type===cur);const av=grp.reduce((a,x)=>a+LVI[bkLv(x)],0)/grp.length;const n=Math.max(1,Math.min(4,Math.round(av)+1));
     units.push(bkU('th:'+s.k+':'+ti+':'+cur,'<div class="th"><b>유형 '+String(ti).padStart(2,'0')+'</b><span>'+esc(cur)+'</span><small>'+'★'.repeat(n)+'☆'.repeat(4-n)+'</small></div>',{keep:true}))}
    no++;nums.set(q.code,no);b._n.push(no);units.push(bkU('q:'+q.code+':t',bkQHtml(q,no,{lv:bkLv(q),code:1}),{code:q.code}))})}
  else if(b.k==='e')b.arr.forEach(q=>{no++;nums.set(q.code,no);b._n.push(no);units.push(bkU('q:'+q.code+':e',bkQHtml(q,no,{ans:1,code:1,lv:bkLv(q)}),{code:q.code}))});
  buf.push(...units);total+=b.arr.length;lastSub=s.k});
 flush();
 // 정답·해설
 const au=[];let aStart=0;
 if(d.ans<2){let ls=null;
  blocks.forEach((b,i)=>{if(b.k==='c')return;const s=b.s,nm=BKFN[b.k];
   if(d.grp!==1&&ls!==s.k){au.push(bkU('as:'+s.k+':'+i,'<div class="u ct"><span>'+esc(s.k)+' '+esc(s.name)+'</span></div>',{keep:true}));ls=s.k}
   const mcq=b.k==='m'||b.k==='t'||b.k==='e';
   const cells=b.arr.map((q,k)=>{const n=(b._n&&b._n[k])||k+1;
    return '<div><b>'+n+'</b><span>'+(b.k==='o'?bkAnsOf(q):b.k==='b'?esc((q.blanks||[]).join(' / ')):b.k==='e'?'서술':bkCir(q.ans))+'</span></div>'}).join('');
   au.push(bkU('ak:'+b.k+':'+s.k+':'+b.arr.length+':'+i,'<div class="u k"><div class="ct sm"><span>'+(d.grp===1?esc(s.k)+' · ':'')+nm+' 정답</span></div><div class="kg '+(b.k==='b'?'w2':'')+'">'+cells+'</div></div>',{}));
   if(d.ans===0&&mcq)b.arr.forEach((q,k)=>au.push(bkU('x:'+q.code,bkXHtml(q,(b._n&&b._n[k])||k+1),{})))});
  aStart=pages.length+1;
  bkPack(au,2,BK_BODY).forEach(p=>pages.push({k:'ak',kind:'a',label:d.ans===0?'정답 · 해설':'정답',...bkCI(p)}))}
 const toc=[...tocM.values()].filter(r=>r.items.length);
 toc.forEach(r=>r.items=r.items.map(it=>[it.name,it.p||1]));
 const parts=d.parts.map(p=>BKFN[p.k]);
 if(d.dz&&d.dz.back)pages.push({k:'back'});
 return {kind:'x',free:1,dz:d.dz||null,title:d.name,short:d.name,sub:d.subt||'',pages,toc,aStart,total,parts,subs,drill:false,last:false,def:d}}

/* ---------- 쪽 HTML ---------- */
const BKCAP=BK_BODY;
function bkBase(){if(window.BKBASE)return window.BKBASE;return ((typeof CF!=='undefined'&&CF&&CF.pub)||location.href).split('#')[0].split('?')[0]}
function bkUrl(plan,p){return bkBase()+'#bk='+plan.id+':'+(plan.kind==='m'?'all':p.n)}
function bkQr(plan,p){return !!((p.codes&&p.codes.length)||(plan.kind==='m'&&p.k==='ak'))}
function bkHd2(plan,p){const even=p.n%2===0;const L='<span>'+esc(SNAME[SUBJ])+' · <b>'+esc(plan.short)+'</b></span>';const R='<span class="lb2">'+(p.sub&&p.sub.k?esc(p.sub.k)+' · ':'')+esc(p.label||'')+'</span>';
 return '<div class="hd2">'+(even?R+L:L+R)+'</div>'}
function bkFb(plan,p){const even=p.n%2===0;
 const pn='<span class="pn'+(even?'':' r')+'">'+p.n+'</span>';
 const lab='<span class="lab">'+esc(p.label||plan.short)+'</span>';
 const mid='<i></i>';
 // 양면 인쇄: 쪽 번호는 바깥쪽 모서리(짝수쪽은 왼쪽 끝, 홀수쪽은 오른쪽 끝), QR은 본문 아래 바깥쪽 모서리(.fq), 단원명은 안쪽
 const q=bkQr(plan,p)?'<div class="fq '+(even?'o-l':'o-r')+'"><div class="qq">'+qrSvg(bkUrl(plan,p))+'</div></div>':'';
 return q+'<div class="fb">'+(even?pn+mid+lab:lab+mid+pn)+'</div>'}
function bkHd(l,r,b){return '<div class="hd"><span class="t1">'+l+'</span><span class="t2">'+r+'<b>'+b+'</b></span></div>'}
function bkFt(plan,p,o){o=o||{};const qr=p.codes&&p.codes.length&&!(plan.dz&&plan.dz.noqr);
 return '<div class="ft"><span class="fl">'+(o.left||'Solvi · '+esc(plan.title))+'</span><span class="pn">'+(o.pn!=null?o.pn:p.n)+'</span>'+
  (qr?'<div class="fr2"><div class="qq">'+qrSvg(bkUrl(plan,p))+'</div></div>':o.right?'<div class="fr2"><span class="fn">'+o.right+'</span></div>':'<div></div>')+'</div>'}
function bkDeco(){const c=bkPal();
 if(SUBJ==='ph')return '<svg class="deco" viewBox="0 0 200 200"><circle cx="100" cy="100" r="78" fill="none" stroke="'+c.line+'" stroke-width="3" stroke-dasharray="6 6"/><circle cx="100" cy="100" r="46" fill="'+c.pl+'" stroke="'+c.p+'" stroke-width="3"/><circle cx="100" cy="100" r="16" fill="'+c.p+'"/><ellipse cx="100" cy="100" rx="78" ry="30" transform="rotate(-24 100 100)" fill="none" stroke="'+c.p+'" stroke-width="2.5"/><circle cx="162" cy="76" r="11" fill="'+c.pl2+'" stroke="'+c.p+'" stroke-width="3"/><circle cx="36" cy="124" r="8" fill="#ffca2c"/><polygon points="170,168 184,168 177,154" fill="'+c.p+'"/></svg>';
 if(SUBJ==='me')return '<svg class="deco" viewBox="0 0 200 200"><polygon points="100,22 168,61 168,139 100,178 32,139 32,61" fill="'+c.pl+'" stroke="'+c.p+'" stroke-width="3"/><polygon points="100,52 142,76 142,124 100,148 58,124 58,76" fill="none" stroke="'+c.line+'" stroke-width="2.5" stroke-dasharray="5 5"/>'+[[100,22],[168,61],[168,139],[100,178],[32,139],[32,61]].map(([x,y],i)=>'<circle cx="'+x+'" cy="'+y+'" r="'+(i%2?9:13)+'" fill="'+(i%2?'#fff':c.p)+'" stroke="'+c.p+'" stroke-width="3"/>').join('')+'<circle cx="100" cy="100" r="14" fill="'+c.pl2+'"/><circle cx="178" cy="22" r="8" fill="#ffca2c"/><circle cx="20" cy="176" r="10" fill="'+c.pl2+'" stroke="'+c.p+'" stroke-width="2"/></svg>';
 return '<svg class="deco" viewBox="0 0 200 200"><circle cx="100" cy="104" r="78" fill="'+c.pl+'" stroke="'+c.p+'" stroke-width="3"/><circle cx="92" cy="96" r="26" fill="'+c.p+'"/><ellipse cx="124" cy="128" rx="20" ry="11" transform="rotate(-28 124 128)" fill="none" stroke="'+c.p+'" stroke-width="3"/><circle cx="46" cy="38" r="22" fill="'+c.pl2+'" stroke="'+c.p+'" stroke-width="2.5"/><circle cx="46" cy="38" r="8" fill="'+c.p+'"/><circle cx="168" cy="40" r="9" fill="#ffca2c"/><circle cx="170" cy="168" r="15" fill="'+c.pl2+'" stroke="'+c.p+'" stroke-width="2"/></svg>'}
function bkCover(plan){
 if(plan.kind==='x')return bkCoverX(plan);
 const kd=plan.kind==='c'?'개념서':'유형서';
 const sc=plan.sel?bkScope(plan.sel):[];const part=plan.sel&&sc.length<plan.sel.subs.length;const rg=part?['범위',sc[0].name+(sc.length>1?' ~ '+sc[sc.length-1].name:'')]:null;
 const rows=(rg?[rg]:[]).concat(plan.kind==='c'?[['개념','단원별 핵심 개념 정리'],['OX · 빈칸','개념을 바로 확인'],['기초 5지선다','기본 문항으로 마무리'],['정답 · 해설','맨 뒤에 정리']]
  :[['구성','소단원 → 유형 → 난이도 순'],['문항 수','총 '+(plan.total||0)+'문항 (서술형 포함)'],['채점','쪽마다 QR로 바로 채점'],['정답 · 해설','맨 뒤에 정리']]);
 return '<div class="cv"><div class="c1"><span>Solvi · 과학</span><span>'+esc(SNAME[SUBJ])+' '+kd+'</span></div>'+bkDeco()+'<div class="c2"><div class="bar"></div><div class="kd">'+(plan.kind==='c'?'CONCEPT BOOK':'TYPE BOOK')+'</div><h1>'+esc(SNAME[SUBJ])+'</h1><h2>'+kd+'</h2><div class="ln"></div><ul>'+rows.map(r=>'<li><b>'+r[0]+'</b><span>'+r[1]+'</span></li>').join('')+'</ul></div>'+
  '<div class="c4">문제 쪽 아래 QR을 스캔하면 그 페이지를 바로 채점할 수 있습니다</div></div>'}
function bkNvTone(){const hex=(bkPal().p||'#2a72bf').replace('#','');const r=parseInt(hex.slice(0,2),16)/255,g=parseInt(hex.slice(2,4),16)/255,b=parseInt(hex.slice(4,6),16)/255;
 const mx=Math.max(r,g,b),mn=Math.min(r,g,b),l=(mx+mn)/2,d=mx-mn;let h=0,sa=0;if(d){sa=d/(1-Math.abs(2*l-1));h=mx===r?((g-b)/d)%6:mx===g?(b-r)/d+2:(r-g)/d+4;h=(h*60+360)%360}
 const S=Math.max(.45,Math.min(.8,sa||.6));const f=L=>{const c=(1-Math.abs(2*L-1))*S,x=c*(1-Math.abs((h/60)%2-1)),m=L-c/2;const [R,G,B]=h<60?[c,x,0]:h<120?[x,c,0]:h<180?[0,c,x]:h<240?[0,x,c]:h<300?[x,0,c]:[c,0,x];return '#'+[R,G,B].map(v=>Math.round((v+m)*255).toString(16).padStart(2,'0')).join('')};
 const yellow=h>=38&&h<=70&&sa>.3;return '--c1:'+f(.13)+';--c2:'+f(.2)+';--c3:'+f(.31)+';--acc:'+(yellow?'#ffffff':'#ffc933')+';--on:'+f(.13)}
function bkCxDef(){const m={me:['MATTER & ENERGY','E'],cm:['CELLS & METABOLISM','C'],ph:['MECHANICS & ENERGY','M']}[SUBJ]||['SCIENCE','S'];return {en:m[0],ser:'SCIENCE SERIES',small:'SCIENCE',school:'',grade:'',wm:m[1]}}
function bkCx(plan){const d=bkCxDef(),z=(plan.dz&&plan.dz.cx)||{};const o={};Object.keys(d).forEach(k=>{o[k]=z[k]!=null&&String(z[k]).trim()!==''?String(z[k]).trim():(k==='school'||k==='grade'?'':d[k])});return o}
function bkCxCard(d){const c={...bkCxDef(),...(d.cx||{})},f=(id,lab,v,ph,w)=>`<div class="bkrow"><label for="bxcx_${id}">${lab}</label><input id="bxcx_${id}" class="bkin" value="${esc(v||'')}" placeholder="${esc(ph||'')}" maxlength="${w||30}" oninput="bkfRead();bkxEst()"></div>`;
 return `<div class="bkc"><h3>시리즈형 표지 문구 <small>비우면 과목에 맞는 기본 문구가 들어가요 · 학교·학년을 비우면 그 칸은 표지에서 빠져요</small></h3>${f('en','영문 제목',c.en,bkCxDef().en,28)}${f('small','작은 영문',c.small,'SCIENCE',16)}${f('ser','시리즈 문구',c.ser,'SCIENCE SERIES',24)}${f('school','학교',c.school,'예: 해원고',14)}${f('grade','학년',c.grade,'예: 2학년',10)}${f('wm','큰 배경 글자',c.wm,'1글자',1)}</div>`}
function bkCoverNavy(plan){const c=bkCx(plan),en=esc(c.en).replace(/ &amp; /,'<br>&amp; ').replace(/ & /,'<br>&amp; ');
 return '<div class="cv nv" style="'+bkNvTone()+'"><div class="wm" aria-hidden="true">'+esc(c.wm)+'</div><div class="tl"><div class="sr">'+esc(c.ser)+'</div><div class="bk">'+esc(SNAME[SUBJ])+'</div></div><div class="tb"><div class="sm">'+esc(c.small)+'</div><div class="bg">'+en+'</div><div class="ru"></div><div class="ko">'+esc(SNAME[SUBJ])+'</div>'+(plan.title&&plan.title!==SNAME[SUBJ]?'<div class="bn">'+esc(plan.title)+(plan.sub?' · '+esc(plan.sub):'')+'</div>':'')+'</div>'+((c.school||c.grade)?'<div class="sb"><div class="sl">SCHOOL</div>'+(c.school?'<div class="sn">'+esc(c.school)+'</div>':'')+(c.grade?'<div class="gr">'+esc(c.grade)+'</div>':'')+'</div>':'')+'</div>'}
function bkBackNavy(plan){const c=bkCx(plan),en=esc(c.en).replace(/ &amp; /,'<br>&amp; ').replace(/ & /,'<br>&amp; ');
 return '<div class="cv nv bkn" style="'+bkNvTone()+'"><div class="wm" aria-hidden="true">'+esc(c.wm)+'</div><div class="ct2"><div class="ru"></div><div class="bg">'+en+'</div><div class="ko">'+esc(SNAME[SUBJ])+'</div></div><div class="bt2"><div><div class="sr">'+esc(c.ser)+'</div><div class="bk">'+esc(SNAME[SUBJ])+'</div></div>'+((c.school||c.grade)?'<div class="sc2">'+esc(c.school)+(c.grade?'<span>'+esc(c.grade)+'</span>':'')+'</div>':'')+'</div></div>'}
function bkCoverX(plan){if(plan.dz&&plan.dz.cover===6)return bkCoverNavy(plan);const rows=[['구성',plan.parts.join(' · ')||'—'],['문항 수','총 '+plan.total+'문항'+(plan.drill?' (양치기)':'')],['소단원',plan.subs.length+'개'],['정답 · 해설',plan.free&&plan.def?['맨 뒤에 정답 · 해설','맨 뒤에 정답표만','정답 없음'][plan.def.ans|0]:'맨 뒤에 정리']];
 return '<div class="cv'+(plan.dz&&plan.dz.cover?' cs'+plan.dz.cover:'')+'"><div class="c1"><span>Solvi · 과학</span><span>'+esc(SNAME[SUBJ])+'</span></div>'+bkDeco()+'<div class="c2"><div class="bar"></div><div class="kd">'+(plan.last?'FINAL CHECK':plan.drill?'DRILL BOOK':'MY BOOK')+'</div><h1>'+esc(plan.title)+'</h1><h2>'+esc(plan.sub||SNAME[SUBJ])+'</h2><div class="ln"></div><ul>'+rows.map(r=>'<li><b>'+r[0]+'</b><span>'+esc(r[1])+'</span></li>').join('')+'</ul></div>'+
  '<div class="c4">문제 쪽 아래 QR을 스캔하면 그 페이지를 바로 채점할 수 있습니다</div>'+bkCoverLogo(plan)+'</div>'}
function bkLogoHtml(src,cls){if(!src||src==='none')return '';
 if(src==='solvi'){const c=bkPal();return '<svg class="'+cls+'" viewBox="'+WMVB+'" role="img" aria-label="Solvi"><path d="'+WMD+'" fill="'+c.pd+'"/><path d="'+WMU+'" fill="none" stroke="#ffc21a" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>'}
 if(src==='academy'){const c=acCfg(),u=c.logo||c.logoDark;if(c.mode==='logo'&&u)return '<img class="'+cls+'" src="'+u+'" alt="">';if(c.name)return '<span class="'+cls+' tx">'+esc(c.name)+'</span>';if(u)return '<img class="'+cls+'" src="'+u+'" alt="">'}
 return ''}
function bkCoverLogo(plan){const z=plan.dz;if(!z||!z.lf||z.lf==='none')return '';const h=bkLogoHtml(z.lf,'lg');return h?'<div class="cvlogo '+(z.lfp==='bl'?'L':z.lfp==='bc'?'C':'R')+'">'+h+'</div>':''}
function bkBackCover(plan){const z=plan.dz||{};if(z.cover===6)return bkBackNavy(plan);const h=bkLogoHtml(z.lb||'solvi','lg');
 return '<div class="cv cvb"><div class="cvbt"><b>'+esc(plan.title)+'</b>'+(plan.sub?'<span>'+esc(plan.sub)+'</span>':'')+'</div>'+(h?'<div class="cvlg '+(z.lbp==='tc'?'tc':'bc')+'">'+h+'</div>':'')+'</div>'}
function bkTocX(plan){
 let h='<div class="toc"><h3>차 례</h3><table><tr><th>소단원</th><th>구성 · 쪽</th></tr>'+plan.toc.map(r=>'<tr><td class="s">'+esc(r.sub.k)+' '+esc(r.sub.name)+'</td><td>'+r.items.map(([n,p])=>esc(n)+' <b style="color:var(--pd)">p.'+p+'</b>').join(' · ')+'</td></tr>').join('')+(plan.toc.es?'<tr><td class="s">서술형</td><td>'+plan.toc.es.n+'문항 <b style="color:var(--pd)">p.'+plan.toc.es.p+'</b></td></tr>':'')+'<tr><td class="s">정답 · 해설</td><td>'+(plan.aStart?'<b style="color:var(--pd)">p.'+plan.aStart+'</b>':'없음')+'</td></tr></table>';
 h+='<div class="how"><h4>이 책의 활용법</h4>① 소단원마다 구성 순서대로 풀어 나간다.<br>② 한 쪽을 풀 때마다 아래 <b>QR을 스캔</b>해 채점한다.<br>③ 틀린 문제는 맨 뒤 해설로 확인한다.</div></div>';return h}
function bkToc(plan){
 let h='<div class="toc"><h3>차 례</h3>';
 if(plan.kind==='x'){return bkTocX(plan)}
 if(plan.kind==='c'){
  h+='<table><tr><th>소단원</th><th>개념 정리</th><th>OX</th><th>빈칸</th><th>기초 5지선다</th></tr>'+plan.toc.map(r=>'<tr><td class="s">'+esc(r.sub.k)+' '+esc(r.sub.name)+'</td><td class="n">'+(r.c||'')+'</td><td class="n">'+(r.ox||'')+'</td><td class="n">'+(r.bl||'')+'</td><td class="n">'+(r.mc||'')+'</td></tr>').join('')+'<tr><td class="s">정답 · 해설</td><td class="n" colspan="4">'+plan.aStart+'</td></tr></table>';
  h+='<div class="how"><h4>이 책의 활용법</h4>① 개념 정리를 읽고 <b>굵은 글씨와 표시된 부분</b>을 중심으로 정리한다.<br>② OX와 빈칸으로 개념을 바로 확인한다.<br>③ 기초 5지선다로 기본 문항을 풀고 맨 뒤 해설로 확인한다.<br>④ 문제 쪽 아래 <b>QR을 스캔</b>하거나 솔비 앱의 「교재」 탭에서 쪽을 골라 채점한다.</div>'}
 else{
  h+='<table><tr><th>소단원</th><th>문항 수</th><th>쪽</th></tr>'+plan.toc.map(r=>'<tr><td class="s">'+esc(r.sub.k)+' '+esc(r.sub.name)+'</td><td class="n">'+r.n+'</td><td class="n">'+r.p+'</td></tr>').join('')+(plan.toc.es?'<tr><td class="s">서술형</td><td class="n">'+plan.toc.es.n+'</td><td class="n">'+plan.toc.es.p+'</td></tr>':'')+'<tr><td class="s">정답 · 해설</td><td class="n"></td><td class="n">'+plan.aStart+'</td></tr></table>';
  h+='<div class="how"><h4>이 책의 활용법</h4>① 소단원마다 <b>유형</b>으로 묶여 있고, 유형 안에서는 <b>쉬운 문제 → 어려운 문제</b> 순으로 배열되어 있다.<br>② 난이도 표시 <b>[하] [중] [상] [최]</b>를 보고 막히는 구간부터 다시 풀어 본다.<br>③ 한 쪽을 풀 때마다 아래 <b>QR을 스캔</b>해 채점하고, 틀린 유형은 솔비의 취약 유형 분석으로 확인한다.<br>④ 서술형은 맨 뒤 모범 답안과 비교해 스스로 채점한다.</div>'}
 return h+'</div>'}
function bkMockCover(plan){const M=plan.M;
 return '<div class="cv2"><div class="row1"><div>'+'Solvi'+'</div><div>'+'전범위'+'</div><div>'+esc(M.sname)+'</div></div><div class="ttl"><div class="a">전 범 위 모 의 고 사</div><div class="b">'+esc(M.sname)+'</div><div class="c">제 '+M.round+' 회 [ '+esc(M.title)+' ]</div><div class="ln"></div></div>'+
 '<table class="info3"><tr><th>출제 범위</th><td>'+M.range.map(esc).join('<br>')+'</td></tr><tr><th>문항 · 배점</th><td>객관식 '+M.codes.length+'문항 · '+M.tot+'점</td></tr><tr><th>시험 시간</th><td>'+esc(M.time)+'</td></tr></table>'+
 '<div class="note"><h3>유 의 사 항</h3><ol><li>시험 시작 종이 울린 후 문제지의 해당란에 학년, 반, 번호, 이름을 정확히 쓰시오.</li><li>모든 문항은 객관식이며, ①~⑤ 중 가장 적절한 것 하나를 고르시오.</li><li>각 문항의 끝에 표시된 배점을 참고하여 시간을 안배하시오.</li><li>문제지 뒤의 정답 및 해설은 시험이 끝난 후에 확인하시오.</li><li>표지와 문제 쪽 아래의 QR은 모두 같으며, 스캔하면 시험 전체를 채점할 수 있다.</li></ol></div>'+
 '<table class="idt"><tr><td class="k">학 년</td><td style="width:20mm"></td><td class="k">반</td><td style="width:20mm"></td><td class="k">번 호</td><td style="width:20mm"></td><td class="k">이 름</td><td></td></tr></table><div class="cvqr"><div class="qq">'+qrSvg(bkUrl(plan,{n:0}))+'</div><span>어느 쪽의 QR을 스캔해도<br>시험 전체를 채점해요</span></div><div class="foot">이 문제지의 저작권은 출제자에게 있으며, 무단 복제 · 전재를 금합니다.</div></div>'}
const BKGUTS=[[0,'없음'],[3,'3mm'],[5,'5mm'],[7,'7mm']];
function bkGutKey(plan){const P=bkParts(plan.id);return P&&P.kind==='x'?P.def.base:bkBare(plan.id)}
function bkGutOf(plan){if(!plan||!plan.id||plan.subj==='me')return 0;const k=bkGutKey(plan);const m=BKO.gutm||{};if(m[k]!=null)return +m[k]||0;const r=bkxAll().find(x=>x.id===k);return r&&+r.gut||0}
function bkGutSet(key,v){const m=Object.assign({},BKO.gutm||{});m[key]=+v||0;bkOset({gutm:m})}
function bkPageHtml(plan,i){const h=bkPageHtml0(plan,i),f=plan.dz&&plan.dz.font&&typeof FONTS!=='undefined'&&FONTS[plan.dz.font];return f?'<style>.bp,.bp *{font-family:'+f[1]+'!important}</style>'+h:h}
function bkPageHtml0(plan,i){
 BKDZ=plan.dz||null;
 const p=plan.pages[i];const g=p.k==='cover'?0:bkGutOf(plan);const V=' style="'+bkVars()+(g?';--gx:'+((p.n%2?1:-1)*g)+'mm':'')+'"'+(g?' data-gut="1"':'');
 if(p.k==='cover')return '<div class="bp bk"'+V+'>'+bkCover(plan)+'</div>';
 if(p.k==='back')return '<div class="bp bk"'+V+'>'+bkBackCover(plan)+'</div>';
 if(p.k==='toc')return '<div class="bp bk"'+V+'>'+bkHd2(plan,p)+'<div class="bd one">'+bkToc(plan)+'</div>'+bkFb(plan,p)+'</div>';
 if(p.k==='cn')return '<div class="bp bk"'+V+'>'+bkHd2(plan,p)+'<div class="bd one">'+p.cols[0].join('')+'</div>'+bkFb(plan,p)+'</div>';
 if(p.k==='mcv')return '<div class="bp mk'+(BKO.design==='color'?' cl':'')+'"'+V+'>'+bkMockCover(plan)+'</div>';
 if(p.k==='mq'){const M=plan.M;
  const t1="Solvi 전범위<em>"+esc(M.sname+' · '+M.title+' '+M.round+'회')+"</em>";
  const h2='<div class="hd"><span class="t1">'+t1+'</span><span class="t2">문제지<b>'+p.idx+' / '+p.of+'</b></span></div>';
  const info=p.first?'<div class="info"><div class="l">'+esc(M.sname)+' · 제 '+M.round+'회<div><span>학년</span><span>반</span><span>번호</span><span>이름</span></div></div><div class="r">점 수<small>/ '+M.tot+'</small></div></div>':'';
  return '<div class="bp mk'+(BKO.design==='color'?' cl':'')+'"'+V+'>'+h2+info+'<div class="'+(p.first?'bd wi':'bd')+'"><div class="cols">'+p.cols.map((c,ci)=>'<div class="col"'+(p.gaps&&p.gaps[ci]?' style="--g:'+p.gaps[ci]+'mm"':'')+'>'+c.join('')+'</div>').join('')+'</div></div>'+
   bkFt(plan,p,{left:'Solvi · '+plan.title,pn:p.idx,right:'※ 제시된 시간 안에 풀고 답을 점검하시오.'})+'</div>'}
 // pr, es, ak
 return '<div class="bp bk"'+V+'>'+bkHd2(plan,p)+'<div class="bd"><div class="cols">'+p.cols.map((c,ci)=>'<div class="col"'+(p.gaps&&p.gaps[ci]?' style="--g:'+p.gaps[ci]+'mm"':'')+'>'+c.join('')+'</div>').join('')+'</div></div>'+bkFb(plan,p)+'</div>'}

/* ---------- 채점 · 경로 ---------- */
function bkPageNums(p){const o={};(p.cols||[]).forEach(c=>c.forEach(h=>{const m=String(h).match(/data-c="([^"]+)"/);if(!m)return;const n=String(h).match(/class="no">(\d+)</)||String(h).match(/class="nc"><b>(\d+)<\/b>/);if(n)o[m[1]]=+n[1]}));return o}
async function bkSolve(id,n){await bkInit();const P=bkParts(id);if(!P)return;if(P.subj!==SUBJ)await setSubject(P.subj);await conceptLoad();const plan=await bkPlan(id);if(!plan)return;
 let codes=[];if(!n){codes=plan.M?plan.M.codes.slice():[]}else{const p=plan.pages.find(x=>x.n===+n);codes=(p&&p.codes)||[]}
 if(!codes.length){toast('p.'+n+'에는 풀 문제가 없어요');return}
 const title=n?plan.short+' p.'+n:plan.short;await practice(codes,title)}
async function bkGradePage(id,n){
 if(needLogin()){askLogin('BK:'+id+':'+n);return}
 await bkInit();const P=bkParts(id);if(!P)return;
 if(P.subj!==SUBJ)await setSubject(P.subj);
 await conceptLoad();const plan=await bkPlan(id);const p=plan&&plan.pages.find(x=>x.n===+n);
 if(!p||!p.codes||!p.codes.length){const ks=plan?plan.pages.filter(x=>x.codes&&x.codes.length).map(x=>x.n):[];toast('p.'+n+'에는 채점할 문제가 없어요'+(ks.length?' (문제가 있는 쪽: p.'+ks[0]+' ~ p.'+ks[ks.length-1]+')':''));return}
 if(guardStu())return;
  const qs=p.codes.map(c=>byCode[c]).filter(Boolean);if(!qs.length){toast('문항을 불러오지 못했어요');return}
 const key=id+':'+p.n,bk={page:key,bk:id,n:p.n,label:plan.short+' p.'+p.n,nums:bkPageNums(p)};
 {const lk=recLock('book',key);if(lk&&lk.items){showLockedRec(lk,{book:bk});return}}
 newCur(qs,{book:bk})}
async function bkGradeAll(id){
 if(needLogin()){askLogin('BK:'+id+':all');return}
 await bkInit();const P=bkParts(id);if(!P)return;if(P.subj!==SUBJ)await setSubject(P.subj);
 const plan=await bkPlan(id);if(guardStu())return;
 if(!plan||!plan.M)return;const qs=plan.M.codes.map(c=>byCode[c]).filter(Boolean);if(!qs.length)return;
 const key=id+':all',bk={page:key,bk:id,n:0,all:1,label:plan.short+' 전체',nums:Object.fromEntries(plan.M.codes.map((c,i)=>[c,i+1]))};
 {const lk=recLock('book',key);if(lk&&lk.items){showLockedRec(lk,{book:bk});return}}
 newCur(qs,{book:bk})}
function bkRouteStr(s){const m=String(s).match(/^((?:me|cm|ph)-(?:c|t|x[0-9a-z._\-]+)(?:~g[1-3])?):(\d+|all)$/);if(!m)return;return m[2]==='all'?bkGradeAll(m[1]):bkGradePage(m[1],+m[2])}
function bkNextHtml(){const b=cur&&cur.book;if(!b||!b.bk||b.all)return '';const plan=BKP[b.bk];if(!plan)return '';
 const nx=plan.pages.find(p=>p.n>b.n&&p.codes&&p.codes.length);
 return nx?'<div class="hint" style="margin:10px 0">'+esc(plan.short)+' p.'+b.n+' 채점을 마쳤습니다. 다음 문제 쪽(<b>p.'+nx.n+'</b>)도 이어서 채점할까요? <button class="p" style="margin-left:8px" onclick="bkGradePage(\''+b.bk+'\','+nx.n+')">p.'+nx.n+' 채점하기</button></div>':''}

/* ---------- 교재함 · 리더 ---------- */
let BKV={v:'shelf',id:null,z:1};
function bkDupTog(){dupSet(!dupGet());const b=document.getElementById('bkdup');if(b)b.classList.toggle('on',!!dupGet())}
function bkZoom(d){const Z=[1,1.6,2.4,3.2];let i=d===0?0:Z.indexOf(BKV.z||1);i=Math.max(0,Math.min(Z.length-1,i+d));BKV.z=Z[i];bkScale();const l=document.getElementById('bkzl');if(l)l.textContent=Math.round(Z[i]*100)+'%'}
function bkBookList(){const S=bkSel();const sk=bkScope(S).map(s=>s.k),inS=k=>sk.includes(k),sm=o=>sk.reduce((a,k)=>a+(o[k]||[]).length,0);const part=sk.length<S.subs.length,rg=part?' · 범위 '+bkScope(S)[0].name+(sk.length>1?' ~ '+bkScope(S)[sk.length-1].name:''):'';
 const nd=!!(CONC[SUBJ]||{}).noDefaultBooks;
 const L=nd?[]:[
 {id:SUBJ+'-c',name:'개념서',sub:'개념 정리 · OX · 빈칸 · 기초 5지선다'+rg,meta:'OX '+sm(S.ox)+' · 빈칸 '+sm(S.bl)+' · 기초 '+sm(S.basic)+'문항'},
 {id:SUBJ+'-t',name:'유형서',sub:'소단원 → 유형 → 난이도별 문제 (N제)'+rg,meta:'객관식·단답형 '+S.type.filter(q=>inS(q.sub)).length+' · 서술형 '+S.essay.filter(q=>inS(q.sub)).length+'문항'}];
 bkxAll().filter(b=>b.subj===SUBJ).forEach(b=>L.push({id:b.id,name:b.name,sub:b.sub||BKK[b.kind==='full'?'full':'std'][0],meta:b.asg?'선생님이 배포한 교재'+(b.due?' · 마감 '+b.due:''):b.kind==='full'?'전범위 · '+(b.rounds||20)+'회분':'내가 만든 교재',custom:1,asg:!!b.asg,full:b.kind==='full'}));
 return L}
async function bkShow(){
 await bkInit();await conceptLoad();
 if(BKV.id&&bkParts(BKV.id)&&bkParts(BKV.id).subj!==SUBJ){BKV={v:'shelf',id:null}}
 if(BKV.v==='new'&&(bkIsStud()||(BKV.d&&BKV.d.subj&&BKV.d.subj!==SUBJ)))BKV={v:'shelf',id:null}
 if(BKV.v==='read'&&BKV.id)return bkReader(BKV.id);
 if(BKV.v==='new'){$('#main').innerHTML=bkBuilder();bkxEst();return}
 if(BKV.v==='rounds'){$('#main').innerHTML=bkRounds(BKV.id);return}
 const L=bkBookList(),m=$('#main');
 const card=b=>`<div class="bkcard"><div class="bkcov"><i></i><b>${esc(b.custom?b.name:SNAME[SUBJ])}</b><span>${esc(b.custom?SNAME[SUBJ]:b.name)}</span><em>Solvi</em></div><div class="bi2"><h3>${esc(b.name)}</h3><p>${esc(b.sub)}<br><small>${esc(b.meta)}</small></p><div class="bt2">${b.full?`<button class="p" onclick="BKV={v:'rounds',id:'${b.id}'};bkShow()">회차 보기</button>`:`<button class="p" onclick="bkOpen('${b.id}')">열기</button><button class="s" onclick="bkPrint('${b.id}',1)">인쇄 · PDF</button>`}${b.custom&&!b.asg&&bkCanDist()?`<button class="s" onclick="bkDistOpen('${b.id}')">학생에게 배포${bkDistN(b.id)?' · '+bkDistN(b.id)+'명':''}</button>`:''}${b.custom&&!b.asg?`<button class="s" onclick="bkxDel('${b.id}')">삭제</button>`:''}</div></div></div>`;
 m.innerHTML=`<div class="card"><h2>교재 <small style="font-weight:400;color:var(--m);font-size:13px">${esc(SNAME[SUBJ])}</small></h2>
 <p style="margin:-4px 0 14px;font-size:13px;color:var(--m);line-height:1.6">문제 쪽 아래 <b>QR</b>을 스캔하면 그 쪽이 바로 채점돼요.</p>
 ${L.some(b=>!b.custom)?`<div class="bkshelf">${L.filter(b=>!b.custom).map(card).join('')}</div>`:(bkIsStud()?`<div class="m" style="font-size:13px">이 과목은 기본 교재 없이, 선생님이 배포한 교재를 아래에서 열어 볼 수 있어요.</div>`:`<div class="m" style="font-size:13px">이 과목은 기본 교재 없이, 아래 <b>교재 만들기</b>로 필요한 범위·유형만 골라 처음부터 만들어요.</div>`)}</div>
 <div class="card"><div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap"><h2 style="margin:0">${bkIsStud()?'배포받은 교재':'내 교재'}</h2>${bkIsStud()?'':`<button class="p" onclick="bkNew('std')">＋ 교재 만들기</button>`}</div>
 <p style="margin:6px 0 12px;font-size:13px;color:var(--m);line-height:1.6">${bkIsStud()?'선생님이 배포한 교재가 여기에 나와요. 교재는 선생님이 만들어 배포해요.':'종합, 직전 대비, 양치기, 전범위 모의고사 중에서 골라 만들어요. 만든 교재는 「학생에게 배포」로 학생 화면에 올릴 수 있어요.'}</p>
 ${L.some(b=>b.custom)?`<div class="bkshelf">${L.filter(b=>b.custom).map(card).join('')}</div>`:bkIsStud()?`<div class="m" style="font-size:13px">아직 배포받은 교재가 없어요.</div>`:`<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:8px">${['std','last','drill','part','full'].map(k=>`<button class="s" onclick="bkNew('${k}')" style="text-align:left;padding:12px;border-radius:10px"><b style="display:block">${BKK[k][0]}</b><small style="font-weight:400;color:var(--m)">${BKK[k][1]}</small></button>`).join('')}</div>`}</div>`}
function bkGroups(plan){const g=new Map();plan.pages.forEach(p=>{if(!p.codes||!p.codes.length)return;const k=plan.kind==='m'?'문제지':((p.sub?p.sub.k+' ':'')+(p.label||''));if(!g.has(k))g.set(k,[]);g.get(k).push(p)});return g}
async function bkPath(lv){
 const s1=$('#bkp1'),s2=$('#bkp2'),s3=$('#bkp3'),go=$('#bkpg');
 if(lv===1){s2.innerHTML='<option value="">구간 고르기</option>';s3.innerHTML='<option value="">쪽 고르기</option>';s2.disabled=s3.disabled=go.disabled=true;if(!s1.value)return;
  const plan=await bkPlan(bkBare(s1.value)+bkSufOf());BKV._g=bkGroups(plan);BKV._plan=plan;
  s2.innerHTML='<option value="">구간 고르기</option>'+(plan.kind==='m'?[]:[...BKV._g]).map(([k,a])=>`<option value="${esc(k)}">${esc(k)} (${a.length}쪽)</option>`).join('')+(plan.kind==='m'?'<option value="__all">시험 전체 (한 번에)</option>':'');s2.disabled=false;return}
 if(lv===2){s3.innerHTML='<option value="">쪽 고르기</option>';s3.disabled=true;go.disabled=true;const v=s2.value;if(!v)return;if(v==='__all'){go.disabled=false;return}
  const a=BKV._g.get(v)||[];s3.innerHTML=a.map(p=>`<option value="${p.n}">p.${p.n} · ${p.codes.length}문항</option>`).join('');s3.disabled=false;go.disabled=false}}
function bkSufOf(){const g=document.getElementById('bkpgap');const v=g?+g.value:0;return v?'~g'+v:''}
function bkPathGo(){const id=bkBare($('#bkp1').value)+bkSufOf(),v=$('#bkp2').value;if(!$('#bkp1').value||!v)return;if(v==='__all')return bkGradeAll(id);const n=$('#bkp3').value;if(n)bkGradePage(id,+n)}
async function bkPathMount(el){await bkInit();await conceptLoad();const L=bkBookList();
 el.innerHTML=`<div class="bkpath"><div><label>책</label><select id="bkp1" onchange="bkPath(1)"><option value="">책 고르기</option>${L.map(b=>b.full?Array.from({length:(bkxAll().find(x=>x.id===b.id)||{}).rounds||20},(_,i)=>`<option value="${b.id}r${i+1}">${esc(b.name)} ${i+1}회</option>`).join(''):`<option value="${b.id}">${esc(b.name)}</option>`).join('')}</select></div>
 <div><label>소단원 · 구성</label><select id="bkp2" onchange="bkPath(2)" disabled><option value="">고르기</option></select></div>
 <div><label>쪽</label><select id="bkp3" disabled><option value="">쪽 고르기</option></select></div>
 <div><button class="p" id="bkpg" onclick="bkPathGo()" disabled style="width:100%">채점 시작</button></div></div>`}
function bkOpen(id){if(tab!=='books'){tab='books'}BKV={v:'shelf',id:null};render();bkEbook(id)}
function bkClose(){BKV={v:'shelf',id:null};render();scrollTo(0,0)}
function bkScale(){const w=document.getElementById('bkpages');if(!w)return;const W=w.clientWidth;const s=Math.min(1,W/(210*BK_MM))*(BKV.z||1);w.style.setProperty('--bks',s.toFixed(4));w.style.setProperty('--bkw',(210*BK_MM*s)+'px');w.style.setProperty('--bkh',(297*BK_MM*s)+'px')}
async function bkReader(id){
 id=bkPid(id);
 const m=$('#main');m.innerHTML='<div class="card">'+ldg('책을 펴는 중…')+'</div>';
 const plan=await bkPlan(id);if(!plan){bkClose();return}
 const jumps=[];if(plan.kind==='c'){plan.toc.forEach(r=>{jumps.push([r.sub.k+' '+r.sub.name+' · 개념',r.c]);if(r.ox)jumps.push(['　'+r.sub.k+' OX',r.ox]);if(r.bl)jumps.push(['　'+r.sub.k+' 빈칸',r.bl]);if(r.mc)jumps.push(['　'+r.sub.k+' 기초 5지선다',r.mc])})}
 else if(plan.kind==='t'){plan.toc.forEach(r=>jumps.push([r.sub.k+' '+r.sub.name,r.p]));if(plan.toc.es)jumps.push(['서술형',plan.toc.es.p])}
 else if(plan.kind==='x'){plan.toc.forEach(r=>r.items.forEach(([n,p])=>jumps.push([r.sub.k+' '+n,p])));if(plan.toc.es)jumps.push(['서술형',plan.toc.es.p])}
 else{jumps.push(['문제지',2],['정답 및 해설',plan.aStart])}
 jumps.push(['정답 · 해설',plan.aStart]);const seen=new Set();const J=jumps.filter(j=>j[1]&&!seen.has(j[0]+j[1]) && seen.add(j[0]+j[1]));
 m.innerHTML=`<div class="bkrd">${tbT('','bkClose()','교재함으로','shelf','교재함')}<b class="bkt">${esc(plan.title)}</b><span class="sp1"></span>${tbS('bkj','bkJump(this.value)','목차로 이동','toc','목차','<option value="">이동…</option><option value="1">표지</option>'+J.map(j=>`<option value="${j[1]}">${esc(j[0])} · p.${j[1]}</option>`).join(''))}${plan.kind==='m'?tbT('','bkGradeAll(\''+id+'\')','시험 전체 채점','grade','전체 채점','pr'):''}${tbT('','thumbTog(\'#main>.thr\')','쪽 썸네일 보이기/숨기기','thumb','썸네일')}${bkCanDist()&&bkxAll().some(x=>x.id===id&&!x.asg)?tbT('','bkDistOpen(\''+id+'\')','학생에게 배포','send','배포'):''}<i class="tbv"></i>${tbT('','bkZoom(-1)','작게','zout','축소')}<button class="tbx" onclick="bkZoom(0)" title="크기 초기화"><b class="pct" id="bkzl">${Math.round((BKV.z||1)*100)}%</b><span class="lb">배율</span></button>${tbT('','bkZoom(1)','크게','zin','확대')}<i class="tbv"></i>${typeof ft==='function'&&!ft('ebook')?'':tbT('','bkEbook(\''+id+'\')','eBook으로 보기 (필기·수업 모드)','ebook','eBook','pr')}${tbT('bkdup','bkDupTog()','인쇄·PDF에서 답안이 뒷면에서 시작하지 않게 빈 쪽을 채워요','duplex','양면',dupGet()?'on':'')}<i class="tbv"></i>${tbT('','bkPdf(\''+id+'\',1)','PDF로 받기','pdf','PDF')}${tbT('','bkPrint(\''+id+'\',0)','문제만 인쇄','print','문제만')}${tbT('','bkPrint(\''+id+'\',1)','전체 인쇄 · PDF (정답·해설 포함)','print','전체 인쇄','pr')}</div><div id="bkpages"></div>`;
 const hdr=document.querySelector('header');const rd=document.querySelector('.bkrd');if(rd&&hdr)rd.style.top=(hdr.getBoundingClientRect().height+6)+'px';const box=$('#bkpages');bkScale();
 box.innerHTML=plan.pages.map((p,i)=>`<div class="bkw" id="bkpg${p.n}" data-i="${i}" style="width:var(--bkw);height:var(--bkh)"></div>`+(p.codes&&p.codes.length?`<div class="bkbar" style="width:var(--bkw)"><span><b>p.${p.n}</b> · ${p.codes.length}문항</span>${STUD&&!permOn('pageSolve')?'':`<button class="s" onclick="bkSolve('${id}',${plan.kind==='m'?0:p.n})">${plan.kind==='m'?'시험 화면에서 풀기':'이 쪽 풀기'}</button>`}<button class="p" onclick="${plan.kind==='m'?`bkGradeAll('${id}')`:`bkGradePage('${id}',${p.n})`}">${plan.kind==='m'?'시험 전체 채점하기':'이 쪽 채점하기'}</button></div>`:'<div style="height:10px"></div>')).join('');
 const fill=el=>{if(el.dataset.f)return;el.dataset.f=1;bkShadow(el,'<div class="bkdoc scr">'+bkPageHtml(plan,+el.dataset.i)+'</div>')};
 if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){fill(e.target);io.unobserve(e.target)}}),{rootMargin:'900px 0px'});box.querySelectorAll('.bkw').forEach(e=>io.observe(e))}
 else box.querySelectorAll('.bkw').forEach(fill);
 {const r=thumbRail({parent:m,n:plan.pages.length,label:i=>String(plan.pages[i].n),render:(el,i)=>{el.style.setProperty('--bks','1');bkShadow(el,'<div class="bkdoc scr">'+bkPageHtml(plan,i)+'</div>')},go:i=>bkJump(plan.pages[i].n)});
  const rd2=document.querySelector('.bkrd');r.setTop(Math.max(8,(rd2?rd2.getBoundingClientRect().bottom:60)+8));window._bkrail=r;thumbAct(r,0)}
 if(!window._bkrs){window._bkrs=1;addEventListener('resize',()=>{if(tab==='books'&&BKV.v==='read')bkScale()});
  let tk=0;addEventListener('scroll',()=>{if(tk||tab!=='books'||BKV.v!=='read'||!window._bkrail||!document.contains(window._bkrail))return;tk=requestAnimationFrame(()=>{tk=0;let k=0;document.querySelectorAll('#bkpages .bkw').forEach(e=>{if(e.getBoundingClientRect().top<=140)k=+e.dataset.i});thumbAct(window._bkrail,k)})},{passive:true})}}
function bkJump(n){const e=document.getElementById('bkpg'+n);if(e){const y=e.getBoundingClientRect().top+scrollY-64;scrollTo({top:y,behavior:'smooth'})}const s=$('#bkj');if(s)s.value=''}


/* ---------- eBook 뷰어: 교재 열기의 기본 화면 · 수업용(프로젝터) · 확대/축소 · 펜 필기 · 번호 눌러 정답/해설 ---------- */
let EBK_dummy;let EBKFX=(()=>{try{return localStorage.getItem('omr_ebfx')!=='0'}catch(e){return true}})();const EBK={tool:'none',color:'#e5484d',w:3,finger:0,proj:0,wh:0,z:1,rev:[],rows:[]};
function ebkSt(){try{return JSON.parse(localStorage.getItem('omr_ebk')||'{}')}catch(e){return {}}}
function ebkSave(id,o){try{const a=ebkSt();a[id]=Object.assign(a[id]||{},o);localStorage.setItem('omr_ebk',JSON.stringify(a))}catch(e){}}
function ebkPenGet(id){try{return (JSON.parse(localStorage.getItem('omr_ebpen')||'{}')[id])||{}}catch(e){return {}}}
function ebkPenSave(){EBK.tex&&EBK.tex.clear();EBK.texOk&&EBK.texOk.clear();try{const a=JSON.parse(localStorage.getItem('omr_ebpen')||'{}');a[EBK.id]=EBK.pen;localStorage.setItem('omr_ebpen',JSON.stringify(a))}catch(e){toast('필기를 저장할 공간이 부족해요')}}
const EBI={pdf:'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12m0 0l-4-4m4 4l4-4"/><path d="M4 17v3h16v-3"/></svg>',
 print:'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M7 14h10v7H7z"/></svg>'};
EBI.mark='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1z"/></svg>';
EBI.thumb='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="8" rx="1.5"/><rect x="14" y="3" width="7" height="8" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>';
const ebT=tbT,ebS=tbS;
const EBC=['#e5484d','#2f7fd0','#1f9d55','#111111','#f7b928','#8e4ec6'];
async function bkEbook(id){
 id=bkPid(id);try{await bkLoadJs('lib/html2canvas.min.js',()=>window.html2canvas)}catch(e){}await bkInit();const P0=bkParts(id);if(P0&&P0.subj!==SUBJ)await setSubject(P0.subj);const plan=await bkPlan(id);if(!plan)return;
 const st=ebkSt()[id]||{};const N=plan.pages.length;
 Object.assign(EBK,{id,plan,N,marks:st.marks||[],p:Math.min(N,Math.max(1,st.last||1)),z:1,rev:[],pen:ebkPenGet(id),view:st.view||'auto',tool:'none',proj:0,wh:0,undo:[],tex:new Map(),txq:Promise.resolve(),busy:0,np:0,cs:null,G:null,noclick:0});
 let el=document.getElementById('ebk');if(el)el.remove();
 el=document.createElement('div');el.id='ebk';
 const J=[['표지',1]];if(plan.kind==='c')plan.toc.forEach(r=>J.push([r.sub.k+' '+r.sub.name,r.c]));else if(plan.kind==='t')plan.toc.forEach(r=>J.push([r.sub.k+' '+r.sub.name,r.p]));else if(plan.kind==='x')plan.toc.forEach(r=>r.items.forEach(([n,p])=>J.push([r.sub.k+' '+n,p])));if(plan.aStart)J.push(['정답 · 해설',plan.aStart]);
 const seen=new Set();EBK.J=J.filter(j=>j[1]&&!seen.has(j[1])&&seen.add(j[1]));
 el.innerHTML=`<style>#ebk{position:fixed;inset:0;z-index:50;background:#1b1f27;color:#e8ecf2;display:flex;flex-direction:column;font:14px Pretendard,PretendardLocal,sans-serif;user-select:none;-webkit-user-select:none}#ebk.wh{background:#f1f3f6}
#ebk .ebw{background:#12151b;flex:none}#ebk .eb,#ebk .et{display:flex;gap:6px;align-items:center;padding:6px 10px;flex-wrap:wrap}#ebk .et{padding-top:0}#ebk .eb>b{flex:1;min-width:60px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}#ebk .sp1{flex:1}
#ebk button,#ebk select{font:inherit;background:#2a303b;color:#e8ecf2;border:1px solid #3a4250;border-radius:8px;padding:6px 10px;cursor:pointer;max-width:44vw;display:inline-flex;align-items:center;gap:4px}#ebk button.on{background:#f7b928;color:#222;border-color:#f7b928}#ebk .eb button,#ebk .et button{flex:none;white-space:nowrap}#ebk button.ebi{padding:6px 11px;justify-content:center}#ebk button.ebi svg{width:18px!important;height:18px!important;flex:none;display:block}#ebk button.pr{background:#2f9d66;border-color:#2f9d66;color:#fff;font-weight:700}
#ebk{--t:#d6dce6;--m:#97a3b4;--sf2:#262c37;--l:#2e3541;--b:#2f9d66;--y:#f7b928}
${TBXCSS.replace(/§/g,'#ebk ')}
#ebk .cds{display:inline-flex;align-items:center;gap:9px;margin:0 6px;flex:none}
#ebk .eb,#ebk .et{gap:2px;padding:5px 10px}#ebk .et{padding-top:0}#ebk .eb>b{padding:0 6px;font-size:15px}
#ebk .thr .thi{display:block!important;padding:3px 0 2px!important;max-width:none!important;min-height:0!important;background:none!important;border:2px solid transparent!important;border-radius:8px;text-align:center}#ebk .thr .thi.on{border-color:#f7b928!important}#ebk .thr .thi small{display:block;margin-top:4px;font-size:11px;text-align:center}
#ebk .cd{width:26px!important;height:26px!important;min-width:26px!important;max-width:26px!important;min-height:26px!important;max-height:26px!important;aspect-ratio:1/1;padding:0!important;border-radius:50%!important;border:2px solid #fff3;flex:none;box-sizing:border-box;line-height:0;font-size:0;-webkit-appearance:none;appearance:none;display:block}#ebk .cd.on{border-color:#fff;box-shadow:0 0 0 2px #f7b928}
#ebk .sp.sc{flex-direction:column;justify-content:flex-start;align-items:center;gap:14px;padding:10px 8px 48px}#ebk .sp.sc.strip{gap:0;padding:0 0 48px}#ebk .sp.sc.strip .pgw{box-shadow:none}#ebk .pgw.ph{background:#fff}
#ebk.thon .stg{margin-left:140px}#ebk .thr{z-index:7;background:#1b1f27;border-color:#3a4250}#ebk .thr .thi{color:#aab4c2}#ebk .thr .thi.on{border-color:#f7b928;color:#f7b928}
#ebk .stg{flex:1;position:relative;overflow:auto;touch-action:pan-x pan-y;overscroll-behavior:contain}#ebk .sp{display:flex;align-items:center;justify-content:center;gap:2px;width:max-content;min-width:100%;min-height:100%;margin:0 auto;padding:6px}
#ebk .pgw{background:#fff;box-shadow:0 4px 22px rgba(0,0,0,.5);position:relative;flex:none}#ebk .pgw.e{background:none;box-shadow:none}#ebk .pgh{position:absolute;inset:0}#ebk canvas.pgc{position:absolute;inset:0;width:100%;height:100%;z-index:3;pointer-events:none}
#ebk.dr canvas.pgc{pointer-events:auto;touch-action:none}#ebk.dr.lz canvas.pgc{cursor:none}#ebk.dr.er canvas.pgc{cursor:cell}#ebk.dr canvas.pgc{cursor:crosshair}
#ebk .nv{position:fixed;top:50%;transform:translateY(-50%);width:50px;height:96px;z-index:9;background:#0009;border:0;color:#fff;font-size:34px;opacity:.7;transition:.2s;justify-content:center;padding:0;-webkit-tap-highlight-color:transparent}#ebk .nv:hover{opacity:1}#ebk.proj:not(.show) .nv{opacity:0}#ebk.thon .nv.l{left:140px}#ebk .nv.l{left:0;border-radius:0 12px 12px 0}#ebk .nv.r{right:0;border-radius:12px 0 0 12px}
#ebk .bt{display:flex;gap:10px;align-items:center;padding:8px 12px;background:#12151b;flex:none}#ebk input[type=range]{flex:1;accent-color:#f7b928}#ebk .ct{min-width:70px;text-align:center;font-variant-numeric:tabular-nums}
#ebk .eba{position:fixed;right:0;top:0;bottom:0;width:min(380px,92vw);background:#fff;color:#1b2430;z-index:8;box-shadow:-6px 0 24px #0005;display:flex;flex-direction:column;transform:translateX(105%);transition:transform .25s;user-select:text;-webkit-user-select:text}#ebk .eba.open{transform:none}
#ebk .eba .ah{display:flex;gap:8px;align-items:center;padding:10px 12px;border-bottom:1px solid #dde3ea}#ebk .eba .ah b{flex:1}#ebk .eba .ah button{background:#eef2f7;color:#1b2430;border-color:#d4dce6}#ebk .eba .al{flex:1;overflow:auto;padding:10px 12px}
#ebk .eba .ai{border:1px solid #dde3ea;border-radius:10px;padding:10px;margin-bottom:10px}#ebk .eba .ai h5{margin:0 0 6px;font-size:14px}#ebk .eba .ai .ans{font-size:18px;font-weight:800;color:#c0392b}
#ebk.proj .eba{width:min(520px,94vw);font-size:18px}
#ebk.proj .ebw,#ebk.proj .bt{position:absolute;left:0;right:0;z-index:7;opacity:0;pointer-events:none;transition:opacity .25s}#ebk.proj .ebw{top:0}#ebk.proj .bt{bottom:0}#ebk.proj.show .ebw,#ebk.proj.show .bt{opacity:1;pointer-events:auto}
#ebk .spp{position:relative;display:flex;flex:none}#ebk #ebcv{position:absolute;pointer-events:none;z-index:5;display:none}#ebk .stg{perspective:1800px}
#ebk .spp.fwd.two .pgw:last-child{transform-origin:left center;animation:ebTurnF .6s cubic-bezier(.22,.7,.2,1) both}#ebk .spp.back.two .pgw:first-child{transform-origin:right center;animation:ebTurnB .6s cubic-bezier(.22,.7,.2,1) both}
#ebk .spp.fwd.two .pgw:first-child,#ebk .spp.back.two .pgw:last-child{animation:ebFade .4s ease both}
#ebk .spp.fwd.one .pgw{animation:ebSlideF .4s cubic-bezier(.22,.7,.2,1) both}#ebk .spp.back.one .pgw{animation:ebSlideB .4s cubic-bezier(.22,.7,.2,1) both}
@keyframes ebTurnF{from{transform:rotateY(-78deg);opacity:.15;filter:brightness(.7)}to{transform:none;opacity:1;filter:none}}@keyframes ebTurnB{from{transform:rotateY(78deg);opacity:.15;filter:brightness(.7)}to{transform:none;opacity:1;filter:none}}
@keyframes ebSlideF{from{transform:translateX(60px);opacity:0}to{transform:none;opacity:1}}@keyframes ebSlideB{from{transform:translateX(-60px);opacity:0}to{transform:none;opacity:1}}
#ebk .ld{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);background:#000a;color:#fff;border-radius:10px;padding:8px 14px;z-index:9;display:none;font-size:13px}@keyframes ebFade{from{opacity:.2}to{opacity:1}}#ebk .spp.fd{animation:ebFade .3s ease both}
#ebk .laser{position:fixed;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:radial-gradient(circle,#ff2b2b 0 35%,#ff2b2b66 36% 70%,#0000 71%);pointer-events:none;z-index:9;display:none}
#ebk .eg{display:inline-flex;gap:6px;flex:none}
@media (max-width:1100px){#ebk .tbx{min-width:48px;padding:7px 5px 5px}#ebk .eb,#ebk .et{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;gap:6px;padding:6px 8px}#ebk .eb::-webkit-scrollbar,#ebk .et::-webkit-scrollbar{display:none}
 #ebk .eb>b{flex:1 0 80px;min-width:80px;max-width:34vw}#ebk .sp1{display:none}#ebk select{max-width:36vw;flex:none}#ebk button,#ebk select{min-height:36px}
 #ebk .eg{position:sticky;right:0;background:#12151b;padding-left:8px;box-shadow:-10px 0 10px -4px #12151b}#ebk .ebi span{display:none}#ebk .ebi{padding:6px 10px}#ebk .eb>button.pr,#ebk .eg .pr{padding:6px 12px}}
@media (max-width:600px){#ebk .et{padding-top:2px}}</style>
<div class="ebw"><div class="eb">${ebT('','bkEbookClose()','교재 닫기','close','닫기')}<b>${esc(plan.title)}</b><span class="sp1"></span>
${ebS('ebj','ebkGo(+this.value);this.value=\'\'','목차로 이동','toc','목차',`<option value="">목차…</option>${EBK.J.map(j=>`<option value="${j[1]}">${esc(j[0])} · p.${j[1]}</option>`).join('')}`)}
${ebT('ebs','ebkMark()','이 쪽 책갈피 (누르면 켜고 끔)','mark','책갈피','fillon')}${ebS('ebm','ebkGo(+this.value);this.value=\'\'','내 책갈피로 이동','marks','책갈피 목록','<option value="">책갈피…</option>')}<i class="tbv"></i>
${ebS('ebv','ebkSetView(this.value)','보기 방식','view','<span id="ebvl">자동</span>','<option value="auto">자동</option><option value="one">한 쪽</option><option value="two">펼침면</option><option value="scroll">스크롤</option><option value="strip">밀착 스크롤</option>')}${ebT('','ebkRail()','쪽 썸네일 보이기/숨기기','thumb','썸네일')}${ebT('','ebkList()','목록형 화면에서 풀기·채점','grade','목록·채점')}<i class="tbv"></i>
${ebT('','ebkZoom(-1)','축소 (−)','zout','축소')}<button class="tbx" id="ebz" onclick="ebkFit()" title="화면에 맞추기 (0)"><b class="pct" id="ebzp">100%</b><span class="lb">맞춤</span></button>${ebT('','ebkZoom(1)','확대 (+)','zin','확대')}<i class="tbv"></i>
${ebT('ebp','ebkProj()','수업용 전체 화면 (P)','proj','수업 모드')}
<span class="eg">${ebT('','bkPdf(EBK.id,1)','PDF 다운로드','pdf','PDF')}${ebT('','bkPrint(EBK.id,1)','인쇄','print','인쇄','pr')}</span></div>
<div class="et">${ebT('','ebkTool(\'none\')','이동·선택 (V)','move','이동','','data-t="none"')}${ebT('','ebkTool(\'pen\')','펜 (D)','pen','펜','','data-t="pen"')}${ebT('','ebkTool(\'hl\')','형광펜 (H)','hl','형광펜','','data-t="hl"')}${ebT('','ebkTool(\'er\')','지우개 (E)','er','지우개','','data-t="er"')}${ebT('','ebkTool(\'lz\')','레이저 포인터 (L)','lz','레이저','','data-t="lz"')}<i class="tbv"></i>
<span class="cds">${EBC.map(c=>`<button class="cd" data-c="${c}" style="background:${c}" onclick="ebkColor('${c}')" aria-label="색"></button>`).join('')}</span>
${ebS('ebw','EBK.w=+this.value','선 굵기','wid','굵기','<option value="2">가늘게</option><option value="3" selected>보통</option><option value="6">굵게</option><option value="10">매우 굵게</option>')}<i class="tbv"></i>
${ebT('','ebkUndo()','되돌리기 (Ctrl+Z)','undo','되돌리기')}${ebT('','ebkClear()','이 화면 필기 모두 지우기','trash','필기 지우기')}${ebT('ebf','ebkFinger()','손가락으로도 필기','finger','손가락 필기')}<i class="tbv"></i>
${ebT('ebb','ebkBg()','배경 밝기','sun','배경')}${ebT('ebx','ebkFx()','쪽 넘김 효과 켜기/끄기','fx','넘김 효과')}${ebT('eba','ebkPanel()','번호를 누르면 정답·해설이 나와요','bulb','정답·해설')}</div></div>
<div class="stg" id="ebst"><div class="sp" id="ebsp"></div><canvas id="ebcv"></canvas></div><div class="ld" id="ebld">책장을 준비하는 중…</div>
<button class="nv l" onclick="ebkStep(-1)" aria-label="이전">‹</button><button class="nv r" onclick="ebkStep(1)" aria-label="다음">›</button>
<div class="bt"><button onclick="ebkStep(-1)">‹</button><input type="range" id="ebr" min="1" max="${N}" value="${EBK.p}" oninput="ebkGo(+this.value,1)"><span class="ct" id="ebc"></span><button onclick="ebkStep(1)">›</button></div>
<aside class="eba" id="ebans"><div class="ah"><b>정답 · 해설</b><button onclick="ebkRevClear()">모두 지우기</button><button onclick="ebkPanel(0)">닫기</button></div><div class="al" id="ebal"></div></aside><div class="laser" id="ebls"></div>`;
 document.body.appendChild(el);document.body.style.overflow='hidden';
 {const rl=thumbRail({parent:el,n:N,label:i=>String(i+1),render:(t,i)=>{t.style.setProperty('--bks','1');bkShadow(t,'<div class="bkdoc scr">'+bkPageHtml(plan,i)+'</div>')},go:i=>ebkGo(i+1)});EBK.rail=rl;
  const fit=()=>{const w=el.querySelector('.ebw');rl.setTop((w?w.getBoundingClientRect().bottom:90)+8);el.classList.toggle('thon',!rl.classList.contains('off')&&innerWidth>=900)};fit();EBK.railFit=fit;thumbAct(rl,EBK.p-1);setTimeout(()=>{try{ebkScale();ebkDraw(1)}catch(e){}},0)}
 EBK.kd=e=>{if(!document.getElementById('ebk')||/INPUT|TEXTAREA|SELECT/.test((e.target||{}).tagName||''))return;const k=e.key;
  if(k==='ArrowRight'||k==='PageDown'||k===' ')ebkStep(1);else if(k==='ArrowLeft'||k==='PageUp')ebkStep(-1);else if(k==='Escape'){if(EBK.proj)ebkProj(0);else bkEbookClose()}
  else if(k==='+'||k==='=')ebkZoom(1);else if(k==='-')ebkZoom(-1);else if(k==='0')ebkFit();else if(k==='p'||k==='P')ebkProj();else if(k==='d'||k==='D')ebkTool('pen');else if(k==='h'||k==='H')ebkTool('hl');else if(k==='e'||k==='E')ebkTool('er');else if(k==='l'||k==='L')ebkTool('lz');else if(k==='v'||k==='V')ebkTool('none');
  else if((e.ctrlKey||e.metaKey)&&(k==='z'||k==='Z'))ebkUndo();else return;e.preventDefault()};
 addEventListener('keydown',EBK.kd);
 EBK.rs=()=>ebkScale();addEventListener('resize',EBK.rs);
 EBK.fs=()=>{if(!document.fullscreenElement&&EBK.proj)ebkProj(0)};document.addEventListener('fullscreenchange',EBK.fs);
 const s=document.getElementById('ebst');let x0=null,y0=null,pd=0,pz=1,pc=null;
 s.addEventListener('touchstart',e=>{if(e.touches.length===1){x0=e.touches[0].clientX;y0=e.touches[0].clientY}else{x0=null}if(e.touches.length===2){const a=e.touches[0],b=e.touches[1];pd=Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY);pz=EBK.z;pc=[(a.clientX+b.clientX)/2,(a.clientY+b.clientY)/2]}},{passive:true});
 s.addEventListener('touchmove',e=>{if(e.touches.length===2&&pd){const a=e.touches[0],b=e.touches[1];const d=Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY);EBK.z=Math.max(.5,Math.min(4,pz*d/pd));ebkScale();e.preventDefault()}},{passive:false});
 s.addEventListener('touchend',()=>{pd=0},{passive:true});
 s.addEventListener('wheel',e=>{if(e.ctrlKey||e.metaKey){e.preventDefault();ebkZoom(e.deltaY<0?1:-1,1)}},{passive:false});
 let pan=null;s.addEventListener('pointerdown',e=>{if(EBK.tool==='none'&&e.pointerType==='mouse'&&EBK.z>1&&!(e.target.closest&&e.target.closest('button'))){pan={x:e.clientX,y:e.clientY,l:s.scrollLeft,t:s.scrollTop};s.setPointerCapture(e.pointerId)}});
 s.addEventListener('pointermove',e=>{if(pan){s.scrollLeft=pan.l-(e.clientX-pan.x);s.scrollTop=pan.t-(e.clientY-pan.y)}});s.addEventListener('pointerup',()=>{pan=null});
 ebkScrubBind(s);el.addEventListener('mousemove',ebkPing);el.addEventListener('touchstart',ebkPing,{passive:true});
 document.getElementById('ebk')&&typeof pushNav==='function'&&(EBK.hist=1,pushNav());ebkTool('none');ebkColor(EBK.color,1);{const x=document.getElementById('ebx');if(x)x.classList.toggle('on',EBKFX)}ebkGlInit();ebkDraw();ebkPing()}
function bkEbookClose(){const hist=EBK.hist;EBK.hist=0;const tx=document.getElementById('ebtx');if(tx)tx.remove();const ts=document.getElementById('ebtxs');if(ts)ts.remove();EBK.G=null;if(document.fullscreenElement)try{document.exitFullscreen()}catch(e){}const el=document.getElementById('ebk');if(el)el.remove();document.body.style.overflow='';removeEventListener('keydown',EBK.kd);removeEventListener('resize',EBK.rs);document.removeEventListener('fullscreenchange',EBK.fs);if(hist&&history.state&&String(history.state.k||'').split('|')[4]==='1'){try{history.back()}catch(e){}}else if(typeof urlSync==='function')urlSync(0)}
function ebkPing(){const el=document.getElementById('ebk');if(!el)return;el.classList.add('show');clearTimeout(EBK.pt);if(EBK.proj&&!EBK.drawing)EBK.pt=setTimeout(()=>{const e=document.getElementById('ebk');if(e&&!e.matches(':hover')||EBK.proj)e&&e.classList.remove('show')},2800)}
function ebkGradePage(n){const id=EBK.id,plan=EBK.plan;EBK.hist=0;bkEbookClose();if(plan.kind==='m')bkGradeAll(id);else bkGradePage(id,n)}
function ebkList(){EBK.hist=0;const id=EBK.id,p=EBK.p;bkEbookClose();BKV={v:'read',id};tab='books';render();setTimeout(()=>bkJump(p),600)}
function ebkProj(on){const el=document.getElementById('ebk');if(!el)return;on=on===undefined?!EBK.proj:!!on;EBK.proj=on?1:0;el.classList.toggle('proj',!!on);document.getElementById('ebp').classList.toggle('on',!!on);
 if(on){try{el.requestFullscreen&&el.requestFullscreen()}catch(e){}toast('수업 모드 · 화면을 움직이면 메뉴가 나타나요 (Esc로 종료)')}else if(document.fullscreenElement){try{document.exitFullscreen()}catch(e){}}
 ebkPing();setTimeout(ebkScale,150)}
function ebkVL(){const l=document.getElementById('ebvl');if(l)l.textContent={auto:'자동',one:'한 쪽',two:'펼침면',scroll:'스크롤',strip:'밀착 스크롤'}[EBK.view]||'자동'}
function ebkScroll(){return EBK.view==='scroll'||EBK.view==='strip'}
function ebkSpread(){if(ebkScroll())return false;const st=document.getElementById('ebst');const w=st.clientWidth,h=st.clientHeight;return EBK.view==='two'||(EBK.view==='auto'&&w>=h*1.25&&w>=900)}
function ebkSetView(v){if(!['auto','one','two','scroll','strip'].includes(v))v='auto';EBK.view=v;ebkSave(EBK.id,{view:v});EBK.z=1;const s=document.getElementById('ebst');if(s){s.scrollLeft=0;s.scrollTop=0}ebkDraw(0,1);if(ebkScroll())toast(v==='strip'?'밀착 스크롤: 쪽을 이어 붙여 위아래로 넘겨요':'스크롤: 위아래로 밀어서 넘겨요')}
function ebkFx(){EBKFX=!EBKFX;try{localStorage.setItem('omr_ebfx',EBKFX?'1':'0')}catch(e){}const x=document.getElementById('ebx');if(x)x.classList.toggle('on',EBKFX);toast(EBKFX?'쪽 넘김 효과를 켰어요':'쪽 넘김 효과를 껐어요')}
function ebkStep(d){if(ebkScroll()){ebkGo(EBK.p+(d>0?1:-1));return}if(EBK.busy)return;if(EBK.z>1.02||!EBKFX){const s=ebkSpec(d>0?1:-1);if(!s)return;EBK.p=s.np;EBK.rev=[];ebkDraw(0,0,EBKFX?(d>0?1:-1):0);return}ebkFlip(d>0?1:-1)}
function ebkStepDirect(d){const s=ebkSpec(d>0?1:-1);if(!s)return;EBK.p=s.np;EBK.rev=[];ebkDraw(0,0,d>0?1:-1)}
function ebkGo(p,noanim){if(!p||EBK.busy)return;p=Math.max(1,Math.min(EBK.N,p));if(ebkScroll()){EBK.p=p;ebkScrollTo(p,noanim);ebkUiSyncLite();return}const two=ebkSpread();const sp=q=>two?(q%2===0?q:q-1):q;const cur=sp(EBK.p),nw=sp(p);
 if(!noanim&&EBKFX&&EBK.z<=1.02&&Math.abs(nw-cur)===(two?2:1)&&nw!==cur){const dir=nw>cur?1:-1;const s=ebkSpec(dir);if(s&&s.np===(two?(nw<1?1:nw):nw)){ebkFlip(dir);return}}
 EBK.p=p;EBK.rev=[];ebkDraw(0,1)}
function ebkMark(){const i=EBK.marks.indexOf(EBK.p);if(i>=0)EBK.marks.splice(i,1);else EBK.marks.push(EBK.p);EBK.marks.sort((a,b)=>a-b);ebkSave(EBK.id,{marks:EBK.marks});ebkDraw(1)}
function ebkZoom(d,wheel){EBK.z=Math.max(.5,Math.min(4,+(EBK.z*(d>0?1.2:1/1.2)).toFixed(3)));ebkScale()}
function ebkFit(){EBK.z=1;ebkScale();const s=document.getElementById('ebst');if(s){s.scrollLeft=0;if(ebkScroll())ebkScrollTo(EBK.p,1);else s.scrollTop=0}}
function ebkBase(){const st=document.getElementById('ebst'),cnt=ebkSpread()?2:1;const pw=210*BK_MM,ph=297*BK_MM;if(ebkScroll())return {pw,ph,s:(st.clientWidth-(EBK.view==='strip'?0:16))/pw};return {pw,ph,s:Math.min((st.clientWidth-16)/cnt/pw,(st.clientHeight-16)/ph)}}
function ebkScale(){const sp=document.getElementById('ebsp');if(!sp)return;const {pw,ph,s}=ebkBase();const k=s*EBK.z;EBK.pgw=pw*k;const keepP=ebkScroll()&&EBK.sm?EBK.p:0;
 sp.querySelectorAll('.pgw').forEach(e=>{e.style.width=pw*k+'px';e.style.height=ph*k+'px';const h=e.querySelector('.pgh');const d=h&&h.shadowRoot&&h.shadowRoot.querySelector('.bkdoc');if(d)d.style.setProperty('--bks',k.toFixed(4));const c=e.querySelector('canvas.pgc');if(c)ebkCanvas(c)});
 const z=document.getElementById('ebzp');if(z)z.textContent=Math.round(EBK.z*100)+'%';if(keepP)ebkScrollTo(keepP,1)}
function ebkCanvas(c){const r=c.getBoundingClientRect(),d=Math.min(2,devicePixelRatio||1);c.width=Math.max(1,Math.round(r.width*d));c.height=Math.max(1,Math.round(r.height*d));ebkRedraw(c)}
function ebkRedraw(c,dot){const n=+c.parentNode.dataset.n,g=c.getContext('2d'),W=c.width,H=c.height;g.clearRect(0,0,W,H);g.lineCap='round';g.lineJoin='round';
 ((EBK.pen||{})[n]||[]).forEach(s=>ebkStroke(g,s,W,H));if(dot&&dot.p&&dot.p.length)ebkStroke(g,dot,W,H)}
function ebkStroke(g,s,W,H){const p=s.p;if(!p.length)return;g.beginPath();g.strokeStyle=s.t==='hl'?s.c+'59':s.c;g.lineWidth=(s.t==='hl'?s.w*3.2:s.w)*W/800;g.globalAlpha=1;g.moveTo(p[0][0]*W,p[0][1]*H);if(p.length===1)g.lineTo(p[0][0]*W+.1,p[0][1]*H);for(let i=1;i<p.length;i++)g.lineTo(p[i][0]*W,p[i][1]*H);g.stroke()}
function ebkTool(t){EBK.tool=t;const el=document.getElementById('ebk');if(!el)return;el.classList.toggle('dr',t!=='none');el.classList.toggle('lz',t==='lz');el.classList.toggle('er',t==='er');
 el.querySelectorAll('.et button[data-t]').forEach(b=>b.classList.toggle('on',b.dataset.t===t));const l=document.getElementById('ebls');if(l&&t!=='lz')l.style.display='none'}
function ebkColor(c,init){EBK.color=c;document.querySelectorAll('#ebk .cd').forEach(b=>b.classList.toggle('on',b.dataset.c===c));if(!init&&(EBK.tool==='none'||EBK.tool==='er'||EBK.tool==='lz'))ebkTool('pen')}
function ebkFinger(){EBK.finger=EBK.finger?0:1;document.getElementById('ebf').classList.toggle('on',!!EBK.finger);toast(EBK.finger?'손가락으로도 필기해요(스크롤은 두 손가락)':'펜슬·마우스로만 필기해요. 손가락은 화면 이동에 써요')}
function ebkBg(){EBK.wh=EBK.wh?0:1;document.getElementById('ebk').classList.toggle('wh',!!EBK.wh)}
function ebkUndo(){const u=EBK.undo.pop();if(!u)return;const a=(EBK.pen[u.n]||[]);if(u.k==='add')a.pop();else if(u.k==='del'){EBK.pen[u.n]=u.prev}ebkPenSave();document.querySelectorAll('#ebsp canvas.pgc').forEach(c=>ebkRedraw(c))}
function ebkClear(){const vr=document.getElementById('ebst').getBoundingClientRect();const ps=[...document.querySelectorAll('#ebsp .pgw[data-n]')].filter(e=>{if(!ebkScroll())return true;const r=e.getBoundingClientRect();return r.bottom>vr.top&&r.top<vr.bottom}).map(e=>+e.dataset.n).filter(n=>(EBK.pen[n]||[]).length);if(!ps.length){toast('지울 필기가 없어요');return}if(!confirm('이 화면의 필기를 모두 지울까요?'))return;ps.forEach(n=>{EBK.undo.push({k:'del',n,prev:EBK.pen[n]});EBK.pen[n]=[]});ebkPenSave();document.querySelectorAll('#ebsp canvas.pgc').forEach(c=>ebkRedraw(c))}
function ebkBindDraw(c){let cur=null,last=null;const pt=e=>{const r=c.getBoundingClientRect();return [Math.min(1,Math.max(0,(e.clientX-r.left)/r.width)),Math.min(1,Math.max(0,(e.clientY-r.top)/r.height))]};
 const n=+c.parentNode.dataset.n;const ok=e=>e.pointerType!=='touch'||EBK.finger;
 c.addEventListener('pointerdown',e=>{if(!ok(e)||EBK.tool==='none')return;e.preventDefault();c.setPointerCapture(e.pointerId);EBK.drawing=1;const p=pt(e);
  if(EBK.tool==='pen'||EBK.tool==='hl'){cur={t:EBK.tool,c:EBK.color,w:EBK.w,p:[p]};ebkRedraw(c,cur)}
  else if(EBK.tool==='er'){EBK.erPrev=(EBK.pen[n]||[]).slice();EBK.erHit=0;ebkErase(c,n,p)}
  else if(EBK.tool==='lz')ebkLaser(e)});
 c.addEventListener('pointermove',e=>{if(EBK.tool==='lz'){ebkLaser(e);return}if(!EBK.drawing)return;const p=pt(e);if(EBK.tool==='er'){ebkErase(c,n,p);return}if(!cur)return;
  const evs=e.getCoalescedEvents?e.getCoalescedEvents():[e];evs.forEach(x=>cur.p.push(pt(x)));ebkRedraw(c,cur)});
 const end=e=>{if(EBK.tool==='lz'){const l=document.getElementById('ebls');if(l&&e.pointerType!=='mouse')l.style.display='none';EBK.drawing=0;return}
  if(!EBK.drawing)return;EBK.drawing=0;
  if(cur&&cur.p.length){(EBK.pen[n]=EBK.pen[n]||[]).push(cur);EBK.undo.push({k:'add',n});if(EBK.undo.length>100)EBK.undo.shift();ebkPenSave()}
  else if(EBK.tool==='er'&&EBK.erHit){EBK.undo.push({k:'del',n,prev:EBK.erPrev});ebkPenSave()}
  cur=null;ebkRedraw(c)};
 c.addEventListener('pointerup',end);c.addEventListener('pointercancel',end);
 c.addEventListener('pointerleave',()=>{if(EBK.tool==='lz'){const l=document.getElementById('ebls');if(l)l.style.display='none'}})}
function ebkErase(c,n,p){const a=EBK.pen[n]||[];const r=c.getBoundingClientRect();const rad=Math.max(.012,12/r.width);
 const keep=a.filter(s=>!s.p.some(q=>Math.hypot((q[0]-p[0])*r.width,(q[1]-p[1])*r.height)<rad*r.width));if(keep.length!==a.length){EBK.pen[n]=keep;EBK.erHit=1;ebkRedraw(c)}}
function ebkLaser(e){const l=document.getElementById('ebls');if(!l)return;l.style.display='block';l.style.left=e.clientX+'px';l.style.top=e.clientY+'px'}
/* --- 정답·해설 패널: 문제 번호를 누르면 열고 닫음 --- */
function ebkPanel(on){const a=document.getElementById('ebans');if(!a)return;const o=on===undefined?!a.classList.contains('open'):!!on;a.classList.toggle('open',o);document.getElementById('eba').classList.toggle('on',o)}
async function ebkReveal(code){const i=EBK.rev.indexOf(code);if(i>=0)EBK.rev.splice(i,1);else EBK.rev.push(code);await ensureCodes([code]);ebkMarkNums();ebkRevDraw();if(EBK.rev.length)ebkPanel(1)}
function ebkRevClear(){EBK.rev=[];ebkMarkNums();ebkRevDraw()}
function ebkMarkNums(){document.querySelectorAll('#ebsp .pgh').forEach(h=>{const r=h.shadowRoot;if(!r)return;r.querySelectorAll('.u.q[data-c]').forEach(u=>{const q=u.querySelector('.no,.qn');if(q)q.classList.toggle('ebon',EBK.rev.includes(u.dataset.c))})})}
function ebkRevDraw(){const el=document.getElementById('ebal');if(!el)return;if(!EBK.rev.length){el.innerHTML='<div style="color:#667;font-size:13px;line-height:1.6">문제 <b>번호</b>를 누르면 정답과 해설이 여기에 나와요.<br>다시 누르면 닫혀요.</div>';return}
 el.innerHTML=EBK.rev.map((c,i)=>`<div class="ai" id="ebai${i}"><h5>${esc(c)}${(byCode[c]||{}).type?' · '+esc(byCode[c].type):''}</h5><div class="ans">정답 ${esc(['mc','top','bank'].includes((byCode[c]||{}).set)||/^[1-5](,[1-5])*$/.test(String((byCode[c]||{}).ans))?bkCir((byCode[c]||{}).ans):String((byCode[c]||{}).ans||'-'))}</div><div class="ex"></div></div>`).join('');
 EBK.rev.forEach((c,i)=>{const q=byCode[c];const h=document.querySelector('#ebai'+i+' .ex');if(h&&q&&q.exp)mount(h,q.exp)})}
function ebkRail(){if(!EBK.rail)return;thumbTog('#ebk>.thr');EBK.railFit();try{ebkScale();ebkDraw(1)}catch(e){}}
function ebkDraw(keep,fade,dir){const sp=document.getElementById('ebsp');if(!sp)return;if(EBK.rail)thumbAct(EBK.rail,EBK.p-1);
 if(ebkScroll()){if(keep&&sp.querySelector('.pgw[data-n]')){ebkUiSyncLite();return}ebkDrawScroll();return}EBK.sm=0;if(EBK.io){EBK.io.disconnect();EBK.io=null}const two=ebkSpread();const {N}=EBK;let p=EBK.p;
 let ps;if(two){const lo=p%2===0?p:p-1;ps=[lo,lo+1];if(lo<1)ps=[0,1]}else ps=[p];
 sp.className='sp';sp.innerHTML='<div class="spp'+(fade?' fd':'')+(dir>0?' fwd':dir<0?' back':'')+(two?' two':' one')+'"></div>';const spp=sp.firstChild;ps.forEach(n=>spp.appendChild(ebkMakePage(n)));
 ebkScale();ebkMarkNums();
 ebkUiSync()}
function ebkUiSync(){const N=EBK.N;const shown=ebkScroll()?[EBK.p||1]:[...document.querySelectorAll('#ebsp .pgw[data-n]')].map(e=>+e.dataset.n);if(!shown.length)shown.push(EBK.p||1);
 EBK.p=Math.min(...shown);const cur=EBK.p;ebkSave(EBK.id,{last:cur});if(typeof urlSync==='function')urlSync();
 const r=document.getElementById('ebr');if(r)r.value=cur;const ct=document.getElementById('ebc');if(ct)ct.textContent=shown.join('-')+' / '+N;
 const mk=shown.some(n=>EBK.marks.includes(n));const bs=document.getElementById('ebs');if(bs)bs.classList.toggle('on',mk);
 const bm=document.getElementById('ebm');if(bm)bm.innerHTML='<option value="">북마크…</option>'+EBK.marks.map(n=>`<option value="${n}">p.${n}</option>`).join('');
 const bv=document.getElementById('ebv');if(bv)bv.value=EBK.view;ebkVL();ebkRevDraw();ebkWarm()}

/* ---------- 말아 올리는(페이지 컬) 효과: 페이지를 그림으로 만들어 WebGL로 원통처럼 말아 넘김 ---------- */
const EBVS='attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;gl_Position=vec4(p,0.,1.);}';
const EBFS=`precision highp float;varying vec2 v;uniform sampler2D F;uniform sampler2D K;uniform float a;uniform float R;uniform float lo;uniform float mirror;uniform float mode;uniform float hasK;
const float PI=3.14159265;
vec4 front(float xo,float y){float u=(xo-lo)/(1.0-lo);if(mirror>.5)u=1.0-u;return texture2D(F,vec2(u,y));}
vec4 back(float xo,float y){float s=(xo-lo)/(1.0-lo);vec4 c;
 if(mode<.5&&hasK>.5){float u=1.0-s;if(mirror>.5)u=1.0-u;c=texture2D(K,vec2(u,y));}
 else{float u=s;if(mirror>.5)u=1.0-u;c=mix(vec4(.97,.96,.94,1.),texture2D(F,vec2(u,y)),.22);}
 return c;}
void main(){float x=mirror>.5?1.0-v.x:v.x;float y=v.y;vec4 col=vec4(0.0);
 float Lb=(1.0-a)-PI*R;
 if(x>a+R){float d=(x-(a+R))/0.09;float sh=a<.999?.34*pow(1.0-clamp(d,0.,1.),1.6):0.;col=vec4(0.,0.,0.,sh);}
 else if(x>=a){float d=x-a;float th=asin(clamp(d/R,-1.,1.));float xo2=a+(PI-th)*R;
  if(xo2<=1.0&&xo2>=lo){col=back(xo2,y);col.rgb*=0.86+0.12*cos(th*.7);col.rgb+=vec3(.10)*pow(clamp(d/R,0.,1.),5.0);}
  else{float xo1=a+th*R;if(xo1>=lo&&xo1<=1.0){col=front(xo1,y);col.rgb*=0.66+0.34*cos(th);}else col=vec4(0.);}}
 else{float dd=a-x;float xo=a+PI*R+dd;
  if(xo<=1.0&&xo>=lo){col=back(xo,y);col.rgb*=0.93;float e=1.0-clamp(dd/0.02,0.,1.);col.rgb*=1.0-0.10*e;}
  else if(x>=lo){col=front(x,y);float e=clamp((a-x)/0.12,0.,1.);col.rgb*=0.92+0.08*e;}
  else col=vec4(0.);}
 col.rgb*=col.a;gl_FragColor=col;}`;
function ebkGlInit(){if(EBK.G)return EBK.G;const cv=document.getElementById('ebcv');if(!cv)return null;let gl=null;try{gl=cv.getContext('webgl',{premultipliedAlpha:true,alpha:true,antialias:true})}catch(e){}if(!gl)return null;
 const sh=(t,s)=>{const o=gl.createShader(t);gl.shaderSource(o,s);gl.compileShader(o);if(!gl.getShaderParameter(o,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(o));return o};
 try{const pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,EBVS));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,EBFS));gl.linkProgram(pr);if(!gl.getProgramParameter(pr,gl.LINK_STATUS))throw new Error('link');
  gl.useProgram(pr);const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);const l=gl.getAttribLocation(pr,'p');gl.enableVertexAttribArray(l);gl.vertexAttribPointer(l,2,gl.FLOAT,false,0,0);
  const U={};['F','K','a','R','lo','mirror','mode','hasK'].forEach(n=>U[n]=gl.getUniformLocation(pr,n));
  const mk=()=>{const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);return t};
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
  EBK.G={gl,pr,U,tF:mk(),tK:mk()};return EBK.G}catch(e){console.warn('curl init',e);return null}}

/* WebGL을 못 쓰는 기기용: 같은 원통 말림을 2D 캔버스로 세로 띠(strip)를 그려 구현 */
function ebkMirrorCv(src){const c=document.createElement('canvas');c.width=src.width;c.height=src.height;const g=c.getContext('2d');g.translate(c.width,0);g.scale(-1,1);g.drawImage(src,0,0);return c}
function ebkCurlDraw2D(t,raw){const r=EBK.r2,s=EBK.cs;if(!r||!s)return;const cv=r.cv,g=r.g,W=cv.width,H=cv.height;
 const e=raw?t:(t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2);let a,R;if(s.book){a=1-.5*e;R=.075*Math.pow(Math.sin(Math.PI*e),.75)+.004}else{R=.07;a=1-1.14*e}
 const lo=s.book?.5:0,L=1-lo,mir=s.dir<0,PI=Math.PI;g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,W,H);if(mir){g.translate(W,0);g.scale(-1,1)}
 const F=mir?r.Fm:r.F,K=mir?r.Km:r.K,PAPER='rgba(247,245,240,.78)';
 const strip=(img,u0,u1,x0,x1,flip)=>{if(x1-x0<.5||!img)return;const iw=img.width,ih=img.height;const sx=Math.max(0,Math.min(iw-1,u0*iw)),sw=Math.max(1,Math.min(iw-sx,(u1-u0)*iw));
  if(flip){g.save();g.translate(x0+x1,0);g.scale(-1,1);g.drawImage(img,sx,0,sw,ih,x0,0,x1-x0,H);g.restore()}else g.drawImage(img,sx,0,sw,ih,x0,0,x1-x0,H)};
 // 1) 아직 안 말린 앞면
 const fe=Math.min(a,1);if(fe>lo)strip(F,0,(fe-lo)/L,lo*W,fe*W);
 // 2) 말려 올라가 뒤로 누운 뒷면
 const Lb=(1-a)-PI*R;if(Lb>0){const xs=Math.max(a-Lb,0),xoS=a+PI*R+(a-xs),xoA=a+PI*R;
  if(s.book){strip(K,1-(xoS-lo)/L,1-(xoA-lo)/L,xs*W,a*W)}else{strip(F,(xoA-lo)/L,(xoS-lo)/L,xs*W,a*W,true);g.fillStyle=PAPER;g.fillRect(xs*W,0,(a-xs)*W,H)}
  g.fillStyle='rgba(0,0,0,.07)';g.fillRect(xs*W,0,(a-xs)*W,H)}
 // 3) 원통 부분
 const c0=Math.max(0,Math.floor(a*W)),c1=Math.min(W,Math.ceil((a+R)*W));
 for(let c=c0;c<c1;c++){const x=(c+.5)/W,d=x-a;if(d<0||d>R)continue;const th=Math.asin(Math.min(1,d/R)),xo2=a+(PI-th)*R;
  const iw=(F||K).width,sww=Math.max(1,iw/W*1.3);
  if(xo2<=1&&xo2>=lo){const u=s.book?1-(xo2-lo)/L:(xo2-lo)/L,img=s.book?K:F;g.drawImage(img,Math.max(0,Math.min(img.width-sww,u*img.width-sww/2)),0,sww,img.height,c,0,1.3,H);
   if(!s.book){g.fillStyle=PAPER;g.fillRect(c,0,1.3,H)}g.fillStyle='rgba(0,0,0,'+(1-(.86+.12*Math.cos(th*.7)))+')';g.fillRect(c,0,1.3,H);const hl=.10*Math.pow(Math.min(1,d/R),5);if(hl>.004){g.fillStyle='rgba(255,255,255,'+hl+')';g.fillRect(c,0,1.3,H)}}
  else{const xo1=a+th*R;if(xo1<lo||xo1>1)continue;const u=(xo1-lo)/L;g.drawImage(F,Math.max(0,Math.min(F.width-sww,u*F.width-sww/2)),0,sww,F.height,c,0,1.3,H);g.fillStyle='rgba(0,0,0,'+(1-(.66+.34*Math.cos(th)))+')';g.fillRect(c,0,1.3,H)}}
 // 4) 말려 올라간 쪽 아래로 드리운 그림자
 if(a<.999){const x0=(a+R)*W,x1=Math.min(W,x0+.09*W);if(x1>x0){const gr=g.createLinearGradient(x0,0,x1,0);gr.addColorStop(0,'rgba(0,0,0,.34)');gr.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gr;g.fillRect(x0,0,x1-x0,H)}}}
function ebkGlPlace(){const cv=document.getElementById('ebcv'),spp=document.querySelector('#ebsp .spp'),st=document.getElementById('ebst');if(!cv||!spp)return false;
 const r=spp.getBoundingClientRect(),s=st.getBoundingClientRect(),d=Math.min(2,devicePixelRatio||1);cv.style.left=(r.left-s.left+st.scrollLeft)+'px';cv.style.top=(r.top-s.top+st.scrollTop)+'px';cv.style.width=r.width+'px';cv.style.height=r.height+'px';
 const w=Math.min(2800,Math.round(r.width*d)),h=Math.min(2800,Math.round(r.height*d));if(cv.width!==w||cv.height!==h){cv.width=w;cv.height=h}return true}
function ebkTexHost(){let s=document.getElementById('ebtxs');if(!s){s=document.createElement('style');s.id='ebtxs';document.head.appendChild(s)}s.textContent=BKCSS+'.bkdoc .bp{margin:0!important;box-shadow:none!important}'+bkFontCssRule();
 let h=document.getElementById('ebtx');if(!h){h=document.createElement('div');h.id='ebtx';h.className='bkdoc';h.style.cssText='position:fixed;left:-20000px;top:0;width:210mm;z-index:-1;background:#fff';document.body.appendChild(h)}return h}
function ebkTexKey(n){const sc=Math.max(.9,Math.min(2,(EBK.pgw||800)*Math.min(2,devicePixelRatio||1)/(210*BK_MM)));return {sc,key:n+'|'+sc.toFixed(1)}}
function ebkTexReady(n){return !!(EBK.texOk&&EBK.texOk.has(ebkTexKey(n).key))}
function ebkTex(n){const {sc,key}=ebkTexKey(n);if(!EBK.tex)EBK.tex=new Map();if(!EBK.texOk)EBK.texOk=new Set();if(EBK.tex.has(key))return EBK.tex.get(key);
 const run=async()=>{const host=ebkTexHost();host.innerHTML=bkPageHtml(EBK.plan,n-1);await Promise.all([...host.querySelectorAll('img')].map(im=>im.complete&&im.naturalWidth?1:new Promise(r=>{im.onload=im.onerror=()=>r();setTimeout(r,6000)})));try{await document.fonts.ready}catch(e){}
  const cv=await window.html2canvas(host.firstElementChild,{scale:sc,backgroundColor:'#ffffff',useCORS:true,logging:false});const g=cv.getContext('2d');g.lineCap='round';g.lineJoin='round';(EBK.pen[n]||[]).forEach(s=>ebkStroke(g,s,cv.width,cv.height));host.innerHTML='';EBK.texOk.add(key);return cv};
 EBK.txq=(EBK.txq||Promise.resolve()).then(run,run);const p=EBK.txq;EBK.tex.set(key,p);if(EBK.tex.size>14){const k=EBK.tex.keys().next().value;EBK.tex.delete(k)}p.catch(()=>EBK.tex.delete(key));return p}
function ebkWarm(){clearTimeout(EBK.wt);EBK.wt=setTimeout(()=>{if(!document.getElementById('ebk')||!window.html2canvas)return;if(EBK.busy){ebkWarm();return}const run=()=>{if(EBK.busy||ebkScroll())return;const two=ebkSpread(),p=EBK.p,N=EBK.N,w=[];
 if(two){const lo=p%2===0?p:p-1;w.push(lo+1,lo+2,lo,lo-1)}else w.push(p,p+1,p-1);w.filter(n=>n>=1&&n<=N).forEach(n=>ebkTex(n).catch(()=>{}))};if(window.requestIdleCallback)requestIdleCallback(run,{timeout:3000});else run()},900)}
function ebkSpec(dir){const N=EBK.N,p=EBK.p;
 if(ebkSpread()){const lo=p%2===0?p:p-1;
  if(dir>0){const nl=lo+2;if(nl>N||lo+1>N)return null;return {dir,book:1,f:lo+1,k:nl,el:1,newN:nl+1<=N?nl+1:0,np:nl}}
  if(lo<=0)return null;const pl=lo-2;return {dir,book:1,f:lo,k:lo-1,el:0,newN:pl>=1?pl:0,np:pl<1?1:pl}}
 if(dir>0){if(p+1>N)return null;return {dir,book:0,f:p,k:0,el:0,newN:p+1,np:p+1}}
 if(p-1<1)return null;return {dir,book:0,f:p,k:0,el:0,newN:p-1,np:p-1}}
function ebkShadow(host,html){const r=host.shadowRoot||host.attachShadow({mode:'open'});
 if(window.CSSStyleSheet&&r.adoptedStyleSheets!==undefined){if(EBK.sheet===undefined){try{const sh=new CSSStyleSheet();sh.replaceSync(BKSH+BKCSS);EBK.sheet=sh}catch(e){EBK.sheet=null}}
  if(EBK.sheet){r.adoptedStyleSheets=[EBK.sheet];r.innerHTML=html;return r}}
 r.innerHTML='<style>'+BKSH+BKCSS+'</style>'+html;return r}
function ebkMakePage(n){const d=document.createElement('div');if(n<1||n>EBK.N){d.className='pgw e';return d}d.className='pgw';d.dataset.n=n;return ebkFillPage(d,n)}
function ebkFillPage(d,n){d.innerHTML='<div class="pgh"></div><canvas class="pgc"></canvas>';
 const r=ebkShadow(d.querySelector('.pgh'),EBKCSS+'<div class="bkdoc scr" style="--bks:1">'+bkPageHtml(EBK.plan,n-1)+'</div>');
 r.addEventListener('click',ev=>{if(EBK.tool!=='none'||EBK.noclick)return;if(ev.target.closest&&ev.target.closest('.fq')){ebkGradePage(+d.dataset.n);return}const q=ev.target.closest&&ev.target.closest('.no,.qn');if(!q)return;const u=q.closest('.u.q[data-c]');if(u)ebkReveal(u.dataset.c)});ebkBindDraw(d.querySelector('canvas.pgc'));return d}
function ebkScrollTo(p,instant){const st=document.getElementById('ebst'),d=document.querySelector('#ebsp .pgw[data-n="'+p+'"]');if(!st||!d)return;EBK.sg=Date.now();st.scrollTo({top:Math.max(0,d.offsetTop-(EBK.view==='strip'?0:6)),behavior:instant?'auto':'smooth'})}
function ebkMount(d){if(!d.dataset.ph)return;delete d.dataset.ph;d.classList.remove('ph');ebkFillPage(d,+d.dataset.n);const k=(EBK.pgw||0)/(210*BK_MM);const h=d.querySelector('.pgh'),doc=h&&h.shadowRoot&&h.shadowRoot.querySelector('.bkdoc');if(doc&&k)doc.style.setProperty('--bks',k.toFixed(4));const c=d.querySelector('canvas.pgc');if(c)ebkCanvas(c);ebkMarkNumsOne(d)}
function ebkUnmount(d){if(d.dataset.ph||!d.firstChild)return;d.innerHTML='';d.dataset.ph=1;d.classList.add('ph')}
function ebkMarkNumsOne(d){const h=d.querySelector('.pgh'),r=h&&h.shadowRoot;if(!r)return;r.querySelectorAll('.u.q[data-c]').forEach(u=>{const q=u.querySelector('.no,.qn');if(q)q.classList.toggle('ebon',EBK.rev.includes(u.dataset.c))})}
function ebkUiSyncLite(){const cur=EBK.p;ebkSave(EBK.id,{last:cur});if(typeof urlSync==='function')urlSync();if(EBK.rail)thumbAct(EBK.rail,cur-1);
 const r=document.getElementById('ebr');if(r)r.value=cur;const ct=document.getElementById('ebc');if(ct)ct.textContent=cur+' / '+EBK.N;
 const bs=document.getElementById('ebs');if(bs)bs.classList.toggle('on',EBK.marks.includes(cur));
 const bm=document.getElementById('ebm');if(bm)bm.innerHTML='<option value="">북마크…</option>'+EBK.marks.map(n=>`<option value="${n}">p.${n}</option>`).join('');
 const bv=document.getElementById('ebv');if(bv)bv.value=EBK.view;ebkVL()}
function ebkDrawScroll(){const sp=document.getElementById('ebsp'),st=document.getElementById('ebst');if(!sp||!st)return;if(EBK.io){EBK.io.disconnect();EBK.io=null}
 sp.className='sp sc'+(EBK.view==='strip'?' strip':'');sp.innerHTML='';const fr=document.createDocumentFragment();
 for(let n=1;n<=EBK.N;n++){const d=document.createElement('div');d.className='pgw ph';d.dataset.n=n;d.dataset.ph=1;fr.appendChild(d)}
 sp.appendChild(fr);EBK.sm=0;ebkScale();
 EBK.io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)ebkMount(e.target);else ebkUnmount(e.target)}),{root:st,rootMargin:'170% 0px'});
 sp.querySelectorAll('.pgw').forEach(d=>EBK.io.observe(d));
 ebkScrollTo(EBK.p,1);EBK.sm=1;
 if(!st._ebsc){st._ebsc=1;let tk=0;st.addEventListener('scroll',()=>{if(!ebkScroll()||tk)return;tk=1;requestAnimationFrame(()=>{tk=0;const a=sp.firstChild,b=sp.children[1];if(!a)return;const step=b?b.offsetTop-a.offsetTop:a.offsetHeight;if(!step)return;
   const p=Math.max(1,Math.min(EBK.N,1+Math.floor((st.scrollTop+st.clientHeight*.3-a.offsetTop)/step)));if(p!==EBK.p){EBK.p=p;ebkUiSyncLite()}})},{passive:true})}
 ebkUiSyncLite();ebkMarkNums()}
const EBKCSS='<style>.fq{cursor:pointer}.u.q .no,.u.q .qn{cursor:pointer}.u.q .no.ebon,.u.q .qn.ebon{background:#ffe27a!important;color:#222!important;border-radius:5px;box-shadow:0 0 0 2px #f7b928}</style>';
function ebkCurlDraw(t,raw){if(EBK.r2){ebkCurlDraw2D(t,raw);return}const G=EBK.G;if(!G||!EBK.cs)return;const {gl,U}=G,s=EBK.cs;const e=raw?t:(t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2);let a,R;
 if(s.book){a=1-.5*e;R=.075*Math.pow(Math.sin(Math.PI*e),.75)+.004}else{R=.07;a=1-1.14*e}
 gl.viewport(0,0,gl.canvas.width,gl.canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
 gl.uniform1f(U.a,a);gl.uniform1f(U.R,R);gl.uniform1f(U.lo,s.book?.5:0);gl.uniform1f(U.mirror,s.dir<0?1:0);gl.uniform1f(U.mode,s.book?0:1);gl.uniform1f(U.hasK,s.k?1:0);
 gl.drawArrays(gl.TRIANGLE_STRIP,0,4)}
async function ebkCurlPrep(s){ // 텍스처 준비 → 캔버스 보이기 → 아래 쪽 갈아 끼우기
 const G=ebkGlInit();if(!window.html2canvas){EBK.curlErr='쪽 그림 라이브러리(html2canvas)를 불러오지 못했어요';return false}
 const [F,K]=await Promise.all([ebkTex(s.f),s.k?ebkTex(s.k):null]);if(!document.getElementById('ebk'))return false;
 if(!ebkGlPlace()){EBK.curlErr='효과 화면을 배치하지 못했어요';return false}
 const cv=document.getElementById('ebcv');EBK.r2=null;
 if(G){const {gl,U}=G;gl.useProgram(G.pr);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,G.tF);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,F);gl.uniform1i(U.F,0);
  gl.activeTexture(gl.TEXTURE1);gl.bindTexture(gl.TEXTURE_2D,G.tK);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,K||F);gl.uniform1i(U.K,1)}
 else{let g=null;try{g=cv.getContext('2d')}catch(e){}if(!g){EBK.curlErr='이 기기에서 캔버스를 쓸 수 없어요';return false}
  const mir=s.dir<0;EBK.r2={cv,g,F:mir?null:F,K:mir?null:(K||F),Fm:mir?ebkMirrorCv(F):null,Km:mir?ebkMirrorCv(K||F):null}}
 EBK.cs=s;ebkCurlDraw(0);cv.style.display='block';
 const spp=document.querySelector('#ebsp .spp');const kids=spp.querySelectorAll('.pgw');const old=kids[s.book?s.el:0];if(old){const nw=ebkMakePage(s.newN);nw.style.width=old.style.width;nw.style.height=old.style.height;old.replaceWith(nw);if(s.book){s.other=ebkMakePage(s.k);s.other.style.width=old.style.width;s.other.style.height=old.style.height}ebkScale()}
 return true}
function ebkCurlEnd(done){const c=document.getElementById('ebcv'),s=EBK.cs;
 if(done&&s&&(!s.book||s.other)){ // 이미 아래에 새 쪽이 깔려 있으므로 나머지 한 쪽만 갈아 끼우고, 다 그린 뒤에 효과 화면을 치움(끊김 없음)
  if(s.book){const spp=document.querySelector('#ebsp .spp'),kids=spp&&spp.querySelectorAll('.pgw');const idx=s.dir>0?0:1;if(kids&&kids[idx])kids[idx].replaceWith(s.other)}
  EBK.cs=null;EBK.r2=null;EBK.busy=0;EBK.p=EBK.np||EBK.p;EBK.np=0;ebkScale();ebkMarkNums();ebkUiSync();requestAnimationFrame(()=>requestAnimationFrame(()=>{if(c)c.style.display='none'}));return}
 if(c)c.style.display='none';EBK.cs=null;EBK.r2=null;EBK.busy=0;if(done&&EBK.np)EBK.p=EBK.np;EBK.np=0;ebkDraw()}
function ebkAnim(from,to,ms,raw){return new Promise(res=>{const t0=performance.now();const f=now=>{const k=Math.min(1,(now-t0)/ms);const t=raw?from+(to-from)*(1-(1-k)*(1-k)):from+(to-from)*k;ebkCurlDraw(t,raw);if(k<1)requestAnimationFrame(f);else res()};requestAnimationFrame(f)})}
async function ebkFlip(dir){if(EBK.busy)return;const s=ebkSpec(dir);if(!s)return;EBK.busy=1;
 {const pr=[ebkTex(s.f)];if(s.k)pr.push(ebkTex(s.k));pr.forEach(p=>p.catch(()=>{}));
  if(!(ebkTexReady(s.f)&&(!s.k||ebkTexReady(s.k)))){await Promise.race([Promise.all(pr).catch(()=>{}),new Promise(r=>setTimeout(r,650))]);
   if(!(ebkTexReady(s.f)&&(!s.k||ebkTexReady(s.k)))){EBK.busy=0;EBK.p=s.np;EBK.rev=[];ebkDraw(0,0,dir);return}}}
 const sp=document.getElementById('ebld');const tm=setTimeout(()=>{if(sp)sp.style.display='block'},260);let ok=false;EBK.curlErr='';
 try{ok=await Promise.race([ebkCurlPrep(s),new Promise((_,rej)=>setTimeout(()=>rej(new Error('쪽 그림을 만드는 데 너무 오래 걸려요')),4500))])}catch(e){EBK.curlErr=String((e&&e.message)||e);console.warn('curl',e)}
 clearTimeout(tm);if(sp)sp.style.display='none';
 if(!ok){const c=document.getElementById('ebcv');if(c)c.style.display='none';EBK.cs=null;EBK.r2=null;EBK.busy=0;EBK.p=s.np;EBK.rev=[];
  if(!EBK.warned){EBK.warned=1;toast('말아 올리기 효과를 쓸 수 없어 기본 효과로 넘겨요 ('+(EBK.curlErr||'알 수 없음')+')')}
  ebkDraw(0,0,dir);return}
 EBK.np=s.np;EBK.rev=[];try{await ebkAnim(0,1,s.book?950:800)}catch(e){console.warn(e)}ebkCurlEnd(true)}
/* 끌어서 넘기기: 가로로 끌면 손가락을 따라 말려 올라가고, 놓을 때 3할 넘게 말렸으면 끝까지 넘김 */
function ebkScrubBind(s){let st=null;
 s.addEventListener('pointerdown',e=>{if(ebkScroll()||EBK.busy||!EBKFX||EBK.tool!=='none'||EBK.z>1.02||e.button>0)return;if(e.target.closest&&e.target.closest('button,select,input,.eba'))return;st={x:e.clientX,y:e.clientY,id:e.pointerId,state:0,dx:0}},true);
 s.addEventListener('pointermove',async e=>{if(!st||e.pointerId!==st.id)return;const dx=e.clientX-st.x,dy=e.clientY-st.y;
  if(st.state===0){if(Math.abs(dx)<14||Math.abs(dx)<Math.abs(dy)*1.2)return;st.state=1;st.dir=dx<0?1:-1;const sp=ebkSpec(st.dir);if(!sp){st=null;return}st.spec=sp;if(!(ebkTexReady(sp.f)&&(!sp.k||ebkTexReady(sp.k)))){ebkTex(sp.f).catch(()=>{});if(sp.k)ebkTex(sp.k).catch(()=>{});st.state=3;EBK.noclick=1;return}EBK.busy=1;EBK.noclick=1;try{s.setPointerCapture(e.pointerId)}catch(x){}
   let ok=false;try{ok=await ebkCurlPrep(sp)}catch(x){}if(!st){return}if(!ok){EBK.busy=0;st=null;ebkDraw();return}st.state=2;EBK.np=sp.np}
  st.dx=dx;if(st.state===3)return;if(st.state===2){const w=document.getElementById('ebcv').getBoundingClientRect().width*(st.spec.book?.5:.9);const t=Math.max(0,Math.min(1,(st.dir>0?-dx:dx)/w));st.t=t;ebkCurlDraw(t,1)}},true);
 const end=async e=>{if(!st||e.pointerId!==st.id)return;const x=st;st=null;if(x.state===0)return;if(x.state===3){setTimeout(()=>EBK.noclick=0,50);if(Math.abs(x.dx||0)>50)ebkStep(x.dir);return}
  if(x.state===1){EBK.busy=0;setTimeout(()=>EBK.noclick=0,0);ebkDraw();return}
  const t=x.t||0;if(t>.3){await ebkAnim(t,1,Math.max(260,(1-t)*850),1);ebkCurlEnd(true)}else{await ebkAnim(t,0,Math.max(200,t*600),1);ebkCurlEnd(false)}setTimeout(()=>EBK.noclick=0,50)};
 s.addEventListener('pointerup',end,true);s.addEventListener('pointercancel',end,true)}

/* ---------- 인쇄 ---------- */
function bkFontCssRule(){const f=BKO.font&&typeof FONTS!=='undefined'&&FONTS[BKO.font];return f&&BKO.font!=='paper'?'.bkdoc,.bkdoc *{font-family:'+f[1]+'!important}':''}
/* 양면 인쇄: 답안이 뒷면에서 시작하지 않게 빈 쪽을 끼우고, 총 쪽수가 홀수면 마지막에 빈 쪽을 붙임(-1 = 빈 쪽) */
function bkSheets(plan,all){const last=plan.pages[plan.pages.length-1],back=!!(all&&last&&last.k==='back');
 const n=all?plan.pages.length-(back?1:0):Math.max(1,(plan.aStart||plan.pages.length+1)-1);const a=[];for(let i=0;i<n;i++)a.push(i);
 const dp=dupGet();
 if(dp&&all&&plan.aStart>1&&plan.aStart-1<n&&plan.aStart%2===0)a.splice(plan.aStart-1,0,-1);
 if(back){if(dp&&a.length%2===0)a.push(-1);a.push(plan.pages.length-1)}else if(dp&&a.length%2)a.push(-1);
 return a}
const BKLOGO='<svg viewBox="0 8 162 76" role="img" aria-label="Solvi" ><path d="M23.8 56.8C36.1 56.8 43.8 51.6 45.4 42.2C46.7 34.4 42.6 29.9 32.2 28L28.6 27.3C23.9 26.4 22.3 25.2 22.7 22.9C23.1 20.6 25.9 18.9 29.6 18.9C33.6 18.9 35.7 20.8 35.5 24.2H47.4C48.7 14.4 42.1 8.7 30.4 8.7C19.4 8.7 11.1 14.3 9.7 22.8C8.4 30.1 12.8 35.2 21.5 36.9L26 37.8C31.1 38.8 32.9 40.2 32.5 42.4C32.1 44.8 29.1 46.5 25 46.5C20.3 46.5 17.7 44.3 18.1 40.5H5.8C4.2 50.7 10.6 56.8 23.8 56.8Z M63.1 56.8C75.6 56.8 83.5 47.7 83.5 36.8C83.5 27.8 77.3 22.2 67.5 22.2C55.6 22.2 47.1 30.6 47.1 42.2C47.1 51.2 53.3 56.8 63.1 56.8ZM63.9 47C61.7 47 59.6 45.5 59.6 42.3C59.6 37.6 62 32 66.7 32C68.9 32 71 33.5 71 36.7C71 41.4 68.6 47 63.9 47Z M102.9 9.4H90.4L82.7 56H95.2Z M107.6 56H121.9L139.2 23H125.8L119.6 37C118.5 39.6 117.3 42.1 116.3 44.7C116 42.1 115.8 39.6 115.4 37L113.7 23H101.2Z M134.3 56H146.8L152.3 23H139.8ZM146.5 20.3C150.1 20.3 153.3 17.6 153.9 14.2C154.5 10.8 152.1 8.1 148.5 8.1C144.9 8.1 141.7 10.8 141.1 14.2C140.5 17.6 142.9 20.3 146.5 20.3Z" fill="#8a96a6"/><path d="M4 68 L27.1 78 L150.3 62" fill="none" stroke="#ffc21a" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const bkBlankHtml=()=>'<div class="bp bk bkblank"><div class="bklg">'+blankLogoHtml()+'</div></div>';
const bkSheetHtml=(plan,i)=>i<0?bkBlankHtml():bkPageHtml(plan,i);
function bkDocHtml(plan,all){
 const abs=location.origin+location.pathname.replace(/[^/]*$/,'');
 let pg='';bkSheets(plan,all).forEach(i=>pg+=bkSheetHtml(plan,i));
 return '<!doctype html><html><head><meta charset="utf-8"><title>'+esc(plan.title)+'</title><link rel="stylesheet" href="'+BKCDN+'"><style>'+bkFontCss(abs)+'@page{size:A4;margin:0}html,body{margin:0;padding:0;background:#d9dde3}'+BKCSS+'.bkdoc .bp{margin:8mm auto;box-shadow:0 1px 8px rgba(0,0,0,.25);page-break-after:always;break-after:page}.bkdoc .bp:last-child{page-break-after:auto;break-after:auto}@media print{html,body{background:#fff}.bkdoc .bp{margin:0;box-shadow:none}}'+bkFontCssRule()+'</style></head><body class="bkdoc">'+pg+'</body></html>'}
let BKPOP=null;
function bkBarHtml(plan){
 const o=(a,sel)=>a.map(([v,t])=>`<option value="${v}" ${String(sel)===String(v)?'selected':''}>${t}</option>`).join('');
 const gap=o([[0,'기본'],[1,'조금 넓게'],[2,'넓게'],[3,'아주 넓게']],BKO.gap||0);
 const fnt=Object.entries(FONTS).map(([k,v])=>`<option value="${k}" ${(BKO.font||'paper')===k?'selected':''}>${v[0]}</option>`).join('');
 const des=plan.kind==='m'?tbS('pdes','','디자인','palette','디자인',o([['exam','시험지 (흑백)'],['color','컬러 포인트']],BKO.design||'exam')):'';
 const gk=plan.subj==='me'?'':tbS('pgut','','제본 여백','bind','제본 여백',o(BKGUTS,bkGutOf(plan)));
 return tbS('pgap','','문제 간격','gap','문제 간격',gap)+tbT('pdup','','양면 인쇄: 답안이 뒷면에서 시작하지 않게 빈 쪽을 채워요','duplex','양면 인쇄',dupGet()?'on':'')+des+gk+swHtml(BKO.color||'',bkPal().p,true)+tbS('pfnt','','글꼴','type','글꼴',fnt)}
async function bkRepop(o){if(!BKPOP||!BKPOP.win||BKPOP.win.closed)return;bkOset(o);if(BKPOP.subj!==SUBJ)await setSubject(BKPOP.subj);
 const plan=await bkPlan(bkPid(BKPOP.id));if(!plan)return;await bkShowIn(BKPOP.win,plan,BKPOP.all)}
async function bkShowIn(w,plan,all){window._popExtra=bkBarHtml(plan);try{await cbPrintHtml(bkDocHtml(plan,all),w)}finally{window._popExtra=''}
 popWire(w,d=>{d.getElementById('pgap').onchange=e=>bkRepop({gap:+e.target.value});d.getElementById('pdup').onclick=()=>{dupSet(!dupGet());bkRepop({})};const des=d.getElementById('pdes');if(des)des.onchange=e=>bkRepop({design:e.target.value});swWire(d,v=>bkRepop({color:v}));const gu=d.getElementById('pgut');if(gu)gu.onchange=e=>{bkGutSet(bkGutKey(plan),e.target.value);bkRepop({})};d.getElementById('pfnt').onchange=e=>bkRepop({font:e.target.value})})}
async function bkPrint(id,all){
 id=bkPid(id);
 if(typeof isMob==='function'&&isMob()){toast('휴대폰·태블릿은 인쇄 창이 열리지 않는 경우가 많아 PDF로 만들어 드려요. 저장한 PDF를 열어 인쇄하세요');return bkPdf(id,all)}
 const pw=typeof popOpen==='function'?popOpen('인쇄할 책을 만드는 중…'):null;
 await bkInit();const P=bkParts(id);if(P&&P.subj!==SUBJ)await setSubject(P.subj);
 busyRun('인쇄할 책을 만드는 중…',async()=>{await conceptLoad();const plan=await bkPlan(id);if(!plan){if(pw)pw.close();return}
  if(pw){BKPOP={win:pw,id,all,subj:SUBJ};await bkShowIn(pw,plan,all)}else await cbPrintHtml(bkDocHtml(plan,all),pw)})}

/* ---------- PDF 파일로 내려받기(쪽마다 이미지로 그려 한 파일로 묶음) ---------- */
function bkLoadJs(src,ok){return new Promise((res,rej)=>{if(ok())return res();const s=document.createElement('script');s.src=src;s.onload=res;s.onerror=()=>rej(new Error(src));document.head.appendChild(s)})}
async function bkPdf(id,all){
 id=bkPid(id);await bkInit();const P=bkParts(id);if(P&&P.subj!==SUBJ)await setSubject(P.subj);
 busyRun('PDF를 만드는 중…',async()=>{let st,host;
  try{
   await conceptLoad();await Promise.all([bkLoadJs('lib/html2canvas.min.js',()=>window.html2canvas),bkLoadJs('lib/jspdf.umd.min.js',()=>window.jspdf)]);
   const plan=await bkPlan(id);if(!plan)return;
   const SH=bkSheets(plan,all),n=SH.length;
   st=document.createElement('style');st.textContent=BKCSS+'.bkdoc .bp{margin:0!important;box-shadow:none!important}'+bkFontCssRule();document.head.appendChild(st);
   host=document.createElement('div');host.className='bkdoc';host.style.cssText='position:absolute;left:0;top:0;width:210mm;z-index:-1;background:#fff';document.body.appendChild(host);
   const doc=new window.jspdf.jsPDF({unit:'mm',format:'a4',compress:true});const t=document.getElementById('busyt');
   for(let i=0;i<n;i++){
    if(t)t.textContent='PDF를 만드는 중… '+(i+1)+' / '+n+'쪽';
    host.innerHTML=bkSheetHtml(plan,SH[i]);
    await Promise.all([...host.querySelectorAll('img')].map(im=>im.complete&&im.naturalWidth?1:new Promise(r=>{im.onload=im.onerror=()=>r();setTimeout(r,8000)})));
    try{await document.fonts.ready}catch(e){}
    const cv=await window.html2canvas(host.firstElementChild,{scale:1.7,backgroundColor:'#ffffff',useCORS:true,logging:false});
    if(i)doc.addPage();doc.addImage(cv.toDataURL('image/jpeg',.8),'JPEG',0,0,210,297,undefined,'FAST');cv.width=cv.height=0;
    if(i%8===7)await new Promise(r=>setTimeout(r,0))}
   const a=document.createElement('a');a.href=URL.createObjectURL(doc.output('blob'));a.download=(plan.title||'교재').replace(/[\\\/:*?"<>|]+/g,' ').trim()+(all?'':' (문제만)')+'.pdf';document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},4000);toast('PDF를 저장했어요')
  }catch(e){alert('PDF를 만들지 못했어요. 「전체 인쇄 · PDF」로 인쇄 창에서 PDF로 저장해 주세요.\n('+(e&&e.message||e)+')')}
  finally{if(host)host.remove();if(st)st.remove()}})}
/* ---------- 단독 HTML 파일(내려받아 열어보는 교재) ---------- */
function bkStandalone(plan){
 const cdn='';
 let pg='';for(let i=0;i<plan.pages.length;i++)pg+=bkPageHtml(plan,i);
 return '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(plan.title)+'</title><link rel="stylesheet" href="'+BKCDN+'"><style>'+cdn+'@page{size:A4;margin:0}*{box-sizing:border-box}html,body{margin:0;padding:0;background:#d9dde3}'+BKCSS+'.bkdoc .bp{margin:8mm auto;box-shadow:0 1px 8px rgba(0,0,0,.25)}@media print{html,body{background:#fff}.bkdoc .bp{margin:0;box-shadow:none;page-break-after:always;break-after:page}.bkdoc .bp:last-child{page-break-after:auto;break-after:auto}}</style></head><body class="bkdoc">'+pg+'<script>(function(){function f(){var s=Math.min(1,innerWidth/(210*96/25.4+16));document.body.style.zoom=s<1?s:""}f();addEventListener("resize",f);addEventListener("beforeprint",function(){document.body.style.zoom=""});addEventListener("afterprint",f)})()</script></body></html>'}
/* ---------- 높이표 만들기(개발용) : 콘솔/자동화에서 await bkMeasureAll() ---------- */
let BKREC=null;
async function bkSettle(fn){let plan;for(let i=0;i<5;i++){BKREC=[];try{plan=fn()}finally{var rec=BKREC;BKREC=null}
  const seen=new Set();let n=0;for(const u of rec){if((BKHT&&BKHT[u.key]!=null)||BKHA[u.key]!=null||seen.has(u.key))continue;seen.add(u.key);BKHA[u.key]=await bkMeasureAsync(u.html,u.w||BK_COLW,u.cls);n++}
  if(!n)break}
 return plan}
async function bkMeasureAsync(html,w,cls){const p=bkProbe();p.innerHTML='<div class="'+(cls||'bk')+'" style="'+bkVars()+';width:'+w+'mm;display:flow-root;font-size:12px;line-height:1.5">'+html+'</div>';
 await Promise.all([...p.querySelectorAll('img')].map(i=>i.complete&&i.naturalWidth?1:new Promise(r=>{i.onload=i.onerror=()=>r();setTimeout(r,30000)})));
 return Math.ceil(p.firstChild.getBoundingClientRect().height/BK_MM*10)/10}
async function bkMeasureAll(){
 await bkInit();BKHT={};const subj=SUBJ;const ids=[subj+'-c',subj+'-t'];
 for(let pass=0;pass<8;pass++){
  delete BKSELC[subj];ids.forEach(id=>delete BKP[id]);
  BKREC=[];for(const id of ids)await bkPlan(id);
  const rec=BKREC;BKREC=null;const seen=new Set();let n=0;
  for(const u of rec){if(BKHA[u.key]!=null||seen.has(u.key))continue;seen.add(u.key);BKHA[u.key]=await bkMeasureAsync(u.html,u.w||BK_COLW,u.cls);n++}
  if(!n)break}
 delete BKSELC[subj];ids.forEach(id=>delete BKP[id]);for(const id of ids)await bkPlan(id);
 return BKHA}
/* ---------- 교재 만들기 화면 ---------- */
/* ---------- 자유 구성 빌더 ---------- */
const BKFPRE={
 std:{n:'종합 교재',s:'개념 · 확인 문제 · 유형',on:'cobmt',cm:{}},
 last:{n:'직전 대비 교재',s:'시험 직전 핵심 압축 정리',on:'cobt',cm:{t:['n',8]}},
 drill:{n:'개념 양치기',s:'OX · 빈칸 집중 반복',on:'ob',cm:{o:['a'],b:['a']}},
 part:{n:'특정 부분 양치기',s:'고른 소단원만 파고들기',on:'obmt',cm:{o:['a'],b:['a'],m:['a'],t:['a']}},
 free:{n:'나만의 교재',s:'',on:'cobmt',cm:{}}};
function bkfNew(k){const P=BKFPRE[k]||BKFPRE.free,cm={};BKFP.forEach(([c])=>{const v=P.cm[c];cm[c]=v?{m:v[0],n:v[1]||10}:{m:'d',n:10}});
 const on={};[...P.on].forEach(c=>on[c]=1);
 return {kind:'free',pre:k,name:P.n,sub:P.s,order:BKFP.map(x=>x[0]),on,cm,lv:{t:15,e:15},subs:k==='part'?[]:[],sort:0,grp:0,ans:0,brk:0,color:'',cover:0,noqr:0,gut:0,font:'',lf:'solvi',lfp:'br',lb:'solvi',lbp:'bc',back:1}}
function bkfParts(d){return d.order.filter(k=>d.on[k]).map(k=>{const c=d.cm[k]||{m:'d',n:10};return {k,all:c.m==='a',cap:c.m==='n'?Math.max(1,Math.min(999,c.n|0)):0,lv:BKFLV.has(k)?(d.lv[k]||15):15}})}
function bkfRead(){const d=BKV.d,g=i=>document.getElementById(i);if(!d||d.kind!=='free')return;
 if(g('bxn'))d.name=g('bxn').value;if(g('bxs'))d.sub=g('bxs').value;if(g('bxg'))d.gut=+g('bxg').value||0;
 BKFP.forEach(([k])=>{if(g('bfo_'+k))d.on[k]=g('bfo_'+k).checked?1:0;if(!d.on[k])delete d.on[k];
  if(g('bfn_'+k)){const c=d.cm[k]=d.cm[k]||{m:'d',n:10};c.n=Math.max(1,Math.min(999,Math.round(+g('bfn_'+k).value)||10))}
  if(BKFLV.has(k)&&g('bfl_'+k+'_1')){let lv=0;[1,2,4,8].forEach(b=>{const e=g('bfl_'+k+'_'+b);if(e&&e.checked)lv|=b});d.lv[k]=lv||15}});
 if(g('bflf'))d.lf=g('bflf').value;if(g('bflfp'))d.lfp=g('bflfp').value;if(g('bflb'))d.lb=g('bflb').value;if(g('bflbp'))d.lbp=g('bflbp').value;if(g('bfback'))d.back=g('bfback').checked?1:0;if(g('bffont'))d.font=g('bffont').value;
 if(g('bxcx_en')){d.cx={en:g('bxcx_en').value,ser:g('bxcx_ser').value,small:g('bxcx_small').value,school:g('bxcx_school').value,grade:g('bxcx_grade').value,wm:g('bxcx_wm').value}}
 if(g('bfs'))d.sort=+g('bfs').value;if(g('bfg'))d.grp=+g('bfg').value;if(g('bfa'))d.ans=+g('bfa').value;if(g('bfb'))d.brk=g('bfb').checked?1:0;if(g('bfq'))d.noqr=g('bfq').checked?0:1;
 if(g('bxs_0')){d.subs=bkSubs().map((s,i)=>g('bxs_'+i)&&g('bxs_'+i).checked?i:-1).filter(i=>i>=0);if(d.subs.length===bkSubs().length)d.subs=[]}}
function bkfSet(k,v){bkfRead();BKV.d[k]=v;bkShow()}
function bkfMove(k,dx){bkfRead();const o=BKV.d.order,i=o.indexOf(k),j=i+dx;if(j<0||j>=o.length)return;[o[i],o[j]]=[o[j],o[i]];bkShow()}
function bkfPre(k){bkfRead();const o=BKV.d,n=bkfNew(k),keepN=o.name&&!Object.values(BKFPRE).some(p=>p.n===o.name);if(keepN)n.name=o.name;if(o.sub&&!Object.values(BKFPRE).some(p=>p.s===o.sub))n.sub=o.sub;
 ['subs','color','cover','noqr','gut','font','lf','lfp','lb','lbp','back'].forEach(x=>{if(x!=='subs'||k!=='part')n[x]=o[x]});BKV.d=n;bkShow()}
function bkfEstText(d){try{const parts=bkfParts(d);if(!parts.length)return '구성을 하나 이상 고르세요';
 const B=bkfBlocks({parts,subs:d.subs||[],sort:d.sort,grp:d.grp});const by={};B.blocks.forEach(b=>by[b.k]=(by[b.k]||0)+b.arr.length);
 const n=Object.values(by).reduce((a,b)=>a+b,0);
 return '소단원 '+B.subs.length+'개 · '+parts.filter(p=>p.k!=='c').map(p=>BKFN[p.k]+' '+(by[p.k]||0)).join(' · ')+' — 총 '+n+'문항'+(d.on.c?' + 개념 정리':'')+(n>900?' (많아요 — 인쇄에 시간이 걸릴 수 있어요)':'')}catch(e){return ''}}
let BKPVT=0,BKPV={plan:null,i:0};
function bkfStep(n){bkfRead();BKV.step=n;bkShow();scrollTo({top:0,behavior:'smooth'})}
function bkfPvTab(k){BKPV.i=k;bkfPvDraw()}
function bkfPvIdx(plan,k){const pr=plan.pages.findIndex(p=>p.k==='pr'||p.k==='cn');return [0,1,pr>=0?pr:Math.min(2,plan.pages.length-1),plan.aStart?plan.aStart-1:plan.pages.length-1,plan.pages.length-1][k]}
function bkfPvDraw(){const plan=BKPV.plan,host=document.getElementById('bkpvp');if(!plan||!host)return;const k=BKPV.i,idx=Math.max(0,Math.min(plan.pages.length-1,bkfPvIdx(plan,k)));
 const W=host.clientWidth||330;host.style.setProperty('--bks',(W/(210*BK_MM)).toFixed(4));host.style.height=(297*BK_MM*W/(210*BK_MM))+'px';
 bkShadow(host,'<div class="bkdoc scr">'+bkPageHtml(plan,idx)+'</div>');
 document.querySelectorAll('.bkpvt button').forEach((b,i)=>b.classList.toggle('on',i===k));
 const c=document.getElementById('bkpvc');if(c)c.textContent='p.'+plan.pages[idx].n+' / 총 '+plan.pages.length+'쪽';
 document.querySelectorAll('.bkcvs [data-c]').forEach(h=>{const cp={...plan,dz:{...(plan.dz||{}),cover:+h.dataset.c}};h.style.setProperty('--bks',(h.clientWidth/(210*BK_MM)).toFixed(4));bkShadow(h,'<div class="bkdoc scr">'+bkPageHtml(cp,0)+'</div>')})}
function bkfPreview(){const box=document.getElementById('bkpv');if(!box||!BKV.d||BKV.d.kind!=='free')return;const my=++BKPVT;clearTimeout(bkfPreview._t);
 const st=document.getElementById('bkpvs');if(st)st.textContent='미리보기를 만드는 중…';
 bkfPreview._t=setTimeout(async()=>{const d=BKV.d,parts=bkfParts(d);if(!parts.length){if(st)st.textContent='구성을 하나 이상 고르세요';return}
  try{await bkInit();await conceptLoad();const def={kind:'free',parts,subs:d.subs||[],sort:d.sort,grp:d.grp,ans:d.ans,brk:d.brk,name:d.name||'교재 이름',subt:d.sub||'',dz:{color:d.color||'',cover:d.cover|0,noqr:d.noqr?1:0,font:d.font||'',lf:d.lf||'solvi',lfp:d.lfp||'br',lb:d.lb||'solvi',lbp:d.lbp||'bc',back:d.back?1:0,cx:d.cx||null}};
   const plan=await bkSettle(()=>bkPlanFree('preview',def));if(my!==BKPVT||!document.getElementById('bkpv'))return;
   plan.pages.forEach((p,i)=>p.n=i+1);plan.id='preview';plan.subj=SUBJ;BKPV.plan=plan;bkfPvDraw();
   if(st)st.textContent='총 '+plan.pages.length+'쪽 · '+plan.total+'문항'+(plan.aStart?' · 정답 p.'+plan.aStart:'')}catch(e){if(st)st.textContent='미리보기를 만들지 못했어요'}},350)}
const LGS=[['solvi','Solvi 로고'],['academy','학원 로고'],['none','넣지 않기']];
function bkfSeg(el,key,val,i){const d=BKV.d;d[key]=(key==='ans'||key==='gut')?+val:val;const g=el.parentElement;g.style.setProperty('--i',i);g.querySelectorAll('button').forEach((b,k)=>{b.classList.toggle('on',k===i);b.setAttribute('aria-checked',String(k===i))});bkxEst()}
function bkfBuilder(){const d=BKV.d,subs=bkSubs();
 const seg=(key,opts,cur)=>`<div class="bkseg" role="radiogroup" style="--n:${opts.length};--i:${Math.max(0,opts.findIndex(o=>String(o[0])===String(cur)))}"><i class="bkth"></i>${opts.map(([v,t],i)=>`<button type="button" role="radio" aria-checked="${String(v)===String(cur)}" class="${String(v)===String(cur)?'on':''}" onclick="bkfSeg(this,'${key}','${v}',${i})">${t}</button>`).join('')}</div>`;const step=BKV.step||1;
 const STP=['구성 고르기','문항 수 · 난이도 · 범위','표지 · 디자인'];
 const stepper=`<div class="steps">${STP.map((t,i)=>`<span class="bkst ${i+1===step?'on':i+1<step?'done':''}" onclick="bkfStep(${i+1})" role="button" tabindex="0" onkeydown="if(event.key==='Enter')bkfStep(${i+1})"><i>${i+1<step?'✓':i+1}</i>${t}</span>`).join('<u></u>')}</div>`;
 const chip=k=>`<button class="${d.pre===k?'p':'s'}" onclick="bkfPre('${k}')" style="text-align:left;padding:10px 12px;border-radius:10px;min-width:0"><b style="display:block;font-size:14px">${BKFPRE[k].n}</b><small style="font-weight:400;opacity:.8">${BKFPRE[k].s||'구성부터 직접 고르기'}</small></button>`;
 const rowA=(k,i)=>{const nm=BKFN[k],on=!!d.on[k];return `<div class="bfr ${on?'':'off'}"><div class="bfh"><label class="chk"><input type="checkbox" id="bfo_${k}" ${on?'checked':''} onchange="bkfRead();bkShow()"> <b>${i+1}. ${nm}</b></label><span class="bfmv"><button class="s sm" onclick="bkfMove('${k}',-1)" ${i?'':'disabled'} aria-label="${nm} 위로">↑</button><button class="s sm" onclick="bkfMove('${k}',1)" ${i<5?'':'disabled'} aria-label="${nm} 아래로">↓</button></span></div><div class="bfb"><span class="m" style="font-size:12.5px">${BKFD[k]}</span></div></div>`};
 const rowB=k=>{const nm=BKFN[k],c=d.cm[k]||{m:'d',n:10};if(k==='c')return `<div class="bfr"><div class="bfh"><b>${nm}</b></div><div class="bfb"><span class="m" style="font-size:12.5px">소단원별 개념 요약을 그대로 담아요</span></div></div>`;
  const lvs=BKFLV.has(k)?`<span class="bflv"><span class="m">난이도</span>${[[1,'하'],[2,'중'],[4,'상'],[8,'최상']].map(([b,t])=>`<label class="chk"><input type="checkbox" id="bfl_${k}_${b}" ${(d.lv[k]||15)&b?'checked':''} onchange="bkfRead();bkxEst()"> ${t}</label>`).join('')}<button class="s sm" onclick="bkfLv('${k}',3)">기초(하·중)</button><button class="s sm" onclick="bkfLv('${k}',6)">표준(중·상)</button><button class="s sm" onclick="bkfLv('${k}',12)">심화(상·최상)</button><button class="s sm" onclick="bkfLv('${k}',15)">전체</button></span>`:'';
  return `<div class="bfr"><div class="bfh"><b>${nm}</b></div><div class="bfb"><span class="bfcm">${[['d','기본 구성'],['a','전부 담기'],['n','직접']].map(([v,t])=>`<label class="chk"><input type="radio" name="bfm_${k}" value="${v}" ${c.m===v?'checked':''} onchange="bkfCm('${k}',this.value)"> ${t}</label>`).join('')}</span>${c.m==='n'?`<span><input type="number" id="bfn_${k}" min="1" max="999" value="${c.n}" style="width:80px" oninput="bkfRead();bkxEst()"> <small class="m">문항 / 소단원</small></span>`:''}${lvs}</div></div>`};
 const op=(v,t,cur)=>`<option value="${v}" ${cur===v?'selected':''}>${t}</option>`;
 const sel=d.subs||[],lo=sel.length?Math.min(...sel):0,hi=sel.length?Math.max(...sel):subs.length-1,hasSc=!!((CONC[SUBJ]||{}).scope||[]).length;
 const sw=[['','기본']].concat(Object.entries(PAL).map(([k,v])=>[k,v[4]]));
 const swb=sw.map(([k,t])=>{const c=k?PAL[k][0]:bkPal().p;return `<button type="button" class="bfsw ${(d.color||'')===k?'on':''}" onclick="bkfSet('color','${k}')" style="--c:${c}" title="${t}" aria-label="색상 ${t}"></button>`}).join('');
 const covs=[[0,'기본형','일러스트 + 흰 바탕'],[1,'컬러 띠형','큰 색 면 위에 제목'],[2,'미니멀형','글자 중심'],[3,'사이드 바','왼쪽 세로 색 띠'],[4,'중앙 정렬형','글자를 가운데로'],[5,'하단 컬러 블록','아래쪽 큰 색 면'],[6,'시리즈형','네이비 · 큰 영문 제목']].map(([v,t,s2])=>`<button class="bkcvb ${(d.cover|0)===v?'on':''}" onclick="bkfSet('cover',${v})" aria-label="${t}"><span class="bkcvh" data-c="${v}"></span><b>${t}</b><small>${s2}</small></button>`).join('');
 let body='';
 if(step===1)body=`<h3 class="bkh">시작 양식 <small>고른 뒤 아래에서 마음대로 바꿀 수 있어요</small></h3><div class="bkpre">${['std','last','drill','part','free'].map(chip).join('')}<button class="s" onclick="bkNew('full')" style="text-align:left;padding:10px 12px;border-radius:10px"><b style="display:block;font-size:14px">전범위 모의고사</b><small style="font-weight:400;opacity:.8">회차별 시험지 (별도 설정)</small></button></div>
  <h3 class="bkh">책에 넣을 구성 <small>체크로 넣고 빼고, ↑↓로 순서를 바꿔요</small></h3>${d.order.map(rowA).join('')}
  <h3 class="bkh">배열 방식</h3><div class="bfg"><div><label class="bkfl">배열</label><select id="bfg" onchange="bkfRead();bkxEst()">${op(0,'소단원별 (소단원 안에서 구성 순서대로)',d.grp|0)}${op(1,'구성별 (OX 전체 → 빈칸 전체 …)',d.grp|0)}</select></div><div style="display:flex;align-items:flex-end"><label class="chk"><input type="checkbox" id="bfb" ${d.brk?'checked':''} onchange="bkfRead();bkxEst()"> 소단원(구성)마다 새 쪽에서 시작</label></div></div>`;
 else if(step===2)body=`<h3 class="bkh">구성별 문항 수 · 난이도 <small>문항 수는 소단원마다 적용돼요</small></h3>${d.order.filter(k=>d.on[k]).map(rowB).join('')||'<div class="hint">1단계에서 구성을 하나 이상 고르세요</div>'}
  <h3 class="bkh">정렬</h3><div class="bfg"><div><label class="bkfl">유형·서술형 문제 정렬 (난이도 순서)</label><select id="bfs" onchange="bkfRead();bkxEst()">${op(0,'유형별로 묶기 (유형 안에서 쉬움→어려움)',d.sort|0)}${op(1,'쉬운 문제 → 어려운 문제',d.sort|0)}${op(3,'어려운 문제 → 쉬운 문제',d.sort|0)}${op(2,'섞어서 (고정된 무작위)',d.sort|0)}</select></div></div>
  <h3 class="bkh">범위 · 소단원 <small>비우면 전체 · 시작과 끝을 고르면 그 사이가 한꺼번에 선택돼요</small></h3>
  <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:6px 0"><select id="bxr1" style="width:auto;max-width:46%">${subs.map((s2,i)=>`<option value="${i}" ${i===lo?'selected':''}>${esc(s2.k)} ${esc(s2.name)}</option>`).join('')}</select><span>~</span><select id="bxr2" style="width:auto;max-width:46%">${subs.map((s2,i)=>`<option value="${i}" ${i===hi?'selected':''}>${esc(s2.k)} ${esc(s2.name)}</option>`).join('')}</select><button class="s sm" onclick="bkxRange()">범위 선택</button><button class="s sm" onclick="bkxRangeSet('all')">전체</button><button class="s sm" onclick="bkxRangeSet('none')">해제</button>${hasSc?'<button class="s sm" onclick="bkxRangeSet(\'def\')">기본 범위</button>':''}</div>
  <div class="bksubs">${subs.map((s2,i)=>`<label class="chk"><input type="checkbox" id="bxs_${i}" ${sel.includes(i)?'checked':''} onchange="bkfRead();bkxEst()"> ${esc(s2.k)} ${esc(s2.name)}</label>`).join('')}</div>`;
 else body=`<div class="bkc"><h3>이름</h3><div class="bkrow"><label for="bxn">교재 이름</label><input id="bxn" class="bkin" value="${esc(d.name)}" maxlength="30" oninput="bkfRead();bkxEst()"></div><div class="bkrow"><label for="bxs">부제</label><input id="bxs" class="bkin" value="${esc(d.sub||'')}" maxlength="40" oninput="bkfRead();bkxEst()"></div></div>
  <div class="bkc"><h3>표지 스타일 <small>눌러서 고르면 오른쪽 미리보기에 바로 보여요</small></h3><div class="bkcvs">${covs}</div></div>
  ${(d.cover|0)===6?bkCxCard(d):''}
  <div class="bkc"><h3>색상</h3><div class="bkswr">${swb}</div></div>
  <div class="bkc"><h3>로고 <small>기본은 Solvi 로고예요 · 학원 로고는 학원 설정에서 올린 이미지·이름을 써요</small></h3>
   <div class="bkrow"><label>앞표지</label><div class="bkctl">${seg('lf',LGS,d.lf||'solvi')}${seg('lfp',[['bl','왼쪽 아래'],['bc','가운데 아래'],['br','오른쪽 아래']],d.lfp||'br')}</div></div>
   <div class="bkrow"><label>뒷표지</label><div class="bkctl">${seg('lb',LGS,d.lb||'solvi')}${seg('lbp',[['tc','위 중앙'],['bc','아래 중앙']],d.lbp||'bc')}</div></div>
   <div class="bkrow"><label>뒷표지 쪽</label><label class="swr bkswt"><span><b>뒷표지 쪽 넣기</b><small>책 맨 끝에 뒷표지 한 쪽을 붙여요</small></span><input class="swi" type="checkbox" id="bfback" ${d.back?'checked':''} onchange="bkfRead();bkxEst()"></label></div></div>
  <div class="bkc"><h3>글꼴 <small>이 교재에만 적용돼요</small></h3><div class="bkrow"><label for="bffont">글꼴</label><select id="bffont" class="bkin" onchange="bkfRead();bkxEst()"><option value="">인쇄 설정 따라가기</option>${Object.entries(FONTS).map(([k,v])=>`<option value="${k}" ${d.font===k?'selected':''}>${esc(v[0])}</option>`).join('')}</select></div></div>
  <div class="bkc"><h3>출력 <small>문제 간격은 인쇄 창의 「옵션」에서 바꿀 수 있어요</small></h3>
   <div class="bkrow"><label>정답 · 해설</label><div class="bkctl">${seg('ans',[[0,'정답 + 해설'],[1,'정답표만'],[2,'넣지 않기']],d.ans|0)}</div></div>
   ${SUBJ==='me'?'':`<div class="bkrow"><label>제본 여백</label><div class="bkctl">${seg('gut',BKGUTS.map(([v,t])=>[v,t]),d.gut|0)}</div></div>`}
   <div class="bkrow"><label>채점 QR</label><label class="swr bkswt"><span><b>문제 쪽마다 QR 넣기</b><small>쪽 아래 QR을 찍어 바로 채점해요</small></span><input class="swi" type="checkbox" id="bfq" ${d.noqr?'':'checked'} onchange="bkfRead()"></label></div></div>`;
 const nav=`<div class="bkn">${step>1?`<button class="s" onclick="bkfStep(${step-1})">‹ 이전</button>`:'<button class="s" onclick="BKV={v:\'shelf\',id:null};render()">취소</button>'}<span style="flex:1"></span>${step<3?`<button class="p" onclick="bkfStep(${step+1})">다음 ›</button>`:'<button class="p" onclick="bkxSaveBook()">교재 만들기</button>'}</div>`;
 const side=`<aside class="bkb-side"><div class="card bkpvc"><div class="bkpvh"><b>미리보기</b><span id="bkpvc" class="m"></span></div><div class="bkpvt"><button class="on" onclick="bkfPvTab(0)">표지</button><button onclick="bkfPvTab(1)">차례</button><button onclick="bkfPvTab(2)">본문</button><button onclick="bkfPvTab(3)">정답</button>${d.back?'<button onclick="bkfPvTab(4)">뒷표지</button>':''}</div><div id="bkpv"><div id="bkpvp" class="bkpvp"></div></div><p id="bkpvs" class="m" style="margin:8px 0 0;font-size:13px"></p></div>
  <div class="card bksum"><h3 style="margin:0 0 6px;font-size:15px">요약</h3><p id="bxe" class="hint" style="margin:0"></p>${step<3?`<button class="p" style="width:100%;margin-top:10px" onclick="bkxSaveBook()">지금 이대로 교재 만들기</button>`:''}</div></aside>`;
 return `<style>.bkb{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:16px;align-items:start}.bkb-side{position:sticky;top:70px;display:flex;flex-direction:column;gap:12px}.bkc{border:1px solid var(--l);border-radius:14px;padding:16px 18px;margin:0 0 14px;background:var(--surface)}.bkc h3{margin:0 0 6px;font-size:15px}.bkc h3 small{display:block;margin-top:2px;font-weight:400;color:var(--m);font-size:12.5px}
.bkrow{display:grid;grid-template-columns:96px minmax(0,1fr);gap:8px 16px;align-items:center;padding:12px 0;border-top:1px solid var(--l)}.bkrow:first-of-type{border-top:0}.bkrow>label:first-child{font-size:13.5px;font-weight:600;color:var(--m2)}.bkctl{display:flex;flex-wrap:wrap;gap:10px}
.bkin{width:100%;box-sizing:border-box;border:1px solid var(--l2);border-radius:10px;padding:11px 13px;font:inherit;font-size:14.5px;background:var(--surface);color:inherit;min-height:44px}select.bkin{appearance:auto}
.bkseg{position:relative;display:inline-flex;background:var(--sf2);border-radius:11px;padding:3px;max-width:100%}.bkseg button{position:relative;z-index:1;flex:1 1 0;border:0;background:none;padding:9px 13px;border-radius:9px;font:inherit;font-size:13.5px;cursor:pointer;white-space:nowrap;color:var(--m2);min-height:44px;transition:color .2s}.bkseg button.on{color:var(--bd);font-weight:700}.bkseg button:focus-visible{outline:2px solid var(--b);outline-offset:1px}.bkth{position:absolute;top:3px;bottom:3px;left:3px;width:calc((100% - 6px)/var(--n));background:var(--surface);border-radius:9px;box-shadow:0 1px 3px #0002;transform:translateX(calc(var(--i)*100%));transition:transform .28s cubic-bezier(.4,0,.2,1)}
.bkswt{margin:0;padding:0;border:0}
@media(max-width:640px){.bkrow{grid-template-columns:1fr}.bkseg button{padding:9px 9px;font-size:13px}}
@media(prefers-reduced-motion:reduce){.bkth{transition:none}}
.bkb .bkh{margin:18px 0 8px;font-size:15px}.bkb .bkh small{font-weight:400;color:var(--m);font-size:12.5px;margin-left:6px}.bkb .bkfl{display:block;font-size:12px;color:var(--m);margin-bottom:3px}.bkst{cursor:pointer}.bkpre{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}.bkn{display:flex;gap:8px;margin-top:22px;padding-top:14px;border-top:1px solid var(--l)}
 .bfr{border:1px solid var(--l);border-radius:12px;padding:10px 12px;margin:6px 0;background:var(--surface)}.bfr.off{opacity:.62}.bfh{display:flex;align-items:center;justify-content:space-between;gap:8px}.bfb{display:flex;gap:8px 16px;flex-wrap:wrap;align-items:center;margin:8px 0 0}.bfmv{display:flex;gap:4px}.bflv{display:flex;gap:4px 12px;flex-wrap:wrap;align-items:center;font-size:12.5px}.bfcm{display:flex;gap:4px 14px;flex-wrap:wrap}
 .bfsw{width:44px;height:44px;border:0;background:none;cursor:pointer;padding:0;position:relative}.bfsw:after{content:"";position:absolute;inset:7px;border-radius:50%;background:var(--c);box-shadow:0 0 0 1px #0002}.bfsw.on:after{box-shadow:0 0 0 2px var(--surface),0 0 0 4px var(--c)}.bkswr{display:flex;gap:0;flex-wrap:wrap}.bfg{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px 14px}.bksubs{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:4px 12px;margin:6px 0}
 .bkcvs{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.bkcvs .bkcvb b{font-size:13px}.bkcvb{border:2px solid var(--l);border-radius:12px;background:var(--surface);padding:8px;cursor:pointer;text-align:left;font:inherit;color:inherit;min-width:0}.bkcvb.on{border-color:var(--b);background:var(--bl)}.bkcvb b{display:block;margin-top:6px;font-size:13.5px}.bkcvb small{color:var(--m);font-size:12px}.bkcvh{display:block;position:relative;width:100%;aspect-ratio:210/297;overflow:hidden;background:#fff;border:1px solid var(--l)}
 .bkpvh{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}.bkpvt{display:flex;gap:4px;margin-bottom:10px}.bkpvt button{flex:1;padding:6px 0;border:1px solid var(--l);background:var(--surface);border-radius:8px;font:inherit;font-size:13px;cursor:pointer;color:inherit}.bkpvt button.on{background:var(--b);border-color:var(--b);color:#fff;font-weight:700}.bkpvp{position:relative;width:100%;background:#fff;border:1px solid var(--l);box-shadow:0 2px 10px #0002;overflow:hidden}
 @media(max-width:980px){.bkb{grid-template-columns:1fr}.bkb-side{position:static}.bkcvs{grid-template-columns:repeat(3,1fr)}}</style>
 <div class="bkb"><div class="card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:8px"><button class="s" onclick="BKV={v:'shelf',id:null};render()" style="padding:6px 12px;border-radius:8px">‹ 교재함</button><h2 style="margin:0">교재 만들기 <small style="font-weight:400;color:var(--m);font-size:13px">${esc(SNAME[SUBJ])}</small></h2></div>${stepper}${body}${nav}</div>${side}</div>`}
const BKFD={c:'소단원별 개념 요약',o:'O/X 확인 문제',b:'빈칸 채우기',m:'하 난이도 5지선다',t:'유형별 문제 (소단원 → 유형)',e:'서술형 · 최상위 도전'};
function bkfCm(k,v){bkfRead();(BKV.d.cm[k]=BKV.d.cm[k]||{m:'d',n:10}).m=v;bkShow()}
function bkfLv(k,m){bkfRead();BKV.d.lv[k]=m;bkShow()}
function bkfShow2(){bkShow()}
const BKK={last:['직전 대비 교재','핵심 개념·OX·빈칸·대표 유형만 압축'],std:['종합 교재','개념·확인 문제·유형을 골라 한 권으로'],drill:['개념 양치기','OX · 빈칸만 전 문항 반복'],part:['특정 부분 양치기','고른 소단원만 전 문항 파고들기'],full:['전범위 모의고사','회차별로 인쇄하는 시험지']};

/* ---------- 교재 배포 (선생님 → 학생). 학생은 교재를 만들 수 없고, 배포받은 교재만 열어요. 배포 기록은 assignments(wid='bk~교재id', note=교재 설정 JSON)에 저장 ---------- */
const bkIsStud=()=>typeof STUD!=='undefined'&&!!STUD;
const bkCanDist=()=>typeof teacher==='function'&&teacher()&&!bkIsStud();
const bkDistN=id=>new Set((typeof BKDIST!=='undefined'?BKDIST:[]).filter(a=>a.wid==='bk~'+id).map(a=>a.student_id)).size;
let BKD=null;
function bkDistOpen(id){if(!bkCanDist())return;const rec=bkxAll().find(b=>b.id===id);if(!rec||rec.asg){toast('이 교재는 배포할 수 없어요');return}
 if(!(cloud()&&sess)){toast('온라인 저장에 로그인해야 학생에게 배포할 수 있어요');return}
 if(!STU.length){toast('먼저 「학생」 탭에서 학생을 등록해 주세요');return}
 BKD={id,mode:'all',cls:[],ids:[],due:''};bkDistDraw()}
function bkDistT(){const D=BKD;return D.mode==='all'?STU.slice():D.mode==='cls'?STU.filter(s=>D.cls.includes(clsName(s))):STU.filter(s=>D.ids.includes(s.id))}
function bkDistDraw(){const D=BKD;if(!D)return;const rec=bkxAll().find(b=>b.id===D.id);if(!rec)return;
 let el=document.getElementById('bkdist');if(!el){el=document.createElement('div');el.id='bkdist';el.style.cssText='position:fixed;inset:0;z-index:100;background:#0008;display:grid;place-items:center;padding:14px';el.onclick=e=>{if(e.target===el)bkDistClose()};document.body.appendChild(el)}
 const cl=clsList(),g={};STU.forEach(s=>(g[clsName(s)||'반 미지정']=g[clsName(s)||'반 미지정']||[]).push(s));
 const ts=bkDistT(),have=bkDistN(D.id);
 const mode=(v,t)=>`<button type="button" class="scb${D.mode===v?' on':''}" aria-pressed="${D.mode===v}" onclick="BKD.mode='${v}';bkDistDraw()">${t}</button>`;
 let body='';
 if(D.mode==='cls')body=`<div class="scopebar nb" style="margin-top:10px">${cl.length?cl.map(([c,n])=>`<button type="button" class="scb${D.cls.includes(c)?' on':''}" data-v="${esc(c)}" onclick="bkDistCls(this.dataset.v)">${esc(c)} <b>${n}</b></button>`).join(''):'<span class="m">학생의 「학년·반」을 입력하면 반 단위로 고를 수 있어요.</span>'}</div>`;
 if(D.mode==='pick')body=`<div style="margin-top:10px;max-height:240px;overflow:auto;display:grid;gap:4px">${Object.entries(g).sort((a,b)=>a[0].localeCompare(b[0],'ko',{numeric:true})).map(([gr,ss])=>`<div><b style="font-size:12px;color:var(--m)">${esc(gr)}</b>${ss.map(x=>`<label class="cb" style="display:flex;gap:8px;align-items:center;padding:3px 0"><input type="checkbox" ${D.ids.includes(x.id)?'checked':''} onchange="bkDistPick('${x.id}',this.checked)"> ${esc(x.name)}${bkHasDist(D.id,x.id)?' <span class="m">· 이미 배포됨</span>':''}</label>`).join('')}</div>`).join('')}</div>`;
 el.innerHTML=`<div class="card" style="max-width:520px;width:100%;max-height:92vh;overflow:auto;margin:0"><h3 style="margin:0 0 4px">학생에게 배포</h3><div class="m" style="margin-bottom:10px">「${esc(rec.name)}」을 고른 학생의 <b>교재</b> 탭에 올려요. 학생은 보기만 할 수 있어요.${have?` · 현재 <b>${have}명</b>에게 배포됨`:''}</div>
 <div class="scopebar nb">${mode('all','전체 학생 '+STU.length+'명')}${mode('cls','반 선택')}${mode('pick','직접 선택')}</div>${body}
 <div class="dsum" style="margin:10px 0">${ts.length?`<b>${ts.length}명</b>에게 배포`:'<span class="m">배포할 학생을 고르세요</span>'}</div>
 <div class="fld"><label for="bkdue">마감일 (선택)</label><input id="bkdue" type="date" value="${esc(D.due)}" onchange="BKD.due=this.value"></div>
 <div style="display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap;margin-top:12px">${have?`<button class="s" onclick="bkDistUndo()">배포 모두 취소</button>`:''}<button class="s" onclick="bkDistClose()">닫기</button><button class="p" onclick="bkDistGo()" ${ts.length?'':'disabled'}>배포하기</button></div></div>`}
const bkHasDist=(id,sid)=>(typeof BKDIST!=='undefined'?BKDIST:[]).some(a=>a.wid==='bk~'+id&&a.student_id===sid);
function bkDistCls(c){const D=BKD;D.cls=D.cls.includes(c)?D.cls.filter(x=>x!==c):D.cls.concat(c);bkDistDraw()}
function bkDistPick(id,on){const D=BKD;D.ids=D.ids.filter(x=>x!==id);if(on)D.ids.push(id);bkDistDraw()}
function bkDistClose(){const el=document.getElementById('bkdist');if(el)el.remove();BKD=null}
async function bkDistGo(){const D=BKD;if(!D)return;const rec=bkxAll().find(b=>b.id===D.id);if(!rec)return;const ts=bkDistT();if(!ts.length){toast('배포할 학생을 고르세요');return}
 const nw=ts.filter(s=>!bkHasDist(D.id,s.id));const pub={...rec};delete pub.asg;delete pub.due;delete pub.t;
 try{if(nw.length){const rows=nw.map(s=>({student_id:s.id,wid:'bk~'+D.id,title:rec.name,due:D.due||null,note:JSON.stringify({bk:pub}),t:Date.now()}));const r=await sb('/rest/v1/assignments',{method:'POST',headers:{Prefer:'return=minimal'},body:JSON.stringify(rows)});if(!r.ok)throw 0}
  await asSync();toast(nw.length?nw.length+'명에게 교재를 배포했어요'+(ts.length>nw.length?' (이미 받은 '+(ts.length-nw.length)+'명 제외)':''):'선택한 학생은 모두 이미 받았어요');bkDistClose();if(tab==='books')bkShow()}
 catch(e){toast('배포하지 못했어요. 로그인 상태와 학생 목록을 확인하세요')}}
async function bkDistUndo(){const D=BKD;if(!D||!confirm('이 교재를 배포받은 모든 학생에게서 거두어들일까요?'))return;
 try{const r=await sb('/rest/v1/assignments?wid=eq.'+encodeURIComponent('bk~'+D.id),{method:'DELETE'});if(!r.ok)throw 0;await asSync();toast('배포를 취소했어요');bkDistClose();if(tab==='books')bkShow()}catch(e){toast('배포를 취소하지 못했어요')}}
function bkNew(kind){if(bkIsStud()){toast('교재는 선생님이 만들어 배포해요');return}BKV={v:'new',id:null,step:1,d:kind==='full'?bkxPreset('full'):bkfNew(kind&&kind!=='std'?kind:'std')};render();scrollTo(0,0)}
function bkxRead(){const d=BKV.d;if(!d)return;if(d.kind==='free')return bkfRead();const g=i=>document.getElementById(i);
 if(g('bxn'))d.name=g('bxn').value;if(g('bxg'))d.gut=+g('bxg').value||0;if(g('bxs'))d.sub=g('bxs').value;
 if(g('bxl_1')){let lv=0;[['1',1],['2',2],['4',4],['8',8]].forEach(([k,b])=>{const e=g('bxl_'+k);if(e&&e.checked)lv|=b});d.lv=lv||15}
 const rdSubs=()=>{d.subs=bkSubs().map((s,i)=>g('bxs_'+i)&&g('bxs_'+i).checked?i:-1).filter(i=>i>=0);if(d.subs.length===bkSubs().length)d.subs=[]};
 if(d.kind==='full'){if(g('bxc'))d.count=Math.max(10,Math.min(60,Math.round(+g('bxc').value)||20));if(g('bxr'))d.rounds=+g('bxr').value;if(g('bxs_0'))rdSubs()}
 else{d.inc={};['concept','ox','bl','basic','type','essay'].forEach(k=>{const e=g('bxi_'+k);if(e&&e.checked)d.inc[k]=1});const a=g('bxa');if(a)d.all=a.checked?1:0;
  if(g('bxk'))d.cap=Math.max(0,Math.min(40,Math.round(+g('bxk').value)||0));
  d.subs=bkSubs().map((s,i)=>g('bxs_'+i)&&g('bxs_'+i).checked?i:-1).filter(i=>i>=0);if(d.subs.length===bkSubs().length)d.subs=[]}}
function bkxKind(k){bkxRead();const o=BKV.d,n=bkxPreset(k);const keepN=o.name!==BKK[o.kind][0]&&o.name!==bkxPreset(o.kind).name;
 if(keepN)n.name=o.name;if(o.sub&&o.sub!==bkxPreset(o.kind).sub)n.sub=o.sub;if(k!=='full'&&o.kind!=='full')n.subs=o.subs;BKV.d=n;bkShow()}
function bkxSaveBook(){bkxRead();const d=BKV.d;let nm=(d.name||'').trim();if(!nm){toast('교재 이름을 입력하세요');return}
 if(d.kind==='free'){const pts=bkfParts(d);if(!pts.length){toast('넣을 구성을 하나 이상 고르세요');return}
  if(d.pre==='part'&&!(d.subs||[]).length){toast('파고들 소단원을 하나 이상 고르세요');return}
  let id=bkxId(SUBJ,{...d,parts:pts}),cp=0;const ex=new Set(bkxAll().map(b=>b.id));while(ex.has(id)&&cp<500){cp++;id=bkxId(SUBJ,{...d,parts:pts,copy:cp.toString(36)})}
  const a=bkxAll();a.push({id,subj:SUBJ,name:nm,sub:(d.sub||'').trim(),kind:'free',gut:SUBJ==='me'?0:(d.gut||0),color:d.color||'',cover:d.cover|0,noqr:d.noqr?1:0,font:d.font||'',lf:d.lf||'solvi',lfp:d.lfp||'br',lb:d.lb||'solvi',lbp:d.lbp||'bc',back:d.back?1:0,cx:d.cx||null,t:Date.now()});bkxStore(a);
  delete BKP[id];BKV={v:'shelf',id:null};toast('교재를 만들었어요');render();scrollTo(0,0);return id}
 if(d.kind!=='full'){if(!Object.keys(d.inc||{}).length){toast('넣을 구성을 하나 이상 고르세요');return}
  if(d.kind==='part'&&!d.subs.length){toast('파고들 소단원을 하나 이상 고르세요');return}}
 const id=bkxId(SUBJ,d);const a=bkxAll().filter(b=>b.id!==id);if(d.kind==='full'&&(d.subs||[]).length&&nm===BKK.full[0])nm='범위 모의고사';a.push({id,subj:SUBJ,name:nm,sub:(d.sub||'').trim(),kind:d.kind==='last'?'std':d.kind,rounds:d.rounds||20,gut:SUBJ==='me'?0:(d.gut||0),t:Date.now()});bkxStore(a);
 delete BKP[id];Object.keys(BKP).forEach(k=>{if(k.startsWith(id+'r'))delete BKP[k]});
 BKV={v:'shelf',id:null};toast('교재를 만들었어요');render();scrollTo(0,0)}
function bkxDel(id){const b=bkxAll().find(x=>x.id===id);if(!b||b.asg||!confirm('「'+b.name+'」 교재를 삭제할까요?\n(이미 인쇄한 책의 QR은 그대로 채점돼요)'))return;
 bkxStore(bkxAll().filter(x=>x.id!==id));Object.keys(BKP).forEach(k=>{if(k===id||k.startsWith(id+'r'))delete BKP[k]});bkShow()}
function bkBuilder(){if(BKV.d&&BKV.d.kind==='free')return bkfBuilder();const d=BKV.d,subs=bkSubs();const S=bkSel();
 const chip=k=>`<button class="${d.kind===k?'p':'s'}" onclick="bkxKind('${k}')" style="text-align:left;padding:10px 12px;border-radius:10px;min-width:0"><b style="display:block;font-size:14px">${BKK[k][0]}</b><small style="font-weight:400;opacity:.8">${BKK[k][1]}</small></button>`;
 const ck=(k,l)=>`<label class="chk"><input type="checkbox" id="bxi_${k}" ${d.inc[k]?'checked':''} onchange="bkxRead();bkxEst()"> ${l}</label>`;
 const lvc=(k,b,l)=>`<label class="chk"><input type="checkbox" id="bxl_${k}" ${(d.lv||15)&b?'checked':''} onchange="bkxRead();bkxEst()"> ${l}</label>`;
 const lvBox=`<div style="margin-top:10px;font-size:13px;font-weight:700">난이도 <small style="font-weight:400;color:var(--m)">${d.kind==='full'?'뽑을 문제의 난이도':'유형 문제에 담을 난이도'}</small></div><div style="display:flex;gap:6px 16px;flex-wrap:wrap;margin:6px 0">${lvc(1,1,'하')}${lvc(2,2,'중')}${lvc(4,4,'상')}${lvc(8,8,'최상')}</div>`;
 const sel=d.subs||[],lo=sel.length?Math.min(...sel):0,hi=sel.length?Math.max(...sel):subs.length-1,hasSc=!!((CONC[SUBJ]||{}).scope||[]).length;
 const subsBox=`<div style="margin-top:10px;font-size:13px;font-weight:700">범위 · 소단원 <small style="font-weight:400;color:var(--m)">${d.kind==='part'?'파고들 부분을 고르세요':'비우면 전체 · 시작과 끝을 고르면 그 사이가 한꺼번에 선택돼요'}</small></div>
  <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:6px 0"><select id="bxr1" style="width:auto;max-width:46%">${subs.map((s,i)=>`<option value="${i}" ${i===lo?'selected':''}>${esc(s.k)} ${esc(s.name)}</option>`).join('')}</select><span>~</span><select id="bxr2" style="width:auto;max-width:46%">${subs.map((s,i)=>`<option value="${i}" ${i===hi?'selected':''}>${esc(s.k)} ${esc(s.name)}</option>`).join('')}</select><button class="s sm" onclick="bkxRange()">범위 선택</button><button class="s sm" onclick="bkxRangeSet('all')">전체</button><button class="s sm" onclick="bkxRangeSet('none')">해제</button>${hasSc?'<button class="s sm" onclick="bkxRangeSet(\'def\')">기본 범위</button>':''}</div>
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:4px 12px;margin:6px 0">${subs.map((s,i)=>`<label class="chk"><input type="checkbox" id="bxs_${i}" ${sel.includes(i)?'checked':''} onchange="bkxRead();bkxEst()"> ${esc(s.k)} ${esc(s.name)}</label>`).join('')}</div>`;
 const body=d.kind==='full'?`<div class="g2" style="margin-top:6px"><div><label style="display:block;font-size:12px;color:var(--m);margin-bottom:3px">회차당 문항 수 (10~60)</label><input type="number" id="bxc" min="10" max="60" value="${d.count}" onchange="bkxRead();bkxEst()" style="width:100%"></div><div><label style="display:block;font-size:12px;color:var(--m);margin-bottom:3px">회차 수 (최대 20)</label><select id="bxr" onchange="bkxRead()">${[5,10,15,20].map(n=>`<option ${d.rounds===n?'selected':''}>${n}</option>`).join('')}</select></div></div>
  ${lvBox}${subsBox}<p class="hint" style="margin-top:10px">회차마다 문제지와 해설을 따로 인쇄해요. 고른 범위에서(비우면 전 범위) 고르게 뽑아 100점으로 배점해요.</p>`
 :`<div style="margin-top:6px;font-size:13px;font-weight:700">구성</div><div class="chks" style="display:flex;gap:6px 16px;flex-wrap:wrap;margin:6px 0">${ck('concept','개념 정리')}${ck('ox','OX')}${ck('bl','빈칸')}${ck('basic','기초 5지선다')}${ck('type','유형 문제')}${ck('essay','서술형')}</div>
  <label class="chk" style="display:block;margin:6px 0"><input type="checkbox" id="bxa" ${d.all?'checked':''} onchange="bkxRead();bkxEst()"> <b>양치기</b> — 대표 문항만이 아니라 해당 구성의 문항을 전부 담기</label>
  ${lvBox}<div style="margin-top:6px"><label style="display:block;font-size:12px;color:var(--m);margin-bottom:3px">유형 문제 수 — 소단원마다 최대 (0이면 기본 구성대로)</label><input type="number" id="bxk" min="0" max="40" value="${d.cap||0}" onchange="bkxRead();bkxEst()" style="width:120px"></div>
  ${subsBox}`;
 return `<div class="card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:8px"><button class="s" onclick="BKV={v:'shelf',id:null};render()" style="padding:6px 12px;border-radius:8px">‹ 교재함</button><h2 style="margin:0">교재 만들기 <small style="font-weight:400;color:var(--m);font-size:13px">${esc(SNAME[SUBJ])}</small></h2></div>
 <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:10px 0">${['std','last','drill','part','full'].map(chip).join('')}</div>
 <div class="g2"><div><label style="display:block;font-size:12px;color:var(--m);margin-bottom:3px">교재 이름</label><input id="bxn" value="${esc(d.name)}" maxlength="30" oninput="bkxRead()"></div><div><label style="display:block;font-size:12px;color:var(--m);margin-bottom:3px">부제</label><input id="bxs" value="${esc(d.sub||'')}" maxlength="40" oninput="bkxRead()"></div></div>
 ${SUBJ==='me'?'':`<div style="margin-top:12px;font-size:13px;font-weight:700">제본 여백 <small style="font-weight:400;color:var(--m)">스프링·제본용. 홀수 쪽은 왼쪽, 짝수 쪽은 오른쪽 안쪽 여백을 늘려요(바깥 여백은 그만큼 줄어요)</small></div><select id="bxg" style="width:auto;margin:6px 0" onchange="bkxRead()">${BKGUTS.map(([v,t])=>`<option value="${v}" ${(d.gut||0)===v?'selected':''}>${t}</option>`).join('')}</select>`}
 ${body}<p id="bxe" class="hint" style="margin:10px 0 0"></p>
 <div style="display:flex;gap:8px;margin-top:12px"><button class="p" onclick="bkxSaveBook()">교재 만들기</button><button class="s" onclick="BKV={v:'shelf',id:null};render()">취소</button></div></div>`}
function bkxRange(){const a=+document.getElementById('bxr1').value,b=+document.getElementById('bxr2').value,lo=Math.min(a,b),hi=Math.max(a,b);bkSubs().forEach((s,i)=>{const e=document.getElementById('bxs_'+i);if(e)e.checked=i>=lo&&i<=hi});bkxRead();bkxEst()}
function bkxRangeSet(m){const sc=(CONC[SUBJ]||{}).scope||[];bkSubs().forEach((s,i)=>{const e=document.getElementById('bxs_'+i);if(e)e.checked=m==='all'?true:m==='none'?false:sc.includes(s.k)});bkxRead();bkxEst()}
function bkxEst(){const e=document.getElementById('bxe');if(!e||!BKV.d)return;const d=BKV.d;if(d.kind==='free'){e.textContent=bkfEstText(d);bkfPreview();return}
 const lvn=(d.lv&&d.lv!==15)?' · 난이도 '+[['하',1],['중',2],['상',4],['최상',8]].filter(x=>d.lv&x[1]).map(x=>x[0]).join('·'):'';
 if(d.kind==='full'){const nn=(d.subs||[]).length;e.textContent='회차당 '+d.count+'문항 · 최대 '+(d.rounds||20)+'회'+lvn+(nn?' · 범위 소단원 '+nn+'개':' · 전 범위');return}
 try{const id=bkxId(SUBJ,d);const base=DATA.filter(q=>q.sub&&q.set!=='bank'&&!q.mock);const subs=bkSubs().filter((s,i)=>!d.subs.length||d.subs.includes(i)).map(s=>s.k);const S=bkSel();
  let n=0;const inc=d.inc;subs.forEach(k=>{const f=(set,lv)=>base.filter(q=>q.sub===k&&q.set===set&&(!lv||bkLv(q)===lv)).length;
   if(d.all){if(inc.ox)n+=f('ox');if(inc.bl)n+=f('blank');if(inc.basic)n+=f('mc','하');if(inc.type)n+=base.filter(q=>q.sub===k&&(q.set==='mc'||q.set==='top')&&!(inc.basic&&bkLv(q)==='하')).length;if(inc.essay)n+=f('essay')}
   else{if(inc.ox)n+=(S.ox[k]||[]).length;if(inc.bl)n+=(S.bl[k]||[]).length;if(inc.basic)n+=(S.basic[k]||[]).length;if(inc.type)n+=S.type.filter(q=>q.sub===k).length;if(inc.essay)n+=S.essay.filter(q=>q.sub===k).length}});
  if(inc.type&&(d.cap>0||(d.lv&&d.lv!==15))){n=0;subs.forEach(k=>{const f=(set,lv)=>base.filter(q=>q.sub===k&&q.set===set&&(!lv||bkLv(q)===lv)).length;
   if(d.all){if(inc.ox)n+=f('ox');if(inc.bl)n+=f('blank');if(inc.basic&&bkLvOk({lv:'하'},d.lv))n+=f('mc','하');if(inc.essay)n+=f('essay')}
   else{if(inc.ox)n+=(S.ox[k]||[]).length;if(inc.bl)n+=(S.bl[k]||[]).length;if(inc.basic&&bkLvOk({lv:'하'},d.lv))n+=(S.basic[k]||[]).length;if(inc.essay)n+=S.essay.filter(q=>q.sub===k).length}
   let ty=d.all?base.filter(q=>q.sub===k&&(q.set==='mc'||q.set==='top')&&!(inc.basic&&bkLv(q)==='하')):S.type.filter(q=>q.sub===k);ty=ty.filter(q=>bkLvOk(q,d.lv));if(d.cap>0)ty=ty.slice(0,d.cap);n+=ty.length})}
  e.textContent='소단원 '+subs.length+'개 · 약 '+n+'문항'+lvn+(n>900?' (많아요 — 인쇄에 시간이 걸릴 수 있어요)':'')}catch(x){e.textContent=''}}
function bkLm(){try{return localStorage.getItem('omr_bklm')==='list'?'list':'card'}catch(e){return 'card'}}
function bkSetLm(v){try{localStorage.setItem('omr_bklm',v)}catch(e){}bkShow()}
function bkGoFull(){const f=bkxAll().find(b=>b.subj===SUBJ&&b.kind==='full');BKV=f?{v:'rounds',id:f.id}:{v:'new',id:null,d:bkxPreset('full')}}
function bkRounds(id){const b=bkxAll().find(x=>x.id===id);if(!b){bkClose();return ''}
 const R=Array.from({length:b.rounds||20},(_,i)=>i+1);
 return `<div class="card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:6px"><button class="s" onclick="bkClose()" style="padding:6px 12px;border-radius:8px">‹ 교재함</button><h2 style="margin:0;flex:1">${esc(b.name)}</h2><span class="bklm"><button class="${bkLm()==='card'?'p':'s'}" onclick="bkSetLm('card')">카드</button><button class="${bkLm()==='list'?'p':'s'}" onclick="bkSetLm('list')">리스트</button></span></div><p style="margin:0 0 12px;font-size:13px;color:var(--m)">${esc(b.sub||'')} · 회차마다 문제지·해설을 따로 열고 인쇄할 수 있어요.</p><div style="margin:0 0 12px"><button class="s" onclick="tab='mock';render()">표지·OMR 포함 모의고사 직접 구성 ›</button></div>
 ${bkLm()==='list'?`<div class="bkrl">${R.map(k=>`<div class="bkrr"><b>${k}회</b><span>${esc(b.name)} · ${b.id.match(/xe(\d+)/)[1]}문항</span><button class="p" onclick="bkOpen('${b.id}r${k}')">열기</button><button class="s" onclick="bkPrint('${b.id}r${k}',0)">문제지 인쇄</button><button class="s" onclick="bkPrint('${b.id}r${k}',1)">해설 포함</button></div>`).join('')}</div>`:`<div class="bkshelf">${R.map(k=>`<div class="bkcard"><div class="bkcov"><i></i><b>${k}회</b><span>${esc(b.name)}</span><em>Solvi</em></div><div class="bi2"><h3>${k}회</h3><p>${esc(SNAME[SUBJ])} · ${b.id.match(/xe(\d+)/)[1]}문항<br><small>문제지 + 해설</small></p><div class="bt2"><button class="p" onclick="bkOpen('${b.id}r${k}')">열기</button><button class="s" onclick="bkPrint('${b.id}r${k}',0)">문제지 인쇄</button><button class="s" onclick="bkPrint('${b.id}r${k}',1)">해설 포함</button></div></div></div>`).join('')}</div>`}</div>`}
window.bkShow=bkShow;
