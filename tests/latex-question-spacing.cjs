/* Measure shipped PDF baselines through XeTeX's delayed save-position writes. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { chromium, browserOptions } = require('./runtime.cjs');
(async () => {
  const browser = await chromium.launch(browserOptions());
  try {
    const page = await browser.newPage();
    await page.route(/supabase\.co/, r => r.fulfill({ json: [] }));
    await page.addInitScript(() => localStorage.setItem('omr_sess_v1', JSON.stringify({ access_token: 'test', user: { id: 'test' } })));
    await page.goto(process.env.BASE + '/index.html?app=1');
    await page.waitForFunction(() => typeof bkLoad === 'function' && Object.keys(BIDX).length && teacher());
    const result = await page.evaluate(async () => {
      await bkLoad(); await ltLoad(); await setSubject('aim');
      const assets = {}, root = document.createElement('div');
      root.innerHTML = byCode['AM-001'].q;
      const vertical = await SolviPrint.ast(root.firstElementChild, assets);
      const unit = (code, number, children) => ({ tag: 'unit', keep: true, code, number, type: number === 1 ? '인공지능의 개념' : '감정 분석', children });
      const model = { title: '문항 내부 간격 검증', subject: '인공지능 수학', subjectId: 'aim', publicBase: 'https://solvi.p-e.kr/', material: 'worksheet', per: 4, fontSize: 8.5, assets,
        pages: [{ kind: 'questions', codes: ['AM-001', 'Space-002'], columns: [[
          unit('AM-001', 1, [vertical]),
          unit('Space-002', 2, [{ tag: 'question', children: [{ tag: 'p', text: '감정 점수의 값은?' }, { tag: 'choices-list', children: ['−1', '2', '3', '1', '0'].map(text => ({ tag: 'span', text })) }] }])
        ]] }] };
      const render = SolviLatexDocument.render, compile = XeTeXEngine.prototype.compileLaTeX;
      const marker = label => String.raw`\leavevmode\pdfsavepos\write16{SOLVISPACE:` + label + String.raw`:\the\pdflastypos}`;
      SolviLatexDocument.render = function (...args) {
        let source = render(...args);
        for (const [label, target] of [['number', String.raw`\selectfont 1.`], ['body', '분류기의 성능을 평가할 자료로 가장 적절한 것은?'], ['first', '학습 자료'], ['second', '중복 자료'], ['rowbody', '감정 점수의 값은?']]) {
          source = source.replace(target, label === 'number' ? String.raw`\selectfont ` + marker(label) + '1.' : marker(label) + target);
        }
        // The short-choice row is typeset inside a table, so put its marker in the first cell.
        source = source.replace(String.raw`\examoptsauto{−1}`, String.raw`\examoptsauto{` + marker('rowfirst') + '−1}');
        return source;
      };
      let log;
      XeTeXEngine.prototype.compileLaTeX = async function () { const r = await compile.call(this); log = r.log; return r; };
      try { const r = await SolviPrint.submit(model); return { log, bytes: [...new Uint8Array(await r.blob.arrayBuffer())] }; }
      catch(e) { throw Error(e.message + '\n' + log?.slice(-2400)); }
      finally { SolviLatexDocument.render = render; XeTeXEngine.prototype.compileLaTeX = compile; }
    });
    fs.writeFileSync('/tmp/solvi-question-spacing.pdf', Buffer.from(result.bytes));
    const positions = Object.fromEntries([...result.log.matchAll(/SOLVISPACE:([a-z]+):(\d+)/g)].map(m => [m[1], +m[2] / 65536 * 25.4 / 72.27]));
    for (const name of ['number', 'body', 'first', 'second', 'rowbody', 'rowfirst']) assert.ok(Number.isFinite(positions[name]), 'Missing baseline: ' + name);
    const gaps = { numberToBody: positions.number - positions.body, bodyToChoices: positions.body - positions.first, verticalRows: positions.first - positions.second, bodyToFiveChoices: positions.rowbody - positions.rowfirst };
    console.log('Measured baseline gaps (mm):', gaps);
    assert.ok(gaps.numberToBody > 5 && gaps.numberToBody < 9, 'Number/body gap should match the compact reference');
    assert.ok(gaps.bodyToChoices > 4 && gaps.bodyToChoices < 8.5, 'Body/vertical choices gap is too wide');
    assert.ok(gaps.verticalRows > 4 && gaps.verticalRows < 6.5, 'Vertical choice rows are too wide');
    assert.ok(gaps.bodyToFiveChoices > 4 && gaps.bodyToFiveChoices < 8.5, 'Body/five-choice row gap is too wide');
    console.log('PASS compact number/body/choice spacing in an actual PDF');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
