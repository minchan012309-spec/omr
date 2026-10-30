/* Solvi 소개: 살아 있는 유형 지도 · 한 바퀴 무대 · 연결 그래프 + 실제 앱 캡처. 스크롤은 브라우저 기본 그대로(wheel · touch · key 를 가로채지 않고, 위치를 바꾸지 않는다).
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
/* 맨 위로: 주소 해시에 기대지 않고 직접 올라간다(같은 해시를 다시 눌러도 · 고정 장면 한가운데에서도 동작) */
D.addEventListener('click',function(e){var a=e.target.closest('a[href="#hero"],a[href="#top"]');if(!a)return;e.preventDefault();var rm=!H.classList.contains('fx');window.scrollTo({top:0,left:0,behavior:rm?'auto':'smooth'});try{history.replaceState(null,'',location.pathname+location.search)}catch(ig){}var f=$('#main');if(f&&f.focus){f.setAttribute('tabindex','-1');f.focus({preventScroll:true})}});
var thm=$('#thm');if(thm)thm.addEventListener('click',function(){var t=H.dataset.theme==='light'?'dark':'light';H.dataset.theme=t;try{localStorage.setItem('omr_theme',t)}catch(e){}});

/* ---------- 요금제: 개발자 탭 「요금제」(site_config 의 pricing). 못 읽으면 HTML 기본값 그대로 ---------- */
var plansEl=$('#plans'),PL=null;
function topIdx(n,pl){var h=pl?pl.findIndex(function(x){return x.hl}):-1;return h>=0?h:n-1}
function needUpd(){var cards=$$('.plan',plansEl),n=cards.length,sel=$$('.need [aria-pressed=true]'),out=$('#needO');
 if(!sel.length){cards.forEach(function(c){c.classList.remove('hit','dim')});out.textContent='고른 기능이 없어요. 위에서 필요한 기능을 눌러 보세요.';return}
 var lv=Math.min(n-1,Math.max.apply(null,sel.map(function(b){return +b.dataset.lv})));
 cards.forEach(function(c,i){c.classList.toggle('hit',i===lv);c.classList.toggle('dim',i<lv)});
 if(!cards[lv])return;var nm=$('h3',cards[lv]).firstChild.textContent.trim();out.innerHTML='고른 '+sel.length+'가지가 모두 들어 있는 요금제는 <b>'+esc(nm)+'</b>예요.'+(n===3&&lv===1?' 학생은 50명까지 등록할 수 있어요.':'')}
function bindNeed(b){b.addEventListener('click',function(){b.setAttribute('aria-pressed',String(b.getAttribute('aria-pressed')!=='true'));needUpd()})}
$$('.need button').forEach(bindNeed);
/* 요금제별 비교표: 개발자 탭이 보낸 줄(g=묶음 제목, t=기능, v=요금제별 칸). O · 빈칸(—) · 글자 */
function cmpCell(c,top){c=String(c==null?'':c).trim();var y=/^(o|○|◯|포함|ㅇ)$/i.test(c),n=!c||/^(x|×|-|—|없음)$/i.test(c),cls=(y?'y':n?'n':'')+(top?' top':'');
 var parts=c.split(';'),h=y?'O':n?'—':esc(parts[0].trim())+(parts[1]?'<small>'+esc(parts.slice(1).join(';').trim())+'</small>':'');return '<td'+(cls?' class="'+cls.trim()+'"':'')+'>'+h+'</td>'}
function cmpBuild(cmp,rows){var n=PL.length,top=topIdx(n,PL),pr=function(x){var p=String(x.price||'').trim(),n0=/^[\d,]+$/.test(p)?+p.replace(/,/g,''):-1;return n0===0?'무료':n0>0?n0.toLocaleString('ko-KR')+'원':p||'문의'};
 var h='<tr><th scope="col"><span class="sr-only">기능</span></th>'+PL.map(function(x,i){return '<th scope="col" data-i="'+i+'"'+(i===top?' class="top"':'')+'>'+esc(x.name)+'</th>'}).join('')+'</tr>';
 var b='<tr class="price"><th scope="row">월 요금</th>'+PL.map(function(x,i){return '<td data-i="'+i+'"'+(i===top?' class="top"':'')+'>'+esc(pr(x))+'</td>'}).join('')+'</tr>';
 rows.forEach(function(r){if(r.g!=null)b+='<tr class="g"><th scope="row" colspan="'+(n+1)+'">'+esc(r.g)+'</th></tr>';else b+='<tr><th scope="row">'+esc(r.t)+'</th>'+PL.map(function(x,i){return cmpCell((r.v||[])[i],i===top)}).join('')+'</tr>'});
 $('thead',cmp).innerHTML=h;$('tbody',cmp).innerHTML=b;cmp.hidden=false}

