/* Solvi 소개 페이지: 직접 눌러 보는 설명들.
   첫 화면 모니터(기울기 · 노란 점 설명) · 흐름 다섯 단계 · 틀린 번호만 누르는 채점 · 선생님/학생/학부모 · 교재 쪽 넘기기 ·
   문항 풀기 · 앱 화면 넘기기 · 출결 단말 체험 · 요금제(서버 값 + 필요한 기능 고르기) · 자주 묻는 질문 · 떠 있는 단추 */
(function(){
 var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
 var RM=matchMedia('(prefers-reduced-motion: reduce)'),still=function(){return RM.matches};
 var clamp=function(v,a,b){return Math.max(a,Math.min(b,v))};
 var esc=function(t){return String(t==null?'':t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
 // 앱으로 가는 단추: 소개 페이지를 본 사람은 다음부터 바로 앱으로
 document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-app]');if(a){try{localStorage.setItem('omr_app','1')}catch(x){}}});

 /* 맨 위 막대 · 목차(좁은 화면은 펼침 메뉴) · 지금 보는 섹션 표시 · 맨 위로 */
 var hd=$('#top'),nav=$('#nav'),menu=$('#menu'),toTop=$('#toTop');
 function navOpen(on){nav.classList.toggle('open',on);menu.setAttribute('aria-expanded',String(on));menu.setAttribute('aria-label',on?'목차 닫기':'목차 열기')}
 menu.addEventListener('click',function(e){e.stopPropagation();navOpen(!nav.classList.contains('open'))});
 nav.addEventListener('click',function(e){if(e.target.closest('a'))navOpen(false)});
 document.addEventListener('click',function(e){if(nav.classList.contains('open')&&!e.target.closest('#nav'))navOpen(false)});
 document.addEventListener('keydown',function(e){if(e.key==='Escape'){navOpen(false);tipShow(-1)}});
 toTop.addEventListener('click',function(){scrollTo({top:0,behavior:still()?'auto':'smooth'});$('.brand').focus({preventScroll:true})});
 var links=$$('#nav a');
 if('IntersectionObserver' in window){var spy=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;links.forEach(function(a){var on=a.getAttribute('href')==='#'+e.target.id;a.classList.toggle('on',on);if(on)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')})})},{rootMargin:'-45% 0px -50% 0px'});
  links.forEach(function(a){var s=$(a.getAttribute('href'));if(s)spy.observe(s)})}

 /* 첫 화면 모니터: 처음엔 뒤로 기울어 있다가 스크롤하면 바로 선다 */
 var xdr=$('#xdr'),xt=$('#xdrT');
 function tilt(){if(!xt)return;if(still()){xt.style.transform='none';return}var r=xdr.getBoundingClientRect(),vh=innerHeight,p=clamp((vh-r.top)/(vh*.85),0,1),e=1-Math.pow(1-p,2);
  xt.style.transform='rotateX('+(14*(1-e)).toFixed(2)+'deg) scale('+(.94+.06*e).toFixed(4)+')'}
 var ticking=false;function onScroll(){var y=scrollY;hd.classList.toggle('sc',y>8);toTop.classList.toggle('on',y>700);if(!ticking){ticking=true;requestAnimationFrame(function(){ticking=false;tilt()})}}
 addEventListener('scroll',onScroll,{passive:true});addEventListener('resize',onScroll);onScroll();

 /* 노란 점: 화면 부분 설명 */
 var TIPS=[['왼쪽 메뉴','홈과 학습 · 만들기 · 학원 · 설정으로 묶여 있어요. 지금은 「취약 유형」 화면이에요.'],
  ['보는 범위','전체 학생, 반, 학생 한 명 중에서 골라 기록을 모아 봐요. 지금은 솔비 학생 한 명을 보고 있어요.'],
  ['다섯 단계 판정','유형마다 누적 정답률과 최근 6회를 합쳐 해골 · 위험 · 보통 · 양호 · 완전 정복으로 나눠요. 아직 안 푼 유형도 따로 세요.'],
  ['유형 카드','소단원마다 유형 카드가 놓여 있어요. 카드에 정답률과 문제 은행 문항 수(DB)가 적혀 있고, 눌러서 학습지에 넣을 유형을 골라요.'],
  ['선택한 유형','「취약 유형 자동 선택」이 약한 유형 5개, 20문항을 골랐어요. 「학습지 만들기」를 누르면 바로 인쇄할 학습지가 나와요.']];
 var tip=$('#hsTip'),body=$('.xdr-body'),hsCur=-1,hsBtns=$$('.hs'),hsList=$$('.hs-list button');
 function tipShow(i){if(!tip)return;if(i===hsCur)i=-1;hsCur=i;
  hsBtns.forEach(function(b){b.setAttribute('aria-expanded',String(+b.dataset.hs===i))});hsList.forEach(function(b){b.setAttribute('aria-pressed',String(+b.dataset.hs===i))});
  if(i<0){tip.hidden=true;return}
  tip.innerHTML='<b>'+(i+1)+'. '+TIPS[i][0]+'</b><span>'+TIPS[i][1]+'</span>';tip.hidden=false;tip.style.left=tip.style.top='';
  if(innerWidth>720){var d=hsBtns[i],br=body.getBoundingClientRect(),dr=d.getBoundingClientRect(),cx=dr.left+dr.width/2-br.left,cy=dr.top+dr.height/2-br.top,w=tip.offsetWidth,h=tip.offsetHeight;
   var x=cx<br.width*.6?cx+22:cx-22-w,y=clamp(cy-h/2,8,br.height-h-8);tip.style.left=x+'px';tip.style.top=y+'px'}}
 hsBtns.concat(hsList).forEach(function(b){b.addEventListener('click',function(e){e.stopPropagation();tipShow(+b.dataset.hs)})});
 document.addEventListener('click',function(e){if(hsCur>=0&&!e.target.closest('.hs-tip'))tipShow(-1)});
 addEventListener('resize',function(){if(hsCur>=0){var i=hsCur;hsCur=-1;tipShow(i)}});

 /* 탭 묶음 공통: 화살표 키로 옮기고, 고르면 fn(i) */
 function tabs(list,fn,vert){list.forEach(function(b,i){b.addEventListener('click',function(){fn(i,true)});
  b.addEventListener('keydown',function(e){var k=e.key,n=list.length,j=-1;if(k===(vert?'ArrowDown':'ArrowRight'))j=(i+1)%n;else if(k===(vert?'ArrowUp':'ArrowLeft'))j=(i-1+n)%n;else if(k==='Home')j=0;else if(k==='End')j=n-1;
   if(j>=0){e.preventDefault();fn(j,true);list[j].focus()}})})}
 function sel(list,i){list.forEach(function(b,j){b.setAttribute('aria-selected',String(i===j));b.tabIndex=i===j?0:-1})}

 /* 흐름 다섯 단계: 화면에 보이는 동안 7초마다 다음 단계로. 한 번 누르면 자동 넘김은 멈춘다 */
 var flow=$('[data-flow]');if(flow){var sts=$$('.step',flow),sb=$$('.step>button',flow),fvs=$$('.fv',flow),fi=0,auto=true,vis=false,ft=0,DUR=7000;
  function fgo(i,user){if(user){auto=false;clearTimeout(ft)}fi=i;sel(sb,i);sts.forEach(function(s,j){s.classList.toggle('on',j===i);s.classList.remove('run')});
   fvs.forEach(function(v,j){var on=j===i;if(on&&v.hidden){v.hidden=false;v.classList.remove('on');void v.offsetWidth;v.classList.add('on')}else if(!on)v.hidden=true});run()}
  function run(){clearTimeout(ft);if(!auto||!vis||still())return;var s=sts[fi];s.style.setProperty('--dur',DUR+'ms');void s.offsetWidth;s.classList.add('run');ft=setTimeout(function(){fgo((fi+1)%sts.length)},DUR)}
  tabs(sb,fgo,true);
  if('IntersectionObserver' in window)new IntersectionObserver(function(es){vis=es[0].isIntersecting;if(vis)run();else{clearTimeout(ft);sts.forEach(function(s){s.classList.remove('run')})}},{threshold:.35}).observe(flow)}

 /* 틀린 번호만 누르는 채점 */
 var omr=$('#omr');if(omr){var rows=$$('.rows button',omr);
  var LV=function(a){return a>=1?['완전 정복','#7ee2a8']:a>=.7?['양호','#7ee2a8']:a>=.5?['보통','#fdc62d']:a>0?['위험','#ff9a8b']:['해골 · 거의 못 맞힘','#ff9a8b']};
  function grade(){var n=rows.length,wrong=rows.filter(function(b){return b.getAttribute('aria-pressed')==='true'}),ok=n-wrong.length,t={},order=[];
   $('#sc').textContent=Math.round(ok/n*100);$('#scn').textContent=n+'문항 중 '+ok+'문항을 맞혔어요';
   rows.forEach(function(b){var k=b.dataset.t;if(!t[k]){t[k]={n:0,w:0};order.push(k)}t[k].n++;if(b.getAttribute('aria-pressed')==='true')t[k].w++});
   var ty=order.map(function(k){return {k:k,a:(t[k].n-t[k].w)/t[k].n,w:t[k].w,n:t[k].n}}).sort(function(a,b){return a.a-b.a||b.n-a.n});
   $('#tyb').innerHTML=ty.map(function(o){var l=LV(o.a);return '<li style="--c:'+l[1]+'"><span>'+esc(o.k)+'</span><em>'+l[0]+' · '+Math.round(o.a*100)+'%</em><span class="bar"><i style="--w:'+Math.max(3,o.a*100)+'%"></i></span></li>'}).join('');
   var weak=ty.filter(function(o){return o.w}),nx=[];weak.slice(0,2).forEach(function(o,i){nx.push([o.k,i?3:6])});
   if(wrong.length)nx.push(['틀린 문항 다시 풀기',wrong.length]);else nx.push(['같은 범위 한 단계 어려운 문항',10]);
   $('#nx').innerHTML=nx.map(function(x){return '<li><span>'+esc(x[0])+'</span><b>'+x[1]+'문항</b></li>'}).join('')}
  rows.forEach(function(b){b.addEventListener('click',function(){var on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',String(on));b.querySelector('.mk').textContent=on?'틀림':'맞음';grade()})});
  $('#omrReset').addEventListener('click',function(){rows.forEach(function(b){b.setAttribute('aria-pressed','false');b.querySelector('.mk').textContent='맞음'});grade()});grade()}

 /* 선생님 · 학생 · 학부모: 선택 표시가 미끄러진다 */
 $$('[data-seg]').forEach(function(seg){var bs=$$('button',seg),pill=$('.pill',seg),ps=bs.map(function(b){return document.getElementById(b.getAttribute('aria-controls'))});
  function place(i){var b=bs[i];pill.style.width=b.offsetWidth+'px';pill.style.transform='translateX('+b.offsetLeft+'px)'}
  function go(i){sel(bs,i);ps.forEach(function(p,j){var on=j===i;if(on&&p.hidden){p.hidden=false;p.classList.remove('on');void p.offsetWidth;p.classList.add('on')}else if(!on)p.hidden=true});place(i)}
  tabs(bs,go);addEventListener('resize',function(){place(bs.findIndex(function(b){return b.getAttribute('aria-selected')==='true'}))});
  pill.style.transition='none';place(0);requestAnimationFrame(function(){pill.style.transition=''});
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){place(bs.findIndex(function(b){return b.getAttribute('aria-selected')==='true'}))})});

 /* 교재 종류: 실제 쪽을 부채꼴로 */
 var bk=$('[data-books]');if(bk){var kb=$$('.kinds button',bk),fan=$('#fan'),bkD=$('#bkD');
  var POS={1:[[0,-2]],2:[[-.34,-5],[.3,4]],3:[[-.46,-7],[0,0],[.46,7]]};
  function show(i,user){sel(kb,i);var b=kb[i],names=b.dataset.pages.split(' '),pos=POS[names.length],wr=names.length===1?(innerWidth<=560?.62:.54):(innerWidth<=560?.52:.44),w=fan.offsetWidth*wr;
   bkD.textContent=b.dataset.desc;fan.setAttribute('aria-label',b.querySelector('b').textContent+' 쪽 예시');
   $$('img',fan).forEach(function(im){im.style.opacity='0';im.style.transform+=' translateY(24px)';setTimeout(function(){im.remove()},still()?0:380)});
   names.forEach(function(n,j){var im=new Image();im.src='intro/'+n+'.webp';im.width=1000;im.height=1414;im.alt='';im.decoding='async';
    var x=pos[j][0]*w,r=pos[j][1],tr='translate(calc(-50% + '+x.toFixed(1)+'px),-50%) rotate('+r+'deg)';
    im.style.width=(wr*100)+'%';im.style.zIndex=names.length===3&&j===1?3:j+1;im.style.opacity='0';im.style.transform=tr+' translateY(36px)';im.dataset.tr=tr;fan.appendChild(im);
    setTimeout(function(){im.style.opacity='1';im.style.transform=tr},still()?0:60+j*70)})}
  tabs(kb,show,true);show(0);
  fan.addEventListener('pointerover',function(e){var im=e.target.closest('img');if(!im)return;$$('img',fan).forEach(function(x){x.style.zIndex=x===im?9:(x.dataset.z||x.style.zIndex)})});
  var rz=0;addEventListener('resize',function(){clearTimeout(rz);rz=setTimeout(function(){show(kb.findIndex(function(b){return b.getAttribute('aria-selected')==='true'}))},150)})}

 /* 문항 하나: A~D 설명에 올리면 문항의 그 부분이 빛나고, 선지를 누르면 채점 */
 var qc=$('#qcard');if(qc){var cl=$$('.callouts li');
  function hl(k){cl.forEach(function(li){li.classList.toggle('on',li.dataset.k===k)});$$('[data-k]',qc).forEach(function(el){el.classList.toggle('hl',el.dataset.k===k)})}
  cl.forEach(function(li){li.addEventListener('pointerenter',function(){hl(li.dataset.k)});li.addEventListener('pointerleave',function(){hl('')});li.addEventListener('click',function(){hl(li.classList.contains('on')?'':li.dataset.k)})});
  var qx=$('#qexp'),cb=$$('.ch button',qc);
  cb.forEach(function(b,i){b.addEventListener('click',function(){cb.forEach(function(x){x.classList.remove('ok','no');x.removeAttribute('aria-pressed')});b.setAttribute('aria-pressed','true');
   var n=b.querySelector('.cn').textContent;
   if(b.dataset.ok){b.classList.add('ok');qx.innerHTML='<b>정답 '+n+'</b>결합 에너지는 결합 1 mol을 끊는 데 필요한 에너지예요. 클수록 끊기 어려우니 그 결합은 강해요.'}
   else{b.classList.add('no');qx.innerHTML='<b>'+n+'은 틀렸어요</b>옳은 문장: '+esc(b.dataset.fix)+' 다른 선지도 눌러 보세요.'};hl('D');setTimeout(function(){hl('')},1400)})})}

 /* 숫자: 화면에 들어오면 0부터 센다 */
 var ups=$$('[data-up]');if(ups.length&&!still()&&'IntersectionObserver' in window){
  var uo=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;uo.unobserve(e.target);var el=e.target,n=+el.dataset.up,t0=performance.now();
   (function st(t){var p=Math.min(1,(t-t0)/1200);el.textContent=Math.round(n*(1-Math.pow(1-p,3))).toLocaleString('ko-KR');if(p<1)requestAnimationFrame(st)})(t0)})},{rootMargin:'0px 0px -15% 0px'});
  ups.forEach(function(el){uo.observe(el)})}

 /* 앱 화면 넘기기: 화살표 · 끌기(마우스) · 진행 막대 */
 var gal=$('#gal');if(gal){var gp=$('#galP'),gn=$('#galN'),bar=$('#galBar');
  function step(){var gi=$('.gi',gal);return gi?gi.offsetWidth+20:400}
  function upd(){var max=gal.scrollWidth-gal.clientWidth,r=gal.clientWidth/gal.scrollWidth;bar.style.width=(r*100)+'%';bar.style.transform='translateX('+(max>0?gal.scrollLeft/max*(1/r-1)*100:0)+'%)';gp.disabled=gal.scrollLeft<4;gn.disabled=gal.scrollLeft>max-4}
  gp.addEventListener('click',function(){gal.scrollBy({left:-step(),behavior:still()?'auto':'smooth'})});gn.addEventListener('click',function(){gal.scrollBy({left:step(),behavior:still()?'auto':'smooth'})});
  gal.addEventListener('scroll',function(){requestAnimationFrame(upd)},{passive:true});addEventListener('resize',upd);addEventListener('load',upd);upd();
  gal.addEventListener('keydown',function(e){if(e.key==='ArrowRight'){e.preventDefault();gn.click()}else if(e.key==='ArrowLeft'){e.preventDefault();gp.click()}});
  var dx=0,sl=0,dn=false,moved=false;
  gal.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse')return;dn=true;moved=false;dx=e.clientX;sl=gal.scrollLeft});
  addEventListener('pointermove',function(e){if(!dn)return;var d=e.clientX-dx;if(Math.abs(d)>4){moved=true;gal.classList.add('drag')}if(moved)gal.scrollLeft=sl-d});
  addEventListener('pointerup',function(){if(!dn)return;dn=false;if(moved){var s=step(),t=Math.round(gal.scrollLeft/s)*s;gal.classList.remove('drag');gal.scrollTo({left:t,behavior:still()?'auto':'smooth'})}})}

 /* 출결 단말 체험판: 앱 단말과 같은 흐름. 처음 누른 번호는 등원, 같은 번호를 다시 누르면 하원, 00000은 없는 번호 */
 var kio=$('#kio');if(kio){var pin='',seen={},kt=0,ht=0,NAMES=['솔비','하늘','바다','별빛'],dg=$('#kDg'),ms=$('#kMs'),hi=$('#kHi'),go=$('[data-k=go]',kio);
  var OK='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
  function now(){var d=new Date(),o={timeZone:'Asia/Seoul'};return [d.toLocaleTimeString('ko-KR',Object.assign({hour:'2-digit',minute:'2-digit',hour12:false},o)),d.toLocaleDateString('ko-KR',Object.assign({month:'long',day:'numeric',weekday:'long'},o))]}
  function clock(){var n=now();$('#kTm').textContent=n[0];$('#kDt').textContent=n[1]}clock();setInterval(clock,15000);
  function draw(){var n=Math.max(5,pin.length),h='';for(var i=0;i<n;i++)h+='<i class="'+(pin[i]?'f':i===pin.length?'c':'')+'"></i>';dg.innerHTML=h;dg.setAttribute('aria-label','입력한 숫자 '+pin.length+'개');go.disabled=pin.length<3}
  function hide(){clearTimeout(ht);hi.className='kio-hi';hi.innerHTML=''}
  function submit(){clearTimeout(kt);if(pin.length<3)return;var p=pin;pin='';draw();
   if(p==='00000'){ms.innerHTML='번호를 찾을 수 없어요<small>선생님께 출결 번호를 물어보세요</small>';dg.classList.remove('sh');void dg.offsetWidth;dg.classList.add('sh');return}
   var kind=seen[p]?'out':'in',name=NAMES[(+p.slice(-2)||0)%NAMES.length];if(kind==='in')seen[p]=1;else delete seen[p];ms.textContent='';
   hi.className='kio-hi on '+kind;hi.innerHTML='<div class="ck">'+OK+'</div><h4>'+name+' 학생</h4><p>'+(kind==='in'?'어서 와요!':'잘 가요!')+'</p><span class="tm">'+now()[0]+' '+(kind==='in'?'등원':'하원')+'</span>';
   clearTimeout(ht);ht=setTimeout(hide,2800)}
  function key(k){if(k==='go')return submit();if(hi.classList.contains('on'))hide();if(k==='c')pin=pin.slice(0,-1);else if(pin.length<8)pin+=k;ms.textContent='';draw();clearTimeout(kt);if(pin.length>=5)kt=setTimeout(submit,700)}
  $$('.kio-kp button',kio).forEach(function(b){b.addEventListener('click',function(){key(b.dataset.k)})});hi.addEventListener('click',hide);
  kio.addEventListener('keydown',function(e){if(/^\d$/.test(e.key))key(e.key);else if(e.key==='Backspace')key('c');else if(e.key==='Enter'&&!e.target.closest('button'))key('go')});draw()}

 /* 요금제: 개발자 탭 「요금제」(site_config 의 pricing). 못 읽으면 HTML 기본값 그대로 */
 var plansEl=$('#plans'),PL=null;
 function topIdx(n,pl){var h=pl?pl.findIndex(function(x){return x.hl}):-1;return h>=0?h:n-1}
 function needUpd(){var cards=$$('.plan',plansEl),n=cards.length,sel=$$('.need [aria-pressed=true]'),out=$('#needO');
  if(!sel.length){cards.forEach(function(c){c.classList.remove('hit','dim')});out.textContent='고른 기능이 없어요. 위에서 필요한 기능을 눌러 보세요.';return}
  var lv=Math.min(n-1,Math.max.apply(null,sel.map(function(b){return +b.dataset.lv})));
  cards.forEach(function(c,i){c.classList.toggle('hit',i===lv);c.classList.toggle('dim',i<lv)});
  var nm=$('h3',cards[lv]).firstChild.textContent.trim();out.innerHTML='고른 '+sel.length+'가지가 모두 들어 있는 요금제는 <b>'+esc(nm)+'</b>예요.'+(n===3&&lv===1?' 학생은 50명까지 등록할 수 있어요.':'')}
 $$('.need button').forEach(function(b){b.addEventListener('click',function(){b.setAttribute('aria-pressed',String(b.getAttribute('aria-pressed')!=='true'));needUpd()})});
 (function(){if(!plansEl||!window.fetch)return;
  var U='https://airejqudbqfsfhadvwqp.supabase.co',K='sb_publishable_YPbHe6NNnV5eQT0u1SZiCg_JLvrM7IV';
  fetch(U+'/rest/v1/site_config?key=eq.pricing&select=value',{headers:{apikey:K}}).then(function(r){return r.ok?r.json():null}).then(function(j){
   var v=j&&j[0]&&j[0].value;if(!v||!v.plans||!v.plans.length)return;PL=v.plans;
   var ct=(v.contact||'').trim(),ctHref=ct?(/^https?:/.test(ct)?ct:'mailto:'+ct):'',top=topIdx(PL.length,PL);
   var who=['학생 최대 30명','학생 최대 50명 · 이후 1명당 추가 요금','학생 수 제한 없음'];
   plansEl.innerHTML=PL.map(function(x,i){var p=(x.price||'').trim(),num=/^[\d,]+$/.test(p),ask=/문의/.test(x.cta||'')&&ctHref,isTop=i===top;
    var n0=num?+p.replace(/,/g,''):-1,price=p?(n0===0?'무료':num?n0.toLocaleString('ko-KR')+'원':esc(p)):'';num=num&&n0>0;
    return '<article class="plan'+(isTop?' top':'')+'" data-i="'+i+'"><h3>'+esc(x.name)+(isTop?' <span class="all">모든 기능</span>':'')+'</h3><p class="price">'+(price?'<b>'+price+'</b>'+(num&&x.unit?'<small>'+esc(x.unit)+'</small>':''):'<b class="tbd">요금 준비 중</b>')+'</p>'+(x.desc?'<p class="pd">'+esc(x.desc)+'</p>':'')+
     (PL.length===3?'<p class="who">'+who[i]+'</p>':'')+((x.items||[]).length?'<ul>'+x.items.map(function(t){return '<li>'+esc(t)+'</li>'}).join('')+'</ul>':'<ul></ul>')+
     '<a class="btn '+(isTop?'yel':'line')+'" href="'+(ask?esc(ctHref):'index.html?app=1#login')+'"'+(ask?'':' data-app')+'>'+esc(x.cta||'무료로 시작하기')+'</a></article>'}).join('');
   if(PL.length===3)$$('.cmp thead th[data-n]').forEach(function(th){var x=PL[+th.dataset.n];if(x&&x.name)th.textContent=x.name.replace(/^솔비\s*/,'')});
   var note=$('#prNote');if(note)note.textContent=v.note||'';
   if(ctHref){var fm=$('#fMail');if(fm)fm.href=ctHref}
   needUpd()}).catch(function(){})})();

 /* 자주 묻는 질문: 열고 닫을 때 높이가 부드럽게 */
 $$('.fl details').forEach(function(d){var s=$('summary',d),a=$('.fa',d),busy=false;
  s.addEventListener('click',function(e){if(still()||!a.animate)return;e.preventDefault();if(busy)return;busy=true;
   if(d.open){var h=a.offsetHeight;a.animate([{height:h+'px',opacity:1},{height:'0px',opacity:0}],{duration:260,easing:'cubic-bezier(.2,.8,.2,1)'}).onfinish=function(){d.open=false;busy=false}}
   else{d.open=true;var h2=a.offsetHeight;a.animate([{height:'0px',opacity:0},{height:h2+'px',opacity:1}],{duration:320,easing:'cubic-bezier(.2,.8,.2,1)'}).onfinish=function(){busy=false}}})});

 /* 섹션 제목과 그림만 한 번 떠오른다 */
 var rv=$$('.sh,.ana-t,.faq-t,.flow-vis,.omr,.seg,.fan,.qcard,.sj,.gal,.tablet-w,.plans,.cmp,.fl,.end h2');
 if('IntersectionObserver' in window&&!still()){rv.forEach(function(el){el.classList.add('rv')});
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -10% 0px'});rv.forEach(function(el){io.observe(el)})}
})();
