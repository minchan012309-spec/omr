/* 학습지 HWPX가 한컴에서 흩어지지 않는지: 한 구역 · 2단 흐름, 한컴 머리말 · 쪽 번호, 가로 줄은 한 문단, 표 칸 바탕색, 흰 글자 배지. */
const assert=require('node:assert/strict');const {chromium,browserOptions}=require('./runtime.cjs');
function unzip(b){let p=0;const f={};while(b.readUInt32LE(p)===0x04034b50){const len=b.readUInt32LE(p+18),n=b.readUInt16LE(p+26),e=b.readUInt16LE(p+28),name=b.subarray(p+30,p+30+n).toString(),start=p+30+n+e;f[name]=b.subarray(start,start+len);p=start+len}return f}
const paras=x=>[...x.matchAll(/<hp:p [^>]*>([\s\S]*?)<\/hp:p>/g)].map(m=>[...m[1].matchAll(/<hp:t>([^<]*)/g)].map(t=>t[1]).join(''));
(async()=>{const browser=await chromium.launch(browserOptions());try{
 // 태블릿(iPad Safari 사용자 에이전트, 터치)에서 내려받기
 const ctx=await browser.newContext({viewport:{width:1180,height:820},hasTouch:true,userAgent:'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1',acceptDownloads:true});
 const page=await ctx.newPage();
 await page.addInitScript(()=>{localStorage.setItem('omr_sess_v1',JSON.stringify({access_token:'test',user:{id:'test'}}));const fetch=window.fetch.bind(window);window.fetch=(input,init)=>String(typeof input==='string'?input:input.url).includes('supabase.co')?Promise.resolve(new Response('[]',{status:200,headers:{'Content-Type':'application/json'}})):fetch(input,init)});
 await page.goto(process.env.BASE+'/index.html?app=1');await page.waitForFunction(()=>typeof bkLoad==='function'&&Object.keys(BIDX).length&&teacher());
 assert.equal(await page.evaluate(()=>isMob()),true,'tablet layout expected');
 const pp=page.waitForEvent('popup');
 await page.evaluate(async()=>{await setSubject('me');const mc=DATA.filter(q=>q.set==='mc'),qs=[...mc.filter(q=>q.q.includes('<table')).slice(0,2),...mc.filter(q=>!q.q.includes('<table')).slice(0,8)].map(q=>q.code);const r=mkWs(qs,{...wsOpts(),ans:1,cols:2});r.title='배치 검증 학습지';r.cover={...(r.cover||{}),org:'검증 학원'};await openWs(r)});
 const pop=await pp;await pop.waitForSelector('#hwpx-download');
 const htmlPages=await pop.evaluate(()=>(document.getElementById('paper')||document.getElementById('wsPaper')).shadowRoot.querySelectorAll('.pg').length);
 await pop.click('#hwpx-download');await pop.waitForSelector('.solvi-hwpx[open]');const dp=pop.waitForEvent('download',{timeout:60000});await pop.locator('.solvi-hwpx button[type=submit]').click();
 const f=unzip(require('node:fs').readFileSync(await (await dp).path()));
 const secs=Object.keys(f).filter(k=>/^Contents\/section\d+\.xml$/.test(k));
 assert.ok(htmlPages>2,'fixture should span several HTML pages');
 assert.equal(secs.length,1,'worksheet pages flow in one section instead of one section per HTML page');
 const sec=f['Contents/section0.xml'].toString(),head=f['Contents/header.xml'].toString(),text=paras(sec);
 assert.match(sec,/<hp:colPr [^>]*colCount="2"/,'native two-column layout');
 assert.match(sec,/<hp:pageNum /,'page number control');
 assert.match(sec,/<hp:header [\s\S]*배치 검증 학습지[\s\S]*<\/hp:header>/,'running header moved into a Hancom header');
 assert.match(sec,/hideFirstHeader="1"/,'first page keeps its own title block');
 assert.ok(!text.some(t=>/^\s*\d+\s*\/\s*\d+\s*$/.test(t)||/배치 검증 학습지\s*\d+\s*\/\s*\d+/.test(t)),'HTML page footer is not body text');
 assert.equal((sec.match(/<hp:t>배치 검증 학습지<\/hp:t>/g)||[]).length<=2,true,'title not repeated per HTML page');
 assert.ok(text.some(t=>t.includes('이름')&&t.includes('날짜')&&t.includes('점수')),'info row is one paragraph');
 assert.ok(text.some(t=>/^1\.\s*(\S|$)/.test(t)&&/점\]/.test(t)),'question number keeps its "." and sits with the points');
 assert.ok(!paras(sec.replace(/<hp:tbl [\s\S]*?<\/hp:tbl>/g,'')).some(t=>/^\d+\.?$/.test(t.trim())),'no bare question number paragraphs');
 assert.match(head,/<hc:winBrush faceColor="#(?!ffffff)[0-9a-f]{6}"/,'table header background kept');
 assert.match(sec,/<hp:p id="\d+" paraPrIDRef="\d+" styleIDRef="0" pageBreak="1"/,'answers start on a new page');
 assert.match(head,/keepWithNext="1"/,'questions kept together');
 assert.match(head,/autoTabRight="1"/,'right tab for number/points rows');
 const white=[...head.matchAll(/<hh:charPr id="(\d+)"[^>]*textColor="#ffffff"/g)].map(m=>m[1]);
 const outside=sec.replace(/<hp:tc [\s\S]*?<\/hp:tc>/g,'');for(const id of white)assert.ok(!outside.includes('charPrIDRef="'+id+'"'),'no white text outside filled table cells');
 console.log('PASS tablet worksheet HWPX: one flowing 2-column section ('+htmlPages+' HTML pages), Hancom header/page number, joined rows, cell fills, readable badges');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
