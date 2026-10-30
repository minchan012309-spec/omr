/* Browser regressions for the intro page (문구 + 실제 앱 캡처, 기기 목업 없음, 스크롤 위치에 맞춘 캡처 연출). Run with BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs */
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
const SCENES = ["book", "device", "academy", "eco"];
/* sticky 장면(run)의 진행도 p 로 스크롤 */
const runTo = async (page, id, p) => {
  await page.evaluate(([id, p]) => { const r = document.getElementById(id), pin = r.firstElementChild, hd = document.querySelector(".hd").offsetHeight; scrollTo(0, r.getBoundingClientRect().top + scrollY - hd + (r.offsetHeight - pin.offsetHeight) * p); }, [id, p]);
  await page.waitForTimeout(350);
};
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
    for (const id of SCENES) {
      await go(page, id);
      const shots = await page.locator("#" + id + " img.shot").evaluateAll((l) => l.map((i) => ({ ok: i.complete && i.naturalWidth > 0, src: i.getAttribute("src"), alt: i.alt })));
      assert.ok(shots.length > 0, id + " has captures");
      for (const sh of shots) {
        assert.ok(sh.ok, id + " capture loads: " + sh.src);
        assert.ok(sh.alt.length > 4, id + " capture has alt text: " + sh.src);
      }
      await page.screenshot({ path: OUT + "/desktop-" + id + ".png" });
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
            if (+getComputedStyle(img).opacity > 0.05 && (r.left < -1 || r.right > innerWidth + 1)) out.push(id + " capture off-screen");
            for (const c of text) if (r.left < c.right - 1 && r.right > c.left + 1 && r.top < c.bottom - 1 && r.bottom > c.top + 1) out.push(id + " capture covers copy");
          }
        }
        return out;
      }, SCENES);
      assert.deepEqual(bad, [], "captures at " + width + "x" + height);
      /* 한 바퀴 무대 · 연결 그래프: 단계 글과 겹치지 않고, 머리글 아래 화면 안에 다 들어온다 */
      for (const [run, side, box, ps] of [["flowRun", ".flow-side", "#fb", [0.05, 0.3, 0.5, 0.7, 0.95]], ["qrRun", ".qr-cp", "#qb", [0.05, 0.3, 0.6, 0.9]], ["linkRun", ".link-cp", "#lb", [0.2, 0.98]], ["dayRun", ".day-steps,.dd.on", ".day-frame", [0.05, 0.5, 0.95]]]) {
        for (const p of ps) {
          await runTo(page, run, p);
          const r = await page.evaluate(([side, box]) => {
            const a = document.querySelector(box).getBoundingClientRect(), hd = document.querySelector(".hd").offsetHeight;
            const t = [...document.querySelectorAll(side.includes(",") ? side : side + " h2," + side + " .fd.on," + side + " .flow-steps," + side + " li.on")].map((e) => e.getBoundingClientRect()).filter((x) => x.height);
            return { over: t.some((c) => a.left < c.right - 1 && a.right > c.left + 1 && a.top < c.bottom - 1 && a.bottom > c.top + 1), top: a.top - hd, bottom: innerHeight - a.bottom, left: a.left, right: innerWidth - a.right, w: a.width };
          }, [side, box]);
          assert.ok(!r.over && r.top > -2 && r.bottom > -2 && r.left > -2 && r.right > -2 && r.w > 200, run + " " + p + " at " + width + "x" + height + ": " + JSON.stringify(r));
        }
      }
      assert.ok(await page.evaluate((w) => document.documentElement.scrollWidth <= w && innerWidth === w, width), "no horizontal overflow at " + width);
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
    await page.locator('.nav a[href="#flow"]').click();
    await page.waitForTimeout(600);
    assert.ok(await page.evaluate(() => Math.abs(document.getElementById("flow").getBoundingClientRect().top - parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop)) < 2), "nav is a plain anchor to the core-flow section");
    assert.equal(await page.locator('.nav a[href="#flow"]').getAttribute("aria-current"), "true", "nav marks the section in view");
    /* 히어로: 살아 있는 취약 유형 지도(실제 앱의 상태 6단계). 처음에 칠해지고 약한 유형이 골라진 뒤, 눌러서 고를 수 있다 */
    await page.evaluate(() => scrollTo(0, 0));
    const lg = () => page.evaluate(() => Object.fromEntries([...document.querySelectorAll(".tm-lg li")].map((l) => [l.dataset.lv, +l.querySelector("b").textContent])));
    assert.equal(await page.locator("#tmap .tt").count(), 15);
    assert.deepEqual(await lg(), { skull: 2, red: 3, yellow: 3, gray: 2, green: 3, star: 2 }, "type map painted: skull · red · yellow …");
    assert.equal(await page.locator('#tmap .tt[aria-pressed="true"]').count(), 5, "weak types picked");
    assert.equal(await page.locator("#tmQ").innerText(), "25");
    await page.locator('#tmap .tt[data-lv="gray"]').first().click();
    assert.equal(await page.locator("#tmN").innerText(), "6", "tapping a type adds it");
    assert.equal(await page.locator("#tmQ").innerText(), "30");
    assert.match(await page.locator('#tmap .tt[data-lv="skull"]').first().getAttribute("aria-label"), /해골 · 거의 못 맞힘 · 정답률 25%/);
    /* 한 바퀴: 진행도마다 단계 · 설명 · 무대가 바뀐다(스크롤 위치에서 바로 계산) */
    for (const [i, p] of [0.1, 0.3, 0.5, 0.7, 0.9].entries()) {
      await runTo(page, "flowRun", p);
      assert.equal(await page.locator(".flow-steps li").nth(i).locator("a").getAttribute("aria-current"), "step", "step " + (i + 1) + " at " + p);
      assert.equal(await page.locator(".fd.on").getAttribute("id"), "flow-" + i);
    }
    await runTo(page, "flowRun", 0.5);
    assert.ok(+(await page.locator(".fphone").evaluate((e) => getComputedStyle(e).opacity)) > 0.9, "phone capture in the grading step");
    await runTo(page, "flowRun", 0.78);
    assert.deepEqual(await page.locator(".fm-g span").evaluateAll((l) => l.map((x) => x.dataset.s)), ["skull", "red", "red", "yellow", "green", "star"], "wrong answers paint the type tiles");
    await runTo(page, "flowRun", 1);
    assert.deepEqual(await page.locator(".fm-g span").evaluateAll((l) => l.map((x) => x.dataset.s)), ["red", "yellow", "green", "green", "star", "star"], "studying again changes the colours");
    await runTo(page, "flowRun", 0.1);
    assert.deepEqual(await page.locator(".fm-g span").evaluateAll((l) => l.map((x) => x.dataset.s)), ["gray", "gray", "gray", "gray", "gray", "gray"], "scrolling back restores the earlier state");
    /* QR 채점: 카메라 창이 QR로 확대 → 인식 → OMR → 결과, 단계가 따라 켜진다 */
    await runTo(page, "qrRun", 0.05);
    assert.equal(await page.locator(".qr-steps li.on").getAttribute("data-i"), "0");
    await runTo(page, "qrRun", 0.36);
    assert.ok((await page.locator(".qpage").evaluate((e) => new DOMMatrix(getComputedStyle(e).transform).a)) > 3, "camera zooms onto the QR");
    assert.equal(await page.locator(".qr-steps li.on").getAttribute("data-i"), "1");
    await runTo(page, "qrRun", 0.45);
    assert.ok(await page.locator(".qfind").evaluate((e) => e.classList.contains("ok")), "QR recognised");
    await runTo(page, "qrRun", 0.9);
    assert.equal(await page.locator(".qscore dd").last().innerText(), "75%");
    assert.ok(+(await page.locator(".qphone .res").evaluate((e) => getComputedStyle(e).opacity)) > 0.9, "result capture shown");
    assert.equal(await page.locator(".qr-ways li").count(), 4, "other ways to grade listed");
    /* 학원의 하루: 아홉 장면이 스크롤 위치대로 넘어간다 */
    assert.equal(await page.locator(".day-steps li").count(), 9);
    for (const i of [0, 2, 4, 7, 8]) {
      await runTo(page, "dayRun", (i + 0.5) / 9);
      assert.equal(await page.locator(".day-steps li.on").getAttribute("data-i"), String(i), "day step " + i);
      assert.equal(await page.locator(".dd.on").getAttribute("id"), "day-" + i);
    }
    const dayImgs = await page.locator(".day-frame .shot").evaluateAll((l) => l.map((i) => ({ ok: i.complete && i.naturalWidth > 0, src: i.getAttribute("src") })));
    for (const d of dayImgs) assert.ok(d.ok, "academy capture loads: " + d.src);
    /* 기능 전체: 분야를 누르면 그 분야 카드만 */
    const total = await page.locator(".spec-g .sp").count();
    assert.ok(total >= 30, "detailed feature catalog: " + total);
    await page.locator('.cats button[data-cat="grade"]').click();
    assert.equal(await page.locator(".spec-g .sp:visible").count(), await page.locator('.spec-g .sp[data-cat="grade"]').count());
    assert.equal(await page.locator("#catN").innerText(), String(await page.locator('.spec-g .sp[data-cat="grade"]').count()));
    await page.locator('.cats button[data-cat="all"]').click();
    assert.equal(await page.locator(".spec-g .sp:visible").count(), total);
    /* 요금제별 비교: 서버 요금제(시험용)의 이름 · 가격으로 맞춰진다 */
    assert.equal(await page.locator("#cmp thead th[data-i]").count(), 3);
    assert.equal(await page.locator('#cmp thead th[data-i="2"]').innerText(), "테스트 플래티넘");
    assert.equal(await page.locator('#cmp tr.price td[data-i="1"]').innerText(), "150,000원");
    /* 연결: 끝까지 내리면 열두 기능이 모두 이어지고, 기능에 올리면 설명과 이어진 선이 강조된다 */
    await runTo(page, "linkRun", 1);
    assert.equal(await page.locator("#lb .ln.lit").count(), 12, "every feature is linked");
    assert.ok((await page.locator("#lb .lsvg path").count()) >= 23);
    await page.locator("#lb .ln").nth(3).hover();
    assert.ok((await page.locator("#lb .lsvg path.hot").count()) >= 3, "hovering a feature highlights its links");
    assert.equal(await page.locator("#lb .ln").nth(3).locator("span").isVisible(), true);
    assert.equal(await page.getByText("학습지 번호로 바로 채점하기").count(), 0, "number-grading shortcut removed from the intro");
    const assets = await page.evaluate(() => [...new Set([...document.querySelectorAll("img")].map((i) => i.getAttribute("src") || i.dataset.src).concat([...document.querySelectorAll(".leaf")].flatMap((l) => [l.dataset.f, l.dataset.k])).concat([...document.querySelectorAll("[data-bg]")].map((e) => e.dataset.bg)).filter(Boolean))]);
    for (const src of assets) assert.equal((await page.request.get(BASE + "/" + src)).ok(), true, "asset exists: " + src);
    assert.equal((await page.request.get(BASE + "/policy.html")).ok(), true);
    for (const p of ["trial.html", "contact.html", "lead.js", "lead.css"]) assert.equal((await page.request.get(BASE + "/" + p)).ok(), true, p);
    assert.ok((await page.locator('a[href="trial.html"]').count()) > 0, "free trial entry under pricing");
    assert.equal(await page.locator('a[href^="mailto:"]').count(), 0, "contact uses the built-in form, not e-mail");
    assert.equal(await page.locator(".ft-logos svg.sym").count(), 1, "footer shows the S symbol");
    assert.equal(await page.locator(".ft-logos svg.ft-wm").count(), 1, "footer shows the Solvi wordmark");
    assert.equal(await page.locator(".ko-logo").count(), 0, "no Korean logo in the footer (user removed it)");

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

    /* 실제 휴대폰처럼(isMobile): 장면을 지나는 동안 레이아웃 폭이 화면보다 넓어지지 않는다(넓어지면 브라우저가 페이지를 축소해 보여 준다) */
    const mob = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
    const mp = await mob.newPage();
    await mp.goto(BASE + "/intro.html");
    await mp.waitForTimeout(1200);
    for (const [run, p] of [["flowRun", 0.5], ["qrRun", 0.3], ["qrRun", 0.55], ["linkRun", 0.9], ["dayRun", 0.3], ["dayRun", 0.9]]) {
      await runTo(mp, run, p);
      const w = await mp.evaluate(() => [innerWidth, document.documentElement.scrollWidth]);
      assert.deepEqual(w, [390, 390], "mobile layout width stays 390 at " + run + " " + p);
    }
    await mp.locator("#cmp").scrollIntoViewIfNeeded();
    assert.ok(await mp.evaluate(() => { const s = document.querySelector(".cmp-scroll"); return s.scrollWidth <= s.clientWidth + 1; }), "plan comparison fits a phone without sideways scrolling");
    await mob.close();

    /* 동작 줄이기: 같은 문서 그대로(움직이는 연출이 원래 없다) */
    const reduced = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
    const rp = await reduced.newPage();
    await rp.goto(BASE + "/intro.html");
    await rp.waitForTimeout(600);
    assert.equal(await rp.evaluate(() => document.documentElement.classList.contains("fx")), false, "no scroll effects with reduced motion");
    assert.equal(await rp.locator("#book .shots").isVisible(), true);
    assert.equal(await rp.locator(".fd:visible").count(), 5, "all five steps readable without motion");
    assert.equal(await rp.locator("#lb .ln:visible").count(), 12);
    assert.equal(await rp.locator('#tmap .tt[aria-pressed="true"]').count(), 5, "type map already painted");
    await rp.locator("#book").scrollIntoViewIfNeeded();
    await rp.screenshot({ path: OUT + "/reduced-motion.png" });
    await reduced.close();

    const staticContext = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
    const staticPage = await staticContext.newPage();
    await staticPage.goto(BASE + "/intro.html", { waitUntil: "networkidle" });
    await staticPage.waitForTimeout(500);
    assert.equal(await staticPage.locator("#h1").isVisible(), true);
    assert.equal(await staticPage.locator("#book .shots").isVisible(), true);
    assert.equal(await staticPage.locator("#tmap .tt").count(), 15);
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
    console.log("PASS: pricing, no mockup/3D/GSAP, live type map (paint · pick · tap), 5-step scroll stage (forward · back), QR scene, academy day (9 steps), feature catalog filter, plan comparison, link graph (draw · hover), mobile layout width, captures load with alt, no copy overlap at 5 sizes, app destinations, keyboard menu, light end, reduced motion, no JS. Screenshots: " + OUT);
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
