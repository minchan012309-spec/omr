(function(g,f){const a=f();if(typeof module==='object'&&module.exports)module.exports=a;else g.SolviLatexDocument=a})(globalThis,function(){
'use strict';
const R=String.raw;
const ESC={'\\':R`\textbackslash{}`,'{':R`\{`,'}':R`\}`,'$':R`\$`,'&':R`\&`,'#':R`\#`,'%':R`\%`,'_':R`\_`,'~':R`\textasciitilde{}`,'^':R`\textasciicircum{}`};
function text(s){return Array.from(String(s??'')).filter(c=>c==='\n'||c==='\t'||c.charCodeAt(0)>=32).map(c=>ESC[c]||c).join('')}
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
 if(t==='b'||t==='strong')return R`\textbf{`+b+'}';if(t==='i'||t==='em')return R`\emph{`+b+'}';if(t==='u')return R`\underline{`+b+'}';
 if(t==='s')return R`\sout{`+b+'}';
 if(t==='sub')return R`\textsubscript{`+b+'}';if(t==='sup')return R`\textsuperscript{`+b+'}';if(t==='br')return R`\leavevmode\newline `+'\n';if(t==='hr')return R`\par\smallskip\hrule\smallskip `;
 if(t==='ul'||t==='ol')return R`\begin{itemize}`+(n.children||[]).map(c=>R`\item `+node(c,d+1)).join('\n')+R`\end{itemize}`;
 if(t==='fraction'){const a=n.children||[];if(a.length!==2)throw Error('분수 구조 오류');return R`\(\dfrac{\text{`+node(a[0],d+1)+R`}}{\text{`+node(a[1],d+1)+R`}}\)`}
 if(t==='choices-list'){n={...n,children:(n.children||[]).filter(c=>!(c.tag==='span'&&!c.children?.length&&!String(c.text||'').trim()))};if(!n.children.length||n.children.length>20)throw Error('선지 개수를 확인해 주세요');const choices=n.children.map(c=>{const children=(c.children||[]).slice();if(children[0]&&['b','strong'].includes(children[0].tag)&&/^[①-⑳]$/.test(children[0].text||''))children.shift();return (children.map(x=>node(x,d+1)).join('')||text(c.text||'')).replace(/\\\(/g,R`\(\displaystyle `)});const lengths=choices.map(s=>s.replace(/\\[a-z]+|[{}]/g,'').length),max=Math.max(...lengths);if(choices.length!==5){const cols=max<=15?3:max<=30?2:1,rows=[];for(let i=0;i<choices.length;i+=cols){const cells=choices.slice(i,i+cols).map((v,j)=>R`\circh{`+(i+j+1)+'}\\,'+v);while(cells.length<cols)cells.push('');rows.push(cells.join(' & ')+R`\\[3.8mm]`)}return R`\par\vspace{3.4mm}\begin{tabularx}{\linewidth}{`+Array(cols).fill('X').join('')+'}'+rows.join('\n')+R`\end{tabularx}\par\vspace{3.8mm}`}const command=max<=12?'examoptsfive':max<=30?'examoptstwo':'examoptsvertical';return '\\'+command+choices.map(s=>'{'+s+'}').join('')}
 if(t==='question-number')return R`{\KoMed\fontsize{14.2}{18}\selectfont `+b+R`.}\hspace{1.2mm}`;if(t==='points')return R`\hfill{\fontsize{8.5}{10.5}\selectfont `+b+'}';if(t==='question-head')return R`\par\noindent `+b+R`\par\vspace{3.4mm}`;
 if(t==='unit'){if(!/^[-A-Za-z0-9_.~]{1,150}$/.test(n.code||''))throw Error('문항 코드 오류');if(n.allowBreak)return R`\par `+b+R`\par\vspace{3.6mm}\hrule height .2pt `;return questionBox(R`\write16{SOLVICODE:\thepage:`+n.code+'}'+(Number.isInteger(n.number)?R`\write16{SOLVINUM:\thepage:`+n.code+':'+n.number+'}':'')+b+R`\write16{SOLVIEND:\thepage:`+n.code+'}',n.minimum||0)}
 if(t==='quick-answers')return b;if(t==='quick-title')return R`\par\vspace*{5mm}{\centering\KoBold\fontsize{17}{23}\selectfont `+b+R`\par}\vspace{4mm}`;
 if(t==='answer-grid'){const cells=(n.children||[]).map(c=>R`\begin{tabular}{@{}c@{}}`+(c.children||[]).map(x=>node(x,d+1)).join(R`\\[1mm]`)+R`\end{tabular}`),rows=[];for(let i=0;i<cells.length;i+=5){const row=cells.slice(i,i+5);while(row.length<5)row.push('');rows.push(row.join(' & ')+R`\\[1.5mm]\hline`)}return R`\par\begin{center}\fontsize{10.7}{18}\selectfont\renewcommand{\arraystretch}{1.65}\begin{tabular}{|*{5}{c|}}\hline `+rows.join('\n')+R`\end{tabular}\end{center}\vspace{7mm}`}
 if(t==='bogi')return R`\choices{`+b+'}';if(t==='question')return questionBox((n.code?R`\write16{SOLVICODE:\thepage:`+n.code+'}':'')+b+(n.code?R`\write16{SOLVIEND:\thepage:`+n.code+'}':''),n.minimum||0);
 throw Error('지원하지 않는 문서 요소: '+t);
}
function questionBox(body,minimum){const mm=Number(minimum);if(!Number.isFinite(mm)||mm<0||mm>200)throw Error('문항 여백 범위');return R`\par\noindent\begingroup\setbox2=\vbox{\hsize=\linewidth `+body+'}'+R`\ifdim\dimexpr\ht2+\dp2\relax>225mm\unvbox2\else\ifdim\dimexpr\ht2+\dp2\relax<`+mm+R`mm\begin{minipage}[t][`+mm+R`mm][t]{\linewidth}\vspace{0pt}\unvbox2\end{minipage}\else\begin{minipage}[t]{\linewidth}\vspace{0pt}\unvbox2\end{minipage}\fi\fi\endgroup\par\vspace{3mm}`}
function manifest(m){if(!Array.isArray(m.pages)||!m.pages.length||m.pages.length>500)throw Error('쪽 수 한도(1~500)');return {printEngine:'xelatex-v1',templateVersion:'haewon-2026-v1',subject:m.subjectId||m.subject,material:m.material||'book',...(m.bookId?{bookId:m.bookId}:{}),...(m.material==='worksheet'?{worksheetId:m.worksheetId}:{}),pages:m.pages.map(p=>{if(!Array.isArray(p.codes)||p.codes.length>300||p.codes.some(c=>!/^[-A-Za-z0-9_.~]{1,150}$/.test(c)))throw Error('문항 코드 오류');return {kind:p.kind,codes:[...new Set(p.codes)]}})}}
function cover(m){
 const c=m.cover||{},lines=(c.ranges||'').split('\n').filter(Boolean),step=Math.min(37,170/Math.max(1,lines.length));
 const instructions=text(c.instructions||'').replace(/\n/g,R`\par `);
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
\node[anchor=north west,inner sep=0pt,text width=139mm] at (112,390) {\KoMed\fontsize{12.82}{17.3}\selectfont\setlength{\parskip}{.8pt}`+instructions+R`};
\draw[line width=.5pt] (81,573) rectangle (626,812);
\node[anchor=north west,inner sep=0pt,text width=148mm] at (97,592) {{\KoMed\fontsize{12.82}{17.3}\selectfont ※ 문제지와 답안 구성을 확인하고, 답을 정확히 표시하시오.}};`];
 for(let i=0;i<lines.length;i++){const [label,range='']=lines[i].split(' ··· '),y=647+i*step;out.push(R`\node[anchor=base west,inner sep=0pt] at (112,`+y+R`) {{\KoMed\fontsize{13.58}{17.3}\selectfont `+text(label)+R`}};\draw[densely dotted,line width=.5pt] (255,`+(y-4)+')--(529,'+(y-4)+R`);\node[anchor=base east,inner sep=0pt] at (592,`+y+R`) {{\KoMed\fontsize{12.07}{16}\selectfont `+text(range)+R`}};`)}
 out.push(R`\draw[fill=black!10,line width=.5pt] (81,832) rectangle (626,877);
\node[inner sep=0pt] at (353.5,854.5) {{\KoBold\fontsize{15.09}{19}\selectfont ※ 시험이 시작될 때까지 표지를 넘기지 마십시오.}};
\node[anchor=base,inner sep=0pt] at (353.5,925) {{\KoBold\fontsize{19.61}{25}\selectfont `+text(c.organization||'')+R`}};
\end{scope}\end{tikzpicture}\clearpage\restoregeometry\gdef\solvicover{0}`);
 return out.join('\n');
}

function render(m,id,pre){
 manifest(m);if(!/^[a-f0-9]{32}$/.test(id)||!/^https:\/\/[A-Za-z0-9.:-]+\/[A-Za-z0-9_./-]*$/.test(m.publicBase))throw Error('QR 주소 오류');
 const out=[pre.replace('top=12mm','top=31mm').replace('bottom=16.5mm','bottom=24mm'),R`\providecommand{\solvitotal}{?}\providecommand{\solvicover}{0}
\makeatletter
\AtBeginShipout{\typeout{SOLVIPAGE:\thepage}\immediate\write\@auxout{\string\gdef\string\solvitotal{\thepage}}}
\makeatother
\AddToShipoutPictureFG{\ifnum\solvicover=0\begin{tikzpicture}[remember picture,overlay]
\node[anchor=south west,inner sep=0pt] at ([xshift=13mm,yshift=5mm]current page.south west) {\qrcode[height=12mm]{`+m.publicBase+R`\#lt=`+id+R`:\thepage}};
\draw[line width=.43pt] ([xshift=-10mm,yshift=8mm]current page.south) rectangle ([xshift=10mm,yshift=14mm]current page.south);
\draw[line width=.32pt] ([xshift=-2mm,yshift=8mm]current page.south) -- ([xshift=2mm,yshift=14mm]current page.south);
\node[font=\KoMed\fontsize{10}{12}\selectfont] at ([xshift=-6mm,yshift=11mm]current page.south) {\thepage};
\node[font=\KoMed\fontsize{10}{12}\selectfont] at ([xshift=6mm,yshift=11mm]current page.south) {\solvitotal};
\end{tikzpicture}\fi}
\setlength{\columnsep}{11mm}\setlength{\columnseprule}{.43pt}
\begin{document}`];
 const sections=[];
 for(const p of m.pages){if(p.kind==='blank')continue;let section=sections.at(-1);if(!section||section.kind!==p.kind||p.kind==='cover'||p.kind==='notes'||p.kind==='back'){section={kind:p.kind,nodes:[],noteStyle:p.noteStyle||'lined',noteLabel:p.noteLabel||'필기 노트'};sections.push(section)}
  const queue=(p.codes||[]).slice();const annotate=(n,inside=false)=>{const copy={...n};if(section.kind==='answers')copy.allowBreak=true;if(section.kind==='questions'&&(n.tag==='unit'&&n.keep||n.tag==='question'&&!inside))copy.minimum=Math.max(0,Math.min(94,232/Math.ceil((m.per||4)/2)-3));if(n.tag==='unit'&&n.code){const i=queue.indexOf(n.code);if(i>=0)queue.splice(i,1);inside=true}else if(n.tag==='question'&&!inside&&queue.length){copy.code=queue.shift();inside=true}if(n.children)copy.children=n.children.map(c=>annotate(c,inside));return copy};
  section.nodes.push(...(p.top||[]).map(n=>annotate(n)),...(p.columns||[]).flat().map(n=>annotate(n)));
  if(queue.length)throw Error('문항과 조판 단위 연결을 확인해 주세요: '+queue[0]);
 }
 for(let i=0;i<sections.length;i++){const sec=sections[i];if(i)out.push(R`\clearpage`);
  if(m.duplex&&sec.kind==='answers')out.push(R`\ifodd\value{page}\else\write16{SOLVIKIND:\thepage:blank}\null\clearpage\fi`);
  if(sec.kind==='cover'){out.push(cover(m));continue}
  if(sec.kind==='back'){out.push(R`\gdef\solvicover{1}\write16{SOLVIKIND:\thepage:back}\null\vfill{\centering\KoBold\fontsize{25}{32}\selectfont `+text(m.title)+R`\par\vspace{5mm}{\KoMed\fontsize{13.58}{18}\selectfont `+text(m.subject)+R`}\par}\vfill{\centering\KoBold\fontsize{19.61}{25}\selectfont `+text(m.cover&&m.cover.organization||'')+R`\par}\clearpage\gdef\solvicover{0}`);continue}
  if(sec.kind==='answers')out.push(R`\newgeometry{left=13mm,right=13mm,top=12mm,bottom=24mm}`);
  out.push(R`\write16{SOLVIKIND:\thepage:`+sec.kind+'}');
  if(sec.kind==='answers'){const quick=sec.nodes.filter(n=>n.tag==='quick-answers'),rest=sec.nodes.filter(n=>n.tag!=='quick-answers');if(quick.length){out.push(R`\write16{SOLVIKIND:\thepage:quick}`,quick.map(n=>node(n)).join('\n'),R`\clearpage\write16{SOLVIKIND:\thepage:answers}`)}out.push(R`{\centering\KoBold\fontsize{17}{23}\selectfont 문항별 정답 및 상세 해설\par}\vspace{4mm}\begin{list}{}{\setlength{\leftmargin}{14.5mm}\setlength{\rightmargin}{14.5mm}}\item[]\fontsize{10.8}{20}\selectfont\RaggedRight`,rest.map(n=>node(n)).join('\n'),R`\end{list}`);continue}
  if(sec.kind==='contents'){out.push(R`{\centering\KoBold\fontsize{17}{23}\selectfont 차례\par}\vspace{8mm}`);for(const e of m.contentsEntries||[]){out.push(R`\par\medskip{\KoMed\fontsize{12.3}{16}\selectfont `+text(e.title)+R`}\par\smallskip `+(e.items||[]).map(x=>text(x)).join(' · ')+R`\par`)}out.push(R`\par\bigskip{\KoBold 쪽 안내}\par\medskip `+text(m.contentsRanges||'').replace(/\n/g,R`\par `));continue}
  if(sec.kind==='notes'){if(!['lined','grid','plain'].includes(sec.noteStyle))throw Error('필기 양식 오류');out.push(R`\noindent{\KoMed `+text(sec.noteLabel)+R`}\par\null\begin{tikzpicture}[remember picture,overlay]`);if(sec.noteStyle==='lined')out.push(R`\foreach \y in {47,53.6,...,271.4}{\draw[black!12,line width=.18mm] ([xshift=13mm,yshift=-\y mm]current page.north west)--([xshift=-13mm,yshift=-\y mm]current page.north east);}`);if(sec.noteStyle==='grid')out.push(R`\draw[step=5mm,black!12,line width=.2mm] ([xshift=13mm,yshift=-47mm]current page.north west) grid ([xshift=-13mm,yshift=22mm]current page.south east);`);out.push(R`\end{tikzpicture}`);continue}
  const heading=sec.kind==='answers'?'정답 및 해설':sec.kind==='concept'?'개념':sec.kind==='notes'?'필기':m.subject;
  out.push(R`\vspace*{-14.6mm}\noindent\makebox[\linewidth][c]{\KoBold\fontsize{12.1}{16}\selectfont `+text(m.title)+R`}\par\vspace{5.6mm}{\centering\KoMed\fontsize{21.5}{26}\selectfont `+text(heading)+R`\par}\vspace{5.4mm}\hrule height .85pt\vspace{5.3mm}`);
  if(sec.kind==='questions'&&m.material!=='book')out.push(R`{\fontsize{9.8}{16}\selectfont 학번 \rule{25mm}{.4pt}\qquad 이름 `+text(m.name||'')+R`\rule{22mm}{.4pt}\hfill 맞힌 개수 \rule{13mm}{.4pt}\,/`+[...new Set(m.pages.filter(p=>p.kind==='questions').flatMap(p=>p.codes))].length+R`}\par\vspace{5.1mm}\noindent\fbox{\KoMed\fontsize{9.5}{12}\selectfont `+text(m.questionKind||'문제')+R`}\par\vspace{5.5mm}`);

  out.push(R`\begin{multicols}{2}\fontsize{10}{17.7}\selectfont\RaggedRight`);
  out.push(sec.nodes.map(n=>node(n)).join('\n'));
  out.push(R`\end{multicols}`);
 }
 if(m.duplex)out.push(R`\clearpage\ifodd\value{page}\else\write16{SOLVIKIND:\thepage:blank}\null\clearpage\fi`);
 out.push(R`\end{document}`);return out.join('\n');
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
