const assert = require("node:assert/strict"),
  fs = require("node:fs");
const { chromium, browserOptions } = require("./runtime.cjs");
(async () => {
  const browser = await chromium.launch(browserOptions());
  try {
    const page = await browser.newPage({
      acceptDownloads: true,
      viewport: { width: 1400, height: 1000 },
    });
    await page.goto(
      (process.env.BASE || "http://127.0.0.1:8765").replace(/\/$/, "") +
        "/index.html?app=1",
    );
    await page.waitForTimeout(1800);
    await page.evaluate(async () => {
      await setSubject("hl");
      await bkLoad();
      const plan = await bkPlan("hl-c");
      const pages = plan.pages.filter((p) => p.k === "cn").slice(0, 2);
      if (pages.length !== 2)
        throw new Error("Missing real Korean concept pages");
      BKP["hl-c"] = { ...plan, pages, aStart: 3 };
    });
    const nativeHtml = await page.evaluate(() => bkDocHtml(BKP["hl-c"], true));
    assert.equal((nativeHtml.match(/class="bp /g) || []).length, 2);
    const native = await browser.newPage();
    await native.setContent(nativeHtml, { waitUntil: "domcontentloaded" });
    await native.evaluate(() => document.fonts.ready);
    await native.pdf({
      path: "/tmp/solvi-concept-native.pdf",
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
    });
    await native.screenshot({
      path: "/tmp/solvi-concept-print.png",
      fullPage: true,
    });
    await native.close();
    const downloadPromise = page.waitForEvent("download", { timeout: 90000 });
    await page.evaluate(() => bkPdf("hl-c", 1));
    const download = await downloadPromise;
    await download.saveAs("/tmp/solvi-concept-app.pdf");
    assert.equal(
      fs.readFileSync("/tmp/solvi-concept-app.pdf").subarray(0, 4).toString(),
      "%PDF",
    );
    assert.ok(fs.statSync("/tmp/solvi-concept-app.pdf").size > 20000);
    console.log(
      "PASS original Korean book preview/native A4 print and html2canvas+jsPDF download (two real concept pages)",
    );
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
