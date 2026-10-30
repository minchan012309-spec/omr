/* 앱 핵심 화면의 실제 브라우저 행동 회귀: 로그인 역할 탭 · entry-mode · 학습지 만들기 · 취약 유형 · 학생 목록 · 공통(글꼴 · 다크 · 동작 줄이기 · 서비스 워커).
   Supabase 는 가짜 응답으로만 대신한다(실서버 · 실데이터 없음). 학생 이름과 기록은 시험용 예시다.
   Run with BASE=http://127.0.0.1:8765 node tests/app-ui.cjs */
const assert = require("node:assert/strict");
const { chromium, browserOptions } = require("./runtime.cjs");
const BASE = (process.env.BASE || "http://127.0.0.1:8765").replace(/\/$/, "");
const APP = BASE + "/index.html?app=1";
const SESS = { access_token: "test-token", refresh_token: "test-refresh", user: { id: "u-test", email: "teacher@example.com" } };
const STUDENTS = [
  { id: "s1", name: "가학생", grade: "고2 1반", memo: "", t: 1, login: "ga01" },
  { id: "s2", name: "나학생", grade: "고2 2반", memo: "", t: 2, login: null },
];
const day = 864e5, now = Date.now();
/* 가학생: 연소 엔탈피 정의 0/3, 발열·흡열 3/3 · 나학생: 반응 속도식 0/2, 연소 엔탈피 정의 2/2 */
const HIST = [
  { t: now - 3 * day, set: "mc", sub: "me", sid: "s1", items: [{ c: "Q31-032", r: 0 }, { c: "Q31-041", r: 0 }, { c: "Q31-001", r: 1 }] },
  { t: now - 2 * day, set: "mc", sub: "me", sid: "s1", items: [{ c: "Q31-032", r: 0 }, { c: "Q31-001", r: 1 }, { c: "Q31-001", r: 1 }] },
  { t: now - 1 * day, set: "mc", sub: "me", sid: "s2", items: [{ c: "Q41-056", r: 0 }, { c: "Q41-056", r: 0 }, { c: "Q31-032", r: 1 }, { c: "Q31-041", r: 1 }] },
];
const EMOJI = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B50}]/u;

async function newApp(browser, { width = 1440, height = 900, session = false, data = false, hash = "", colorScheme = "light", reducedMotion = "no-preference", students = STUDENTS } = {}) {
  const context = await browser.newContext({ viewport: { width, height }, serviceWorkers: "block", colorScheme, reducedMotion, hasTouch: width < 800 });
  const calls = [];
  await context.route(/supabase\.co/, (route) => {
    const req = route.request(), u = new URL(req.url());
    calls.push({ path: u.pathname, method: req.method(), body: req.postData() });
    if (u.pathname.endsWith("/auth/v1/token")) return route.fulfill({ json: SESS });
    if (u.pathname.endsWith("/rest/v1/students") && req.method() === "GET") return route.fulfill({ json: students });
    if (/\/rpc\/(st_login|pa_login)$/.test(u.pathname)) return route.fulfill({ json: null });
    if (u.pathname.endsWith("/rpc/ops_access")) return route.fulfill({ json: { role: "owner", operations: true, billing: true, learning: true, manage: true } });
    return route.fulfill({ json: [] });
  });
  await context.route(/jsdelivr|googleapis|gstatic|cdnjs/, (r) => r.abort());
  await context.addInitScript(({ session, data, SESS, STUDENTS, HIST }) => {
    if (sessionStorage.getItem("__seeded")) return;
    sessionStorage.setItem("__seeded", "1");
    localStorage.clear();
    if (session) localStorage.setItem("omr_sess_v1", JSON.stringify(SESS));
    if (data) {
      localStorage.setItem("omr_stu_v1", JSON.stringify(STUDENTS));
      localStorage.setItem("omr_hist_v1", JSON.stringify(HIST));
    }
  }, { session, data, SESS, STUDENTS, HIST });
  const page = await context.newPage();
  const errors = [], dialogs = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("dialog", async (d) => {
    dialogs.push(d.type() + ":" + d.message());
    if (d.type() === "prompt") await d.accept("1234-5678");
    else await d.accept();
  });
  await page.goto(APP + hash);
  await page.waitForFunction(() => typeof render === "function" && document.querySelector("#main") && document.querySelector("#main").children.length > 0);
  await page.waitForTimeout(900);
  return { context, page, calls, errors, dialogs };
}
const entryMode = (page) => page.evaluate(() => document.documentElement.classList.contains("entry-mode"));
const shown = (page, sel) => page.evaluate((sel) => { const e = document.querySelector(sel); return !!e && getComputedStyle(e).display !== "none" && e.getClientRects().length > 0; }, sel);
const noOverflow = (page) => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1);
const selectedRole = (page) => page.evaluate(() => { const t = document.querySelector('.entry-roles [aria-selected="true"]'); return t && t.dataset.role; });
const focusedId = (page) => page.evaluate(() => document.activeElement && document.activeElement.id);

