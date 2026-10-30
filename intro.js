/* Solvi 소개: 스크롤 하나가 필름 한 편을 재생한다. GSAP ScrollTrigger 하나(pin + scrub)에 모든 장면이 같은 타임라인으로 이어진다.
   스크립트가 없거나 · 동작 줄이기 · 저사양이면 html.cine 없이 같은 내용을 정적인 장면으로 보여 준다. 터치 스크롤은 건드리지 않는다. */
(function(){
'use strict';
var D=document,H=D.documentElement;
var $=function(s,r){return (r||D).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||D).querySelectorAll(s))};
var esc=function(t){return String(t==null?'':t).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})};

/* ---------- 머리글 · 목차 · 오른쪽 아래 버튼 ---------- */
var hd=$('.hd'),menu=$('#menu'),nav=$('#nav'),dock=$('#dock');
function navOpen(on){nav.classList.toggle('open',on);menu.setAttribute('aria-expanded',String(on));menu.setAttribute('aria-label',on?'목차 닫기':'목차 열기')}
menu.addEventListener('click',function(){navOpen(menu.getAttribute('aria-expanded')!=='true')});
nav.addEventListener('click',function(e){if(e.target.closest('a'))navOpen(false)});
D.addEventListener('keydown',function(e){if(e.key==='Escape'&&menu.getAttribute('aria-expanded')==='true'){navOpen(false);menu.focus()}});
D.addEventListener('click',function(e){if(!e.target.closest('.hd'))navOpen(false);if(e.target.closest('[data-app]')){try{localStorage.setItem('omr_app','1')}catch(ignore){}}});
var lightFilm=false,lightSecs=0,scrollQ=false;
function theme(){hd.classList.toggle('light',lightFilm||lightSecs>0)}
function onScroll(){scrollQ=false;var y=scrollY;hd.classList.toggle('scrolled',y>12);dock.classList.toggle('on',y>innerHeight*.9)}
addEventListener('scroll',function(){if(!scrollQ){scrollQ=true;requestAnimationFrame(onScroll)}},{passive:true});onScroll();

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
  var ct=String(v.contact||'').trim(),ctHref=/^https?:\/\//i.test(ct)?ct:/^[^\s:@]+@[^\s@]+\.[^\s@]+$/.test(ct)?'mailto:'+ct:'',top=topIdx(PL.length,PL);
  var who=['학생 최대 30명','학생 최대 50명 · 이후 1명당 추가 요금','학생 수 제한 없음'];
  plansEl.innerHTML=PL.map(function(x,i){var p=String(x.price||'').trim(),num=/^[\d,]+$/.test(p),ask=/문의/.test(x.cta||'')&&ctHref,isTop=i===top;
   var n0=num?+p.replace(/,/g,''):-1,price=p?(n0===0?'무료':num?n0.toLocaleString('ko-KR')+'원':esc(p)):'';num=num&&n0>0;
   return '<article class="plan'+(isTop?' top':'')+'" data-i="'+i+'"><h3>'+esc(x.name)+'</h3><p class="price">'+(price?'<b>'+price+'</b>'+(num&&x.unit?'<small>'+esc(x.unit)+'</small>':''):'<b class="tbd">요금 준비 중</b>')+'</p>'+(x.desc?'<p class="pd">'+esc(x.desc)+'</p>':'')+
    (PL.length===3?'<p class="who">'+who[i]+'</p>':'')+((x.items||[]).length?'<ul>'+x.items.map(function(t){return '<li>'+esc(t)+'</li>'}).join('')+'</ul>':'<ul></ul>')+
    '<a class="btn '+(isTop?'yel':'line')+'" href="'+(ask?esc(ctHref):'index.html?app=1#login')+'"'+(ask?'':' data-app')+'>'+esc(x.cta||'무료로 시작하기')+'</a></article>'}).join('');
  var note=$('#prNote');if(note)note.textContent=v.note||'';
  if(ctHref){var fm=$('#fMail');if(fm)fm.href=ctHref}
  needUpd()}).catch(function(){})})();

/* ---------- 밝은 면(요금제 · 질문 · 바닥글, 정적 모드의 마지막 장면) 위에서는 머리글도 밝게 ---------- */
function watchLight(cine){if(!('IntersectionObserver' in window))return;
 var io=new IntersectionObserver(function(es){es.forEach(function(e){lightSecs+=e.isIntersecting?1:-1;if(lightSecs<0)lightSecs=0});theme()},{rootMargin:'0px 0px -96% 0px'});
 $$('.sec,.ft'+(cine?'':',.sc-end')).forEach(function(s){io.observe(s)})}

/* ---------- 시네마틱 모드를 켤 수 있나 ---------- */
var rm=matchMedia('(prefers-reduced-motion: reduce)');
var nav2=navigator,low=(nav2.hardwareConcurrency&&nav2.hardwareConcurrency<=2)||(nav2.deviceMemory&&nav2.deviceMemory<=2)||(nav2.connection&&nav2.connection.saveData);
var can=!!(window.gsap&&window.ScrollTrigger&&window.CSS&&CSS.supports('transform-style','preserve-3d'))&&!rm.matches&&!low;
if(rm.addEventListener)rm.addEventListener('change',function(){location.reload()});
if(!can){watchLight(false);return}
H.classList.add('cine');watchLight(true);
var gsap=window.gsap,ST=window.ScrollTrigger;gsap.registerPlugin(ST);ST.config({ignoreMobileResize:true});

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

