// 지울 수 없는 기본 학습지(해원고 물질과 에너지 빌드업): 자동 등록 · 삭제/이름/편집 잠금 · 복제 · 소단원별 재출제 · 다시 출력 고르기
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.addInitScript(()=>{localStorage.setItem('omr_subj_v1','me');localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test',email:'Teacher@Example.com'}}));
  window.__posts=[];const f=window.fetch.bind(window);
  window.fetch=(u,o)=>{const url=String(typeof u==='string'?u:u.url);if(!url.includes('supabase.co'))return f(u,o);
   if(o&&o.method==='POST'&&url.includes('/rest/v1/worksheets')){window.__posts.push(JSON.parse(o.body));return Promise.resolve(new Response('',{status:201}))}
   return Promise.resolve(new Response('[]',{headers:{'Content-Type':'application/json'}}))}});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof presetSeed==='function'&&Object.keys(BIDX).length&&teacher());
 const r=await page.evaluate(async()=>{
  const out={};const P=PRESETS[0];
  // 다른 계정에는 등록되지 않는다
  await presetSeed();out.otherAccount=WSH.some(w=>w.id===P.id);
  P.owner=await sha256hex('teacher@example.com');await presetSeed();
  const w=WSH.find(x=>x.id===P.id);out.seeded=!!w;out.locked=w&&w.locked;out.n=w&&w.codes.length;out.posted=__posts.filter(x=>x.wid===P.id).length;out.metaLocked=__posts[0]&&__posts[0].meta.locked;out.metaPreset=__posts[0]&&__posts[0].meta.preset;
  await presetSeed();out.postedAgain=__posts.filter(x=>x.wid===P.id).length;
  // 목록 메뉴: 삭제 · 이름 변경 · 문항 편집 없음, 복제 · 재출제 · 다시 출력 있음
  const menu=wsOpts2(w);out.menuDel=/wsDel\(/.test(menu);out.menuRename=/wsRename\(/.test(menu);out.menuEdit=/wsEdit\(/.test(menu);out.menuDup=/wsClone\(/.test(menu);out.menuRegen=/wsRegen\(/.test(menu);out.menuPick=/wsReprintPick\(/.test(menu);
  window.confirm=()=>true;await wsDel(P.id);out.afterDel=!!WSH.find(x=>x.id===P.id&&!x.deletedAt);
  WSSEL.clear();WSSEL.add(P.id);await wsDelSel();out.afterDelSel=!!WSH.find(x=>x.id===P.id&&!x.deletedAt);
  window.prompt=()=>'바뀐 이름';await wsRename(P.id);out.title=WSH.find(x=>x.id===P.id).title;
  const before=WSH.length;wsClone(P.id);const dup=WSH[WSH.length-1];out.dupInfo=[WSH.length-before,dup.id,dup.locked,dup.preset,dup.codes.length];out.dup=WSH.length===before+1&&dup.id!==P.id&&!dup.locked&&!dup.preset&&dup.codes.length===148;
  // 학생 범위를 골라도 기본 학습지는 목록에 보임
  STU.push({id:'s9',name:'예시'});CUR_S='s9';navGo('ws');await new Promise(r=>setTimeout(r,300));out.scoped=document.body.innerText.includes(w.title);CUR_S='';
  // 다시 출력 고르기
  wsReprintPick(P.id);out.pick=[...document.querySelectorAll('#cfgBox .pkc b')].map(b=>b.textContent);closeCfg();
  // 재출제: 소단원 6개, 하나 빼고 1:1 교체
  await presetRegen(P.id);out.chips=document.querySelectorAll('#cfgBox .prs .chp').length;
  const subs=[...new Set(w.codes.map(c=>byCode[c].sub))];presetRegenTog(subs[0]);
  let opened=null;const keep=window.openWs;window.openWs=rec=>{opened=rec};await presetRegenGo(P.id);window.openWs=keep;
  const nw=WSH[WSH.length-1];out.regenN=nw.codes.length;out.regenExpect=w.codes.filter(c=>byCode[c].sub!==subs[0]).length;out.regenLocked=!!nw.locked;
  out.regenNoSub0=nw.codes.every(c=>byCode[c].sub!==subs[0]);
  // 변형이 있는 원본은 원본이 아닌 문항으로 바뀐다
  const withVar=w.codes.filter(c=>byCode[c].sub!==subs[0]&&DATA.some(q=>q.fam===byCode[c].fam&&q.hw&&q.hw!=='o'));
  out.withVar=withVar.length;out.replaced=withVar.filter((c,i)=>true).length&&nw.codes.filter(c=>byCode[c].hw!=='o').length;
  out.unique=new Set(nw.codes).size===nw.codes.length;out.regenTitle=nw.title;
  return out});
 console.log(r);
 assert.equal(r.otherAccount,false,'이메일 해시가 다르면 등록하지 않음');
 assert.equal(r.seeded,true);assert.equal(r.locked,1);assert.equal(r.n,148);assert.equal(r.posted,1);assert.equal(r.metaLocked,1);assert.equal(r.metaPreset,'me-haewon-buildup');
 assert.equal(r.postedAgain,1,'두 번 등록하지 않음');
 assert.equal(r.menuDel,false);assert.equal(r.menuRename,false);assert.equal(r.menuEdit,false);assert.equal(r.menuDup,true);assert.equal(r.menuRegen,true);assert.equal(r.menuPick,true);
 assert.equal(r.afterDel,true,'삭제 안 됨');assert.equal(r.afterDelSel,true,'선택 삭제 안 됨');assert.notEqual(r.title,'바뀐 이름');
 assert.equal(r.dup,true,'복제본은 일반 학습지');
 assert.equal(r.scoped,true,'학생 범위에서도 기본 학습지 보임');assert.deepEqual(r.pick,['빌드업 PDF','앱 인쇄 양식']);
 assert.equal(r.chips,6);assert.equal(r.regenN,r.regenExpect);assert.equal(r.regenLocked,false);assert.equal(r.regenNoSub0,true);assert.equal(r.unique,true);
 assert.ok(r.replaced>=r.withVar,'변형이 있는 원본은 모두 교체');
 console.log('PASS 기본 학습지 등록·잠금·복제·소단원 재출제·출력 고르기');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
