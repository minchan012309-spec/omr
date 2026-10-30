/* 무료 체험 신청(trial.html) · 문의(contact.html) 공통: 서버 표 site_leads 에 남기고 개발자 탭에서 확인한다(supabase/sql_26_site_leads.sql) */
(function(){
'use strict';
var U='https://airejqudbqfsfhadvwqp.supabase.co',K='sb_publishable_YPbHe6NNnV5eQT0u1SZiCg_JLvrM7IV';
var H=document.documentElement,f=document.getElementById('lead'),out=document.getElementById('leadOut'),t0=Date.now();
var thm=document.getElementById('thm');if(thm)thm.addEventListener('click',function(){var t=H.dataset.theme==='light'?'dark':'light';H.dataset.theme=t;try{localStorage.setItem('omr_theme',t)}catch(e){}});
if(!f)return;
var val=function(n){var e=f.elements[n];if(!e)return '';if(e.length&&e[0]&&e[0].type==='checkbox')return Array.prototype.filter.call(e,function(x){return x.checked}).map(function(x){return x.value}).join(', ');return String(e.value||'').trim()};
function msg(t,ok){out.textContent=t;out.className='out '+(ok?'ok':'err');out.hidden=false}
f.addEventListener('submit',function(ev){ev.preventDefault();
 if(val('website'))return; // 자동 입력 방지(사람에게는 보이지 않는 칸)
 if(Date.now()-t0<2500){msg('조금만 천천히 다시 눌러 주세요.');return}
 var phone=val('phone'),email=val('email');
 if(!val('name')){msg('이름을 적어 주세요.');f.elements.name.focus();return}
 if(!phone&&!email){msg('연락받을 전화번호나 이메일 중 하나는 적어 주세요.');(f.elements.phone||f.elements.email).focus();return}
 if(f.dataset.kind==='contact'&&!val('message')){msg('문의 내용을 적어 주세요.');f.elements.message.focus();return}
 if(email&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){msg('이메일 주소를 확인해 주세요.');f.elements.email.focus();return}
 if(f.elements.agree&&!f.elements.agree.checked){msg('개인정보 수집 · 이용에 동의해 주세요.');f.elements.agree.focus();return}
 var body={kind:f.dataset.kind,name:val('name'),academy:val('academy')||null,phone:phone||null,email:email||null,students:val('students')||null,subjects:val('subjects')||null,topic:val('topic')||null,message:val('message')||null};
 var btn=f.querySelector('button[type=submit]');btn.disabled=true;btn.textContent='보내는 중…';
 fetch(U+'/rest/v1/site_leads',{method:'POST',headers:{apikey:K,'Content-Type':'application/json',Prefer:'return=minimal'},body:JSON.stringify(body)}).then(function(r){
  if(!r.ok)throw new Error(r.status);
  f.hidden=true;var d=document.getElementById('leadDone');if(d){d.hidden=false;d.focus()}
 }).catch(function(e){btn.disabled=false;btn.textContent=f.dataset.kind==='trial'?'체험 신청하기':'문의 보내기';
  msg('보내지 못했어요. 잠시 뒤 다시 시도해 주세요. ('+(e&&e.message||'연결')+')')})});
})();
