/* Solvi 소개 페이지: 스크롤 값 하나로 모든 장면을 움직인다.
   current += (target - current) * 0.12 로 부드럽게 따라가고, 장면마다 progress = (current - 시작) / 길이 를 구해
   data-anim 구간표("x 0 .35 70 18|o .55 .7 1 0" = 속성 시작 끝 처음값 끝값)대로 transform·opacity 만 바꾼다. */
(function(){
 var H=document.documentElement,lite=function(){return H.classList.contains('lite')};
 var mob=function(){return innerWidth<=720};
 // 앱으로 가는 단추: 소개 페이지를 본 사람은 다음부터 바로 앱으로
 document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-app]');if(a){try{localStorage.setItem('omr_app','1')}catch(x){}}});
 // 효과 줄이기
 var fx=document.getElementById('fx');function fxSync(){if(fx)fx.setAttribute('aria-pressed',String(lite()))}
 if(fx)fx.addEventListener('click',function(){var on=!lite();H.classList.toggle('lite',on);try{localStorage.setItem('omr_intro_lite',on?'1':'0')}catch(e){}fxSync();layout();frame(true)});fxSync();
 // 첫 화면 단어 순서
 document.querySelectorAll('.hero h1 .w').forEach(function(w,i){w.style.setProperty('--i',i)});

 /* 구간표 */
 var E=function(t){return 1-Math.pow(1-t,3)};
 function parse(el){return el.getAttribute('data-anim').split('|').map(function(s){var a=s.trim().split(/\s+/);return {k:a[0],a:+a[1],b:+a[2],v0:+a[3],v1:+a[4]}})}
 var scenes=[].slice.call(document.querySelectorAll('[data-pin]')).map(function(sc){
  return {el:sc,items:[].slice.call(sc.querySelectorAll('[data-anim]')).map(function(el){return {el:el,t:parse(el),last:''}}),steps:[].slice.call(sc.querySelectorAll('.steps li')),counts:[].slice.call(sc.querySelectorAll('[data-count]')),top:0,len:1}});
 var hz=document.querySelector('[data-hz]'),track=hz&&hz.querySelector('.track'),hzTop=0,hzLen=1;
 function val(t,k,p,def){var v=def,hit=false;t.forEach(function(s){if(s.k!==k)return;if(p<=s.a){if(!hit)v=s.v0}else if(p>=s.b){v=s.v1;hit=true}else{v=s.v0+(s.v1-s.v0)*E((p-s.a)/(s.b-s.a));hit=true}});return v}
 function apply(it,p){var t=it.t,x=val(t,'x',p,0),y=val(t,'y',p,0),s=val(t,'s',p,1),r=val(t,'r',p,0),o=val(t,'o',p,1);
  var tr='translate3d('+x.toFixed(2)+'%,'+y.toFixed(2)+'%,0) rotate('+r.toFixed(2)+'deg) scale('+s.toFixed(4)+')';
  if(it.el.classList.contains('chip'))tr='translate(-50%,-50%) translate3d('+x.toFixed(2)+'vw,'+y.toFixed(2)+'vh,0) rotate('+r.toFixed(2)+'deg)';
  if(it.el.classList.contains('scan'))tr='translate3d(0,'+(y*4).toFixed(1)+'px,0)';
  if(it.el.classList.contains('phone')&&it.el.classList.contains('sm'))tr='translate(0,-50%) translate3d('+x.toFixed(2)+'%,'+y.toFixed(2)+'%,0) rotate('+r.toFixed(2)+'deg) scale('+s.toFixed(4)+')';
  var key=tr+o.toFixed(3);if(key===it.last)return;it.last=key;it.el.style.transform=tr;it.el.style.opacity=o.toFixed(3)}
 function layout(){var y=scrollY;scenes.forEach(function(s){var r=s.el.getBoundingClientRect();s.top=r.top+y;s.len=Math.max(1,s.el.offsetHeight-innerHeight)});
  if(hz&&track){if(lite()||mob()){hz.style.height='';track.style.transform=''}else{var w=track.scrollWidth-innerWidth;hz.style.height=(innerHeight+Math.max(0,w))+'px';var r=hz.getBoundingClientRect();hzTop=r.top+y;hzLen=Math.max(1,w)}}}
 var cur=scrollY,tgt=scrollY,ticking=false;
 function frame(force){
  if(lite()||mob()){scenes.forEach(function(s){s.items.forEach(function(it){if(mob()){it.el.style.transform='';it.el.style.opacity='';it.last=''}else apply(it,1)}); /* 효과 줄이기: 장면의 마지막 모습으로 */s.steps.forEach(function(li){li.classList.add('on')});s.counts.forEach(function(c){c.textContent=(+c.dataset.count).toLocaleString('ko-KR')})});ticking=false;return}
  cur+= (tgt-cur)*0.12;if(Math.abs(tgt-cur)<.4)cur=tgt;
  scenes.forEach(function(s){var p=Math.min(1,Math.max(0,(cur-s.top)/s.len));if(!force&&(cur<s.top-innerHeight*1.2||cur>s.top+s.len+innerHeight))return;
   s.items.forEach(function(it){apply(it,p)});
   s.steps.forEach(function(li){li.classList.toggle('on',p>=+(li.dataset.at||0))});
   s.counts.forEach(function(c){var n=Math.round(+c.dataset.count*E(Math.min(1,p/.6)));c.textContent=n.toLocaleString('ko-KR')})});
  if(hz&&track){var p=Math.min(1,Math.max(0,(cur-hzTop)/hzLen));track.style.transform='translate3d('+(-p*hzLen).toFixed(1)+'px,0,0)'}
  if(cur!==tgt)requestAnimationFrame(function(){frame()});else ticking=false}
 function kick(){tgt=scrollY;if(!ticking){ticking=true;requestAnimationFrame(function(){frame()})}}
 addEventListener('scroll',kick,{passive:true});addEventListener('resize',function(){layout();kick()});
 addEventListener('load',function(){layout();frame(true)});layout();frame(true);
 if('ResizeObserver' in window){var rt=0;new ResizeObserver(function(){clearTimeout(rt);rt=setTimeout(function(){layout();kick();frame(true)},60)}).observe(document.body)} // 늦게 불러온 그림으로 높이가 바뀌면 장면 위치를 다시 잰다

 // 맨 위 막대: 내려갈 때 숨고 올라올 때 나온다
 var top=document.getElementById('top'),ly=scrollY;addEventListener('scroll',function(){var y=scrollY;if(top)top.classList.toggle('hide',y>ly&&y>200);ly=y},{passive:true});

 // 섹션마다 부분 등장(제목 → 글 → 그림). 스크립트가 없으면 처음부터 보인다
 var rv=[];document.querySelectorAll('.gap,.ways,.kinds,.ana,.subj,.loop,.hz,.two,.par,.acad,.env,.price,.cta,.faq,.foot').forEach(function(sec){var k=0;sec.querySelectorAll('h2,.say,.sheet,.res,.note,.shot,.sq,.half h3,.half img,.half .phone,.plan,.btn.big,.cards details,.mark,.fcols,.gp,.wy article,.also,.kpg,.qcard,.callouts li,.sj article,.tiles li,.bento article,.env li').forEach(function(el){if(el.closest('.track')&&!el.classList.contains('shot'))return;el.classList.add('rv');el.style.setProperty('--i',k++%6);rv.push(el)})});
 if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'});rv.forEach(function(el){io.observe(el)})}else rv.forEach(function(el){el.classList.add('in')});

 // 네 과목 숫자: 화면에 들어오면 0부터 센다(효과 줄이기면 처음부터 끝 숫자)
 var ups=[].slice.call(document.querySelectorAll('[data-up]'));
 if(ups.length&&!lite()&&'IntersectionObserver' in window){ups.forEach(function(el){el.textContent='0'});
  var uo=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;uo.unobserve(e.target);var el=e.target,n=+el.dataset.up,t0=performance.now();
   (function st(t){var p=Math.min(1,(t-t0)/1300);el.textContent=Math.round(n*E(p)).toLocaleString('ko-KR');if(p<1)requestAnimationFrame(st)})(t0)})},{rootMargin:'0px 0px -10% 0px'});
  ups.forEach(function(el){uo.observe(el)})}

 // 카드 기울이기 · 자석 단추 (마우스일 때만)
 if(matchMedia('(hover:hover) and (pointer:fine)').matches){
  document.querySelectorAll('.tilt').forEach(function(c){c.addEventListener('pointermove',function(e){if(lite())return;var r=c.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;c.style.transform='perspective(1000px) rotateX('+(-y*5).toFixed(2)+'deg) rotateY('+(x*6).toFixed(2)+'deg)'+(c.classList.contains('mid')?' translateY(-18px)':'')});c.addEventListener('pointerleave',function(){c.style.transform=''})});
  document.querySelectorAll('.mag').forEach(function(b){b.addEventListener('pointermove',function(e){if(lite())return;var r=b.getBoundingClientRect();b.style.transform='translate('+((e.clientX-r.left-r.width/2)*.18).toFixed(1)+'px,'+((e.clientY-r.top-r.height/2)*.28).toFixed(1)+'px)'});b.addEventListener('pointerleave',function(){b.style.transform=''})})}

 // 직접 해 보기: 미니 OMR
 var omr=document.getElementById('omr');if(omr){var bs=[].slice.call(omr.querySelectorAll('.sheet button'));
  function grade(){var wrong=bs.filter(function(b){return b.getAttribute('aria-pressed')==='true'}),sc=Math.round((bs.length-wrong.length)/bs.length*100);
   document.getElementById('sc').textContent=sc;var cnt={};wrong.forEach(function(b){cnt[b.dataset.t]=(cnt[b.dataset.t]||0)+1});
   var ks=Object.keys(cnt).sort(function(a,b){return cnt[b]-cnt[a]});document.getElementById('wk').textContent=ks.length?ks[0]:'없음 · 모두 맞혔어요';
   var nx=document.getElementById('nx'),li=[];if(ks.length){ks.slice(0,2).forEach(function(k,i){li.push(k+' · '+(i?3:6)+'문항')});li.push('틀린 문항 다시 풀기 · '+wrong.length+'문항')}else li.push('한 단계 어려운 문항 · 10문항');
   nx.innerHTML=li.map(function(t){return '<li>'+t+'</li>'}).join('')}
  bs.forEach(function(b){b.addEventListener('click',function(){var on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',String(on));b.querySelector('i').textContent=on?'틀림':'맞음';grade()})});grade()}
})();
