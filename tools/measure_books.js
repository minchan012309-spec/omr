// 교재 쪽 나눔용 문항 높이표를 만든다.  node tools/measure_books.js  (python3 server.py 가 8765에서 실행 중이어야 함)
const {chromium}=require(process.env.PW||'/opt/node-tools/node_modules/playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1300,height:950}});
 pg.on('pageerror',e=>console.log('PAGEERR',String(e)));
 await pg.goto('http://localhost:8765/index.html');await pg.waitForTimeout(2000);
 await pg.evaluate("sess={access_token:'x',user:{}};STU=[{id:'s1',name:'테스트',grade:'고2'}];CUR_S='s1'");
 const out={};
 for(const s of ['me','cm']){await pg.evaluate(`setSubject('${s}')`);await pg.waitForTimeout(600);
  await pg.evaluate("bkLoad()");await pg.waitForTimeout(300);await pg.evaluate("conceptLoad()");
  await pg.evaluate("BKHT=null;BKREADY=null");
  const r=await pg.evaluate("(async()=>{await bkInit();BKHT={};const o=await bkMeasureAll();return o})()");Object.assign(out,r);console.log(s,Object.keys(r).length)}
 fs.mkdirSync('books',{recursive:true});fs.writeFileSync('books/heights.json',JSON.stringify(out));console.log('saved',Object.keys(out).length);
 await b.close()})()
