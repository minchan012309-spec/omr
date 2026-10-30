/* 인트로 스크롤 회귀: 휠 · 키보드 · 스크롤바 · 터치가 브라우저 기본 스크롤 그대로인지(장면 단위로 튀지 않는지) 실제 브라우저에서 잰다.
   Run with BASE=http://127.0.0.1:8765 node tests/intro-scroll.cjs (BASE 가 없으면 file:// 로 연다) */
const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium, browserOptions } = require("./runtime.cjs");
const URL = process.env.BASE ? process.env.BASE + "/intro.html" : "file://" + path.resolve(__dirname, "../intro.html");
const FILE = "file://" + path.resolve(__dirname, "../intro.html");
const settle = (page, ms = 700) => page.waitForTimeout(ms);
const y = (page) => page.evaluate(() => scrollY);
const at = async (page, top) => {
  await page.evaluate((t) => scrollTo(0, t), top);
  await settle(page, 300);
  return y(page);
};
const secTop = (page, id) => page.evaluate((id) => document.getElementById(id).getBoundingClientRect().top + scrollY, id);
const openIntro = async (browser, opts, url = URL) => {
  const context = await browser.newContext({ serviceWorkers: "block", ...opts });
  await context.route("**/rest/v1/**", (r) => r.abort());
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(url);
  await settle(page, 2800);
  return { context, page, errors };
};
/* 휠 한 번: 이동량이 입력과 비슷하고, 멈춘 뒤 위치가 다시 바뀌지 않는다(장면 정렬 · 되돌림 없음) */
const wheel = async (page, dy) => {
  const before = await y(page);
  await page.mouse.wheel(0, dy);
  await settle(page, 450);
  const after = await y(page);
  await settle(page, 600);
  assert.equal(await y(page), after, "no corrective scroll after the wheel stops (" + dy + ")");
  return after - before;
};

