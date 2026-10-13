/* Solvi 교재 — 개념서 · 유형서 · 실전 모의고사
   index.html 의 전역(DATA, CONC, byCode, SUBJ …)을 그대로 사용하는 보조 스크립트입니다. 교재 탭을 처음 열 때 불러옵니다.
   쪽 나눔은 books/heights.json 에 저장된 문항 높이로 계산하므로 어느 기기에서나 같은 쪽 번호가 나옵니다(QR 쪽 채점용). */
const BK_MM=96/25.4,BK_BODY=236,BK_COLW=89,BK_FULLW=186;
const BKP={},BKSELC={},BKH={};let BKHT=null,BKM=null,BKREADY=null;
const BKCIR='①②③④⑤⑥⑦⑧⑨⑩';
const bkLv=q=>q.lv0||q.lv||'';
const bkCir=a=>String(a).split(',').map(x=>BKCIR[(+x)-1]||x).join(', ');

/* ---------- 스타일 ---------- */
const BKCSS=`
.bkdoc{font-family:Pretendard,'Noto Sans CJK KR','Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;color:#111;font-weight:400;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all;overflow-wrap:break-word}
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
.bkdoc .ft .qq{width:15mm;height:15mm;display:flex;align-items:center;justify-content:center;border:.6px solid #111;padding:.8mm;background:#fff}
.bkdoc .ft .qq svg{width:100%;height:100%;display:block}
.bkdoc .ft .fn{font-size:9.5px;color:#444;text-align:right}
/* 공통 부품 */
.bkdoc .ct{background:#111;color:#fff;font-weight:800;font-size:13px;padding:1.2mm 3mm;letter-spacing:-.2px;margin:0 0 2mm;display:flex;gap:2.4mm;align-items:baseline}
.bkdoc .ct small{font-weight:500;font-size:10px;opacity:.85;margin-left:auto}
.bkdoc .ct.sm{font-size:11.5px;padding:.8mm 2.6mm}
.bkdoc .sbn{margin:0 0 4mm;padding:3.2mm 4mm 3mm;border:.6mm solid #111;border-left-width:2.4mm}
.bkdoc .sbn b{display:block;font-size:17px;font-weight:800;letter-spacing:-.4px;line-height:1.3}.bkdoc .sbn b i{font-family:inherit;font-style:normal;margin-right:2.5mm}
.bkdoc .sbn span{display:block;margin-top:1.4mm;font-size:11px;color:#333;line-height:1.5}
.bkdoc .th{margin:2mm 0 2.4mm;padding:0 0 1mm;border-bottom:.6mm solid #111;font-size:12.5px;font-weight:800;display:flex;gap:2.2mm;align-items:baseline;line-height:1.35}
.bkdoc .th b{background:#111;color:#fff;font-size:10.5px;padding:0 2mm;font-weight:700;border-radius:1px;white-space:nowrap}
.bkdoc .th small{margin-left:auto;font-weight:600;font-size:10.5px;color:#444;white-space:nowrap;letter-spacing:.5px}
/* 문항 */
.bkdoc .u.q{margin:0 0 4.6mm;font-size:12.2px;line-height:1.52}
.bkdoc .u.q .qs p{margin:0 0 1.6mm;text-align:justify}
.bkdoc .u.q .no{display:inline-block;min-width:6mm;font-weight:800;font-size:14.5px;margin-right:.6mm;letter-spacing:-.5px}
.bkdoc .u.q .pt{font-weight:700;font-size:11px;white-space:nowrap}
.bkdoc .u.q .lv{display:inline-block;margin-left:1.6mm;font-size:9px;font-weight:700;border:.5px solid #111;border-radius:2px;padding:0 1.3mm;line-height:3.5mm;vertical-align:1px;white-space:nowrap}
.bkdoc .u.q .lv.h{background:#111;color:#fff}
.bkdoc .u.q .fg{text-align:center;margin:1.6mm 0}.bkdoc .u.q .fg img{max-width:100%;max-height:62mm;height:auto}
.bkdoc .u.q .bogi,.bkdoc .u.q .bxx{border:.6px solid #111;padding:1.6mm 2.2mm;margin:2mm 0;font-size:11.8px;line-height:1.5}
.bkdoc .u.q .bogi .bt{text-align:center;font-weight:700;margin-bottom:.6mm;font-size:11.3px}
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
.bkdoc .u.o{margin:0 0 2.4mm;display:flex;gap:1.4mm;font-size:12px;line-height:1.5;align-items:flex-start}
.bkdoc .u.o .no{flex:none;width:6.4mm;font-weight:800;font-size:12.5px}
.bkdoc .u.o .tx{flex:1;text-align:justify}
.bkdoc .u.o .bx{flex:none;width:9mm;height:6mm;border:.6px solid #111;margin-left:1.2mm;align-self:center;text-align:center;line-height:5.4mm;font-size:10px;color:#888}
.bkdoc .u.o .tx .bk{display:inline-block;min-width:13mm;text-align:center;border-bottom:.6px solid #111;font-weight:700;color:#555;line-height:1.1;margin:0 .6mm}
.bkdoc .u.b .tx{line-height:1.7}
/* 해설 */
.bkdoc .u.x{margin:0 0 3.4mm;font-size:10.8px;line-height:1.5;border:.6px solid #111}
.bkdoc .u.x .xh{display:flex;gap:2mm;align-items:baseline;padding:.7mm 2mm;background:#eceff3;border-bottom:.6px solid #111}
.bkdoc .u.x .xn{font-size:12.5px;font-weight:800}.bkdoc .u.x .xa{font-weight:800;border:.6px solid #111;background:#fff;padding:0 1.6mm;font-size:10.8px}
.bkdoc .u.x .xm{margin-left:auto;font-size:9px;color:#555}
.bkdoc .u.x .xb{padding:1.2mm 2mm 1.4mm}.bkdoc .u.x .xb p{margin:.9mm 0}
.bkdoc .u.x .lb{display:inline-block;font-size:9px;font-weight:700;border:.5px solid #111;border-radius:2px;padding:0 1.2mm;margin-right:1mm;line-height:3.4mm;vertical-align:1px}
.bkdoc .u.x .ss{font-size:9px;color:#666;margin-bottom:.6mm}
.bkdoc .u.x .o{color:#111;font-weight:800}.bkdoc .u.x .x{color:#111;font-weight:800;text-decoration:line-through}
.bkdoc .u.k{margin:0 0 3.4mm}
.bkdoc .u.k .kg{display:grid;grid-template-columns:repeat(5,1fr);border-top:.6px solid #111;border-left:.6px solid #111}
.bkdoc .u.k .kg div{border-right:.6px solid #111;border-bottom:.6px solid #111;padding:.7mm 1.4mm;font-size:10.6px;line-height:1.35;display:flex;justify-content:space-between;gap:1mm}
.bkdoc .u.k .kg div b{font-weight:800}.bkdoc .u.k .kg.w3{grid-template-columns:repeat(3,1fr)}.bkdoc .u.k .kg.w2{grid-template-columns:repeat(2,1fr)}
.bkdoc .u.k .kg div span{text-align:right}
/* 개념 본문 (직전노트풍: 검정 제목 막대 · 얇은 선 · 절제된 강조) */
.bkdoc .cbk{font-size:12.4px;line-height:1.62;color:#111}
.bkdoc .cbk p{margin:0 0 1.4mm}
.bkdoc .cbk b,.bkdoc .cbk strong{font-weight:700}
.bkdoc .cbk .hl{background:linear-gradient(transparent 56%,#e6e6e6 56%);font-weight:700}
.bkdoc .cbk h4{margin:2.6mm 0 1.2mm;font-size:12.4px;font-weight:800;border-left:1.2mm solid #111;padding-left:2mm;line-height:1.35}
.bkdoc .cbk ul.l{margin:0 0 1.6mm;padding-left:4.4mm;list-style:none}.bkdoc .cbk ul.l>li{position:relative;margin:.5mm 0}
.bkdoc .cbk ul.l>li:before{content:"";position:absolute;left:-3.4mm;top:.62em;width:1.3mm;height:1.3mm;background:#111}
.bkdoc .cbk ul.l ul.l>li:before{background:#fff;border:.5px solid #111}
.bkdoc .cbk table.tb{width:100%;border-collapse:collapse;margin:1.8mm 0 2.4mm;font-size:11px;line-height:1.42}
.bkdoc .cbk table.tb th{background:#eceff3;border:.6px solid #111;padding:.7mm 1.8mm;font-weight:700;text-align:center}
.bkdoc .cbk table.tb td{border:.6px solid #111;padding:.7mm 1.8mm;text-align:center;vertical-align:middle}
.bkdoc .cbk table.tb td.l,.bkdoc .cbk table.tb th.l{text-align:left}.bkdoc .cbk table.tb td.b{font-weight:700;white-space:nowrap}
.bkdoc .cbk .nt{margin:3.6mm 0 2mm;padding:2.8mm 2.6mm 1mm;border:.6px solid #111;position:relative;break-inside:avoid}
.bkdoc .cbk .nt>.lb{display:inline-block;font-size:10px;font-weight:700;color:#fff;background:#111;padding:0 2mm;margin:-5.6mm 0 1mm;line-height:4mm}
.bkdoc .cbk .nt.wa{border-left:1.4mm solid #111;background:#f5f5f5}.bkdoc .cbk .nt.wa>.lb{background:#fff;color:#111;border:.6px solid #111}
.bkdoc .cbk .nt.ds,.bkdoc .cbk .nt.es{background:#fff}.bkdoc .cbk .nt.es{border-style:dashed}
.bkdoc .cbk .eqn{margin:1.6mm 0 2.4mm;padding:1.4mm 2mm;text-align:center;font-weight:700;border-top:.6px solid #111;border-bottom:.6px solid #111;background:#f7f7f7}
.bkdoc .cbk .eqn small{display:block;font-weight:400;font-size:.9em;color:#444}
.bkdoc .cbk .fg{margin:1.6mm 0 2.4mm;text-align:center;break-inside:avoid}.bkdoc .cbk .fg img,.bkdoc .cbk .fg svg{max-width:100%;height:auto;max-height:64mm}
.bkdoc .cbk .fg .cap{font-size:10.4px;color:#444;margin-top:.8mm}
.bkdoc .cbk .two-c{display:grid;grid-template-columns:1fr 1fr;gap:5mm;align-items:start}
.bkdoc .cbk .tag{display:inline-block;font-size:.9em;font-weight:700;border:.5px solid #111;padding:0 1.2mm;margin-right:1mm}
.bkdoc .cbk .tp{white-space:nowrap}.bkdoc .cbk .sm{font-size:.92em;color:#444}
.bkdoc .cbk .fr{display:inline-block;vertical-align:middle;text-align:center;line-height:1.12;margin:0 .6mm}
.bkdoc .cbk img{max-width:100%}
/* 표지 */
.bkdoc .cv{position:absolute;inset:12mm 14mm 12mm 14mm;border:.35mm solid #111;padding:0}
.bkdoc .cv .c1{display:flex;justify-content:space-between;align-items:center;height:11mm;border-bottom:.35mm solid #111;padding:0 5mm;font-size:11px;font-weight:600;letter-spacing:.5px}
.bkdoc .cv .c1 b{font-weight:800;letter-spacing:3px}
.bkdoc .cv .c2{position:absolute;left:12mm;right:12mm;top:62mm}
.bkdoc .cv .bar{width:16mm;height:2.2mm;background:#111;margin-bottom:9mm}
.bkdoc .cv .c2 .kd{font-size:15px;font-weight:600;letter-spacing:6px;color:#444}
.bkdoc .cv .c2 h1{margin:5mm 0 0;font-size:50px;line-height:1.12;font-weight:800;letter-spacing:-1.8px}
.bkdoc .cv .c2 h2{margin:3mm 0 0;font-size:30px;font-weight:300;letter-spacing:1px;color:#222}
.bkdoc .cv .c2 .ln{margin:12mm 0 0;border-top:.9mm solid #111;border-bottom:.25mm solid #111;height:1.5mm;width:100%}
.bkdoc .cv .c2 ul{list-style:none;margin:8mm 0 0;padding:0;font-size:13px;line-height:2}
.bkdoc .cv .c2 li{display:flex;gap:4mm;border-bottom:.2mm solid #bbb;padding:.4mm 0}.bkdoc .cv .c2 li b{width:25mm;flex:none;font-weight:700}
.bkdoc .cv .c3{position:absolute;left:12mm;right:12mm;bottom:22mm;border-collapse:collapse;width:calc(100% - 24mm);font-size:13px}
.bkdoc .cv .c3 td{border:.35mm solid #111;height:13mm;text-align:center}.bkdoc .cv .c3 td.k{width:21mm;font-weight:800;letter-spacing:3px;background:#f2f2f2}
.bkdoc .cv .c4{position:absolute;left:0;right:0;bottom:6mm;text-align:center;font-size:10.5px;color:#444;letter-spacing:.3px}
/* 차례 */
.bkdoc .toc h3{margin:0 0 5mm;font-size:21px;font-weight:800;letter-spacing:6px;text-align:center;border-bottom:.6mm solid #111;padding-bottom:3mm}
.bkdoc .toc table{width:100%;border-collapse:collapse;font-size:12.4px;line-height:1.5;margin-bottom:6mm}
.bkdoc .toc th{background:#111;color:#fff;font-weight:700;padding:1.2mm 2mm;font-size:11.5px}
.bkdoc .toc td{border-bottom:.3mm solid #999;padding:1.5mm 2mm;vertical-align:top}.bkdoc .toc td.n{text-align:center;white-space:nowrap;font-variant-numeric:tabular-nums}
.bkdoc .toc td.s{font-weight:700}
.bkdoc .toc .how{border:.35mm solid #111;padding:3.4mm 4.4mm;font-size:12px;line-height:1.75}.bkdoc .toc .how b{font-weight:800}
.bkdoc .toc .how h4{margin:0 0 1.6mm;font-size:13px;font-weight:800;letter-spacing:4px;text-align:center}
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
.bkbar{display:flex;gap:10px;align-items:center;justify-content:space-between;margin:0 auto 14px;padding:6px 10px;font-size:12.5px;color:var(--m)}
.bkbar b{color:var(--t)}.bkbar button{padding:6px 14px;border-radius:8px;font:inherit;font-size:13px}
.bkrd{position:sticky;top:0;z-index:20;background:#fff;border:1px solid var(--l);border-radius:12px;padding:8px 10px;margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
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
function bkFontCss(abs){const b=abs||'';return [[400,'Regular'],[600,'SemiBold'],[700,'Bold'],[800,'ExtraBold']].map(([w,n])=>`@font-face{font-family:Pretendard;font-weight:${w};font-display:swap;src:url(${b}fonts/Pretendard-${n}.woff2) format('woff2')}`).join('')}
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
function bkShadow(host,html){const r=host.shadowRoot||host.attachShadow({mode:'open'});r.innerHTML='<style>'+BKSH+BKCSS+'</style>'+html;return r}
function bkProbe(){let p=document.getElementById('bkprobe');if(!p){p=document.createElement('div');p.id='bkprobe';p.style.cssText='position:absolute;left:-9999px;top:0;visibility:hidden;pointer-events:none;width:300mm';document.body.appendChild(p);bkShadow(p,'<div class="bkdoc"><div id="bkpm"></div></div>')}return p.shadowRoot.getElementById('bkpm')}
function bkMeasure(html,w){const p=bkProbe();p.innerHTML='<div style="width:'+w+'mm;display:flow-root;font-size:12px;line-height:1.5">'+html+'</div>';return Math.ceil(p.firstChild.getBoundingClientRect().height/BK_MM*10)/10}
function bkH(u){const k=u.key;if(BKREC)BKREC.push(u);if(BKHT&&BKHT[k]!=null)return BKHT[k];if(BKH[k]==null)BKH[k]=bkMeasure(u.html,u.w||BK_COLW);return BKH[k]}

/* ---------- 문항 → HTML ---------- */
function bkDoc(h){return new DOMParser().parseFromString('<body>'+h+'</body>','text/html').body}
function bkChoices(root){const c=root.querySelector('.chs');if(!c)return;const t=[...c.querySelectorAll(':scope>div')].map(d=>(d.querySelector('span')||d).textContent.trim());const m=Math.max(0,...t.map(x=>x.length));c.classList.add(m<=10?'sh':m<=20?'md':'lg')}
function bkQHtml(q,no,o){o=o||{};
 const r=bkDoc(q.q);const qs=r.querySelector('.qs');if(!qs)return '<div class="u q">'+q.q+'</div>';
 const qp=r.querySelector('.qp');let pt=o.pt!=null?'['+o.pt+'점]':qp?qp.textContent:'';
 bkChoices(qs);
 const first=qs.firstElementChild;const numH='<b class="no">'+no+'</b>';
 if(first&&first.tagName==='P')first.insertAdjacentHTML('afterbegin',numH);else qs.insertAdjacentHTML('afterbegin','<p>'+numH+'</p>');
 if(pt){const kids=[...qs.children];let tgt=null;for(const k of kids){if(k.classList.contains('chs')||k.classList.contains('bogi'))break;if(k.tagName==='P')tgt=k}
  if(!tgt)tgt=kids.filter(k=>k.tagName==='P').pop();if(tgt)tgt.insertAdjacentHTML('beforeend',' <span class="pt">'+pt+'</span>')}
 if(o.lv){const f=qs.querySelector('p');if(f)f.insertAdjacentHTML('beforeend','<span class="lv'+(o.lv==='최'||o.lv==='상'?' h':'')+'">'+o.lv+'</span>')}
 if(o.ans){qs.insertAdjacentHTML('beforeend','<div class="ans"><div></div><div></div><div></div></div>')}
 return '<div class="u q" data-c="'+q.code+'">'+qs.innerHTML.replace(/ id="[^"]*"/g,'')+'</div>'}
function bkOxHtml(q,no,kind){const r=bkDoc(q.q);const qs=r.querySelector('.qs')||r;let h=qs.innerHTML.replace(/^<p>/,'').replace(/<\/p>$/,'');
 return '<div class="u o '+(kind==='bl'?'b':'')+'" data-c="'+q.code+'"><span class="no">'+no+'</span><span class="tx">'+h+'</span>'+(kind==='ox'?'<span class="bx">O / X</span>':'')+'</div>'}
function bkAnsOf(q){if(q.set==='ox')return String(q.ans).toUpperCase()==='O'?'○':'×';if(q.set==='blank')return (q.blanks||[]).map((a,k)=>'㉠㉡㉢㉣㉤'[k]+' '+a).join(' · ');if(q.set==='essay')return '';return bkCir(q.ans)}
function bkXHtml(q,no){const r=bkDoc(q.exp||'');const sol=r.querySelector('.sol')||r;sol.querySelectorAll('.sh').forEach(e=>e.remove());
 let body=sol.innerHTML;if(!r.querySelector('.sol'))body=r.innerHTML;
 const a=q.set==='essay'?'모범 답안':'정답 '+bkAnsOf(q);
 return '<div class="u x"><div class="xh"><span class="xn">'+no+'</span><span class="xa">'+a+'</span><span class="xm">'+(bkLv(q)?'난이도 '+bkLv(q):'')+'</span></div><div class="xb">'+body+'</div></div>'}

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
 subs.forEach(s=>{S.ox[s.k]=base.filter(q=>q.sub===s.k&&q.set==='ox').sort(byNo);S.bl[s.k]=base.filter(q=>q.sub===s.k&&q.set==='blank').sort(byNo)});
 const used=new Set();
 subs.forEach(s=>{const lows=base.filter(q=>q.sub===s.k&&q.set==='mc'&&bkLv(q)==='하').sort(byNo);
  const tg=new Map();lows.forEach(q=>{if(!tg.has(q.type))tg.set(q.type,[]);tg.get(q.type).push(q)});
  const pick=[];const lists=[...tg.values()];for(let i=0;pick.length<5&&i<6;i++)lists.forEach(l=>{if(pick.length<5&&l[i])pick.push(l[i])});
  pick.sort(byNo);S.basic[s.k]=pick;pick.forEach(q=>used.add(q.code))});
 const cap={me:255,cm:999}[SUBJ]||255,ecap={me:25,cm:99}[SUBJ]||25;
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
  let need=u.h;if(u.keep&&units[i+1])need+=Math.min(units[i+1].h,40);
  if(used+need>capOf()&&used>0){ci++;used=0;if(ci>=ncol)np()}
  pg.cols[ci].push(u);used+=u.h}
 return pages}
const bkU=(key,html,o)=>{const u={key:SUBJ+'|'+key,html,w:(o&&o.w)||BK_COLW,...(o||{})};u.h=bkH(u);return u};

/* ---------- 쪽 계획 ---------- */
function bkParts(id){const m=id.match(/^(me|cm)-(c|t|m\d+)$/);return m?{subj:m[1],kind:m[2]}:null}
async function bkPlan(id){
 if(BKP[id]&&BKP[id].subj===SUBJ)return BKP[id];
 await bkInit();await conceptLoad();
 const P=bkParts(id);if(!P)return null;
 const plan=P.kind==='c'?bkPlanConcept(id):P.kind==='t'?bkPlanType(id):bkPlanMock(id,P.kind.slice(1));
 plan.pages.forEach((p,i)=>p.n=i+1);
 plan.id=id;plan.subj=SUBJ;return BKP[id]=plan}
function bkPageObjs(pg,extra){return pg.cols.map(c=>c.map(u=>u.html))}
function bkQrPg(pages,k,kind,sub,label,pgs,extra){pgs.forEach(p=>{pages.push({k,kind,sub,label,cols:p.cols.map(c=>c.map(u=>u.html)),codes:p.cols.flat().map(u=>u.code).filter(Boolean),...extra})})}

function bkPlanConcept(id){
 const S=bkSel(),C=CONC[SUBJ]||{secs:[]};const pages=[{k:'cover'},{k:'toc'}];const toc=[];
 S.subs.forEach(s=>{
  const row={sub:s,c:null,ox:null,bl:null,mc:null};
  const secs=(C.secs||[]).filter(x=>x.sub===s.k);
  // 개념 정리 (한 단)
  const cu=[bkU('sb:'+SUBJ+':'+s.k+':c','<div class="u sbn"><b><i>'+esc(s.k)+'</i>'+esc(s.name)+'</b>'+(s.goal?'<span>'+esc(s.goal)+'</span>':'')+'</div>',{w:BK_FULLW,brk:true,keep:true})];
  secs.forEach(sec=>{
   cu.push(bkU('ch:'+sec.id,'<div class="u ct"><span>'+esc(sec.no)+'. '+esc(sec.title)+'</span></div>',{w:BK_FULLW,keep:true}));
   const d=bkDoc('<div class="cbk">'+sec.html+'</div>').firstElementChild;
   [...d.children].forEach((el,i)=>cu.push(bkU('cb:'+sec.id+':'+i,'<div class="u cbk">'+el.outerHTML+'</div>',{w:BK_FULLW})))});
  const cp=bkPack(cu,1,BK_BODY);row.c=pages.length+1;
  cp.forEach(p=>pages.push({k:'cn',kind:'c',sub:s,label:'개념 정리',cols:[p.cols[0].map(u=>u.html)]}));
  // OX · 빈칸 · 기초 5지선다
  [['ox','OX 확인',S.ox[s.k],'o'],['bl','빈칸 채우기',S.bl[s.k],'o'],['mc','기초 5지선다',S.basic[s.k],'q']].forEach(([kd,nm,arr,t])=>{
   if(!arr||!arr.length)return;
   const hu=bkU('h:'+kd,'<div class="u ct"><span>'+nm+'</span><small>'+esc(s.k)+' · '+arr.length+'문항</small></div>',{keep:true,brk:true});
   const us=arr.map((q,i)=>bkU(t==='q'?'q:'+q.code:'o:'+q.code+':'+kd,t==='q'?bkQHtml(q,i+1):bkOxHtml(q,i+1,kd),{code:q.code}));
   row[kd]=pages.length+1;
   bkPack([hu,...us],2,BK_BODY).forEach(p=>pages.push({k:'pr',kind:kd,sub:s,label:nm,cols:p.cols.map(c=>c.map(u=>u.html)),codes:p.cols.flat().map(u=>u.code).filter(Boolean)}))});
  toc.push(row)});
 // 정답
 const au=[];
 S.subs.forEach(s=>{
  au.push(bkU('as:'+s.k,'<div class="u sbn" style="margin-bottom:2mm"><b><i>'+esc(s.k)+'</i>'+esc(s.name)+'</b></div>',{keep:true}));
  [['ox','OX 정답',S.ox[s.k]],['bl','빈칸 정답',S.bl[s.k]]].forEach(([kd,nm,arr])=>{if(!arr||!arr.length)return;
   const cells=arr.map((q,i)=>'<div><b>'+(i+1)+'</b><span>'+(kd==='ox'?bkAnsOf(q):esc((q.blanks||[]).join(' / ')))+'</span></div>').join('');
   au.push(bkU('ak:'+kd+':'+s.k,'<div class="u k"><div class="ct sm"><span>'+nm+'</span></div><div class="kg '+(kd==='ox'?'':'w2')+'">'+cells+'</div></div>',{}))});
  const b=S.basic[s.k]||[];
  if(b.length){au.push(bkU('ak:mc:'+s.k,'<div class="u k"><div class="ct sm"><span>기초 5지선다 정답</span></div><div class="kg">'+b.map((q,i)=>'<div><b>'+(i+1)+'</b><span>'+bkCir(q.ans)+'</span></div>').join('')+'</div></div>',{}));
   b.forEach((q,i)=>au.push(bkU('x:'+q.code,bkXHtml(q,i+1),{})))}});
 const ap=bkPack(au,2,BK_BODY);const aStart=pages.length+1;
 ap.forEach(p=>pages.push({k:'ak',kind:'a',label:'정답 · 해설',cols:p.cols.map(c=>c.map(u=>u.html))}));
 return {kind:'c',title:SNAME[SUBJ]+' 개념서',short:'개념서',pages,toc,aStart,sel:S}}

function bkPlanType(id){
 const S=bkSel();const pages=[{k:'cover'},{k:'toc'}];const toc=[];let no=0;const nums=new Map();
 S.subs.forEach(s=>{
  const qs=S.type.filter(q=>q.sub===s.k);if(!qs.length)return;
  const units=[bkU('sb:'+SUBJ+':'+s.k+':t','<div class="u sbn"><b><i>'+esc(s.k)+'</i>'+esc(s.name)+'</b><span>'+qs.length+'문항 · 유형별로 묶고 난이도 순으로 배열</span></div>',{brk:true,keep:true})];
  let cur=null,ti=0;
  qs.forEach(q=>{if(q.type!==cur){cur=q.type;ti++;const grp=qs.filter(x=>x.type===cur);const av=grp.reduce((a,x)=>a+LVI[bkLv(x)],0)/grp.length;const st='★'.repeat(Math.max(1,Math.round(av)+1))+'☆'.repeat(4-Math.max(1,Math.round(av)+1));
    units.push(bkU('th:'+s.k+':'+ti+':'+cur,'<div class="th"><b>유형 '+String(ti).padStart(2,'0')+'</b><span>'+esc(cur)+'</span><small>'+st+'</small></div>',{keep:true}))}
   no++;nums.set(q.code,no);units.push(bkU('q:'+q.code,bkQHtml(q,no,{lv:bkLv(q)}),{code:q.code}))});
  const row={sub:s,n:qs.length,p:pages.length+1};toc.push(row);
  bkPack(units,2,BK_BODY).forEach(p=>pages.push({k:'pr',kind:'t',sub:s,label:'유형 문제',cols:p.cols.map(c=>c.map(u=>u.html)),codes:p.cols.flat().map(u=>u.code).filter(Boolean)}))});
 // 서술형
 if(S.essay.length){const eu=[bkU('sb:es','<div class="u sbn"><b><i>서술형</i>서술형 · 최상위 도전</b><span>풀이 과정을 서술하시오 (자기 채점)</span></div>',{brk:true,keep:true})];
  S.essay.forEach((q,i)=>{no++;nums.set(q.code,no);eu.push(bkU('q:'+q.code+':e',bkQHtml(q,no,{ans:1}),{code:q.code}))});
  toc.es={n:S.essay.length,p:pages.length+1};
  bkPack(eu,2,BK_BODY).forEach(p=>pages.push({k:'es',kind:'e',label:'서술형',cols:p.cols.map(c=>c.map(u=>u.html))}))}
 // 정답·해설
 const au=[];
 S.subs.forEach(s=>{const qs=S.type.filter(q=>q.sub===s.k);if(!qs.length)return;
  au.push(bkU('as:'+s.k,'<div class="u sbn" style="margin-bottom:2mm"><b><i>'+esc(s.k)+'</i>'+esc(s.name)+'</b></div>',{keep:true}));
  au.push(bkU('akt:'+s.k,'<div class="u k"><div class="ct sm"><span>빠른 정답</span></div><div class="kg">'+qs.map(q=>'<div><b>'+nums.get(q.code)+'</b><span>'+bkCir(q.ans)+'</span></div>').join('')+'</div></div>',{}));
  qs.forEach(q=>au.push(bkU('x:'+q.code,bkXHtml(q,nums.get(q.code)),{})))});
 if(S.essay.length){au.push(bkU('as:es','<div class="u sbn" style="margin-bottom:2mm"><b><i>서술형</i>모범 답안</b></div>',{keep:true}));S.essay.forEach(q=>au.push(bkU('x:'+q.code,bkXHtml(q,nums.get(q.code)),{})))}
 const aStart=pages.length+1;
 bkPack(au,2,BK_BODY).forEach(p=>pages.push({k:'ak',kind:'a',label:'정답 · 해설',cols:p.cols.map(c=>c.map(u=>u.html))}));
 return {kind:'t',title:SNAME[SUBJ]+' 유형서',short:'유형서',pages,toc,aStart,sel:S,total:no}}

function bkPlanMock(id,rd){
 const M=BKM&&BKM[rd];if(!M)return {kind:'m',title:'모의고사',short:'모의고사',pages:[{k:'cover'}],toc:[]};
 const qs=M.codes.map(c=>byCode[c]).filter(Boolean);const pages=[{k:'mcv'}];
 const us=qs.map((q,i)=>bkU('mq:'+q.code,bkQHtml(q,i+1,{pt:M.pts[q.code]}),{code:q.code}));
 const pp=bkPack(us,2,BK_BODY,BK_BODY-19);const nq=pp.length;
 pp.forEach((p,i)=>pages.push({k:'mq',kind:'q',label:'문제지',idx:i+1,of:nq,first:i===0,cols:p.cols.map(c=>c.map(u=>u.html)),codes:p.cols.flat().map(u=>u.code).filter(Boolean)}));
 // 정답·해설 : 새 레이아웃
 const exu=qs.map((q,i)=>{const e=M.ex[q.code]||{};const lines=(e.core&&!/^<b>/.test(e.core)?[e.core]:[]).concat(e.ch||[]);const items=lines.map(t=>{const m=t.match(/<span class="(o|x)">/);if(!m)return '<li class="sm"><i style="visibility:hidden">·</i><span>'+t+'</span></li>';const ok=m[1]==='o';return '<li><i class="'+(ok?'':'x')+'">'+(ok?'○':'×')+'</i><span>'+t.replace(/<span class="[ox]">[^<]*<\/span>\s*/,'')+'</span></li>'}).join('');
  const html='<div class="u ex"><div class="rl"><b>'+(i+1)+'</b><span>'+bkCir(q.ans)+'</span></div><div class="rb">'+(e.core&&/^<b>/.test(e.core)?'<div class="core">'+e.core.replace(/<b>([^<]*)<\/b>\s*:\s*/,'<b>$1</b> ')+'</div>':'')+(items?'<ul>'+items+'</ul>':'')+'<div class="ft2"><b>개념</b> '+esc(e.need||'')+' <br><b>복습</b> '+esc(e.rv||'')+'</div></div></div>';
  return bkU('mx:'+q.code,html,{})});
 // 요약(정답표)용 높이: 1쪽에 고정 블록
 const sumH=118;const xp=bkPack(exu,2,BK_BODY,BK_BODY-sumH);
 xp.forEach((p,i)=>pages.push({k:'ma',kind:'a',label:'정답 및 해설',idx:i+1,of:xp.length,first:i===0,cols:p.cols.map(c=>c.map(u=>u.html))}));
 return {kind:'m',rd,title:M.title,short:rd+'회 모의고사',pages,toc:[],M,qs,aStart:nq+2,nq}}

/* ---------- 쪽 HTML ---------- */
const BKCAP=BK_BODY;
function bkBase(){return ((typeof CF!=='undefined'&&CF&&CF.pub)||location.href).split('#')[0].split('?')[0]}
function bkUrl(plan,p){return bkBase()+'#bk='+plan.id+':'+p.n}
function bkHd(l,r,b){return '<div class="hd"><span class="t1">'+l+'</span><span class="t2">'+r+'<b>'+b+'</b></span></div>'}
function bkFt(plan,p,o){o=o||{};const qr=p.codes&&p.codes.length;
 return '<div class="ft"><span class="fl">'+(o.left||'Solvi · '+esc(plan.title))+'</span><span class="pn">'+(o.pn!=null?o.pn:p.n)+'</span>'+
  (qr?'<div class="fr2"><div class="qt"><b>이 쪽 채점</b>QR을 스캔하세요</div><div class="qq">'+qrSvg(bkUrl(plan,p))+'</div></div>':o.right?'<div class="fr2"><span class="fn">'+o.right+'</span></div>':'<div></div>')+'</div>'}
function bkCover(plan){
 const kd=plan.kind==='c'?'개념서':'유형서';const S=plan.sel;
 const rows=plan.kind==='c'?[['개념','단원별 핵심 개념 정리'],['OX · 빈칸','개념을 바로 확인'],['기초 5지선다','기본 문항으로 마무리'],['정답·해설','맨 뒤 정답과 해설']]
  :[['구성','소단원 → 유형 → 난이도 순'],['문항 수','총 '+(plan.total||0)+'문항 (서술형 포함)'],['채점','쪽마다 QR로 바로 채점'],['정답·해설','맨 뒤 정답과 해설']];
 return '<div class="cv"><div class="c1"><span>Solvi · 과학</span><b>SERIES</b><span>'+esc(SNAME[SUBJ])+'</span></div><div class="c2"><div class="bar"></div><div class="kd">'+(plan.kind==='c'?'CONCEPT BOOK':'TYPE BOOK')+'</div><h1>'+esc(SNAME[SUBJ])+'</h1><h2>'+kd+'</h2><div class="ln"></div><ul>'+rows.map(r=>'<li><b>'+r[0]+'</b><span>'+r[1]+'</span></li>').join('')+'</ul></div>'+
  '<table class="c3"><tr><td class="k">학 년</td><td></td><td class="k">반</td><td></td><td class="k">번 호</td><td></td><td class="k">이 름</td><td style="width:36mm"></td></tr></table><div class="c4">문제 쪽 아래 QR을 스캔하면 그 쪽을 바로 채점할 수 있습니다</div></div>'}
function bkToc(plan){
 let h='<div class="toc"><h3>차 례</h3>';
 if(plan.kind==='c'){
  h+='<table><tr><th>소단원</th><th>개념 정리</th><th>OX</th><th>빈칸</th><th>기초 5지선다</th></tr>'+plan.toc.map(r=>'<tr><td class="s">'+esc(r.sub.k)+' '+esc(r.sub.name)+'</td><td class="n">'+(r.c||'')+'</td><td class="n">'+(r.ox||'')+'</td><td class="n">'+(r.bl||'')+'</td><td class="n">'+(r.mc||'')+'</td></tr>').join('')+'<tr><td class="s">정답 · 해설</td><td class="n" colspan="4">'+plan.aStart+'</td></tr></table>';
  h+='<div class="how"><h4>이 책의 활용법</h4>① 개념 정리를 읽고 <b>굵은 글씨와 표시된 부분</b>을 중심으로 정리한다.<br>② OX와 빈칸으로 개념을 바로 확인한다.<br>③ 기초 5지선다로 기본 문항을 풀고 맨 뒤 해설로 확인한다.<br>④ 문제 쪽 아래 <b>QR을 스캔</b>하거나 솔비 앱의 「교재」 탭에서 쪽을 골라 채점한다.</div>'}
 else{
  h+='<table><tr><th>소단원</th><th>문항 수</th><th>쪽</th></tr>'+plan.toc.map(r=>'<tr><td class="s">'+esc(r.sub.k)+' '+esc(r.sub.name)+'</td><td class="n">'+r.n+'</td><td class="n">'+r.p+'</td></tr>').join('')+(plan.toc.es?'<tr><td class="s">서술형</td><td class="n">'+plan.toc.es.n+'</td><td class="n">'+plan.toc.es.p+'</td></tr>':'')+'<tr><td class="s">정답 · 해설</td><td class="n"></td><td class="n">'+plan.aStart+'</td></tr></table>';
  h+='<div class="how"><h4>이 책의 활용법</h4>① 소단원마다 <b>유형</b>으로 묶여 있고, 유형 안에서는 <b>쉬운 문제 → 어려운 문제</b> 순으로 배열되어 있다.<br>② 난이도 표시 <b>[하] [중] [상] [최]</b>를 보고 막히는 구간부터 다시 풀어 본다.<br>③ 한 쪽을 풀 때마다 아래 <b>QR을 스캔</b>해 채점하고, 틀린 유형은 솔비의 취약 유형 분석으로 확인한다.<br>④ 서술형은 맨 뒤 모범 답안과 비교해 스스로 채점한다.</div>'}
 return h+'</div>'}
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
 const p=plan.pages[i],S=esc(SNAME[SUBJ]);
 if(p.k==='cover')return '<div class="bp">'+bkCover(plan)+'</div>';
 if(p.k==='toc')return '<div class="bp">'+bkHd(S+'<em>'+plan.short+'</em>','','차례')+'<div class="bd one">'+bkToc(plan)+'</div>'+bkFt(plan,p)+'</div>';
 const hd=bkHd(S+'<em>'+esc(plan.short)+'</em>',(p.sub?esc(p.sub.k)+' · ':'')+esc(p.label||''),p.n);
 if(p.k==='cn')return '<div class="bp">'+hd+'<div class="bd one">'+p.cols[0].join('')+'</div>'+bkFt(plan,p)+'</div>';
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
 // pr, es, ak
 return '<div class="bp">'+hd+'<div class="bd"><div class="cols">'+p.cols.map(c=>'<div class="col">'+c.join('')+'</div>').join('')+'</div></div>'+bkFt(plan,p,p.k==='es'?{right:'서술형은 모범 답안과 비교해 스스로 채점'}:{})+'</div>'}

/* ---------- 채점 · 경로 ---------- */
async function bkGradePage(id,n){
 if(needLogin()){askLogin('BK:'+id+':'+n);return}
 await bkInit();const P=bkParts(id);if(!P)return;
 if(P.subj!==SUBJ)await setSubject(P.subj);
 await conceptLoad();const plan=await bkPlan(id);const p=plan&&plan.pages.find(x=>x.n===+n);
 if(!p||!p.codes||!p.codes.length){toast('이 쪽에는 채점할 문제가 없어요');return}
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
let BKV={v:'shelf',id:null};
function bkBookList(){const S=bkSel();const L=[
 {id:SUBJ+'-c',name:'개념서',sub:'개념 정리 · OX · 빈칸 · 기초 5지선다',meta:'OX '+Object.values(S.ox).reduce((a,x)=>a+x.length,0)+' · 빈칸 '+Object.values(S.bl).reduce((a,x)=>a+x.length,0)+' · 기초 '+Object.values(S.basic).reduce((a,x)=>a+x.length,0)+'문항'},
 {id:SUBJ+'-t',name:'유형서',sub:'소단원 → 유형 → 난이도별 문제 (N제)',meta:'객관식·단답형 '+S.type.length+' · 서술형 '+S.essay.length+'문항'}];
 if(SUBJ==='cm'&&BKM)Object.keys(BKM).forEach(k=>L.push({id:'cm-m'+k,name:k+'회 실전 모의고사',sub:BKM[k].kind+' · '+BKM[k].codes.length+'문항 · '+BKM[k].time,meta:'문제지 · 정답표 · 해설',mock:1}));
 return L}
async function bkShow(){
 await bkInit();await conceptLoad();
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
function bkGroups(plan){const g=new Map();plan.pages.forEach(p=>{if(!p.codes||!p.codes.length)return;const k=plan.kind==='m'?'문제지':((p.sub?p.sub.k+' ':'')+(p.label||''));if(!g.has(k))g.set(k,[]);g.get(k).push(p)});return g}
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
function bkScale(){const w=document.getElementById('bkpages');if(!w)return;const W=w.clientWidth;const s=Math.min(1,W/(210*BK_MM));w.style.setProperty('--bks',s.toFixed(4));w.style.setProperty('--bkw',(210*BK_MM*s)+'px');w.style.setProperty('--bkh',(297*BK_MM*s)+'px')}
async function bkReader(id){
 const m=$('#main');m.innerHTML='<div class="card">'+ldg('책을 펴는 중…')+'</div>';
 const plan=await bkPlan(id);if(!plan){bkClose();return}
 const jumps=[];if(plan.kind==='c'){plan.toc.forEach(r=>{jumps.push([r.sub.k+' '+r.sub.name+' · 개념',r.c]);if(r.ox)jumps.push(['　'+r.sub.k+' OX',r.ox]);if(r.bl)jumps.push(['　'+r.sub.k+' 빈칸',r.bl]);if(r.mc)jumps.push(['　'+r.sub.k+' 기초 5지선다',r.mc])})}
 else if(plan.kind==='t'){plan.toc.forEach(r=>jumps.push([r.sub.k+' '+r.sub.name,r.p]));if(plan.toc.es)jumps.push(['서술형',plan.toc.es.p])}
 else{jumps.push(['문제지',2],['정답 및 해설',plan.aStart])}
 jumps.push(['정답 · 해설',plan.aStart]);const seen=new Set();const J=jumps.filter(j=>j[1]&&!seen.has(j[0]+j[1]) && seen.add(j[0]+j[1]));
 m.innerHTML=`<div class="bkrd"><button onclick="bkClose()">‹ 교재함</button><b style="font-size:14px">${esc(plan.title)}</b><select id="bkj" onchange="bkJump(this.value)"><option value="">이동…</option><option value="1">표지</option>${J.map(j=>`<option value="${j[1]}">${esc(j[0])} · p.${j[1]}</option>`).join('')}</select>${plan.kind==='m'?`<button class="p" onclick="bkGradeAll('${id}')">시험 전체 채점</button>`:''}<button onclick="bkPrint('${id}',0)">문제만 인쇄</button><button class="p" onclick="bkPrint('${id}',1)">전체 인쇄 · PDF</button></div><div id="bkpages"></div>`;
 const box=$('#bkpages');bkScale();
 box.innerHTML=plan.pages.map((p,i)=>`<div class="bkw" id="bkpg${p.n}" data-i="${i}" style="width:var(--bkw);height:var(--bkh)"></div>`+(p.codes&&p.codes.length?`<div class="bkbar" style="width:var(--bkw)"><span><b>p.${p.n}</b> · ${p.codes.length}문항</span><button class="p" onclick="bkGradePage('${id}',${p.n})">이 쪽 채점하기</button></div>`:'<div style="height:10px"></div>')).join('');
 const fill=el=>{if(el.dataset.f)return;el.dataset.f=1;bkShadow(el,'<div class="bkdoc scr">'+bkPageHtml(plan,+el.dataset.i)+'</div>')};
 if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){fill(e.target);io.unobserve(e.target)}}),{rootMargin:'900px 0px'});box.querySelectorAll('.bkw').forEach(e=>io.observe(e))}
 else box.querySelectorAll('.bkw').forEach(fill);
 if(!window._bkrs){window._bkrs=1;addEventListener('resize',()=>{if(tab==='books'&&BKV.v==='read')bkScale()})}}
function bkJump(n){const e=document.getElementById('bkpg'+n);if(e){const y=e.getBoundingClientRect().top+scrollY-64;scrollTo({top:y,behavior:'smooth'})}const s=$('#bkj');if(s)s.value=''}

/* ---------- 인쇄 ---------- */
function bkDocHtml(plan,all){
 const abs=location.origin+location.pathname.replace(/[^/]*$/,'');
 const n=all?plan.pages.length:Math.max(1,(plan.aStart||plan.pages.length+1)-1);
 let pg='';for(let i=0;i<n;i++)pg+=bkPageHtml(plan,i);
 return '<!doctype html><html><head><meta charset="utf-8"><title>'+esc(plan.title)+'</title><style>'+bkFontCss(abs)+'@page{size:A4;margin:0}html,body{margin:0;padding:0;background:#fff}'+BKCSS+'.bkdoc .bp{page-break-after:always;break-after:page}.bkdoc .bp:last-child{page-break-after:auto;break-after:auto}</style></head><body class="bkdoc">'+pg+'</body></html>'}
async function bkPrint(id,all){
 await bkInit();const P=bkParts(id);if(P&&P.subj!==SUBJ)await setSubject(P.subj);
 busyRun('인쇄할 책을 만드는 중…',async()=>{await conceptLoad();const plan=await bkPlan(id);if(!plan)return;await cbPrintHtml(bkDocHtml(plan,all))})}

/* ---------- 높이표 만들기(개발용) : 콘솔/자동화에서 await bkMeasureAll() ---------- */
let BKREC=null;
async function bkMeasureAsync(html,w){const p=bkProbe();p.innerHTML='<div style="width:'+w+'mm;display:flow-root;font-size:12px;line-height:1.5">'+html+'</div>';
 await Promise.all([...p.querySelectorAll('img')].map(i=>i.complete&&i.naturalWidth?1:new Promise(r=>{i.onload=i.onerror=()=>r();setTimeout(r,30000)})));
 return Math.ceil(p.firstChild.getBoundingClientRect().height/BK_MM*10)/10}
async function bkMeasureAll(){
 await bkInit();BKHT={};const subj=SUBJ;const ids=[subj+'-c',subj+'-t',...(BKM&&subj==='cm'?Object.keys(BKM).map(k=>'cm-m'+k):[])];
 BKREC=[];for(const id of ids){delete BKP[id];await bkPlan(id)}
 const rec=BKREC;BKREC=null;
 for(const u of rec){BKH[u.key]=await bkMeasureAsync(u.html,u.w||BK_COLW)}
 for(const id of ids)delete BKP[id];
 for(const id of ids)await bkPlan(id);
 return BKH}
window.bkShow=bkShow;
