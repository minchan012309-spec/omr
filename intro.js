/* Solvi 소개: 문구 + 실제 앱 캡처. 스크롤은 브라우저 기본 그대로(wheel · touch · key 를 가로채지 않고, 위치를 바꾸지 않는다).
   html.fx(동작 줄이기가 아닐 때)에서만 스크롤 위치를 읽어 캡처의 transform · opacity 를 바로 계산한다(지연 · 관성 없음). 문구는 움직이지 않는다. */
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
var lightSecs=0,scrollQ=false;
function theme(){hd.classList.toggle('light',lightSecs>0)}
function onScroll(){scrollQ=false;var y=scrollY;hd.classList.toggle('scrolled',y>12);dock.classList.toggle('on',y>innerHeight*.9)}
addEventListener('scroll',function(){if(!scrollQ){scrollQ=true;requestAnimationFrame(onScroll)}},{passive:true});onScroll();

/* ---------- 밝은 · 어두운 화면: 앱과 같은 저장값(omr_theme) ---------- */
var thm=$('#thm');if(thm)thm.addEventListener('click',function(){var t=H.dataset.theme==='light'?'dark':'light';H.dataset.theme=t;try{localStorage.setItem('omr_theme',t)}catch(e){}});

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

/* ---------- 밝은 면(마지막 장면 · 요금제 · 질문 · 바닥글) 위에서는 머리글도 밝게 ---------- */
function watchLight(){if(!('IntersectionObserver' in window))return;
 var io=new IntersectionObserver(function(es){es.forEach(function(e){lightSecs+=e.isIntersecting?1:-1;if(lightSecs<0)lightSecs=0});theme()},{rootMargin:'0px 0px -96% 0px'});
 $$('.sec,.ft,.sc-end').forEach(function(s){io.observe(s)})}

