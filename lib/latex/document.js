(function(g,f){const a=f();if(typeof module==='object'&&module.exports)module.exports=a;else g.SolviLatexDocument=a})(globalThis,function(){
'use strict';
const R=String.raw;
const ESC={'\\':R`\textbackslash{}`,'{':R`\{`,'}':R`\}`,'$':R`\$`,'&':R`\&`,'#':R`\#`,'%':R`\%`,'_':R`\_`,'~':R`\textasciitilde{}`,'^':R`\textasciicircum{}`};
function text(s){return Array.from(String(s??'')).filter(c=>c==='\n'||c==='\t'||c.charCodeAt(0)>=32).map(c=>ESC[c]||(/[㉠-㉻ⓐ-ⓩⒶ-Ⓩ]/.test(c)?R`\solvimark{`+c+'}':c)).join('')}
const SYMBOLS={'−':'-','×':R`\times `,'÷':R`\div `,'≤':R`\le `,'≥':R`\ge `,'≠':R`\ne `,'∞':R`\infty `,'∑':R`\sum `,'∫':R`\int `,'∈':R`\in `,'∉':R`\notin `,'∪':R`\cup `,'∩':R`\cap `,'⋅':R`\cdot `,'·':R`\cdot `,'→':R`\to `,'⇒':R`\Rightarrow `,'±':R`\pm `,'≈':R`\approx `,'α':R`\alpha `,'β':R`\beta `,'θ':R`\theta `,'π':R`\pi `,'σ':R`\sigma `,'λ':R`\lambda `,'μ':R`\mu `,'Δ':R`\Delta `,'∅':R`\emptyset `,'ℝ':R`\mathbb{R}`,'{':R`\{`,'}':R`\}`};
function math(n,d=0){if(d>60)throw Error('수식 중첩 한도');const t=n.tag,a=(n.children||[]).map(c=>math(c,d+1)),v=Array.from(n.text||'',c=>SYMBOLS[c]||text(c)).join('');
 if(t==='mtext')return R`\text{`+text(n.text||'')+'}'+a.join('');
 if(['math','mrow','mi','mn','mo','mstyle','mpadded','span'].includes(t))return v+a.join('');
 const arity={mfrac:2,msup:2,msub:2,msubsup:3,mroot:2,mover:2,munder:2,munderover:3};if(arity[t]&&a.length!==arity[t])throw Error('수식 피연산자 오류');
 if(t==='mfrac')return R`\frac{`+a[0]+'}{'+a[1]+'}';
 if(t==='msup')return '{'+a[0]+'}^{'+a[1]+'}';if(t==='msub')return '{'+a[0]+'}_{'+a[1]+'}';
 if(t==='msubsup'||t==='munderover')return '{'+a[0]+'}_{'+a[1]+'}^{'+a[2]+'}';
 if(t==='msqrt')return R`\sqrt{`+a.join('')+'}';if(t==='mroot')return R`\sqrt[`+a[1]+']{'+a[0]+'}';
 if(t==='mover')return R`\overset{`+a[1]+'}{'+a[0]+'}';if(t==='munder')return R`\underset{`+a[1]+'}{'+a[0]+'}';
 if(t==='mtable')return R`\begin{matrix}`+a.join(R`\\`)+R`\end{matrix}`;if(t==='mtr')return a.join(' & ');if(t==='mtd')return a.join('');if(t==='mspace')return R`\, `;
 if(t==='mfenced'){const o=n.open||'(',c=n.close||')';if(!'([{|'.includes(o)||!')]}|'.includes(c))throw Error('수식 괄호 오류');return R`\left`+(SYMBOLS[o]||o)+a.join(',')+R`\right`+(SYMBOLS[c]||c)}
 throw Error('지원하지 않는 수식: '+t);
}
function table(n,d){const rows=[];let caption='';const walk=ns=>ns.forEach(c=>{if(c.tag==='tr')rows.push(c);else if(['tbody','thead','tfoot'].includes(c.tag))walk(c.children||[]);else if(c.tag==='caption')caption=node(c,d+1);else throw Error('지원하지 않는 표 요소')});walk(n.children||[]);if(!rows.length)return '';
 const occupied=[];let width=0;const grid=[];
 rows.forEach((r,ri)=>{let ci=0;const cells=[];for(const c of r.children||[]){while((occupied[ci]||0)>ri){cells[ci]='';ci++}const cs=+(c.colspan||1),rs=+(c.rowspan||1);if(!Number.isInteger(cs)||!Number.isInteger(rs)||cs<1||cs>12||rs<1||rs>100)throw Error('표 병합 범위 오류');let value=node(c,d+1);if(rs>1)value=R`\multirow{`+rs+'}{*}{'+value+'}';if(cs>1)value=R`\multicolumn{`+cs+'}{|c|}{'+value+'}';cells[ci]=value;for(let i=0;i<cs;i++){if(i)cells[ci+i]=null;occupied[ci+i]=ri+rs}ci+=cs}while((occupied[ci]||0)>ri){cells[ci]='';ci++}width=Math.max(width,ci);grid.push(cells)});
 if(width>12)throw Error('표 열 한도');const out=grid.map(cs=>{while(cs.length<width)cs.push('');return cs.filter(c=>c!==null).join(' & ')+R`\\\hline`});
 return '\n'+R`\par {\centering `+caption+R`\par}\smallskip\noindent\begin{tabularx}{\linewidth}{|`+Array(width).fill('X').join('|')+R`|}\hline `+out.join('\n')+R`\end{tabularx}\par`+'\n';
}
function node(n,d=0){if(!n||typeof n!=='object'||d>60)throw Error('문서 구조 한도');const t=n.tag||'span';if(t==='math')return R`\(`+math(n)+R`\)`;if(t==='table')return table(n,d);
 if(t==='img'){if(!/^a\d+\.png$/.test(n.asset))throw Error('그림 경로 오류');return R`\par\begin{center}\includegraphics[width=\linewidth,height=62mm,keepaspectratio]{`+n.asset+R`}\end{center}`}
 const b=text(n.text||'')+(n.children||[]).map(c=>node(c,d+1)).join('');
 if(['span','small','label','td','th','caption','a','figure','figcaption'].includes(t))return b;
 if(['div','section','article','p','li'].includes(t))return '\n'+R`\par `+b+'\n'+R`\par`+'\n';
 if(['h1','h2','h3','h4','h5','h6'].includes(t))return R`\par\medskip{\KoBold `+b+R`}\par\smallskip`;
 if(t==='b'||t==='strong')return /^[㉠-㉻ㄱ-ㅎ]$/.test(n.text||'')?R`\uline{`+b+'}':R`\textbf{`+b+'}';if(t==='i'||t==='em')return R`\emph{`+b+'}';if(t==='u')return R`\uline{`+b+'}';
 if(t==='s')return R`\sout{`+b+'}';
 if(t==='sub')return R`\textsubscript{`+b+'}';if(t==='sup')return R`\textsuperscript{`+b+'}';if(t==='br')return R`\leavevmode\newline `+'\n';if(t==='hr')return R`\par\smallskip\hrule\smallskip `;
 if(t==='ul'||t==='ol')return R`\begin{itemize}`+(n.children||[]).map(c=>R`\item `+node(c,d+1)).join('\n')+R`\end{itemize}`;
 if(t==='fraction'){const a=n.children||[];if(a.length!==2)throw Error('분수 구조 오류');return R`\(\dfrac{\text{`+node(a[0],d+1)+R`}}{\text{`+node(a[1],d+1)+R`}}\)`}
 if(t==='choices-list'){
  const children=(n.children||[]).filter(c=>!(c.tag==='span'&&!c.children?.length&&!String(c.text||'').trim()));
  if(!children.length||children.length>20)throw Error('선지 개수를 확인해 주세요');
  const choices=children.map(c=>{const parts=(c.children||[]).slice();if(parts[0]&&['b','strong'].includes(parts[0].tag)&&/^[①-⑳]$/.test(parts[0].text||''))parts.shift();return (parts.map(x=>node(x,d+1)).join('')||text(c.text||'')).replace(/\\\(/g,R`\(\displaystyle `)});
  if(choices.length===5)return '\\'+(n.layout==='vertical'?'examoptsvertical':'examoptsauto')+choices.map(s=>'{'+s+'}').join('');
  return R`\par\vspace{2.9mm}`+choices.map((s,i)=>R`\solvioption{`+(i+1)+'}{'+s+'}').join('\n')+R`\vspace{2.5mm}`;
 }
 if(t==='question-number')return R`{\KoMed\fontsize{14.2}{18}\selectfont `+b+R`.}\hspace{1.2mm}`;if(t==='points')return R`\hfill{\fontsize{8.5}{10.5}\selectfont `+b+'}';if(t==='question-head')return R`\par\noindent `+b+R`\par\nobreak\vspace{3.4mm}\nobreak`;
 if(t==='unit'){
  if(!/^[-A-Za-z0-9_.~]{1,150}$/.test(n.code||''))throw Error('문항 코드 오류');
  if(n.allowBreak)return R`\par `+(n.header||'')+b+R`\par\vspace{3.6mm}\hrule height .2pt `;
  const content=R`\write16{SOLVICODE:\thepage:`+n.code+'}'+(Number.isInteger(n.number)?R`\write16{SOLVINUM:\thepage:`+n.code+':'+n.number+'}':'')+(n.header||'')+b+R`\write16{SOLVIEND:\thepage:`+n.code+'}';
  if(n.slotHeight){if(!Number.isFinite(n.slotHeight)||n.slotHeight<=0||n.slotHeight>235)throw Error('문항 칸 높이 오류');return R`\noindent\begingroup\setbox2=\vbox{\hsize=\linewidth\solvibodyfont\setlength{\parskip}{0pt} `+content+R`}\typeout{SOLVIMEASURE:`+n.code+R`:\the\dimexpr\ht2+\dp2\relax}\begin{minipage}[t][`+n.slotHeight.toFixed(4)+R`mm][t]{\linewidth}\vspace{0pt}\unvbox2\end{minipage}\endgroup\par\nointerlineskip`}
  return questionBox(content,n.minimum||0,n.code);
 }
 if(t==='quick-answers')return b;if(t==='quick-title')return R`\par\vspace*{5mm}{\centering\KoBold\fontsize{17}{23}\selectfont `+b+R`\par}\vspace{4mm}`;
 if(t==='answer-grid'){const cells=(n.children||[]).map(c=>R`\begin{tabular}{@{}c@{}}`+(c.children||[]).map(x=>node(x,d+1)).join(R`\\[1mm]`)+R`\end{tabular}`),rows=[];for(let i=0;i<cells.length;i+=5){const row=cells.slice(i,i+5);while(row.length<5)row.push('');rows.push(row.join(' & ')+R`\\[1.5mm]\hline`)}return R`\par\begin{center}\fontsize{10.7}{18}\selectfont\renewcommand{\arraystretch}{1.65}\begin{tabular}{|*{5}{c|}}\hline `+rows.join('\n')+R`\end{tabular}\end{center}\vspace{7mm}`}
 if(t==='passage')return (n.heading?R`\par\noindent{\fontsize{9.6}{15}\selectfont `+node(n.heading,d+1)+R`}\par\nobreak\vspace{2mm}\nobreak`:'')+R`\solvipassage{`+b+'}';if(t==='bogi')return R`\solvibogi{`+(/^[〈<]?\s*보\s*기\s*[〉>]?$/.test(n.title||'보기')?R`〈\,보\,기\,〉`:text(n.title))+'}{'+b+'}';if(t==='question')return questionBox((n.code?R`\write16{SOLVICODE:\thepage:`+n.code+'}':'')+b+(n.code?R`\write16{SOLVIEND:\thepage:`+n.code+'}':''),n.minimum||0);
 throw Error('지원하지 않는 문서 요소: '+t);
}
function questionBox(body,minimum,code){const mm=Number(minimum);if(!Number.isFinite(mm)||mm<0||mm>200)throw Error('문항 여백 범위');return R`\par\noindent\begingroup\setbox2=\vbox{\hsize=\linewidth\setlength{\parskip}{0pt} `+body+'}'+(code?R`\typeout{SOLVIMEASURE:`+code+R`:\the\dimexpr\ht2+\dp2\relax}`:'')+R`\ifdim\dimexpr\ht2+\dp2\relax>190mm\unvbox2\else\ifdim\dimexpr\ht2+\dp2\relax<`+mm+R`mm\begin{minipage}[t][`+mm+R`mm][t]{\linewidth}\vspace{0pt}\unvbox2\end{minipage}\else\begin{minipage}[t]{\linewidth}\vspace{0pt}\unvbox2\end{minipage}\fi\fi\endgroup\par\vspace{3mm}`}
function manifest(m){if(!Array.isArray(m.pages)||!m.pages.length||m.pages.length>500)throw Error('쪽 수 한도(1~500)');return {printEngine:'xelatex-v1',templateVersion:'haewon-2026-v1',subject:m.subjectId||m.subject,material:m.material||'book',...(m.bookId?{bookId:m.bookId}:{}),...(m.material==='worksheet'?{worksheetId:m.worksheetId}:{}),pages:m.pages.map(p=>{if(!Array.isArray(p.codes)||p.codes.length>300||p.codes.some(c=>!/^[-A-Za-z0-9_.~]{1,150}$/.test(c)))throw Error('문항 코드 오류');return {kind:p.kind,codes:[...new Set(p.codes)]}})}}
function cover(m){
 const c=m.cover||{},lines=(c.ranges||'').split('\n').filter(Boolean),step=Math.min(37,170/Math.max(1,lines.length));
 const instructions=R`\begin{list}{○}{\setlength{\leftmargin}{0pt}\setlength{\labelwidth}{3.2mm}\setlength{\labelsep}{3.9mm}\setlength{\itemsep}{1.2mm}\setlength{\parsep}{0pt}\setlength{\topsep}{0pt}\setlength{\partopsep}{0pt}}`+(c.instructions||'').split('\n').filter(s=>s.trim()).map(s=>R`\item `+text(s.replace(/^\s*[○◯•]\s*/,''))).join('\n')+R`\end{list}`;
 const out=[R`\newgeometry{left=13mm,right=13mm,top=12mm,bottom=24mm}\gdef\solvicover{1}\write16{SOLVIKIND:\thepage:cover}
\noindent\null
\begin{tikzpicture}[remember picture,overlay,x=.290039mm,y=-.290039mm]
\coordinate (origin) at ([xshift=2.47mm]current page.north west);
\begin{scope}[shift={(origin)}]
\node[anchor=base,inner sep=0pt] at (353.5,109) {\scalebox{.85}[1]{{\KoBold\fontsize{18.86}{23.5}\selectfont `+text(m.title)+R`}}};
\node[anchor=base,inner sep=0pt] at (353.5,179) {{\KoBold\fontsize{34.70}{43}\selectfont `+text(m.subject)+R`}};
\draw[line width=.5pt] (125,228) rectangle (269,260);
\draw[line width=.5pt] (170,228)--(170,260);
\node[inner sep=0pt] at (147.5,244) {\scalebox{.9}[1]{{\KoMed\fontsize{15.09}{19}\selectfont 성명}}};
\node[inner sep=0pt] at (219.5,244) {{\KoMed\fontsize{13}{17}\selectfont `+text(m.name||'')+R`}};
\draw[line width=.5pt] (285,228) rectangle (583,260);
\draw[line width=.5pt] (369,228)--(369,260);
\node[inner sep=0pt] at (327,244) {\scalebox{.9}[1]{{\KoMed\fontsize{15.09}{19}\selectfont 수험 번호}}};
\foreach \x in {392.78,416.56,440.33,511.67,535.44,559.22}{\draw[densely dotted,line width=.4pt] (\x,228)--(\x,260);}
\foreach \x in {464.11,487.89}{\draw[line width=.5pt] (\x,228)--(\x,260);}
\node at (476,244) {\KoMed\fontsize{15.09}{19}\selectfont —};
\draw[line width=.5pt] (81,278) rectangle (626,550);
\foreach \y in {304,330}{\draw[line width=.5pt] (119,\y) circle[radius=5.5];}
\node[anchor=base west,inner sep=0pt] at (138,311) {{\KoMed\fontsize{12.82}{17.3}\selectfont 문제지의 해당란에 성명과 수험번호를 정확히 쓰시오.}};
\node[anchor=base west,inner sep=0pt] at (138,337) {{\KoMed\fontsize{12.82}{17.3}\selectfont 답안지의 필적 확인란에 다음의 문구를 정자로 기재하시오.}};
\draw[fill=black!10,line width=.5pt] (138,348) rectangle (534,380);
\node[inner sep=0pt] at (336,364) {{\KoBold\fontsize{12.82}{17}\selectfont `+text(c.handwriting||'')+R`}};
\node[anchor=north west,inner sep=0pt,align=left,text width=134mm] at (138,390) {\KoMed\fontsize{12.82}{17.3}\selectfont\RaggedRight\setlength{\parskip}{0pt}`+instructions+R`};
\draw[line width=.5pt] (81,573) rectangle (626,812);
\node[anchor=north west,inner sep=0pt,align=left,text width=148mm] at (97,592) {{\KoMed\fontsize{12.82}{17.3}\selectfont ※ 문제지와 답안 구성을 확인하고, 답을 정확히 표시하시오.}};`];
 const rows=[],ranges=new Map(lines.map(s=>s.split(' ··· ')));
 for(const label of ['차례','개념','문제지'])if(ranges.has(label))rows.push({label,range:ranges.get(label),bullet:true});
 if(ranges.has('빠른 정답')||ranges.has('정답 및 해설')){rows.push({label:'답안지',range:'',bullet:true});for(const label of ['빠른 정답','정답 및 해설'])if(ranges.has(label))rows.push({label,range:ranges.get(label),indent:true});}
 if(ranges.has('필기'))rows.push({label:'필기',range:ranges.get('필기'),indent:true});
 const rowStep=Math.min(37,170/Math.max(1,rows.length-1));
 for(let i=0;i<rows.length;i++){const {label,range,bullet,indent}=rows[i],y=647+i*rowStep,x=indent?149:138;
  if(bullet)out.push(R`\draw[line width=.5pt] (119,`+(y-5)+R`) circle[radius=5.5];`);
  if(range)out.push(R`\node[anchor=base west,inner sep=0pt] at (`+x+','+y+R`) {\hbox to `+((592-x)*.290039).toFixed(3)+R`mm{\KoMed\fontsize{12.82}{17.3}\selectfont `+text(label)+R`\hspace{3mm}\leaders\hbox{\fontsize{5}{5}\selectfont .\kern.18mm}\hfill\hspace{4mm}{\fontsize{12.07}{16}\selectfont `+text(range)+R`}}};`);
  else out.push(R`\node[anchor=base west,inner sep=0pt] at (`+x+','+y+R`) {{\KoMed\fontsize{12.82}{17.3}\selectfont `+text(label)+R`}};`);
 }
 out.push(R`\draw[fill=black!10,line width=.5pt] (81,832) rectangle (626,877);
\node[inner sep=0pt] at (353.5,854.5) {{\KoBold\fontsize{15.09}{19}\selectfont ※ 시험이 시작될 때까지 표지를 넘기지 마십시오.}};
\node[anchor=base,inner sep=0pt] at (353.5,925) {{\KoBold\fontsize{19.61}{25}\selectfont `+text(c.organization||'')+R`}};
\end{scope}\end{tikzpicture}\clearpage\restoregeometry\gdef\solvicover{0}`);
 return out.join('\n');
}

function render(m,id,pre){
 if(m.layout==='book-original-v1'){manifest(m);if(!globalThis.SolviLatexBookDocument)throw Error('교재 조판기를 불러오지 못했습니다');return globalThis.SolviLatexBookDocument.render(m,id,pre)}
 manifest(m);if(!/^[a-f0-9]{32}$/.test(id)||!/^https:\/\/[A-Za-z0-9.:-]+\/[A-Za-z0-9_./-]*$/.test(m.publicBase))throw Error('QR 주소 오류');
 const family=m.fontFamily||'shin';if(!['shin','kopub','pretendard'].includes(family))throw Error('지원하지 않는 글꼴입니다');const size=Number(m.fontSize||10);if(!Number.isFinite(size)||size<8||size>14)throw Error('글자 크기 범위(8~14pt)');if(m.design&&!['reference','simple','boxed'].includes(m.design))throw Error('지원하지 않는 디자인입니다');
 const fontFile=family==='kopub'?'KoPubWorldMedium.ttf':family==='pretendard'?'PretendardRegular.ttf':'ShinMyeongjo.ttf',boldFile=family==='kopub'?'KoPubWorldBold.ttf':family==='pretendard'?'PretendardBold.ttf':null;
 const fontOverride=family==='shin'?'':['setmainfont','setsansfont','setmainhangulfont','setsanshangulfont'].map(command=>'\\'+command+'[Path=fonts/,BoldFont='+boldFile+']{'+fontFile+'}').join('\n');
 const marksOverride=family==='pretendard'?R`\newfontfamily\SolviMarks[Path=fonts/]{ShinMyeongjo.ttf}\renewcommand{\solvimark}[1]{{\SolviMarks #1}}`:'';
 const bodyOverride=R`\renewcommand{\solvibodyfont}{\fontsize{`+size+'}{'+(size*1.77).toFixed(2)+R`}\selectfont}`;
 const out=[pre,fontOverride,marksOverride,bodyOverride,R`\providecommand{\solvitotal}{?}\providecommand{\solvicover}{0}
\makeatletter
\AtBeginShipout{\typeout{SOLVIPAGE:\thepage}\immediate\write\@auxout{\string\gdef\string\solvitotal{\thepage}}}
\makeatother
\AddToShipoutPictureFG{\ifnum\solvicover=0\begin{tikzpicture}[remember picture,overlay]
\node[anchor=south west,inner sep=0pt] at ([xshift=13mm,yshift=5mm]current page.south west) {\IfFileExists{qr\thepage.png}{\includegraphics[width=12mm,height=12mm]{qr\thepage.png}}{\rule{12mm}{12mm}}};
\draw[line width=.43pt] ([xshift=-10mm,yshift=8mm]current page.south) rectangle ([xshift=10mm,yshift=14mm]current page.south);
\draw[line width=.32pt] ([xshift=-2mm,yshift=8mm]current page.south) -- ([xshift=2mm,yshift=14mm]current page.south);
\node[font=\KoMed\fontsize{10}{12}\selectfont] at ([xshift=-6mm,yshift=11mm]current page.south) {\thepage};
\node[font=\KoMed\fontsize{10}{12}\selectfont] at ([xshift=6mm,yshift=11mm]current page.south) {\solvitotal};
\end{tikzpicture}\fi}
\setlength{\columnsep}{9.2mm}\setlength{\columnseprule}{0pt}
\begin{document}`];
 const sections=[];const seenPassages=new Set();
 for(const p of m.pages){if(p.kind==='blank')continue;let section=sections.at(-1);if(!section||section.kind!==p.kind||p.kind==='cover'||p.kind==='notes'||p.kind==='back'){section={kind:p.kind,nodes:[],noteStyle:p.noteStyle||'lined',noteLabel:p.noteLabel||'필기 노트'};sections.push(section)}
  const queue=(p.codes||[]).slice();const annotate=(n,inside=false)=>{if(n.tag==='passage'&&n.group){if(seenPassages.has(n.group))return {tag:'span',text:''};seenPassages.add(n.group)}const copy={...n};if(n.tag==='unit'&&n.role==='answer'){copy.header=R`\par\noindent{\KoMed\fontsize{12}{17.7}\selectfont `+text(n.number||'')+R`.}\hspace{1.2mm} `+text(n.answer||'')+(m.showCodes?R`\hfill{\fontsize{8.5}{10.5}\selectfont `+text(n.code)+'}':'')+R`\par\nobreak\vspace{3mm}\nobreak`;}else if(n.tag==='unit'&&n.keep){copy.header=R`\par\noindent{\KoMed\fontsize{14.2}{18}\selectfont `+text(n.number||'')+R`.}\hspace{1.2mm}`+(m.showTypes!==false&&n.type?R`{\fontsize{9.6}{13.4}\selectfont `+text(n.type)+'}':'')+(m.showCodes?R`\hfill{\fontsize{8.5}{10.5}\selectfont `+text(n.code)+'}':'')+(n.points?R`\hfill{\fontsize{8.5}{10.5}\selectfont `+text(n.points)+'}':'')+R`\par\nobreak\vspace{3.4mm}\nobreak`;}if(section.kind==='answers')copy.allowBreak=true;if(section.kind==='questions'&&(n.tag==='unit'&&n.keep||n.tag==='question'&&!inside))copy.minimum=Math.max(0,Math.min(94,195/Math.ceil((m.per||4)/2)-4));if(n.tag==='unit'&&n.code){const i=queue.indexOf(n.code);if(i>=0)queue.splice(i,1);inside=true}else if(n.tag==='question'&&!inside&&queue.length){copy.code=queue.shift();inside=true}if(n.children)copy.children=n.children.map(c=>annotate(c,inside));return copy};
  section.nodes.push(...(p.top||[]).map(n=>annotate(n)),...(p.columns||[]).flat().map(n=>annotate(n)));
  if(queue.length)throw Error('문항과 조판 단위 연결을 확인해 주세요: '+queue[0]);
 }
 for(let i=0;i<sections.length;i++){const sec=sections[i];if(i)out.push(R`\clearpage`);
  if(m.duplex&&sec.kind==='answers')out.push(R`\ifodd\value{page}\else\write16{SOLVIKIND:\thepage:blank}\null\clearpage\fi`);
  if(sec.kind==='cover'){out.push(cover(m));continue}
  if(sec.kind==='back'){out.push(R`\gdef\solvicover{1}\write16{SOLVIKIND:\thepage:back}\null\vfill{\centering\KoBold\fontsize{25}{32}\selectfont `+text(m.title)+R`\par\vspace{5mm}{\KoMed\fontsize{13.58}{18}\selectfont `+text(m.subject)+R`}\par}\vfill{\centering\KoBold\fontsize{19.61}{25}\selectfont `+text(m.cover&&m.cover.organization||'')+R`\par}\clearpage\gdef\solvicover{0}`);continue}
  out.push(R`\write16{SOLVIKIND:\thepage:`+sec.kind+'}');
  if(sec.kind==='answers'){
   const quick=sec.nodes.filter(n=>n.tag==='quick-answers'),rest=sec.nodes.filter(n=>n.tag!=='quick-answers');
   if(quick.length)out.push(R`\write16{SOLVIKIND:\thepage:quick}`,quick.map(n=>node(n)).join('\n'),R`\clearpage\write16{SOLVIKIND:\thepage:answers}`);
   out.push(sectionPages(m,'정답 및 해설',rest,false));continue;
  }
  if(sec.kind==='contents'){out.push(R`{\centering\KoBold\fontsize{17}{23}\selectfont 차례\par}\vspace{8mm}`);for(const e of m.contentsEntries||[]){out.push(R`\par\medskip{\KoMed\fontsize{12.3}{16}\selectfont `+text(e.title)+R`}\par\smallskip `+(e.items||[]).map(x=>text(x)).join(' · ')+R`\par`)}out.push(R`\par\bigskip{\KoBold 쪽 안내}\par\medskip `+text(m.contentsRanges||'').replace(/\n/g,R`\par `));continue}
  if(sec.kind==='notes'){if(!['lined','grid','plain'].includes(sec.noteStyle))throw Error('필기 양식 오류');out.push(R`\noindent{\KoMed `+text(sec.noteLabel)+R`}\par\null\begin{tikzpicture}[remember picture,overlay]`);if(sec.noteStyle==='lined')out.push(R`\foreach \y in {47,53.6,...,271.4}{\draw[black!12,line width=.18mm] ([xshift=13mm,yshift=-\y mm]current page.north west)--([xshift=-13mm,yshift=-\y mm]current page.north east);}`);if(sec.noteStyle==='grid')out.push(R`\draw[step=5mm,black!12,line width=.2mm] ([xshift=13mm,yshift=-47mm]current page.north west) grid ([xshift=-13mm,yshift=22mm]current page.south east);`);out.push(R`\end{tikzpicture}`);continue}
  out.push(sectionPages(m,sec.kind==='concept'?'개념':m.subject,sec.nodes,sec.kind==='questions'));
 }
 if(m.duplex)out.push(R`\clearpage\ifodd\value{page}\else\write16{SOLVIKIND:\thepage:blank}\null\clearpage\fi`);
 out.push(R`\end{document}`);return out.join('\n');
}
function sectionPages(m,subject,nodes,questions){
 const round=text(m.roundLabel||m.cover?.roundLabel||'학습 자료'),title=text(m.title),label=text(subject),count=[...new Set(m.pages.filter(p=>p.kind==='questions').flatMap(p=>p.codes))].length;
 let first=R`\par\vspace*{4.4mm}\noindent\makebox[\linewidth][c]{\KoBold\fontsize{12.1}{16}\selectfont `+title+R`}\par\vspace{5.6mm}
\noindent\makebox[28mm][l]{\tikz[baseline=(a.base)]\node[draw,ellipse,line width=.62pt,inner xsep=7pt,inner ysep=3.6pt,font=\KoBold\fontsize{10.6}{13}\selectfont] (a) {`+round+R`};}\makebox[\dimexpr\linewidth-56mm\relax][c]{\KoMed\fontsize{21.5}{26}\selectfont `+label+R`}\makebox[28mm][r]{\KoMed\fontsize{21}{25}\selectfont \thepage}\par\vspace{5.4mm}\hrule height .85pt\par\vspace{5.3mm}`+(questions?R`
{\fontsize{9.8}{16}\selectfont 학번 \rule{25mm}{.4pt}\qquad 이름 `+text(m.name||'')+R`\rule{28mm}{.4pt}\hfill 맞힌 개수 \rule{13mm}{.4pt}\,/`+count+R`}\par\vspace{5.1mm}
\noindent\fbox{\KoMed\fontsize{9.5}{12}\selectfont `+text(m.questionKind||'학습 문항')+R`}\par\vspace{5.5mm}`:'');
 let running=R`\solvirunningheader{`+round+'}{'+label+'}';
 if(m.design==='simple')first=R`\vspace*{4.4mm}\noindent{\KoBold\fontsize{17}{23}\selectfont `+title+R`}\par\vspace{4mm}\noindent{\KoMed `+label+R`\hfill `+round+R`\quad\thepage}\par\vspace{3mm}\hrule height .5pt\vspace{12mm}`;
 if(m.design==='boxed'){first=R`\vspace*{4.4mm}\noindent\fbox{\begin{minipage}{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}\vspace{3mm}{\centering\KoBold\fontsize{17}{23}\selectfont `+title+R`\par}\vspace{5mm}\noindent\KoMed `+round+R`\hfill `+label+R`\hfill\thepage\par\vspace{3mm}\end{minipage}}\par\vspace{10mm}`;running=R`\noindent\fbox{\makebox[\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax]{\KoMed `+round+R`\hfill `+label+R`\hfill\thepage}}\par\vspace{5.2mm}`;}

 const items=nodes.filter(n=>!(n.tag==='span'&&!n.children?.length&&!String(n.text||'').trim()));
 if(questions&&items.length&&items.every(n=>n.tag==='unit'&&n.keep&&Number.isFinite(m.unitHeights?.[n.code])&&m.unitHeights[n.code]<190)){
  const cap=Math.max(1,Math.min(4,Math.ceil((m.per||4)/2))),pages=[];let index=0,page=0;
  while(index<items.length){const h=page?235:195,columns=[];
   for(let col=0;col<2;col++){let take=Math.min(cap,items.length-index);while(take>1&&Math.max(...items.slice(index,index+take).map(n=>m.unitHeights[n.code]+1))>h/take)take--;const part=items.slice(index,index+take);index+=take;columns.push(R`\begin{minipage}[t][`+h+R`mm][t]{.475\textwidth}\vspace{0pt}\solvibodyfont\RaggedRight\setlength{\parskip}{0pt}`+part.map(n=>node({...n,slotHeight:h/Math.max(1,take)})).join('\n')+R`\end{minipage}`)}
   pages.push((page?running:first)+R`\noindent `+columns.join(R`\hfill `)+R`\par\AddToShipoutPictureBG*{\begin{tikzpicture}[remember picture,overlay]\draw[black!70,line width=.43pt] ([yshift=-`+(page?'31':'75')+R`mm]current page.north)--([yshift=18mm]current page.south);\end{tikzpicture}}\clearpage`);page++;
  }
  return pages.join('\n');
 }
 return R`\solvisection{`+first+'}{'+running+'}{'+nodes.map(n=>node(n)).join('\n')+'}{'+(questions?'195mm':'222mm')+'}{235mm}';
}

function pageManifest(model,log){
 const emitted=[...log.matchAll(/SOLVIPAGE:(\d+)/g)].map(m=>+m[1]);if(!emitted.length)throw Error('조판 쪽 정보를 찾지 못했습니다');const total=Math.max(...emitted);if(total>500)throw Error('쪽 수 한도');
 const pages=Array.from({length:total},()=>({kind:'questions',codes:[]}));const kinds=[...log.matchAll(/SOLVIKIND:(\d+):([a-z]+)/g)].map(m=>({page:+m[1],kind:m[2]})).sort((a,b)=>a.page-b.page);
 for(let i=0;i<kinds.length;i++){const k=kinds[i],end=i+1<kinds.length?kinds[i+1].page-1:total;for(let p=k.page;p<=end&&p<=total;p++)if(p>0)pages[p-1].kind=k.kind}
 for(const m of log.matchAll(/SOLVICODE:(\d+):([-A-Za-z0-9_.~]+)/g)){const p=pages[+m[1]-1];if(p&&p.kind==='questions'&&!p.codes.includes(m[2]))p.codes.push(m[2])}
 const starts=new Map();for(const m of log.matchAll(/(SOLVICODE|SOLVIEND):(\d+):([-A-Za-z0-9_.~]+)/g)){const page=+m[2],code=m[3];if(m[1]==='SOLVICODE')starts.set(code,page);else{const first=starts.get(code);if(first)for(let p=first;p<=page;p++){const dest=pages[p-1];if(dest&&dest.kind==='questions'&&!dest.codes.includes(code))dest.codes.push(code)}starts.delete(code)}}
 const nums=new Map([...log.matchAll(/SOLVINUM:\d+:([-A-Za-z0-9_.~]+):(\d+)/g)].map(m=>[m[1],+m[2]]));for(const p of pages){const entries=p.codes.filter(c=>nums.has(c)).map(c=>[c,nums.get(c)]);if(entries.length)p.nums=Object.fromEntries(entries)}
 const expected=[...new Set(model.pages.filter(p=>p.kind==='questions').flatMap(p=>p.codes))],actual=new Set(pages.flatMap(p=>p.codes));if(expected.some(c=>!actual.has(c))||[...actual].some(c=>!expected.includes(c)))throw Error('최종 쪽과 QR 문항 목록이 다릅니다');
 return {...manifest(model),pages};
}

function coverRanges(manifest){const labels={questions:'문제지',quick:'빠른 정답',answers:'정답 및 해설',concept:'개념',contents:'차례',notes:'필기'},lines=[];for(const [kind,label] of Object.entries(labels)){const nums=manifest.pages.flatMap((p,i)=>p.kind===kind?[i+1]:[]);if(!nums.length)continue;const spans=[];let lo=nums[0],hi=lo;for(const n of nums.slice(1)){if(n===hi+1)hi=n;else{spans.push(lo===hi?String(lo):lo+'~'+hi);lo=hi=n}}spans.push(lo===hi?String(lo):lo+'~'+hi);lines.push(label+' ··· '+spans.join(', ')+'쪽')}return lines.join('\n')}

return {text,node,math,manifest,render,pageManifest,coverRanges};
});