(function(){if(!plansEl||!window.fetch)return;
 var U='https://airejqudbqfsfhadvwqp.supabase.co',K='sb_publishable_YPbHe6NNnV5eQT0u1SZiCg_JLvrM7IV';
 fetch(U+'/rest/v1/site_config?key=eq.pricing&select=value',{headers:{apikey:K}}).then(function(r){return r.ok?r.json():null}).then(function(j){
  var v=j&&j[0]&&j[0].value;if(!v||!v.plans||!v.plans.length)return;PL=v.plans;
  var ct=String(v.contact||'').trim(),ctHref=/^https?:\/\//i.test(ct)?ct:'contact.html',top=topIdx(PL.length,PL);
  var who=['학생 최대 30명','학생 최대 50명 · 이후 1명당 추가 요금','학생 수 제한 없음'];
  plansEl.innerHTML=PL.map(function(x,i){var p=String(x.price||'').trim(),num=/^[\d,]+$/.test(p),ask=/문의/.test(x.cta||'')&&ctHref,isTop=i===top;
   var n0=num?+p.replace(/,/g,''):-1,price=p?(n0===0?'무료':num?n0.toLocaleString('ko-KR')+'원':esc(p)):'';num=num&&n0>0;
   return '<article class="plan'+(isTop?' top':'')+'" data-i="'+i+'"><h3>'+esc(x.name)+'</h3><p class="price">'+(price?'<b>'+price+'</b>'+(num&&x.unit?'<small>'+esc(x.unit)+'</small>':''):'<b class="tbd">요금 준비 중</b>')+'</p>'+(x.desc?'<p class="pd">'+esc(x.desc)+'</p>':'')+
    ((x.who!=null?String(x.who).trim():(PL.length===3?who[i]:''))?'<p class="who">'+esc(x.who!=null?String(x.who).trim():who[i])+'</p>':'')+((x.items||[]).length?'<ul>'+x.items.map(function(t){return '<li>'+esc(t)+'</li>'}).join('')+'</ul>':'<ul></ul>')+
    '<a class="btn '+(isTop?'yel':'line')+'" href="'+(ask?esc(ctHref):'index.html?app=1#login')+'"'+(ask?'':' data-app')+'>'+esc(x.cta||'무료로 시작하기')+'</a></article>'}).join('');
  var note=$('#prNote');if(note)note.textContent=v.note||'';
  var cmp=$('#cmp');if(cmp&&v.cmp&&v.cmp.length){cmpBuild(cmp,v.cmp)}
  else if(cmp){if(PL.length!==3)cmp.hidden=true;else PL.forEach(function(x,i){var th=$('thead th[data-i="'+i+'"]',cmp),td=$('tr.price td[data-i="'+i+'"]',cmp),pr=String(x.price||'').trim(),n0=/^[\d,]+$/.test(pr)?+pr.replace(/,/g,''):-1;if(th)th.textContent=x.name||th.textContent;if(td)td.textContent=n0===0?'무료':n0>0?n0.toLocaleString('ko-KR')+'원':pr||'문의'})}
  
  if(v.need&&v.need.length){var nb=$('.need');if(nb)nb.innerHTML=v.need.map(function(n){return '<button type="button" aria-pressed="false" data-lv="'+Math.max(0,Math.min(PL.length-1,(+n.lv||1)-1))+'">'+esc(n.t)+'</button>'}).join('');$$('.need button').forEach(bindNeed)}
  needUpd()}).catch(function(){})})();

/* ---------- 밝은 면(마지막 장면 · 요금제 · 질문 · 바닥글) 위에서는 머리글도 밝게 ---------- */
function watchLight(){if(!('IntersectionObserver' in window))return;
 var io=new IntersectionObserver(function(es){es.forEach(function(e){lightSecs+=e.isIntersecting?1:-1;if(lightSecs<0)lightSecs=0});theme()},{rootMargin:'0px 0px -96% 0px'});
 $$('.sec,.ft,.sc-end').forEach(function(s){io.observe(s)})}

