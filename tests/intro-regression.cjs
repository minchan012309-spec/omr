/* Browser regressions. Run with BASE=http://127.0.0.1:8765 node tests/intro-regression.cjs */
const assert = require("node:assert/strict");
const { chromium, browserOptions } = require("./runtime.cjs");
const fs = require("node:fs");
const BASE = process.env.BASE || "http://127.0.0.1:8765";
const OUT = process.env.INTRO_SHOTS || "/tmp/solvi-intro-verification";
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch(browserOptions());
  try {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
      serviceWorkers: "block",
    });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    let requests = 0;
    await context.route("**/rest/v1/site_config?**", (route) => {
      requests++;
      return route.fulfill({
        json: [
          {
            value: {
              plans: [
                {
                  name: "테스트 라이트",
                  price: "50000",
                  unit: "/ 월",
                  items: ["교재 인쇄"],
                  cta: "시작하기",
                },
                {
                  name: "테스트 플러스",
                  price: "150000",
                  unit: "/ 월",
                  items: ["OMR 채점"],
                  cta: "시작하기",
                },
                {
                  name: "테스트 플래티넘",
                  price: "300000",
                  unit: "/ 월",
                  items: ["학원 운영"],
                  cta: "문의하기",
                  hl: true,
                },
              ],
              contact: "https://example.com/solvi-contact",
              note: "테스트 요금 안내",
            },
          },
        ],
      });
    });
    await page.goto(BASE + "/intro.html");
    await page
      .locator("#plans h3")
      .first()
      .filter({ hasText: "테스트 라이트" })
      .waitFor();
    assert.equal(requests, 1, "existing pricing endpoint is still called");
    assert.equal(await page.locator("#prNote").innerText(), "테스트 요금 안내");
    assert.equal(
      await page
        .locator("#plans .plan")
        .last()
        .locator("a")
        .getAttribute("href"),
      "https://example.com/solvi-contact",
    );
    assert.equal(await page.locator("#plans .plan").count(), 3);
    await page.locator('.need button[data-lv="2"]').first().click();
    assert.match(await page.locator("#needO").innerText(), /테스트 플래티넘/);
    assert.equal(await page.locator(".plan.hit").count(), 1);
    const assets = await page
      .locator("img")
      .evaluateAll((imgs) => [
        ...new Set(imgs.map((i) => i.getAttribute("src"))),
      ]);
    await Promise.all(
      assets.map(async (src) =>
        assert.equal(
          (await page.request.get(BASE + "/" + src)).ok(),
          true,
          "asset exists: " + src,
        ),
      ),
    );
    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: OUT + "/desktop-hero.png" });
    for (const [chapter, label] of [
      ["question-bank", "bank"],
      ["books", "book"],
      ["omr", "omr"],
      ["analysis", "analysis"],
    ]) {
      await page
        .locator("#" + chapter)
        .evaluate((e) =>
          scrollTo(
            0,
            e.offsetTop +
              document.querySelector("#flow").offsetTop -
              innerHeight * 0.15,
          ),
        );
      await page.waitForTimeout(150);
      await page.screenshot({ path: OUT + "/desktop-" + label + ".png" });
    }
    await page.locator("#flow").evaluate((e) => scrollTo(0, e.offsetTop));
    await page.waitForTimeout(60);
    const initial = await page
      .locator(".stage-canvas")
      .evaluate((e) => e.style.getPropertyValue("--base-opacity"));
    await page.locator("#books").evaluate((e) => e.scrollIntoView());
    await page.waitForTimeout(60);
    const book = await page
      .locator(".stage-canvas")
      .evaluate((e) => ({
        base: e.style.getPropertyValue("--base-opacity"),
        cover: e.style.getPropertyValue("--cover-angle"),
        opacity: e.style.getPropertyValue("--book-opacity"),
      }));
    assert.notEqual(initial, book.base, "tablet changes to laptop");
    assert.notEqual(book.cover, "0deg", "book cover follows scroll");
    assert.ok(+book.opacity > 0.5, "actual book pages replace the screen");
    await page.locator("#flow").evaluate((e) => {
      const ch = e.querySelectorAll("[data-chapter]");
      scrollTo(
        0,
        scrollY +
          ch[0].getBoundingClientRect().top +
          (ch[3].offsetTop - ch[0].offsetTop) * 0.51 -
          innerHeight * 0.48,
      );
    });
    await page.waitForTimeout(60);
    assert.ok(
      parseFloat(
        await page
          .locator(".stage-canvas")
          .evaluate((e) => e.style.getPropertyValue("--leaf-angle")),
      ) < -40,
      "a real inner page turns after the cover opens",
    );
    await page.locator("#omr").evaluate((e) => e.scrollIntoView());
    await page.waitForTimeout(60);
    assert.ok(
      +(await page
        .locator(".stage-canvas")
        .evaluate((e) => e.style.getPropertyValue("--phone-opacity"))) > 0.5,
      "OMR phone is revealed",
    );
    await page.locator("#analysis").evaluate((e) => e.scrollIntoView());
    await page.waitForTimeout(60);
    assert.ok(
      +(await page
        .locator(".stage-canvas")
        .evaluate((e) => e.style.getPropertyValue("--analysis-opacity"))) > 0.8,
      "actual product UI changes to analysis",
    );
    assert.equal(
      await page.evaluate(
        () => getComputedStyle(document.documentElement).scrollSnapType,
      ),
      "none",
    );
    assert.equal(
      (await page
        .locator('a[data-app][href="index.html?app=1#login"]')
        .count()) > 0,
      true,
    );
    await page
      .locator('a[data-app][href="index.html?app=1#student"]')
      .first()
      .evaluate((e) => {
        e.addEventListener("click", (ev) => ev.preventDefault(), {
          once: true,
        });
        e.click();
      });
    assert.equal(
      await page.evaluate(() => localStorage.getItem("omr_app")),
      "1",
    );
    for (const width of [1440, 768, 390]) {
      await page.setViewportSize({ width, height: 900 });
      await page.evaluate(() => scrollTo(0, 0));
      await page.waitForTimeout(80);
      if (width <= 900) {
        await page
          .locator(".mobile-proof")
          .evaluateAll((es) => Promise.all(es.map((e) => e.decode())));
        assert.ok(
          await page
            .locator(".mobile-proof")
            .evaluateAll((es) => es.every((e) => e.naturalWidth > 0)),
          "mobile proof images decode",
        );
      }
      assert.ok(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        "no horizontal overflow at " + width,
      );
      await page.screenshot({
        path: OUT + "/viewport-" + width + ".png",
        fullPage: true,
      });
    }
    await page.screenshot({ path: OUT + "/mobile-hero.png" });
    await page.locator("#omr").scrollIntoViewIfNeeded();
    await page.screenshot({ path: OUT + "/mobile-omr.png" });
    await page.locator("#menu").click();
    assert.equal(
      await page.locator("#menu").getAttribute("aria-expanded"),
      "true",
    );
    await page.keyboard.press("Escape");
    assert.equal(
      await page.locator("#menu").getAttribute("aria-expanded"),
      "false",
    );
    assert.equal(await page.evaluate(() => document.activeElement.id), "menu");
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.waitForTimeout(80);
    assert.equal(await page.locator(".story-stage").isVisible(), false);
    assert.equal(await page.locator("#books .mobile-proof").isVisible(), true);
    assert.equal(await page.locator("#omr .mobile-proof").isVisible(), true);
    await page.locator("#books").scrollIntoViewIfNeeded();
    await page.screenshot({ path: OUT + "/reduced-motion.png" });
    const staticContext = await browser.newContext({
      javaScriptEnabled: false,
      viewport: { width: 390, height: 844 },
    });
    const staticPage = await staticContext.newPage();
    await staticPage.goto(BASE + "/intro.html");
    assert.equal(await staticPage.locator("#h1").isVisible(), true);
    assert.equal(
      await staticPage.locator("#omr .mobile-proof").isVisible(),
      true,
    );
    assert.equal(await staticPage.locator("#plans .plan").count(), 3);
    await staticPage.locator("details").first().locator("summary").click();
    assert.equal(
      await staticPage.locator("details").first().getAttribute("open"),
      "",
    );
    await staticPage.screenshot({ path: OUT + "/no-js.png", fullPage: true });
    await staticContext.close();
    const fallbackContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    await fallbackContext.route("**/rest/v1/site_config?**", (r) => r.abort());
    const fallback = await fallbackContext.newPage();
    await fallback.goto(BASE + "/intro.html");
    assert.match(
      await fallback.locator("#plans .plan h3").first().innerText(),
      /솔비 라이트/,
    );
    assert.equal(await fallback.locator("#plans .plan").count(), 3);
    await fallbackContext.close();
    assert.deepEqual(errors, [], "no uncaught browser errors");
    await context.close();
    console.log(
      "PASS: pricing, 3D scroll states, actual UI changes, app destinations, overflow at 3 widths, keyboard menu, reduced motion, no JS. Screenshots: " +
        OUT,
    );
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
