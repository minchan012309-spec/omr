/* Shared business rules. No network, DOM or personal data persistence. */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.AcademyCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  function monthRange(ym) {
    if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(ym))
      throw new Error("올바른 월을 선택해 주세요");
    const [y, m] = ym.split("-").map(Number);
    if (y < 1900 || y > 9998) throw new Error("날짜 범위를 확인해 주세요");
    return {
      from: ym + "-01",
      to: ym + "-" + new Date(Date.UTC(y, m, 0)).getUTCDate(),
    };
  }
  function nextDue(day, repeat, anchor) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(day))
      throw new Error("날짜를 확인해 주세요");
    const d = new Date(day + "T00:00:00Z");
    if (!Number.isFinite(+d) || d.toISOString().slice(0, 10) !== day)
      throw new Error("날짜를 확인해 주세요");
    if (repeat === "monthly") {
      const dom = anchor || d.getUTCDate();
      d.setUTCDate(1);
      d.setUTCMonth(d.getUTCMonth() + 1);
      d.setUTCDate(
        Math.min(
          dom,
          new Date(
            Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 0),
          ).getUTCDate(),
        ),
      );
    } else if (repeat === "daily" || repeat === "weekly")
      d.setUTCDate(d.getUTCDate() + (repeat === "daily" ? 1 : 7));
    else return null;
    return d.toISOString().slice(0, 10);
  }
  const time = (t) => {
    if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(t || ""))
      throw new Error("수업 시간을 확인해 주세요");
    const [h, m] = t.split(":").map(Number);
    return h * 60 + m;
  };
  function validateSchedule(sched) {
    if (!Array.isArray(sched)) throw new Error("요일과 시간을 확인해 주세요");
    sched.forEach((t) => {
      if (
        !Number.isInteger(+t.d) ||
        +t.d < 1 ||
        +t.d > 7 ||
        time(t.s) >= time(t.e)
      )
        throw new Error("종료 시간은 시작 시간보다 늦어야 해요");
    });
    for (let i = 0; i < sched.length; i++)
      for (let j = i + 1; j < sched.length; j++)
        if (
          +sched[i].d === +sched[j].d &&
          time(sched[i].s) < time(sched[j].e) &&
          time(sched[j].s) < time(sched[i].e)
        )
          throw new Error("반 안에서 겹치는 수업 시간이 있어요");
    return sched;
  }
  function scheduleConflicts(candidate, classes) {
    validateSchedule(candidate.sched || []);
    const out = [];
    (classes || [])
      .filter(
        (c) => c.active !== false && String(c.id) !== String(candidate.id),
      )
      .forEach((c) => {
        const room =
            candidate.room &&
            candidate.room.trim() === String(c.room || "").trim(),
          teacher =
            candidate.teacher &&
            candidate.teacher.trim() === String(c.teacher || "").trim();
        if (!room && !teacher) return;
        (candidate.sched || []).forEach((a) =>
          (c.sched || []).forEach((b) => {
            try {
              if (
                +a.d === +b.d &&
                time(a.s) < time(b.e) &&
                time(b.s) < time(a.e)
              )
                out.push({
                  classId: c.id,
                  name: c.name,
                  day: +a.d,
                  start: a.s,
                  end: a.e,
                  room: !!room,
                  teacher: !!teacher,
                });
            } catch (e) {
              /* legacy incomplete schedules are surfaced in their editor */
            }
          }),
        );
      });
    return out;
  }
  function datedConflicts(candidate, classes, changes) {
    if (candidate.kind !== "대체") return [];
    const start = Date.parse(candidate.starts_at),
      end = Date.parse(candidate.ends_at);
    if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start)
      throw new Error("대체수업 시간을 확인해 주세요");
    const kstDay = (t) => new Date(t + 9 * 36e5).toISOString().slice(0, 10);
    const day = kstDay(start);
    if (kstDay(end) !== day)
      throw new Error("대체수업은 같은 날에 시작하고 끝나야 해요");
    const cls = (classes || []).filter((c) => c.active !== false);
    const current =
      cls.find((c) => String(c.id) === String(candidate.class_id)) || {};
    const room = String(candidate.room || current.room || "").trim();
    const teacher = String(candidate.teacher || current.teacher || "").trim();
    const edits = (changes || []).filter(
      (c) => !candidate.id || String(c.id) !== String(candidate.id),
    );
    const lessons = [];
    const dow = new Date(day + "T00:00:00Z").getUTCDay() || 7;
    cls.forEach((c) => {
      const omitted =
        (String(c.id) === String(candidate.class_id) &&
          candidate.on_date === day) ||
        edits.some(
          (x) => String(x.class_id) === String(c.id) && x.on_date === day,
        );
      if (!omitted)
        (c.sched || [])
          .filter((t) => +t.d === dow)
          .forEach((t) => {
            const a = Date.parse(day + "T" + t.s + ":00+09:00"),
              b = Date.parse(day + "T" + t.e + ":00+09:00");
            if (Number.isFinite(a) && Number.isFinite(b))
              lessons.push({
                c,
                start: a,
                end: b,
                room: c.room,
                teacher: c.teacher,
              });
          });
    });
    edits
      .filter((x) => x.kind === "대체")
      .forEach((x) => {
        const c = cls.find((c) => String(c.id) === String(x.class_id));
        if (c)
          lessons.push({
            c,
            start: Date.parse(x.starts_at),
            end: Date.parse(x.ends_at),
            room: x.room || c.room,
            teacher: x.teacher || c.teacher,
          });
      });
    return lessons
      .filter(
        (x) =>
          start < x.end &&
          x.start < end &&
          ((room && room === String(x.room || "").trim()) ||
            (teacher && teacher === String(x.teacher || "").trim())),
      )
      .map((x) => ({
        classId: x.c.id,
        name: x.c.name,
        room: room === x.room,
        teacher: teacher === x.teacher,
      }));
  }
  function csvCell(value) {
    let v = String(value == null ? "" : value);
    if (/^[\s\u0000-\u001f]*[=+@-]/.test(v) || /^[\t\r\n]/.test(v)) v = "'" + v;
    return '"' + v.replace(/"/g, '""') + '"';
  }
  function money(v) {
    if (v == null || String(v).trim() === "")
      throw new Error("금액을 입력해 주세요");
    const n = Number(v);
    if (!Number.isInteger(n) || n < 0 || n > 2147483647)
      throw new Error("금액은 0원 이상 정수로 입력해 주세요");
    return n;
  }
  function learningSummary(attempts, byCode) {
    const rows = [],
      types = {};
    let answered = 0,
      correct = 0;
    (attempts || [])
      .slice()
      .sort((a, b) => (a.t || 0) - (b.t || 0))
      .forEach((a) => {
        let n = 0,
          c = 0;
        const items = Array.isArray(a.items) ? a.items : [];
        items.forEach((i) => {
          if (!i || typeof i !== "object") return;
          const ok = i.r !== undefined ? i.r : i.ok;
          if (ok !== 0 && ok !== 1 && ok !== false && ok !== true) return;
          n++;
          c += ok ? 1 : 0;
          const q = (byCode || {})[i.c || i.code] || {},
            t = q.type || i.type || "유형 미분류";
          const x = types[t] || (types[t] = { type: t, total: 0, correct: 0 });
          x.total++;
          x.correct += ok ? 1 : 0;
        });
        if (n)
          rows.push({
            t: a.t,
            total: n,
            correct: c,
            rate: Math.round((c / n) * 100),
          });
        answered += n;
        correct += c;
      });
    return {
      answered,
      correct,
      rate: answered ? Math.round((correct / answered) * 100) : null,
      trend: rows,
      weak: Object.values(types)
        .map((t) => ({ ...t, rate: Math.round((t.correct / t.total) * 100) }))
        .sort((a, b) => a.rate - b.rate || b.total - a.total),
    };
  }
  return {
    monthRange,
    nextDue,
    validateSchedule,
    scheduleConflicts,
    datedConflicts,
    csvCell,
    money,
    learningSummary,
  };
});