(async () => {
  const browser = await chromium.launch(browserOptions());
  try {
    for (const [width, height] of [[1440, 900], [768, 1024], [390, 844]]) {
      const { context, page, errors } = await openIntro(browser, { viewport: { width, height } });
      const tag = width + "px";
      /* 스크롤을 잡는 장치가 없다 */
      const css = await page.evaluate(() => {
        const h = getComputedStyle(document.documentElement), b = getComputedStyle(document.body);
        return { snap: h.scrollSnapType + "|" + b.scrollSnapType, behavior: h.scrollBehavior, ho: h.overflowY, bo: b.overflowY, ta: h.touchAction + "|" + b.touchAction };
      });
      assert.equal(css.snap, "none|none", tag + " no scroll snap");
      assert.equal(css.behavior, "auto", tag + " no forced smooth scrolling");
      assert.ok(!/hidden|clip/.test(css.ho + css.bo), tag + " page itself scrolls");
      assert.ok(!/none/.test(css.ta), tag + " touch scrolling not disabled");
      assert.equal(await page.evaluate(() => typeof window.ScrollTrigger), "undefined", tag + " no pinned ScrollTrigger film");
      await page.mouse.move(width / 2, height / 2);

      /* 1. 작은 휠: 입력만큼만, 화면 한 장보다 훨씬 적게. 글(문구)도 같은 만큼 올라간다 */
      const h1Before = await page.locator("#h1").evaluate((e) => e.getBoundingClientRect().top);
      const d1 = await wheel(page, 80);
      assert.ok(d1 > 0 && Math.abs(d1 - 80) <= 16, tag + " small wheel moves ~80px, got " + d1);
      assert.ok(d1 < height / 4, tag + " small wheel stays far below one screen");
      const h1After = await page.locator("#h1").evaluate((e) => e.getBoundingClientRect().top);
      assert.ok(Math.abs(h1Before - h1After - d1) <= 2, tag + " hero copy travels with the scroll 1:1");

      /* 장면 경계 바로 앞에서 작은 휠: 다음 장면 시작점으로 끌려가지 않는다 */
      for (const id of ["book", "device", "academy"]) {
        const top = await secTop(page, id);
        const start = await at(page, top - 40);
        const d = await wheel(page, 80);
        assert.ok(Math.abs(d - 80) <= 16, tag + " near #" + id + " wheel moved " + d);
        assert.ok(Math.abs(start + d - top) > 8, tag + " not aligned to #" + id + " start");
        /* 화면 아래에서 들어오는 다음 장면 문구는 스크롤한 만큼만 올라온다 */
        await at(page, top - height * 0.7);
        const cpTop = () => page.locator("#" + id + " .cp").evaluate((e) => e.getBoundingClientRect().top);
        const c0 = await cpTop();
        const dc = await wheel(page, 80);
        assert.ok(Math.abs(c0 - (await cpTop()) - dc) <= 2, tag + " #" + id + " copy enters 1:1 with the scroll");
      }

      /* 2. 연속된 작은 휠: 하나도 버려지지 않고 고르게 쌓인다 */
      const s2 = await at(page, (await secTop(page, "book")) + 200);
      const steps = [];
      for (let i = 0; i < 5; i++) steps.push(await wheel(page, 80));
      assert.ok(steps.every((d) => d > 50 && d < 110), tag + " every small wheel counts: " + steps.join(","));
      assert.ok(Math.abs((await y(page)) - s2 - 400) <= 40, tag + " 5×80 accumulates to ~400px");

      /* 3. 큰 휠: 입력에 비례해서 멀리 간다(장면 하나로 제한하지 않음) */
      const big = await wheel(page, 900);
      assert.ok(big > 700 && big < 1100, tag + " big wheel moves ~900px, got " + big);
      await at(page, (await secTop(page, "connect")) - 300);
      let far = 0;
      for (let i = 0; i < 6; i++) far += await wheel(page, 900);
      const passed = await page.evaluate(() => ["connect", "book", "device", "academy", "spec"].filter((id) => document.getElementById(id).getBoundingClientRect().top < 0).length);
      assert.ok(far > 4500 && passed >= 2, tag + " fast scrolling passes several sections (" + far + "px, " + passed + ")");

      /* 4. 역방향: 작은 음수 휠은 조금만 올라간다 */
      await at(page, (await secTop(page, "book")) + 120);
      const up = await wheel(page, -80);
      assert.ok(up < 0 && Math.abs(up + 80) <= 16, tag + " small reverse wheel moves ~-80px, got " + up);
      const up2 = await wheel(page, -80);
      assert.ok(Math.abs(up2 + 80) <= 16, tag + " reverse again ~-80px, got " + up2);

      /* 5. 스크롤바로 직접 옮긴 위치를 그대로 둔다 */
      const want = await page.evaluate(() => Math.round(document.body.scrollHeight * 0.45));
      await page.evaluate((t) => window.scrollTo(0, t), want);
      await settle(page, 1200);
      assert.equal(await y(page), want, tag + " direct scroll position is kept");

      /* 6. 키보드: 브라우저 기본 동작 그대로 */
      await page.evaluate(() => { document.activeElement && document.activeElement.blur(); });
      const key = async (k) => {
        const b = await y(page);
        await page.keyboard.press(k);
        await settle(page, 900);
        return (await y(page)) - b;
      };
      await at(page, (await secTop(page, "book")) + 100);
      const vh = height;
      const pd = await key("PageDown");
      assert.ok(pd > vh * 0.5 && pd <= vh, tag + " PageDown ≈ one screen, got " + pd);
      const pu = await key("PageUp");
      assert.ok(pu < -vh * 0.5 && pu >= -vh, tag + " PageUp ≈ one screen back, got " + pu);
      const sp = await key("Space");
      assert.ok(sp > vh * 0.5 && sp <= vh, tag + " Space ≈ one screen, got " + sp);
      const ssp = await key("Shift+Space");
      assert.ok(ssp < -vh * 0.5 && ssp >= -vh, tag + " Shift+Space ≈ one screen back, got " + ssp);
      const ad = await key("ArrowDown");
      assert.ok(ad > 0 && ad < 200, tag + " ArrowDown is a small step, got " + ad);
      const au = await key("ArrowUp");
      assert.ok(au < 0 && au > -200, tag + " ArrowUp is a small step, got " + au);
      await key("End");
      assert.ok(await page.evaluate(() => scrollY + innerHeight >= document.documentElement.scrollHeight - 2), tag + " End reaches the bottom");
      await key("Home");
      assert.equal(await y(page), 0, tag + " Home returns to the top");

      /* 섹션 중간에서 멈출 수 있고, 긴 문구도 끝까지 화면에 들어온다 */
      for (const id of ["book", "device", "academy", "eco", "start"]) {
        await at(page, (await secTop(page, id)) + 1);
        const r = await page.locator("#" + id + " .cp").evaluate((e) => { const b = e.getBoundingClientRect(); return { top: b.top, bottom: b.bottom }; });
        assert.ok(r.top >= 0 && r.bottom <= height + 1, tag + " #" + id + " copy fits on screen while its section is in view");
      }
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), tag + " no horizontal page overflow");
      assert.deepEqual(errors, [], tag + " no page errors");
      await context.close();
    }

    /* 7. 휴대폰 터치: 세로로 밀면 그만큼 움직이고, 가로 넘침이 없다 */
    {
      const { context, page, errors } = await openIntro(browser, { viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
      const cdp = await context.newCDPSession(page);
      /* 실제 터치 이벤트 열(시작 → 이동 여러 번 → 끝)을 보내고, 관성까지 멈출 때까지 기다린다 */
      const swipe = async (dy) => {
        const b = await y(page), x = 195, y0 = dy < 0 ? 640 : 240, steps = 12;
        await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y: y0 }] });
        for (let i = 1; i <= steps; i++) {
          await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x, y: y0 + (dy * i) / steps }] });
          await page.waitForTimeout(16);
        }
        await page.waitForTimeout(120);
        await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
        let last = -1, now = await y(page);
        for (let i = 0; i < 40 && now !== last; i++) { await page.waitForTimeout(150); last = now; now = await y(page); }
        return now - b;
      };
      const down = await swipe(-300);
      assert.ok(down > 200 && down < 700, "touch swipe up scrolls about the swipe distance, got " + down);
      const back = await swipe(200);
      assert.ok(back < -120 && back > -600, "touch swipe down scrolls back about the swipe distance, got " + back);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "no horizontal overflow on touch phone");
      assert.deepEqual(errors, []);
      await context.close();
    }

    /* 8. 동작 줄이기: 처음부터 내용이 보이고, 스크롤도 그대로 */
    {
      const { context, page, errors } = await openIntro(browser, { viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
      assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior), "auto");
      const hidden = await page.evaluate(() => [...document.querySelectorAll(".sc .cp")].filter((e) => getComputedStyle(e).visibility === "hidden" || +getComputedStyle(e).opacity < 0.99).length);
      assert.equal(hidden, 0, "every scene copy is visible without motion");
      await page.mouse.move(720, 450);
      const d = await wheel(page, 80);
      assert.ok(Math.abs(d - 80) <= 16, "reduced motion wheel ~80px, got " + d);
      await page.locator('.nav a[href="#flow"]').click();
      await settle(page, 200);
      assert.ok(await page.evaluate(() => Math.abs(document.getElementById("flow").getBoundingClientRect().top - parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop)) < 2), "anchor jumps instantly with reduced motion");
      assert.deepEqual(errors, []);
      await context.close();
    }

    /* file:// 로 바로 열어도 같은 원리로 움직인다 */
    {
      const { context, page, errors } = await openIntro(browser, { viewport: { width: 1440, height: 900 } }, FILE);
      assert.equal(await page.locator("#h1").isVisible(), true, "file:// page renders");
      await page.mouse.move(720, 450);
      const d = await wheel(page, 80);
      assert.ok(Math.abs(d - 80) <= 16, "file:// small wheel ~80px, got " + d);
      assert.deepEqual(errors, []);
      await context.close();
    }
    console.log("intro scroll: wheel · keys · scrollbar · touch · reduced motion · file:// passed");
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