/* ---------- 목차: 지금 보고 있는 구역(실제 교차 결과)에 aria-current ---------- */
(function(){if(!('IntersectionObserver' in window))return;var links=$$('.nav a[href^="#"]'),seen={};
 var io=new IntersectionObserver(function(es){es.forEach(function(e){seen[e.target.id]=e.isIntersecting});var cur=null;links.forEach(function(a){if(seen[a.getAttribute('href').slice(1)])cur=a});links.forEach(function(a){if(a===cur)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')})},{rootMargin:'-45% 0px -45% 0px'});
 links.forEach(function(a){var t=D.getElementById(a.getAttribute('href').slice(1));if(t)io.observe(t)})})();

/* ---------- 히어로: 살아 있는 취약 유형 지도(누르면 고르기 · 처음 한 번 채점 결과가 칠해진다) ---------- */
(function(){var map=$('#tmap');if(!map)return;
 var tiles=$$('.tt',map),lg={},nE=$('#tmN'),qE=$('#tmQ'),live=$('.tm-live',map),PER=5,timers=[],done=false;
 $$('.tm-lg li',map).forEach(function(li){lg[li.dataset.lv]=$('b',li)});
 var LV={skull:'해골 · 거의 못 맞힘',red:'위험',yellow:'보통',gray:'아직 안 풀어 봄',green:'양호',star:'완전 정복'};
 tiles.forEach(function(t){t.dataset.final=t.dataset.lv;t.dataset.fp=t.getAttribute('aria-pressed');
  t.setAttribute('aria-label',$('span',t).textContent+' · '+LV[t.dataset.lv]+(t.dataset.p?' · 정답률 '+t.dataset.p+'%':'')+(+t.dataset.n?' · '+t.dataset.n+'문항 풀이':''))});
 function counts(){var c={skull:0,red:0,yellow:0,gray:0,green:0,star:0},n=0;tiles.forEach(function(t){c[t.classList.contains('pre')?'gray':t.dataset.lv]++;if(t.getAttribute('aria-pressed')==='true')n++});
  for(var k in lg)lg[k].textContent=c[k];nE.textContent=n;qE.textContent=n*PER}
 function finish(){if(done)return;done=true;timers.forEach(clearTimeout);tiles.forEach(function(t){t.classList.remove('pre');if(t.dataset.fp)t.setAttribute('aria-pressed',t.dataset.fp)});if(live)live.textContent='반영 완료';counts()}
 map.addEventListener('click',function(e){var t=e.target.closest('.tt');if(!t)return;finish();t.dataset.fp='';t.setAttribute('aria-pressed',String(t.getAttribute('aria-pressed')!=='true'));counts()});
 if(!H.classList.contains('fx')){counts();return}
 /* 처음: 모두 「아직 안 풀어 봄」 → 채점 결과가 한 칸씩 칠해지고 → 약한 유형이 골라진다 */
 tiles.forEach(function(t){t.classList.add('pre');t.setAttribute('aria-pressed','false')});if(live)live.textContent='채점 반영 중';counts();
 var order=[6,0,9,1,5,2,7,10,3,11,14,4,12,8,13];
 order.forEach(function(ix,k){timers.push(setTimeout(function(){var t=tiles[ix];if(!t)return;t.classList.remove('pre');t.classList.add('pop');setTimeout(function(){t.classList.remove('pop')},360);counts()},500+k*85))});
 var picks=tiles.filter(function(t){return t.dataset.fp==='true'});
 picks.forEach(function(t,k){timers.push(setTimeout(function(){t.setAttribute('aria-pressed','true');counts()},500+order.length*85+260+k*150))});
 timers.push(setTimeout(finish,500+order.length*85+260+picks.length*150+100))})();

/* ---------- 스크롤 연출 공통 ---------- */
var cl=function(v){return v<0?0:v>1?1:v},out=function(p){return 1-Math.pow(1-p,3)},io2=function(p){return p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2};
var seg=function(p,a,b){return cl((p-a)/(b-a))},lerp=function(a,b,t){return a+(b-a)*t};

/* 문제은행 장면에 쓰는 실제 문항(물질과 에너지 문제은행의 코드 · 유형 · 난이도) */
var QS=[["Q41-056","Ⅳ","반응 속도식·반응 차수·반응 속도 상수","중"],["Q31-032","Ⅲ","연소·생성·분해·용해·기화 엔탈피의 정의","하"],["Q43-040","Ⅳ","온도와 반응 속도","상"],["Q32-016","Ⅲ","열화학 반응식의 조합(헤스 법칙 계산)","중"],
 ["Q42-013","Ⅳ","유효 충돌의 조건","하"],["Q42-042","Ⅳ","반응 진행에 따른 에너지 도표 해석","중"],["Q33-018","Ⅲ","엔트로피가 증가·감소하는 경우","하"],["Q41-121","Ⅳ","1차 반응과 반감기","상"],
 ["Q31-041","Ⅲ","연소·생성·분해·용해·기화 엔탈피의 정의","중"],["Q43-024","Ⅳ","온도와 반응 속도","중"],["Q41-031","Ⅳ","반응 계수와 농도 변화량의 관계","하"],["Q42-028","Ⅳ","활성화 에너지와 활성화물","상"]];
var DOT={'하':1,'중':2,'상':3,'최':4};

/* ---------- 한 바퀴 무대: 스크롤 진행도 p(0~1)에서 모든 조각의 자리를 바로 계산한다 ---------- */
var FLOW=(function(){var run=$('#flowRun'),fb=$('#fb');if(!run||!fb)return null;
 var box=$('#fqs',fb);box.innerHTML=QS.map(function(q){var d='';for(var k=1;k<=4;k++)d+=k<=DOT[q[3]]?'●':'○';return '<div class="fq"><span class="c">'+q[0]+'<i>'+d+'</i></span><span class="t">'+esc(q[2])+'</span></div>'}).join('');
 var qs=$$('.fq',fb),chips=$$('.fchips span',fb),chipBox=$('.fchips',fb),sheet=$('.fsheet',fb),qr=$('.fqr',fb),scan=$('b',qr),phone=$('.fphone',fb),res=$('.res',phone),score=$('.fscore',fb),dds=$$('dd',score),map=$('.fmap',fb),mt=$$('.fm-g span',map),bars=$$('.fbars b',map),wrong=$$('.fwrong',fb),neu=$('.fnew',fb),loop=$$('.floop path',fb),cap=$('.fcap',fb);
 var steps=$$('.flow-steps li'),fills=$$('.flow-steps a>i i'),descs=$$('.fd'),cur=-1;
 var CAP=['물질과 에너지 · Ⅳ 반응 속도 · 중 이상 → 6문항','고른 6문항이 A4 학습지로 · 쪽마다 채점 QR','QR을 찍으면 OMR이 열리고, 답을 고르면 바로 채점','틀린 43 · 47 · 51번이 유형으로 모여요','약한 유형으로 새 학습지 → 다시 풀면 색이 바뀌어요'];
 /* 고른 문항: Ⅳ 단원이면서 난이도 중 이상 */
 var sel=QS.map(function(q){return q[1]==='Ⅳ'&&q[3]!=='하'});
 /* 넓은 화면은 72×54, 휴대폰은 44×64 단위 무대. 같은 이야기를 자리만 바꿔 그린다 */
 var mq=matchMedia('(max-width: 860px)'),L;
 var LD={g:function(i){return {x:1.5+(i%4)*16.6,y:6.8+Math.floor(i/4)*8.6}},slot:[40.5,9.5],ph:[-14,0,0,1],map5:[-35,0,1],mt:[[40.6,9.2],[55.6,9.2],[40.6,15.2],[55.6,15.2],[40.6,21.2],[55.6,21.2]],w0:[9,31],loop:['M600 470 C 660 520, 690 300, 640 120 C 610 40, 520 20, 470 40','M482 26 L466 41 L486 50'],vb:'0 0 720 540'};
 var LM={g:function(i){return {x:1+(i%2)*21.5,y:5.5+Math.floor(i/2)*7.8}},slot:[8.5,10.5],ph:[-12,0,0,1],ph4:[-1,5,.8],map5:[-12,-2,.75],mt:[[14.6,9.4],[29.4,9.4],[14.6,15.6],[29.4,15.6],[14.6,21.8],[29.4,21.8]],w0:[6,40],loop:['M330 600 C 250 650, 40 620, 30 430','M16 448 L30 426 L46 446'],vb:'0 0 440 640'};
 function lay(){L=mq.matches?LM:LD;var sv=$('.floop',fb);sv.setAttribute('viewBox',L.vb);loop[0].setAttribute('d',L.loop[0]);loop[1].setAttribute('d',L.loop[1])}
 var G=function(i){return L.g(i)};
 var slot=0,SL=sel.map(function(s){return s?slot++:-1});

 function st(el,o,t){el.style.opacity=o.toFixed(3);el.style.transform=t||'none';el.style.visibility=o<.01?'hidden':'visible'}
 function update(p,e){var step=Math.min(4,Math.floor(p*5+.0001));
  if(step!==cur){cur=step;steps.forEach(function(li,i){li.classList.toggle('on',i===step);var a=$('a',li);if(i===step)a.setAttribute('aria-current','step');else a.removeAttribute('aria-current')});descs.forEach(function(d,i){d.classList.toggle('on',i===step)});cap.textContent=CAP[step]}
  fills.forEach(function(f,i){f.style.transform='scaleX('+cl(p*5-i).toFixed(3)+')'});
  /* 01 고르기 */
  var cOut=seg(p,.2,.24);st(chipBox,(1-cOut)*cl(e*1.4),'translateY('+((1-out(cl(e)))*12).toFixed(1)+'px)');
  chips.forEach(function(c,i){c.classList.toggle('on',p>.025+i*.035)});
  qs.forEach(function(q,i){var g=G(i),ent=out(cl(e*1.5-i*.04)),o=ent,x=g.x,y=g.y+(1-ent)*3,s=1;
   var dim=(QS[i][1]!=='Ⅳ'?seg(p,.06,.1):0)+(QS[i][1]==='Ⅳ'&&QS[i][3]==='하'?seg(p,.11,.15):0);o*=1-.8*cl(dim);
   q.classList.toggle('sel',sel[i]&&p>.16&&p<.3);
   if(!sel[i])o*=1-seg(p,.2,.23);
   else{var k=SL[i],m=io2(seg(p,.22+k*.012,.3+k*.012)),tx=L.slot[0]+(k%2)*13.6,ty=L.slot[1]+Math.floor(k/2)*9.2;x=lerp(x,tx,m);y=lerp(y,ty,m);s=lerp(1,.78,m);o*=1-seg(p,.31+k*.006,.34+k*.006)}
   st(q,o,'translate('+x.toFixed(2)+'em,'+y.toFixed(2)+'em) scale('+s.toFixed(3)+')')});
  /* 02 만들기: 학습지 */
  var sIn=out(seg(p,.24,.32)),sOut=seg(p,.6,.64);st(sheet,sIn*(1-sOut),'scale('+lerp(.9,1,sIn).toFixed(3)+') translateY('+(sOut*-2).toFixed(2)+'em)');
  var qIn=seg(p,.33,.37),qOut=seg(p,.53,.57);st(qr,qIn*(1-qOut),'scale('+lerp(1.3,1,out(qIn)).toFixed(3)+')');
  scan.style.top=(seg(p,.44,.5)*85).toFixed(1)+'%';scan.style.opacity=p>.44&&p<.5?1:0;
  /* 03 채점: 휴대폰 화면 캡처 → 결과 */
  var pIn=out(seg(p,.4,.46)),pOut=mq.matches?seg(p,.86,.9):seg(p,.8,.84),p4=L.ph4?io2(seg(p,.6,.64)):0;st(phone,pIn*(1-pOut),'translate('+((1-pIn)*L.ph[0]+(L.ph4?L.ph4[0]*p4:0)).toFixed(2)+'em,'+(L.ph4?L.ph4[1]*p4:0).toFixed(2)+'em) scale('+(L.ph4?lerp(1,L.ph4[2],p4):1).toFixed(3)+')');
  res.style.opacity=seg(p,.5,.53).toFixed(3);
  var scIn=seg(p,.52,.55),scOut=seg(p,.8,.83);st(score,scIn*(1-scOut),'translateY('+((1-out(scIn))*1.5).toFixed(2)+'em)');
  var cnt=out(seg(p,.52,.58));dds[0].textContent=Math.round(9*cnt);dds[1].textContent=Math.round(3*cnt);dds[2].textContent=Math.round(75*cnt)+'%';
  /* 04 분석: 틀린 문항이 유형 칸으로 날아가 칠한다 */
  var mIn=out(seg(p,.6,.64)),mv=io2(seg(p,.8,.86));st(map,mIn,'translate('+(mv*L.map5[0]).toFixed(2)+'em,'+((1-mIn)*2+mv*L.map5[1]).toFixed(2)+'em) scale('+lerp(1,L.map5[2],mv).toFixed(3)+')');
  mt.forEach(function(t,i){var s0=p>.66+i*.014?t.dataset.a:'gray';if(p>.93+i*.008)s0=t.dataset.b;if(t.dataset.s!==s0){t.dataset.s=s0}t.classList.toggle('pk',p>.84&&p<.93&&/skull|red/.test(t.dataset.a))});
  bars.forEach(function(b,i){b.style.transform='scaleX('+(+b.style.getPropertyValue('--w')*out(seg(p,.72+i*.015,.78+i*.015))).toFixed(3)+')'});
  wrong.forEach(function(w,i){var a=seg(p,.63+i*.008,.65+i*.008),m=io2(seg(p,.65+i*.012,.71+i*.012)),f=seg(p,.71+i*.012,.73+i*.012),to=L.mt[i];
   var x=lerp(L.w0[0]+i*2.6,to[0],m)/1.4,y=lerp(L.w0[1]+i*2.2,to[1],m)/1.4;st(w,a*(1-f),'translate('+x.toFixed(2)+'em,'+y.toFixed(2)+'em) scale('+lerp(1,.8,m).toFixed(3)+')')});
  /* 05 다시 학습: 왼쪽으로 비킨 지도에서 새 학습지가 나오고, 한 바퀴 화살표 */
  var nIn=out(seg(p,.86,.9));st(neu,nIn,'translateX('+((1-nIn)*4).toFixed(2)+'em) scale('+lerp(.94,1,nIn).toFixed(3)+')');
  loop.forEach(function(l,i){l.style.strokeDashoffset=(1-seg(p,.9+i*.04,.95+i*.04)).toFixed(3)})}
 lay();mq.addEventListener&&mq.addEventListener('change',function(){lay();update(lastP<0?0:lastP,1)});
 var lastP=-1,upd=update;update=function(p,e){lastP=p;upd(p,e)};
 return {run:run,update:function(p,e){update(p,e)}}})();

/* ---------- 연결 그래프: 가운데 기록에서 열두 기능으로 선이 그려지고, 그 위로 기록이 흐른다 ---------- */
var LINK=(function(){var run=$('#linkRun'),lb=$('#lb');if(!run||!lb)return null;
 var svg=$('.lsvg',lb),nodes=$$('.ln',lb),C={x:360,y:280},NS='http://www.w3.org/2000/svg',paths=[],dots=[],gli=$$('.link-g li');
 var mq=matchMedia('(max-width: 860px)'),P=[];
 function place(){var m=mq.matches,W=m?440:720,Hh=m?640:560;C={x:W/2,y:Hh/2};svg.setAttribute('viewBox','0 0 '+W+' '+Hh);
  P=nodes.map(function(n,i){var a=(-165+30*i)*Math.PI/180,x=m?W/2+168*Math.cos(a):+n.dataset.x,y=m?Hh/2+268*Math.sin(a):+n.dataset.y;n.style.left=(x/W*100).toFixed(2)+'%';n.style.top=(y/Hh*100).toFixed(2)+'%';return {x:x,y:y,g:+n.dataset.g}})}
 place();
 function curve(a,b,bend){var mx=(a.x+b.x)/2,my=(a.y+b.y)/2,dx=b.x-a.x,dy=b.y-a.y,l=Math.sqrt(dx*dx+dy*dy)||1;return 'M'+a.x+' '+a.y+' Q'+(mx-dy/l*bend).toFixed(1)+' '+(my+dx/l*bend).toFixed(1)+' '+b.x+' '+b.y}
 function add(d,cls,ends,from,to){var p=D.createElementNS(NS,'path');p.setAttribute('d',d);p.setAttribute('pathLength','1');if(cls)p.setAttribute('class',cls);svg.appendChild(p);var o={el:p,ends:ends,from:from,to:to,len:0};paths.push(o);return o}
 function draw(){svg.textContent='';paths=[];dots=[];
 P.forEach(function(n,i){add(curve(C,n,18),'',[i],.04+n.g*.28+(i%6)*.022,.16+n.g*.28+(i%6)*.022)});
 /* 학습 순환 고리와, 사람 · 운영으로 건너가는 선 */
 [[0,1],[1,2],[2,3],[3,4],[4,1],[3,5],[2,6],[3,7],[9,8],[11,8],[10,6]].forEach(function(e,k){add(curve(P[e[0]],P[e[1]],e[0]<6&&e[1]<6?-40:60),'x',e,.84+k*.008,.93+k*.008)});
 paths.forEach(function(o){o.len=o.el.getTotalLength()});
 paths.forEach(function(o,k){if(k%2&&o.el.getAttribute('class')!=='x')return;var c=D.createElementNS(NS,'circle');c.setAttribute('r','4');c.style.opacity=0;svg.appendChild(c);dots.push({c:c,o:o,ph:(k*.137)%1,sp:.18+(k%3)*.05})});}
 draw();mq.addEventListener&&mq.addEventListener('change',function(){place();draw();var q=lastP;lastP=-1;update(q<0?1:q)});
 function hot(i){paths.forEach(function(o){o.el.classList.toggle('hot',i!=null&&o.ends.indexOf(i)>=0)});nodes.forEach(function(n,j){n.classList.toggle('on',j===i)})}
 nodes.forEach(function(n,i){n.addEventListener('mouseenter',function(){hot(i)});n.addEventListener('mouseleave',function(){hot(null)});n.addEventListener('focus',function(){hot(i)});n.addEventListener('blur',function(){hot(null)});
  n.addEventListener('click',function(){hot(n.classList.contains('on')?null:i)})});
 var lastP=-1;
 function update(p){if(Math.abs(p-lastP)<.0005)return;lastP=p;
  var g=p<.33?0:p<.6?1:2;gli.forEach(function(li,i){li.classList.toggle('on',i===g||(p>.86&&!mq.matches))});
  paths.forEach(function(o){o.drawn=seg(p,o.from,o.to);o.el.style.strokeDashoffset=(1-o.drawn).toFixed(3)});
  nodes.forEach(function(n,i){n.classList.toggle('lit',paths[i].drawn>.6)})}
 var raf=0,on=false,t0=0;
 function pulse(t){if(!on){raf=0;return}if(!t0)t0=t;var s=(t-t0)/1000;
  dots.forEach(function(d){if(!(d.o.drawn>.98)){d.c.style.opacity=0;return}var f=(s*d.sp+d.ph)%1,pt=d.o.el.getPointAtLength(d.o.len*(d.o.el.getAttribute('class')==='x'?f:1-f));d.c.setAttribute('cx',pt.x.toFixed(1));d.c.setAttribute('cy',pt.y.toFixed(1));d.c.style.opacity=(Math.sin(f*Math.PI)).toFixed(2)});
  raf=requestAnimationFrame(pulse)}
 function visible(v){on=v&&H.classList.contains('fx');if(on&&!raf)raf=requestAnimationFrame(pulse)}
 if(!H.classList.contains('fx'))update(1);
 return {run:run,update:update,visible:visible}})();


/* ---------- QR 채점: 카메라 창이 쪽 아래 QR로 다가가 확대 → 인식 → OMR → 결과 ---------- */
var QRS=(function(){var run=$('#qrRun'),qb=$('#qb');if(!run||!qb)return null;
 var qz=$('.qz',qb),page=$('.qpage',qb),fd=$('.qfind',qb),scan=$('b',fd),ok=$('.qok',qb),ph=$('.qphone',qb),res=$('.res',ph),sc=$('.qscore',qb),dds=$$('dd',sc),steps=$$('.qr-steps li'),mq=matchMedia('(max-width: 860px)'),cur=-1;
 /* 쪽 안 QR 가운데(34×48.1 창 기준): 가로 92% · 세로 89.7%, 한 변 약 1.4 */
 var QX=31.28,QY=43.16,CX=17,CY=24.05;
 function st(el,o,t){el.style.opacity=o.toFixed(3);el.style.transform=t||'none';el.style.visibility=o<.01?'hidden':'visible'}
 function update(p,e){var m=mq.matches,i=p<.3?0:p<.5?1:p<.78?2:3;
  if(i!==cur){cur=i;steps.forEach(function(li,k){li.classList.toggle('on',k===i)})}
  var zin=io2(seg(p,.08,.32)),zout=io2(seg(p,.5,.6)),mm=zin*(1-zout),z=1+4*mm,dx=(CX-QX)*mm,dy=(CY-QY)*mm;
  page.style.transform='translate('+dx.toFixed(2)+'em,'+dy.toFixed(2)+'em) scale('+z.toFixed(3)+')';
  var k=zout,sx=m?-4*k:0;st(qz,cl(e*1.3),'translate('+sx.toFixed(2)+'em,0) scale('+lerp(1,m?.5:.55,k).toFixed(3)+')');
  var fx=QX+dx,fy=QY+dy,fs=2.2*z/10;st(fd,seg(p,.12,.2)*(1-seg(p,.5,.55)),'translate('+(fx-5).toFixed(2)+'em,'+(fy-5).toFixed(2)+'em) scale('+fs.toFixed(3)+')');
  fd.classList.toggle('ok',p>.42);scan.style.top=(seg(p,.32,.42)*88).toFixed(1)+'%';scan.style.opacity=p>.32&&p<.42?1:0;
  ok.textContent=p<.7?'인식 완료 · 물질과 에너지 유형서 3쪽 · 문항 2개':'학생 기록 · 유형 지도에 바로 반영';
  st(ok,seg(p,.42,.46)*(1-seg(p,.56,.6))+seg(p,.8,.84),'translateY('+((1-out(seg(p,.42,.46)))*.6).toFixed(2)+'em)');
  var pin=out(seg(p,.52,.6));st(ph,pin,'translateY('+((1-pin)*10).toFixed(2)+'em)');res.style.opacity=seg(p,.66,.7).toFixed(3);
  st(sc,seg(p,.7,.74),'translateY('+((1-out(seg(p,.7,.74)))*1.5).toFixed(2)+'em)');
  var c=out(seg(p,.7,.78));dds[0].textContent=Math.round(9*c);dds[1].textContent=Math.round(3*c);dds[2].textContent=Math.round(75*c)+'%'}
 return {run:run,update:update}})();

/* ---------- 학원의 하루: 아홉 장면. 화면이 장면마다 다른 방식으로 돌고 · 넘어가고 · 날아간다(스크롤 위치에서 바로 계산, 되감으면 그대로) ---------- */
var DAY=(function(){var run=$('#dayRun');if(!run)return null;
 var steps=$$('.day-steps li'),descs=$$('.dd'),imgs=$$('.day-frame .shot'),MAP=[0,1,2,2,3,4,5,6,7,8],N=9,cur=-1;
 /* 들어올 때(E)와 나갈 때(X)의 모양: [가로 %, 세로 %, 깊이 px, X회전, Y회전, Z회전, 크기] */
 var V=[
  {E:[60,0,-200,0,-58,0,.86],X:[-60,0,-200,0,58,0,.86]},   /* 회전목마처럼 옆으로 돈다 */
  {E:[0,70,-120,-48,0,0,.9],X:[0,-60,-120,40,0,0,.9]},     /* 아래에서 젖혀 올라오고, 위로 넘어간다 */
  {E:[90,10,0,0,0,9,.8],X:[-95,-8,0,0,0,-10,.8]},          /* 기울어진 채 날아든다 */
  {E:[0,0,-600,0,0,0,.6],X:[0,0,420,0,0,0,1.25]},          /* 깊은 곳에서 다가와 지나간다 */
  {E:[0,0,0,0,-110,0,1],X:[0,0,0,0,110,0,1]},              /* 책장처럼 뒤집힌다 */
  {E:[-60,0,-200,0,58,0,.86],X:[60,0,-200,0,-58,0,.86]},
  {E:[0,-70,-120,48,0,0,.9],X:[0,70,-120,-40,0,0,.9]},
  {E:[-90,10,0,0,0,-9,.8],X:[95,-8,0,0,0,10,.8]},
  {E:[0,30,-500,24,0,0,.7],X:[0,0,0,0,0,0,1]}];
 var mix=function(A,B,t){return A.map(function(a,i){return a+(B[i]-a)*t})},ID=[0,0,0,0,0,0,1];
 var tf=function(v){return 'translate3d('+v[0].toFixed(1)+'%,'+v[1].toFixed(1)+'%,'+v[2].toFixed(0)+'px) rotateX('+v[3].toFixed(1)+'deg) rotateY('+v[4].toFixed(1)+'deg) rotateZ('+v[5].toFixed(1)+'deg) scale('+v[6].toFixed(3)+')'};
 function update(p){var f=p*N,i=Math.max(0,Math.min(N-1,Math.floor(f)));
  if(i!==cur){cur=i;steps.forEach(function(li,k){li.classList.toggle('on',k===i);li.classList.toggle('past',k<i);var a=$('a',li);if(k===i)a.setAttribute('aria-current','step');else a.removeAttribute('aria-current')});descs.forEach(function(d,k){d.classList.toggle('on',k===i)});var ck=$('#dayClock'),nw=$('#dayNow');if(ck)ck.textContent=$('time',steps[i]).textContent;if(nw)nw.textContent=i+1}
  var fr=$('.day-frame'),fi=f-i,sw=Math.sin(fi*Math.PI);if(fr)fr.style.transform='rotateY('+((fi-.5)*-7).toFixed(2)+'deg) rotateX('+(sw*2.2).toFixed(2)+'deg)';
  imgs.forEach(function(im,k){var s=MAP[k],v=V[s],d=f-(s+.5),kio=im.classList.contains('kio');if(kio)d-=.12;
   var tin=s===0?1:io2(cl((d+1)/.72)),tout=s===N-1?0:io2(cl((d-.28)/.72)),o=cl(tin*1.4-.2)*(1-cl(tout*1.4-.4));
   var m=tout>0?mix(ID,v.X,tout):mix(v.E,ID,tin);if(kio)m=mix([0,40,0,0,0,0,.9],ID,tin);
   im.style.opacity=o.toFixed(3);im.style.visibility=o<.01?'hidden':'visible';im.style.zIndex=String(Math.round(10-Math.abs(d)*4));im.style.transform=tf(m)})}
 if(!H.classList.contains('fx'))update(0);
 return {run:run,update:update}})();

/* ---------- 기능 전체: 분야 고르기 ---------- */
(function(){var bs=$$('.cats button'),cards=$$('.spec-g .sp'),n=$('#catN');if(!bs.length)return;
 function set(c){bs.forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.cat===c))});var k=0;cards.forEach(function(a){var on=c==='all'||a.dataset.cat===c;a.hidden=!on;if(on){k++;a.classList.add('in')}});n.textContent=k}
 bs.forEach(function(b){b.addEventListener('click',function(){set(b.dataset.cat)})});set('all')})();

