const { test } = require("node:test");
const assert = require("node:assert/strict");
let C;
try {
  C = require("../lib/academy-core.js");
} catch (e) {
  C = {};
}
test("month bounds support leap years and reject invalid months", () => {
  assert.deepEqual(C.monthRange("2024-02"), {
    from: "2024-02-01",
    to: "2024-02-29",
  });
  assert.deepEqual(C.monthRange("2026-04"), {
    from: "2026-04-01",
    to: "2026-04-30",
  });
  assert.throws(() => C.monthRange("2026-13"));
});
test("monthly repeat preserves anchored billing day after February", () => {
  assert.equal(C.nextDue("2026-01-31", "monthly", 31), "2026-02-28");
  assert.equal(C.nextDue("2026-02-28", "monthly", 31), "2026-03-31");
  assert.equal(C.nextDue("2026-12-31", "weekly"), "2027-01-07");
});
test("schedule conflict detects same room or teacher, ignores adjacent lessons", () => {
  const classes = [
    {
      id: 1,
      name: "A",
      room: "101",
      teacher: "김",
      active: true,
      sched: [{ d: 1, s: "18:00", e: "20:00" }],
    },
  ];
  assert.equal(
    C.scheduleConflicts(
      {
        id: 2,
        room: "101",
        teacher: "이",
        sched: [{ d: 1, s: "19:00", e: "21:00" }],
      },
      classes,
    ).length,
    1,
  );
  assert.equal(
    C.scheduleConflicts(
      {
        id: 2,
        room: "102",
        teacher: "김",
        sched: [{ d: 1, s: "19:00", e: "21:00" }],
      },
      classes,
    ).length,
    1,
  );
  assert.equal(
    C.scheduleConflicts(
      {
        id: 2,
        room: "101",
        teacher: "김",
        sched: [{ d: 1, s: "20:00", e: "21:00" }],
      },
      classes,
    ).length,
    0,
  );
  assert.throws(() => C.validateSchedule([{ d: 1, s: "20:00", e: "18:00" }]));
  assert.throws(() => C.validateSchedule([{ d: 8, s: "18:00", e: "20:00" }]));
});
test("CSV escapes formulas including leading whitespace and tabs", () => {
  assert.equal(C.csvCell('=HYPERLINK("x")'), '"\'=HYPERLINK(""x"")"');
  assert.equal(C.csvCell("  +cmd"), '"\'  +cmd"');
  assert.equal(C.csvCell("김,학생"), '"김,학생"');
  assert.equal(C.csvCell(123), '"123"');
});
test("money rejects fractions, negatives, nonfinite and PostgreSQL integer overflow", () => {
  assert.equal(C.money("120000"), 120000);
  for (const v of [-1, 2.5, NaN, Infinity, "", "1e30"])
    assert.throws(() => C.money(v));
});
test("learning report counts actual graded items and weak types without inventing scores", () => {
  const r = C.learningSummary(
    [
      {
        t: 2,
        items: [
          { c: "a", r: 1 },
          { c: "b", r: 0 },
          { c: "c", r: null },
        ],
      },
      { t: 1, items: [{ c: "d", r: 0 }] },
    ],
    { a: { type: "형태소" }, b: { type: "음운" }, d: { type: "음운" } },
  );
  assert.equal(r.answered, 3);
  assert.equal(r.correct, 1);
  assert.equal(r.rate, 33);
  assert.equal(r.weak[0].type, "음운");
  assert.equal(C.learningSummary([]).rate, null);
});

test("learning report skips malformed legacy/student items", () => {
  const r = C.learningSummary([{ items: [null, 7, "x", { c: "a", r: 1 }] }]);
  assert.equal(r.answered, 1);
  assert.equal(r.correct, 1);
});

test("dated replacement conflicts consider moved lessons and cancellations", () => {
  const cls = [
    {
      id: 1,
      name: "A",
      room: "101",
      teacher: "김",
      active: true,
      sched: [{ d: 1, s: "18:00", e: "20:00" }],
    },
    { id: 2, name: "B", room: "102", teacher: "이", active: true, sched: [] },
  ];
  const change = {
    id: 5,
    class_id: 1,
    on_date: "2026-12-07",
    kind: "대체",
    starts_at: "2026-12-06T09:00:00Z",
    ends_at: "2026-12-06T11:00:00Z",
    room: "101",
  };
  const candidate = {
    class_id: 2,
    on_date: "2026-12-08",
    kind: "대체",
    starts_at: "2026-12-06T10:00:00Z",
    ends_at: "2026-12-06T12:00:00Z",
    room: "101",
  };
  assert.equal(C.datedConflicts(candidate, cls, [change]).length, 1);
  assert.equal(
    C.datedConflicts(
      {
        ...candidate,
        starts_at: "2026-12-14T09:00:00Z",
        ends_at: "2026-12-14T11:00:00Z",
      },
      cls,
      [{ class_id: 1, on_date: "2026-12-14", kind: "휴강" }],
    ).length,
    0,
  );
});