var M,vw,vh,u,S={},tl,trig,leaves=[],built=false,total=2320;
function sizes(){vw=innerWidth;vh=innerHeight;M=vw<861;
 u=M?Math.min(vw*.0145,vh*.0075):Math.min(vw*.01,vh*.0165);H.style.setProperty('--u',u.toFixed(2)+'px');
 S.xdr=M?vw*.92:64*u;S.mac=M?vw*.8:50*u;S.pad=M?vw*.46:24*u;S.phone=M?Math.min(vw*.42,vh*.2):15*u;S.book=M?vw*.42:21*u;S.sheet=M?vw*.62:25*u;
 S.tw=M?Math.floor((vw*.92-16)/3):150;S.th=M?62:122;S.cols=M?3:5;S.gap=M?8:12;S.aw=M?Math.min(vw*.88,420):400}

function build(){
 stage.innerHTML='';leaves=[];loadedS=-1;
 var NS=M?6:12,NE=M?4:6;
 var h='<div class="floor"></div><svg class="links" id="links"></svg><div class="rig" id="rig">';
 /* Pro Display XDR */
 h+='<div class="obj xdr" id="xdr" style="--w:'+S.xdr+'px"><div class="xdr-in" id="xdrIn"><i class="glow"></i><i class="arm"></i><i class="arm-b"></i><i class="foot"></i><i class="foot-e"></i><div class="xdr-body"><div class="face f-back"></div><div class="face f-l"></div><div class="face f-r"></div><div class="face f-t"></div><div class="face f-b"></div><div class="face f-front"><div class="scr" data-ui>'+
  IMG('xdr-dash',0,'on')+IMG('xdr-cls',1)+IMG('xdr-build',1)+IMG('xdr-dash',6,'a8')+IMG('xdr-stu',6)+IMG('xdr-cls',6,'a8c')+IMG('xdr-cns',6)+IMG('xdr-weak',7)+
  '<i class="hl" style="left:20.6%;top:17.9%;width:73.8%;height:16%"></i><i class="hl" style="left:48.5%;top:17.9%;width:27.4%;height:16%"></i><i class="hl" style="left:20.6%;top:40.7%;width:24.2%;height:34.4%"></i><i class="hl" style="left:70.2%;top:40.7%;width:24.2%;height:34.4%"></i><i class="hl" style="left:20.6%;top:22%;width:73.8%;height:62%"></i><i class="pw" style="position:absolute;inset:0;background:#000"></i></div><i class="sheen"></i></div></div></div></div>';
 /* 문제은행 카드 · 학습지 */
 h+='<div class="obj qb" id="qb"><div class="qf" id="qf"><span>물질과 에너지</span><span>Ⅲ 반응 엔탈피</span><span>Ⅳ 반응 속도</span><span>난이도 하</span><span>중</span><span>상</span></div>';
 QS.forEach(function(q,i){var d=DOTS[q[3]],dots='';for(var k=1;k<=4;k++)dots+=k<=d?'●':'<span class="o">●</span>';
  h+='<div class="qt" data-i="'+i+'" style="--tw:'+S.tw+'px;--th:'+S.th+'px"><div class="q1"><span class="code">'+q[0]+'</span><span class="dots" aria-hidden="true">'+dots+'</span></div><div class="ty">'+esc(q[2])+'</div><div class="sx">'+esc(q[4])+'</div></div>'});
 h+='<div class="qcount" id="qcount">반응 속도 · 중 이상 6문항으로 학습지 만들기</div></div>';
 h+='<div class="obj sheet" id="sheet" style="--w:'+S.sheet+'px"><div class="pp"><div class="face f" data-bg="intro/book-sheet.webp"><i class="sd"></i></div><div class="face k"><i class="sd"></i></div></div></div>';
 /* 교재 */
 h+='<div class="obj book" id="book" style="--w:'+S.book+'px"><div class="bk"><div class="face back"></div><i class="ee r"></i><i class="ee t"></i><i class="ee b"></i><div class="spine"><span>물질과 에너지 개념서</span></div><div class="pg base" data-bg="intro/book-answer.webp"></div>';
 [['book-basic','book-problem'],['book-concept','book-ox'],['cover-me-c','book-toc']].forEach(function(p,i){h+='<div class="leaf'+(i===2?' cover':'')+'" data-f="intro/'+p[0]+'.webp" data-k="intro/'+p[1]+'.webp" style="transform:translateZ('+((i+1)*1.4)+'px)">'+stripHTML(i===2?1:NS,0)+'</div>'});
 h+='</div></div>';
 [['cover-me-t','#2b6fc0','물질과 에너지 유형서'],['cover-cm-c','#2e9b57','세포와 물질대사 개념서'],['cover-cm-t','#2e9b57','세포와 물질대사 유형서'],['mock-cover','#1d3f73','전범위 모의고사']].forEach(function(b,i){h+='<div class="obj mb book" id="mb'+i+'" style="--w:'+S.book+'px">'+bookBox(b[0],b[1],b[2])+'</div>'});
 /* MacBook */
 h+='<div class="obj mac" id="mac" style="--w:'+S.mac+'px"><div class="mac-base"><div class="face deck"><div class="kbd">'+kbd()+'</div><div class="tpad"></div></div><div class="face under" style="backface-visibility:visible"></div></div><i class="bf"></i><i class="bs l"></i><i class="bs r"></i>'+
  '<div class="mac-lid" id="lid"><div class="face lid-b"></div><div class="face lid-f"><div class="scr" data-ui>'+IMG('mac-thome',3,'on')+IMG('mac-diag',5)+IMG('mac-stu',6)+'</div><i class="notch"></i></div></div></div>';
 /* iPad */
 h+='<div class="obj pad-o" id="pad"><div class="slab pad" style="--w:'+S.pad+'px">'+slabEdges(NE)+'<div class="face bk"><i class="cam"></i></div><div class="face fr"><div class="scr" data-ui>'+IMG('cover-me-c',3,'on')+IMG('pad-home',3)+IMG('pad-stat',7)+'<div class="kio">'+IMG('kiosk',6,'on')+'</div></div></div></div></div>';
 /* iPhone */
 h+='<div class="obj ph-o" id="phone"><div class="slab phone" style="--w:'+S.phone+'px">'+slabEdges(NE+1)+'<div class="face bk"><i class="lens"></i></div><div class="face fr"><div class="scr" data-ui>'+IMG('phone-omr',4,'on')+IMG('phone-result',4,'res')+IMG('phone-weak',4)+IMG('phone-home',7)+
  '<div class="scan">'+IMG('book-sheet',4,'on')+'<i class="fr4"></i><i class="line"></i><span class="lab">QR 인식 · 학습지 04271938</span></div><div class="burst"><b></b>'+new Array(15).join('<i></i>')+'</div></div><i class="island"></i></div></div></div>';
 /* 오답 분석 */
 h+='<div class="obj ana" id="ana"><div class="agrp" style="--aw:'+S.aw+'px"><h3>틀린 문항 · 유형별로 모으기</h3><p class="tt">연소·생성·분해·용해·기화 엔탈피의 정의</p><div class="slots"><i></i><i></i><i></i></div><p class="why"><span>진술 오판단 2</span><span>개념 혼동 1</span></p></div>'+
  '<div class="abars" style="--aw:'+S.aw+'px"><h3>유형별 정답률 · 솔비 학생</h3><ol>'+BARS.map(function(b){return '<li><span>'+esc(b[0])+'</span><i><b style="--c:'+b[2]+'"></b></i><em>'+b[1]+'%</em></li>'}).join('')+'</ol></div>'+
  ['43번','47번','51번'].map(function(t){return '<span class="chip">'+t+'</span>'}).join('')+'</div>';
 h+='</div>';
 h+='<div class="scrim"></div><div class="hl-cap"><span>재원생 · 오늘 수업 · 출석률 · 수납률을 한눈에</span><span>출석률 92% · 수납률 88% · 미수금까지</span><span>반마다 오늘 수업과 등원 현황</span><span>7일 안에 할 상담과 다음 할 일</span><span>반 · 시간표도 같은 화면에서</span></div>';
 h+='<div class="tags"><span class="tag" data-t="x0"><b>원생</b>재원 · 휴원 · 상담 상태</span><span class="tag" data-t="x1"><b>반 · 시간표</b>주간 시간표와 담당 선생님</span><span class="tag" data-t="x2"><b>상담</b>상담 일지와 보강 일정</span><span class="tag" data-t="m"><b>학생</b>학생별 학습 기록</span><span class="tag" data-t="p"><b>출결</b>입구 태블릿 출결 단말</span><span class="tag" data-t="f"><b>행정</b>학부모 알림장 · 수납</span></div><div class="veil" id="veil"></div>';
 stage.innerHTML=h;
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
 for(var i=0;i<L.st.length;i++){var s=L.st[i];if(i>0||!L.rigid)s.style.transform=i===0?'':'rotateY('+b.toFixed(2)+'deg)';var a=(th+b*i)*Math.PI/180,o=(.28*Math.abs(Math.sin(a))).toFixed(3);s.children[0].children[0].style.opacity=o;s.children[1].children[0].style.opacity=o}}

