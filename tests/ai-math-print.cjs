const assert = require('node:assert/strict');
const {chromium, browserOptions} = require('./runtime.cjs');

(async () => {
  const browser = await chromium.launch(browserOptions());
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1050},serviceWorkers:'block'});
    await page.addInitScript(() => localStorage.setItem('omr_subj_v1','aim'));
    await page.goto((process.env.BASE || 'http://127.0.0.1:8765')+'/index.html?app=1');
    await page.waitForFunction(() => typeof BIDX !== 'undefined' && !!BIDX.aim131);
    const fractionChoices = await page.evaluate(async () => {
      await ensureCodes(['AM-043']);
      await bkLoad();
      const question = byCode['AM-043'];
      const book = new DOMParser().parseFromString(bkQHtml(question, 1, {}), 'text/html');
      const preview = document.createElement('div');
      document.body.append(preview);
      await openWs({id:'12345678',t:Date.now(),title:'잔차',style:'w-simple',cols:2,part:'q',
        per:'auto',codes:[question.code],cover:{},tags:{}},preview);
      const choices = preview.shadowRoot.querySelector('.chs');
      const option = choices.children[1];
      const formula = option.querySelector('math');
      const result = {
        bookLayout: book.querySelector('.chs').classList.contains('md'),
        printColumns: getComputedStyle(choices).gridTemplateColumns.split(' ').length,
        tuple: formula?.textContent,
        fractions: option.querySelectorAll('mfrac').length,
        fits: formula && formula.getBoundingClientRect().right <= option.getBoundingClientRect().right,
      };
      return result;
    });
    assert.deepEqual(fractionChoices,{bookLayout:true,printColumns:2,tuple:'(−23,23)',fractions:2,fits:true});
    if (process.env.AI_MATH_SHOTS) {
      await page.locator('.wq:has(.chs)').first()
        .screenshot({path:process.env.AI_MATH_SHOTS+'/print-fraction-choices.png'});
    }
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
      codes.push(...Array(34).fill('AM-050'));
      await openWs({
        id:'12345678',t:Date.now(),title:'인공지능 수학 정답과 해설',style:'w-simple',color:'teal',p100:1,
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
        quick: quick.querySelector('h2').firstChild.textContent,
        total: quick.querySelector('h2 small').textContent,
        quickCount: quick.querySelectorAll('.key>span').length,
        columns: getComputedStyle(quick.querySelector('.key')).gridTemplateColumns.split(' ').length,
        answerLabel: badge.textContent,
        inLeftColumn: quick.parentElement === quick.closest('.pg').querySelector('.col'),
        rowCounts: [...quick.querySelectorAll('.key>span')].reduce((rows,cell)=>{
          const top=cell.offsetTop;rows[top]=(rows[top]||0)+1;return rows;
        },{}),
        firstAnswer: quick.querySelector('.key>span>b').textContent,
        border: Number.parseFloat(getComputedStyle(quick.querySelector('.key')).borderTopWidth),
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
    assert.deepEqual(result.choices,[5,5,5,5,0,0,...Array(34).fill(5)],JSON.stringify(result));
    assert.equal(result.quick,'정답표');
    assert.equal(result.total,'40문항 · 100점');
    assert.equal(result.quickCount,40);
    assert.equal(result.inLeftColumn,true);
    assert.deepEqual(Object.values(result.rowCounts),Array(8).fill(5));
    assert.equal(result.firstAnswer,'③');
    assert.equal(result.columns,5);
    assert.equal(result.answerLabel,'정답: 3');
    assert.ok(result.border>0);
    assert.equal(result.answerColor,'rgb(21, 56, 80)');
    assert.equal(result.answerBackground,'rgb(220, 234, 245)');
    assert.ok(result.fractions > 10);
    assert.equal(result.mathNamespace,'http://www.w3.org/1998/Math/MathML');
    assert.equal(result.overflow,0);
    if (process.env.AI_MATH_SHOTS) await popup.locator('#paper .pg').first().screenshot({path:process.env.AI_MATH_SHOTS+'/print-solution.png'});
    await popup.emulateMedia({media:'print'});
    const pdf = await popup.pdf({preferCSSPageSize:true});
    assert.ok((pdf.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length>=1);
    await popup.close();
    const lessonReady = page.waitForEvent('popup');
    await page.evaluate(async () => {
      await conceptLoad();
      CB.print = new Set(CONC.aim.secs.map(section => section.id));
      cbPrint();
    });
    const lesson = await lessonReady;
    await lesson.locator('.cpg').first().waitFor();
    const printed = await lesson.evaluate(() => {
      const pages = [...document.querySelectorAll('.cpg')];
      return {
        headings: pages.flatMap(p => [...p.querySelectorAll('h2.sc')]).map(h => h.textContent),
        formulae: document.querySelectorAll('.aim-concept-formula math').length,
        clipping: pages.flatMap(p => {
          const bottom = p.querySelector('.cpf').getBoundingClientRect().top;
          return [...p.querySelectorAll('.cin > *')].filter(e => e.getBoundingClientRect().bottom > bottom)
            .map(e => e.textContent);
        }),
      };
    });
    assert.equal(printed.headings.length,16);
    assert.ok(printed.formulae >= 50);
    assert.deepEqual(printed.clipping, []);
    if (process.env.AI_MATH_SHOTS) {
      await lesson.locator('.cpg').filter({hasText:'자카드 유사도와 거리'}).first()
        .screenshot({path:process.env.AI_MATH_SHOTS+'/print-concept.png'});
    }
    await lesson.emulateMedia({media:'print'});
    const lessonPdf = await lesson.pdf({preferCSSPageSize:true});
    assert.ok(lessonPdf.length > 10000);
    console.log('PASS 인공지능 수학 선지·답지 및 개념 15개 절 A4 인쇄');
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
