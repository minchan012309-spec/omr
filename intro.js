/* Solvi 소개: 장면 섹션은 보통 문서처럼 흐르고, 3D 무대(sticky)가 스크롤 위치를 따라 GSAP 타임라인 한 편을 재생한다.
   스크롤은 브라우저 기본 동작 그대로다: wheel · touch · key 를 가로채지 않고, 고정(pin) · 스크럽 지연 · 스냅 · 위치 보정이 없다.
   스크립트가 없거나 · 동작 줄이기 · 저사양이면 html.cine 없이 같은 내용을 정적인 장면으로 보여 준다. */
(function(){
'use strict';
var D=document,H=D.documentElement;
var $=function(s,r){return (r||D).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||D).querySelectorAll(s))};
var esc=function(t){return String(t==null?'':t).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})};

/* ---------- 머리글 · 목차 · 오른쪽 아래 버튼 ---------- */
var hd=$('.hd'),menu=$('#menu'),nav=$('#nav'),dock=$('#dock');
var cssv=function(n){return getComputedStyle(H).getPropertyValue(n).trim()};
function navOpen(on){nav.classList.toggle('open',on);menu.setAttribute('aria-expanded',String(on));menu.setAttribute('aria-label',on?'목차 닫기':'목차 열기')}
menu.addEventListener('click',function(){navOpen(menu.getAttribute('aria-expanded')!=='true')});
nav.addEventListener('click',function(e){if(e.target.closest('a'))navOpen(false)});
D.addEventListener('keydown',function(e){if(e.key==='Escape'&&menu.getAttribute('aria-expanded')==='true'){navOpen(false);menu.focus()}});
D.addEventListener('click',function(e){if(!e.target.closest('.hd'))navOpen(false);if(e.target.closest('[data-app]')){try{localStorage.setItem('omr_app','1')}catch(ignore){}}});
var lightFilm=false,lightSecs=0,scrollQ=false,sync=null;
function theme(){hd.classList.toggle('light',lightFilm||lightSecs>0)}
function onScroll(){scrollQ=false;var y=scrollY;hd.classList.toggle('scrolled',y>12);dock.classList.toggle('on',y>innerHeight*.9);if(sync)sync()}
addEventListener('scroll',function(){if(!scrollQ){scrollQ=true;requestAnimationFrame(onScroll)}},{passive:true});onScroll();

/* ---------- 밝은 · 어두운 화면: 앱과 같은 저장값(omr_theme) ---------- */
var thm=$('#thm');if(thm)thm.addEventListener('click',function(){var t=H.dataset.theme==='light'?'dark':'light';H.dataset.theme=t;try{localStorage.setItem('omr_theme',t)}catch(e){}if(window.__rebuild)window.__rebuild()});

/* ---------- 요금제: 개발자 탭 「요금제」(site_config 의 pricing). 못 읽으면 HTML 기본값 그대로 ---------- */
var plansEl=$('#plans'),PL=null;
function topIdx(n,pl){var h=pl?pl.findIndex(function(x){return x.hl}):-1;return h>=0?h:n-1}
function needUpd(){var cards=$$('.plan',plansEl),n=cards.length,sel=$$('.need [aria-pressed=true]'),out=$('#needO');
 if(!sel.length){cards.forEach(function(c){c.classList.remove('hit','dim')});out.textContent='고른 기능이 없어요. 위에서 필요한 기능을 눌러 보세요.';return}
 var lv=Math.min(n-1,Math.max.apply(null,sel.map(function(b){return +b.dataset.lv})));
 cards.forEach(function(c,i){c.classList.toggle('hit',i===lv);c.classList.toggle('dim',i<lv)});
 if(!cards[lv])return;var nm=$('h3',cards[lv]).firstChild.textContent.trim();out.innerHTML='고른 '+sel.length+'가지가 모두 들어 있는 요금제는 <b>'+esc(nm)+'</b>예요.'+(n===3&&lv===1?' 학생은 50명까지 등록할 수 있어요.':'')}
$$('.need button').forEach(function(b){b.addEventListener('click',function(){b.setAttribute('aria-pressed',String(b.getAttribute('aria-pressed')!=='true'));needUpd()})});
(function(){if(!plansEl||!window.fetch)return;
 var U='https://airejqudbqfsfhadvwqp.supabase.co',K='sb_publishable_YPbHe6NNnV5eQT0u1SZiCg_JLvrM7IV';
 fetch(U+'/rest/v1/site_config?key=eq.pricing&select=value',{headers:{apikey:K}}).then(function(r){return r.ok?r.json():null}).then(function(j){
  var v=j&&j[0]&&j[0].value;if(!v||!v.plans||!v.plans.length)return;PL=v.plans;
  var ct=String(v.contact||'').trim(),ctHref=/^https?:\/\//i.test(ct)?ct:'contact.html',top=topIdx(PL.length,PL);
  var who=['학생 최대 30명','학생 최대 50명 · 이후 1명당 추가 요금','학생 수 제한 없음'];
  plansEl.innerHTML=PL.map(function(x,i){var p=String(x.price||'').trim(),num=/^[\d,]+$/.test(p),ask=/문의/.test(x.cta||'')&&ctHref,isTop=i===top;
   var n0=num?+p.replace(/,/g,''):-1,price=p?(n0===0?'무료':num?n0.toLocaleString('ko-KR')+'원':esc(p)):'';num=num&&n0>0;
   return '<article class="plan'+(isTop?' top':'')+'" data-i="'+i+'"><h3>'+esc(x.name)+'</h3><p class="price">'+(price?'<b>'+price+'</b>'+(num&&x.unit?'<small>'+esc(x.unit)+'</small>':''):'<b class="tbd">요금 준비 중</b>')+'</p>'+(x.desc?'<p class="pd">'+esc(x.desc)+'</p>':'')+
    (PL.length===3?'<p class="who">'+who[i]+'</p>':'')+((x.items||[]).length?'<ul>'+x.items.map(function(t){return '<li>'+esc(t)+'</li>'}).join('')+'</ul>':'<ul></ul>')+
    '<a class="btn '+(isTop?'yel':'line')+'" href="'+(ask?esc(ctHref):'index.html?app=1#login')+'"'+(ask?'':' data-app')+'>'+esc(x.cta||'무료로 시작하기')+'</a></article>'}).join('');
  var note=$('#prNote');if(note)note.textContent=v.note||'';
  
  needUpd()}).catch(function(){})})();

/* ---------- 밝은 면(요금제 · 질문 · 바닥글, 정적 모드의 마지막 장면) 위에서는 머리글도 밝게 ---------- */
function watchLight(cine){if(!('IntersectionObserver' in window))return;
 var io=new IntersectionObserver(function(es){es.forEach(function(e){lightSecs+=e.isIntersecting?1:-1;if(lightSecs<0)lightSecs=0});theme()},{rootMargin:'0px 0px -96% 0px'});
 $$('.sec,.ft'+(cine?'':',.sc-end')).forEach(function(s){io.observe(s)})}

