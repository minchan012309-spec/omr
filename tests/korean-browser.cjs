const assert = require("node:assert/strict"),
  fs = require("node:fs");
const { chromium, browserOptions } = require("./runtime.cjs");
(async () => {
  const b = await chromium.launch(browserOptions());
  const p = await b.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  p.on("pageerror", (e) => errors.push(e.message));
  await p.route("**/*.supabase.co/**", (r) =>
    r.fulfill({ status: 404, contentType: "application/json", body: "{}" }),
  );
  try {
    await p.goto(
      (process.env.BASE || "http://127.0.0.1:8765").replace(/\/$/, "") +
        "/index.html?app=1",
    );
    await p.waitForTimeout(2000);
    await p.evaluate(async () => {
      sess = {
        access_token: "fixture",
        user: { id: "test-korean", email: "fixture@example.invalid" },
      };
      await setSubject("hl");
      await bkLoad();
      tab = "books";
      BKV = { v: "shelf", id: null };
      await bkShow();
    });
    await p
      .getByRole("button", { name: "국어 원고 편집", exact: true })
      .click();
    await p.locator("#ko-title").waitFor();
    await p.locator("#ko-title").fill("화법과 언어 검증 교재");
    await p
      .locator("[data-ko=body]")
      .fill("**핵심** & 예문 __밑줄__\n한글과 옛한글 ᄒᆞᆫ");
    await p.locator("[data-ko=teacher]").fill("교사만 보는 지도 해설");
    await p.locator("#ko-add-kind").selectOption("question");
    await p.getByRole("button", { name: "블록 추가", exact: true }).click();
    await p.locator("[data-ko=body]").fill("다음 설명으로 적절한 것은?");
    await p
      .locator("[data-ko=choices]")
      .fill(
        "첫째 선택지\n둘째 선택지\n셋째 선택지\n넷째 선택지\n다섯째 선택지",
      );
    await p.locator("[data-ko=answer]").fill("정답은 ③, 교사용 해설");
    await p.getByRole("button", { name: "원고 저장", exact: true }).click();
    await p.waitForTimeout(350);
    let fr = p.frameLocator("#ko-preview");
    await fr.getByText("다음 설명으로 적절한 것은?", { exact: true }).waitFor();
    assert.equal(
      await fr.getByText("교사만 보는 지도 해설", { exact: true }).count(),
      0,
    );
    assert.equal(
      await fr.getByText("정답은 ③, 교사용 해설", { exact: true }).count(),
      0,
    );
    await p.locator("#ko-edition").selectOption("teacher");
    await p.waitForTimeout(350);
    await fr.getByText("교사만 보는 지도 해설", { exact: true }).waitFor();
    await fr.getByText("정답은 ③, 교사용 해설", { exact: true }).waitFor();
    await p.screenshot({ path: "/tmp/solvi-korean-editor-desktop.png" });
    await p.setViewportSize({ width: 390, height: 844 });
    await p.evaluate(() => KoreanEditor.open());
    assert.ok(
      await p.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    );
    await p.screenshot({ path: "/tmp/solvi-korean-editor-mobile.png" });
    const docs = await p.evaluate(() => {
      const raw = JSON.parse(
        localStorage.getItem(
          "solvi_korean_editor_v1:t:fixture@example.invalid",
        ),
      );
      if (!raw) throw new Error("Saved manuscript missing");
      return ["student", "teacher"].map((v) =>
        KoreanEditor.render(raw, v, location.origin + "/"),
      );
    });
    const pdf = await b.newPage();
    for (let i = 0; i < 2; i++) {
      await pdf.setContent(docs[i]);
      await pdf.evaluate(() => document.fonts.ready);
      await pdf.pdf({
        path: "/tmp/solvi-korean-" + (i ? "teacher" : "student") + ".pdf",
        format: "A4",
        printBackground: true,
        preferCSSPageSize: true,
      });
      assert.ok(
        fs.statSync("/tmp/solvi-korean-" + (i ? "teacher" : "student") + ".pdf")
          .size > 10000,
      );
    }
    await pdf.close();
    await p.getByRole("button", { name: "교재함", exact: true }).click();
    await p
      .getByRole("button", { name: "국어 원고 편집", exact: true })
      .waitFor();
    await p.evaluate(() => {
      OPSUI.user = "test-korean";
      OPSUI.access = {
        role: "staff",
        operations: true,
        billing: true,
        learning: false,
        manage: false,
      };
      nav();
    });
    assert.ok(
      !(await p.evaluate(() => navAllTabs().map((x) => x[0]))).includes(
        "books",
      ),
    );
    assert.ok(
      (await p.evaluate(() => navAllTabs().map((x) => x[0]))).includes("fee"),
    );
    assert.deepEqual(errors, []);
    console.log(
      "PASS Korean editor save, student/teacher separation, A4 PDFs, desktop/mobile and role navigation",
    );
  } finally {
    await b.close();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
