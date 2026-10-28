/* Isolated browser fixtures only: no live Supabase, credentials or external requests. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const { chromium, browserOptions } = require("./runtime.cjs");
(async () => {
  const browser = await chromium.launch(browserOptions());
  try {
    const page = await browser.newPage({
      viewport: { width: 390, height: 844 },
    });
    await page.route("**/*", (r) => r.abort());
    await page.setContent(
      '<main id="main"></main><div id="cfg"><div id="cfgBox"></div></div>',
    );
    await page.addScriptTag({
      content: `var tab='admin',sess={},STUD=null,byCode={q:{type:'문법'}};var calls=[],messages=[],access={role:'owner',operations:true,billing:true,learning:true,manage:true},missing=false;var $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),cloud=()=>true,ldg=s=>s,toast=s=>messages.push(s),cfgChrome=()=>{},closeCfg=()=>$('#cfg').classList.remove('open'),confirm=()=>true,tsRaw=async()=>({}),navGo=()=>{},render=()=>{};async function rpc(n,a){calls.push({rpc:n,args:a});if(missing&&n==='ops_access')return new Response('{}',{status:404});return new Response(JSON.stringify(n==='ops_access'?access:n==='ops_monthly_bill'?{created:2}:n==='ops_complete_task'?{completed:true,next_id:3}:n==='ops_staff'?[{member_id:'member',label:'김 선생님',role:'teacher'}]:null),{status:200})}async function sb(path,o){calls.push({path,method:o?.method||'GET',body:o?.body?JSON.parse(o.body):null});let rows=[];if(path.includes('/students?'))rows=[{id:'s1',name:'가학생',status:'재원',guardian:'김보호',guardian_phone:'0101234'},{id:'s2',name:'나학생',status:'휴원'}];if(path.includes('/classes?'))rows=[{id:1,name:'국어',teacher:'김',room:'A',tuition:10000,sched:[{d:1,s:'18:00',e:'19:00'}]}];if(path.includes('/class_members?'))rows=[{class_id:1,student_id:'s1'}];if(path.includes('/attempts?'))rows=[{t:Date.now(),items:[{c:'q',r:1},{c:'q',r:0}]}];if(path.includes('/attendance?'))rows=[{student_id:'s1',day:'2026-02-28',status:'early'}];return new Response(o?.method&&o.method!=='GET'?JSON.stringify([{id:1}]):JSON.stringify(rows),{status:200})}`,
    });
    for (const f of ["lib/academy-core.js", "lazy/acad.js", "lazy/admin.js"])
      await page.addScriptTag({ content: fs.readFileSync(f, "utf8") });
    await page.evaluate(() => adminView());
    await page.evaluate(() => adSec("stu"));
    await page.getByText("가학생", { exact: true }).click();
    await page.getByRole("heading", { name: "학습", exact: true }).waitFor();
    assert.match(await page.locator("#cfgBox").innerText(), /정답률 50%/);
    assert.match(await page.locator("#cfgBox").innerText(), /김보호/);
    assert.match(await page.locator("#cfgBox").innerText(), /조퇴 1/);
    await page.evaluate(() => {
      closeCfg();
      adSec("ops");
    });
    await page.getByRole("button", { name: "＋ 업무", exact: true }).click();
    await page.locator("#ado_title").fill("월말 확인");
    await page.locator("#ado_due_on").fill("2026-01-31");
    await page.locator("#ado_repeat_kind").selectOption("monthly");
    await page.locator("#ado_save").click();
    await page.waitForFunction(() =>
      calls.some(
        (c) => c.path?.includes("ops_tasks") && c.body?.title === "월말 확인",
      ),
    );
    assert.equal(
      await page.evaluate(
        () => calls.find((c) => c.body?.title === "월말 확인").body.anchor_day,
      ),
      31,
    );
    await page.evaluate(() => adTaskDone(2));
    assert.equal(
      await page.evaluate(() =>
        calls.some((c) => c.rpc === "ops_complete_task" && c.args.p_id === 2),
      ),
      true,
    );
    await page.evaluate(() => adOpsEdit("appointment"));
    await page.locator("#ado_student_id").selectOption("s1");
    await page.locator("#ado_assignee").fill("김");
    await page.locator("#ado_starts_at").fill("2026-02-28T18:00");
    await page.locator("#ado_ends_at").fill("2026-02-28T17:00");
    await page.locator("#ado_save").click();
    assert.match(await page.evaluate(() => messages.at(-1)), /종료/);
    await page.locator("#ado_ends_at").fill("2026-02-28T19:00");
    await page.locator("#ado_save").click();
    await page.waitForFunction(() =>
      calls.some((c) => c.body?.starts_at === "2026-02-28T09:00:00.000Z"),
    );
    await page.evaluate(() => adOpsEdit("change"));
    await page.locator("#ado_class_id").selectOption("1");
    await page.locator("#ado_save").click();
    await page.waitForFunction(() =>
      calls.some(
        (c) => c.path?.includes("lesson_changes") && c.body?.kind === "휴강",
      ),
    );
    await page.evaluate(() => {
      AD.bm = "2026-02";
      adModal('<input id="adb_due" type="date" value="2026-02-28">');
      return adBillGo();
    });
    assert.equal(
      await page.evaluate(() =>
        calls.some(
          (c) =>
            c.rpc === "ops_monthly_bill" && c.args.p_month === "2026-02-01",
        ),
      ),
      true,
    );
    assert.equal(
      await page.evaluate(() =>
        calls.some((c) => c.path?.includes("/fees") && c.method === "POST"),
      ),
      false,
    );
    await page.evaluate(() => {
      AC.sec = "month";
      AC.sid = "s1";
      AC.mon = "2026-02";
      return acLoad();
    });
    assert.equal(
      await page.evaluate(() =>
        calls.some((c) => c.path?.includes("day=lte.2026-02-28")),
      ),
      true,
    );
    assert.equal(
      await page.evaluate(() =>
        calls.some((c) => c.path?.includes("2026-02-31")),
      ),
      false,
    );
    await page.evaluate(() => {
      access = {
        role: "staff",
        operations: true,
        billing: true,
        learning: false,
        manage: false,
      };
      return adLoad();
    });
    await page.evaluate(() => {
      calls = [];
      return adStuDetail("s1");
    });
    assert.equal(
      await page.evaluate(() =>
        calls.some((c) => c.path?.includes("/attempts")),
      ),
      false,
    );
    assert.equal(
      await page.getByRole("heading", { name: "학습", exact: true }).count(),
      0,
    );
    await page.evaluate(() => {
      access = {
        role: "teacher",
        operations: true,
        billing: false,
        learning: true,
        manage: false,
      };
      return adLoad();
    });
    assert.equal(
      await page.evaluate(() => adDash().includes("미납 · 기한 지남")),
      false,
    );
    await page.evaluate(() => {
      tab = "fee";
      AC.ld = 0;
      return attView();
    });
    assert.match(await page.locator("#main").innerText(), /수납 권한/);
    await page.evaluate(() => {
      access = {
        role: "owner",
        operations: true,
        billing: true,
        learning: true,
        manage: true,
      };
      return adLoad();
    });
    await page.evaluate(() => {
      adClsEdit(1);
      AD.sch = [{ d: 1, s: "19:00", e: "18:00" }];
    });
    await page.locator("#adc_name").fill("검증반");
    await page.evaluate(() => adClsSave());
    assert.match(await page.evaluate(() => messages.at(-1)), /종료/);
    await page.evaluate(() => {
      AD.sch = [{ d: 1, s: "18:30", e: "19:30" }];
      AD.cls.push({
        id: 2,
        name: "겹치는 반",
        room: "A",
        teacher: "김",
        sched: [{ d: 1, s: "18:00", e: "19:00" }],
      });
    });
    await page.evaluate(() => adClsSave());
    assert.match(await page.evaluate(() => messages.at(-1)), /겹쳐/);
    await page.evaluate(() => adOpsEdit("change"));
    await page.locator("#ado_class_id").selectOption("1");
    await page.locator("#ado_kind").selectOption("대체");
    await page.locator("#ado_starts_at").fill("2026-02-28T18:00");
    await page.locator("#ado_ends_at").fill("2026-02-28T19:00");
    await page.locator("#ado_save").click();
    await page.waitForFunction(() =>
      calls.some(
        (c) =>
          c.path?.includes("lesson_changes") &&
          c.body?.kind === "대체" &&
          c.body?.starts_at === "2026-02-28T09:00:00.000Z",
      ),
    );
    await page.evaluate(() => {
      AD.cls = [
        { id: 1, name: "대체반", room: "A", teacher: "김", sched: [] },
        {
          id: 2,
          name: "다른반",
          room: "A",
          teacher: "이",
          sched: [{ d: 6, s: "18:00", e: "19:00" }],
        },
      ];
      AD.changes = [
        {
          id: 8,
          class_id: 2,
          on_date: "2026-02-27",
          kind: "대체",
          starts_at: "2026-02-28T09:00:00.000Z",
          ends_at: "2026-02-28T10:00:00.000Z",
        },
      ];
      adOpsEdit("change");
    });
    await page.locator("#ado_class_id").selectOption("1");
    await page.locator("#ado_on_date").fill("2026-02-28");
    await page.locator("#ado_kind").selectOption("대체");
    await page.locator("#ado_starts_at").fill("2026-02-28T18:00");
    await page.locator("#ado_ends_at").fill("2026-02-28T19:00");
    await page.evaluate(() => {
      calls = [];
    });
    await page.locator("#ado_save").click();
    assert.match(await page.evaluate(() => messages.at(-1)), /겹쳐/);
    assert.equal(
      await page.evaluate(() =>
        calls.some(
          (c) => c.method === "POST" && c.path?.includes("lesson_changes"),
        ),
      ),
      false,
    );
    await page.evaluate(() => {
      AD.changes = [
        { id: 9, class_id: 2, on_date: "2026-02-28", kind: "휴강" },
      ];
    });
    await page.locator("#ado_save").click();
    await page.waitForFunction(() =>
      calls.some(
        (c) =>
          c.method === "POST" &&
          c.path?.includes("lesson_changes") &&
          c.body?.kind === "대체",
      ),
    );
    await page.evaluate(() => adStaffView());
    await page.locator("#cfgBox select").selectOption("staff");
    await page.waitForFunction(() =>
      calls.some((c) => c.rpc === "ops_set_role" && c.args.p_role === "staff"),
    );
    await page.evaluate(() => {
      tab = "admin";
      STUD = { parent: true };
      SCH.ld = 1;
      SCH.d = {
        classes: [
          {
            id: 1,
            name: "취소한정규수업",
            sched: [{ d: adDow(adDay()), s: "18:00", e: "19:00" }],
          },
        ],
        lesson_changes: [
          {
            class_id: 1,
            on_date: adDay(),
            kind: "휴강",
            class: "취소한정규수업",
            reason: "휴일",
          },
        ],
      };
      return schedView();
    });
    assert.match(
      await page.locator("#main").innerText(),
      /오늘은 수업이 없어요/,
    );
    assert.match(await page.locator("#main").innerText(), /휴일/);
    await page.evaluate(() => {
      STUD = null;
      return adStuDetail("s1");
    });
    await page.evaluate(() => {
      window.printed = "";
      window.popOpen = () => ({
        document: {
          open() {},
          write(s) {
            window.printed += s;
          },
          close() {},
        },
      });
      adLearningPrint();
    });
    assert.match(await page.evaluate(() => printed), /가학생 학생 학습 보고서/);
    assert.match(await page.evaluate(() => printed), /정답률 50%/);
    await page.evaluate(() => {
      missing = true;
      return adLoad();
    });
    assert.equal(await page.evaluate(() => AD.opsReady), false);
    assert.match(await page.evaluate(() => adBillHtml()), /sql_24_operations/);
    assert.equal(
      await page.evaluate(() => AcademyCore.csvCell("=1+1")),
      `"'=1+1"`,
    );
    await page.evaluate(() => {
      AD.q = "가";
      AD.st = "all";
      AD.sort = "name";
    });
    assert.deepEqual(
      await page.evaluate(() => adFilteredStudents().map((s) => s.id)),
      ["s1"],
    );
    await page.evaluate(() => {
      AD.stu = [{ id: "s1", name: "학생", status: "재원" }];
      AD.cls = [
        { id: 1, name: "동명반", tuition: 10000 },
        { id: 2, name: "동명반", tuition: 10000 },
      ];
      AD.mem = [
        { class_id: 1, student_id: "s1" },
        { class_id: 2, student_id: "s1" },
      ];
      AD.fees = [
        {
          student_id: "s1",
          title: "2026년 2월 동명반 수강료",
          billing_key: "2026-02:1:s1",
        },
      ];
    });
    assert.deepEqual(
      await page.evaluate(() =>
        adBillPlan("2026-02")
          .filter((x) => !x.dup)
          .map((x) => x.c.id),
      ),
      [2],
    );
    await page.evaluate(() => {
      AD.cls[0].name = "이름변경반";
    });
    assert.equal(
      await page.evaluate(
        () => adBillPlan("2026-02").find((x) => x.c.id === 1).dup,
      ),
      true,
    );
    await page.evaluate(() => {
      AD.fees = [
        {
          student_id: "s1",
          title: "2026년 2월 동명반 수강료",
          billing_key: null,
        },
      ];
    });
    assert.equal(
      await page.evaluate(
        () => adBillPlan("2026-02").find((x) => x.c.id === 2).dup,
      ),
      true,
    );
    await page.evaluate(async () => {
      await adPost("students", { name: "신규" }, 1);
      await adPatch("students", "id=eq.s1", { name: "수정" });
    });
    assert.equal(
      await page.evaluate(() =>
        calls
          .filter(
            (c) =>
              c.path?.includes("/students") &&
              ["POST", "PATCH"].includes(c.method),
          )
          .every((c) => c.path.includes("select=id,name,grade,memo")),
      ),
      true,
    );
    await page.evaluate(() => {
      AD.access = { billing: true };
      AD.accessUser = "account-a";
      AC.access = { billing: true };
      AC.accessUser = "account-a";
      sess = { user: { id: "account-b" } };
    });
    assert.equal(await page.evaluate(() => adCan("billing")), false);
    assert.equal(await page.evaluate(() => acCanBill()), false);
    console.log(
      "PASS admin isolated browser fixtures: detail, capabilities, recurring task RPC, appointment KST/validation, lesson cancellation, transactional billing, February range, CSV/filter. No live DB tested.",
    );
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
