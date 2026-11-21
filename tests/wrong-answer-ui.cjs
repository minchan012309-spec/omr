// 선생님 O/X 채점: 오답 문항에 학생이 쓴 답(선택) 입력 → 제출 기록에 a 저장(r=0) → 제출 뒤 오답 문항 답만 수정, 정답은 못 넣음
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.addInitScript(()=>{localStorage.setItem('omr_subj_v1','hl');localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}}));window.__rpc=[];const f=window.fetch.bind(window);window.fetch=(u,o)=>{const url=String(typeof u==='string'?u:u.url);if(!url.includes('supabase.co'))return f(u,o);if(url.includes('/rpc/attempt_wrong_answer')){window.__rpc.push(JSON.parse(o.body));return Promise.resolve(new Response(null,{status:204}))}return Promise.resolve(new Response('[]',{headers:{'Content-Type':'application/json'}}))}});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof wansSet==='function'&&Object.keys(BIDX).length&&teacher());
 const r=await page.evaluate(async()=>{await ensureTags(['hl052']);const qs=DATA.filter(q=>/^\d$/.test(String(q.ans))).slice(0,3);
  STU.push({id:'s1',name:'예시 학생'});CUR_S='s1';newCur(qs);const out={};
  out.allRight=qs.every((q,i)=>cur.ans[i]===q.ans);
  markTog(1);cur.sel=1;fillDet();out.chips=[...document.querySelectorAll('#qdet .wans .chp')].map(b=>b.textContent);
  const wrong=String(qs[1].ans)==='1'?'2':'1';wansSet(1,wrong);out.picked=cur.wa[1];
  wansSet(1,qs[1].ans);out.rightBlocked=cur.wa[1]==='';wansSet(1,wrong);
  markTog(2);
  window.confirm=()=>true;await finish0(true);const h=hist[hist.length-1];out.items=h.items.map(x=>({a:x.a,r:x.r}));out.wrong=wrong;out.ans=qs.map(q=>q.ans);
  // 제출 뒤 수정
srv='cloud';const other=String(qs[2].ans)==='3'?'4':'3';await wansSave(qs[2].code,other);out.after=hist[hist.length-1].items[2];out.rpc=__rpc.length;
  await wansSave(qs[2].code,qs[2].ans);out.afterRight=hist[hist.length-1].items[2];
  showCode(qs[2].code,cur.ans[2]);out.editor=!!document.querySelector('#exp .wans2');
  showCode(qs[0].code,cur.ans[0]);out.editorRight=!!document.querySelector('#exp .wans2');
  return out});
 console.log(r);
 assert.equal(r.allRight,true);assert.equal(r.chips.length,4,'정답 빼고 4개');assert.equal(r.picked,r.wrong);assert.equal(r.rightBlocked,true);
 assert.deepEqual(r.items[0],{a:r.ans[0],r:1});assert.deepEqual(r.items[1],{a:r.wrong,r:0});assert.deepEqual(r.items[2],{a:'',r:0});
 assert.equal(r.after.r,0);assert.ok(r.after.a&&r.after.a!==r.ans[2]);assert.equal(r.rpc,1);
 assert.equal(r.afterRight.r,0,'정답으로 못 바꿈');assert.equal(r.afterRight.a,r.after.a);
 assert.equal(r.editor,true);assert.equal(r.editorRight,false,'정답 문항은 수정 칸 없음');
 console.log('PASS 선생님 채점 오답 학생 답 입력·수정');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
