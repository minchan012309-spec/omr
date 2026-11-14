const assert = require('node:assert/strict');
const {chromium, browserOptions} = require('./runtime.cjs');

(async () => {
  const browser = await chromium.launch(browserOptions());
  try {
    for (const width of [1440, 820, 390]) {
      const page = await browser.newPage({viewport:{width, height:900}, serviceWorkers:'block'});
      await page.route(/supabase\.co/, route => route.fulfill({json:[]}));
      await page.addInitScript(() => localStorage.setItem('omr_sess_v1', JSON.stringify({access_token:'test-token',user:{id:'test'}})));
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto((process.env.BASE || 'http://127.0.0.1:8765')+'/index.html?app=1');
      await page.locator('#subj').click();
      await page.getByRole('button', {name:'정보', exact:true}).click({timeout:3000});
      for (const name of [/데이터과학.*준비 중/, /^정보.*준비 중/, /인공지능 기초.*준비 중/]) {
        assert.equal(await page.getByRole('button', {name}).isDisabled(), true);
      }
      assert.equal(await page.getByRole('button', {name:'정보', exact:true}).getAttribute('aria-pressed'), 'true');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      if (process.env.AI_MATH_SHOTS) await page.screenshot({path:process.env.AI_MATH_SHOTS+'/'+width+'.png'});
      await page.getByRole('button', {name:/^인공지능 수학/}).click();
      assert.equal(await page.locator('body').getAttribute('data-subj'), 'aim');
      await page.reload();
      await page.waitForFunction(() => document.body.dataset.subj === 'aim' && DATA.length >= 30);
      const result = await page.evaluate(async () => {
        await conceptLoad();
        await bkLoad();
        const plans = [await bkPlan('aim-c'), await bkPlan('aim-t')];
        const mc = DATA.filter(q => q.set === 'mc');
        return {
          mc: mc.length,
          advancedWithVisuals: mc.filter(q => ['상','최'].includes(q.lv) && q.q.includes('<figure')).length,
          figures: mc.filter(q => q.q.includes('<svg')).length,
          correct: mc.every(q => ok(q, q.ans) && /^[1-5]$/.test(q.ans) && (q.q.match(/<div><b>[①②③④⑤]<\/b>/g) || []).length === 5),
          planned: plans.every(plan => plan.pages.some(page => page.codes?.length)),
          sections: CONC.aim.secs.length,
          tagged: DATA.every(q => subjOf(q.code) === 'aim') && subjOf(shufCode('AM-035', '1602')) === 'aim',
          book: !!bkParts('aim-c'),
        };
      });
      assert.deepEqual(result, {mc:60, advancedWithVisuals:30, figures:5, correct:true, planned:true, sections:15, tagged:true, book:true});
      if (width < 720) await page.getByRole('button', {name:'메뉴 열기', exact:true}).click();
      await page.locator('#nav').getByRole('button', {name:'개념학습', exact:true}).click();
      await page.getByRole('heading', {name:/인공지능의 개념/}).waitFor();
      await page.getByRole('heading', {name:'풀이 예제'}).waitFor();
      if (process.env.AI_MATH_SHOTS) await page.screenshot({path:process.env.AI_MATH_SHOTS+'/lesson-'+width+'.png', animations:'disabled'});
      await page.getByRole('button', {name:'다음 연습'}).click();
      await page.getByText('추가 연습 2 / 24쪽', {exact:true}).waitFor();
      const blank = page.locator('#cbb_G-aim013-0007');
      await blank.locator('input').fill(await page.evaluate(() => byCode['G-aim013-0007'].ans));
      await blank.getByRole('button', {name:'확인', exact:true}).click();
      await blank.locator('input.okb').waitFor();
      if (process.env.AI_MATH_SHOTS) await page.screenshot({path:process.env.AI_MATH_SHOTS+'/concept-'+width+'.png'});
      if (width === 1440) {
        await page.locator('#nav').getByRole('button', {name:'문항 검색', exact:true}).click();
        await page.locator('#sq').fill('G-aim151-0668');
        await page.locator('#sr .res .top').filter({hasText:'G-aim151-0668'}).first().waitFor();
      }

      if (width === 1440) {
        const bank = await page.evaluate(async () => {
          const label = '인공지능의 개념';
          const typeKey = 'Ⅰ|' + label;
          const counts = {};
          for (const kind of ['mc', 'ox', 'blank']) {
            W.sets = {[kind]:1};
            W.sel = new Map([[typeKey, 8]]);
            W.mode = 'per';
            const before = typeRows().find(t => t.k === typeKey).pool;
            const codes = await pickCodes();
            const after = typeRows().find(t => t.k === typeKey).pool;
            counts[kind] = [before, after, codes.length, codes.every(c => byCode[c].set === kind), codes.some(c => c.startsWith('G-aim'))];
          }
          return counts;
        });
        assert.deepEqual(bank, {
          mc:[676,676,8,true,true], ox:[145,145,8,true,true], blank:[144,144,8,true,true],
        });
      }
      await page.evaluate(() => practice(['AM-035'], '인공지능 수학'));
      await page.locator('#main svg[role="img"]').first().waitFor();
      await page.locator('#busy.on').waitFor({state:'hidden'});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      if (process.env.AI_MATH_SHOTS) await page.screenshot({path:process.env.AI_MATH_SHOTS+'/question-'+width+'.png'});
      await page.locator('#main .chs2').getByRole('button', {name:'5', exact:true}).click();
      await page.getByText('정답입니다', {exact:true}).waitFor();
      assert.deepEqual(errors, []);
      await page.close();
    }
    console.log('PASS 정보 탭 · 과목 복원 · 문제 및 개념 자료 · 교재 ID (1440 · 820 · 390)');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
