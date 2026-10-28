// Real DOM checks: theme inheritance, A4 preview parity and Korean text preservation.
const assert = require("node:assert/strict");
const { chromium, browserOptions } = require("./runtime.cjs");
(async () => {
  const browser = await chromium.launch(browserOptions());
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  let failed = 0;
  try {
    await page.goto(
      (process.env.BASE || "http://127.0.0.1:8765").replace(/\/$/, "") +
        "/index.html?app=1",
    );
    await page.waitForFunction(() => typeof startView === "function");
    await page.waitForTimeout(2000);
    const check = async (name, fn) => {
      try {
        await fn();
        console.log("PASS", name);
      } catch (e) {
        failed++;
        console.error("FAIL", name, e.message);
      }
    };
    await page.evaluate(() => {
      document.documentElement.dataset.theme = "dark";
      startView();
    });
    await check("dark start cards use dark surfaces", async () =>
      assert.notEqual(
        await page
          .locator(".stp-k")
          .first()
          .evaluate((e) => getComputedStyle(e).backgroundColor),
        "rgb(255, 255, 255)",
      ),
    );
    await check("switch stays 40px without checkbox tick", async () => {
      const v = await page.evaluate(() => {
        const e = document.createElement("input");
        e.type = "checkbox";
        e.className = "sw";
        e.checked = true;
        document.body.append(e);
        const v = {
          width: getComputedStyle(e).width,
          before: getComputedStyle(e, "::before").content,
        };
        e.remove();
        return v;
      });
      assert.equal(v.width, "40px");
      assert.ok(["none", "normal"].includes(v.before));
    });
    await check("selected design label readable in dark mode", async () => {
      const v = await page.evaluate(() => {
        const e = document.createElement("button");
        e.className = "bdt on";
        e.innerHTML = styleThumb("basic", "blue") + "<span>표준</span>";
        document.body.append(e);
        const c = getComputedStyle(e),
          v = {
            bg: c.backgroundColor,
            fg: c.color,
            thumb: getComputedStyle(e.firstElementChild).backgroundColor,
          };
        e.remove();
        return v;
      });
      assert.notEqual(v.bg, "rgb(243, 247, 255)");
      assert.equal(v.thumb, "rgb(255, 255, 255)");
    });
    await check(
      "print preview preserves white paper and unfiltered ink",
      async () => {
        const v = await page.evaluate(async () => {
          const host = document.createElement("div");
          host.id = "testPaper";
          document.body.append(host);
          await openWs(
            {
              id: "00000000",
              t: Date.now(),
              title: "국어 출력 검사",
              codes: DATA.filter((q) => q.set === "mc")
                .slice(0, 2)
                .map((q) => q.code),
              style: "basic",
              color: "teal",
              font: "paper",
              per: 2,
              cols: 2,
            },
            host,
          );
          const v = {
            filter: getComputedStyle(host.shadowRoot.querySelector(".wrap"))
              .filter,
            paper: getComputedStyle(host.shadowRoot.querySelector(".pg"))
              .backgroundColor,
          };
          host.remove();
          return v;
        });
        assert.equal(v.filter, "none");
        assert.equal(v.paper, "rgb(255, 255, 255)");
      },
    );
    await page.evaluate(() => bkLoad());
    await page.waitForFunction(() => typeof bkCbUnits === "function");
    await check(
      "Korean concept renderer preserves text nodes and HTML entities once",
      async () => {
        const v = await page.evaluate(() => {
          const us = bkCbUnits(
            {
              id: "regression",
              no: "1",
              title: "개념",
              html: "앞말 &amp; 공백\n<p>본문 &lt;예문&gt; <u>밑줄</u> ᄒᆞᆫ</p>뒷말",
            },
            180,
          );
          const root = document.createElement("div");
          root.innerHTML = us.map((u) => u.html).join("");
          return { text: root.textContent, under: !!root.querySelector("u") };
        });
        assert.ok(v.text.includes("앞말 & 공백"));
        assert.ok(v.text.includes("뒷말"));
        assert.ok(v.text.includes("<예문>"));
        assert.ok(v.under);
      },
    );
    await check(
      "standalone Korean book includes local fallback font definitions",
      async () => {
        const h = await page.evaluate(() =>
          bkStandalone({ title: "검사", pages: [] }),
        );
        assert.ok(h.includes("KoPubDotum-Medium.subset.woff2"));
        assert.ok(h.includes("Pretendard-Regular.woff2"));
      },
    );
    await page.screenshot({ path: "/tmp/solvi-dark-after.png" });
  } finally {
    await browser.close();
  }
  if (failed) process.exit(1);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
