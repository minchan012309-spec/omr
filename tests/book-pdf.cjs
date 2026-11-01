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
    const concept = await page.evaluate(async () => {
      await setSubject("hl");
      await bkLoad();
      BKO.gutm = { ...(BKO.gutm || {}), "hl-c": 7 };
      const plan = await bkPlan("hl-c");
      const pages = plan.pages.filter((p) => p.k === "cn").slice(0, 2);
      if (pages.length !== 2)
        throw new Error("Missing real Korean concept pages");
      BKP["hl-c"] = { ...plan, pages, aStart: 3 };
      const main = await bkPlan("hl-hs");
      const passageIndex = main.pages.findIndex((p) => p.k === "cn" && p.kind === "p");
      if (passageIndex < 0) throw new Error("Missing Korean passage page");
      return { nums: pages.map((p) => p.n), passage: bkPageHtml(main, passageIndex) };
    });
    assert.doesNotMatch(concept.passage, /class="cnnote"/, "passage pages keep the existing layout");
    const nativeHtml = await page.evaluate(() => bkDocHtml(BKP["hl-c"], true));
    assert.equal((nativeHtml.match(/class="bp /g) || []).length, 2);
    assert.doesNotMatch(nativeHtml, /data-gut="1"/, "fixed concept geometry is not shifted by binding gutter");
    const native = await browser.newPage();
    await native.setContent(nativeHtml, { waitUntil: "domcontentloaded" });
    await native.evaluate(() => document.fonts.ready);
    const layout = await native.locator(".bp.cnp").evaluateAll((pages) => pages.map((p) => {
      const body = p.querySelector(".cnbody"), note = p.querySelector(".cnnote");
      const pr = p.getBoundingClientRect(), br = body.getBoundingClientRect(), nr = note.getBoundingClientRect(), ns = getComputedStyle(note);
      return {
        side: note.dataset.side,
        page: { left: pr.left, right: pr.right },
        body: { left: br.left, right: br.right, width: br.width },
        note: { left: nr.left, right: nr.right, width: nr.width },
        background: ns.backgroundColor,
        image: ns.backgroundImage,
        border: [ns.borderTopWidth, ns.borderRightWidth, ns.borderBottomWidth, ns.borderLeftWidth],
      };
    }));
    assert.equal(layout.length, 2, "two real concept pages use the note-margin layout");
    const pxmm = 96 / 25.4, close = (a, b, msg) => assert.ok(Math.abs(a - b) <= 1.5, `${msg}: ${a} vs ${b}`);
    layout.forEach((v, i) => {
      const expected = concept.nums[i] % 2 ? "right" : "left";
      assert.equal(v.side, expected, `p.${concept.nums[i]} uses the outer margin`);
      close(v.body.width, 148 * pxmm, "concept body is 148mm");
      close(v.note.width, 32 * pxmm, "note margin is 32mm");
      close(expected === "right" ? v.note.left - v.body.right : v.body.left - v.note.right, 6 * pxmm, "body-note gap is 6mm");
      close(expected === "right" ? v.body.left - v.page.left : v.page.right - v.body.right, 12 * pxmm, "inner safety margin is 12mm");
      close(expected === "right" ? v.page.right - v.note.right : v.note.left - v.page.left, 12 * pxmm, "outer safety margin is 12mm");
      assert.ok(v.body.left >= v.page.left - 1 && v.body.right <= v.page.right + 1, "concept body stays inside A4");
      assert.ok(v.note.left >= v.page.left - 1 && v.note.right <= v.page.right + 1, "note margin stays inside A4");
      assert.notEqual(v.background, "rgba(0, 0, 0, 0)", "note margin has a subject tint");
      assert.equal(v.image, "none", "note margin has no lines or image");
      assert.deepEqual(v.border, ["0px", "0px", "0px", "0px"], "note margin has no border");
    });
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