(async () => {
  const browser = await chromium.launch(browserOptions());
  let failed = 0;
  const check = async (name, fn) => {
    try {
      await fn();
      console.log("PASS", name);
    } catch (e) {
      failed++;
      console.error("FAIL", name, "\n  ", e.message.split("\n")[0]);
    }
  };
  try {
    /* ───────── 로그인 화면 ───────── */
    for (const width of [1440, 390]) {
      const { context, page, calls, errors, dialogs } = await newApp(browser, { width, height: width < 800 ? 844 : 900 });
      const tag = "login " + width + "px";
      await page.waitForSelector("#main>.entry-shell #stid");
      await check(tag + ": entry-mode hides app header · QR (toast stays usable)", async () => {
        assert.equal(await entryMode(page), true);
        assert.equal(await shown(page, "body>header"), false);
        await page.waitForTimeout(1800);
        assert.equal(await page.evaluate(() => (document.getElementById("toast") || {}).innerText || ""), "", "no app update toast over the login form");
        assert.equal(await page.evaluate(() => { const q = document.getElementById("qrFab"); return !q || getComputedStyle(q).display === "none"; }), true);
      });
      await check(tag + ": one tablist + one tabpanel, roving tabindex, labelled inputs", async () => {
        assert.equal(await page.locator(".entry-roles").count(), 1, "role tabs are not duplicated");
        assert.equal(await page.locator("#stid").count(), 1, "login form is not duplicated");
        assert.equal(await selectedRole(page), "student");
        const tabs = await page.$$eval('.entry-roles [role="tab"]', (ts) => ts.map((t) => ({ id: t.id, sel: t.getAttribute("aria-selected"), ti: t.tabIndex, ctl: t.getAttribute("aria-controls") })));
        assert.deepEqual(tabs.map((t) => t.ti), [-1, 0, -1]);
        assert.ok(tabs.every((t) => t.ctl === "stbody" && t.id));
        assert.equal(await page.getAttribute("#stbody", "role"), "tabpanel");
        assert.equal(await page.getAttribute("#stbody", "aria-labelledby"), "er-tab-student");
        assert.equal(await page.evaluate(() => [...document.querySelectorAll("#stbody input:not([type=checkbox])")].every((i) => i.labels && i.labels.length > 0)), true);
      });
      await check(tag + ": arrow · Home · End move between roles", async () => {
        await page.focus("#er-tab-student");
        await page.keyboard.press("ArrowRight");
        assert.equal(await selectedRole(page), "parent");
        assert.equal(await focusedId(page), "er-tab-parent");
        assert.equal(await page.getAttribute("#stbody", "aria-labelledby"), "er-tab-parent");
        await page.keyboard.press("ArrowRight");
        assert.equal(await selectedRole(page), "teacher", "wraps to the first tab");
        await page.keyboard.press("End");
        assert.equal(await selectedRole(page), "parent");
        await page.keyboard.press("Home");
        assert.equal(await selectedRole(page), "teacher");
        await page.keyboard.press("ArrowLeft");
        assert.equal(await selectedRole(page), "parent");
        await page.keyboard.press("ArrowLeft");
        assert.equal(await selectedRole(page), "student");
        assert.deepEqual(await page.$$eval('.entry-roles [role="tab"]', (ts) => ts.map((t) => t.tabIndex)), [-1, 0, -1]);
      });
      await check(tag + ": typed id survives a role round trip; teacher tab does not reload", async () => {
        await page.evaluate(() => { window.__noReload = 1; });
        await page.fill("#stid", "ga01");
        await page.click("#er-tab-parent");
        assert.equal(await focusedId(page), "stid", "focus moves to the first field");
        await page.click("#er-tab-teacher");
        assert.equal(await focusedId(page), "ete");
        assert.equal(await page.locator("#ete").count(), 1);
        await page.click("#er-tab-student");
        assert.equal(await page.inputValue("#stid"), "ga01");
        assert.equal(await page.evaluate(() => window.__noReload), 1, "no full page reload");
      });
      await check(tag + ": Enter submits student and parent logins", async () => {
        await page.fill("#stid", "ga01");
        await page.fill("#stpw", "pw1234");
        await page.press("#stpw", "Enter");
        await page.waitForTimeout(400);
        assert.ok(calls.some((c) => c.path.endsWith("/rpc/st_login") && JSON.parse(c.body).p_login === "ga01"));
        await page.click("#er-tab-parent");
        await page.fill("#stid", "pa01");
        await page.fill("#stpw", "pw1234");
        await page.press("#stid", "Enter");
        await page.waitForTimeout(400);
        assert.ok(calls.some((c) => c.path.endsWith("/rpc/pa_login") && JSON.parse(c.body).p_login === "pa01"));
        assert.equal(await entryMode(page), true, "failed login stays on the login screen");
      });
      await check(tag + ": number grading entry asks for the number then for login", async () => {
        dialogs.length = 0;
        await page.getByRole("button", { name: "번호로 바로 채점" }).click();
        await page.waitForTimeout(400);
        assert.match(dialogs.join("|"), /prompt:학습지 번호/);
        /* 앱의 alert 는 토스트로 바뀌어 있다: 로그인 화면에서도 안내가 보여야 한다 */
        assert.match(await page.locator("#toast").innerText(), /로그인/);
        assert.equal(await shown(page, "#toast"), true);
        assert.equal(await entryMode(page), true);
      });
      await check(tag + ": tabs fit, no page overflow, nothing covers the form", async () => {
        assert.equal(await noOverflow(page), true);
        assert.equal(await page.$$eval('.entry-roles [role="tab"]', (ts) => ts.every((t) => t.scrollWidth <= t.clientWidth + 1 && t.getBoundingClientRect().right <= innerWidth)), true);
        const covered = await page.evaluate(() => [...document.querySelectorAll(".entry-card input, .entry-card button")].filter((e) => e.getClientRects().length).some((e) => {
          const r = e.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
          if (y < 0 || y > innerHeight) return false;
          const top = document.elementFromPoint(x, y);
          return top && !e.contains(top) && !top.contains(e);
        }));
        assert.equal(covered, false);
      });
      await check(tag + ": teacher login clears entry-mode, header and toast come back", async () => {
        await page.click("#er-tab-teacher");
        await page.fill("#ete", "teacher@example.com");
        await page.fill("#etp", "secret12");
        await page.press("#etp", "Enter");
        await page.waitForFunction(() => !document.documentElement.classList.contains("entry-mode"), null, { timeout: 8000 });
        await page.waitForTimeout(500);
        assert.equal(await shown(page, "body>header"), true);
        await page.evaluate(() => toast("저장했어요"));
        assert.equal(await page.evaluate(() => getComputedStyle(document.getElementById("toast")).display !== "none"), true);
        assert.equal(await page.evaluate(() => { const q = document.getElementById("qrFab"); return !q || !document.documentElement.classList.contains("entry-mode"); }), true);
      });
      await check(tag + ": back · forward keep the right chrome; logout returns to login", async () => {
        await page.evaluate(() => navGo("stu"));
        await page.waitForTimeout(300);
        await page.evaluate(() => navGo("weak"));
        await page.waitForTimeout(300);
        await page.goBack();
        await page.waitForFunction(() => tab === "stu", null, { timeout: 5000 });
        assert.equal(await entryMode(page), false);
        await page.goForward();
        await page.waitForFunction(() => tab === "weak", null, { timeout: 5000 });
        assert.equal(await entryMode(page), false);
        await page.evaluate(() => logout());
        await page.waitForFunction(() => document.documentElement.classList.contains("entry-mode"), null, { timeout: 8000 });
        assert.equal(await shown(page, "body>header"), false);
        await page.goBack();
        await page.waitForTimeout(500);
        assert.equal(await entryMode(page), !!(await page.$("#main>.entry-shell")), "chrome follows the screen after back");
      });
      assert.deepEqual(errors, [], tag + " page errors");
      await context.close();
    }

    await check("session auto-restore opens the app without entry-mode", async () => {
      const { context, page, errors } = await newApp(browser, { session: true, data: true });
      assert.equal(await entryMode(page), false);
      assert.equal(await shown(page, "body>header"), true);
      assert.deepEqual(errors, []);
      await context.close();
    });
    await check("URL hash #login opens the teacher tab, #student the student tab", async () => {
      let a = await newApp(browser, { hash: "#login" });
      await a.page.waitForTimeout(500);
      assert.equal(await selectedRole(a.page), "teacher");
      assert.equal(await focusedId(a.page), "ete");
      assert.equal(await entryMode(a.page), true);
      await a.context.close();
      a = await newApp(browser, { hash: "#student" });
      await a.page.waitForTimeout(500);
      assert.equal(await selectedRole(a.page), "student");
      await a.context.close();
    });

    /* ───────── 학습지 만들기 · 취약 유형 · 학생 목록 (선생님 로그인 + 예시 데이터) ───────── */
    for (const width of [1440, 390]) {
      const { context, page, errors } = await newApp(browser, { width, height: width < 800 ? 844 : 900, session: true, data: true });
      const tag = width + "px";
      /* 학습지 만들기 시작 화면은 build 탭에서 아직 고른 유형이 없을 때 나온다 */
      const go = async (k) => { await page.evaluate((k) => { if (k === "start") { BGO = 0; resetW(); tab = "build"; } else tab = k; render(); }, k); await page.waitForTimeout(250); };

      await check(tag + " start: recommended starting points, one title, builder entries", async () => {
        await go("start");
        assert.ok((await page.locator(".stp-k").count()) >= 8);
        assert.equal(await page.locator("#main h1, #main h2").filter({ hasText: "학습지 만들기" }).count(), 1, "title is not duplicated");
        await page.locator(".stp-k", { hasText: "유형별" }).click();
        await page.waitForTimeout(300);
        assert.equal(await page.evaluate(() => tab), "build", "bGo opens the builder");
        assert.equal(await shown(page, "#mkw"), true, "bGo opens the existing builder window");
        await page.evaluate(() => bwClose());
        await go("start");
        await page.locator(".stp-k", { hasText: "취약 유형 자동" }).click();
        await page.waitForTimeout(600);
        assert.equal(await page.evaluate(() => tab), "build");
        assert.ok(await page.evaluate(() => W.sel.size > 0), "weak recommendation selects types");
        assert.match(await page.locator("#mkw .bwsum").innerText(), /[1-9]\d*\s*유형 · \d+\s*문항/, "selection summary");
        const next = page.locator("#mkw button", { hasText: "다음 · 문항 확인" });
        assert.equal(await next.isEnabled(), true);
        const nb = await next.boundingBox();
        assert.ok(nb && nb.y + nb.height <= (width < 800 ? 844 : 900) + 1, "builder action (bottom summary) stays on screen");
        await page.evaluate(() => { window.__made = 0; window.makeNow = () => { window.__made = 1; }; bdGo(); });
        assert.equal(await page.evaluate(() => window.__made), 1, "bdGo makes the worksheet from the selection");
        await page.evaluate(() => bwClose());
        assert.equal(await noOverflow(page), true);
      });

      await check(tag + " weak: scope question, real weakest type, select · make · practice", async () => {
        await page.evaluate(() => { CUR_S = ""; SCOPE = "*"; tab = "weak"; resetW(); render(); });
        await page.waitForTimeout(300);
        assert.equal(await page.locator(".wk-q").innerText(), "전체 학생이 가장 어려워하는 유형은?");
        assert.match(await page.locator(".wk-a").innerText(), /반응 속도식.*정답률 0% · 2문항/);
        await page.evaluate(() => setScope("c:고2 1반"));
        await page.waitForTimeout(400);
        assert.match(await page.locator(".wk-q").innerText(), /고2 1반 학생들이/);
        assert.match(await page.locator(".wk-a").innerText(), /연소·생성·분해·용해·기화 엔탈피의 정의.*정답률 0% · 3문항/);
        await page.evaluate(() => { setStu("s2"); render(); });
        await page.waitForTimeout(400);
        assert.match(await page.locator(".wk-q").innerText(), /나학생 학생이/);
        assert.match(await page.locator(".wk-a").innerText(), /반응 속도식/);
        const card = page.locator(".tc").first();
        await card.click();
        assert.equal(await page.evaluate(() => W.sel.size), 1, "type selected");
        await page.locator(".tc").first().click();
        assert.equal(await page.evaluate(() => W.sel.size), 0, "type deselected");
        await page.locator(".tc").first().click();
        await page.evaluate(() => { window.__pr = null; window.practice = (codes) => { window.__pr = codes.length; }; });
        /* 넓은 화면은 오른쪽 요약 카드, 휴대폰은 하단 고정 요약에서 누른다 */
        const sum = width < 800 ? ".wkstick" : ".wksum";
        await page.locator(sum + " button", { hasText: "바로 풀기" }).click();
        await page.waitForFunction(() => window.__pr !== null, null, { timeout: 8000 });
        assert.ok(await page.evaluate(() => window.__pr > 0), "quickPractice picks questions");
        if (width < 800) assert.equal(await shown(page, ".wkstick"), true, "mobile bottom summary");
        assert.equal(await noOverflow(page), true);
        await page.locator(sum + " button", { hasText: "학습지 만들기" }).click();
        await page.waitForTimeout(300);
        assert.equal(await page.evaluate(() => tab), "build");
      });

      await check(tag + " students: rows, search, class filter, detail, mobile keeps core info", async () => {
        await page.evaluate(() => { CUR_S = ""; SQ = ""; SGR = ""; STAB = "list"; tab = "stu"; render(); });
        await page.waitForTimeout(300);
        assert.equal(await page.locator(".stx-row:not(.stx-head)").count(), 2);
        await page.fill('.stx-tool input[type="search"]', "가학생");
        await page.waitForTimeout(500);
        assert.equal(await page.locator(".stx-row:not(.stx-head)").count(), 1);
        await page.evaluate(() => { SQ = ""; stuView(); });
        await page.locator('.clsb .chp[data-c="고2 2반"]').click();
        await page.waitForTimeout(200);
        assert.deepEqual(await page.$$eval(".stx-row:not(.stx-head) .stx-name b", (b) => b.map((x) => x.textContent)), ["나학생"]);
        await page.evaluate(() => { SGR = ""; stuView(); });
        const info = await page.$$eval(".stx-row:not(.stx-head)", (rows) => rows.map((r) => {
          const vis = (sel) => { const e = r.querySelector(sel); if (!e) return false; const b = e.getBoundingClientRect(); return getComputedStyle(e).display !== "none" && b.width > 0 && b.left >= 0 && b.right <= innerWidth + 1; };
          return { name: vis(".stx-name b"), cls: vis(".stx-name small"), acc: vis(".stx-acc"), last: vis(".stx-last"), risk: vis(".stx-risk"), weak: vis(".stx-weak"), detail: vis(".stx-act > button"), more: vis(".stx-more > summary") };
        }));
        for (const r of info) assert.deepEqual(r, { name: true, cls: true, acc: true, last: true, risk: true, weak: true, detail: true, more: true });
        assert.match(await page.locator(".stx-row:not(.stx-head)").first().locator(".stx-acc").innerText(), /\d+%/);
        assert.equal(await noOverflow(page), true);
        await page.locator(".stx-row:not(.stx-head)").first().locator(".stx-act > button").click();
        await page.waitForTimeout(300);
        assert.equal(await page.evaluate(() => [tab, CUR_S].join()), "weak,s1");
      });

      await check(tag + " students: more menu keyboard, Escape, outside click, handlers kept", async () => {
        await page.evaluate(() => { CUR_S = ""; tab = "stu"; render(); });
        await page.waitForTimeout(300);
        const more = page.locator(".stx-row:not(.stx-head)").first().locator(".stx-more");
        await more.locator("summary").focus();
        await page.keyboard.press("Enter");
        await page.waitForTimeout(150);
        assert.equal(await more.evaluate((d) => d.open), true);
        assert.equal(await page.evaluate(() => document.activeElement.getAttribute("role")), "menuitem");
        const first = await page.evaluate(() => document.activeElement.textContent);
        await page.keyboard.press("ArrowDown");
        assert.notEqual(await page.evaluate(() => document.activeElement.textContent), first);
        await page.keyboard.press("End");
        assert.equal(await page.evaluate(() => document.activeElement.textContent), "삭제");
        assert.equal(await page.evaluate(() => document.activeElement.classList.contains("dg")), true, "delete is set apart");
        const box = await more.locator(".stx-menu").boundingBox();
        assert.ok(box.x >= 0 && box.x + box.width <= (width) + 1, "menu stays on screen");
        await page.keyboard.press("Escape");
        assert.equal(await more.evaluate((d) => d.open), false);
        assert.equal(await page.evaluate(() => document.activeElement.tagName), "SUMMARY");
        await more.locator("summary").click();
        assert.equal(await more.evaluate((d) => d.open), true);
        await page.mouse.click(5, 5);
        assert.equal(await more.evaluate((d) => d.open), false, "outside click closes");
        const handlers = await more.locator('[role="menuitem"]').evaluateAll((b) => b.map((x) => x.getAttribute("onclick")).join(" "));
        for (const fn of ["repOpen", "attOpenStu", "issueLogin", "revokeLogin", "paOpen", "previewStudent", "stuEdit", "stuDel"]) assert.match(handlers, new RegExp(fn + "\\("), fn);
        assert.equal(await more.locator("summary").getAttribute("aria-label"), "가학생 더보기");
      });

      await check(tag + " students: empty state", async () => {
        await page.evaluate(() => { window.__stu = STU; STU = []; stuView(); });
        assert.equal(await page.locator(".stx .ui-empty").count(), 1);
        await page.evaluate(() => { STU = window.__stu; stuView(); });
      });

      await check(tag + " common: Pretendard app UI, no YetHangul, no backdrop-filter, no decorative emoji", async () => {
        for (const k of ["stu", "weak", "start"]) {
          await go(k);
          const r = await page.evaluate(() => {
            const els = [document.body, ...document.querySelectorAll("body>header, body>header *, #main, #main *")];
            return {
              yet: els.filter((e) => /YetHangul|SolviSymbols/.test(getComputedStyle(e).fontFamily)).length,
              notPret: els.filter((e) => !/^"?Pretendard/.test(getComputedStyle(e).fontFamily)).map((e) => e.tagName + "." + e.className).slice(0, 3),
              blur: els.filter((e) => getComputedStyle(e).backdropFilter !== "none").length,
              text: document.querySelector("#main").innerText,
            };
          });
          assert.equal(r.yet, 0, k + " YetHangul/SolviSymbols in app UI");
          assert.deepEqual(r.notPret, [], k + " app UI font");
          assert.equal(r.blur, 0, k + " backdrop-filter");
          assert.equal(EMOJI.test(r.text), false, k + " decorative emoji: " + (r.text.match(EMOJI) || [])[0]);
        }
      });
      assert.deepEqual(errors, [], tag + " page errors");
      await context.close();
    }

    await check("dark mode: student list uses dark surfaces", async () => {
      const { context, page } = await newApp(browser, { session: true, data: true, colorScheme: "dark" });
      await page.evaluate(() => { tab = "stu"; render(); });
      await page.waitForTimeout(300);
      const lum = await page.evaluate(() => {
        const c = getComputedStyle(document.body).backgroundColor.match(/\d+/g).map(Number);
        const p = getComputedStyle(document.querySelector(".stx-list")).backgroundColor.match(/\d+/g).map(Number);
        return [c, p].map((x) => (x[0] * 299 + x[1] * 587 + x[2] * 114) / 1000);
      });
      assert.ok(lum[0] < 80 && lum[1] < 80, "dark body/panel " + lum);
      await context.close();
    });
    await check("reduced motion: login screen has no entrance animation", async () => {
      const { context, page } = await newApp(browser, { reducedMotion: "reduce" });
      assert.equal(await page.evaluate(() => getComputedStyle(document.querySelector(".entry-title")).animationName), "none");
      assert.equal(await page.evaluate(() => getComputedStyle(document.querySelector(".entry-card")).opacity), "1");
      await context.close();
    });
    await check("service worker precaches the versioned CSS in the new order and opens offline", async () => {
      const context = await browser.newContext({ viewport: { width: 1280, height: 800 }, serviceWorkers: "allow" });
      await context.route(/supabase\.co|jsdelivr|googleapis|gstatic|cdnjs/, (r) => r.abort());
      const page = await context.newPage();
      await page.goto(APP);
      /* 앱은 https · localhost 에서만 스스로 등록한다. 시험 서버(127.0.0.1)에서는 같은 sw.js 를 직접 등록한다 */
      await page.evaluate(async () => { await navigator.serviceWorker.register("sw.js"); await navigator.serviceWorker.ready; });
      const r = await page.evaluate(async () => {
        const v = (await caches.keys()).find((k) => /^solvi-v\d+$/.test(k));
        const keys = (await (await caches.open(v)).keys()).map((q) => new URL(q.url).pathname + new URL(q.url).search);
        const links = [...document.querySelectorAll('link[rel="stylesheet"][href^="styles/"]')].map((l) => "/" + l.getAttribute("href"));
        return { v, keys, links };
      });
      assert.deepEqual(r.links, ["/styles/tokens.css?v=3", "/styles/legacy.css?v=3", "/styles/base.css?v=3", "/styles/shell.css?v=3", "/styles/components.css?v=3", "/styles/screens.css?v=3"]);
      for (const l of r.links) assert.ok(r.keys.includes(l), "cached " + l);
      await page.reload();
      await page.waitForTimeout(800);
      await context.setOffline(true);
      await page.reload();
      await page.waitForFunction(() => typeof render === "function" && document.querySelector("#main").children.length > 0, null, { timeout: 10000 });
      assert.equal(await page.evaluate(() => getComputedStyle(document.body).fontFamily.startsWith("Pretendard")), true, "offline page uses the new CSS order");
      await context.close();
    });
  } finally {
    await browser.close();
  }
  if (failed) {
    console.error(failed + " app UI check(s) failed");
    process.exit(1);
  }
  console.log("PASS app UI behaviour");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
