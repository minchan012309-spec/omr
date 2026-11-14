const assert = require('node:assert/strict');
const {chromium, browserOptions} = require('./runtime.cjs');

(async () => {
  const browser = await chromium.launch(browserOptions());
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1050},serviceWorkers:'block'});
    await page.addInitScript(() => localStorage.setItem('omr_subj_v1','aim'));
    await page.goto((process.env.BASE || 'http://127.0.0.1:8765')+'/index.html?app=1');
    await page.waitForFunction(() => typeof BIDX !== 'undefined' && !!BIDX.aim131);
    const popupReady = page.waitForEvent('popup');
    await page.evaluate(async () => {
      const codes = ['AM-050','G-aim041-0506','G-aim131-0668','G-aim132-0008','G-aim133-0010'];
      await ensureCodes(codes);
      await openWs({
        id:'12345678',t:Date.now(),title:'인공지능 수학 정답과 해설',style:'w-simple',
        cols:2,per:'auto',ans:1,part:'a',codes,cover:{},tags:{},
      });
    });
    const popup = await popupReady;
    await popup.locator('.sb.wq').last().waitFor();
    const result = await popup.evaluate(() => {
      const root = document.querySelector('#paper').shadowRoot;
      const solutions = [...root.querySelectorAll('.sb.wq')];

      const fraction = root.querySelector('.mfrac');
      return {
        titles: solutions.map(el=>el.firstElementChild.textContent),
        choices: solutions.map(el => el.querySelectorAll('.aim-choice').length),
        fractions: root.querySelectorAll('.mfrac[role="math"]').length,
        fractionGrid: fraction && getComputedStyle(fraction).display,
        overflow: solutions.filter(el => {
          const col = el.closest('.col');
          return col && el.getBoundingClientRect().bottom > col.getBoundingClientRect().bottom + 2;
        }).length,
      };
    });
    assert.deepEqual(result.choices,[5,5,5,0,0],JSON.stringify(result));
    assert.ok(result.fractions > 10);
    assert.equal(result.fractionGrid,'inline-grid');
    assert.equal(result.overflow,0);
    if (process.env.AI_MATH_SHOTS) await popup.locator('#paper .pg').first().screenshot({path:process.env.AI_MATH_SHOTS+'/print-solution.png'});
    await popup.emulateMedia({media:'print'});
    const pdf = await popup.pdf({preferCSSPageSize:true});
    assert.ok((pdf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length>=2);
    console.log('PASS 인공지능 수학 인쇄 해설: ①~⑤ · 분수 · 열 높이');
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
