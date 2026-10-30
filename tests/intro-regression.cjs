/* Browser regressions for the cinematic intro. Run with BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs */
const assert = require("node:assert/strict");
const { chromium, browserOptions } = require("./runtime.cjs");
const fs = require("node:fs");
const BASE = process.env.BASE || "http://127.0.0.1:8765";
const OUT = process.env.INTRO_SHOTS || "/tmp/solvi-intro-verification";
fs.mkdirSync(OUT, { recursive: true });
const PRICING = {
  plans: [
    { name: "테스트 라이트", price: "50000", unit: "/ 월", items: ["교재 인쇄"], cta: "시작하기" },
    { name: "테스트 플러스", price: "150000", unit: "/ 월", items: ["OMR 채점"], cta: "시작하기" },
    { name: "테스트 플래티넘", price: "300000", unit: "/ 월", items: ["학원 운영"], cta: "문의하기", hl: true },
  ],
  contact: "https://example.com/solvi-contact",
  note: "테스트 요금 안내",
};
/* 필름 타임라인의 시간 t(0–2320)로 스크롤하고, 스크럽이 따라올 때까지 기다린다 */
const seek = async (page, t) => {
  await page.evaluate((t) => {
    scrollTo(0, window.__intro.yAt(t));
  }, t);
  await page.waitForTimeout(1400);
};
const prop = (page, sel, p) => page.evaluate(([sel, p]) => gsap.getProperty(document.querySelector(sel), p), [sel, p]);
(async () => {
  const browser = await chromium.launch(browserOptions());
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, serviceWorkers: "block", colorScheme: "dark" });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    let requests = 0;
    await context.route("**/rest/v1/site_config?**", (route) => {
      requests++;
      return route.fulfill({ json: [{ value: PRICING }] });
    });
    await page.goto(BASE + "/intro.html");
    await page.locator("#plans h3").first().filter({ hasText: "테스트 라이트" }).waitFor();
    assert.equal(requests, 1, "existing pricing endpoint is still called");
    assert.equal(await page.locator("#prNote").innerText(), "테스트 요금 안내");
    assert.equal(await page.locator("#plans .plan").last().locator("a").getAttribute("href"), "https://example.com/solvi-contact");
    assert.equal(await page.locator("#plans .plan").count(), 3);
    await page.locator('.need button[data-lv="2"]').first().click();
    assert.match(await page.locator("#needO").innerText(), /테스트 플래티넘/);
    assert.equal(await page.locator(".plan.hit").count(), 1);
    await page.evaluate(() => scrollTo(0, 0));

    /* 시네마틱 모드: 장면은 문서 흐름, 무대만 sticky. 고정(pin) · 스크럽 지연 없음(스크롤 테스트는 intro-scroll.cjs) */
    assert.ok(await page.evaluate(() => document.documentElement.classList.contains("cine")), "cinematic mode on desktop");
    assert.equal(await page.evaluate(() => typeof window.ScrollTrigger), "undefined", "no ScrollTrigger pin/scrub");
    assert.equal(await page.locator("#stage").evaluate((e) => getComputedStyle(e).position), "sticky", "stage sticks while scenes scroll");
    assert.ok(await page.evaluate(() => document.documentElement.scrollHeight > innerHeight * 15), "long continuous scroll");
    assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).scrollSnapType), "none", "no forced scroll");
    await page.waitForTimeout(2600);
    await page.screenshot({ path: OUT + "/desktop-hero.png" });
    const s0 = await prop(page, "#xdr", "scale");
    assert.equal(await page.locator("#h1").isVisible(), true);

    /* 디바이스 화면이 프레임 안에 정확히 들어간다 */
    const fit = await page.evaluate(() => {
      const inside = (a, b) => a.left >= b.left - 1 && a.top >= b.top - 1 && a.right <= b.right + 1 && a.bottom <= b.bottom + 1;
      const r = (s) => document.querySelector(s).getBoundingClientRect();
      return inside(r("#xdr .scr"), r("#xdr .f-front"));
    });
    assert.ok(fit, "display UI stays inside the bezel");

    /* 장면별 상태 */
    await seek(page, 180);
    assert.ok((await prop(page, "#xdr", "x")) > 0, "display steps aside to the right of the scene 2 copy");
    assert.ok(+(await page.locator(".sc-ops .cp").evaluate((e) => getComputedStyle(e).opacity)) > 0.9, "scene 2 copy");
    await page.screenshot({ path: OUT + "/desktop-ops.png" });
    await seek(page, 380);
    assert.ok(+(await page.locator(".qt").first().evaluate((e) => getComputedStyle(e).opacity)) < 0.5, "unit filter dims other questions");
    assert.equal(await page.locator(".qt").nth(2).evaluate((e) => getComputedStyle(e).opacity), "1", "selected question stays");
    await page.screenshot({ path: OUT + "/desktop-bank.png" });
    await seek(page, 705);
    const leaf = await page.evaluate(() => [...document.querySelectorAll(".leaf")].map((l) => l.style.transform));
    assert.match(leaf[2], /rotateY\(-180/, "cover opened");
    assert.match(leaf[1], /rotateY\(-[1-9]/, "inner page is turning");
    assert.ok(await page.evaluate(() => [...document.querySelectorAll(".leaf")][1].querySelectorAll(".st")[5].style.transform.includes("rotateY")), "page bends while turning");
    await page.screenshot({ path: OUT + "/desktop-book.png" });
    await seek(page, 1145);
    assert.ok((await prop(page, "#lid", "rotationX")) > 0, "laptop lid opens");
    assert.equal(await page.locator("#pad").evaluate((e) => getComputedStyle(e).visibility), "visible");
    await page.screenshot({ path: OUT + "/desktop-devices.png" });
    await seek(page, 1350);
    assert.equal(await page.locator(".score dd").last().innerText(), "75%", "OMR result counts up to the real result");
    await page.screenshot({ path: OUT + "/desktop-omr.png" });
    await seek(page, 1580);
    const slots = await page.evaluate(() => [...document.querySelectorAll(".chip")].map((c, i) => {
      const a = c.getBoundingClientRect(), b = document.querySelectorAll(".slots i")[i].getBoundingClientRect();
      return Math.abs(a.left + a.width / 2 - b.left - b.width / 2) + Math.abs(a.top + a.height / 2 - b.top - b.height / 2);
    }));
    assert.ok(slots.every((d) => d < 6), "wrong answers land in their type group");
    await page.screenshot({ path: OUT + "/desktop-wrong.png" });
    await seek(page, 1820);
    await page.screenshot({ path: OUT + "/desktop-academy.png" });
    await seek(page, 2080);
    await page.screenshot({ path: OUT + "/desktop-eco.png" });
    await seek(page, 2310);
    assert.ok(await page.locator(".hd").evaluate((e) => e.classList.contains("light")), "header turns light on the final scene");
    assert.equal(await page.locator("#h-end").isVisible(), true);
    await page.screenshot({ path: OUT + "/desktop-end.png" });

    /* 거꾸로 스크롤하면 처음 장면으로 되돌아온다 */
    await seek(page, 705);
    await seek(page, 0);
    assert.ok(Math.abs((await prop(page, "#xdr", "scale")) - s0) < 0.01, "reverse scroll restores the hero display");
    assert.equal(await page.evaluate(() => [...document.querySelectorAll(".leaf")].every((l) => !/rotateY\(-[1-9]/.test(l.style.transform))), true, "pages close again when scrolling back");
    assert.ok(+(await page.locator(".sc-hero .cp").evaluate((e) => getComputedStyle(e).opacity)) > 0.9);

    /* 이동 경로 */
    assert.ok((await page.locator('a[data-app][href="index.html?app=1#login"]').count()) > 0);
    assert.ok((await page.locator('a[data-app][href="index.html?app=1#student"]').count()) > 0);
    await page.locator('a[data-app][href="index.html?app=1#student"]').first().evaluate((e) => {
      e.addEventListener("click", (ev) => ev.preventDefault(), { once: true });
      e.click();
    });
    assert.equal(await page.evaluate(() => localStorage.getItem("omr_app")), "1");
    await page.locator('.nav a[href="#bank"]').click();
    await page.waitForTimeout(600);
    assert.ok(await page.evaluate(() => Math.abs(document.getElementById("bank").getBoundingClientRect().top - parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop)) < 2), "nav is a plain anchor to the question bank section");
    assert.equal(await page.locator('.nav a[href="#bank"]').getAttribute("aria-current"), "true", "nav marks the section in view");
    const assets = await page.evaluate(() => [...new Set([...document.querySelectorAll("img")].map((i) => i.getAttribute("src") || i.dataset.src).concat([...document.querySelectorAll(".leaf")].flatMap((l) => [l.dataset.f, l.dataset.k])).concat([...document.querySelectorAll("[data-bg]")].map((e) => e.dataset.bg)).filter(Boolean))]);
    for (const src of assets) assert.equal((await page.request.get(BASE + "/" + src)).ok(), true, "asset exists: " + src);
    assert.equal((await page.request.get(BASE + "/policy.html")).ok(), true);
    for (const p of ["trial.html", "contact.html", "lead.js", "lead.css"]) assert.equal((await page.request.get(BASE + "/" + p)).ok(), true, p);
    assert.ok((await page.locator('a[href="trial.html"]').count()) > 0, "free trial entry under pricing");
    assert.equal(await page.locator('a[href^="mailto:"]').count(), 0, "contact uses the built-in form, not e-mail");
    assert.equal(await page.locator(".ft-word svg.sym").count(), 1, "footer shows the S symbol");

    /* 장면이 자리 잡은 순간: 기기 · 카드가 그 장면 문구(제목 · 설명 · 기능 줄)와 겹치지 않고, 화면 밖으로 잘리지 않는다.
       (예전에 노트북 바닥판이 화면보다 크게 그려지고, 대시보드 위에 문구가 겹치던 문제) */
    for (const [width, height] of [[1440, 900], [1280, 720], [1990, 1150]]) {
      await page.setViewportSize({ width, height });
      await page.waitForTimeout(900);
      for (const [t, scene] of [[200, "ops"], [380, "bank"], [705, "book"], [1140, "device"], [1560, "wrong"], [1640, "wrong"], [1880, "academy"], [2120, "eco"]]) {
        await seek(page, t);
        const bad = await page.evaluate((scene) => {
          const cp = document.querySelector('.sc[data-scene="' + scene + '"] .cp');
          const text = [...cp.querySelectorAll("h2,p,.det,.ops-list,.pages")].map((e) => e.getBoundingClientRect()).filter((r) => r.width && r.height);
          const shown = (e) => { const o = e.closest(".obj"); const st = getComputedStyle(o || e); return st.visibility !== "hidden" && +st.opacity > 0.3 };
          const parts = [...document.querySelectorAll("#xdr .f-front,#xdr .foot,.mac .lid-f,.mac .deck,#pad .fr,#phone .fr,#qb .qt,.agrp,.abars,#sheet .pp,#bookO .bk")].filter((e) => shown(e) && +getComputedStyle(e).opacity > 0.3);
          const out = parts.length ? [] : ["nothing on stage"];
          for (const e of parts) {
            const r = e.getBoundingClientRect();
            if (!r.width) continue;
            if (r.left < -2 || r.right > innerWidth + 2) out.push(e.className + " off-screen " + Math.round(r.left) + "," + Math.round(r.right));
            for (const c of text) if (r.left < c.right - 2 && r.right > c.left + 2 && r.top < c.bottom - 2 && r.bottom > c.top + 2) out.push(e.className + " covers copy");
          }
          return out;
        }, scene);
        assert.deepEqual(bad, [], "scene " + scene + " at " + width + "x" + height);
      }
    }
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.waitForTimeout(700);

    /* 폭마다 가로 넘침 없음 · 모바일은 가벼운 3D 그대로 */
    for (const width of [1440, 1024, 768, 390]) {
      await page.setViewportSize({ width, height: width < 800 ? 844 : 900 });
      await page.waitForTimeout(700);
      for (const t of [0, 380, 705, 1350, 1820, 2310]) {
        await seek(page, t);
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "no horizontal overflow at " + width + " / " + t);
      }
      await seek(page, 705);
      await page.screenshot({ path: OUT + "/viewport-" + width + "-book.png" });
    }
    await seek(page, 0);
    await page.screenshot({ path: OUT + "/mobile-hero.png" });
    await page.locator("#menu").click();
    assert.equal(await page.locator("#menu").getAttribute("aria-expanded"), "true");
    await page.keyboard.press("Escape");
    assert.equal(await page.locator("#menu").getAttribute("aria-expanded"), "false");
    assert.equal(await page.evaluate(() => document.activeElement.id), "menu");
    assert.deepEqual(errors, [], "no uncaught browser errors");
    await context.close();

    /* 라이트 모드: 시스템 설정을 따르고, 물질과 에너지 파랑으로 끝난다. 버튼으로 바꿀 수 있다 */
    const lightCtx = await browser.newContext({ viewport: { width: 1920, height: 900 }, colorScheme: "light" });
    const lp = await lightCtx.newPage();
    await lp.goto(BASE + "/intro.html");
    await lp.waitForTimeout(2500);
    assert.equal(await lp.evaluate(() => document.documentElement.dataset.theme), "light");
    await seek(lp, 1820);
    assert.ok(await lp.evaluate(() => [...document.querySelectorAll("#pad,#mac,#phone,#xdr")].every((e) => { const r = e.querySelector(".slab,.mac-lid,.xdr-body,.mac-base") || e; const b = r.getBoundingClientRect(); return b.right <= innerWidth + 2 && b.left >= -2 })), "operations scene fits a wide screen");
    await lp.screenshot({ path: OUT + "/light-academy-1920.png" });
    await seek(lp, 2310);
    assert.equal(await lp.locator(".film-bg").evaluate((e) => getComputedStyle(e).backgroundColor), "rgb(47, 127, 208)");
    await lp.locator("#thm").click();
    await lp.waitForTimeout(800);
    assert.equal(await lp.evaluate(() => document.documentElement.dataset.theme), "dark");
    await lightCtx.close();

    /* 동작 줄이기: 3D 무대 없이 같은 장면이 정적으로 이어진다 */
    const reduced = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
    const rp = await reduced.newPage();
    await rp.goto(BASE + "/intro.html");
    await rp.waitForTimeout(600);
    assert.equal(await rp.evaluate(() => document.documentElement.classList.contains("cine")), false);
    assert.equal(await rp.locator("#stage").isVisible(), false);
    assert.equal(await rp.locator("#book .still").isVisible(), true);
    assert.equal(await rp.locator("#omr .still").isVisible(), true);
    await rp.locator("#book").scrollIntoViewIfNeeded();
    await rp.screenshot({ path: OUT + "/reduced-motion.png" });
    await reduced.close();

    const staticContext = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
    const staticPage = await staticContext.newPage();
    await staticPage.goto(BASE + "/intro.html", { waitUntil: "networkidle" });
    await staticPage.waitForTimeout(500);
    assert.equal(await staticPage.locator("#h1").isVisible(), true);
    assert.equal(await staticPage.locator("#omr .still").isVisible(), true);
    assert.equal(await staticPage.locator("#plans .plan").count(), 3);
    await staticPage.locator("details").first().locator("summary").click();
    assert.equal(await staticPage.locator("details").first().getAttribute("open"), "");
    assert.ok(await staticPage.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "no overflow without JS");
    await staticPage.screenshot({ path: OUT + "/no-js.png", fullPage: true });
    await staticContext.close();

    const fallbackContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    await fallbackContext.route("**/rest/v1/site_config?**", (r) => r.abort());
    const fallback = await fallbackContext.newPage();
    await fallback.goto(BASE + "/intro.html");
    assert.match(await fallback.locator("#plans .plan h3").first().innerText(), /솔비 라이트/);
    assert.equal(await fallback.locator("#plans .plan").count(), 3);
    await fallbackContext.close();
    console.log("PASS: pricing, pinned scroll film, 10 scene states, reverse scroll, device UI fit, app destinations, overflow at 4 widths, keyboard menu, reduced motion, no JS. Screenshots: " + OUT);
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
