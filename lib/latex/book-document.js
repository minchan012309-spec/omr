/* Fixed A4 pages retain the established book design; text is native XeTeX. */
(function(g,f){const api=f();if(typeof module==='object'&&module.exports)module.exports=api;else g.SolviLatexBookDocument=api})(globalThis,function(){'use strict';
const R=String.raw,escape={'\\':R`\textbackslash{}`,'{':R`\{`,'}':R`\}`,'$':R`\$`,'&':R`\&`,'#':R`\#`,'%':R`\%`,'_':R`\_`,'~':R`\textasciitilde{}`,'^':R`\textasciicircum{}`};
function text(s){return [...String(s)].map(c=>escape[c]||(c===' '?R`\ `:c)).join('')}
function n(value){if(!Number.isFinite(+value)||Math.abs(+value)>5000)throw Error('교재 위치 정보 오류');return (+value).toFixed(4)}
function render(model,id,pre){
 if(model.layout!=='book-original-v1'||!Array.isArray(model.pages)||!model.pages.length||model.pages.length>500)throw Error('교재 쪽 정보 오류');
 if(!/^[a-f0-9]{32}$/.test(id))throw Error('교재 QR 식별자 오류');
 const files=[...new Set(model.bookFonts||[])];if(files.some(f=>!/^[-A-Za-z0-9]+\.ttf$/.test(f)))throw Error('교재 글꼴 경로 오류');
 const fonts=new Map(files.map((file,i)=>[file,'BKFont'+String.fromCharCode(65+Math.floor(i/26))+String.fromCharCode(65+i%26)]));
 const out=[R`\documentclass[a4paper]{article}
\usepackage[margin=0pt,noheadfoot]{geometry}
\usepackage{fontspec,kotex,unicode-math,amsmath,graphicx,xcolor,eso-pic,atbegshi}
\setmainfont[Path=fonts/]{ShinMyeongjo.ttf}
\setmainhangulfont[Path=fonts/]{ShinMyeongjo.ttf}
\setsansfont[Path=fonts/]{ShinMyeongjo.ttf}
\setsanshangulfont[Path=fonts/]{ShinMyeongjo.ttf}
\newfontfamily\HancomMath[Path=fonts/]{HancomEQN.ttf}
\setmathfont{latinmodern-math.otf}\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\topskip}{0pt}
\defaultfontfeatures{Ligatures=NoCommon}
\newcommand{\BKput}[3]{\put(\LenToUnit{#1mm},\LenToUnit{#2mm}){#3}}
\begin{document}`];
 // Both Latin and Hangul families must be switched: KoTeX otherwise keeps the
 // document-wide Hangul font even when a Latin fontspec family is selected.
 if(pre)out[0]=pre+'\n'+String.raw`\geometry{margin=0pt,noheadfoot}\pagestyle{empty}\setlength{\parindent}{0pt}\setlength{\parskip}{0pt}\setlength{\topskip}{0pt}\newcommand{\BKput}[3]{\put(\LenToUnit{#1mm},\LenToUnit{#2mm}){#3}}\begin{document}`;
 const declarations=files.map(file=>{const f=fonts.get(file);return '\\newfontfamily\\'+f+'[Path=fonts/]{'+file+'}\n\\newhangulfontfamily\\'+f+'Hangul[Path=fonts/]{'+file+'}'}).join('\n');out[0]=out[0].replace('\\begin{document}',declarations+'\n\\begin{document}\n\\special{dvipdfmx:config z 9}');
 for(let i=0;i<model.pages.length;i++){
  const page=model.pages[i],d=page.drawing;if(!d||!/^a\d+\.png$/.test(d.background))throw Error('교재 배경 정보 오류');
  if(!/^[a-z]+$/.test(page.kind))throw Error('교재 쪽 종류 오류');
  const physical=i+1,layer=[R`\BKput{0}{0}{\includegraphics[width=210mm,height=297mm]{`+d.background+'}}'];
  for(const run of d.text||[]){const family=fonts.get(run.fontFile);if(!family||!run.text)throw Error('교재 본문 글꼴 정보 오류');if(!/^[0-9A-F]{6}$/.test(run.color))throw Error('교재 본문 색 정보 오류');
   // \resizebox horizontally matches the original browser's measured advance.
   // A fixed vertical scale keeps the original CSS font size and baseline.
   const body='{\\'+family+'\\'+family+'Hangul'+(run.italic?'\\addfontfeatures{FakeSlant=.2493}':'')+'\\fontsize{'+n(run.fontSize)+'}{'+n(run.fontSize*1.2)+'}\\selectfont\\color[HTML]{'+run.color+'}'+text(run.text)+'}';
   layer.push('\\BKput{'+n(run.x)+'}{'+n(297-run.y)+'}{\\makebox[0pt][l]{\\begingroup\\setbox0=\\hbox{'+body+'}\\ifdim\\wd0>0pt\\resizebox{'+n(run.width)+'mm}{\\height}{\\copy0}\\fi\\endgroup}}');
  }
  for(const formula of d.math||[]){
   if(!globalThis.SolviLatexDocument?.math||formula.formula?.tag!=='math'||!/^[0-9A-F]{6}$/.test(formula.color))throw Error('교재 수식 정보 오류');
   const expression=globalThis.SolviLatexDocument.math(formula.formula),body=R`{\fontsize{`+n(formula.fontSize)+'}{'+n(formula.fontSize*1.2)+R`}\selectfont\color[HTML]{`+formula.color+R`}\(`+(formula.display?R`\displaystyle `:R`\textstyle `)+expression+R`\)}`;
   layer.push(R`\BKput{`+n(formula.x)+'}{'+n(297-formula.y)+R`}{\makebox[0pt][l]{\begingroup\setbox0=\hbox{`+body+R`}\makebox[`+n(formula.width)+R`mm][`+(formula.display?'c':'l')+R`]{\ifdim\wd0>`+n(formula.width)+R`mm\resizebox{`+n(formula.width)+R`mm}{!}{\copy0}\else\copy0\fi}\endgroup}}`);
  }
  for(const qr of d.qrs||[])layer.push('\\BKput{'+n(qr.x)+'}{'+n(297-qr.y-qr.height)+'}{\\IfFileExists{qr'+physical+'.png}{\\includegraphics[width='+n(qr.width)+'mm,height='+n(qr.height)+'mm]{qr'+physical+'.png}}{\\rule{0pt}{'+n(qr.height)+'mm}}}');
  out.push('\\AddToShipoutPictureBG*{\\AtPageLowerLeft{'+layer.join('\n')+'}}');
  // Non-immediate writes are attached to this page's vertical list, so boxed
  // material cannot move metadata onto an earlier physical page.
  out.push('\\write16{SOLVIPAGE:'+physical+'}\\write16{SOLVIKIND:'+physical+':'+page.kind+'}');
  for(const code of page.codes||[]){if(!/^[-A-Za-z0-9_.~]{1,150}$/.test(code))throw Error('교재 문항 코드 오류');out.push('\\write16{SOLVICODE:'+physical+':'+code+'}\\write16{SOLVIEND:'+physical+':'+code+'}');if(Number.isInteger(page.nums?.[code]))out.push('\\write16{SOLVINUM:'+physical+':'+code+':'+page.nums[code]+'}')}
  out.push(R`\null\clearpage`);
 }
 out.push(R`\end{document}`);return out.join('\n');
}
return {render};
});
