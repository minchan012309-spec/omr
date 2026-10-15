// 교재를 단독 HTML 파일로 내보낸다.  node tools/export_books.js [출력폴더]  (python3 server.py 실행 중이어야 함)
const {chromium}=require(process.env.PW||'/opt/node-tools/node_modules/playwright');const fs=require('fs');
const OUT=process.argv[2]||'textbooks';const SITE='https://solvi.p-e.kr/';
const NAMES={'me-c':'물질과에너지_개념서','me-t':'물질과에너지_유형서','cm-c':'세포와물질대사_개념서','cm-t':'세포와물질대사_유형서','ph-c':'역학과에너지_개념서','ph-t':'역학과에너지_유형서'};
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1000,height:900}});
 pg.on('pageerror',e=>console.log('PAGEERR',String(e)));
 await pg.goto('http://localhost:8765/index.html');await pg.waitForTimeout(1500);
 await pg.evaluate("sess={access_token:'x',user:{}};STU=[{id:'s1',name:'t',grade:'x'}];CUR_S='s1'");
 fs.mkdirSync(OUT,{recursive:true});
 for(const id of Object.keys(NAMES)){const s=id.split('-')[0];await pg.evaluate(`setSubject('${s}')`);await pg.waitForTimeout(500);await pg.evaluate("bkLoad()");await pg.waitForTimeout(300);
  let html=await pg.evaluate(`(async()=>{window.BKBASE='${SITE}';await conceptLoad();await bkInit();const p=await bkPlan('${id}');let h=bkStandalone(p);
   const urls=[...new Set([...h.matchAll(/<img[^>]+src="([^"#]+)"/g)].map(m=>m[1]))].filter(u=>!u.startsWith('data:'));
   const map={};for(const u of urls){try{const r=await fetch(u);const bl=await r.blob();map[u]=await new Promise(res=>{const f=new FileReader();f.onload=()=>res(f.result);f.readAsDataURL(bl)})}catch(e){}}
   h=h.replace(/(<img[^>]+src=")([^"#]+)(")/g,(m,a,u,c)=>a+(map[u]||u)+c);return h})()`);
  fs.writeFileSync(`${OUT}/${NAMES[id]}.html`,html);console.log(id,(html.length/1e6).toFixed(1)+'MB')}
 await b.close()})()
