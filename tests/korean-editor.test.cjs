const { test } = require("node:test");
const assert = require("node:assert/strict");
let K;
try {
  K = require("../lib/korean-editor.js");
} catch (e) {
  K = {};
}
const doc = {
  title: "국어 <개념>",
  layout: "kice",
  paragraphs: true,
  lines: true,
  blocks: [
    {
      kind: "passage",
      area: "문학",
      title: "작품",
      body: "첫 문단 & 의미\n둘째 문단 ᄒᆞᆫ",
      teacher: "교사 전용 메모",
    },
    {
      kind: "question",
      area: "독서",
      title: "적절한 것은?",
      body: "발문",
      box: "보기 내용",
      choices: "첫 선지\n둘째 선지",
      answer: "정답 비공개",
    },
    {
      kind: "table",
      area: "언어",
      title: "비교",
      body: "개념|예문\n음운|소리",
    },
  ],
};
test("student HTML excludes teacher answers entirely", () => {
  const h = K.render(doc, "student");
  assert.ok(!h.includes("교사 전용 메모"));
  assert.ok(!h.includes("정답 비공개"));
  assert.ok(h.includes("보기 내용"));
  assert.ok(h.includes("①"));
});
test("teacher edition includes separate explanations", () => {
  const h = K.render(doc, "teacher");
  assert.ok(h.includes("교사 전용 메모"));
  assert.ok(h.includes("정답 비공개"));
});
test("render escapes active HTML, preserves Korean, line breaks and print fonts", () => {
  const h = K.render({ ...doc, title: "<script>alert(1)</script>" }, "student");
  assert.ok(!h.includes("<script>"));
  assert.ok(h.includes("&lt;script&gt;"));
  assert.ok(h.includes("ᄒᆞᆫ"));
  assert.ok(h.includes("@page"));
  assert.ok(h.includes("KoPubDotum"));
  assert.ok(h.includes("<table"));
  assert.ok(h.includes("둘째 문단"));
});
test("import validates structure, limits and enumerations", () => {
  assert.throws(() => K.validate({ title: "x", blocks: [{ kind: "script" }] }));
  assert.throws(() =>
    K.validate({ ...doc, blocks: new Array(201).fill(doc.blocks[0]) }),
  );
  assert.equal(K.validate(doc).blocks.length, 3);
});