/* ---------- 목차: 지금 보고 있는 구역(실제 교차 결과)에 aria-current ---------- */
(function(){if(!('IntersectionObserver' in window))return;var links=$$('.nav a[href^="#"]'),seen={};
 var io=new IntersectionObserver(function(es){es.forEach(function(e){seen[e.target.id]=e.isIntersecting});var cur=null;links.forEach(function(a){if(seen[a.getAttribute('href').slice(1)])cur=a});links.forEach(function(a){if(a===cur)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')})},{rootMargin:'-45% 0px -45% 0px'});
 links.forEach(function(a){var t=D.getElementById(a.getAttribute('href').slice(1));if(t)io.observe(t)})})();

/* ---------- 시네마틱 모드를 켤 수 있나 ---------- */
var rm=matchMedia('(prefers-reduced-motion: reduce)');
var nav2=navigator,low=(nav2.hardwareConcurrency&&nav2.hardwareConcurrency<=2)||(nav2.deviceMemory&&nav2.deviceMemory<=2)||(nav2.connection&&nav2.connection.saveData);
var can=!!(window.gsap&&window.CSS&&CSS.supports('transform-style','preserve-3d'))&&!rm.matches&&!low;
if(rm.addEventListener)rm.addEventListener('change',function(){location.reload()});
if(!can){watchLight(false);return}
H.classList.add('cine');watchLight(true);
var gsap=window.gsap;

/* 문제은행 장면에 쓰는 실제 문항(bank/data.js 의 코드 · 단원 · 유형 · 난이도 · 발문 앞부분) */
var QS=[["Q31-032","Ⅲ-A","연소·생성·분해·용해·기화 엔탈피의 정의","하","그림은 25 ℃, 1기압에서 C(s, 흑연)의 연소 반응의 엔탈피 변화를 나타낸 것이다."],
["Q32-016","Ⅲ-B","열화학 반응식의 조합(헤스 법칙 계산)","중","다음은 25 ℃, 1기압에서 3가지 반응의 열화학 반응식이다."],
["Q41-056","Ⅳ-A","반응 속도식·반응 차수·반응 속도 상수","중","A(g)와 B(g)가 반응하는 반응의 반응 속도식은 v = k[A]ᵐ[B]ⁿ이다."],
["Q42-013","Ⅳ-B","유효 충돌의 조건","하","다음은 유효 충돌과 활성화 에너지에 대한 세 학생의 대화이다."],
["Q43-040","Ⅳ-C","온도와 반응 속도","상","표는 3개의 동일한 강철 용기에 같은 양의 A(g)를 넣고 반응시킨 실험이다."],
["Q33-018","Ⅲ-C","엔트로피가 증가·감소하는 경우","하","다음은 생활 주변에서 관찰할 수 있는 3가지 현상이다."],
["Q42-042","Ⅳ-B","반응 진행에 따른 에너지(엔탈피) 도표 해석","중","어떤 반응의 정반응의 활성화 에너지는 120 kJ이고 반응 엔탈피는 +80 kJ이다."],
["Q41-031","Ⅳ-A","반응 계수와 농도 변화량의 관계","하","A(g) → 2B(g) + 3C(g) 반응에서 B(g)의 농도 변화 속도를 비교한다."],
["Q31-041","Ⅲ-A","연소·생성·분해·용해·기화 엔탈피의 정의","중","다음은 25 ℃, 1기압에서 3가지 반응의 열화학 반응식이다."],
["Q43-024","Ⅳ-C","온도와 반응 속도","중","다음은 A(g)로부터 B(g)가 생성되는 반응의 화학 반응식이다."],
["Q41-121","Ⅳ-A","1차 반응과 반감기","상","A(g) → 2B(g) 반응(1차 반응)에서 강철 용기에 A(g)를 넣었다."],
["Q33-033","Ⅲ-C","엔트로피가 증가·감소하는 경우","중","그림은 25 ℃에서 설탕이 물에 자발적으로 용해되는 변화를 나타낸 것이다."],
["Q43-044","Ⅳ-C","촉매와 반응 속도","하","촉매에 대한 설명으로 옳은 것만을 보기에서 있는 대로 고른 것은?"],
["Q42-028","Ⅳ-B","활성화 에너지와 활성화물","상","다음은 A(g)로부터 B(g)가 생성되는 반응의 열화학 반응식이다."],
["Q32-044","Ⅲ-B","열화학 반응식의 조합(헤스 법칙 계산)","상","다음은 25 ℃, 1기압에서 2가지 반응의 열화학 반응식이다."]];
var DOTS={'하':1,'중':2,'상':3,'최':4};
/* 오답 분석 장면: 실제 화면(취약 유형 지도 · 채점 결과)에 보이는 예시 학습 데이터 그대로 */
var BARS=[["연소·생성·분해·용해·기화 엔탈피의 정의",25,'#ff5d52'],["생성 엔탈피로 반응 엔탈피 구하기",40,'#ff5d52'],["결합 에너지와 반응 엔탈피",67,'#f5b400'],["발열·흡열 반응과 ΔH의 부호",86,'#30c060'],["열화학 반응식의 표기(상태·조건·계수·역반응)",100,'#30c060']];

/* ---------- 3D 무대 만들기 ---------- */
var stage=$('#stage'),film=$('#film'),filmBg=$('.film-bg');
var IMG=function(src,s,cls){return '<img data-src="intro/'+src+'.webp" data-s="'+s+'" alt="" decoding="async"'+(cls?' class="'+cls+'"':'')+'>'};
function slabEdges(n){var h='';for(var i=0;i<n;i++)h+='<i class="ed" style="transform:translateZ(calc(var(--t)*'+(i/(n-1)-.5).toFixed(3)+'))"></i>';return h}
function kbd(){var h='',i;for(i=0;i<14;i++)h+='<i></i>';for(var r=0;r<3;r++){for(i=0;i<12;i++)h+='<i></i>';h+='<i class="w2"></i>'}h+='<i class="w2"></i>';for(i=0;i<10;i++)h+='<i></i>';h+='<i class="w2"></i>';for(i=0;i<3;i++)h+='<i></i>';h+='<i class="w6"></i>';for(i=0;i<5;i++)h+='<i></i>';return h}
function stripHTML(n,i){if(i>=n)return '';var w='calc(var(--w)/'+n+' + .6px)';
 return '<div class="st"'+(i===0?' style="width:'+w+'"':'')+'><div class="face f" style="background-image:var(--f);background-size:var(--w) var(--h);background-position:calc(var(--w)/'+n+'*-'+i+') 0"><i class="sd"></i></div><div class="face k" style="background-image:var(--k);background-size:var(--w) var(--h);background-position:calc(var(--w)/'+n+'*-'+(n-1-i)+') 0"><i class="sd"></i></div>'+stripHTML(n,i+1)+'</div>'}
function bookBox(cover,color,spine){return '<div class="bk"><div class="face back" style="background:'+color+'"></div><i class="ee r"></i><i class="ee t"></i><i class="ee b"></i><div class="spine" style="background:'+color+'"><span>'+spine+'</span></div><div class="face cv" data-bg="intro/'+cover+'.webp"></div></div>'}

var M,vw,vh,u,S={},tl,leaves=[],zs=[],built=false,total=2320;
function zsync(){zs.forEach(function(z){var v=+gsap.getProperty(z.o,'scaleX');if(Math.abs(v-z.s)>.0005){z.s=v;z.w.style.transform='scaleZ('+v.toFixed(4)+')'}})}
function sizes(){vw=innerWidth;vh=stage.clientHeight||innerHeight;M=vw<861;
 u=M?Math.min(vw*.0145,vh*.0075):Math.min(vw*.01,vh*.0165);H.style.setProperty('--u',u.toFixed(2)+'px');
 S.xdr=M?vw*.92:64*u;S.mac=M?vw*.8:50*u;S.pad=M?vw*.46:24*u;S.phone=M?Math.min(vw*.42,vh*.2):15*u;S.book=M?vw*.42:21*u;S.sheet=M?vw*.62:25*u;
 S.tw=M?Math.floor((vw*.92-16)/3):150;S.th=M?62:122;S.cols=M?3:5;S.gap=M?8:12;S.aw=M?Math.min(vw*.88,420):400}

function build(){
 stage.innerHTML='';leaves=[];loadedS=-1;
 var NS=M?6:12,NE=M?4:6;
 var h='<div class="rig" id="rig">';
 /* Pro Display XDR */
 h+='<div class="obj xdr" id="xdr" style="--w:'+S.xdr+'px"><div class="xdr-in" id="xdrIn"><i class="glow"></i><i class="arm"></i><i class="arm-b"></i><i class="foot"></i><i class="foot-e"></i><div class="xdr-body"><div class="face f-back"></div><div class="face f-l"></div><div class="face f-r"></div><div class="face f-t"></div><div class="face f-b"></div><div class="face f-front"><div class="scr" data-ui>'+
  IMG('xdr-dash',0,'on')+IMG('xdr-cls',1)+IMG('xdr-build',1)+IMG('xdr-dash',6,'a8')+IMG('xdr-stu',6)+IMG('xdr-cls',6,'a8c')+IMG('xdr-cns',6)+IMG('xdr-weak',7)+
  '<i class="pw" style="position:absolute;inset:0;background:#000"></i></div><i class="sheen"></i></div></div></div></div>';
 /* 문제은행 카드 · 학습지 */
 h+='<div class="obj qb" id="qb" data-ui><div class="qf" id="qf"><span>물질과 에너지</span><span>Ⅲ 반응 엔탈피</span><span>Ⅳ 반응 속도</span><span>난이도 하</span><span>중</span><span>상</span></div>';
 QS.forEach(function(q,i){var d=DOTS[q[3]],dots='';for(var k=1;k<=4;k++)dots+=k<=d?'●':'<span class="o">●</span>';
  h+='<div class="qt" data-i="'+i+'" style="--tw:'+S.tw+'px;--th:'+S.th+'px"><div class="q1"><span class="code">'+q[0]+'</span><span class="dots" aria-hidden="true">'+dots+'</span></div><div class="ty">'+esc(q[2])+'</div><div class="sx">'+esc(q[4])+'</div></div>'});
 h+='<div class="qcount" id="qcount">반응 속도 · 중 이상 6문항으로 학습지 만들기</div></div>';
 h+='<div class="obj sheet" id="sheet" style="--w:'+S.sheet+'px"><div class="pp"><div class="face f" data-bg="intro/book-sheet.webp"><i class="sd"></i></div><div class="face k"><i class="sd"></i></div></div></div>';
 /* 교재 */
 h+='<div class="obj book" id="bookO" style="--w:'+S.book+'px"><div class="bk"><div class="face back"></div><i class="ee r"></i><i class="ee t"></i><i class="ee b"></i><div class="spine"><span>물질과 에너지 개념서</span></div><div class="pg base" data-bg="intro/book-answer.webp"></div>';
 [['book-basic','book-problem'],['book-concept','book-ox'],['cover-me-c','book-toc']].forEach(function(p,i){h+='<div class="leaf'+(i===2?' cover':'')+'" data-f="intro/'+p[0]+'.webp" data-k="intro/'+p[1]+'.webp" style="transform:translateZ('+((i+1)*1.4)+'px)">'+stripHTML(i===2?1:NS,0)+'</div>'});
 h+='</div></div>';
 [['cover-me-t','#2b6fc0','물질과 에너지 유형서'],['cover-cm-c','#2e9b57','세포와 물질대사 개념서'],['cover-cm-t','#2e9b57','세포와 물질대사 유형서'],['mock-cover','#1d3f73','전범위 모의고사']].forEach(function(b,i){h+='<div class="obj mb book" id="mb'+i+'" style="--w:'+S.book+'px">'+bookBox(b[0],b[1],b[2])+'</div>'});
 /* MacBook */
 h+='<div class="obj mac" id="mac" style="--w:'+S.mac+'px"><div class="mac-base"><div class="face deck"><div class="kbd">'+kbd()+'</div><div class="tpad"></div></div><div class="face under" style="backface-visibility:visible"></div></div><i class="bf"></i><i class="bs l"></i><i class="bs r"></i>'+
  '<div class="mac-lid" id="lid"><div class="face lid-b"></div><div class="face lid-f"><div class="scr" data-ui>'+IMG('mac-thome',3,'on')+IMG('mac-diag',5)+IMG('mac-stu',6)+'</div><i class="notch"></i></div></div></div>';
 /* iPad */
 h+='<div class="obj pad-o" id="pad"><div class="slab pad" style="--w:'+S.pad+'px">'+slabEdges(NE)+'<div class="face bk"><i class="cam"></i></div><div class="face fr"><div class="scr" data-ui>'+IMG('cover-me-c',3,'on')+IMG('pad-home',3)+IMG('pad-stat',7)+'<div class="kio">'+IMG('kiosk',6,'on')+'</div></div></div></div></div>';
 /* iPhone */
 h+='<div class="obj ph-o" id="phone"><div class="slab phone" style="--w:'+S.phone+'px">'+slabEdges(NE+1)+'<div class="btns" aria-hidden="true"><i></i><i></i><i></i></div><div class="face bk"><i class="lens"></i></div><div class="face fr"><div class="scr" data-ui>'+IMG('phone-omr',4,'on')+IMG('phone-result',4,'res')+IMG('phone-weak',4)+IMG('phone-parent',7)+IMG('phone-home',7)+
  '<div class="scan">'+IMG('book-problem',4,'cam')+'<div class="camtop">교재 · 학습지의 QR 찍기</div><div class="fr4"><i></i><i></i><i></i><i></i><b class="line"></b></div><span class="lab">QR 인식 · 이 쪽 문항을 불러와요</span></div><div class="burst"><b></b>'+new Array(15).join('<i></i>')+'</div></div><i class="island"></i></div></div></div>';
 /* 오답 분석 */
 h+='<div class="obj ana" id="ana" data-ui><div class="agrp" style="--aw:'+S.aw+'px"><h3>틀린 문항 · 유형별로 모으기</h3><p class="tt">연소·생성·분해·용해·기화 엔탈피의 정의</p><div class="slots"><i></i><i></i><i></i></div><p class="why"><span>진술 오판단 2</span><span>개념 혼동 1</span></p></div>'+
  '<div class="abars" style="--aw:'+S.aw+'px"><h3>유형별 정답률 · 솔비 학생</h3><ol>'+BARS.map(function(b){return '<li><span>'+esc(b[0])+'</span><i><b style="--c:'+b[2]+'"></b></i><em>'+b[1]+'%</em></li>'}).join('')+'</ol></div>'+
  ['43번','47번','51번'].map(function(t){return '<span class="chip">'+t+'</span>'}).join('')+'</div>';
 h+='</div>';
 h+='<div class="veil" id="veil"></div>';
 stage.innerHTML=h;
 /* GSAP 의 scale 은 가로 · 세로만 줄인다. 기기 · 책의 두께(z)도 같이 줄도록 안쪽 껍질에 scaleZ 를 건다(줄인 노트북 바닥판이 화면보다 크게 보이던 원인) */
 zs=[];$$('.obj',stage).forEach(function(o){if(o.matches('.qb,.ana'))return;var w=D.createElement('div');w.className='zs';while(o.firstChild)w.appendChild(o.firstChild);o.appendChild(w);zs.push({o:o,w:w,s:-1})});
 $$('.leaf',stage).forEach(function(l){leaves.push({el:l,st:$$('.st',l),sd:$$('.sd',l),rigid:l.classList.contains('cover'),t:0,z:parseFloat(l.style.transform.slice(11))})});
 built=true}

/* 이미지는 그 장면이 다가올 때 받는다 */
var loadedS=-1;
function loadUpTo(s){if(s<=loadedS)return;loadedS=s;
 $$('img[data-src]',stage).forEach(function(im){if(+im.dataset.s<=s){im.src=im.dataset.src;im.removeAttribute('data-src')}});
 $$('[data-bg]',stage).forEach(function(e){var sc=e.closest('.sheet')?1:2;if(sc<=s){e.style.backgroundImage='url('+e.dataset.bg+')';e.removeAttribute('data-bg')}});
 if(s>=2)leaves.forEach(function(L){if(!L.on){L.on=1;L.el.style.setProperty('--f','url('+L.el.dataset.f+')');L.el.style.setProperty('--k','url('+L.el.dataset.k+')')}})}

/* 책장 넘기기: 잎 전체는 책등을 축으로 돌고, 띠마다 조금씩 더 돌아 종이가 휜다 */
function setLeaf(L,t){L.t=t;var th=-180*t,b=L.rigid?0:-46*Math.sin(Math.PI*t)/L.st.length;
 /* 넘긴 잎은 왼쪽 더미에서 먼저 넘긴 것이 아래로 가도록 깊이를 뒤집는다 */
 L.el.style.transform='translateZ('+(L.z*(1-2*t)).toFixed(2)+'px) rotateY('+th.toFixed(2)+'deg)';
 for(var i=0;i<L.st.length;i++){var s=L.st[i];if(i>0||!L.rigid)s.style.transform=i===0?'':'rotateY('+b.toFixed(2)+'deg)';var a=(th+b*i)*Math.PI/180,o=((L.rigid?.1:.22)*Math.abs(Math.sin(a))).toFixed(3);s.children[0].children[0].style.opacity=o;s.children[1].children[0].style.opacity=o}}

function timeline(){
 var X=function(id){return $('#'+id,stage)},xdr=X('xdr'),xin=X('xdrIn'),qb=X('qb'),sheet=X('sheet'),book=X('bookO'),mac=X('mac'),lid=X('lid'),pad=X('pad'),phone=X('phone'),ana=X('ana'),rig=X('rig'),veil=X('veil');
 var mbs=[0,1,2,3].map(function(i){return X('mb'+i)});
 var cps={};$$('.sc').forEach(function(s){cps[s.dataset.scene]=$('.cp',s)});
 var xs=$$('.scr img',xdr),pw=$('.pw',xdr);
 var ms=$$('.scr img',mac),ps=$$('.scr>img',pad),kio=$('.kio',pad),fs=$$('.scr>img',phone),scan=$('.scan',phone),line=$('.line',scan),fr4=$('.fr4',scan),lab=$('.lab',scan),burst=$$('.burst i',phone),ring=$('.burst b',phone);
 var tiles=$$('.qt',qb),qf=$$('.qf span',qb),qcount=X('qcount'),chips=$$('.chip',ana),agrp=$('.agrp',ana),abars=$('.abars',ana),bars=$$('.abars b',ana),why=$$('.why span',ana);
 var heroCp=cps.hero,heroKids=[$('h1',heroCp),$('p',heroCp)],cue=$('.cue');
 var P=function(d,m){return M?m:d};
 /* 가로 배치 기준 폭: 기기 크기(u)와 같은 비율로. 아주 넓은 화면에서 기기가 바깥으로 퍼져 잘리지 않게 */
 var LW=M?vw:Math.min(vw,u*100),HD=hd.offsetHeight||64;
 /* 기기를 둘 자리: 왼쪽 문구 장면은 문구 오른쪽, 가운데 문구 장면(과 휴대폰)은 문구 아래. 문구와 기기가 겹치지 않게 실제 문구 크기로 잰다.
    좌표는 무대 가운데가 0 인 rig 좌표(l · t = 왼쪽 위, x · y = 가운데) */
 function area(name,mid){var cp=cps[name],top=parseFloat(getComputedStyle(cp).top)||HD,x0,x1,y0,y1;
  if(M||mid){y0=top+cp.offsetHeight+(M?.025:.04)*vh;y1=vh-(M?.03:.04)*vh;x0=M?.04*vw:parseFloat(getComputedStyle(cp).marginLeft)||24;x1=vw-x0}
  else{x0=cp.getBoundingClientRect().right+.035*vw;x1=vw-Math.max(.03*vw,16);y0=HD+.035*vh;y1=vh-.05*vh}
  if(y1-y0<vh*.28)y0=y1-vh*.28;
  return {l:x0-vw/2,t:y0-vh/2,w:x1-x0,h:y1-y0,x:(x0+x1)/2-vw/2,y:(y0+y1)/2-vh/2}}
 /* 원근(perspective)을 되돌린 위치: 깊이 z 에 두어도 화면에서는 (x, y) 에 크기 s 로 보이게 */
 var PER=parseFloat(getComputedStyle(stage).perspective)||3400,OY=.05*vh;
 var Z=function(x,y,z,s,o){var f=PER/(PER-z),r={x:x/f,y:(y+OY)/f-OY,z:z,scale:s/f};for(var k in o)r[k]=o[k];return r};
 /* 기기별 화면 위 크기(너비 W 기준): XDR 은 받침대까지 .756W(화면 가운데에서 위 .287W · 아래 .469W),
    MacBook 은 경첩에서 위 .665W · 아래 .30W, iPad 는 W × 1.4065W, iPhone 은 W × 2.049W */
 var XH=.756;

 /* 첫 화면: 히어로 문구 아래 남는 공간에 디스플레이 + 받침대를 맞춘다 */
 var cb=heroCp.getBoundingClientRect().bottom-heroCp.parentNode.getBoundingClientRect().top,gap=P(.035,.04)*vh,avail=vh-cb-gap-P(.15,.14)*vh,grp=S.xdr*XH;
 var s0=Math.min(avail/grp,P(.66,.98)*LW/S.xdr),dispY=cb+gap-vh/2+S.xdr*.287*s0;
 tl=gsap.timeline({defaults:{ease:'none',duration:20},paused:true});
 var at=function(t,target,vars,dur){vars.duration=dur==null?20:dur;tl.to(target,vars,t);return tl};
 gsap.set([qb,sheet,book,mac,pad,phone,ana].concat(mbs),{autoAlpha:0});
 gsap.set(xdr,{autoAlpha:1,y:dispY,scale:s0});

 /* SCENE 02: 디스플레이가 문구 옆으로 비켜서며 돌아선다. 문구는 왼쪽, 대시보드는 오른쪽 — 겹치지 않는다 */
 tl.fromTo(cue,{autoAlpha:1},{autoAlpha:0,duration:24,immediateRender:false},0);
 var a2=area('ops'),s2=Math.min(a2.w*P(.97,.96)/S.xdr,a2.h*P(.9,.94)/(XH*S.xdr)),x2=a2.x,y2=a2.y-.091*S.xdr*s2;
 at(12,xdr,{x:x2,y:y2,scale:s2,rotationY:P(-14,0),rotationX:P(3,0),ease:'power2.inOut'},84);
 if(!M)at(96,xdr,{rotationY:-4,rotationX:0,ease:'sine.inOut'},176);
 at(204,xs[1],{opacity:1},12);
 at(258,xs[2],{opacity:1},12);
 /* SCENE 03: 문제은행 */
 at(272,xdr,{scale:s2*.62,y:y2-P(.06,.1)*vh,z:-380,ease:'power2.inOut'},52);
 at(318,xdr,{autoAlpha:0},22);
 var a3=area('bank'),cols=S.cols,rows=Math.ceil(tiles.length/cols),gw=cols*S.tw+(cols-1)*S.gap,gh=rows*S.th+(rows-1)*S.gap;
 var qs=M?1:Math.min(1,a3.w*.96/gw,a3.h*.8/(gh+110)),qX=a3.x,qY=a3.y+P(8,6);
 gsap.set(qb,{x:qX,y:qY,scale:qs});
 var qfEl=$('.qf',qb);qfEl.style.left='0px';qfEl.style.top=(-gh/2-16)+'px';qcount.style.left='0px';qcount.style.top=(gh/2+18)+'px';
 at(296,qb,{autoAlpha:1},6);
 gsap.set(qfEl,{autoAlpha:0});at(300,qfEl,{autoAlpha:1},16);
 var pos=tiles.map(function(t,i){var c=i%cols,r=Math.floor(i/cols);return {x:-gw/2+c*(S.tw+S.gap),y:-gh/2+r*(S.th+S.gap)}});
 tiles.forEach(function(t,i){gsap.set(t,{x:(x2-qX)/qs-S.tw/2+(i%cols-cols/2)*14,y:(y2-P(.06,.1)*vh-qY)/qs-S.th/2,z:-420,scale:.3,autoAlpha:0});
  tl.to(t,{x:pos[i].x,y:pos[i].y,z:0,scale:1,autoAlpha:1,duration:34,ease:'power2.out'},296+i*1.6)});
 var ACC=cssv('--acc'),AINK=cssv('--acc-ink'),INK=cssv('--ink-d'),MUTE=cssv('--mute-d');
 var on=function(sp,t){tl.to(sp,{backgroundColor:ACC,color:AINK,duration:6},t)};
 on(qf[0],330);on(qf[2],350);on(qf[4],372);on(qf[5],374);
 var unitIV=function(i){return QS[i][1].charAt(0)==='Ⅳ'},sel=[];
 tiles.forEach(function(t,i){if(!unitIV(i))tl.to(t,{autoAlpha:.14,scale:.94,z:-60,duration:12},352);else if(QS[i][3]==='하')tl.to(t,{autoAlpha:.14,scale:.94,z:-60,duration:12},375);else sel.push(t)});
 sel.forEach(function(t){tl.to(t,{boxShadow:'0 0 0 3px '+ACC,duration:8},384)});
 at(388,qcount,{opacity:1},8);
 /* 고른 문항이 학습지 한 장으로 모인다 */
 var sw2=S.sheet,shH=sw2*1.414,ss=M?1:Math.min(1,a3.h*.86/shH,a3.w*.6/sw2);
 gsap.set(sheet,{x:qX,y:qY,scale:.7*ss,z:-120});
 at(398,sheet,{autoAlpha:1,scale:ss,z:0,ease:'power2.out'},20);
 tiles.forEach(function(t){if(sel.indexOf(t)<0)tl.to(t,{autoAlpha:0,duration:10},398)});
 at(398,qfEl,{autoAlpha:0},10);at(424,qcount,{opacity:0},8);
 sel.forEach(function(t,k){var c=k%2,r=Math.floor(k/2);tl.to(t,{x:((c?.06:-.44)*sw2-S.tw*.1)*ss/qs,y:(-.36+r*.22)*shH*ss/qs,scale:.36*ss/qs,z:6,duration:30,ease:'power2.inOut'},404+k*2);tl.to(t,{autoAlpha:0,duration:10},430+k*2)});
 var sd=$$('.sd',sheet);
 at(446,sheet,{x:qX,y:a3.y+P(0,.04)*vh,z:P(150,60),rotationX:-10,rotationY:-28,rotationZ:3,ease:'power2.inOut'},34);
 at(446,sd,{opacity:.12},34);
 at(482,sheet,{rotationY:26,rotationX:8,rotationZ:-2,ease:'sine.inOut'},40);
 at(482,sd,{opacity:.05},40);
 at(524,sheet,{y:-vh*.9,rotationX:42,autoAlpha:0,ease:'power2.in'},28);

 /* SCENE 04: 살아 움직이는 교재(펼친 두 쪽이 문구 오른쪽에 들어오는 크기) */
 var a4=area('book'),bw=S.book,sb=M?1:Math.min(1,a4.w*.9/(2*bw),a4.h*.84/(bw*1.414)),bwS=bw*sb,bX=a4.x,bY=a4.y;
 gsap.set(book,{x:bX-bwS/2,y:vh*.85,scale:sb,rotationX:62,rotationY:-40,rotationZ:12});
 /* 잎의 상태는 타임라인 시간에서 바로 계산한다(되감기 · 건너뛰기에도 어긋나지 않게) */
 var ease=gsap.parseEase('sine.inOut'),leafTo=function(L,v,t,d){(L.k||(L.k=[])).push([t,d,v])};
 var LC=leaves[2],L1=leaves[1],L0=leaves[0];
 at(546,book,{autoAlpha:1},10);
 at(546,book,{y:bY,rotationX:14,rotationY:-24,rotationZ:0,ease:'power2.out'},56);
 at(604,book,{rotationX:6,rotationY:-8,ease:'sine.inOut'},22);
 leafTo(LC,1,628,44);at(628,book,{x:bX,rotationY:0,rotationX:4,ease:'sine.inOut'},44);
 leafTo(L1,1,678,54);leafTo(L0,1,738,54);
 at(796,book,{rotationY:-30,rotationX:24,z:70,ease:'sine.inOut'},34);
 at(832,book,{rotationY:0,rotationX:4,z:0,ease:'sine.inOut'},24);
 leafTo(L0,0,858,18);leafTo(L1,0,866,18);leafTo(LC,0,874,20);
 at(874,book,{x:bX-bwS/2},20);
 var pg=$$('.pages span',cps.book),pgOn=function(i,a,b){tl.to(pg[i],{color:INK,duration:6},a);tl.to(pg[i],{color:MUTE,duration:6},b)};
 pgOn(0,560,640);pgOn(1,650,722);pgOn(2,650,722);pgOn(3,724,782);pgOn(4,724,782);pgOn(5,784,860);pgOn(6,784,860);
 /* 책이 닫히고 여러 권이 한 줄로 정돈된다 */
 var sR=Math.min(P(.6,.4),a4.w*.96/(5.4*bw)),step=bw*sR*1.1,slots=[-2,-1,1,2],lY=bY+P(.02,.02)*vh;
 at(890,book,{x:bX-bw*sR/2,y:lY,scale:sR,rotationY:-10,rotationX:6,ease:'power2.inOut'},34);
 mbs.forEach(function(m,i){gsap.set(m,{x:bX+slots[i]*step*1.8-bw*sR/2,y:lY+30,scale:sR,rotationY:-10,rotationX:6});
  tl.to(m,{autoAlpha:1,duration:12},896+i*3);tl.to(m,{x:bX+slots[i]*step-bw*sR/2,y:lY,duration:30,ease:'power2.out'},896+i*3)});

 /* SCENE 05: 교재 → 태블릿 → 노트북(문구 오른쪽에서) */
 var a5=area('device');
 mbs.forEach(function(m,i){tl.to(m,{x:'+='+(slots[i]<0?-1:1)*a5.w*.18,y:'+='+vh*.06,autoAlpha:0,duration:22,ease:'power2.in'},932)});
 var pS=Math.min(a5.h*.74/(1.4065*S.pad),a5.w*P(.42,.5)/S.pad),k=S.pad*pS*(1-2*.0303)/bw,padX=a5.x,padY=a5.y;
 at(936,book,{x:padX-bw*k/2,y:padY,scale:k,rotationY:0,rotationX:0,ease:'power2.inOut'},30);
 gsap.set(pad,{x:padX,y:padY,scale:pS});
 at(962,pad,{autoAlpha:1},16);at(976,book,{autoAlpha:0},8);
 at(990,ps[1],{opacity:1},14);
 at(1006,pad,{rotationY:360,y:padY-vh*.02,ease:'sine.inOut'},64);
 at(1006,pad,{rotationX:14,rotationZ:-5,ease:'sine.out'},32);at(1038,pad,{rotationX:4,rotationZ:0,ease:'sine.in'},32);
 /* 노트북은 뒤(z<0)에, 태블릿은 앞 오른쪽에. 노트북 바닥판이 앞으로 길게 나와 보이지 않게 위에서 살짝 내려다본다 */
 var Wm=Math.min(a5.w*P(.8,.9),a5.h*P(.84,.6)/.965),mZ=-Wm*.6,macX=a5.x-P(.1,0)*a5.w,macHy=a5.t+.665*Wm+P(.02,0)*a5.h;
 var Wp=Math.min(a5.h*P(.56,.5)/1.4065,a5.w*P(.3,.36)),padX2=a5.l+a5.w-Wp/2-.02*a5.w,padY2=a5.t+a5.h-Wp*1.4065/2-.03*a5.h;
 var macEnd=Z(macX,macHy,mZ,Wm/S.mac,{rotationX:-8,rotationY:P(5,0)});
 gsap.set(mac,Z(macX,vh*.95,mZ,Wm/S.mac,{rotationX:-8,rotationY:P(5,0)}));gsap.set(lid,{rotationX:-90});
 at(1072,pad,Z(padX2,padY2,60,Wp/S.pad,{rotationY:338,rotationX:4,ease:'power2.inOut'}),50);
 at(1076,mac,{autoAlpha:1},10);at(1076,mac,{y:macEnd.y,ease:'power2.out'},40);
 at(1090,lid,{rotationX:12,ease:'power2.inOut'},46);

 /* SCENE 06: OMR 채점 */
 var phY=P(.04,.035)*vh,phH=S.phone*2.049;
 at(1150,mac,{y:'+='+vh*.7,ease:'power2.in'},34);at(1166,mac,{autoAlpha:0},14);
 at(1150,pad,{x:'+='+vw*.5,ease:'power2.in'},34);at(1170,pad,{autoAlpha:0},14);
 gsap.set(phone,{y:vh*.9,rotationY:180,rotationZ:-10});
 at(1166,phone,{autoAlpha:1},10);
 at(1166,phone,{y:phY,rotationY:0,rotationZ:0,ease:'power2.out'},58);
 gsap.set(scan,{opacity:1});gsap.set(lab,{opacity:0});
 tl.fromTo(line,{top:'6%'},{top:'92%',duration:28,ease:'sine.inOut',immediateRender:false},1226);
 at(1254,$$('i',fr4),{borderColor:ACC},6);at(1254,line,{opacity:0},4);at(1254,lab,{opacity:1},6);
 at(1266,scan,{opacity:0},14);
 at(1290,fs[1],{opacity:1},10);
 burst.forEach(function(d,i){var a=i/burst.length*Math.PI*2,r=S.phone*(.34+.08*(i%3));gsap.set(d,{x:0,y:0,scale:.5});tl.to(d,{opacity:1,duration:3},1298);tl.to(d,{x:Math.cos(a)*r,y:Math.sin(a)*r,scale:1,duration:20,ease:'power2.out'},1298);tl.to(d,{opacity:0,duration:10},1310)});
 tl.fromTo(ring,{opacity:0,scale:.4},{opacity:1,scale:1,duration:6,immediateRender:false},1298);at(1304,ring,{opacity:0,scale:2.4,ease:'power1.out'},18);
 var dds=$$('.score > div',cps.omr);gsap.set(dds,{autoAlpha:0,y:20});
 var cnt=dds.map(function(d,i){var dd=$('dd',d);tl.to(d,{autoAlpha:1,y:0,duration:10},1304+i*10);return {dd:dd,n:+dd.dataset.n,u:dd.dataset.u||'',a:1304+i*10,last:-1}});
 at(1368,fs[2],{opacity:1},14);

 /* SCENE 07: 오답 분석과 맞춤형 학습(휴대폰은 문구 오른쪽 자리의 왼쪽, 분석 카드는 그 오른쪽) */
 var a7=area('wrong'),Wph=Math.min(a7.h*.68/2.049,a7.w*.26),phS7=P(Wph/S.phone,.55),phX7=P(a7.l+Wph/2+.02*a7.w,-.3*LW),phY7=P(a7.y+.04*a7.h,a7.y+.1*vh);
 var anaS=M?1:Math.min(1,(a7.w-Wph-.1*a7.w)/S.aw,a7.h*.92/460),aX=P(a7.l+a7.w-S.aw*anaS/2-.02*a7.w,0),aY=a7.y;
 at(1420,fs[2],{opacity:0},12);
 at(1420,phone,{x:phX7,y:phY7,rotationY:P(14,0),scale:phS7,ease:'power2.inOut'},30);
 at(1430,fs[1],{scale:1.75,transformOrigin:'50% 84%',ease:'power2.inOut'},26);
 gsap.set(ana,{x:aX,y:aY,scale:anaS});
 var gH=agrp.offsetHeight,bH=abars.offsetHeight,gy=-(gH+bH+16)/2+gH/2,by=gy+gH/2+16+bH/2;
 gsap.set([agrp,abars],{xPercent:-50,yPercent:-50});gsap.set(agrp,{x:0,y:gy});gsap.set(abars,{x:0,y:by});gsap.set(why,{autoAlpha:0});
 at(1440,ana,{autoAlpha:1},4);
 tl.fromTo(agrp,{autoAlpha:0,y:gy+24},{autoAlpha:1,y:gy,duration:16,immediateRender:false},1446);
 var slotsEl=$$('.slots i',agrp);
 chips.forEach(function(c,i){var sl=slotsEl[i];
  gsap.set(c,{xPercent:-50,yPercent:-50,x:(phX7-aX+(i-1)*S.phone*.3)/anaS,y:(phY7-aY+phH*phS7*.25)/anaS,scale:.6});
  tl.to(c,{opacity:1,duration:6},1452+i*5);var d=function(k){var a=sl.getBoundingClientRect(),q=c.getBoundingClientRect();return (k?a.top+a.height/2-q.top-q.height/2:a.left+a.width/2-q.left-q.width/2)/anaS+(k?gy-gsap.getProperty(agrp,'y'):0)};
  tl.to(c,{x:function(){return gsap.getProperty(c,'x')+d(0)},y:function(){return gsap.getProperty(c,'y')+d(1)},scale:1,duration:30,ease:'power3.inOut'},1452+i*5)});
 why.forEach(function(w,i){tl.to(w,{autoAlpha:1,duration:10},1494+i*6)});
 tl.fromTo(abars,{autoAlpha:0,y:by+24},{autoAlpha:1,y:by,duration:16,immediateRender:false},1512);
 bars.forEach(function(b,i){tl.to(b,{scaleX:BARS[i][1]/100,duration:26,ease:'power2.out'},1522+i*5)});
 at(1592,ana,{autoAlpha:0,scale:.92*anaS,x:aX+P(.03,0)*vw},20);
 /* 진단 화면을 띄운 노트북이 분석 카드 자리로 들어온다 */
 var Wm7=Math.min((a7.w-P(Wph,0))*P(.86,.9),a7.h*P(.8,.62)/.965),m7=Z(P(a7.l+a7.w-Wm7*.56-.03*a7.w,0),a7.t+.665*Wm7+P(.04,.02)*a7.h,-Wm7*.6,Wm7/S.mac,{rotationY:P(-5,0),rotationX:-8});
 at(1588,ms[1],{opacity:1},4);
 at(1596,mac,{y:m7.y,z:m7.z,scale:m7.scale,rotationY:m7.rotationY,rotationX:-8,ease:'power2.out'},44);
 tl.fromTo(mac,{x:vw*.7},{x:m7.x,duration:44,ease:'power2.out',immediateRender:false},1596);
 at(1596,mac,{autoAlpha:1},10);
 at(1600,fs[2],{opacity:1},14);
 if(M)at(1462,phone,{autoAlpha:0},14);

 /* SCENE 08: 학원 운영 — 뒤에 디스플레이(원생 · 시간표 · 상담), 앞 왼쪽 휴대폰(학부모), 앞 오른쪽 출결 단말 */
 var a8=area('academy');
 var W8=Math.min(a8.w*P(.84,.92),a8.h*P(.7,.56)/XH),x8=a8.x+P(.05,0)*a8.w,y8=a8.t+.287*W8+P(.02,0)*a8.h;
 var Wk=Math.min(a8.w*P(.42,.5),a8.h*.4*1.4065),kx=a8.l+a8.w-Wk/2,ky=a8.t+a8.h-Wk/1.4065/2;
 var Wf=Math.min(a8.h*P(.5,.44)/2.049,a8.w*.22),fx=a8.l+Wf/2+P(.08,.04)*a8.w,fy=a8.t+a8.h-Wf*2.049/2;
 at(1680,mac,{y:'+='+vh*.7,ease:'power2.in'},30);at(1696,mac,{autoAlpha:0},14);
 at(1680,phone,Z(fx,fy,140,Wf/S.phone,{rotationY:P(12,0),autoAlpha:1,ease:'power2.inOut'}),44);
 at(1680,fs[1],{opacity:0},10);at(1690,fs[3],{opacity:1},10);
 at(1690,xs[3],{opacity:1},2);
 tl.fromTo(xdr,{autoAlpha:0},{autoAlpha:1,duration:16,immediateRender:false},1690);
 at(1690,xdr,Z(x8,y8,-260,W8/S.xdr,{rotationY:P(-6,0),rotationX:0,ease:'power2.out'}),40);
 gsap.set(kio,{opacity:0});
 var k8=Z(kx,ky,80,Wk/1.4065/S.pad);
 tl.fromTo(pad,{x:vw*.75,y:k8.y,z:80,rotationY:360,rotationX:0,rotationZ:0,scale:k8.scale},{x:k8.x,rotationZ:-90,duration:44,ease:'power2.out',immediateRender:false},1684);
 at(1684,pad,{autoAlpha:1},10);at(1700,kio,{opacity:1},10);
 var lis=$$('.ops-list li',cps.academy),liOn=function(i,a,b){tl.to(lis[i],{color:ACC,duration:6},a);tl.to(lis[i],{color:INK,duration:6},b)};
 liOn(2,1730,1768);liOn(4,1752,1790);
 at(1790,xs[4],{opacity:1},12);liOn(0,1790,1830);
 at(1830,xs[5],{opacity:1},12);liOn(1,1830,1868);
 at(1868,xs[6],{opacity:1},12);liOn(3,1868,1904);

 /* SCENE 09: 전체 제품 생태계 — 가운데 문구가 올라오는 동안 기기는 비켜 내려갔다가, 문구 아래에 한 줄로 선다 */
 [xdr,pad,phone].forEach(function(o){at(1918,o,{y:'+='+vh*.55,autoAlpha:0,ease:'power2.in'},30)});
 var a9=area('eco',true);
 var W9=Math.min(a9.h*.9/XH,LW*P(.4,.78)),x9=a9.x,y9=a9.t+.287*W9;
 var Wm9=Math.min(W9*P(.66,.6),a9.h*.6/.965),mx9=Math.max(x9-W9*.5-Wm9*.12,-vw/2+Wm9/2+.03*vw),my9=a9.t+a9.h-.3*Wm9-.02*a9.h;
 var Wp9=Math.min(a9.h*.64/1.4065,W9*.34),px9=Math.min(x9+W9*.5+Wp9*.2,vw/2-Wp9/2-.03*vw),py9=a9.t+a9.h-Wp9*1.4065/2;
 var Wf9=Math.min(a9.h*.44/2.049,W9*P(.2,.17)),fx9=x9+W9*P(.26,.2),fy9=a9.t+a9.h-Wf9*2.049/2;
 var E={x:Z(x9,y9,-320,W9/S.xdr,{rotationY:0}),m:Z(mx9,my9,-Wm9*.55,Wm9/S.mac,{rotationY:P(6,4),rotationX:-8}),p:Z(px9,py9,40,Wp9/S.pad,{rotationZ:0,rotationY:340,rotationX:0}),f:Z(fx9,fy9,160,Wf9/S.phone,{rotationY:-10})};
 var rise=function(o,v,t){var y=v.y;v=Object.assign({},v);delete v.y;tl.set(o,Object.assign(v,{y:y+vh*.4}),t);at(t+4,o,{y:y,autoAlpha:1,ease:'power2.out'},48)};
 tl.set(ms[2],{opacity:1},1990);tl.set(kio,{opacity:0},1990);tl.set(ps[2],{opacity:1},1990);tl.set(fs[4],{opacity:1},1990);tl.set(xs[7],{opacity:1},1990);
 rise(xdr,E.x,1990);rise(mac,E.m,1996);rise(pad,E.p,2000);rise(phone,E.f,2004);
 tl.fromTo(rig,{rotationY:-3,scale:1.02},{rotationY:3,scale:1,duration:170,ease:'sine.inOut',immediateRender:false},1990);

 /* SCENE 10: 밝은 마지막 장면 */
 at(2140,rig,{y:vh*.22,autoAlpha:0,ease:'power2.in'},50);
 at(2160,filmBg,{backgroundColor:cssv('--end')},44);
 tl.to({},{duration:total-2230},2230);

 /* 장면별 이미지 받기 · 밝은 머리글 */
 var sceneAt=[0,150,296,540,930,1150,1420,1680,1960,2140];
 var frame=function(t){leaves.forEach(function(L){var v=0;(L.k||[]).forEach(function(k){if(t>=k[0])v=t>=k[0]+k[1]?k[2]:(1-k[2])+(k[2]-(1-k[2]))*ease((t-k[0])/k[1])});if(v!==L.t)setLeaf(L,v)});
  cnt.forEach(function(c){var p=Math.max(0,Math.min(1,(t-c.a)/16)),v=Math.round(c.n*(1-Math.pow(1-p,2)));if(v!==c.last){c.last=v;c.dd.textContent=v+c.u}})};
 S.frame=frame;frame(0);zsync();
 tl.eventCallback('onUpdate',function(){var t=tl.time(),s=0;frame(t);zsync();for(var i=0;i<sceneAt.length;i++)if(t>=sceneAt[i]-120)s=i;loadUpTo(s+1);var lf=t>=2186&&H.dataset.theme!=='light';if(lf!==lightFilm){lightFilm=lf;theme()}});

 /* 들어오는 순간: 어둠 속에서 디스플레이가 드러나고, 테두리를 따라 빛이 지난다 */
 if(S.introDone){gsap.set([veil,pw],{opacity:0});return}S.introDone=1;
 gsap.set(veil,{opacity:1});gsap.set(xin,{rotationY:-28,rotationX:7,z:-160});
 var cueKids=$$('.cue>*');gsap.set(heroKids,{autoAlpha:0,y:28});gsap.set(cueKids,{autoAlpha:0});
 var intro=gsap.timeline({delay:.15});
 intro.to(veil,{opacity:0,duration:1.6,ease:'power2.inOut'},0)
  .to(xin,{rotationY:0,rotationX:0,z:0,duration:2.4,ease:'power3.out'},0)
  .to(heroKids,{autoAlpha:1,y:0,duration:1.1,stagger:.16,ease:'power3.out'},.55)
  .to($('.sheen',xdr),{backgroundPosition:'-20% 0',duration:1.8,ease:'power2.inOut'},1)
  .to(pw,{opacity:0,duration:.9,ease:'power1.inOut'},1.35)
  .to(cueKids,{autoAlpha:1,duration:.8},2);
 S.intro=intro}

/* 스크롤 위치 → 타임라인 시간. 장면 섹션 i 의 윗변이 화면 위에 닿는 순간이 그 장면 문구가 자리 잡는 시간 A[i] 이고,
   그 사이는 직선으로 잇는다. 섹션 높이는 장면 길이에 비례하되 문구가 다 읽히도록 문구 높이보다 짧지 않게 한다.
   스크롤 위치는 한 번도 바꾸지 않는다(크기가 바뀌어 다시 짤 때 같은 장면으로 되돌려 놓는 것만 예외). */
var secs=$$('.sc',film),A=[0,140,298,556,992,1186,1440,1700,2000,2196,total],tops=[],filmTop=0;
function layout(){var k=vh/100*(M?1.4:1.7),n=secs.length;
 secs.forEach(function(s,i){var cp=$('.cp',s),h=(A[i+1]-A[i])*k+(i===n-1?vh:0),need=(cp&&i?cp.offsetHeight+vh*.5:0);s.style.height=Math.round(Math.max(h,need,vh))+'px'});
 filmTop=film.getBoundingClientRect().top+scrollY;tops=secs.map(function(s){return s.offsetTop});tops.push(tops[n-1]+secs[n-1].offsetHeight-vh)}
function timeAt(y){var n=tops.length-1;if(y<=0)return 0;if(y>=tops[n])return total;for(var i=0;i<n-1&&y>=tops[i+1];i++);return A[i]+(A[i+1]-A[i])*(y-tops[i])/(tops[i+1]-tops[i])}
function yAt(t){var n=tops.length-1;if(t<=0)return 0;if(t>=total)return tops[n];for(var i=0;i<n-1&&t>=A[i+1];i++);return tops[i]+(tops[i+1]-tops[i])*(t-A[i])/(A[i+1]-A[i])}
sync=function(){if(tl)tl.time(timeAt(scrollY-filmTop))};
S.timeAt=function(y){return timeAt(y-filmTop)};S.yAt=function(t){return filmTop+yAt(t)};
function start(){sizes();build();loadUpTo(1);timeline();layout();sync()}
function rebuild(){var t=tl?tl.time():0;if(tl)tl.kill();if(S.intro)S.intro.progress(1).kill();
 gsap.set($$('.cp,.cp h1,.cp p,.cue,.score > div,.pages span,.ops-list li,.film-bg'),{clearProps:'all'});
 start();if(scrollY>filmTop||t>0)scrollTo(0,Math.round(filmTop+yAt(t)));sync()}
window.__rebuild=function(){rebuild()};
window.__intro=S;
var lastW=innerWidth,lastH=innerHeight,rt;
addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(function(){var w=innerWidth,hh=innerHeight;if(w===lastW&&(Math.abs(hh-lastH)<160||w<861))return;lastW=w;lastH=hh;rebuild()},250)});

start();
addEventListener('load',function(){setTimeout(function(){loadUpTo(9)},2500);layout();sync()});
})();
