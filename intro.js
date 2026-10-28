/* Scroll follows the lesson. Native scrolling, no autoplay, no remote writes. */
(function(){
'use strict';
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
var esc=function(t){return String(t==null?'':t).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})};
var rm=matchMedia('(prefers-reduced-motion: reduce)'),mobile=matchMedia('(max-width: 900px)');
var menu=$('#menu'),nav=$('#nav');
function navOpen(on){nav.classList.toggle('open',on);menu.setAttribute('aria-expanded',String(on));menu.setAttribute('aria-label',on?'목차 닫기':'목차 열기')}
menu.addEventListener('click',function(){navOpen(menu.getAttribute('aria-expanded')!=='true')});
nav.addEventListener('click',function(e){if(e.target.closest('a'))navOpen(false)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&menu.getAttribute('aria-expanded')==='true'){navOpen(false);menu.focus()}});
document.addEventListener('click',function(e){if(!e.target.closest('.hd'))navOpen(false);if(e.target.closest('[data-app]')){try{localStorage.setItem('omr_app','1')}catch(ignore){}}});
var stage=$('.stage-canvas'),chapters=$$('[data-chapter]'),controls=$$('.story-controls a'),titles=['학습지 만들기','개념 · 유형 교재','OMR 채점','취약 유형 지도'];
var pending=false,current=-1;
var clamp=function(n){return Math.max(0,Math.min(1,n))};
function range(n,a,b){return clamp((n-a)/(b-a))}
function update(){pending=false;if(rm.matches||mobile.matches){document.documentElement.classList.remove('motion-ready');return}document.documentElement.classList.add('motion-ready');
 var first=chapters[0].getBoundingClientRect(),last=chapters[3].getBoundingClientRect(),span=last.top-first.top;
 var p=clamp((innerHeight*.48-first.top)/span),bookIn=range(p,.22,.31),bookOut=range(p,.55,.67),book=bookIn*(1-bookOut),phone=range(p,.54,.65)*(1-range(p,.86,.98)),analysis=range(p,.78,.9),laptop=range(p,.05,.22),open=range(p,.29,.43),turn=range(p,.43,.56);
 var vars={'--device-x':(-42*phone)+'px','--device-scale':String(.83+.07*laptop-.13*phone),'--device-angle':(-7+7*laptop)+'deg','--base-opacity':String(laptop),'--device-opacity':String(1-book*.92),'--book-opacity':String(book),'--book-y':((1-book)*50)+'px','--cover-angle':(-176*open)+'deg','--leaf-angle':(-158*turn)+'deg','--phone-opacity':String(phone),'--phone-x':((1-phone)*80)+'px','--analysis-opacity':String(analysis),'--phone-result':String(range(p,.69,.79))};
 Object.keys(vars).forEach(function(k){stage.style.setProperty(k,vars[k])});
 var idx=p<.23?0:p<.56?1:p<.81?2:3;
 if(idx!==current){current=idx;stage.dataset.step=String(idx);$('#screenTitle').textContent=titles[idx];controls.forEach(function(a,i){if(i===idx)a.setAttribute('aria-current','step');else a.removeAttribute('aria-current')})}
}
function schedule(){if(!pending){pending=true;requestAnimationFrame(update)}}
addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule);addEventListener('load',schedule);
if(rm.addEventListener){rm.addEventListener('change',schedule);mobile.addEventListener('change',schedule)}else{rm.addListener(schedule);mobile.addListener(schedule)}
update();
/* Enter only on arrival: content is visible even if observers or scripts fail. */
if('IntersectionObserver' in window&&!rm.matches){
 var reveals=new IntersectionObserver(function(entries){entries.forEach(function(entry){if(entry.isIntersecting){entry.target.classList.add('arrived');reveals.unobserve(entry.target)}})},{threshold:.12});
 $$('.hero-copy h1,.hero-intro,.hero-art,.chapter h2,.chapter p,.chapter a,.learning-top h2,.learning-top p,.learning-images figure,.academy h2,.academy dl,.pr-h,.plans,.faq-t,.end h2').forEach(function(el){reveals.observe(el)});
 rm.addEventListener&&rm.addEventListener('change',function(){if(rm.matches){reveals.disconnect();$$('.arrived').forEach(function(el){el.classList.remove('arrived')})}});
}
 /* 요금제: 개발자 탭 「요금제」(site_config 의 pricing). 못 읽으면 HTML 기본값 그대로 */
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
   if(PL.length===3)$$('.cmp thead th[data-n]').forEach(function(th){var x=PL[+th.dataset.n];if(x&&x.name)th.textContent=x.name.replace(/^솔비\s*/,'')});
   var note=$('#prNote');if(note)note.textContent=v.note||'';
   if(ctHref){var fm=$('#fMail');if(fm)fm.href=ctHref}
   needUpd()}).catch(function(){})})();

})();