function timeline(){
 var X=function(id){return $('#'+id,stage)},xdr=X('xdr'),xin=X('xdrIn'),qb=X('qb'),sheet=X('sheet'),book=X('book'),mac=X('mac'),lid=X('lid'),pad=X('pad'),phone=X('phone'),ana=X('ana'),rig=X('rig'),veil=X('veil');
 var mbs=[0,1,2,3].map(function(i){return X('mb'+i)});
 var cps={};$$('.sc').forEach(function(s){cps[s.dataset.scene]=$('.cp',s)});
 var xs=$$('.scr img',xdr),hl=$$('.hl',xdr),pw=$('.pw',xdr),cap=$$('.hl-cap span',stage),scrim=$('.scrim',stage),floor=$('.floor',stage);
 var ms=$$('.scr img',mac),ps=$$('.scr>img',pad),kio=$('.kio',pad),fs=$$('.scr>img',phone),scan=$('.scan',phone),line=$('.line',scan),fr4=$('.fr4',scan),lab=$('.lab',scan),burst=$$('.burst i',phone),ring=$('.burst b',phone);
 var tiles=$$('.qt',qb),qf=$$('.qf span',qb),qcount=X('qcount'),chips=$$('.chip',ana),agrp=$('.agrp',ana),abars=$('.abars',ana),bars=$$('.abars b',ana),why=$$('.why span',ana);
 var tags={};$$('.tag',stage).forEach(function(t){tags[t.dataset.t]=t});var links=X('links');
 var heroCp=cps.hero,heroKids=[$('h1',heroCp),$('p',heroCp)],cue=$('.cue');
 var P=function(d,m){return M?m:d};

 /* 첫 화면: 히어로 문구 아래 남는 공간에 디스플레이 + 받침대를 맞춘다 */
 gsap.set(heroCp,{autoAlpha:1});
 var cb=heroCp.getBoundingClientRect().bottom,gap=P(.035,.04)*vh,avail=vh-cb-gap-P(.15,.14)*vh,grp=S.xdr*.756;
 var s0=Math.min(avail/grp,P(.66,.98)*vw/S.xdr),dispY=cb+gap-vh/2+S.xdr*.287*s0;
 var sw=S.xdr*.969,sh=S.xdr*.543,sF=M?vw/sw:Math.max(vw/sw,vh/sh)*1.01;
 tl=gsap.timeline({defaults:{ease:'none',duration:20},paused:true});
 var at=function(t,target,vars,dur){vars.duration=dur==null?20:dur;tl.to(target,vars,t);return tl};
 var copyIn=function(k,a,b){var c=cps[k];tl.fromTo(c,{autoAlpha:0,y:36},{autoAlpha:1,y:0,duration:24,ease:'power2.out',immediateRender:false},a);if(b!=null)tl.to(c,{autoAlpha:0,y:-36,duration:18,ease:'power1.in'},b)};
 gsap.set([qb,sheet,book,mac,pad,phone,ana].concat(mbs),{autoAlpha:0});
 gsap.set(xdr,{autoAlpha:1,y:dispY,scale:s0});
 Object.keys(cps).forEach(function(k){if(k!=='hero')gsap.set(cps[k],{autoAlpha:0})});

 /* SCENE 01 → 02: 디스플레이 속으로 들어가는 카메라 */
 tl.fromTo(cue,{autoAlpha:1},{autoAlpha:0,duration:24,immediateRender:false},0);
 at(40,heroCp,{autoAlpha:0,y:-60,ease:'power1.in'},44);
 at(55,xdr,{scale:sF,y:0,ease:'power2.inOut'},95);
 at(118,scrim,{opacity:M?0:1},26);
 copyIn('ops',140,250);
 var hlT=[150,174,196,216,244];
 hl.forEach(function(e,i){tl.fromTo(e,{opacity:0},{opacity:1,duration:10,immediateRender:false},hlT[i]);tl.to(e,{opacity:0,duration:8},hlT[i]+(i===4?16:18));tl.fromTo(cap[i],{opacity:0,y:10},{opacity:1,y:0,duration:8,immediateRender:false},hlT[i]);tl.to(cap[i],{opacity:0,duration:6},hlT[i]+(i===4?16:19))});
 at(230,xs[1],{opacity:1},12);
 at(262,xs[2],{opacity:1},12);
 at(258,scrim,{opacity:0},14);
 /* SCENE 03: 문제은행 */
 at(272,xdr,{scale:s0*.62,y:P(-.1,-.2)*vh,z:-380,ease:'power2.inOut'},52);
 at(318,xdr,{autoAlpha:0},22);
 var qX=P(.15,0)*vw,qY=P(.05,.12)*vh,cols=S.cols,rows=Math.ceil(tiles.length/cols),gw=cols*S.tw+(cols-1)*S.gap,gh=rows*S.th+(rows-1)*S.gap;
 gsap.set(qb,{x:qX,y:qY});
 var qfEl=$('.qf',qb);qfEl.style.left='0px';qfEl.style.top=(-gh/2-16)+'px';qcount.style.left='0px';qcount.style.top=(gh/2+18)+'px';
 at(296,qb,{autoAlpha:1},6);
 gsap.set(qfEl,{autoAlpha:0});at(300,qfEl,{autoAlpha:1},16);
 var pos=tiles.map(function(t,i){var c=i%cols,r=Math.floor(i/cols);return {x:-gw/2+c*(S.tw+S.gap),y:-gh/2+r*(S.th+S.gap)}});
 tiles.forEach(function(t,i){gsap.set(t,{x:-qX-S.tw/2+(i%cols-cols/2)*14,y:P(-.1,-.2)*vh-qY-S.th/2,z:-420,scale:.3,autoAlpha:0});
  tl.to(t,{x:pos[i].x,y:pos[i].y,z:0,scale:1,autoAlpha:1,duration:34,ease:'power2.out'},296+i*1.6)});
 var on=function(sp,t){tl.to(sp,{backgroundColor:'#ffffff',color:'#111111',duration:6},t)};
 on(qf[0],330);on(qf[2],350);on(qf[4],372);on(qf[5],374);
 var unitIV=function(i){return QS[i][1].charAt(0)==='Ⅳ'},sel=[];
 tiles.forEach(function(t,i){if(!unitIV(i))tl.to(t,{autoAlpha:.14,scale:.94,z:-60,duration:12},352);else if(QS[i][3]==='하')tl.to(t,{autoAlpha:.14,scale:.94,z:-60,duration:12},375);else sel.push(t)});
 sel.forEach(function(t){tl.to(t,{boxShadow:'0 0 0 3px #fdc62d',duration:8},384)});
 at(388,qcount,{opacity:1},8);
 /* 고른 문항이 학습지 한 장으로 모인다 */
 var sw2=S.sheet,shH=sw2*1.414;
 gsap.set(sheet,{x:qX,y:qY,scale:.7,z:-120});
 at(398,sheet,{autoAlpha:1,scale:1,z:0,ease:'power2.out'},20);
 tiles.forEach(function(t){if(sel.indexOf(t)<0)tl.to(t,{autoAlpha:0,duration:10},398)});
 at(398,qfEl,{autoAlpha:0},10);at(424,qcount,{opacity:0},8);
 sel.forEach(function(t,k){var c=k%2,r=Math.floor(k/2);tl.to(t,{x:(c?.06:-.44)*sw2-S.tw*.1,y:(-.36+r*.22)*shH,scale:.36,z:6,duration:30,ease:'power2.inOut'},404+k*2);tl.to(t,{autoAlpha:0,duration:10},430+k*2)});
 var sd=$$('.sd',sheet);
 at(446,sheet,{x:P(.12,0)*vw,y:P(.01,.08)*vh,z:P(150,60),rotationX:-10,rotationY:-28,rotationZ:3,ease:'power2.inOut'},34);
 at(446,sd,{opacity:.12},34);
 at(482,sheet,{rotationY:26,rotationX:8,rotationZ:-2,ease:'sine.inOut'},40);
 at(482,sd,{opacity:.05},40);
 at(524,sheet,{y:-vh*.9,rotationX:42,autoAlpha:0,ease:'power2.in'},28);
 copyIn('bank',298,522);

 /* SCENE 04: 살아 움직이는 교재 */
 var bw=S.book,bX=P(.1,0)*vw,bY=P(.07,.1)*vh;
 gsap.set(book,{x:bX-bw/2,y:vh*.85,rotationX:62,rotationY:-40,rotationZ:12});
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
 at(874,book,{x:bX-bw/2},20);
 var pg=$$('.pages span',cps.book),pgOn=function(i,a,b){tl.to(pg[i],{color:'#f5f5f7',duration:6},a);tl.to(pg[i],{color:'#a1a1a6',duration:6},b)};
 pgOn(0,560,640);pgOn(1,650,722);pgOn(2,650,722);pgOn(3,724,782);pgOn(4,724,782);pgOn(5,784,860);pgOn(6,784,860);
 /* 책이 닫히고 여러 권이 한 줄로 정돈된다 */
 var sR=P(.6,.4),step=bw*sR*1.1,slots=[-2,-1,1,2];
 at(890,book,{x:P(.04,0)*vw-bw*sR/2,y:bY+P(.04,.02)*vh,scale:sR,rotationY:-10,rotationX:6,ease:'power2.inOut'},34);
 mbs.forEach(function(m,i){gsap.set(m,{x:P(.04,0)*vw+slots[i]*step*1.8-bw*sR/2,y:bY+P(.04,.02)*vh+30,scale:sR,rotationY:-10,rotationX:6});
  tl.to(m,{autoAlpha:1,duration:12},896+i*3);tl.to(m,{x:P(.04,0)*vw+slots[i]*step-bw*sR/2,y:bY+P(.04,.02)*vh,duration:30,ease:'power2.out'},896+i*3)});
 copyIn('book',556,920);

 /* SCENE 05: 교재 → 태블릿 → 노트북 */
 var pS=P(.82,1),pw0=S.pad*pS,k=pw0*(1-2*.0303)/bw,padY=P(.12,.06)*vh;
 mbs.forEach(function(m,i){tl.to(m,{x:'+='+(slots[i]<0?-1:1)*vw*.4,autoAlpha:0,duration:26,ease:'power2.in'},934)});
 at(940,book,{x:-bw*k/2,y:padY,scale:k,rotationY:0,rotationX:0,ease:'power2.inOut'},30);
 gsap.set(pad,{y:padY,scale:pS});
 at(966,pad,{autoAlpha:1},16);at(980,book,{autoAlpha:0},8);
 at(990,ps[1],{opacity:1},14);
 copyIn('device',992,1148);
 at(1010,pad,{rotationY:360,y:padY-vh*.03,ease:'sine.inOut'},64);
 at(1010,pad,{rotationX:14,rotationZ:-5,ease:'sine.out'},32);at(1042,pad,{rotationX:4,rotationZ:0,ease:'sine.in'},32);
 var macS=P(.78,1),macX=P(-.08,0)*vw,macHy=P(.4*vh+.69*S.mac*macS-vh/2,.1*vh+S.mac*.26);
 gsap.set(mac,{x:macX,y:vh*.9,rotationX:-14,rotationY:P(16,0)});gsap.set(lid,{rotationX:-90});
 at(1076,pad,{x:P(.25,.25)*vw,y:P(.2,.2)*vh,z:P(90,40),rotationY:338,rotationX:4,scale:P(.72,.62),ease:'power2.inOut'},50);
 at(1078,mac,{autoAlpha:1},10);at(1078,mac,{y:macHy,scale:macS,ease:'power2.out'},40);
 at(1092,lid,{rotationX:12,ease:'power2.inOut'},46);

 /* SCENE 06: OMR 채점 */
 var phY=P(.04,.035)*vh,phH=S.phone*2.049;
 at(1150,mac,{x:-vw*.75,z:-200,rotationY:30,ease:'power2.in'},34);at(1170,mac,{autoAlpha:0},14);
 at(1150,pad,{x:vw*.75,ease:'power2.in'},34);at(1170,pad,{autoAlpha:0},14);
 gsap.set(phone,{y:vh*.9,rotationY:180,rotationZ:-10});
 at(1166,phone,{autoAlpha:1},10);
 at(1166,phone,{y:phY,rotationY:0,rotationZ:0,ease:'power2.out'},58);
 copyIn('omr',1186,1410);
 gsap.set(scan,{opacity:1});gsap.set(line,{y:0});gsap.set(lab,{opacity:0});
 at(1226,line,{y:phH*.86},30);
 at(1254,fr4,{boxShadow:'0 0 0 3px #fdc62d'},6);at(1254,lab,{opacity:1},6);
 at(1266,scan,{opacity:0},14);
 at(1290,fs[1],{opacity:1},10);
 burst.forEach(function(d,i){var a=i/burst.length*Math.PI*2,r=S.phone*(.34+.08*(i%3));gsap.set(d,{x:0,y:0,scale:.5});tl.to(d,{opacity:1,duration:3},1298);tl.to(d,{x:Math.cos(a)*r,y:Math.sin(a)*r,scale:1,duration:20,ease:'power2.out'},1298);tl.to(d,{opacity:0,duration:10},1310)});
 tl.fromTo(ring,{opacity:0,scale:.4},{opacity:1,scale:1,duration:6,immediateRender:false},1298);at(1304,ring,{opacity:0,scale:2.4,ease:'power1.out'},18);
 var dds=$$('.score > div',cps.omr);gsap.set(dds,{autoAlpha:0,y:20});
 var cnt=dds.map(function(d,i){var dd=$('dd',d);tl.to(d,{autoAlpha:1,y:0,duration:10},1304+i*10);return {dd:dd,n:+dd.dataset.n,u:dd.dataset.u||'',a:1304+i*10,last:-1}});
 at(1368,fs[2],{opacity:1},14);

 /* SCENE 07: 오답 분석과 맞춤형 학습 */
 var aX=P(.17,0)*vw,aY=P(.06,.08)*vh,phX7=P(-.27,-.3)*vw;
 at(1420,fs[2],{opacity:0},12);
 at(1420,phone,{x:phX7,y:P(.17,.22)*vh,rotationY:14,scale:P(.84,.55),ease:'power2.inOut'},30);
 at(1430,fs[1],{scale:1.75,transformOrigin:'50% 84%',ease:'power2.inOut'},26);
 gsap.set(ana,{x:aX,y:aY});
 var gH=agrp.offsetHeight,bH=abars.offsetHeight,gy=-(gH+bH+16)/2+gH/2,by=gy+gH/2+16+bH/2;
 gsap.set([agrp,abars],{xPercent:-50,yPercent:-50});gsap.set(agrp,{x:0,y:gy});gsap.set(abars,{x:0,y:by});gsap.set(why,{autoAlpha:0});
 at(1440,ana,{autoAlpha:1},4);
 tl.fromTo(agrp,{autoAlpha:0,y:gy+24},{autoAlpha:1,y:gy,duration:16,immediateRender:false},1446);
 var slotsEl=$$('.slots i',agrp);
 chips.forEach(function(c,i){var sl=slotsEl[i];
  gsap.set(c,{xPercent:-50,yPercent:-50,x:phX7-aX+(i-1)*S.phone*.3,y:P(.17,.22)*vh-aY+phH*.25,scale:.6});
  tl.to(c,{opacity:1,duration:6},1452+i*5);var d=function(k){var a=sl.getBoundingClientRect(),q=c.getBoundingClientRect();return k?a.top+a.height/2-q.top-q.height/2+(gy-gsap.getProperty(agrp,'y')):a.left+a.width/2-q.left-q.width/2};
  tl.to(c,{x:function(){return gsap.getProperty(c,'x')+d(0)},y:function(){return gsap.getProperty(c,'y')+d(1)},scale:1,duration:30,ease:'power3.inOut'},1452+i*5)});
 why.forEach(function(w,i){tl.to(w,{autoAlpha:1,duration:10},1494+i*6)});
 tl.fromTo(abars,{autoAlpha:0,y:by+24},{autoAlpha:1,y:by,duration:16,immediateRender:false},1512);
 bars.forEach(function(b,i){tl.to(b,{scaleX:BARS[i][1]/100,duration:26,ease:'power2.out'},1522+i*5)});
 copyIn('wrong',1440,1668);
 at(1592,ana,{autoAlpha:0,scale:.92,x:aX+P(.05,0)*vw},20);
 at(1588,ms[1],{opacity:1},4);
 at(1596,mac,{y:P(.36*vh+.69*S.mac*.66-vh/2,.14*vh+S.mac*.26*.9),z:0,rotationY:P(-14,0),scale:P(.66,.9),ease:'power2.out'},44);
 tl.fromTo(mac,{x:vw*.7},{x:P(.18,0)*vw,duration:44,ease:'power2.out',immediateRender:false},1596);
 at(1596,mac,{autoAlpha:1},10);
 at(1600,fs[2],{opacity:1},14);
 if(M)at(1462,phone,{autoAlpha:0},14);

 /* SCENE 08: 학원 운영 시스템 */
 var L8={x:{x:P(.14,0),y:P(-.05,-.05),s:P(.6,.8)},m:{x:P(-.25,-.22),y:P(.33,.33),s:P(.64,.48)},p:{x:P(.37,.24),y:P(.22,.24),s:P(.72,.56)},f:{x:P(.17,.04),y:P(.27,.31),s:P(.72,.46)}};
 var px8=function(o){return {x:o.x*vw,y:o.y*vh}};
 at(1680,phone,{x:L8.f.x*vw,y:L8.f.y*vh,rotationY:-12,scale:L8.f.s,autoAlpha:1,ease:'power2.inOut'},44);
 at(1700,ms[2],{opacity:1},10);
 at(1680,mac,{x:L8.m.x*vw,y:L8.m.y*vh,rotationY:18,scale:L8.m.s,ease:'power2.inOut'},44);
 at(1690,xs[3],{opacity:1},2);
 tl.fromTo(xdr,{autoAlpha:0},{autoAlpha:1,duration:16,immediateRender:false},1690);
 at(1690,xdr,{x:L8.x.x*vw,y:L8.x.y*vh,z:0,scale:L8.x.s*vw/S.xdr*P(.74,1),ease:'power2.out'},40);
 gsap.set(kio,{opacity:0});
 tl.fromTo(pad,{x:vw*.75,y:L8.p.y*vh,rotationY:360,rotationZ:0,scale:L8.p.s,z:0},{x:L8.p.x*vw,rotationZ:-90,duration:44,ease:'power2.out',immediateRender:false},1684);
 at(1684,pad,{autoAlpha:1},10);at(1700,kio,{opacity:1},10);
 copyIn('academy',1700,1946);
 /* 기기 사이를 잇는 선과 이름표 */
 links.setAttribute('viewBox','0 0 '+vw+' '+vh);
 var c0={x:vw/2,y:vh/2},cx=function(o,dy){return {x:c0.x+o.x*vw,y:c0.y+o.y*vh+(dy||0)}};
 var xdrS=L8.x.s*vw/S.xdr*P(.74,1),xc=cx(L8.x),mc=cx(L8.m,-S.mac*.32*L8.m.s),pc=cx(L8.p),fc=cx(L8.f);
 var path=function(a,b){var mx=(a.x+b.x)/2,my=Math.min(a.y,b.y)-40;return 'M'+a.x.toFixed(1)+' '+a.y.toFixed(1)+' Q'+mx.toFixed(1)+' '+my.toFixed(1)+' '+b.x.toFixed(1)+' '+b.y.toFixed(1)};
 links.innerHTML=[[xc,mc],[xc,pc],[xc,fc],[mc,fc]].map(function(p){return '<path d="'+path(p[0],p[1])+'"/><path class="flow" d="'+path(p[0],p[1])+'" style="stroke:#fdc62d;stroke-width:2;stroke-dasharray:3 14"/>'}).join('');
 var lp=$$('path',links);lp.forEach(function(p){if(!p.classList.contains('flow')){var L=p.getTotalLength();gsap.set(p,{strokeDasharray:L,strokeDashoffset:L})}else gsap.set(p,{opacity:0})});
 lp.forEach(function(p,i){if(p.classList.contains('flow')){tl.to(p,{opacity:1,duration:8},1770);tl.to(p,{strokeDashoffset:-170,duration:170},1770);tl.to(p,{opacity:0,duration:10},1900)}else{tl.to(p,{strokeDashoffset:0,duration:26},1742+i*3);tl.to(p,{opacity:0,duration:10},1900)}});
 var tagAt=function(t,pt,dx,dy){gsap.set(t,{x:pt.x+dx,y:pt.y+dy})};
 var xTop={x:xc.x+(S.xdr*xdrS*P(.5,.2)),y:xc.y-S.xdr*.287*xdrS};
 tagAt(tags.x0,xTop,P(-60,-40),P(-18,-48));tagAt(tags.x1,xTop,P(-60,-40),P(-18,-48));tagAt(tags.x2,xTop,P(-60,-40),P(-18,-48));
 tagAt(tags.m,mc,P(-150,-60),P(-S.mac*.5*L8.m.s,-S.mac*.42*L8.m.s));tagAt(tags.p,pc,P(-80,-56),P(-S.pad*.5*L8.p.s-36,-S.pad*.5*L8.p.s-30));tagAt(tags.f,fc,P(-40,-80),S.phone*1.02*L8.f.s+P(10,6));
 [tags.m,tags.p,tags.f].forEach(function(t,i){tl.fromTo(t,{opacity:0,y:'+=10'},{opacity:1,y:'-=10',duration:10,immediateRender:false},1752+i*8);tl.to(t,{opacity:0,duration:10},1900)});
 var lis=$$('.ops-list li',cps.academy),liOn=function(i,a,b){tl.to(lis[i],{color:'#fdc62d',duration:6},a);tl.to(lis[i],{color:'#f5f5f7',duration:6},b)};
 tl.fromTo(tags.x0,{opacity:0},{opacity:1,duration:8,immediateRender:false},1790);at(1830,tags.x0,{opacity:0},8);
 at(1790,xs[4],{opacity:1},12);liOn(0,1790,1830);
 at(1830,xs[5],{opacity:1},12);tl.fromTo(tags.x1,{opacity:0},{opacity:1,duration:8,immediateRender:false},1832);at(1868,tags.x1,{opacity:0},8);liOn(1,1830,1868);
 liOn(2,1752,1790);liOn(4,1768,1790);
 at(1868,xs[6],{opacity:1},12);tl.fromTo(tags.x2,{opacity:0},{opacity:1,duration:8,immediateRender:false},1870);at(1904,tags.x2,{opacity:0},8);liOn(3,1868,1904);

 /* SCENE 09: 전체 제품 생태계 */
 var L9={x:{x:0,y:P(.1,-.02),s:P(.38,.84)},m:{x:P(-.27,-.24),y:P(.42,.3),s:P(.5,.46)},p:{x:P(.27,.27),y:P(.24,.2),s:P(.6,.5)},f:{x:P(.12,.05),y:P(.3,.3),s:P(.56,.44)}};
 at(1960,floor,{opacity:1},40);
 at(1960,xdr,{x:0,y:L9.x.y*vh,scale:L9.x.s*vw/S.xdr,ease:'power2.inOut'},50);
 at(1960,mac,{x:L9.m.x*vw,y:L9.m.y*vh,scale:L9.m.s,rotationY:22,ease:'power2.inOut'},50);
 at(1960,pad,{x:L9.p.x*vw,y:L9.p.y*vh,scale:L9.p.s,rotationZ:0,rotationY:340,ease:'power2.inOut'},50);
 at(1972,kio,{opacity:0},12);at(1972,ps[2],{opacity:1},12);
 at(1960,phone,{x:L9.f.x*vw,y:L9.f.y*vh,scale:L9.f.s,rotationY:-10,ease:'power2.inOut'},50);
 at(1972,fs[3],{opacity:1},12);at(1972,xs[7],{opacity:1},12);
 tl.fromTo(rig,{rotationY:-7,scale:1.06},{rotationY:7,scale:1,duration:180,ease:'sine.inOut',immediateRender:false},1960);
 copyIn('eco',2000,2134);

 /* SCENE 10: 밝은 마지막 장면 */
 at(2140,rig,{y:vh*.22,autoAlpha:0,ease:'power2.in'},50);
 at(2140,floor,{opacity:0},30);
 at(2160,filmBg,{backgroundColor:'#f5f5f7'},44);
 copyIn('end',2196,null);
 tl.to({},{duration:total-2230},2230);

 /* 장면별 이미지 받기 · 밝은 머리글 */
 var sceneAt=[0,150,296,540,930,1150,1420,1680,1960,2140];
 var frame=function(t){leaves.forEach(function(L){var v=0;(L.k||[]).forEach(function(k){if(t>=k[0])v=t>=k[0]+k[1]?k[2]:(1-k[2])+(k[2]-(1-k[2]))*ease((t-k[0])/k[1])});if(v!==L.t)setLeaf(L,v)});
  cnt.forEach(function(c){var p=Math.max(0,Math.min(1,(t-c.a)/16)),v=Math.round(c.n*(1-Math.pow(1-p,2)));if(v!==c.last){c.last=v;c.dd.textContent=v+c.u}})};
 S.frame=frame;frame(0);
 tl.eventCallback('onUpdate',function(){var t=tl.time(),s=0;frame(t);for(var i=0;i<sceneAt.length;i++)if(t>=sceneAt[i]-120)s=i;loadUpTo(s+1);var lf=t>=2186;if(lf!==lightFilm){lightFilm=lf;theme()}});
 S.labels={hero:0,ops:200,bank:330,book:600,device:1040,omr:1230,wrong:1500,academy:1760,eco:2040,end:total};

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

function start(){
 sizes();build();loadUpTo(1);timeline();
 trig=ST.create({trigger:film,start:'top top',end:function(){return '+='+Math.round(total/100*vh*(M?.78:.9))},pin:true,scrub:.7,anticipatePin:1,animation:tl});
 ST.refresh()}
function rebuild(){var p=trig?trig.progress:0;if(trig){trig.kill(true)}if(tl)tl.kill();if(S.intro)S.intro.progress(1).kill();
 gsap.set($$('.cp,.cp h1,.cp p,.cue,.score > div,.pages span,.ops-list li,.film-bg'),{clearProps:'all'});
 start();var y=trig.start+p*(trig.end-trig.start);scrollTo(0,y)}
var lastW=innerWidth,lastH=innerHeight,rt;
addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(function(){var w=innerWidth,hh=innerHeight;if(w===lastW&&(Math.abs(hh-lastH)<160||w<861))return;lastW=w;lastH=hh;rebuild()},250)});

/* 목차 · 장면 이동: 고정된 필름 안의 장면은 타임라인 위치로 부드럽게 스크롤 */
D.addEventListener('click',function(e){var a=e.target.closest('[data-go]');if(!a||!trig)return;var t=S.labels[a.dataset.go];if(t==null)return;e.preventDefault();
 scrollTo({top:trig.start+(t/total)*(trig.end-trig.start),behavior:'smooth'})});

start();
addEventListener('load',function(){setTimeout(function(){loadUpTo(9)},2500);ST.refresh()});
})();
