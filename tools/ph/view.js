// 생성한 문항을 앱의 문제 렌더러로 그려서 PNG 로 저장한다.
//   node tools/ph/view.js <json파일> <시작> <개수> <출력.png> [exp]
// 사전 조건: 저장소 루트에서 `python3 -m http.server 8765` 가 실행 중이어야 한다(앱 CSS 를 쓰려고 index.html 을 연다).
const {chromium}=require(process.env.PW||'/opt/node-tools/node_modules/playwright');const fs=require('fs');
(async()=>{const [file,from,count,out,showExp]=process.argv.slice(2);
 const data=JSON.parse(fs.readFileSync(file,'utf8')).slice(+from,+from+ +count);
 const b=await chromium.launch();const pg=await (await b.newContext({viewport:{width:1000,height:900},deviceScaleFactor:1.2})).newPage();
 pg.on('pageerror',e=>console.log('PAGEERR',String(e)));
 await pg.goto('http://localhost:8765/index.html');await pg.waitForTimeout(1500);
 await pg.evaluate("sessionStorage.setItem('omr_domnt','1')");
 await pg.evaluate(({sel,showExp})=>{
  document.body.innerHTML='<div id="vv" style="padding:12px;background:#fff;max-width:900px;display:grid;grid-template-columns:1fr 1fr;gap:10px"></div>';
  const v=document.getElementById('vv');
  for(const q of sel){const c=document.createElement('div');c.style.cssText='border:1px solid #ccd;padding:8px;border-radius:8px';const h=document.createElement('div');c.appendChild(h);const e=document.createElement('div');c.appendChild(e);v.appendChild(c);mount(h,q.q);if(showExp)mount(e,q.exp);const t=document.createElement('div');t.style.cssText='font:11px monospace;color:#888';t.textContent=q.code+' '+q.lv+' ans'+q.ans+' '+q.fam;c.appendChild(t)}
 },{sel:data,showExp:!!showExp});
 await pg.waitForTimeout(700);
 await pg.screenshot({path:out,fullPage:true});await b.close()})()
