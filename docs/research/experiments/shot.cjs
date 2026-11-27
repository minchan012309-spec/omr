const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({deviceScaleFactor:2});
for(const t of JSON.parse(fs.readFileSync(process.argv[2]+'/list.json'))){await p.goto('file://'+process.cwd()+'/'+process.argv[2]+'/'+t+'.html');await p.evaluate(()=>document.fonts.ready);await (await p.$('svg')).screenshot({path:process.argv[2]+'/'+t+'.png'})}
await b.close()})();