/* ---------- 스크롤 → 진행도. 매 프레임 읽기를 먼저, 쓰기는 나중에 ---------- */
(function(){
 /* 숫자 세기(처음 보일 때 한 번): 문제은행 문항 수 등 */
 if('IntersectionObserver' in window&&H.classList.contains('fx')){var cio=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;cio.unobserve(en.target);
  var el=en.target,to=+el.dataset.count,u=el.dataset.unit||'',t0=0;
  (function tick(t){if(!t0)t0=t;var k=cl((t-t0)/900);el.textContent=Math.round(to*out(k)).toLocaleString('ko-KR')+u;if(k<1)requestAnimationFrame(tick)})(performance.now())})},{threshold:.6});
  $$('[data-count]').forEach(function(el){el.textContent='0'+(el.dataset.unit||'');cio.observe(el)});
  var sio=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');sio.unobserve(en.target)}})},{threshold:.35});$$('.sp').forEach(function(s){sio.observe(s)})}
 if(!H.classList.contains('fx')||!window.requestAnimationFrame)return;
 var vh=innerHeight,hdH=64,items=[],q=false;var tmap=$('#tmap');
 $$('[data-fx]').forEach(function(el){var k=el.dataset.fx,it={el:el,k:k,last:-1};
  if(k==='rise')it.kids=$$('[data-lag]',el);
  if(k==='fly'||k==='flip')it.kids=Array.prototype.slice.call(el.children);
  if(k==='fan')it.pages=$$('.shot',el);
  if(k==='strip'){it.pin=$('.strip-pin',el);it.track=$('.strip-track',el)}
  items.push(it)});
 if(LINK&&'IntersectionObserver' in window)new IntersectionObserver(function(es){LINK.visible(es[0].isIntersecting)}).observe(LINK.run);
 function measure(){vh=innerHeight;hdH=hd.offsetHeight||64;items.forEach(function(it){
  if(it.k==='fan'){var w=it.el.clientWidth/2;it.dx=it.pages.map(function(p){return w-(p.offsetLeft+p.offsetWidth/2)})}
  if(it.k==='strip'){it.run=Math.max(0,it.track.scrollWidth-it.pin.clientWidth);it.el.style.height=(it.pin.clientHeight+it.run)+'px'}
  it.last=-1})}
 var runP=function(run){var r=run.getBoundingClientRect(),pin=run.firstElementChild,h=r.height-pin.offsetHeight;return {p:h>0?cl((hdH-r.top)/h):0,e:cl(1+(hdH-r.top)/(vh*.6)),near:r.top<vh*1.2&&r.bottom>-vh*.2}};
 function frame(){q=false;var st=[],fp=FLOW&&runP(FLOW.run),lp=LINK&&runP(LINK.run);
  items.forEach(function(it){var r=it.el.getBoundingClientRect(),p;
   if(it.k==='strip'&&!it.eager&&r.top<vh*2){it.eager=true;$$('img',it.el).forEach(function(i){i.loading='eager'})}
   if(r.bottom<-vh*.5||r.top>vh*1.5)p=r.top>0?0:1;
   else if(it.k==='fan')p=cl((vh*.95-r.top)/(vh*.7));
   else if(it.k==='strip')p=it.run?cl((hdH-r.top)/it.run):0;
   else p=cl((vh-r.top)/(vh*.62));
   st.push(p)});
  if(tmap&&scrollY<vh*1.4){var hk=out(cl(scrollY/(vh*.55))),sm=innerWidth<861?.45:1;tmap.style.transform='rotateX('+(9*(1-hk)*sm).toFixed(2)+'deg) rotateY('+(-15*(1-hk)*sm).toFixed(2)+'deg) scale('+(.95+.05*hk).toFixed(4)+')'}
  if(fp&&fp.near)FLOW.update(fp.p,fp.e);
  var qp=QRS&&runP(QRS.run),dp=DAY&&runP(DAY.run);if(qp&&qp.near)QRS.update(qp.p,qp.e);if(dp&&dp.near)DAY.update(dp.p);
  if(lp&&lp.near)LINK.update(lp.p);
  items.forEach(function(it,i){var p=st[i];if(Math.abs(p-it.last)<.0005)return;it.last=p;var e=out(p);
   if(it.k==='rise'){it.el.style.opacity=(.2+.8*cl(p*1.6)).toFixed(3);it.el.style.transform='translateY('+((1-e)*56).toFixed(1)+'px) scale('+(.965+.035*e).toFixed(4)+')';
    it.kids.forEach(function(c){c.style.transform='translateY('+((1-e)*(+c.dataset.lag||1)*26).toFixed(1)+'px)'})}
   else if(it.k==='fly'){var F=[[-34,0,0,26],[0,30,-28,0],[34,0,0,-26]];it.kids.forEach(function(c,j){var g=F[j%3],q=out(cl(p*1.25-j*.12)),r=1-q;c.style.opacity=(.1+.9*q).toFixed(3);c.style.transform='perspective(1400px) translate3d('+(g[0]*r).toFixed(1)+'%,'+(g[1]*r).toFixed(1)+'%,0) rotateX('+(g[2]*r).toFixed(1)+'deg) rotateY('+(g[3]*r).toFixed(1)+'deg) scale('+(.88+.12*q).toFixed(3)+')'})}
   else if(it.k==='flip')it.kids.forEach(function(c,j){var q=out(cl(p*1.3-j*.18)),r=1-q;c.style.opacity=(.15+.85*q).toFixed(3);c.style.transform='rotateY('+((j%2?-1:1)*92*r).toFixed(1)+'deg) translateZ('+(-120*r).toFixed(0)+'px)';c.style.transformOrigin=j%2?'100% 50%':'0 50%'})
   else if(it.k==='fan')it.pages.forEach(function(pg,j){pg.style.transform='translateX('+((1-e)*it.dx[j]).toFixed(1)+'px) translateY('+((1-e)*(j%2?14:0)).toFixed(1)+'px) rotate('+(e*parseFloat(pg.style.getPropertyValue('--r'))).toFixed(2)+'deg)'});
   else if(it.k==='strip')it.track.style.transform='translateX('+(-p*it.run).toFixed(1)+'px)'})}
 function req(){if(!q){q=true;requestAnimationFrame(frame)}}
 addEventListener('scroll',req,{passive:true});
 var rz;addEventListener('resize',function(){clearTimeout(rz);rz=setTimeout(function(){measure();req()},120)});
 addEventListener('load',function(){measure();req()});
 measure();if(FLOW)FLOW.update(0,0);if(QRS)QRS.update(0,0);if(DAY)DAY.update(0);frame();
 window.__intro={flow:FLOW,link:LINK,qr:QRS,day:DAY};
})();

watchLight();
})();
