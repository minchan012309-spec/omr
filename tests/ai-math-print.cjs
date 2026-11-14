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
      const codes = ['AM-050','G-aim041-0506','G-aim131-0668','G-aim081-0001','G-aim132-0008','G-aim133-0010'];
      await ensureCodes([...codes,'G-aim021-0043','G-aim081-0001']);
      await bkLoad();
      const q = byCode['G-aim021-0043'];
      const legacyMarkup = {...q};
      const render = html => new DOMParser().parseFromString(html,'text/html');
      const dom = render(q.q);
      const qs = dom.querySelector('.qs');
      qs.after(qs.querySelector('.chs'));
      legacyMarkup.q = dom.body.innerHTML;
      for(const shape of [q,legacyMarkup]){
        if(render(bkQHtml(shape,1,{pt:2})).querySelectorAll('.chs > div').length!==5)throw new Error('교재 선지 누락');
      }
      const equation = render(byCode['G-aim081-0001'].exp).querySelector('.aim-equation math[display=block] mfrac');
      if(!equation)throw new Error('영상 변환식 MathML 누락');
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

      const fraction = root.querySelector('math.mfrac mfrac');
      const quick = root.querySelector('.pg .ws-quick');
      const badge = solutions[0].querySelector('.ws-answer');
      return {
        quick: quick.querySelector('h2').textContent,
        quickCount: quick.querySelectorAll('.ws-answer').length,
        columns: getComputedStyle(quick.querySelector('.key')).gridTemplateColumns.split(' ').length,
        answerLabel: badge.textContent,
        wide: quick.offsetWidth > solutions[0].offsetWidth * 1.7,
        border: Number.parseFloat(getComputedStyle(quick).borderTopWidth),
        answerColor: getComputedStyle(badge).color,
        answerBackground: getComputedStyle(badge).backgroundColor,
        titles: solutions.map(el=>el.firstElementChild.textContent),
        choices: solutions.map(el => el.querySelectorAll('.aim-choice').length),
        fractions: root.querySelectorAll('math mfrac').length,
        mathNamespace: fraction && fraction.namespaceURI,
        overflow: solutions.filter(el => {
          const col = el.closest('.col');
          return col && el.getBoundingClientRect().bottom > col.getBoundingClientRect().bottom + 2;
        }).length,
      };
    });
    assert.deepEqual(result.choices,[5,5,5,5,0,0],JSON.stringify(result));
    assert.equal(result.quick,'빠른 정답');
    assert.equal(result.quickCount,6);
    assert.equal(result.wide,true);
    assert.equal(result.columns,2);
    assert.equal(result.answerLabel,'정답: 3');
    assert.ok(result.border>=2);
    assert.equal(result.answerColor,'rgb(21, 56, 80)');
    assert.equal(result.answerBackground,'rgb(220, 234, 245)');
    assert.ok(result.fractions > 10);
    assert.equal(result.mathNamespace,'http://www.w3.org/1998/Math/MathML');
    assert.equal(result.overflow,0);
    if (process.env.AI_MATH_SHOTS) await popup.locator('#paper .pg').first().screenshot({path:process.env.AI_MATH_SHOTS+'/print-solution.png'});
    await popup.emulateMedia({media:'print'});
    const pdf = await popup.pdf({preferCSSPageSize:true});
    assert.ok((pdf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length>=1);
    console.log('PASS 인공지능 수학 인쇄 해설: ①~⑤ · 분수 · 열 높이');
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
