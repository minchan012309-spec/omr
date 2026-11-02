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
      const plan = await bkPlan("hl-c");
      const notes = plan.pages.filter((p) => p.k === "nt");
      if (notes.length !== 10 || plan.noteStart !== 3)
        throw new Error("Missing ten lined note pages before Korean concepts");
      if (!notes.every((p, i) => p.st === "lined" && p.note === i + 1))
        throw new Error("Korean concept note pages must be numbered lined notes");
      const free = bkPlanFree("preview", {
        kind: "free",
        name: "화법과 언어 개념서",
        parts: [{ k: "c", all: false, cap: 0, lv: 15 }],
        subs: [0],
        sort: 0,
        grp: 0,
        ans: 2,
        brk: 0,
        dz: {},
      });
      free.pages.forEach((p, i) => (p.n = i + 1));
      const freeNotes = free.pages.filter((p) => p.k === "nt");
      const firstFreeConcept = free.pages.findIndex((p) => p.k === "cn");
      if (freeNotes.length !== 10 || firstFreeConcept !== 12)
        throw new Error("Custom Korean concept books need ten note pages before concepts");
      const freeHtml = bkDocHtml(free, true);
      if ((freeHtml.match(/class="bp bk"/g) || []).length < 10)
        throw new Error("Printed custom Korean concept books must include the note pages");
      const note = bkPageHtml(plan, plan.pages.indexOf(notes[0]));
      const pages = plan.pages.filter((p) => p.k === "cn").slice(0, 2);
      if (pages.length !== 2)
        throw new Error("Missing real Korean concept pages");
      BKP["hl-c"] = { ...plan, pages, aStart: 3 };
      const main = await bkPlan("hl-hs"), passage = main.pages.findIndex((p) => p.k === "cn" && p.kind === "p");
      return { nums: pages.map((p) => p.n), note, passage: bkPageHtml(main, passage) };
    });
    assert.doesNotMatch(concept.passage, /class="cnnote"/);
    const nativeHtml = await page.evaluate(() => bkDocHtml(BKP["hl-c"], true));
    assert.equal((nativeHtml.match(/class="bp /g) || []).length, 2);
    const native = await browser.newPage();
    await native.setContent(nativeHtml, { waitUntil: "domcontentloaded" });
    await native.evaluate(() => document.fonts.ready);
    const layout = await native.locator(".bp.cnp").evaluateAll((pages) => pages.map((p) => {
      const top = p.querySelector(".cntop"), body = p.querySelector(".cnbody"), note = p.querySelector(".cnnote"), pr = p.getBoundingClientRect(), br = body.getBoundingClientRect(), nr = note.getBoundingClientRect();
      return { hasTitle: !!top, titleWidth: top ? top.getBoundingClientRect().width : 0, titleBottom: top ? top.getBoundingClientRect().bottom : 0, bodyTop: br.top, bodyCssTop:getComputedStyle(body).top, bodyWidth: br.width, noteTop: nr.top, noteCssTop:getComputedStyle(note).top, noteWidth: nr.width, noteHeight:nr.height, side: note.dataset.side, font: getComputedStyle(body).fontSize, lineHeight: getComputedStyle(body).lineHeight, radius: getComputedStyle(note).borderRadius, border: getComputedStyle(note).borderTopWidth, pageLeft: pr.left, pageRight: pr.right, style:p.getAttribute('style') };
    }));
    assert.equal(layout.length, 2);
    const mm = 96 / 25.4, close = (a, b) => assert.ok(Math.abs(a - b) < 1.6, `${a} != ${b}`);
    close(layout[0].titleWidth, 186 * mm);
    close(layout[0].bodyWidth, 132 * mm);
    close(layout[0].noteWidth, 48 * mm);
    assert.ok(layout[0].bodyTop >= layout[0].titleBottom, JSON.stringify(layout[0]));
    assert.ok(layout[0].noteTop >= layout[0].titleBottom, JSON.stringify(layout[0]));
    assert.equal(layout[0].font, "9.5px");
    assert.equal(layout[0].lineHeight, "17.1px");
    assert.equal(layout[0].radius, "0px");
    assert.equal(layout[0].border, "0px");
    assert.ok(layout[1].noteHeight > 800);
    layout.forEach((v, i) => assert.equal(v.side, concept.nums[i] % 2 ? "right" : "left"));
    const nativeNote = await browser.newPage();
    const nativeNoteCss = await page.evaluate(() => BKCSS);
    await nativeNote.setContent(`<style>${nativeNoteCss}</style><div class="bkdoc">${concept.note}</div>`, { waitUntil: "domcontentloaded" });
    const noteLayout = await nativeNote.locator(".ntp.lined").evaluate((note) => ({
      count: note.querySelectorAll(".ntb").length,
      size: getComputedStyle(note.querySelector(".ntb")).backgroundSize,
      label: note.querySelector(".nth").textContent,
    }));
    assert.equal(noteLayout.count, 1);
    assert.match(noteLayout.size, /^100% 24\.9\d+px$/);
    assert.match(noteLayout.label, /NOTE 01 \/ 10/);
    await nativeNote.close();
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