/* ---------- 목차: 지금 보고 있는 구역(실제 교차 결과)에 aria-current ---------- */
(function(){if(!('IntersectionObserver' in window))return;var links=$$('.nav a[href^="#"]'),seen={};
 var io=new IntersectionObserver(function(es){es.forEach(function(e){seen[e.target.id]=e.isIntersecting});var cur=null;links.forEach(function(a){if(seen[a.getAttribute('href').slice(1)])cur=a});links.forEach(function(a){if(a===cur)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')})},{rootMargin:'-45% 0px -45% 0px'});
 links.forEach(function(a){var t=D.getElementById(a.getAttribute('href').slice(1));if(t)io.observe(t)})})();

/* ---------- 스크롤 연출: 위치 → 진행도(0~1) → transform · opacity. 매 프레임 읽기를 먼저, 쓰기는 나중에 ---------- */
(function(){if(!H.classList.contains('fx')||!window.requestAnimationFrame)return;
 var cl=function(v){return v<0?0:v>1?1:v},out=function(p){return 1-Math.pow(1-p,3)};
 var vh=innerHeight,items=[],q=false;
 /* 문제 제기 문장을 낱말로 나눈다(읽기 프로그램에는 문장 그대로) */
 $$('[data-fx=words] .why-t').forEach(function(h){h.setAttribute('aria-label',h.textContent.replace(/\s+/g,' ').trim());
  (function split(el){Array.prototype.slice.call(el.childNodes).forEach(function(n){
   if(n.nodeType===3){var f=D.createDocumentFragment();n.textContent.split(/(\s+)/).forEach(function(t){if(!t)return;if(/^\s+$/.test(t)){f.appendChild(D.createTextNode(t));return}var w=D.createElement('span');w.className='w';w.setAttribute('aria-hidden','true');w.textContent=t;f.appendChild(w)});el.replaceChild(f,n)}
   else if(n.nodeType===1)split(n)})})(h)});
 $$('[data-fx]').forEach(function(el){var k=el.dataset.fx,it={el:el,k:k,last:-1};
  if(k==='words')it.ws=$$('.w',el);
  if(k==='rise')it.kids=$$('[data-lag]',el);
  if(k==='fan')it.pages=$$('.shot',el);
  if(k==='hero')it.img=$('.shot',el);
  if(k==='strip'){it.pin=$('.strip-pin',el);it.track=$('.strip-track',el)}
  items.push(it)});
 var loop=$('#loop'),rail=$$('.rail a'),bar=$('.rail-bar i'),steps=rail.map(function(a){return D.getElementById(a.getAttribute('href').slice(1))}),railCur=-1;
 /* 크기가 바뀌면 다시 재는 값: 교재 쪽마다 가운데까지 거리, 운영 화면 띠 길이 */
 var hdH=64;
 function measure(){vh=innerHeight;hdH=hd.offsetHeight||64;items.forEach(function(it){
  if(it.k==='fan'){var w=it.el.clientWidth/2;it.dx=it.pages.map(function(p){return w-(p.offsetLeft+p.offsetWidth/2)})}
  if(it.k==='strip'){it.run=Math.max(0,it.track.scrollWidth-it.pin.clientWidth);it.el.style.height=(it.pin.clientHeight+it.run)+'px'}
  it.last=-1})}
 function frame(){q=false;var y=scrollY,st=[];
  items.forEach(function(it){var r=it.el.getBoundingClientRect(),p;
   /* 띠 안의 캡처는 옆으로 가려져 있어 지연 로딩이 늦게 깨어난다 → 띠가 가까워지면 미리 받는다 */
   if(it.k==='strip'&&!it.eager&&r.top<vh*2){it.eager=true;$$('img',it.el).forEach(function(i){i.loading='eager'})}
   if(r.bottom<-vh*.5||r.top>vh*1.5)p=r.top>0?0:1;
   else if(it.k==='hero')p=cl(y/(vh*.6));
   else if(it.k==='words')p=cl((vh*.55-r.top)/(vh*.55+(r.height-vh)*.8));
   else if(it.k==='fan')p=cl((vh*.95-r.top)/(vh*.7));
   else if(it.k==='strip')p=it.run?cl((hdH-r.top)/it.run):0;
   else p=cl((vh-r.top)/(vh*.62));
   st.push(p)});
  var ri=-1,rp=0;if(loop){var lr=loop.getBoundingClientRect();rp=cl((vh*.45-lr.top)/(lr.height-vh*.45));steps.forEach(function(s,i){if(s&&s.getBoundingClientRect().top<=vh*.45)ri=i})}
  items.forEach(function(it,i){var p=st[i];if(Math.abs(p-it.last)<.0005)return;it.last=p;var e=out(p);
   if(it.k==='hero')it.img.style.transform='scale('+(.9+.1*e).toFixed(4)+')';
   else if(it.k==='rise'){it.el.style.opacity=(.2+.8*cl(p*1.6)).toFixed(3);it.el.style.transform='translateY('+((1-e)*56).toFixed(1)+'px) scale('+(.965+.035*e).toFixed(4)+')';
    it.kids.forEach(function(c){c.style.transform='translateY('+((1-e)*(+c.dataset.lag||1)*26).toFixed(1)+'px)'})}
   else if(it.k==='fan')it.pages.forEach(function(pg,j){pg.style.transform='translateX('+((1-e)*it.dx[j]).toFixed(1)+'px) translateY('+((1-e)*(j%2?14:0)).toFixed(1)+'px) rotate('+(e*parseFloat(pg.style.getPropertyValue('--r'))).toFixed(2)+'deg)'});
   else if(it.k==='words'){var n=it.ws.length;it.ws.forEach(function(w,j){w.style.opacity=(.16+.84*cl(p*(n+4)-j)).toFixed(2)})}
   else if(it.k==='strip')it.track.style.transform='translateX('+(-p*it.run).toFixed(1)+'px)'});
  if(bar)bar.style.transform='scaleX('+rp.toFixed(4)+')';
  if(ri!==railCur){railCur=ri;rail.forEach(function(a,i){if(i===ri)a.setAttribute('aria-current','step');else a.removeAttribute('aria-current')})}}
 function req(){if(!q){q=true;requestAnimationFrame(frame)}}
 addEventListener('scroll',req,{passive:true});
 var rz;addEventListener('resize',function(){clearTimeout(rz);rz=setTimeout(function(){measure();req()},120)});
 addEventListener('load',function(){measure();req()});
 measure();frame();
 /* 예시 채점 숫자: 처음 보일 때 한 번만 0부터 세어 올린다 */
 if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;io.unobserve(en.target);
  var el=en.target,to=+el.dataset.count,u=el.dataset.unit||'',t0=0;
  (function tick(t){if(!t0)t0=t;var k=cl((t-t0)/700);el.textContent=Math.round(to*out(k))+u;if(k<1)requestAnimationFrame(tick)})(performance.now())})},{threshold:.6});
  $$('[data-count]').forEach(function(el){el.textContent='0'+(el.dataset.unit||'');io.observe(el)})}
})();

watchLight();
})();
