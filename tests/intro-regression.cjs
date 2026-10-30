/* Browser regressions for the intro page (문구 + 실제 앱 캡처, 기기 목업 없음). Run with BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs */
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
/* 장면 섹션으로 스크롤(보통 문서: 위치만 바꾸고 잠깐 기다린다) */
const go = async (page, id) => {
  await page.evaluate((id) => document.getElementById(id).scrollIntoView({ block: "start" }), id);
  await page.waitForTimeout(500);
};
const SCENES = ["bank", "book", "device", "omr", "wrong", "academy", "eco"];
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

    /* 기기 목업 · 3D 무대 · GSAP 없이, 장면마다 문구와 실제 앱 캡처만 있다 */
    assert.equal(await page.evaluate(() => typeof window.gsap), "undefined", "no animation library loaded");
    assert.equal(await page.evaluate(() => typeof window.ScrollTrigger), "undefined", "no pinned ScrollTrigger film");
    assert.equal(await page.locator("#stage,.stage,.film-bg,.xdr,.mac,.slab,.rig,.obj").count(), 0, "no device mockup or 3D stage");
    assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).scrollSnapType), "none", "no forced scroll");
    assert.equal(await page.locator("#h1").isVisible(), true);
    await page.screenshot({ path: OUT + "/desktop-hero.png" });
    for (const id of ["hero"].concat(SCENES)) {
      await go(page, id);
      const shots = await page.locator("#" + id + " img.shot").evaluateAll((l) => l.map((i) => ({ ok: i.complete && i.naturalWidth > 0, src: i.getAttribute("src"), alt: i.alt })));
      assert.ok(shots.length > 0, id + " has captures");
      for (const sh of shots) {
        assert.ok(sh.ok, id + " capture loads: " + sh.src);
        assert.ok(sh.alt.length > 4, id + " capture has alt text: " + sh.src);
      }
      if (id !== "hero") await page.screenshot({ path: OUT + "/desktop-" + id + ".png" });
    }
    await page.evaluate(() => scrollTo(0, document.getElementById("start").getBoundingClientRect().top + scrollY + 120));
    await page.waitForTimeout(600);
    assert.ok(await page.locator(".hd").evaluate((e) => e.classList.contains("light")), "header turns light on the final scene");
    assert.equal(await page.locator("#h-end").isVisible(), true);

    /* 폭마다: 캡처가 그 장면 문구와 겹치지 않고 화면 밖으로 나가지 않는다 */
    for (const [width, height] of [[1990, 1150], [1440, 900], [1280, 720], [820, 1180], [390, 844]]) {
      await page.setViewportSize({ width, height });
      await page.waitForTimeout(500);
      const bad = await page.evaluate((ids) => {
        const out = [];
        for (const id of ids) {
          const sec = document.getElementById(id);
          const text = [...sec.querySelectorAll(".cp h2,.cp p,.cp .det,.cp .score")].map((e) => e.getBoundingClientRect());
          for (const img of sec.querySelectorAll("img.shot")) {
            const r = img.getBoundingClientRect();
            if (r.width < 40) out.push(id + " capture too small " + Math.round(r.width));
            if (r.left < -1 || r.right > innerWidth + 1) out.push(id + " capture off-screen");
            for (const c of text) if (r.left < c.right - 1 && r.right > c.left + 1 && r.top < c.bottom - 1 && r.bottom > c.top + 1) out.push(id + " capture covers copy");
          }
        }
        return out;
      }, SCENES);
      assert.deepEqual(bad, [], "captures at " + width + "x" + height);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "no horizontal overflow at " + width);
    }
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.waitForTimeout(400);

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

    await page.setViewportSize({ width: 390, height: 844 });
    await page.evaluate(() => scrollTo(0, 0));
    await page.waitForTimeout(500);
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
    await go(lp, "start");
    assert.equal(await lp.locator(".sc-end").evaluate((e) => getComputedStyle(e).backgroundColor), "rgb(47, 127, 208)");
    await lp.screenshot({ path: OUT + "/light-end-1920.png" });
    await lp.locator("#thm").click();
    await lp.waitForTimeout(800);
    assert.equal(await lp.evaluate(() => document.documentElement.dataset.theme), "dark");
    await lightCtx.close();

    /* 동작 줄이기: 같은 문서 그대로(움직이는 연출이 원래 없다) */
    const reduced = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
    const rp = await reduced.newPage();
    await rp.goto(BASE + "/intro.html");
    await rp.waitForTimeout(600);
    assert.equal(await rp.locator("#book .shots").isVisible(), true);
    assert.equal(await rp.locator("#omr .shots").isVisible(), true);
    await rp.locator("#book").scrollIntoViewIfNeeded();
    await rp.screenshot({ path: OUT + "/reduced-motion.png" });
    await reduced.close();

    const staticContext = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
    const staticPage = await staticContext.newPage();
    await staticPage.goto(BASE + "/intro.html", { waitUntil: "networkidle" });
    await staticPage.waitForTimeout(500);
    assert.equal(await staticPage.locator("#h1").isVisible(), true);
    assert.equal(await staticPage.locator("#omr .shots").isVisible(), true);
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
    console.log("PASS: pricing, captures only (no mockup/3D/GSAP), captures load with alt, no copy overlap at 5 sizes, app destinations, keyboard menu, light end, reduced motion, no JS. Screenshots: " + OUT);
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
