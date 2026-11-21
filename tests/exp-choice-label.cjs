// 해설 선지 번호: 풀이 줄이 선지 글로 시작하면 ①~⑤를 붙이고 선지 순서로 정렬, 이미 번호가 있으면 그대로
const assert=require('node:assert/strict');
const {chromium,browserOptions}=require('./runtime.cjs');
(async()=>{const browser=await chromium.launch(browserOptions());try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.addInitScript(()=>{localStorage.setItem('omr_subj_v1','hl');localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}}));const f=window.fetch.bind(window);window.fetch=(u,o)=>String(typeof u==='string'?u:u.url).includes('supabase.co')?Promise.resolve(new Response('[]',{headers:{'Content-Type':'application/json'}})):f(u,o)});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof expLabel==='function'&&Object.keys(BIDX).length);
 const r=await page.evaluate(async()=>{await ensureTags(['hl052']);const st=h=>[...h.matchAll(/<p class="st">([\s\S]*?)<\/p>/g)].map(m=>m[1].replace(/<[^>]+>/g,''));
  const q=byCode['G-hl052-0027'];
  const ch='<div class="chs"><div><b>①</b><span>가</span></div><div><b>②</b><span>사과</span></div><div><b>③</b><span>배</span></div><div><b>④</b><span>감나무</span></div><div><b>⑤</b><span>귤</span></div></div>';
  const done='<p class="st">① 옳다.</p><p class="st">② 옳지 않다.</p>';
  return {real:st(q.exp).map(t=>t.slice(0,4)),keep:expLabel(ch,done)===done,partial:st(expLabel(ch,'<p class="st">감나무: 틀림</p><p>설명</p><p class="st">사과는 맞다</p>')),none:expLabel('<p>x</p>','<p class="st">a</p>')==='<p class="st">a</p>'}});
 assert.deepEqual(r.real,['① 남자','② 스승','③ 참 ','④ 많다','⑤ 깊다']);
 assert.equal(r.keep,true);assert.deepEqual(r.partial,['④ 감나무: 틀림','② 사과는 맞다']);assert.equal(r.none,true);
 console.log('PASS 해설 선지 번호 붙이기');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
